from __future__ import annotations

import os
import re
import shutil
from datetime import datetime, timezone
from typing import Any

from agent import AgentContext


REVIEW_TYPES = ("blog", "social", "reddit", "email", "influencer")
RESEARCH_TYPES = ("competitor-watch", "trend-reports", "keyword-research")
DASHBOARD_FILENAME = "growth-dashboard.md"


def get_config_value(config: dict | None, key: str, default: Any = None) -> Any:
    """Read a value from plugin config with a fallback."""
    if not config:
        return default
    value = config.get(key, default)
    if value is None:
        return default
    return value


def get_growth_dir(config: dict | None, context_id: str = "") -> str:
    """Resolve the growth docs directory from plugin config.

    The path from config is resolved relative to the active project workdir.
    """
    raw_path = str(get_config_value(config, "growth_docs_path", "docs/growth") or "docs/growth")
    raw_path = raw_path.strip()

    if os.path.isabs(raw_path):
        return os.path.abspath(raw_path)

    workdir = _resolve_workdir(context_id)
    return os.path.abspath(os.path.join(workdir, raw_path))


def _resolve_workdir(context_id: str = "") -> str:
    """Best-effort resolve of the current project workdir."""
    if context_id:
        try:
            context = AgentContext.get(context_id)
            if context and getattr(context, "workdir", None):
                return context.workdir
        except Exception:
            pass
    try:
        context = AgentContext.get()
        if context and getattr(context, "workdir", None):
            return context.workdir
    except Exception:
        pass
    return os.path.abspath("/a0/usr/workdir")


def ensure_directory(path: str) -> None:
    """Create a directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def full_directory_structure() -> list[str]:
    """Return the relative paths of every directory the engine expects."""
    dirs: list[str] = []
    for rtype in REVIEW_TYPES:
        dirs.append(os.path.join("review", rtype))
    for rtype in RESEARCH_TYPES:
        dirs.append(os.path.join("research", rtype))
    dirs.append("pipeline")
    dirs.append("published")
    return dirs


def scan_directory(path: str) -> dict[str, Any]:
    """Recursively count files in a directory grouped by immediate subdirectory."""
    result: dict[str, Any] = {"count": 0, "items": {}}
    if not os.path.isdir(path):
        return result

    for entry in sorted(os.listdir(path)):
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            sub = scan_directory(entry_path)
            result["items"][entry] = sub
            result["count"] += sub["count"]
        else:
            result["count"] += 1
    return result


def _file_metadata(path: str, content_type: str) -> dict[str, Any]:
    try:
        stat = os.stat(path)
        created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat()
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        size = stat.st_size
    except OSError:
        created = modified = ""
        size = 0
    return {
        "filename": os.path.basename(path),
        "type": content_type,
        "path": path,
        "date_created": created,
        "date_modified": modified,
        "size": size,
    }


def list_review_items(growth_dir: str) -> list[dict[str, Any]]:
    """List all files in review/ subdirectories with metadata."""
    review_root = os.path.join(growth_dir, "review")
    items: list[dict[str, Any]] = []
    if not os.path.isdir(review_root):
        return items

    for rtype in REVIEW_TYPES:
        type_dir = os.path.join(review_root, rtype)
        if not os.path.isdir(type_dir):
            continue
        for entry in sorted(os.listdir(type_dir)):
            entry_path = os.path.join(type_dir, entry)
            if os.path.isfile(entry_path):
                items.append(_file_metadata(entry_path, rtype))
    return items


def list_pipeline_items(growth_dir: str) -> list[dict[str, Any]]:
    """List files directly under pipeline/ (flat list)."""
    pipeline_dir = os.path.join(growth_dir, "pipeline")
    items: list[dict[str, Any]] = []
    if not os.path.isdir(pipeline_dir):
        return items
    for entry in sorted(os.listdir(pipeline_dir)):
        entry_path = os.path.join(pipeline_dir, entry)
        if os.path.isfile(entry_path):
            items.append(_file_metadata(entry_path, "pipeline"))
    return items


def list_published_items(growth_dir: str) -> list[dict[str, Any]]:
    """List files directly under published/."""
    published_dir = os.path.join(growth_dir, "published")
    items: list[dict[str, Any]] = []
    if not os.path.isdir(published_dir):
        return items
    for entry in sorted(os.listdir(published_dir)):
        entry_path = os.path.join(published_dir, entry)
        if os.path.isfile(entry_path):
            items.append(_file_metadata(entry_path, "published"))
    return items


def list_research_items(growth_dir: str) -> list[dict[str, Any]]:
    """List research files grouped by research subdirectory."""
    research_root = os.path.join(growth_dir, "research")
    items: list[dict[str, Any]] = []
    if not os.path.isdir(research_root):
        return items
    for rtype in RESEARCH_TYPES:
        type_dir = os.path.join(research_root, rtype)
        if not os.path.isdir(type_dir):
            continue
        for entry in sorted(os.listdir(type_dir)):
            entry_path = os.path.join(type_dir, entry)
            if os.path.isfile(entry_path):
                items.append(_file_metadata(entry_path, rtype))
    return items


def move_file(source: str, dest_dir: str) -> str:
    """Move a file into a destination directory, returning the new path."""
    if not os.path.isfile(source):
        raise FileNotFoundError(f"Source file not found: {source}")
    ensure_directory(dest_dir)
    filename = os.path.basename(source)
    dest_path = os.path.join(dest_dir, filename)
    if os.path.exists(dest_path):
        stem, ext = os.path.splitext(filename)
        dest_path = os.path.join(dest_dir, f"{stem}-{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}")
    shutil.move(source, dest_path)
    return dest_path


def delete_file(source: str) -> None:
    """Delete a file if it exists."""
    if os.path.isfile(source):
        os.remove(source)
    else:
        raise FileNotFoundError(f"File not found: {source}")


def read_text_file(path: str) -> str:
    """Read a text file, returning empty string if missing."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def dashboard_path(growth_dir: str) -> str:
    """Return the expected dashboard markdown path."""
    return os.path.join(growth_dir, DASHBOARD_FILENAME)


