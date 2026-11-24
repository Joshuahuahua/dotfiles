import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { isLocalModel, LOCAL_MODEL_ID, LOCAL_PROVIDER } from "./lib/mode.ts";

const QUOTA_RE = /\bquota\b/i;
const STATUS_RE = /429|exceeded/i;

/**
 * When a cloud model fails with a quota error (for example "429 quota exceeded"), switch to the
 * local qwen model, set thinking to low and ask it to continue. It stays on qwen until the user
 * switches back with /model, at which point the previous thinking level is restored.
 */
export default function modelFallback(pi: ExtensionAPI) {
	let fellBack = false;
	let previousLevel: ReturnType<typeof pi.getThinkingLevel> | undefined;

	pi.on("agent_end", async (event: any, ctx: any) => {
		if (fellBack || isLocalModel(ctx.model)) return;
		const last = [...(event.messages ?? [])].reverse().find((m: any) => m.role === "assistant");
		const error: string = last?.errorMessage ?? "";
		if (last?.stopReason !== "error" || !QUOTA_RE.test(error) || !STATUS_RE.test(error)) return;

		const target = ctx.modelRegistry.find(LOCAL_PROVIDER, LOCAL_MODEL_ID);
		if (!target) return;

		previousLevel = pi.getThinkingLevel();
		fellBack = true;
		const ok = await pi.setModel(target);
		if (!ok) {
			fellBack = false;
			return;
		}
		pi.setThinkingLevel("low");
		ctx.ui.notify("Cloud quota hit: switched to local qwen. Use /model to switch back.", "warning");
		pi.sendUserMessage(
			"The previous model hit its usage quota, so you are now the local model. Continue with my last request from where it stopped.",
			{ deliverAs: "followUp" },
		);
	});

	pi.on("model_select", async (event: any) => {
		if (!fellBack || isLocalModel(event.model)) return;
		fellBack = false;
		if (previousLevel) pi.setThinkingLevel(previousLevel);
		previousLevel = undefined;
	});
}
