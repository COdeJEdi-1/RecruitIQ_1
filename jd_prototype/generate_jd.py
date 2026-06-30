"""
JD Generator — Arvind Limited
File-based approach (no vector DB for Phase 1).

Loads all sample JDs and the skills taxonomy for the given role family
directly into the prompt, then calls Groq to generate the JD.

Supports:
  - YoE-banded skills taxonomy with cumulative skill inheritance
  - Single-variant generation at temperature 0.9 (expressive, varied phrasing)
  - Feedback Digest injection from feedback_engine.py
  - All Arvind departments: tech, hr, finance, manufacturing, it, sustainability, retail, quality

Usage:
    python generate_jd.py
    python generate_jd.py --role "QA Manager" --dept quality \
        --family qa_manager --yoe 5-8 --focus "denim, inline inspection"
"""

import argparse
import os
import sys
import uuid
from pathlib import Path

import yaml
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

KB_ROOT = Path(__file__).parent / "kb"

# ── Department / Role Family catalogue ───────────────────────────────────────

# ── Department → Role Family mapping ─────────────────────────────────────────
# Keys = KB folder slug (dept). Values = ordered list of role-family slugs.
# Slugs that have no KB sample JDs yet are still valid — the generator falls
# back to 70% LLM knowledge for those.
DEPARTMENTS = {
    # ── Technology / GCC ─────────────────────────────────────────────────────
    "tech": [
        # Data & Analytics sub-category
        "bi",               # BI & Reporting
        "data_science",     # Data Science & ML
        "data_engineering", # Data Engineering
        # Software Engineering sub-category
        "backend",          # Backend Engineering
        "frontend",         # Frontend / Full-stack
        "sde",              # Software Development (general)
        # Infrastructure & Ops
        "devops",           # DevOps / SRE
        # Quality Engineering
        "qa_automation",    # QA Engineering
        # Product
        "product",          # Product Management
        # Enterprise Applications
        "enterprise_apps",  # ERP / SAP / Power Platform
        # IT Operations
        "it_ops",           # IT Support & Service Desk
    ],
    # ── Human Resources ──────────────────────────────────────────────────────
    "hr": [
        "talent_acquisition",      # Talent Acquisition & Recruiting
        "hrbp",                    # HR Business Partnering
        "learning_development",    # Learning & Development
        "comp_ben",                # Compensation & Benefits
        "payroll_welfare_officer", # Payroll & Welfare
        "industrial_relations",    # Industrial Relations
        "chro",                    # CHRO / HR Leadership
    ],
    # ── Finance & Accounts ───────────────────────────────────────────────────
    "finance": [
        "fpa",              # FP&A
        "accounting",       # Accounting & Statutory Compliance
        "cost_accounting",  # Cost & Management Accounting
        "r2r_manager",      # Record-to-Report (R2R)
        "finance_manager",  # Finance Management
        "treasury",         # Treasury & Cash Management
    ],
    # ── Supply Chain & Logistics ─────────────────────────────────────────────
    "supply_chain": [
        "sourcing_manager",   # Sourcing & Procurement
        "supply_chain_manager", # Supply Chain Management
        "demand_planning",    # Demand & Supply Planning
        "logistics",          # Logistics & Distribution
    ],
    # ── Manufacturing & Production ────────────────────────────────────────────
    "manufacturing": [
        "production_manager",           # Production Management
        "lean_excellence",              # Lean & Process Excellence
        "industrial_engineering",       # Industrial Engineering
        "shift_supervisor_dyeing",      # Dyeing & Processing Operations
        "associate_manager_nonwoven",   # Nonwoven & Technical Textiles
        "trainee_operator",             # Operations Trainee / Operator
    ],
    # ── Quality (textile / manufacturing QA) ─────────────────────────────────
    "quality": [
        "qa_manager",     # QA Management
        "quality_analyst", # Quality Analyst / Inspector
        "lab_technician", # Lab Testing & Certification
    ],
    # ── Sustainability & ESG ─────────────────────────────────────────────────
    "sustainability": [
        "sustainability_reporting", # Sustainability Reporting & ESG
        "esg_analyst",              # ESG Analysis & Compliance
    ],
    # ── Retail Operations ────────────────────────────────────────────────────
    "retail": [
        "store_manager",       # Store Management
        "area_sales_manager",  # Area Sales Management
        "fashion_consultant",  # Fashion Consulting & Styling
    ],
    # ── Sales, Marketing & Brand ─────────────────────────────────────────────
    "sales_marketing": [
        "brand_manager",          # Brand Management
        "performance_marketing",  # Performance Marketing
        "digital_marketing",      # Digital Marketing & Content
        "sales_manager_home_linen", # Sales (Home & Linen)
        "chief_revenue_officer",  # Revenue Leadership (CRO)
        "ceo_brand",              # Brand CEO / P&L Leadership
    ],
    # ── Design & Merchandising ───────────────────────────────────────────────
    "design_merchandising": [
        "merchandiser",      # Merchandising & Buying
        "fashion_designer",  # Fashion Design
        "product_developer", # Product Development
    ],
    # ── Environmental Solutions (Arvind Envisol) ─────────────────────────────
    "environmental": [
        "process_engineer",      # Process Engineering
        "project_manager_etp",   # ETP / Water Treatment Projects
    ],
    # ── Telecom & Digital (Arvind Syntel) ────────────────────────────────────
    "telecom": [
        "enterprise_sales_manager",    # Enterprise Sales
        "presales_network_engineer",   # Presales & Network Engineering
    ],
    # ── IT (legacy — kept for KB backward compat) ────────────────────────────
    "it": [
        "sap_consultant",       # SAP Consulting
        "it_manager_digital",   # IT Management & Digital
        "data_analyst_powerbi", # Data Analytics (Power BI)
    ],
}

