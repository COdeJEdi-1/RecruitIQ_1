"""
seed_supabase.py — one-time script to populate MySQL tables from the
existing filesystem KB (kb/ directory).

Run once after applying the MySQL schema (see database/init_db.py):
  python3 seed_supabase.py

Requires MySQL connection configured via Config (see config.py / .env).
Safe to re-run (all upserts are idempotent).
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask

from config import Config
from database.db import init_engine
from database.models import RoleTaxonomy, SampleJd
from services.kb_service import upsert_sample_jd, KB_ROOT


def seed():
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

                # Find (but don't yet create) role_taxonomy, so we can look up
                # taxonomy_id for the dedup check below. upsert_sample_jd()
                # performs the actual find-or-create/update when we call it.
                taxonomy = RoleTaxonomy.query.filter_by(
                    department=dept, role_family=family, yoe_band=yoe_band
                ).first()
                taxonomy_id = taxonomy.id if taxonomy else None

                # Skip if already seeded (check if it already exists by
                # metadata->jd_id to avoid dups)
                jd_id_meta = meta.get("jd_id", "")
                if taxonomy_id and jd_id_meta:
                    existing = SampleJd.query.filter_by(taxonomy_id=taxonomy_id).filter(
                        SampleJd.sample_metadata["jd_id"].as_string() == jd_id_meta
                    ).first()
                    if existing:
                        skipped += 1
                        continue

                ok = upsert_sample_jd(
                    department=dept,
                    division=division or "",
                    role_family=family,
                    yoe_band=yoe_band,
                    seniority_label=seniority_lab,
                    jd_text=jd_text,
                    metadata=meta,
                    added_by=meta.get("approved_by", "seed_script"),
                )

                if not ok:
                    print(f"  WARN: mirror failed for {dept}/{family}/{yoe_band}")
                    skipped += 1
                    continue

                seeded += 1
                print(f"  ✓ {dept}/{family}/{yoe_band} — {jd_file.name}")

    print(f"\nDone — seeded: {seeded}, skipped/no-text: {skipped}")


if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(Config)
    init_engine(app)
    with app.app_context():
        seed()
