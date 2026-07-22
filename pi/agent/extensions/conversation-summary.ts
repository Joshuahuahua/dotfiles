import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

// ---------------------------------------------------------------------------
// Conversation summaries
//
// Instead of a "recent sessions" picker, this extension keeps a living summary
// document for each conversation. The agent maintains:
//   - an accurate, evolving TITLE that names every topic covered, and
//   - a SUMMARY capturing the important, durable facts: file paths touched,
//     decisions made, values/answers discovered, etc.
//
// The current conversation's summary is injected into the system prompt each
// turn so the agent can keep extending it. Summaries are searchable by title
// and content so past information can be found later.
// ---------------------------------------------------------------------------

const SUMMARY_ROOT = path.join(process.env.HOME || "", ".pi", "agent", "summaries");
const SESSIONS_ROOT = path.join(process.env.HOME || "", ".pi", "agent", "sessions");
const MAX_INJECT_CHARS = 4000;
const MAX_RESULT_BODY_CHARS = 6000;
const MAX_TITLES = 60;
const MAX_TRANSCRIPT_CHARS = 40000;

interface ConversationSummary {
	sessionId: string;
	cwd: string;
	title: string;
	summary: string;
	created: string;
	updated: string;
}

function ensureRoot(): void {
	fs.mkdirSync(SUMMARY_ROOT, { recursive: true });
}

function summaryPath(sessionId: string): string {
	return path.join(SUMMARY_ROOT, `${sessionId}.json`);
}

function readSummary(sessionId: string): ConversationSummary | undefined {
	try {
		return JSON.parse(fs.readFileSync(summaryPath(sessionId), "utf-8")) as ConversationSummary;
	} catch {
		return undefined;
	}
}

function listSummaries(): ConversationSummary[] {
	ensureRoot();
	let files: string[];
	try {
		files = fs.readdirSync(SUMMARY_ROOT).filter((f) => f.endsWith(".json"));
	} catch {
		return [];
	}
	const out: ConversationSummary[] = [];
	for (const f of files) {
		try {
			out.push(JSON.parse(fs.readFileSync(path.join(SUMMARY_ROOT, f), "utf-8")) as ConversationSummary);
		} catch {
			// skip corrupt entries
		}
	}
	return out;
}

function writeSummary(s: ConversationSummary): void {
	ensureRoot();
	fs.writeFileSync(summaryPath(s.sessionId), `${JSON.stringify(s, null, 2)}\n`, "utf-8");
}

/** Recursively collect all *.jsonl session files under SESSIONS_ROOT. */
function walkSessionFiles(dir: string, out: string[]): void {
	let entries: fs.Dirent[];
	try {
		entries = fs.readdirSync(dir, { withFileTypes: true });
	} catch {
		return;
	}
	for (const e of entries) {
		const full = path.join(dir, e.name);
		if (e.isDirectory()) walkSessionFiles(full, out);
		else if (e.isFile() && e.name.endsWith(".jsonl")) out.push(full);
	}
}

/** Locate the session transcript file for a sessionId (filenames end with _<id>.jsonl). */
function findSessionFile(sessionId: string): string | undefined {
	const files: string[] = [];
	walkSessionFiles(SESSIONS_ROOT, files);
	return files.find((f) => f.includes(sessionId));
}

interface TranscriptBlock {
	role: string;
	text: string;
}

/** Parse a session jsonl into condensed role/text blocks (user, assistant, tool calls/results). */
function extractTranscript(file: string): TranscriptBlock[] {
	let raw: string;
	try {
		raw = fs.readFileSync(file, "utf-8");
	} catch {
		return [];
	}
	const blocks: TranscriptBlock[] = [];
	for (const line of raw.split("\n")) {
		if (!line.trim()) continue;
		let o: any;
		try {
			o = JSON.parse(line);
		} catch {
			continue;
		}
		if (o?.type !== "message") continue;
		const msg = o.message ?? o;
		const role: string = msg.role ?? "?";
		const content = msg.content;
		let text = "";
		if (typeof content === "string") {
			text = content;
		} else if (Array.isArray(content)) {
			const parts: string[] = [];
			for (const p of content) {
				if (!p || typeof p !== "object") continue;
				if (p.type === "text" && p.text) parts.push(p.text);
				else if (p.type === "tool_use") parts.push(`[tool:${p.name}] ${JSON.stringify(p.input ?? {})}`);
				else if (p.type === "tool_result") {
					let t = p.content;
					if (Array.isArray(t)) t = t.map((x: any) => (x && typeof x === "object" ? x.text ?? "" : "")).join(" ");
					parts.push(`[result] ${String(t ?? "")}`);
				}
			}
			text = parts.join("\n");
		}
		text = String(text).trim();
		if (text) blocks.push({ role, text });
	}
	return blocks;
}