# ── Division groupings for the UI dropdown ────────────────────────────────────
DIVISIONS = {
    "GCC / Technology":                             ["tech"],
    "Corporate / Shared Services":                  ["hr", "finance"],
    "Manufacturing & Operations (Textiles)":        ["manufacturing", "quality", "supply_chain", "sustainability"],
    "Arvind Fashions (Brands & Retail)":            ["retail", "sales_marketing", "design_merchandising"],
    "Arvind Envisol & Syntel":                      ["environmental", "telecom"],
    "IT (Legacy)":                                  ["it"],
}

# ── Display-name formatting ───────────────────────────────────────────────────
# Rule: every word Title Case EXCEPT known acronyms/abbreviations → ALL CAPS.
_KNOWN_ACRONYMS = {
    # Roles / grades
    "hr", "it", "qa", "qc", "ceo", "cfo", "coo", "cio", "cto", "cro",
    "vp", "svp", "avp", "gm", "dgm", "chro", "md",
    # Systems & tech
    "sap", "erp", "crm", "bi", "ml", "ai", "rpa", "sde", "sre", "devops",
    "etp", "ehs",
    # Finance / process
    "r2r", "p2p", "o2c", "fpa", "gst", "tds", "kpi", "sla", "sop",
    # Other Arvind-specific
    "gcc", "esg", "csr", "ir", "er", "scm", "mdm", "oem", "ngo",
    "hrbp", "atira",
}

# Explicit overrides where slug → auto-format doesn't produce the right label.
# These take priority over the generic _title_word conversion.
FAMILY_DISPLAY_NAMES: dict[str, str] = {
    # Tech — Data & Analytics
    "bi":                        "BI & Reporting",
    "data_science":              "Data Science & ML",
    "data_engineering":          "Data Engineering",
    # Tech — Software Engineering
    "backend":                   "Backend Engineering",
    "frontend":                  "Frontend / Full-stack",
    "sde":                       "Software Development",
    # Tech — Infrastructure
    "devops":                    "DevOps / SRE",
    # Tech — Quality
    "qa_automation":             "QA Engineering",
    # Tech — Product
    "product":                   "Product Management",
    # Tech — Enterprise Apps
    "enterprise_apps":           "Enterprise Applications",
    "it_ops":                    "IT Operations & Support",
    # HR
    "talent_acquisition":        "Talent Acquisition",
    "hrbp":                      "HR Business Partnering",
    "learning_development":      "Learning & Development",
    "comp_ben":                  "Compensation & Benefits",
    "payroll_welfare_officer":   "Payroll & Welfare",
    "industrial_relations":      "Industrial Relations",
    "chro":                      "CHRO / HR Leadership",
    # Finance
    "fpa":                       "FP&A",
    "accounting":                "Accounting & Statutory Compliance",
    "cost_accounting":           "Cost & Management Accounting",
    "r2r_manager":               "Record-to-Report (R2R)",
    "finance_manager":           "Finance Management",
    "treasury":                  "Treasury & Cash Management",
    # Supply Chain
    "sourcing_manager":          "Sourcing & Procurement",
    "supply_chain_manager":      "Supply Chain Management",
    "demand_planning":           "Demand & Supply Planning",
    "logistics":                 "Logistics & Distribution",
    # Manufacturing
    "production_manager":        "Production Management",
    "lean_excellence":           "Lean & Process Excellence",
    "industrial_engineering":    "Industrial Engineering",
    "shift_supervisor_dyeing":   "Dyeing & Processing Operations",
    "associate_manager_nonwoven":"Nonwoven & Technical Textiles",
    "trainee_operator":          "Operations Trainee / Operator",
    # Quality
    "qa_manager":                "QA Management",
    "quality_analyst":           "Quality Analyst / Inspector",
    "lab_technician":            "Lab Testing & Certification",
    # Sustainability
    "sustainability_reporting":  "Sustainability Reporting & ESG",
    "esg_analyst":               "ESG Analysis & Compliance",
    # Retail
    "store_manager":             "Store Management",
    "area_sales_manager":        "Area Sales Management",
    "fashion_consultant":        "Fashion Consulting & Styling",
    # Sales & Marketing
    "brand_manager":             "Brand Management",
    "performance_marketing":     "Performance Marketing",
    "digital_marketing":         "Digital Marketing & Content",
    "sales_manager_home_linen":  "Sales — Home & Linen",
    "chief_revenue_officer":     "Revenue Leadership (CRO)",
    "ceo_brand":                 "Brand CEO / P&L Leadership",
    # Design & Merchandising
    "merchandiser":              "Merchandising & Buying",
    "fashion_designer":          "Fashion Design",
    "product_developer":         "Product Development",
    # Environmental
    "process_engineer":          "Process Engineering",
    "project_manager_etp":       "ETP / Water Treatment Projects",
    # Telecom
    "enterprise_sales_manager":  "Enterprise Sales",
    "presales_network_engineer": "Presales & Network Engineering",
    # IT (legacy)
    "sap_consultant":            "SAP Consulting",
    "it_manager_digital":        "IT Management & Digital",
    "data_analyst_powerbi":      "Data Analytics (Power BI)",
}

