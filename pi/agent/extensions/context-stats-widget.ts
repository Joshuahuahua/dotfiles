/**
 * Context Stats Widget
 *
 * Small, out-of-the-way line above the editor showing total messages in the
 * current conversation and how full the model's context window is.
 */

import type { AssistantMessage, Usage } from "@earendil-works/pi-ai";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

function calculateContextTokens(usage: Usage): number {
	return usage.totalTokens || usage.input + usage.output + usage.cacheRead + usage.cacheWrite;
}

function formatTokens(n: number): string {
	if (n < 1000) return `${n}`;
	return `${(n / 1000).toFixed(1)}k`;
}

export default function (pi: ExtensionAPI) {
	const update = (ctx: ExtensionContext) => {
		if (!ctx.hasUI) return;

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
		const pct = contextWindow > 0 ? Math.round((used / contextWindow) * 100) : undefined;

		const theme = ctx.ui.theme;
		const ctxStr =
			contextWindow > 0
				? `${pct}%/${formatTokens(contextWindow)} ctx`
				: `${formatTokens(used)} ctx`;
		const line = theme.fg("dim", `${messageCount} msgs · ${ctxStr}`);

		ctx.ui.setWidget("context-stats", [line]);
	};

	pi.on("session_start", (_event, ctx) => update(ctx));
	pi.on("turn_start", (_event, ctx) => update(ctx));
	pi.on("turn_end", (_event, ctx) => update(ctx));
	pi.on("message_end", (_event, ctx) => update(ctx));
}
