"""
SQLAlchemy/MySQL ↔ kb/ sync layer for the Sample JD Library.

Phase 3: replaces supabase_kb.py. The filesystem (kb/) remains the source of
truth and the fast read path for the running app — this module mirrors
approvals into MySQL (role_taxonomy, sample_jds) for durable storage,
analytics, and multi-instance deployments. Writes are best-effort: a DB
outage must never break the working filesystem-based flow.
"""

from __future__ import annotations

import json
from pathlib import Path

from database.db import db
from database.models import RoleTaxonomy, SampleJd

KB_ROOT = Path(__file__).parent.parent / "kb"

# MySQL is a required local dependency in Phase 3 (unlike the optional
# Supabase SaaS it replaces), so the mirror path is always attempted.
KB_DB_ENABLED = True


def upsert_sample_jd(
    department: str,
    division: str,
    role_family: str,
    yoe_band: str,
    seniority_label: str,
    jd_text: str,
    metadata: dict,
    added_by: str = "",
) -> bool:
    """
    Best-effort mirror of one approved JD into MySQL. Returns True on success,
    False (silently) on any failure — callers should never let this block the
    filesystem-based approval flow.
    """
    try:
        taxonomy = RoleTaxonomy.query.filter_by(
            department=department, role_family=role_family, yoe_band=yoe_band
        ).first()
        if taxonomy is None:
            taxonomy = RoleTaxonomy(
                department=department,
                division=division,
                role_family=role_family,
                yoe_band=yoe_band,
                seniority_label=seniority_label,
            )
            db.session.add(taxonomy)
            db.session.flush()
        else:
            taxonomy.division = division
            taxonomy.seniority_label = seniority_label

        sample = SampleJd(
            taxonomy_id=taxonomy.id,
            jd_text=jd_text,
            sample_metadata=metadata,
            added_by=added_by,
        )
        db.session.add(sample)
        db.session.commit()
        return True
    except Exception as exc:
        db.session.rollback()
        print(f"[kb_service] mirror failed (non-fatal): {exc}")
        return False


def fetch_sample_jds(dept: str = "", family: str = "", yoe_band: str = "") -> list[dict] | None:
    """
    Read sample JDs from MySQL, filtered by dept/family/yoe_band (all optional).
    Returns None on failure (caller should fall back to filesystem).
    """
    try:
        q = SampleJd.query.join(RoleTaxonomy, SampleJd.taxonomy_id == RoleTaxonomy.id)
        if dept:
            q = q.filter(db.func.lower(RoleTaxonomy.department) == dept.lower())
        if family:
            q = q.filter(db.func.lower(RoleTaxonomy.role_family) == family.lower())
        if yoe_band:
            q = q.filter(RoleTaxonomy.yoe_band == yoe_band)

        out = []
        for row in q.all():
            tax = row.taxonomy
            out.append({
                "id": row.id,
                "department": tax.department if tax else None,
                "division": tax.division if tax else None,
                "role_family": tax.role_family if tax else None,
                "yoe_band": tax.yoe_band if tax else None,
                "seniority_label": tax.seniority_label if tax else None,
                "jd_text": row.jd_text,
                "metadata": row.sample_metadata or {},
                "added_by": row.added_by,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            })
        return out
    except Exception as exc:
        print(f"[kb_service] fetch failed, falling back to filesystem: {exc}")
        return None


def _already_mirrored(department: str, role_family: str, yoe_band: str, jd_id: str) -> bool:
    """Dedup guard so mirror_kb_to_mysql() is safe to run more than once."""
    if not jd_id:
        return False
    taxonomy = RoleTaxonomy.query.filter_by(
        department=department, role_family=role_family, yoe_band=yoe_band
    ).first()
    if taxonomy is None:
        return False
    return (
        SampleJd.query.filter_by(taxonomy_id=taxonomy.id)
        .filter(SampleJd.sample_metadata["jd_id"] == jd_id)
        .first()
        is not None
    )


def mirror_kb_to_mysql() -> dict:
    """
    One-time/backfill bulk sync: walk kb/ and upsert every sample JD into
    MySQL. Safe to run more than once — skips files already mirrored (by
    jd_id). Run manually: python3 -c "from services.kb_service import mirror_kb_to_mysql; mirror_kb_to_mysql()"
    """
    synced, skipped, failed = 0, 0, 0
    for dept_dir in sorted(KB_ROOT.iterdir()):
        if not dept_dir.is_dir():
            continue
        for family_dir in sorted(dept_dir.iterdir()):
            if not family_dir.is_dir():
                continue
            sample_dir = family_dir / "sample_jds"
            if not sample_dir.exists():
                continue
            for jd_file in sorted(sample_dir.iterdir()):
                if not jd_file.name.endswith(".txt"):
                    continue
                raw = jd_file.read_text(encoding="utf-8").strip()
                if "\n\n---\n\n" not in raw:
                    continue
                meta_str, body = raw.split("\n\n---\n\n", 1)
                try:
                    meta = json.loads(meta_str)
                except Exception:
                    failed += 1
                    continue

                role_family = meta.get("role_family", family_dir.name)
                yoe_band = meta.get("yoe_band", "")
                jd_id = meta.get("jd_id", "")

                if _already_mirrored(dept_dir.name, role_family, yoe_band, jd_id):
                    skipped += 1
                    continue

                ok = upsert_sample_jd(
                    department=dept_dir.name,
                    division="",
                    role_family=role_family,
                    yoe_band=yoe_band,
                    seniority_label=meta.get("seniority_label", ""),
                    jd_text=body.strip(),
                    metadata=meta,
                    added_by=meta.get("approved_by", "kb_seed"),
                )
                if ok:
                    synced += 1
                else:
                    failed += 1

    print(f"Mirror complete: {synced} synced, {skipped} already present, {failed} failed.")
    return {"synced": synced, "skipped": skipped, "failed": failed}


if __name__ == "__main__":
    mirror_kb_to_mysql()