def parse_dashboard(growth_dir: str) -> dict[str, Any]:
    """Read the growth dashboard and extract section headings + raw text."""
    path = dashboard_path(growth_dir)
    if not os.path.isfile(path):
        return {"exists": False, "path": path, "sections": {}, "raw": ""}

    raw = read_text_file(path)
    sections: dict[str, str] = {}
    current_heading = ""
    current_lines: list[str] = []

    for line in raw.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            if current_heading:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_heading:
        sections[current_heading] = "\n".join(current_lines).strip()

    return {"exists": True, "path": path, "sections": sections, "raw": raw}


def update_dashboard_section(growth_dir: str, section: str, content: str) -> str:
    """Replace the body of a markdown section in the dashboard file.

    If the section does not exist, it is appended.
    """
    path = dashboard_path(growth_dir)
    if not os.path.isfile(path):
        ensure_directory(growth_dir)
        new_raw = f"# Growth Dashboard\n\n## {section}\n\n{content}\n"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new_raw)
        return path

    raw = read_text_file(path)
    lines = raw.splitlines()
    output: list[str] = []
    i = 0
    replaced = False

    while i < len(lines):
        line = lines[i]
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match and match.group(2).strip() == section:
            prefix = match.group(1)
            output.append(f"{prefix} {section}")
            output.append("")
            output.append(content)
            output.append("")
            i += 1
            while i < len(lines):
                next_match = re.match(r"^(#{1,6})\s+.*$", lines[i])
                if next_match:
                    break
                i += 1
            replaced = True
            continue
        output.append(line)
        i += 1

    if not replaced:
        if output and output[-1].strip():
            output.append("")
        output.append(f"## {section}")
        output.append("")
        output.append(content)
        output.append("")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(output))
    return path


def touch_dashboard(growth_dir: str) -> str:
    """Update the 'Last updated' marker in the dashboard header."""
    path = dashboard_path(growth_dir)
    if not os.path.isfile(path):
        return path
    raw = read_text_file(path)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    updated = re.sub(
        r"(?i)(Last updated:\s*)([^\n]*)",
        lambda m: f"{m.group(1)}{now_str}",
        raw,
        count=1,
    )
    if updated != raw:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(updated)
    return path
