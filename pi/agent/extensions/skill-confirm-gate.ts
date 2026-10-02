/**
 * Skill Confirm Gate Extension
 *
 * Lets a skill declare, in its own SKILL.md frontmatter, that invoking it
 * requires a real user confirmation - without the skill's script having to
 * implement that itself. A script-level confirm (e.g. a zenity dialog it
 * pops up) can always be bypassed by the agent choosing a different script
 * or a raw command. This extension gates at the engine's tool_call event
 * instead, so the bash tool genuinely cannot run a command touching a
 * flagged skill's directory until ctx.ui.confirm() returns true.
 *
 * How to flag a skill:
 *
 *   ---
 *   name: my-skill
 *   description: ...
 *   metadata:
 *     requires-confirmation: true
 *   ---
 *
 * Any bash command whose text references that skill's directory path will
 * be held for confirmation before it runs. Declining blocks the tool call
 * with { block: true }; the agent cannot make it proceed by retrying,
 * using a different tool, or bypassing the script.
 *
 * This is a prototype: path-text matching on the bash command string is a
 * simple heuristic, not a sandboxed boundary. It is meant to gate normal,
 * honestly-constructed skill invocations, not to resist a deliberately
 * adversarial model trying to evade detection.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

interface FlaggedSkill {
	name: string;
	baseDir: string;
	/** Literal substrings that, if present in a bash command, mean it touches this skill. */
	matchPatterns: string[];
}

function buildMatchPatterns(baseDir: string): string[] {
	const patterns = new Set<string>();
	patterns.add(baseDir);

	try {
		const real = fs.realpathSync(baseDir);
		if (real !== baseDir) patterns.add(real);
	} catch {
		// baseDir may not exist yet under its realpath target; ignore
	}

	const home = os.homedir();
	for (const p of [...patterns]) {
		if (p.startsWith(home)) {
			patterns.add("~" + p.slice(home.length));
		}
	}

	// Catch relative invocations too: match on the "<skills-root>/<skill-name>" suffix
	// regardless of what precedes it (absolute, ~, ./, or a bare relative cd).
	const skillName = path.basename(baseDir);
	for (const marker of ["skills/" + skillName, ".agents/skills/" + skillName]) {
		patterns.add(marker);
	}

	return [...patterns];
}

const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", "__pycache__"]);

function extractFrontmatter(content: string): string | undefined {
	if (!content.startsWith("---")) return undefined;
	const end = content.indexOf("\n---", 3);
	if (end === -1) return undefined;
	return content.slice(3, end);
}

/** Minimal check for `metadata: { requires-confirmation: true }` without a full YAML parser. */
function frontmatterRequiresConfirmation(frontmatter: string): boolean {
	const lines = frontmatter.split("\n");
	let inMetadata = false;
	let metadataIndent = -1;

	for (const line of lines) {
		const indentMatch = line.match(/^(\s*)/);
		const indent = indentMatch ? indentMatch[1].length : 0;
		const trimmed = line.trim();

		if (!inMetadata) {
			if (/^metadata\s*:/.test(trimmed)) {
				inMetadata = true;
				metadataIndent = indent;
				// Support inline form: metadata: { requires-confirmation: true }
				if (/requires-confirmation\s*:\s*true/i.test(trimmed)) return true;
			}
			continue;
		}

		if (trimmed === "") continue;
		if (indent <= metadataIndent) {
			inMetadata = false;
			continue;
		}

		if (/requires-confirmation\s*:\s*true/i.test(trimmed)) return true;
	}

	return false;
}

function findSkillMdFiles(root: string, depth = 0, maxDepth = 6): string[] {
	if (depth > maxDepth) return [];
	let entries: fs.Dirent[];
	try {
		entries = fs.readdirSync(root, { withFileTypes: true });
	} catch {
		return [];
	}

	const found: string[] = [];
	const hasSkillMd = entries.some((e) => e.isFile() && e.name === "SKILL.md");
	if (hasSkillMd) {
		found.push(path.join(root, "SKILL.md"));
		return found; // don't recurse further once a skill root is found
	}

	for (const entry of entries) {
		if (!entry.isDirectory() || SKIP_DIRS.has(entry.name)) continue;
		found.push(...findSkillMdFiles(path.join(root, entry.name), depth + 1, maxDepth));
	}

	return found;
}

function discoverFlaggedSkills(cwd: string): FlaggedSkill[] {
	const roots = [
		path.join(os.homedir(), ".pi", "agent", "skills"),
		path.join(os.homedir(), ".agents", "skills"),
		path.join(cwd, ".pi", "skills"),
		path.join(cwd, ".agents", "skills"),
	];

	const flagged: FlaggedSkill[] = [];

	for (const root of roots) {
		if (!fs.existsSync(root)) continue;
		for (const skillMdPath of findSkillMdFiles(root)) {
			let content: string;
			try {
				content = fs.readFileSync(skillMdPath, "utf-8");
			} catch {
				continue;
			}
			const frontmatter = extractFrontmatter(content);
			if (!frontmatter || !frontmatterRequiresConfirmation(frontmatter)) continue;

			const nameMatch = frontmatter.match(/^name\s*:\s*(.+)$/m);
			const baseDir = path.dirname(skillMdPath);
			flagged.push({
				name: nameMatch ? nameMatch[1].trim() : path.basename(baseDir),
				baseDir,
				matchPatterns: buildMatchPatterns(baseDir),
			});
		}
	}

	return flagged;
}

export default function (pi: ExtensionAPI) {
	pi.on("tool_call", async (event, ctx) => {
		if (event.toolName !== "bash") return undefined;

		// Re-scan on every call rather than caching once per session/reload: a
		// skill can be created or edited mid-session, and a stale cached list
		// would silently let a newly-flagged skill's commands through
		// unconfirmed. This is a handful of small file reads, not a hot path.
		const flaggedSkills = discoverFlaggedSkills(ctx.cwd);
		if (flaggedSkills.length === 0) return undefined;

		const command = String(event.input.command ?? "");
		const matched = flaggedSkills.find((skill) => skill.matchPatterns.some((pattern) => command.includes(pattern)));
		if (!matched) return undefined;

		if (!ctx.hasUI) {
			return { block: true, reason: `Skill "${matched.name}" requires confirmation (no UI available)` };
		}

		const confirmed = await ctx.ui.confirm(
			`Confirm: ${matched.name}`,
			`This runs a command for the "${matched.name}" skill, which is flagged as\nrequires-confirmation: true.\n\nCommand:\n${command}\n\nProceed?`,
		);

		if (!confirmed) {
			return { block: true, reason: `"${matched.name}" was not approved by the user` };
		}

		return undefined;
	});
}
