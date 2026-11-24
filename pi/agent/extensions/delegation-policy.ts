import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { activeRuns, isLocalModel, LOCAL_MODEL_ID, LOCAL_PROVIDER } from "./lib/mode.ts";

const LOCAL_AGENTS = ["local-scout", "local-worker", "local-researcher"];
const LOCAL_MODEL = `${LOCAL_PROVIDER}/${LOCAL_MODEL_ID}`;
// Tools the local parent may still use while one of its local children is running.
const ALLOWED_WHILE_CHILD_RUNS = new Set(["subagent", "subagent_supervisor", "contact_supervisor"]);
// Guards against two local launches issued in the same turn, before the first shows up on disk.
const LAUNCH_GRACE_MS = 8000;

/**
 * Enforces the delegation rules:
 * - Cloud mode (Claude parent): unlimited Claude children, at most ONE local qwen child at a time.
 * - Local mode (qwen parent): one child at a time, always qwen, always background, and the parent
 *   may not run other tools while that child works (it must end its turn and wait).
 */
export default function delegationPolicy(pi: ExtensionAPI) {
	let lastLocalLaunchAt = 0;

	const block = (reason: string) => ({ block: true as const, reason });

	pi.on("tool_call", async (event: any, ctx: any) => {
		const local = isLocalModel(ctx.model);
		const sessionId: string | undefined = ctx.sessionManager?.getSessionId?.();

		if (event.toolName !== "subagent") {
			if (!local || ALLOWED_WHILE_CHILD_RUNS.has(event.toolName)) return;
			const own = activeRuns().some((r) => r.local && (!sessionId || r.sessionId === sessionId));
			if (own) {
				return block(
					"A local child agent is running. End your turn now and wait. Its result or question will arrive as a message.",
				);
			}
			return;
		}

		const input = event.input ?? {};
		const action = input.action;
		const isResume = action === "resume";
		if (action !== undefined && !isResume) return; // status, list, reply, stop, guide, ...

		const multi =
			input.tasks || input.chain || input.workflow || input.options?.script || (typeof input.count === "number" && input.count > 1);
		const text = JSON.stringify(input);

		if (local) {
			if (multi) {
				return block("Local mode allows one child at a time. Use a single call with one agent and one task. No parallel, chain or workflow.");
			}
			if (activeRuns().some((r) => r.local) || Date.now() - lastLocalLaunchAt < LAUNCH_GRACE_MS) {
				return block("A local child is already running. End your turn and wait for it to finish or ask a question.");
			}
			if (!isResume) {
				input.model = LOCAL_MODEL; // only the local qwen model may be used
			}
			input.async = true; // background, so the child can ask questions while the parent is idle
			lastLocalLaunchAt = Date.now();
			return;
		}

		// Cloud mode: only the local agents need limiting.
		const localMentions = LOCAL_AGENTS.reduce((n, a) => n + (text.split(a).length - 1), 0);
		const usesLocalModel = typeof input.model === "string" && input.model.startsWith(`${LOCAL_PROVIDER}/`);
		if (localMentions === 0 && !usesLocalModel) return;

		if (localMentions > 1 || (multi && localMentions > 0 && usesLocalModel)) {
			return block("Only ONE local qwen agent may run at a time. Launch a single local agent per call, and wait for it to finish.");
		}
		if (activeRuns().some((r) => r.local) || Date.now() - lastLocalLaunchAt < LAUNCH_GRACE_MS) {
			return block("A local qwen agent is already running. Only one is allowed at a time. Wait for it, or use a Claude agent (scout/worker).");
		}
		lastLocalLaunchAt = Date.now();
	});
}
