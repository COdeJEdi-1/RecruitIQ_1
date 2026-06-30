"""
Supabase ↔ kb/ sync layer for the Sample JD Library.

The filesystem (kb/) remains the source of truth and the fast read path for
the running app — this module mirrors approvals into Supabase tables
(role_taxonomy, sample_jds — see supabase_schema.sql) for durable storage,
analytics, and multi-instance deployments. All writes use the service_role
key (bypasses RLS) and are best-effort: a Supabase outage must never break
the working filesystem-based flow.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

KB_ROOT = Path(__file__).parent / "kb"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

SUPABASE_DB_ENABLED = bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)

_service_client = None


def get_service_client():
    """Lazily create the service-role Supabase client (bypasses RLS). None if not configured."""
    global _service_client
    if not SUPABASE_DB_ENABLED:
        return None
    if _service_client is None:
        from supabase import create_client
        _service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _service_client


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
    Best-effort mirror of one approved JD into Supabase. Returns True on success,
    False (silently) on any failure — callers should never let this block the
    filesystem-based approval flow.
    """
    client = get_service_client()
    if client is None:
        return False
    try:
        tax_result = client.table("role_taxonomy").upsert(
            {
                "department": department,
                "division": division,
                "role_family": role_family,
                "yoe_band": yoe_band,
                "seniority_label": seniority_label,
            },
            on_conflict="department,role_family,yoe_band",
        ).execute()
        if not tax_result.data:
            return False
        taxonomy_id = tax_result.data[0]["id"]

        client.table("sample_jds").insert({
            "taxonomy_id": taxonomy_id,
            "jd_text": jd_text,
            "metadata": metadata,
            "added_by": added_by,
        }).execute()
        return True
    except Exception as exc:
        print(f"[supabase_kb] mirror failed (non-fatal): {exc}")
        return False


def fetch_sample_jds(dept: str = "", family: str = "", yoe_band: str = "") -> list[dict] | None:
    """
    Read sample JDs from Supabase, filtered by dept/family/yoe_band (all optional).
    Returns None if Supabase isn't configured (caller should fall back to filesystem).
    """
    client = get_service_client()
    if client is None:
        return None
    try:
        query = client.table("sample_jds").select(
            "id, jd_text, metadata, added_by, created_at, "
            "role_taxonomy(department, division, role_family, yoe_band, seniority_label)"
        )
        result = query.execute()
        rows = result.data or []

        out = []
        for row in rows:
            tax = row.get("role_taxonomy") or {}
            if dept and tax.get("department", "").lower() != dept.lower():
                continue
            if family and tax.get("role_family", "").lower() != family.lower():
                continue
            if yoe_band and tax.get("yoe_band") != yoe_band:
                continue
            out.append({
                "id": row["id"],
                "department": tax.get("department"),
                "division": tax.get("division"),
                "role_family": tax.get("role_family"),
                "yoe_band": tax.get("yoe_band"),
                "seniority_label": tax.get("seniority_label"),
                "jd_text": row["jd_text"],
                "metadata": row.get("metadata") or {},
                "added_by": row.get("added_by"),
                "created_at": row.get("created_at"),
            })
        return out
    except Exception as exc:
        print(f"[supabase_kb] fetch failed, falling back to filesystem: {exc}")
        return None


def mirror_kb_to_supabase() -> dict:
    """
    One-time/backfill bulk sync: walk kb/ and upsert every sample JD into
    Supabase. Run manually: python3 -c "from supabase_kb import mirror_kb_to_supabase; mirror_kb_to_supabase()"
    """
    if not SUPABASE_DB_ENABLED:
        print("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set — skipping sync.")
        return {"synced": 0, "failed": 0}

    synced, failed = 0, 0
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

                ok = upsert_sample_jd(
                    department=dept_dir.name,
                    division="",
                    role_family=meta.get("role_family", family_dir.name),
                    yoe_band=meta.get("yoe_band", ""),
                    seniority_label=meta.get("seniority_label", ""),
                    jd_text=body.strip(),
                    metadata=meta,
                    added_by=meta.get("approved_by", meta.get("approved_by", "kb_seed")),
                )
                if ok:
                    synced += 1
                else:
                    failed += 1

    print(f"Mirror complete: {synced} synced, {failed} failed.")
    return {"synced": synced, "failed": failed}


if __name__ == "__main__":
    mirror_kb_to_supabase()
