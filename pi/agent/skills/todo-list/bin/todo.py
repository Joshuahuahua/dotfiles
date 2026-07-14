#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "todos.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_data() -> dict:
    return {"next_id": 1, "items": []}


def load_data() -> dict:
    if not DATA_FILE.exists():
        return default_data()
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Error: failed to parse {DATA_FILE}: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict) or "items" not in data or "next_id" not in data:
        print(f"Error: invalid data format in {DATA_FILE}", file=sys.stderr)
        sys.exit(1)
    return data


def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_item(data: dict, item_id: int) -> dict:
    for item in data["items"]:
        if item["id"] == item_id:
            return item
    print(f"Error: todo #{item_id} not found", file=sys.stderr)
    sys.exit(1)


def status_prefix(status: str) -> str:
    return {
        "open": "[ ]",
        "done": "[x]",
    }.get(status, "[-]")


def format_item(item: dict, include_notes: bool = False) -> str:
    lines = [f"{status_prefix(item['status'])} #{item['id']} {item['text']}"]
    lines.append(f"    created: {item['created_at']}")
    lines.append(f"    updated: {item['updated_at']}")
    if include_notes and item.get("notes"):
        lines.append("    notes:")
        for note in item["notes"]:
            lines.append(f"      - {note['at']}: {note['text']}")
    return "\n".join(lines)


def cmd_list(args: argparse.Namespace) -> int:
    data = load_data()
    items = data["items"]
    status = args.status or "open"
    if args.all:
        if args.status:
            items = [item for item in items if item["status"] == args.status]
    else:
        items = [item for item in items if item["status"] == status]

    items = sorted(items, key=lambda item: item["id"])

    if not items:
        if args.all and not args.status:
            print("No todo items.")
        else:
            print(f"No {status} todo items.")
        return 0

    for item in items:
        print(format_item(item, include_notes=args.notes))
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    text = " ".join(args.text).strip()
    if not text:
        print("Error: todo text cannot be empty", file=sys.stderr)
        return 1
    data = load_data()
    timestamp = now_iso()
    item = {
        "id": data["next_id"],
        "text": text,
        "status": "open",
        "created_at": timestamp,
        "updated_at": timestamp,
        "notes": [],
    }
    data["next_id"] += 1
    data["items"].append(item)
    save_data(data)
    print(f"Added todo #{item['id']}: {item['text']}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    data = load_data()
    item = get_item(data, args.id)
    print(format_item(item, include_notes=True))
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    text = " ".join(args.text).strip()
    if not text:
        print("Error: updated todo text cannot be empty", file=sys.stderr)
        return 1
    data = load_data()
    item = get_item(data, args.id)
    item["text"] = text
    item["updated_at"] = now_iso()
    save_data(data)
    print(f"Updated todo #{item['id']}: {item['text']}")
    return 0


def cmd_note(args: argparse.Namespace) -> int:
    text = " ".join(args.note).strip()
    if not text:
        print("Error: note text cannot be empty", file=sys.stderr)
        return 1
    data = load_data()
    item = get_item(data, args.id)
    item.setdefault("notes", []).append({"at": now_iso(), "text": text})
    item["updated_at"] = now_iso()
    save_data(data)
    print(f"Added note to todo #{item['id']}")
    return 0


def cmd_done(args: argparse.Namespace) -> int:
    data = load_data()
    item = get_item(data, args.id)
    item["status"] = "done"
    item["updated_at"] = now_iso()
    save_data(data)
    print(f"Marked todo #{item['id']} done")
    return 0


def cmd_reopen(args: argparse.Namespace) -> int:
    data = load_data()
    item = get_item(data, args.id)
    item["status"] = "open"
    item["updated_at"] = now_iso()
    save_data(data)
    print(f"Reopened todo #{item['id']}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    data = load_data()
    item = get_item(data, args.id)
    data["items"] = [existing for existing in data["items"] if existing["id"] != args.id]
    save_data(data)
    print(f"Removed todo #{item['id']}: {item['text']}")
    return 0


def matches_query(item: dict, query: str) -> bool:
    haystack = [item.get("text", "")]
    haystack.extend(note.get("text", "") for note in item.get("notes", []))
    corpus = "\n".join(haystack).lower()
    tokens = [token for token in query.lower().split() if token]
    return all(token in corpus for token in tokens)


def cmd_search(args: argparse.Namespace) -> int:
    query = " ".join(args.query).strip()
    if not query:
        print("Error: search query cannot be empty", file=sys.stderr)
        return 1
    data = load_data()
    items = [item for item in data["items"] if matches_query(item, query)]
    items = sorted(items, key=lambda item: item["id"])
    if not items:
        print(f'No todo items matched "{query}".')
        return 0
    for item in items:
        print(format_item(item, include_notes=args.notes))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage a personal todo list.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List todo items")
    list_parser.add_argument("--all", action="store_true", help="Include all statuses")
    list_parser.add_argument("--status", choices=["open", "done"], help="Status filter")
    list_parser.add_argument("--notes", action="store_true", help="Show notes")
    list_parser.set_defaults(func=cmd_list)

    add_parser = subparsers.add_parser("add", help="Add a todo item")
    add_parser.add_argument("text", nargs="+", help="Todo text")
    add_parser.set_defaults(func=cmd_add)

    show_parser = subparsers.add_parser("show", help="Show one todo item")
    show_parser.add_argument("id", type=int, help="Todo id")
    show_parser.set_defaults(func=cmd_show)

    update_parser = subparsers.add_parser("update", help="Update todo text")
    update_parser.add_argument("id", type=int, help="Todo id")
    update_parser.add_argument("text", nargs="+", help="New todo text")
    update_parser.set_defaults(func=cmd_update)

    note_parser = subparsers.add_parser("note", help="Add a note to a todo item")
    note_parser.add_argument("id", type=int, help="Todo id")
    note_parser.add_argument("note", nargs="+", help="Note text")
    note_parser.set_defaults(func=cmd_note)

    done_parser = subparsers.add_parser("done", help="Mark a todo item done")
    done_parser.add_argument("id", type=int, help="Todo id")
    done_parser.set_defaults(func=cmd_done)

    reopen_parser = subparsers.add_parser("reopen", help="Reopen a completed todo item")
    reopen_parser.add_argument("id", type=int, help="Todo id")
    reopen_parser.set_defaults(func=cmd_reopen)

    remove_parser = subparsers.add_parser("remove", help="Remove a todo item")
    remove_parser.add_argument("id", type=int, help="Todo id")
    remove_parser.set_defaults(func=cmd_remove)

    search_parser = subparsers.add_parser("search", help="Search todo items")
    search_parser.add_argument("query", nargs="+", help="Search query")
    search_parser.add_argument("--notes", action="store_true", help="Show notes")
    search_parser.set_defaults(func=cmd_search)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
