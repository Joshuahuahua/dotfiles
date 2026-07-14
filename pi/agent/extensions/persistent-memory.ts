import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

const MEMORY_ROOT = path.join(process.env.HOME || "", ".pi", "agent", "memory");
const GLOBAL_MEMORY = path.join(MEMORY_ROOT, "MEMORY.md");
const PROJECTS_DIR = path.join(MEMORY_ROOT, "projects");
const MAX_GLOBAL_CHARS = 12000;
const MAX_PROJECT_CHARS = 6000;

type MemoryScope = "global" | "project";

function projectSlug(cwd: string): string {
	const stripped = cwd.trim().replaceAll("\\", "/").replace(/^\/+|\/+$/g, "") || "root";
	return stripped.replaceAll("/", "__");
}

function projectMemoryPath(cwd: string): string {
	return path.join(PROJECTS_DIR, `${projectSlug(cwd)}.md`);
}

function ensureMemoryDirs(): void {
	fs.mkdirSync(PROJECTS_DIR, { recursive: true });
	if (!fs.existsSync(GLOBAL_MEMORY)) {
		fs.writeFileSync(GLOBAL_MEMORY, "# Persistent Assistant Memory\n", "utf-8");
	}
}

function readText(filePath: string): string {
	try {
		return fs.readFileSync(filePath, "utf-8").trim();
	} catch {
		return "";
	}
}

function truncate(text: string, limit: number): string {
	if (text.length <= limit) return text;
	return `${text.slice(0, limit - 16).trimEnd()}\n\n[truncated]`;
}

function appendMemory(filePath: string, heading: string, text: string): { status: "added" | "duplicate"; path: string } {
	ensureMemoryDirs();
	const trimmed = text.trim();
	if (!trimmed) {
		throw new Error("Memory text cannot be empty");
	}

	const existing = readText(filePath);
	if (existing.includes(trimmed)) {
		return { status: "duplicate", path: filePath };
	}

	const timestamp = new Date().toISOString().slice(0, 10);
	const block = `\n## ${heading}\n- ${trimmed} _(saved ${timestamp})_\n`;
	fs.mkdirSync(path.dirname(filePath), { recursive: true });

	if (!existing) {
		fs.writeFileSync(filePath, `# ${heading}\n- ${trimmed} _(saved ${timestamp})_\n`, "utf-8");
	} else {
		fs.appendFileSync(filePath, block, "utf-8");
	}

	return { status: "added", path: filePath };
}

function saveMemory(scope: MemoryScope, cwd: string, text: string): { status: "added" | "duplicate"; path: string } {
	const filePath = scope === "project" ? projectMemoryPath(cwd) : GLOBAL_MEMORY;
	const heading = scope === "project" ? "Project memory" : "Remembered items";
	return appendMemory(filePath, heading, text);
}

function buildMemorySection(cwd: string): string {
	ensureMemoryDirs();
	const globalText = truncate(readText(GLOBAL_MEMORY), MAX_GLOBAL_CHARS);
	const projectFile = projectMemoryPath(cwd);
	const projectText = truncate(readText(projectFile), MAX_PROJECT_CHARS);

	const parts = [
		"## Persistent Memory",
		"You have a persistent user-level memory system stored under ~/.pi/agent/memory.",
		`Global memory file: ${GLOBAL_MEMORY}`,
		`Project memory file for this cwd: ${projectFile}`,
		"Use this memory to improve continuity across sessions and projects.",
		"Update it when the user explicitly asks you to remember something, or when a durable preference is clearly worth keeping.",
		"When a memory is ambiguous or temporary, ask before saving it.",
		"Never store secrets, credentials, tokens, or other sensitive values in memory.",
	];

	if (globalText) {
		parts.push(`<assistant-memory>\n${globalText}\n</assistant-memory>`);
	}

	if (projectText) {
		parts.push(`<project-memory>\n${projectText}\n</project-memory>`);
	}

	return parts.join("\n\n");
}

export default function persistentMemory(pi: ExtensionAPI) {
	let currentCwd = "";

	pi.registerCommand("remember", {
		description: "Save a durable global memory item: /remember <text>",
		handler: async (args, ctx) => {
			const text = args.trim();
			if (!text) {
				ctx.ui.notify("Usage: /remember <durable fact or preference>", "warning");
				return;
			}

			const result = saveMemory("global", ctx.cwd, text);
			ctx.ui.notify(
				result.status === "added" ? `Saved global memory: ${result.path}` : `Memory already exists: ${result.path}`,
				result.status === "added" ? "info" : "warning",
			);
		},
	});

	pi.registerCommand("remember-project", {
		description: "Save a durable project-specific memory item: /remember-project <text>",
		handler: async (args, ctx) => {
			const text = args.trim();
			if (!text) {
				ctx.ui.notify("Usage: /remember-project <project-specific note>", "warning");
				return;
			}

			const result = saveMemory("project", ctx.cwd, text);
			ctx.ui.notify(
				result.status === "added" ? `Saved project memory: ${result.path}` : `Memory already exists: ${result.path}`,
				result.status === "added" ? "info" : "warning",
			);
		},
	});

	pi.registerTool({
		name: "remember_memory",
		label: "Remember Memory",
		description: "Save a durable memory item for future sessions. Only use when the user explicitly asks you to remember something or confirms it should be saved.",
		promptSnippet: "Save a durable preference or fact to persistent memory for future sessions.",
		promptGuidelines: [
			"Use remember_memory only when the user explicitly asks you to remember something or clearly confirms a durable preference/fact should be saved.",
			"Use remember_memory with scope 'project' for repo- or cwd-specific notes, and scope 'global' for cross-project preferences.",
			"Do not use remember_memory for secrets, tokens, passwords, or short-lived task details.",
		],
		parameters: Type.Object({
			text: Type.String({ description: "The durable memory item to save" }),
			scope: Type.Optional(
				Type.Union([Type.Literal("global"), Type.Literal("project")], {
					description: "Where to save the memory item",
				}),
			),
		}),
		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			const scope = (params.scope ?? "global") as MemoryScope;
			const result = saveMemory(scope, ctx.cwd, params.text);
			const scopeLabel = scope === "project" ? "project" : "global";
			return {
				content: [
					{
						type: "text",
						text:
							result.status === "added"
								? `Saved ${scopeLabel} memory to ${result.path}`
								: `Memory already exists in ${result.path}`,
					},
				],
				details: {
					status: result.status,
					scope,
					path: result.path,
				},
			};
		},
	});

	pi.on("session_start", async (_event, ctx) => {
		currentCwd = ctx.cwd;
		ensureMemoryDirs();
	});

	pi.on("before_agent_start", async (event) => {
		const cwd = event.systemPromptOptions.cwd || currentCwd;
		if (!cwd) return;

		const memorySection = buildMemorySection(cwd);
		return {
			systemPrompt: `${event.systemPrompt}\n\n${memorySection}`,
		};
	});
}
