"""
seed_supabase.py — one-time script to populate Supabase tables from the
existing filesystem KB (kb/ directory).

Run once after applying supabase_schema_v2.sql:
  python3 seed_supabase.py

Requires SUPABASE_SERVICE_ROLE_KEY to be set in .env.
Safe to re-run (all upserts are idempotent).
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from supabase_kb import get_service_client, SUPABASE_DB_ENABLED, KB_ROOT

def seed():
    if not SUPABASE_DB_ENABLED:
        print("ERROR: SUPABASE_SERVICE_ROLE_KEY not set in .env — cannot seed.")
        sys.exit(1)

    client = get_service_client()
    print(f"Seeding from {KB_ROOT} …")
    seeded = 0
    skipped = 0

    for dept_dir in sorted(KB_ROOT.iterdir()):
        if not dept_dir.is_dir():
            continue
        dept = dept_dir.name

        for family_dir in sorted(dept_dir.iterdir()):
            if not family_dir.is_dir():
                continue
            family = family_dir.name
            sample_dir = family_dir / "sample_jds"
            if not sample_dir.exists():
                continue

            for jd_file in sorted(sample_dir.glob("*.txt")):
                raw = jd_file.read_text(encoding="utf-8").strip()
                first_line = raw.split("\n")[0]
                try:
                    meta = json.loads(first_line)
                except Exception:
                    skipped += 1
                    continue

                yoe_band      = meta.get("yoe_band", "2-5")
                role_family   = meta.get("role_family", family.replace("_", " ").title())
                division      = meta.get("division", "")
                seniority_lab = meta.get("seniority_label", "")
                jd_text_lines = raw.split("\n")
                sep_idx = next((i for i, ln in enumerate(jd_text_lines) if ln.strip() == "---"), None)
                jd_text = "\n".join(jd_text_lines[sep_idx + 1:]).strip() if sep_idx else "\n".join(jd_text_lines[1:]).strip()

                if not jd_text:
                    skipped += 1
                    continue

                # Upsert into role_taxonomy
                tax_res = client.table("role_taxonomy").upsert({
                    "department":      dept,
                    "division":        division or "",
                    "role_family":     family,
                    "yoe_band":        yoe_band,
                    "seniority_label": seniority_lab,
                }, on_conflict="department,role_family,yoe_band").execute()

                taxonomy_id = None
                if tax_res.data:
                    taxonomy_id = tax_res.data[0].get("id")
                else:
                    # Fetch existing
                    rows = (client.table("role_taxonomy")
                            .select("id")
                            .eq("department", dept)
                            .eq("role_family", family)
                            .eq("yoe_band", yoe_band)
                            .execute().data)
                    if rows:
                        taxonomy_id = rows[0]["id"]

                if not taxonomy_id:
                    print(f"  WARN: no taxonomy_id for {dept}/{family}/{yoe_band}")
                    skipped += 1
                    continue

                # Insert sample JD (check if already exists by metadata->jd_id to avoid dups)
                jd_id_meta = meta.get("jd_id", "")
                if jd_id_meta:
                    existing = (client.table("sample_jds")
                                .select("id")
                                .eq("taxonomy_id", taxonomy_id)
                                .eq("metadata->>jd_id", jd_id_meta)
                                .execute().data)
                    if existing:
                        skipped += 1
                        continue

                client.table("sample_jds").insert({
                    "taxonomy_id": taxonomy_id,
                    "jd_text":     jd_text,
                    "metadata":    meta,
                    "added_by":    meta.get("approved_by", "seed_script"),
                }).execute()

                seeded += 1
                print(f"  ✓ {dept}/{family}/{yoe_band} — {jd_file.name}")

    print(f"\nDone — seeded: {seeded}, skipped/no-text: {skipped}")


if __name__ == "__main__":
    seed()
