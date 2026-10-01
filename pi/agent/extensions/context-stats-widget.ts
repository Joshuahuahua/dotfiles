/**
 * Context Stats Bar
 *
 * Small, out-of-the-way sticky bar pinned to the top of the terminal showing
 * total messages in the current conversation, how full the model's context
 * window is, and GitHub Copilot premium-request/AI-credit usage for the
 * current billing cycle (the same number shown on
 * https://github.com/settings/copilot/features). Implemented as a
 * non-capturing overlay so it never steals keyboard focus from the editor.
 *
 * Copilot usage is fetched from `gh auth token` + the same undocumented
 * endpoint GitHub's own Copilot Chat clients use (`/copilot_internal/user`).
 * No token is stored; it is re-read from `gh` on every refresh. It updates
 * on session start, every 10 minutes in the background, and on each turn
 * (cheap: just re-renders the cached value), plus on demand via
 * `/copilot-usage`.
 */

import type { AssistantMessage, Usage } from "@earendil-works/pi-ai";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import type { Component, TUI, Theme } from "@earendil-works/pi-tui";
import { truncateToWidth } from "@earendil-works/pi-tui";

const COPILOT_POLL_INTERVAL_MS = 10 * 60 * 1000; // 10 minutes

const COPILOT_HEADERS = {
	"Content-Type": "application/json",
	Accept: "application/json",
	"User-Agent": "GitHubCopilotChat/0.35.0",
	"Editor-Version": "vscode/1.107.0",
	"Editor-Plugin-Version": "copilot-chat/0.35.0",
	"Copilot-Integration-Id": "vscode-chat",
} as const;

type QuotaDetail = {
	entitlement: number;
	remaining: number;
	percent_remaining: number;
	credits_used?: number;
	unlimited: boolean;
};

type CopilotInternalUser = {
	quota_reset_date?: string;
	quota_snapshots?: {
		premium_interactions?: QuotaDetail;
	};
};

function calculateContextTokens(usage: Usage): number {
	return usage.totalTokens || usage.input + usage.output + usage.cacheRead + usage.cacheWrite;
}

function formatTokens(n: number): string {
	if (n < 1000) return `${n}`;
	return `${(n / 1000).toFixed(1)}k`;
}

async function getGitHubToken(pi: ExtensionAPI): Promise<string> {
	const result = await pi.exec("gh", ["auth", "token"], { timeout: 5000 });
	const token = result.stdout.trim();
	if (!token) {
		const detail = result.stderr.trim() || `exit code ${result.code}`;
		throw new Error(`gh auth token: ${detail}`);
	}
	return token;
}

async function fetchPremiumQuota(token: string): Promise<CopilotInternalUser> {
	const response = await fetch("https://api.github.com/copilot_internal/user", {
		headers: { Authorization: `Bearer ${token}`, ...COPILOT_HEADERS },
	});
	if (!response.ok) {
		throw new Error(`${response.status} ${response.statusText}`);
	}
	return (await response.json()) as CopilotInternalUser;
}

function formatCopilotUsage(data: CopilotInternalUser): string | undefined {
	const quota = data.quota_snapshots?.premium_interactions;
	if (!quota || quota.unlimited) return undefined;
	const used = quota.credits_used ?? Math.max(0, quota.entitlement - quota.remaining);
	const usedPercent = quota.entitlement > 0 ? Math.round((used / quota.entitlement) * 100) : 0;
	return `Credits: ${used.toLocaleString()}/${quota.entitlement.toLocaleString()} (${usedPercent}%)`;
}

class StatsBar implements Component {
	text = "";
	constructor(private theme: Theme) {}
	render(width: number): string[] {
		return [truncateToWidth(this.theme.fg("dim", this.text), width)];
	}
	invalidate(): void {}
}

function computeText(ctx: ExtensionContext, copilotText: string | undefined): string {
	const branch = ctx.sessionManager.getBranch();
	const messageCount = branch.filter((e) => e.type === "message").length;

	let lastUsage: Usage | undefined;
	for (let i = branch.length - 1; i >= 0; i--) {
		const e = branch[i];
		if (e.type === "message" && e.message.role === "assistant") {
			lastUsage = (e.message as AssistantMessage).usage;
			break;
		}
	}

	const contextWindow = ctx.model?.contextWindow ?? 0;
	const used = lastUsage ? calculateContextTokens(lastUsage) : 0;
	const ctxStr =
		contextWindow > 0
			? `${Math.round((used / contextWindow) * 100)}%/${formatTokens(contextWindow)} ctx`
			: `${formatTokens(used)} ctx`;

	const parts = [`${messageCount} msgs`, ctxStr];
	if (copilotText) parts.push(copilotText);
	return parts.join(" · ");
}

export default function (pi: ExtensionAPI) {
	let bar: StatsBar | undefined;
	let tuiRef: TUI | undefined;
	let copilotText: string | undefined;
	let copilotTimer: ReturnType<typeof setInterval> | undefined;

	const render = (ctx: ExtensionContext) => {
		if (!ctx.hasUI) return;
		const text = computeText(ctx, copilotText);

		if (!bar) {
			// Fire-and-forget: open once and never resolve, so it stays pinned
			// for the life of the session.
			void ctx.ui.custom<void>(
				(tui, theme) => {
					tuiRef = tui;
					bar = new StatsBar(theme);
					bar.text = text;
					return bar;
				},
				{
					overlay: true,
					overlayOptions: {
						anchor: "top-center",
						width: "100%",
						nonCapturing: true,
					},
				},
			);
			return;
		}

		bar.text = text;
		tuiRef?.requestRender();
	};

	const refreshCopilotUsage = async (ctx: ExtensionContext, options: { notifyOnError?: boolean } = {}) => {
		try {
			const token = await getGitHubToken(pi);
			const data = await fetchPremiumQuota(token);
			copilotText = formatCopilotUsage(data);
			render(ctx);
		} catch (error) {
			if (options.notifyOnError) {
				ctx.ui.notify(`Copilot usage: ${error instanceof Error ? error.message : String(error)}`, "warning");
			}
		}
	};

	pi.on("session_start", (_event, ctx) => {
		render(ctx);
		void refreshCopilotUsage(ctx);
		copilotTimer = setInterval(() => void refreshCopilotUsage(ctx), COPILOT_POLL_INTERVAL_MS);
	});
	pi.on("session_shutdown", (_event, _ctx) => {
		if (copilotTimer) clearInterval(copilotTimer);
		copilotTimer = undefined;
	});
	pi.on("turn_start", (_event, ctx) => render(ctx));
	pi.on("turn_end", (_event, ctx) => render(ctx));
	pi.on("message_end", (_event, ctx) => render(ctx));

	pi.registerCommand("copilot-usage", {
		description: "Refresh GitHub Copilot usage shown in the stats bar",
		handler: async (_args, ctx) => {
			await refreshCopilotUsage(ctx, { notifyOnError: true });
		},
	});
}