function relativeTime(iso: string): string {
	const t = Date.parse(iso);
	if (Number.isNaN(t)) return "unknown";
	const min = Math.floor((Date.now() - t) / 60000);
	if (min < 1) return "just now";
	if (min < 60) return `${min}m ago`;
	const hr = Math.floor(min / 60);
	if (hr < 24) return `${hr}h ago`;
	const days = Math.floor(hr / 24);
	if (days < 30) return `${days}d ago`;
	return `${Math.floor(days / 30)}mo ago`;
}

function truncate(text: string, limit: number): string {
	if (text.length <= limit) return text;
	return `${text.slice(0, limit - 16).trimEnd()}\n[truncated]`;
}

function scoreMatch(s: ConversationSummary, query: string): number {
	const q = query.toLowerCase().trim();
	if (!q) return 0;
	const title = (s.title || "").toLowerCase();
	const body = (s.summary || "").toLowerCase();

	let score = 0;
	if (title === q) score += 100;
	if (title.includes(q)) score += 40;
	if (body.includes(q)) score += 15;

	const tokens = q.split(/\s+/).filter((t) => t.length > 2);
	for (const t of tokens) {
		if (title.includes(t)) score += 8;
		else if (body.includes(t)) score += 3;
	}
	return score;
}

// ---------------------------------------------------------------------------
// Extension
// ---------------------------------------------------------------------------

