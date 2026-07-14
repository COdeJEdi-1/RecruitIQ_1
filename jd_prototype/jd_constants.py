"""Shared constants for JD Generator UI and export paths."""

JD_FOOTER_HEADING = "Next Steps"
JD_FOOTER_TEXT = "Shortlisted candidates can expect a call shortly from our voice bot, Veda."
JD_FOOTER_BRAND_LABEL = "POWERED BY AI"
JD_FOOTER_BRAND_NAME = "VEDA VOICE"

_LEGACY_FOOTERS = (
    "You will be getting a call shortly.",
    "Selected candidates will get a call or text shortly.",
    f"{JD_FOOTER_HEADING}\nSelected candidates will get a call or text shortly.",
    JD_FOOTER_TEXT,
    f"{JD_FOOTER_HEADING}\n{JD_FOOTER_TEXT}",
)


def strip_jd_footer(text: str) -> str:
    text = text.rstrip()
    for footer in _LEGACY_FOOTERS:
        if text.endswith(footer):
            return text[:-len(footer)].rstrip()
    return text


def append_jd_footer(text: str) -> str:
    body = strip_jd_footer(text)
    line = f"{JD_FOOTER_HEADING}\n{JD_FOOTER_TEXT}"
    return line if not body else f"{body}\n\n{line}"
