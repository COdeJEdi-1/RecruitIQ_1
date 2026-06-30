"""
JD Section Parser — Arvind JD Generator

Parses the plain-text LLM output into structured sections for
rendering into the Arvind-branded HTML / PDF / DOCX templates.
"""

import re
from typing import Optional


# All known section heading variants the LLM might output
_SECTION_MAP = {
    "role_summary": [
        "role summary", "about the role", "the role", "position summary",
        "job summary", "overview",
    ],
    "key_responsibilities": [
        "key responsibilities", "responsibilities", "what you will do",
        "your responsibilities", "role responsibilities",
    ],
    "must_have": [
        "must-have skills", "must have skills", "must-have skills & qualifications",
        "required skills", "requirements", "qualifications", "skills required",
        "must have", "mandatory skills", "essential skills",
    ],
    "nice_to_have": [
        "nice-to-have skills", "nice to have skills", "nice-to-have",
        "good to have", "preferred skills", "bonus skills", "preferred qualifications",
    ],
    "what_we_offer": [
        "what we offer", "why join us", "what you get", "benefits",
        "perks", "compensation & benefits", "what arvind offers",
    ],
}


def _normalise(line: str) -> str:
    return line.strip().lower().lstrip("#*◆ ").rstrip(":* ")


def _detect_section(line: str) -> Optional[str]:
    norm = _normalise(line)
    # Strip bold markdown
    norm = norm.strip("*").strip()
    for section_key, variants in _SECTION_MAP.items():
        for v in variants:
            if norm == v or norm.startswith(v):
                return section_key
    return None


def _is_bullet(line: str) -> bool:
    return bool(re.match(r"^[-•*]\s+", line.strip()))


def _clean_bullet(line: str) -> str:
    return re.sub(r"^[-•*]\s+", "", line.strip())


def parse_jd_sections(jd_text: str) -> dict:
    """
    Parse raw LLM JD text into structured sections.

    Returns:
    {
        "role_summary":         str   (paragraph text),
        "key_responsibilities": list  (bullet strings),
        "must_have":            list  (bullet strings),
        "nice_to_have":         list  (bullet strings),
        "what_we_offer":        list  (bullet strings or paragraph),
        "raw":                  str   (original text),
    }
    """
    sections = {
        "role_summary": "",
        "key_responsibilities": [],
        "must_have": [],
        "nice_to_have": [],
        "what_we_offer": [],
        "raw": jd_text,
    }

    lines = jd_text.split("\n")
    current_section = None
    buffer: list[str] = []

    def _flush(section_key, buf):
        if not section_key or not buf:
            return
        text = "\n".join(buf).strip()
        if section_key == "role_summary":
            sections["role_summary"] = text
        else:
            items = []
            for line in buf:
                line = line.strip()
                if not line:
                    continue
                if _is_bullet(line):
                    items.append(_clean_bullet(line))
                else:
                    # Non-bullet body line — treat as a paragraph item
                    items.append(line)
            if items:
                sections[section_key] = items

    for line in lines:
        stripped = line.strip()
        # Skip divider lines (──────) produced by _formatJD
        if re.match(r'^─{3,}$', stripped):
            continue
        detected = _detect_section(stripped)

        if detected:
            _flush(current_section, buffer)
            current_section = detected
            buffer = []
        else:
            if stripped:
                buffer.append(stripped)

    _flush(current_section, buffer)

    return sections


def format_for_email(sections: dict, meta: dict) -> dict:
    """
    Combine parsed sections with role metadata for template rendering.

    meta keys: role_title, department, family, yoe_band, division,
               location, employment_type, reporting_to, openings, job_code,
               generated_by, generated_date
    """
    return {**sections, **meta}
