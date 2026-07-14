#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

MEMORY_ROOT = Path.home() / ".pi" / "agent" / "memory"
GLOBAL_MEMORY = MEMORY_ROOT / "MEMORY.md"
PROJECTS_DIR = MEMORY_ROOT / "projects"


def ensure_dirs() -> None:
    MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    if not GLOBAL_MEMORY.exists():
        GLOBAL_MEMORY.write_text("# Persistent Assistant Memory\n", encoding="utf-8")


def project_slug(cwd: str) -> str:
    stripped = cwd.strip().replace("\\", "/").strip("/") or "root"
    return stripped.replace("/", "__")


def project_memory_path(cwd: str) -> Path:
    return PROJECTS_DIR / f"{project_slug(cwd)}.md"


def append_bullet(path: Path, heading: str, text: str) -> None:
    text = text.strip()
    if not text:
        raise SystemExit("Memory text cannot be empty")

    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if text in existing:
        print(f"Already present in {path}")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    block = f"\n## {heading}\n- {text} _(saved {timestamp})_\n"
    path.parent.mkdir(parents=True, exist_ok=True)

    if not existing.strip():
        path.write_text(f"# {heading}\n- {text} _(saved {timestamp})_\n", encoding="utf-8")
        print(path)
        return

    with path.open("a", encoding="utf-8") as fh:
        fh.write(block)
    print(path)


def cmd_show() -> None:
    ensure_dirs()
    print(GLOBAL_MEMORY.read_text(encoding="utf-8"))


def cmd_add_global(text: str) -> None:
    ensure_dirs()
    append_bullet(GLOBAL_MEMORY, "Remembered items", text)


def cmd_add_project(text: str) -> None:
    ensure_dirs()
    append_bullet(project_memory_path(str(Path.cwd())), "Project memory", text)


def cmd_project_path() -> None:
    ensure_dirs()
    print(project_memory_path(str(Path.cwd())))


def usage() -> None:
    print(
        "Usage:\n"
        "  memory.py show\n"
        "  memory.py add-global <text>\n"
        "  memory.py add-project <text>\n"
        "  memory.py project-path"
    )


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        usage()
        return 1

    cmd = argv[1]
    if cmd == "show":
        cmd_show()
        return 0
    if cmd == "add-global":
        if len(argv) < 3:
            usage()
            return 1
        cmd_add_global(" ".join(argv[2:]))
        return 0
    if cmd == "add-project":
        if len(argv) < 3:
            usage()
            return 1
        cmd_add_project(" ".join(argv[2:]))
        return 0
    if cmd == "project-path":
        cmd_project_path()
        return 0

    usage()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
