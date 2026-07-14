import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

type TodoItem = {
	id: number;
	text: string;
	status: string;
};

type TodoData = {
	next_id: number;
	items: TodoItem[];
};

const TODO_FILE = path.join(process.env.HOME || "", ".pi", "agent", "skills", "todo-list", "data", "todos.json");
const WIDGET_ID = "todo-startup";
const STATUS_ID = "todo-startup";
const MAX_ITEMS = 8;

function readOpenTodos(): TodoItem[] {
	try {
		const raw = fs.readFileSync(TODO_FILE, "utf-8");
		const data = JSON.parse(raw) as Partial<TodoData>;
		const items = Array.isArray(data.items) ? data.items : [];
		return items
			.filter((item): item is TodoItem => Boolean(item && typeof item.id === "number" && typeof item.text === "string"))
			.filter((item) => item.status === "open")
			.sort((a, b) => a.id - b.id);
	} catch {
		return [];
	}
}

function renderTodoLines(ctx: ExtensionContext, todos: TodoItem[]): string[] {
	const lines: string[] = [];
	const title = ctx.ui.theme?.fg ? ctx.ui.theme.fg("accent", "Todo list") : "Todo list";
	lines.push(title);

	for (const todo of todos.slice(0, MAX_ITEMS)) {
		const prefix = ctx.ui.theme?.fg ? ctx.ui.theme.fg("muted", `#${todo.id} `) : `#${todo.id} `;
		lines.push(`${prefix}${todo.text}`);
	}

	if (todos.length > MAX_ITEMS) {
		const remaining = todos.length - MAX_ITEMS;
		lines.push(ctx.ui.theme?.fg ? ctx.ui.theme.fg("muted", `… and ${remaining} more`) : `… and ${remaining} more`);
	}

	return lines;
}

function refreshTodoUi(ctx: ExtensionContext): void {
	if (!ctx.hasUI) return;

	const todos = readOpenTodos();
	if (todos.length === 0) {
		ctx.ui.setWidget(WIDGET_ID, undefined);
		ctx.ui.setStatus(STATUS_ID, undefined);
		return;
	}

	ctx.ui.setWidget(WIDGET_ID, renderTodoLines(ctx, todos));
	ctx.ui.setStatus(STATUS_ID, `todos: ${todos.length}`);
}

export default function todoStartupExtension(pi: ExtensionAPI) {
	pi.on("session_start", async (_event, ctx) => {
		refreshTodoUi(ctx);
	});

	pi.registerCommand("todo-refresh", {
		description: "Refresh the startup todo widget from the todo list file",
		handler: async (_args, ctx) => {
			refreshTodoUi(ctx);
			ctx.ui.notify("Todo widget refreshed", "info");
		},
	});
}