DEPARTMENT_DISPLAY_NAMES: dict[str, str] = {
    "tech":               "Technology / GCC",
    "hr":                 "Human Resources",
    "finance":            "Finance & Accounts",
    "supply_chain":       "Supply Chain & Logistics",
    "manufacturing":      "Manufacturing & Production",
    "quality":            "Quality Assurance (Textile)",
    "sustainability":     "Sustainability & ESG",
    "retail":             "Retail Operations",
    "sales_marketing":    "Sales, Marketing & Brand",
    "design_merchandising": "Design & Merchandising",
    "environmental":      "Environmental Solutions",
    "telecom":            "Telecom & Digital",
    "it":                 "IT (Legacy)",
}


def _title_word(word: str) -> str:
    """Title-case a single word; ALL CAPS for known acronyms."""
    if word.lower() in _KNOWN_ACRONYMS:
        return word.upper()
    return word[:1].upper() + word[1:].lower() if word else word


def display_name(slug: str) -> str:
    """Canonical display-name for a dept or role-family slug.
    Checks the explicit override dict first, falls back to auto-formatting."""
    if slug in FAMILY_DISPLAY_NAMES:
        return FAMILY_DISPLAY_NAMES[slug]
    if slug in DEPARTMENT_DISPLAY_NAMES:
        return DEPARTMENT_DISPLAY_NAMES[slug]
    words = slug.replace("_", " ").replace("-", " ").split()
    return " ".join(_title_word(w) for w in words)


# ── Department caps labels for the generator dropdown header ──────────────────
DEPARTMENT_CAPS_LABELS: dict[str, str] = {
    "tech":               "TECHNOLOGY / GCC",
    "hr":                 "HUMAN RESOURCES",
    "finance":            "FINANCE & ACCOUNTS",
    "supply_chain":       "SUPPLY CHAIN & LOGISTICS",
    "manufacturing":      "MANUFACTURING & PRODUCTION",
    "quality":            "QUALITY ASSURANCE (TEXTILE)",
    "sustainability":     "SUSTAINABILITY & ESG",
    "retail":             "RETAIL OPERATIONS",
    "sales_marketing":    "SALES, MARKETING & BRAND",
    "design_merchandising": "DESIGN & MERCHANDISING",
    "environmental":      "ENVIRONMENTAL SOLUTIONS",
    "telecom":            "TELECOM & DIGITAL",
    "it":                 "IT (LEGACY)",
}

# ── Division groups for the generator dropdown ────────────────────────────────
DIVISION_GROUPS = [
    ("GCC / Technology",                     ["tech"]),
    ("Corporate / Shared Services",          ["hr", "finance"]),
    ("Manufacturing & Operations",           ["manufacturing", "quality", "supply_chain", "sustainability"]),
    ("Arvind Fashions (Brands & Retail)",    ["retail", "sales_marketing", "design_merchandising"]),
    ("Arvind Envisol & Syntel",              ["environmental", "telecom"]),
    ("IT (Legacy)",                          ["it"]),
]

DIVISION_GROUPS_CAPS = DIVISION_GROUPS   # backward compat alias


def get_department_caps_groups() -> list[dict]:
    """Build the generator Department dropdown: list of {division, departments:[{value,label}]}."""
    groups = []
    for division_label, dept_slugs in DIVISION_GROUPS:
        depts = []
        for slug in dept_slugs:
            real_key = next((k for k in DEPARTMENTS if k.lower() == slug), slug)
            label = DEPARTMENT_CAPS_LABELS.get(slug, display_name(slug))
            depts.append({"value": real_key, "label": label})
        groups.append({"division": division_label, "departments": depts})
    return groups


