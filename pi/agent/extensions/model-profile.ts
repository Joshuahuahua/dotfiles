import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { isLocalModel } from "./lib/mode.ts";

const DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DESC_MAX_LOCAL = 70;
// Tools the local parent hands to children instead (web research goes to local-researcher).
const HIDDEN_IN_LOCAL = new Set(["web_search", "source_check", "fetch_content", "get_search_content", "read_full_conversation"]);

function readProfile(name: string): string {
	try {
		return fs.readFileSync(path.join(DIR, "profiles", name), "utf-8").trim();
	} catch {
		return "";
	}
}

function shorten(text: string, max: number): string {
	const oneLine = text.replace(/\s+/g, " ").trim();
	const firstSentence = oneLine.split(/(?<=[.!?])\s/)[0] ?? oneLine;
	const base = firstSentence.length <= max ? firstSentence : oneLine;
	return base.length <= max ? base : `${base.slice(0, max - 1).trimEnd()}…`;
}

/**
 * Injects the delegation profile that matches the active model.
 * In local (qwen) mode it also shrinks the skills catalog to short one-line descriptions
 * (full SKILL.md files are still read on demand).
 */
export default function modelProfile(pi: ExtensionAPI) {
	pi.on("before_agent_start", async (event, ctx) => {
		const local = isLocalModel(ctx.model);

		if (local) {
			const skills = (event.systemPromptOptions as any).skills as Array<{ description?: string }> | undefined;
			for (const skill of skills ?? []) {
				if (typeof skill.description === "string") {
					skill.description = shorten(skill.description, SKILL_DESC_MAX_LOCAL);
				}
			}
		}

		if (local) {
			const opts = event.systemPromptOptions as any;
			if (Array.isArray(opts.selectedTools)) {
				opts.selectedTools = opts.selectedTools.filter((t: string) => !HIDDEN_IN_LOCAL.has(t));
			}
		}

		const profile = readProfile(local ? "local.md" : "cloud.md");
		if (!profile) return;
		// Structured section (not a systemPrompt return) so the skills edit above is kept.
		const sections = ((event.systemPromptOptions as any).sections ??= {});
		sections["delegation-mode"] = profile;
	});
}
