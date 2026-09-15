/**
 * Context Stats Bar
 *
 * Small, out-of-the-way sticky bar pinned to the top of the terminal showing
 * total messages in the current conversation and how full the model's
 * context window is. Implemented as a non-capturing overlay so it never
 * steals keyboard focus from the editor.
 */

import type { AssistantMessage, Usage } from "@earendil-works/pi-ai";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import type { Component, TUI, Theme } from "@earendil-works/pi-tui";
import { truncateToWidth } from "@earendil-works/pi-tui";

function calculateContextTokens(usage: Usage): number {
	return usage.totalTokens || usage.input + usage.output + usage.cacheRead + usage.cacheWrite;
}

function formatTokens(n: number): string {
	if (n < 1000) return `${n}`;
	return `${(n / 1000).toFixed(1)}k`;
}

class StatsBar implements Component {
	text = "";
	constructor(private theme: Theme) {}
	render(width: number): string[] {
		return [truncateToWidth(this.theme.fg("dim", this.text), width)];
	}
	invalidate(): void {}
}

function computeText(ctx: ExtensionContext): string {
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

	return `${messageCount} msgs · ${ctxStr}`;
}

export default function (pi: ExtensionAPI) {
	let bar: StatsBar | undefined;
	let tuiRef: TUI | undefined;

	const update = (ctx: ExtensionContext) => {
		if (!ctx.hasUI) return;
		const text = computeText(ctx);

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

	pi.on("session_start", (_event, ctx) => update(ctx));
	pi.on("turn_start", (_event, ctx) => update(ctx));
	pi.on("turn_end", (_event, ctx) => update(ctx));
	pi.on("message_end", (_event, ctx) => update(ctx));
}