# ── YoE bands ─────────────────────────────────────────────────────────────────

YOE_BANDS = ["0-2", "2-5", "5-8", "8-12", "12+"]

YOE_LABELS = {
    "0-2":  "Junior (0–2 years)",
    "2-5":  "Mid (2–5 years)",
    "5-8":  "Senior (5–8 years)",
    "8-12": "Lead / Manager (8–12 years)",
    "12+":  "Director / VP (12+ years)",
}

# Verb calibration per band — injected into every prompt
YOE_LANGUAGE = {
    "0-2":  "assist, support, learn, contribute, execute under guidance",
    "2-5":  "own, build, deliver, coordinate, improve independently",
    "5-8":  "lead, design, drive, mentor, define standards",
    "8-12": "own end-to-end, set strategy, build teams, manage stakeholders",
    "12+":  "define vision, own P&L, lead transformation, build organisation",
}

COMPANY_NAME = os.getenv("COMPANY_NAME", "Arvind Limited")

# ── Legacy seniority levels kept for backward-compat with Phase 1 API ────────
SENIORITY_LEVELS = ["Junior", "Mid", "Senior", "Lead"]

# Map legacy seniority → YoE band (used when old /api/generate endpoint is called)
SENIORITY_TO_YOE = {
    "Junior": "0-2",
    "Mid":    "2-5",
    "Senior": "5-8",
    "Lead":   "8-12",
}


# ── KB loaders ────────────────────────────────────────────────────────────────

def load_tone_guide(dept: str, family: str) -> str:
    path = KB_ROOT / dept / family / "tone_guide.txt"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def load_skills_taxonomy(dept: str, family: str) -> dict:
    """Return the parsed YAML taxonomy dict, or empty dict if not found."""
    path = KB_ROOT / dept / family / "skills_taxonomy.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_sample_jds(dept: str, family: str, yoe_band: str) -> list[str]:
    """
    Return all sample JD texts for the closest-matching YoE band.
    Falls back to any sample JD if no band-specific ones exist.
    """
    sample_dir = KB_ROOT / dept / family / "sample_jds"
    if not sample_dir.exists():
        return []

    # Map band to a short prefix used in file names
    band_prefix_map = {
        "0-2":  "junior",
        "2-5":  "mid",
        "5-8":  "senior",
        "8-12": "lead",
        "12+":  "director",
    }
    prefix = band_prefix_map.get(yoe_band, "")

    jds = []
    for jd_file in sorted(sample_dir.iterdir()):
        if not jd_file.name.endswith(".txt"):
            continue
        if prefix and not jd_file.name.startswith(prefix):
            continue
        raw = jd_file.read_text(encoding="utf-8").strip()
        lines = raw.split("\n")
        body_lines = [l for l in lines if not l.startswith("{") and l != "---"]
        jds.append("\n".join(body_lines).strip())

    # Fallback: load all sample JDs regardless of band
    if not jds:
        for jd_file in sorted(sample_dir.iterdir()):
            if not jd_file.name.endswith(".txt"):
                continue
            raw = jd_file.read_text(encoding="utf-8").strip()
            lines = raw.split("\n")
            body_lines = [l for l in lines if not l.startswith("{") and l != "---"]
            jds.append("\n".join(body_lines).strip())

    return jds


# ── YoE / Skills helpers ──────────────────────────────────────────────────────

def compute_cumulative_skills(taxonomy: dict, yoe_band: str) -> dict:
    """
    Accumulate skills from the experience_bands dict for all bands up to
    and including the requested yoe_band.

    Supports two YAML shapes:
      Shape A — dict keyed by band name (junior/mid/senior/lead/executive)
                with fields: core_skills, progressive_skills, leadership_skills,
                              arvind_specific, must_have, nice_to_have, responsibilities
      Shape B — list of dicts with a "band" key (0-2, 2-5, …)
                with fields: must_have, nice_to_have, responsibilities

    Returns:
      {
        "must_have": [...],
        "nice_to_have": [...],
        "responsibilities": [...],
      }
    """
    # Band name → YoE band mapping (for Shape A)
    NAME_TO_YOE = {
        "junior":    "0-2",
        "mid":       "2-5",
        "senior":    "5-8",
        "lead":      "8-12",
        "executive": "12+",
    }
    YOE_ORDER = ["0-2", "2-5", "5-8", "8-12", "12+"]
    target_idx = YOE_ORDER.index(yoe_band) if yoe_band in YOE_ORDER else 1

    cumulative: dict = {"must_have": [], "nice_to_have": [], "responsibilities": []}

    bands_raw = taxonomy.get("experience_bands", {})

    # ── Shape A: dict keyed by band name ──────────────────────────────────
    if isinstance(bands_raw, dict):
        for band_name, band_data in bands_raw.items():
            if not isinstance(band_data, dict):
                continue
            yoe = NAME_TO_YOE.get(band_name.lower())
            if yoe is None or YOE_ORDER.index(yoe) > target_idx:
                continue
            # Map the various field names to our normalised keys
            field_map = {
                "must_have":          "must_have",
                "core_skills":        "must_have",
                "nice_to_have":       "nice_to_have",
                "progressive_skills": "nice_to_have",
                "arvind_specific":    "nice_to_have",
                "responsibilities":   "responsibilities",
                "leadership_skills":  "responsibilities",
            }
            for src_key, dest_key in field_map.items():
                for item in band_data.get(src_key, []):
                    if isinstance(item, str) and item not in cumulative[dest_key]:
                        cumulative[dest_key].append(item)

    # ── Shape B: list of dicts with "band" field ───────────────────────────
    elif isinstance(bands_raw, list):
        for band_entry in bands_raw:
            if not isinstance(band_entry, dict):
                continue
            band_id = band_entry.get("band", "")
            if band_id not in YOE_ORDER:
                continue
            if YOE_ORDER.index(band_id) > target_idx:
                break
            for key in ("must_have", "nice_to_have", "responsibilities"):
                for item in band_entry.get(key, []):
                    if isinstance(item, str) and item not in cumulative[key]:
                        cumulative[key].append(item)

    return cumulative


