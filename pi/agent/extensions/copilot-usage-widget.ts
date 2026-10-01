/**
 * Copilot Usage Widget
 *
 * Shows GitHub Copilot premium-request / AI-credit usage for the current
 * billing cycle in the footer status bar (the same number shown on
 * https://github.com/settings/copilot/features, e.g. "844 / 30,000 AI
 * credits").
 *
 * Gets a GitHub token from `gh auth token` (requires the GitHub CLI to be
 * logged in) and calls the same undocumented endpoint GitHub's own Copilot
 * Chat clients use (`/copilot_internal/user`). No token is stored by this
 * extension; it is re-read from `gh` on every poll.
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

const POLL_INTERVAL_MS = 10 * 60 * 1000; // 10 minutes
const STATUS_KEY = "copilot-usage";

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

function formatResetDate(dateStr: string | undefined): string {
	if (!dateStr) return "";
	const date = new Date(dateStr);
	if (Number.isNaN(date.getTime())) return "";
	return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function formatStatus(ctx: ExtensionContext, data: CopilotInternalUser): string | undefined {
	const quota = data.quota_snapshots?.premium_interactions;
	if (!quota || quota.unlimited) return undefined;

	const used = quota.credits_used ?? Math.max(0, quota.entitlement - quota.remaining);
	const resetLabel = formatResetDate(data.quota_reset_date);
	const theme = ctx.ui.theme;
	const low = quota.percent_remaining <= 10;
	const colored = theme.fg(low ? "warning" : "dim", `${used.toLocaleString()}/${quota.entitlement.toLocaleString()}`);
	const suffix = resetLabel ? theme.fg("dim", ` (resets ${resetLabel})`) : "";
	return `${theme.fg("dim", "Copilot ")}${colored}${suffix}`;
}

export default function (pi: ExtensionAPI) {
	let timer: ReturnType<typeof setInterval> | undefined;

	const refresh = async (ctx: ExtensionContext, options: { notifyOnError?: boolean } = {}) => {
		if (!ctx.hasUI) return;
		try {
			const token = await getGitHubToken(pi);
			const data = await fetchPremiumQuota(token);
			const text = formatStatus(ctx, data);
			ctx.ui.setStatus(STATUS_KEY, text);
		} catch (error) {
			if (options.notifyOnError) ctx.ui.notify(`Copilot usage: ${error instanceof Error ? error.message : String(error)}`, "warning");
		}
	};

	pi.on("session_start", (_event, ctx) => {
		void refresh(ctx);
		timer = setInterval(() => void refresh(ctx), POLL_INTERVAL_MS);
	});

	pi.on("session_shutdown", (_event, _ctx) => {
		if (timer) clearInterval(timer);
		timer = undefined;
	});

	pi.registerCommand("copilot-usage", {
		description: "Refresh GitHub Copilot usage in the status bar",
		handler: async (_args, ctx) => {
			await refresh(ctx, { notifyOnError: true });
		},
	});
}
