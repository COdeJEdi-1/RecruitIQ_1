"""
Feedback Learning Engine — Arvind JD Generator

Stores and retrieves two types of learning signals (single-variant generation
at temperature 0.9 — there is no variant selection signal):
  1. Edit diff          — what the user changed before approving
  2. Explicit feedback  — star rating, section scores, tags, free text

Builds a Feedback Digest per dept/role/yoe_band that is injected into
Layer 3 of future prompts for the same combination.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

KB_ROOT = Path(__file__).parent / "kb"

# ── helpers ──────────────────────────────────────────────────────────────────

def _feedback_dir(dept: str, family: str) -> Path:
    d = KB_ROOT / dept / family / "feedback"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _append_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records


def _update_version(dept: str, family: str, field: str) -> None:
    """Bump a counter in version.yaml."""
    import yaml
    vpath = KB_ROOT / dept / family / "version.yaml"
    if not vpath.exists():
        return
    data = yaml.safe_load(vpath.read_text()) or {}
    if field in data and isinstance(data[field], (int, float)):
        data[field] += 1
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    vpath.write_text(yaml.dump(data, allow_unicode=True))


# ── Signal 2: Edit diff ───────────────────────────────────────────────────────

def compute_edit_ratio(original: str, final: str) -> float:
    """
    Simple character-level edit ratio.
    0.0 = no changes, 1.0 = completely rewritten.
    """
    if not original:
        return 1.0
    orig_len = len(original)
    final_len = len(final)
    # Levenshtein approximation via difflib
    import difflib
    matcher = difflib.SequenceMatcher(None, original, final)
    ratio = matcher.ratio()
    return round(1.0 - ratio, 3)


def summarise_diff(original: str, final: str) -> str:
    """
    Produce a human-readable summary of what changed.
    Uses simple line-diff — no LLM call to keep it fast.
    """
    import difflib
    orig_lines = original.splitlines()
    final_lines = final.splitlines()
    diff = list(difflib.unified_diff(orig_lines, final_lines, lineterm="", n=0))
    added = [l[1:].strip() for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l[1:].strip() for l in diff if l.startswith("-") and not l.startswith("---")]
    parts = []
    if added:
        parts.append(f"Added: {'; '.join(added[:3])}{'...' if len(added) > 3 else ''}")
    if removed:
        parts.append(f"Removed: {'; '.join(removed[:3])}{'...' if len(removed) > 3 else ''}")
    return " | ".join(parts) if parts else "No significant changes."


def store_edit_diff(
    dept: str,
    family: str,
    yoe_band: str,
    jd_id: str,
    generation_id: str,
    original_text: str,
    final_text: str,
    role_title: str,
    user_email: str = "",
) -> float:
    """Stores the edit diff and returns the edit_ratio."""
    ratio = compute_edit_ratio(original_text, final_text)
    summary = summarise_diff(original_text, final_text)

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "jd_id": jd_id,
        "generation_id": generation_id,
        "dept": dept,
        "family": family,
        "yoe_band": yoe_band,
        "role_title": role_title,
        "edit_ratio": ratio,
        "diff_summary": summary,
        "user_email": user_email,
    }
    path = _feedback_dir(dept, family) / "edit_diffs.jsonl"
    _append_jsonl(path, record)

    # Update version.yaml edit ratio trend
    import yaml
    vpath = KB_ROOT / dept / family / "version.yaml"
    if vpath.exists():
        data = yaml.safe_load(vpath.read_text()) or {}
        trend = data.get("edit_ratio_trend", [])
        trend.append(round(ratio, 3))
        data["edit_ratio_trend"] = trend[-20:]  # keep last 20
        data["approved_jds_count"] = data.get("approved_jds_count", 0) + 1
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        vpath.write_text(yaml.dump(data, allow_unicode=True))

    return ratio


# ── Signal 3: Explicit feedback ───────────────────────────────────────────────

def store_explicit_feedback(
    dept: str,
    family: str,
    yoe_band: str,
    jd_id: str,
    overall_rating: int,            # 1–5
    section_ratings: dict,          # {"role_summary": 4, "responsibilities": 5, ...}
    positive_tags: list[str],
    improvement_tags: list[str],
    free_text: str,
    better_than_manual: str,        # "yes" | "about_the_same" | "no"
    role_title: str,
    user_email: str = "",
) -> None:
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "jd_id": jd_id,
        "dept": dept,
        "family": family,
        "yoe_band": yoe_band,
        "role_title": role_title,
        "overall_rating": overall_rating,
        "section_ratings": section_ratings,
        "positive_tags": positive_tags,
        "improvement_tags": improvement_tags,
        "free_text": free_text,
        "better_than_manual": better_than_manual,
        "user_email": user_email,
    }
    path = _feedback_dir(dept, family) / "feedback_log.jsonl"
    _append_jsonl(path, record)

    # Update version.yaml
    import yaml
    vpath = KB_ROOT / dept / family / "version.yaml"
    if vpath.exists():
        data = yaml.safe_load(vpath.read_text()) or {}
        data["feedback_submissions_count"] = data.get("feedback_submissions_count", 0) + 1
        # Rolling avg rating
        prev_avg = data.get("avg_quality_rating") or overall_rating
        count = data["feedback_submissions_count"]
        data["avg_quality_rating"] = round(
            (prev_avg * (count - 1) + overall_rating) / count, 2
        )
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        vpath.write_text(yaml.dump(data, allow_unicode=True))


# ── Feedback Digest builder ───────────────────────────────────────────────────

def build_feedback_digest(dept: str, family: str, yoe_band: str) -> str:
    """
    Compiles both signal types into a plain-text digest for
    injection into the Layer 3 prompt context.
    Returns empty string if no feedback exists yet.
    """
    fdir = _feedback_dir(dept, family)

    # --- edit diffs ---
    diffs = [r for r in _read_jsonl(fdir / "edit_diffs.jsonl") if r.get("yoe_band") == yoe_band]
    avg_edit_ratio = (
        round(sum(r["edit_ratio"] for r in diffs) / len(diffs), 3) if diffs else None
    )
    diff_summaries = [r["diff_summary"] for r in diffs[-5:] if r.get("diff_summary")]

    # --- explicit feedback ---
    feedbacks = [r for r in _read_jsonl(fdir / "feedback_log.jsonl") if r.get("yoe_band") == yoe_band]
    if not feedbacks and not diffs:
        return ""

    avg_rating = (
        round(sum(r["overall_rating"] for r in feedbacks) / len(feedbacks), 1)
        if feedbacks else None
    )
    all_pos_tags = [t for r in feedbacks for t in r.get("positive_tags", [])]
    all_imp_tags = [t for r in feedbacks for t in r.get("improvement_tags", [])]
    free_texts = [r["free_text"] for r in feedbacks[-3:] if r.get("free_text", "").strip()]

    # Build digest string
    lines = [
        f"--- FEEDBACK SIGNALS ({dept}/{family} · {yoe_band} years) ---",
        f"Based on {len(feedbacks)} explicit feedback submission(s) and {len(diffs)} approved JD(s).",
    ]

    if avg_rating is not None:
        lines.append(f"Average quality rating: {avg_rating}/5 — target 4.5+")
    if avg_edit_ratio is not None:
        lines.append(f"Average edit ratio: {avg_edit_ratio} (0=no edits, 1=fully rewritten). Target <0.10.")

    if all_pos_tags:
        from collections import Counter
        top_pos = [t for t, _ in Counter(all_pos_tags).most_common(5)]
        lines.append(f"What users approved: {', '.join(top_pos)}")

    if all_imp_tags:
        from collections import Counter
        top_imp = [t for t, _ in Counter(all_imp_tags).most_common(5)]
        lines.append(f"What users changed: {', '.join(top_imp)}")

    if diff_summaries:
        lines.append("Recent edit patterns:")
        for s in diff_summaries[:3]:
            lines.append(f"  · {s}")

    if free_texts:
        lines.append("Direct user instructions for next generation:")
        for t in free_texts:
            lines.append(f"  · {t}")

    return "\n".join(lines)


# ── Admin analytics helpers ───────────────────────────────────────────────────

def get_analytics_summary() -> list[dict]:
    """
    Returns a list of per role-family summary dicts for the admin analytics page.
    """
    import yaml
    summaries = []
    for dept_dir in sorted(KB_ROOT.iterdir()):
        if not dept_dir.is_dir():
            continue
        for family_dir in sorted(dept_dir.iterdir()):
            if not family_dir.is_dir():
                continue
            vpath = family_dir / "version.yaml"
            if not vpath.exists():
                continue
            data = yaml.safe_load(vpath.read_text()) or {}
            summaries.append({
                "dept": dept_dir.name,
                "family": family_dir.name,
                "version": data.get("current_version", "v1.0"),
                "approved_jds": data.get("approved_jds_count", 0),
                "feedback_count": data.get("feedback_submissions_count", 0),
                "avg_rating": data.get("avg_quality_rating"),
                "edit_ratio_trend": data.get("edit_ratio_trend", []),
                "last_updated": data.get("last_updated", ""),
            })
    return summaries