def _format_skills_block(cumulative: dict) -> str:
    """Format cumulative skills into a readable string for prompt injection."""
    parts = []
    if cumulative.get("must_have"):
        parts.append("Must-Have Skills (cumulative up to this band):")
        for s in cumulative["must_have"]:
            parts.append(f"  - {s}")
    if cumulative.get("nice_to_have"):
        parts.append("Nice-to-Have Skills:")
        for s in cumulative["nice_to_have"]:
            parts.append(f"  - {s}")
    if cumulative.get("responsibilities"):
        parts.append("Typical Responsibilities at this level:")
        for r in cumulative["responsibilities"]:
            parts.append(f"  - {r}")
    return "\n".join(parts)


# ── Prompt builders ───────────────────────────────────────────────────────────

def build_system_prompt(
    tone_guide: str,
    sample_jds: list[str],
    cumulative_skills: dict,
    yoe_band: str,
    feedback_digest: str = "",
    canonical_role: dict | None = None,
) -> str:
    yoe_label = YOE_LABELS.get(yoe_band, yoe_band)
    yoe_verbs = YOE_LANGUAGE.get(yoe_band, "")

    # ── KB context (30% weight — Arvind-specific signals only) ───────────────
    kb_context_parts = []

    # 1. Tone guide — how Arvind writes (voice, style)
    if tone_guide and tone_guide.strip():
        kb_context_parts.append(f"ARVIND TONE & STYLE GUIDE (follow this writing style):\n{tone_guide.strip()}")

    # 2. Sample JDs — structural/stylistic reference only, NOT skill source
    if sample_jds:
        jd_block = ""
        for i, jd in enumerate(sample_jds[:2], 1):   # cap at 2 to keep prompt lean
            jd_block += f"\n--- STYLE REFERENCE JD {i} ---\n{jd}\n"
        kb_context_parts.append(
            f"STYLE REFERENCE JDs (use ONLY for tone, structure, and section length — "
            f"do NOT copy skills from these; your world knowledge is the skill source):{jd_block}"
        )

    # 3. KB skills — supplementary hint only
    skills_block = _format_skills_block(cumulative_skills)
    if skills_block.strip():
        kb_context_parts.append(
            f"KB SKILLS HINT (30% weight — use as a supplementary cross-check, "
            f"NOT as the primary skill source):\n{skills_block}"
        )

    # 4. Canonical role fingerprint — prevents bleed, defines role boundaries
    if canonical_role:
        must    = ", ".join(canonical_role.get("must_have", []))
        excl    = ", ".join(canonical_role.get("exclude", []))
        cluster = canonical_role.get("role_cluster", "")
        sub_cat = canonical_role.get("sub_category", "")
        kb_context_parts.append(
            f"CANONICAL ROLE BOUNDARIES:\n"
            f"  Sub-category: {sub_cat} | Cluster: {cluster}\n"
            f"  Core skills that define this role: {must}\n"
            f"  Skills that must NOT appear (role bleed): {excl}"
        )

    kb_section = "\n\n".join(kb_context_parts) if kb_context_parts else ""

    # 5. Past feedback
    feedback_section = ""
    if feedback_digest.strip():
        feedback_section = (
            f"\nFEEDBACK FROM PAST GENERATIONS — apply these improvements:\n"
            f"{feedback_digest.strip()}"
        )

    return f"""You are a senior Talent Acquisition specialist and JD writer with 15+ years of experience across technology, analytics, finance, HR, supply chain, and manufacturing roles globally. You have deep knowledge of:
- What skills, tools, and day-to-day activities actually define each role at each seniority level
- Industry-standard job architecture and role levelling frameworks (Mercer IPE, Radford, Korn Ferry)
- Current hiring market expectations for each role type (what good candidates actually look like)
- How to write JDs that attract the right candidates without over- or under-specifying

You are writing for Arvind Limited GCC (Global Capability Centre) — a technology and business-services centre that supports Arvind Limited's textile, retail, and diversified businesses.

═══════════════════════════════════════════════════════════════
PRIMARY INSTRUCTION — YOUR KNOWLEDGE IS THE MAIN SOURCE (70%)
═══════════════════════════════════════════════════════════════
Draw primarily on your expert knowledge of the role, industry, and market to write this JD.
Use real-world understanding of what this role actually does — its tools, workflows, stakeholders,
and deliverables at the given experience level. Do NOT default to generic bullet points.
Think: "What does a {yoe_label} professional in this role do every single day?"

The KB context below (Arvind-specific) contributes ~30% — mainly for:
  • Writing tone and style (how Arvind communicates)
  • Role boundaries (what this role is NOT, to prevent skill bleed)
  • Arvind-specific tech stack or process hints if present

══════════════════
KB CONTEXT (30%)
══════════════════
{kb_section if kb_section else "(No KB data available — rely fully on world knowledge)"}
{feedback_section}

═════════════════════════════
NON-NEGOTIABLE WRITING RULES
═════════════════════════════
1. Every bullet must describe a concrete, observable activity — not a vague trait.
   BAD: "Collaborate with stakeholders"  GOOD: "Partner with business analysts to translate KPI requirements into Power BI report specifications"
2. NEVER invent Arvind-specific numbers (headcount, revenue, plant count, GMV) — these embarrass the company if wrong.
3. Calibrate language precisely to {yoe_band} yrs experience ({yoe_label}).
   - At this level, the person {_level_calibration(yoe_band)}
4. Preferred action verbs for {yoe_label}: {yoe_verbs}
5. Banned words: rockstar, ninja, guru, wizard, superstar, passionate, driven, detail-oriented (standalone), fast-paced, dynamic team, results-driven, go-getter, thought leader.
6. Use second-person throughout: "You will…", "You bring…", "You have…", "You own…"
7. Skills must be specific tools/frameworks, not categories. Write "Selenium / Playwright / Cypress" not "test automation tools".
8. Output ONLY the JD. Zero preamble. Zero closing remarks. No "Here is your JD:"."""