export default function conversationSummary(pi: ExtensionAPI) {
	let currentSessionId = "";
	let currentCwd = "";

	pi.on("session_start", async (_event, ctx) => {
		ensureRoot();
		currentSessionId = ctx.sessionManager.getSessionId() || "";
		currentCwd = ctx.cwd;
	});

	// Inject the current conversation's living summary into the system prompt so
	// the agent can keep extending it accurately each turn.
	pi.on("before_agent_start", async (event) => {
		const cwd = event.systemPromptOptions.cwd || currentCwd;
		const existing = currentSessionId ? readSummary(currentSessionId) : undefined;

		const parts = [
			"## Conversation Summary",
			"You maintain a living summary of THIS conversation, saved for later recall.",
			"Update it with `update_conversation_summary` only when it is worth doing — NOT after every message.",
			"Good moments to update: a meaningful unit of work or discovery is complete, e.g.",
			"- file paths / directories were touched or decided on,",
			"- a decision was taken or a change was actually made,",
			"- a concrete fact/value/answer was discovered (a hex code, a URL, a command, a config value),",
			"- a task or topic wraps up.",
			"Skip updating for greetings, acknowledgements, clarifying questions, dead-end exploration, or anything that adds no new durable fact. When in doubt, batch small developments into one later update.",
			"Keep the `title` accurate, but only revise it when the conversation's scope actually shifts (a new topic, changed focus) — not for every small addition. If several topics are covered, the title should mention each so the summary can be found by any of them (e.g. \"client html file changes and dark red hex code\").",
			"Always pass the full, updated summary (it replaces the stored version); keep it concise, complete, and deduplicated. Do not store secrets or credentials.",
			"When the user asks where/what something from a past conversation was, use `find_conversation_summaries` (titles only) to find the right one, then `read_conversation_summary` to load just that summary's details — don't ingest every summary.",
		];

		if (existing) {
			parts.push(
				`Current saved summary for this conversation (extend/refine it):\n<conversation-summary>\ntitle: ${existing.title}\n\n${truncate(existing.summary, MAX_INJECT_CHARS)}\n</conversation-summary>`,
			);
		} else {
			parts.push("No summary saved yet for this conversation. Create one once a real topic emerges.");
		}

		return {
			systemPrompt: `${event.systemPrompt}\n\n${parts.join("\n")}`,
		};
	});

	pi.registerTool({
		name: "update_conversation_summary",
		label: "Update Conversation Summary",
		description:
			"Create or update the living summary of the CURRENT conversation. Provide the full, updated title and summary body " +
			"(this replaces the stored version). Capture file paths, decisions, changes actually made, and facts/values discovered. " +
			"Keep the title accurate and covering every topic discussed so it can be found later.",
		promptSnippet: "Save/refresh the running summary and title of the current conversation.",
		promptGuidelines: [
			"Call update_conversation_summary only when it's worth it — not every message. Update at natural checkpoints when durable info appears (file paths, decisions, changes actually made, discovered values) or a task/topic wraps up.",
			"Skip updates for greetings, acknowledgements, clarifying questions, or dead-end exploration; batch small developments into one later update.",
			"Keep the title specific, but only revise it when the scope actually shifts (a new topic or changed focus); cover every topic discussed so it stays findable.",
			"Always pass the full updated summary (it replaces the previous one). Never store secrets or credentials.",
		],
		parameters: Type.Object({
			title: Type.String({
				description: "Accurate, specific title covering every topic discussed so far in this conversation.",
			}),
			summary: Type.String({
				description:
					"Full updated summary body (markdown ok): file paths, decisions, changes made, discovered facts/values. Replaces the stored version.",
			}),
		}),
		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			const sessionId = ctx.sessionManager.getSessionId() || currentSessionId;
			if (!sessionId) {
				return { content: [{ type: "text", text: "No active session id; summary not saved." }], details: {} };
			}
			const title = params.title.replace(/\s+/g, " ").trim();
			const summary = params.summary.trim();
			if (!title && !summary) {
				return { content: [{ type: "text", text: "Nothing to save (empty title and summary)." }], details: {} };
			}
			const now = new Date().toISOString();
			const prev = readSummary(sessionId);
			const record: ConversationSummary = {
				sessionId,
				cwd: ctx.cwd,
				title,
				summary,
				created: prev?.created ?? now,
				updated: now,
			};
			writeSummary(record);
			return {
				content: [{ type: "text", text: `Saved conversation summary: "${title}"` }],
				details: { sessionId, title, path: summaryPath(sessionId) },
			};
		},
	});

	pi.registerTool({
		name: "find_conversation_summaries",
		label: "Find Conversation Summaries",
		description:
			"List saved conversation summary TITLES (lightweight — no bodies) so you can pick which one to read. " +
			"With no query, lists the most recent titles. With a query, ranks titles by topic match. " +
			"To get the actual details of a summary, call read_conversation_summary with its sessionId afterwards.",
		promptSnippet: "List saved conversation titles (no bodies) to decide which summary to read.",
		promptGuidelines: [
			"When the user asks where/what something from a previous conversation was, first call find_conversation_summaries (titles only), then read_conversation_summary for the best-matching sessionId.",
			"Do not read full summaries just to list titles — find_conversation_summaries already returns titles cheaply.",
		],
		parameters: Type.Object({
			query: Type.Optional(
				Type.String({ description: "Topic keywords to rank titles by. Omit to list the most recent titles." }),
			),
		}),
		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			const currentId = ctx.sessionManager.getSessionId() || currentSessionId;
			const all = listSummaries().filter((s) => s.title || s.summary);
			const query = params.query?.trim();

			let results: ConversationSummary[];
			if (query) {
				results = all
					.map((s) => ({ s, score: scoreMatch(s, query) }))
					.filter((r) => r.score > 0)
					.sort((a, b) => b.score - a.score)
					.slice(0, MAX_TITLES)
					.map((r) => r.s);
			} else {
				results = all.sort((a, b) => Date.parse(b.updated) - Date.parse(a.updated)).slice(0, MAX_TITLES);
			}

			if (results.length === 0) {
				return {
					content: [
						{ type: "text", text: query ? `No saved summaries matched "${query}".` : "No conversation summaries saved yet." },
					],
					details: { results: [] },
				};
			}

			// Titles only — no summary bodies, to keep context small.
			const text = results
				.map((s, i) => {
					const here = s.cwd === ctx.cwd ? "" : `  [${s.cwd}]`;
					const current = s.sessionId === currentId ? "  (this conversation)" : "";
					return `${i + 1}. ${s.title || "(untitled)"}  (${relativeTime(s.updated)})${here}${current}\n   id: ${s.sessionId}`;
				})
				.join("\n");

			const header = `${results.length} summary title(s)${query ? ` matching "${query}"` : ""}. Use read_conversation_summary with an id to see details.`;

			return {
				content: [{ type: "text", text: `${header}\n\n${text}` }],
				details: {
					results: results.map((s) => ({
						sessionId: s.sessionId,
						title: s.title,
						cwd: s.cwd,
						updated: s.updated,
					})),
				},
			};
		},
	});

	pi.registerTool({
		name: "read_conversation_summary",
		label: "Read Conversation Summary",
		description:
			"Read the full body of one (or a few) saved conversation summaries. Provide a sessionId from find_conversation_summaries, " +
			"or a titleQuery to fetch the best title match. Only read the summaries you actually need.",
		promptSnippet: "Read the full details of a specific saved conversation summary.",
		promptGuidelines: [
			"Call read_conversation_summary only for the specific summary/summaries relevant to the user's question — not all of them.",
		],
		parameters: Type.Object({
			sessionId: Type.Optional(Type.String({ description: "Exact sessionId of the summary to read (from find_conversation_summaries)." })),
			titleQuery: Type.Optional(Type.String({ description: "If no sessionId, keywords to pick the best-matching title to read." })),
		}),
		async execute(_toolCallId, params, _signal, _onUpdate, _ctx) {
			const sessionId = params.sessionId?.trim();
			const titleQuery = params.titleQuery?.trim();

			let record: ConversationSummary | undefined;
			if (sessionId) {
				record = readSummary(sessionId) || listSummaries().find((s) => s.sessionId === sessionId);
			} else if (titleQuery) {
				record = listSummaries()
					.map((s) => ({ s, score: scoreMatch(s, titleQuery) }))
					.filter((r) => r.score > 0)
					.sort((a, b) => b.score - a.score)
					.map((r) => r.s)[0];
			} else {
				return { content: [{ type: "text", text: "Provide a sessionId or a titleQuery." }], details: {} };
			}

			if (!record) {
				return {
					content: [{ type: "text", text: sessionId ? `No summary found for id ${sessionId}.` : `No summary matched "${titleQuery}".` }],
					details: {},
				};
			}

			const body = [
				`Title: ${record.title || "(untitled)"}`,
				`Updated: ${relativeTime(record.updated)}  |  cwd: ${record.cwd || "?"}`,
				`Resume: pi --session ${record.sessionId}`,
				"",
				truncate(record.summary || "(empty)", MAX_RESULT_BODY_CHARS),
			].join("\n");

			return {
				content: [{ type: "text", text: body }],
				details: {
					sessionId: record.sessionId,
					title: record.title,
					cwd: record.cwd,
					updated: record.updated,
				},
			};
		},
	});

	pi.registerTool({
		name: "read_full_conversation",
		label: "Read Full Conversation",
		description:
			"Fallback: ingest the FULL raw transcript of a past conversation by sessionId, when its summary hints the topic was " +
			"discussed but doesn't contain the specific detail you need. This is heavy — use it only after read_conversation_summary " +
			"came up short. Provide a `search` term to return only matching excerpts (strongly preferred for long conversations).",
		promptSnippet: "Ingest a full past conversation transcript by sessionId as a last resort.",
		promptGuidelines: [
			"Only call read_full_conversation when the summary suggests the info exists but lacks the specific detail; prefer find + read_conversation_summary first.",
			"Pass a `search` term whenever possible so you pull only relevant excerpts instead of the whole transcript.",
		],
		parameters: Type.Object({
			sessionId: Type.String({ description: "sessionId of the conversation to ingest (from find_conversation_summaries)." }),
			search: Type.Optional(
				Type.String({ description: "Keyword/phrase to filter to matching message blocks (case-insensitive). Recommended." }),
			),
		}),
		async execute(_toolCallId, params, _signal, _onUpdate, _ctx) {
			const sessionId = params.sessionId?.trim();
			if (!sessionId) {
				return { content: [{ type: "text", text: "Provide a sessionId." }], details: {} };
			}
			const file = findSessionFile(sessionId);
			if (!file) {
				return { content: [{ type: "text", text: `No session transcript file found for id ${sessionId}.` }], details: {} };
			}

			const blocks = extractTranscript(file);
			if (blocks.length === 0) {
				return { content: [{ type: "text", text: `Transcript for ${sessionId} is empty or unreadable.` }], details: { file } };
			}

			const search = params.search?.trim().toLowerCase();
			let selected = blocks;
			let matchNote = "";
			if (search) {
				const hits: TranscriptBlock[] = [];
				blocks.forEach((b, i) => {
					if (b.text.toLowerCase().includes(search)) {
						// include one block of context on each side
						if (i > 0 && !hits.includes(blocks[i - 1])) hits.push(blocks[i - 1]);
						hits.push(b);
						if (i + 1 < blocks.length) hits.push(blocks[i + 1]);
					}
				});
				if (hits.length === 0) {
					return {
						content: [
							{
								type: "text",
								text: `No message in conversation ${sessionId} matched "${params.search}". It has ${blocks.length} messages; retry without a search term to read it all.`,
							},
						],
						details: { file, messageCount: blocks.length, matches: 0 },
					};
				}
				// de-dupe while preserving order
				selected = hits.filter((b, i) => hits.indexOf(b) === i);
				matchNote = ` (showing excerpts matching "${params.search}")`;
			}

			const rendered = selected.map((b) => `### ${b.role}\n${b.text}`).join("\n\n");
			const clipped = truncate(rendered, MAX_TRANSCRIPT_CHARS);
			const header = `Full conversation ${sessionId}${matchNote} — ${blocks.length} messages total${search ? `, ${selected.length} shown` : ""}.`;
			const tip = clipped.length < rendered.length ? "\n[transcript truncated — narrow with a `search` term for the specific detail]" : "";

			return {
				content: [{ type: "text", text: `${header}\n\n${clipped}${tip}` }],
				details: { file, messageCount: blocks.length, shown: selected.length },
			};
		},
	});
}
