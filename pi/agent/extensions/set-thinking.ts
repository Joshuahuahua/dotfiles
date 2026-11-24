import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { isLocalModel } from "./lib/mode.ts";

/** Lets the model raise or lower its own thinking level (cloud mode only). Takes effect next turn. */
export default function setThinking(pi: ExtensionAPI) {
	pi.registerTool({
		name: "set_thinking",
		label: "Set Thinking",
		description: "Set your own thinking level for the next turns: low (mechanical work), medium (normal), high (hard debugging or design).",
		promptSnippet: "Set your thinking level (low, medium or high).",
		parameters: Type.Object({
			level: Type.Union([Type.Literal("low"), Type.Literal("medium"), Type.Literal("high")], {
				description: "The thinking level to use from the next turn",
			}),
		}),
		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			if (isLocalModel(ctx.model)) {
				return { content: [{ type: "text", text: "Thinking level is fixed in local mode. No change made." }], details: {} };
			}
			pi.setThinkingLevel(params.level);
			return { content: [{ type: "text", text: `Thinking level set to ${params.level}.` }], details: { level: params.level } };
		},
	});
}