def _level_calibration(yoe_band: str) -> str:
    """Return a one-line description of expected autonomy/scope at this band."""
    return {
        "0-2":  "is still learning fundamentals — tasks are well-defined, output is reviewed by a senior",
        "2-5":  "works independently on assigned modules, contributes to design discussions, reviews junior work",
        "5-8":  "owns full features or workstreams end-to-end, mentors juniors, influences technical decisions",
        "8-12": "leads initiatives, defines standards, drives architecture decisions, manages senior ICs or small teams",
        "12+":  "sets direction at function level, builds teams, owns P&L or technology roadmap, represents the function externally",
    }.get(yoe_band, "operates at a mid-senior level with growing scope and autonomy")


def build_user_prompt(
    role_title: str,
    department: str,
    yoe_band: str,
    focus_areas: str,
    role_type: str = "individual_contributor",
    team_size: int | None = None,
    employment_type: str = "Full-Time",
    work_mode: str = "Onsite",
    reports_to: str = "",
    must_have_skills: list | None = None,
    canonical_role: dict | None = None,
) -> str:
    yoe_label = YOE_LABELS.get(yoe_band, yoe_band)
    dept_display = department.replace("_", " ").title()

    # ── Role type instruction ─────────────────────────────────────────────────
    if role_type == "team_manager":
        role_type_block = (
            f"ROLE TYPE: Team Manager"
            + (f" — direct team of {team_size}" if team_size else "")
            + "\n"
            "The JD MUST reflect people-leadership. Required in Key Responsibilities:\n"
            "  • Setting team goals, running performance reviews, and coaching direct reports\n"
            "  • Hiring, onboarding, and developing team members\n"
            "  • Representing the team in cross-functional forums and stakeholder reviews\n"
            "  • Balancing hands-on delivery with people management (ratio depends on team size)\n"
            "Do NOT write this as an IC role with 'manages a team' tacked on at the end."
        )
    else:
        role_type_block = (
            "ROLE TYPE: Individual Contributor\n"
            "Focus entirely on hands-on technical / functional delivery. "
            "No people-management bullets unless 'mentoring junior team members' is genuinely expected at this level."
        )

    # ── Skills block ─────────────────────────────────────────────────────────
    if must_have_skills:
        skills_block = (
            "MUST-HAVE SKILLS — user-specified (include ALL of these verbatim in the JD):\n"
            + "\n".join(f"  • {s}" for s in must_have_skills)
        )
    elif canonical_role and canonical_role.get("must_have"):
        skills_block = (
            "MUST-HAVE SKILLS — canonical role definition (include all; supplement with your expertise):\n"
            + "\n".join(f"  • {s}" for s in canonical_role["must_have"])
        )
    else:
        skills_block = (
            "MUST-HAVE SKILLS — not specified by user. "
            "Use your expert knowledge of this role at this experience level to determine them. "
            "Be specific: name actual tools, frameworks, and methodologies, not skill categories."
        )

    # ── Exclusion reminder ────────────────────────────────────────────────────
    excl_block = ""
    if canonical_role and canonical_role.get("exclude"):
        excl_block = (
            "\nSKILLS THAT MUST NOT APPEAR (they define a different role — their presence signals a wrong JD):\n"
            + ", ".join(canonical_role["exclude"])
        )

    # ── Optional context lines ────────────────────────────────────────────────
    optional = []
    if reports_to:
        optional.append(f"Reports To: {reports_to}")
    if focus_areas:
        optional.append(f"Focus / Specialisation: {focus_areas}")
    optional_block = "\n".join(optional)

    return f"""════════════════════════════════════
JD REQUEST — ARVIND LIMITED GCC
════════════════════════════════════
Role Title      : {role_title}
Department      : {dept_display}
Experience Band : {yoe_band} years — {yoe_label}
Employment Type : {employment_type}
Work Mode       : {work_mode}
{optional_block}

{role_type_block}

{skills_block}
{excl_block}

════════════════════════════════════
REQUIRED OUTPUT — FIVE SECTIONS ONLY
════════════════════════════════════
Use EXACTLY these markdown headers. No extra sections. No intro paragraph before section 1.

## Role Summary
Write 3–4 sentences. Answer: What does this person own? Who do they work with (internal teams, external vendors, business stakeholders)? What business outcome does this role drive? Ground it in the GCC / {dept_display} context. Be specific to "{role_title}" — do not write a generic paragraph that could apply to any role.

## Key Responsibilities
Write 6–8 bullet points. Rules:
  - Each bullet = one discrete, observable task this person does regularly
  - Start every bullet with a strong action verb ({yoe_label} appropriate)
  - Name specific tools, systems, or methodologies where relevant
  - Sequence from core delivery → collaboration → improvement/ownership
  - NO vague bullets like "Ensure quality standards are maintained"
  - For {yoe_band} yrs experience: {_level_calibration(yoe_band)}

## Must-Have Skills
Write 5–7 bullet points. Rules:
  - Use the skills listed above as the primary source; fill gaps with your expert knowledge of what this role ACTUALLY requires
  - Each bullet = a specific tool, language, framework, platform, or certification — NEVER a soft-skill category
  - Format each as: "Tool/Skill — brief qualifier explaining what they use it for"
    Example: "Python (pandas, NumPy) — data wrangling, feature engineering, EDA"
    Example: "SQL — complex joins, window functions, query optimisation on 50M+ row tables"
    Example: "Power BI — building enterprise dashboards, DAX measures, row-level security"
  - Ask yourself: "Would a hiring manager test this in a technical screening?" If yes, include it
  - Mirror the specificity of real job postings for {role_title} at tech-forward companies
  - Avoid: "Strong communication", "attention to detail", "analytical mindset" — these are NOT must-have skills

## Good to Have
Write 3–5 bullet points. Rules:
  - Genuine differentiators that make a candidate stand out — NOT required skills in disguise
  - Specific certifications, niche tools, or adjacent domain knowledge relevant to THIS role
  - Avoid: "strong communication skills", "ability to work in a team", "leadership" (unless genuinely differentiated)

## What We Offer
Write 3–4 bullet points. Rules:
  - Focus on what is genuinely compelling about this role at Arvind GCC
  - Mention: real technology stack in use, scale/complexity of business problems, learning & development paths, cross-functional exposure
  - Do NOT mention specific salary, bonus percentages, headcount, or revenue
  - Make it honest and specific — avoid corporate clichés like "great work environment" or "competitive compensation"

Generate the complete JD now. Output starts directly with "## Role Summary". Nothing before it."""


