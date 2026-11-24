import * as fs from "node:fs";
import * as path from "node:path";

export const LOCAL_PROVIDER = "home-ollama";
export const LOCAL_MODEL_ID = "qwen3.6:35b-a3b";

/** Local mode = the primary model runs on the home Ollama server. Everything else is cloud mode. */
export function isLocalModel(model?: { provider?: string } | null): boolean {
	return model?.provider === LOCAL_PROVIDER;
}

export type ActiveRun = {
	runId: string;
	sessionId?: string;
	local: boolean;
};

const ACTIVE_STATES = new Set(["running", "paused", "queued", "starting", "pending"]);

function runsDir(): string {
	const uid = typeof process.getuid === "function" ? process.getuid() : 0;
	return path.join("/tmp", `pi-subagents-uid-${uid}`, "async-subagent-runs");
}

function pidAlive(pid: unknown): boolean {
	if (typeof pid !== "number") return true;
	try {
		process.kill(pid, 0);
		return true;
	} catch {
		return false;
	}
}

/** Reads the pi-subagents async run files and returns runs that are still alive. */
export function activeRuns(): ActiveRun[] {
	const dir = runsDir();
	let names: string[];
	try {
		names = fs.readdirSync(dir);
	} catch {
		return [];
	}
	const out: ActiveRun[] = [];
	const cutoff = Date.now() - 6 * 60 * 60 * 1000;
	for (const name of names) {
		const file = path.join(dir, name, "status.json");
		try {
			if (fs.statSync(file).mtimeMs < cutoff) continue;
			const status = JSON.parse(fs.readFileSync(file, "utf-8"));
			if (!ACTIVE_STATES.has(String(status.state))) continue;
			if (!pidAlive(status.pid)) continue;
			const steps: any[] = Array.isArray(status.steps) ? status.steps : [];
			const local = steps.some((s) => {
				if (s.status && !ACTIVE_STATES.has(String(s.status))) return false;
				const provider = s.resolvedModel?.provider ?? String(s.model ?? "").split("/")[0];
				return provider === LOCAL_PROVIDER;
			});
			out.push({ runId: String(status.runId ?? name), sessionId: status.sessionId, local });
		} catch {
			// Half-written or unreadable file: ignore it.
		}
	}
	return out;
}
