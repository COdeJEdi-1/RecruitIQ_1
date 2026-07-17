"""
Generates seed_samples.py by reading back every skills_taxonomy.yaml and
sample_jds/*.txt file from kb_master/ — per the KB Builder spec's
"extract all data from the YAML and TXT files you just created" instruction.

Run after build_kb_master.py: python3 generate_seed_samples.py
"""

import json
from pathlib import Path

import yaml

KB_ROOT = Path(__file__).parent / "kb_master"
OUTPUT = Path(__file__).parent / "seed_samples.py"

BAND_ORDER = ["junior", "mid", "senior", "lead", "executive"]


def collect_taxonomies():
    """One entry per populated department + role_family + yoe_band."""
    entries = []
    for tax_file in sorted(KB_ROOT.glob("*/*/skills_taxonomy.yaml")):
        data = yaml.safe_load(tax_file.read_text(encoding="utf-8"))
        dept = data["department"]
        division = data["division"]
        role_family = data["role_family"]
        for band_key in BAND_ORDER:
            band = data["experience_bands"].get(band_key)
            if not band or band.get("data_available") is False:
                continue
            entries.append({
                "department": dept,
                "division": division,
                "role_family": role_family,
                "yoe_band": band["years"],
                "seniority_label": band["label"],
            })
    return entries


def collect_sample_jds():
    """One entry per sample JD .txt file, keyed to its taxonomy entry."""
    entries = []
    for jd_file in sorted(KB_ROOT.glob("*/*/sample_jds/*.txt")):
        raw = jd_file.read_text(encoding="utf-8")
        if "---METADATA---" not in raw or "---END METADATA---" not in raw:
            continue
        meta_str = raw.split("---METADATA---", 1)[1].split("---END METADATA---", 1)[0].strip()
        body = raw.split("---END METADATA---", 1)[1].strip()
        meta = json.loads(meta_str)
        entries.append({
            "taxonomy_key": (meta["department"], meta["role_family"], meta["yoe_band"]),
            "jd_text": body,
            "metadata": {
                "source_doc": meta["source_doc"],
                "extracted_date": meta["extracted_date"],
            },
        })
    return entries


def py_repr_taxonomies(entries: list) -> str:
    lines = ["TAXONOMIES = ["]
    for t in entries:
        lines.append("    {")
        lines.append(f"        \"department\":      {t['department']!r},")
        lines.append(f"        \"division\":        {t['division']!r},")
        lines.append(f"        \"role_family\":     {t['role_family']!r},")
        lines.append(f"        \"yoe_band\":        {t['yoe_band']!r},")
        lines.append(f"        \"seniority_label\": {t['seniority_label']!r},")
        lines.append("    },")
    lines.append("]")
    return "\n".join(lines)


def py_repr_sample_jds(entries: list) -> str:
    lines = ["SAMPLE_JDS = ["]
    for s in entries:
        lines.append("    {")
        lines.append(f"        \"taxonomy_key\": {s['taxonomy_key']!r},")
        lines.append(f"        \"jd_text\": {s['jd_text']!r},")
        lines.append(f"        \"metadata\": {s['metadata']!r},")
        lines.append("    },")
    lines.append("]")
    return "\n".join(lines)


def main():
    taxonomies = collect_taxonomies()
    sample_jds = collect_sample_jds()

    taxonomies_src = py_repr_taxonomies(taxonomies)
    sample_jds_src = py_repr_sample_jds(sample_jds)

    script = f'''"""
Auto-generated from KB files built from Arvind uploaded documents.
Run: python seed_samples.py
Requires: MySQL connection configured via Config / .env (see config.py).
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask

from config import Config
from database.db import init_engine
from services.kb_service import upsert_sample_jd

{taxonomies_src}

{sample_jds_src}

def run():
    print("Seeding role taxonomy...")
    tax_map = {{}}
    for t in TAXONOMIES:
        key = (t["department"], t["role_family"], t["yoe_band"])
        tax_map[key] = t
        print(f"  ✓ {{t['department']}} | {{t['role_family']}} | {{t['yoe_band']}}")

    print(f"\\nTaxonomy seeded: {{len(TAXONOMIES)}} entries\\n")
    print("Seeding sample JDs...")

    seeded = 0
    for s in SAMPLE_JDS:
        key = s["taxonomy_key"]
        taxonomy = tax_map.get(key)
        if not taxonomy:
            print(f"  ✗ No taxonomy for {{key}} — skipping")
            continue
        ok = upsert_sample_jd(
            department=taxonomy["department"],
            division=taxonomy["division"],
            role_family=taxonomy["role_family"],
            yoe_band=taxonomy["yoe_band"],
            seniority_label=taxonomy["seniority_label"],
            jd_text=s["jd_text"],
            metadata=s.get("metadata", {{}}),
            added_by="seed_script",
        )
        if not ok:
            print(f"  ✗ Mirror failed for {{key[1]}} | {{key[2]}}")
            continue
        seeded += 1
        print(f"  ✓ JD seeded for {{key[1]}} | {{key[2]}}")

    print(f"\\nDone. {{seeded}} sample JDs seeded into MySQL.")


if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(Config)
    init_engine(app)
    with app.app_context():
        run()
'''

    OUTPUT.write_text(script, encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"  TAXONOMIES: {len(taxonomies)} entries")
    print(f"  SAMPLE_JDS: {len(sample_jds)} entries")


if __name__ == "__main__":
    main()