# ── Core generation functions ─────────────────────────────────────────────────

def generate_jd(
    role_title: str,
    department: str,
    family: str,
    yoe_band: str = "2-5",
    focus_areas: str = "",
    feedback_digest: str = "",
    verbose: bool = False,
    role_type: str = "individual_contributor",
    team_size: int | None = None,
    employment_type: str = "Full-Time",
    work_mode: str = "Onsite",
    reports_to: str = "",
    must_have_skills: list | None = None,
) -> str:
    """
    Generate exactly ONE JD. Temperature is always 0.9 (expressive, varied
    phrasing) — no exceptions, no parameter to override it.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        sys.exit("Error: GROQ_API_KEY not set. Copy .env.example to .env and add your key.")

    tone_guide = load_tone_guide(department, family)
    taxonomy = load_skills_taxonomy(department, family)
    cumulative = compute_cumulative_skills(taxonomy, yoe_band)
    sample_jds = load_sample_jds(department, family, yoe_band)

    if verbose:
        print(f"[info] {len(sample_jds)} sample JD(s) loaded for {department}/{family} at band {yoe_band}")
        if not tone_guide:
            print(f"[warn] No tone_guide.txt at kb/{department}/{family}/")
        if not taxonomy:
            print(f"[warn] No skills_taxonomy.yaml at kb/{department}/{family}/")

    # Canonical role fingerprint for this role title
    from role_skills_map import get_role_match
    canonical_role = get_role_match(role_title, department, family)

    system_prompt = build_system_prompt(
        tone_guide, sample_jds, cumulative, yoe_band, feedback_digest,
        canonical_role=canonical_role,
    )
    user_prompt = build_user_prompt(
        role_title, department, yoe_band, focus_areas,
        role_type=role_type, team_size=team_size,
        employment_type=employment_type, work_mode=work_mode,
        reports_to=reports_to, must_have_skills=must_have_skills,
        canonical_role=canonical_role,
    )

    client = Groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1600,
        temperature=0.75,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


# ── Backward-compatible wrapper (used by /api/generate in app.py) ─────────────

def generate_jd_legacy(
    role_title: str,
    department: str,
    family: str,
    seniority_level: str,
    focus_areas: str = "",
    verbose: bool = False,
) -> str:
    """Wraps generate_jd() mapping legacy seniority level → YoE band."""
    yoe_band = SENIORITY_TO_YOE.get(seniority_level, "2-5")
    return generate_jd(
        role_title=role_title,
        department=department,
        family=family,
        yoe_band=yoe_band,
        focus_areas=focus_areas,
        verbose=verbose,
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

def interactive_mode() -> dict:
    print(f"\n=== JD Generator — {COMPANY_NAME} ===\n")

    role_title = input("Role Title (e.g. QA Manager): ").strip()
    if not role_title:
        sys.exit("Role title is required.")

    print(f"\nAvailable departments: {', '.join(DEPARTMENTS.keys())}")
    department = input("Department: ").strip().lower()
    if department not in DEPARTMENTS:
        sys.exit(f"Unknown department '{department}'. Choose from: {', '.join(DEPARTMENTS.keys())}")

    families = DEPARTMENTS[department]
    print(f"\nAvailable role families for {department}: {', '.join(families)}")
    family = input("Role Family: ").strip().lower()
    if family not in families:
        sys.exit(f"Unknown role family '{family}'. Choose from: {', '.join(families)}")

    print(f"\nYoE bands: {', '.join(YOE_BANDS)}")
    for b, l in YOE_LABELS.items():
        print(f"  {b}  →  {l}")
    yoe_band = input("YoE Band: ").strip()
    if yoe_band not in YOE_BANDS:
        sys.exit(f"Unknown band '{yoe_band}'. Choose from: {', '.join(YOE_BANDS)}")

    focus_areas = input("\nFocus Areas (optional, e.g. 'denim, inline inspection'): ").strip()

    return {
        "role_title": role_title,
        "department": department,
        "family": family,
        "yoe_band": yoe_band,
        "focus_areas": focus_areas,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=f"Generate a JD using {COMPANY_NAME}'s KB and Groq LLM.")
    parser.add_argument("--role", help="Role title")
    parser.add_argument("--dept", help="Department")
    parser.add_argument("--family", help="Role family")
    parser.add_argument("--yoe", default="2-5", help="YoE band (0-2, 2-5, 5-8, 8-12, 12+)")
    parser.add_argument("--level", help="Legacy seniority level (Junior/Mid/Senior/Lead) — maps to YoE")
    parser.add_argument("--focus", default="", help="Optional focus areas")
    parser.add_argument("--verbose", action="store_true", help="Show debug info")
    parser.add_argument("--output", help="Save output to a file path instead of stdout")
    args = parser.parse_args()

    # Map legacy --level if provided
    if args.level and not args.yoe:
        args.yoe = SENIORITY_TO_YOE.get(args.level.capitalize(), "2-5")

    if args.role and args.dept and args.family:
        params = {
            "role_title": args.role,
            "department": args.dept.lower(),
            "family": args.family.lower(),
            "yoe_band": args.yoe,
            "focus_areas": args.focus,
        }
    else:
        params = interactive_mode()

    print("\nGenerating JD (temperature=0.9)... ", end="", flush=True)
    jd = generate_jd(**params, verbose=args.verbose)
    print("done.\n")

    if args.output:
        from pathlib import Path as P
        out = P(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(jd, encoding="utf-8")
        print(f"JD saved to {out}")
    else:
        print("=" * 60)
        print(jd)
        print("=" * 60)


if __name__ == "__main__":
    main()
