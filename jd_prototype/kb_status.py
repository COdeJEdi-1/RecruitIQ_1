"""
Shows the current state of the knowledge base:
- departments, role families, and sample JD counts per level
- presence of skills_taxonomy.yaml and tone_guide.txt
"""

from pathlib import Path

KB_ROOT = Path(__file__).parent / "kb"
LEVELS = ["junior", "mid", "senior", "lead"]


def main() -> None:
    print("\n=== Knowledge Base Status ===\n")

    if not KB_ROOT.exists():
        print("  KB directory not found.")
        return

    for dept_dir in sorted(KB_ROOT.iterdir()):
        if not dept_dir.is_dir():
            continue
        print(f"Department: {dept_dir.name}")

        for family_dir in sorted(dept_dir.iterdir()):
            if not family_dir.is_dir():
                continue
            print(f"  Role Family: {family_dir.name}")

            has_taxonomy = (family_dir / "skills_taxonomy.yaml").exists()
            has_tone = (family_dir / "tone_guide.txt").exists()
            print(f"    skills_taxonomy.yaml : {'✓' if has_taxonomy else '✗ MISSING'}")
            print(f"    tone_guide.txt       : {'✓' if has_tone else '✗ MISSING'}")

            sample_dir = family_dir / "sample_jds"
            if sample_dir.exists():
                counts = {level: 0 for level in LEVELS}
                for jd_file in sample_dir.iterdir():
                    if not jd_file.name.endswith(".txt"):
                        continue
                    for level in LEVELS:
                        if jd_file.name.startswith(level):
                            counts[level] += 1
                            break
                total = sum(counts.values())
                level_summary = ", ".join(f"{l.capitalize()}: {c}" for l, c in counts.items() if c > 0)
                print(f"    Sample JDs           : {total} total ({level_summary})")
            else:
                print(f"    Sample JDs           : 0 (no sample_jds/ folder)")
        print()


if __name__ == "__main__":
    main()
