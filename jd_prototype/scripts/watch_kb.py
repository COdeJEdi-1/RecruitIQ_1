#!/usr/bin/env python3
"""
Live terminal watcher for the JD Generator's knowledge base.

Polls kb/*/*/feedback/*.jsonl and prints a readable line the moment a
recruiter submits feedback, approves a JD, or adds a custom skill — so you
can watch the KB build up in real time while using the app in the browser.

Usage (from jd_prototype/):
    python3 scripts/watch_kb.py
"""

import json
import sys
import time
from pathlib import Path

KB_ROOT = Path(__file__).parent.parent / "kb"
sys.path.insert(0, str(Path(__file__).parent.parent))

from community_skills import get_promoted_skills, _normalize_skill  # noqa: E402

POLL_SECONDS = 1.0

# path -> byte offset already printed
_offsets: dict[Path, int] = {}


def _role_from_path(path: Path) -> tuple[str, str]:
    # kb/{dept}/{family}/feedback/{file}.jsonl
    family_dir = path.parent.parent
    dept_dir = family_dir.parent
    return dept_dir.name, family_dir.name


def _format_feedback(dept: str, family: str, rec: dict) -> str:
    tags = rec.get("positive_tags", []) + rec.get("improvement_tags", [])
    tag_str = f" · tags: {', '.join(tags)}" if tags else ""
    text = rec.get("free_text", "").strip()
    text_str = f' · "{text}"' if text else ""
    return (
        f"[FEEDBACK]  {dept}/{family}  ·  {rec.get('role_title', '?')}  "
        f"·  {rec.get('overall_rating', '?')}/5 by {rec.get('user_email', '?')}"
        f"{tag_str}{text_str}"
    )


def _format_edit_diff(dept: str, family: str, rec: dict) -> str:
    return (
        f"[APPROVED]  {dept}/{family}  ·  {rec.get('role_title', '?')}  "
        f"·  edit_ratio={rec.get('edit_ratio', '?')} by {rec.get('user_email', '?')}  "
        f"·  {rec.get('diff_summary', '')}"
    )


def _format_custom_skill(dept: str, family: str, rec: dict) -> str:
    skill = rec.get("skill_raw", "?")
    user = rec.get("user_email", "?")
    promoted = get_promoted_skills(dept, family)
    is_promoted = any(_normalize_skill(p) == rec.get("skill_key") for p in promoted)
    status = "PROMOTED ✓" if is_promoted else "pending"
    return (
        f"[SKILL ADDED]  {dept}/{family}  ·  \"{skill}\"  "
        f"added by {user}  ·  status: {status}"
    )


FORMATTERS = {
    "feedback_log.jsonl": _format_feedback,
    "edit_diffs.jsonl": _format_edit_diff,
    "custom_skills.jsonl": _format_custom_skill,
}


def _scan_once(startup: bool) -> None:
    for path in sorted(KB_ROOT.glob("*/*/feedback/*.jsonl")):
        formatter = FORMATTERS.get(path.name)
        if formatter is None:
            continue

        size = path.stat().st_size
        if path not in _offsets:
            # First time we've seen this file — on startup, skip existing
            # history (jump to end); files that appear later are new KB
            # activity, so show from the top.
            _offsets[path] = size if startup else 0

        if size < _offsets[path]:
            # File was truncated/rotated — reset
            _offsets[path] = 0

        if size == _offsets[path]:
            continue

        with path.open("r", encoding="utf-8") as f:
            f.seek(_offsets[path])
            new_data = f.read()
            _offsets[path] = f.tell()

        dept, family = _role_from_path(path)
        for line in new_data.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            print(formatter(dept, family, rec), flush=True)


def main() -> None:
    print(f"Watching {KB_ROOT} for feedback / approvals / custom skills…")
    print("(Ctrl+C to stop)\n")
    _scan_once(startup=True)
    try:
        while True:
            time.sleep(POLL_SECONDS)
            _scan_once(startup=False)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
