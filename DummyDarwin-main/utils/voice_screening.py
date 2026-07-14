"""
AI voice-screening: pulls candidate call answers from the Google Sheet that
OmniDimension writes to, and applies rule-based criteria to flag who's ready
for an interview.

No Google API credentials needed — reads the sheet's public CSV export.
"""

import csv
import io
import re
import ssl
import urllib.request

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CONTEXT = None

_VADER = SentimentIntensityAnalyzer()

SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1_XhyYrCA6dlSsjqNuvX1Nnc8-txVeUOMRbtkJCJBxL0/export?format=csv&gid=113540099"
)

MIN_CALL_SECONDS = 45
SCORE_READY = 70
SCORE_MANUAL_REVIEW = 40
CTC_JUMP_FLAG_RATIO = 1.75  # expected_ctc / current_ctc above this is flagged
NOTICE_PERIOD_FLAG_DAYS = 60

RED_FLAG_KEYWORDS = [
    "terminated", "fired", "conflict", "issue with manager",
    "asked to leave", "let go", "harassment",
]

FILLER_WORDS = [
    "uh", "um", "umm", "uh-huh", "like", "you know", "i mean",
    "sort of", "kind of", "basically", "actually",
]
HEDGE_PHRASES = [
    "i guess", "maybe", "i think", "not sure", "probably",
    "i suppose", "possibly", "i'm not certain",
]

_MISSING_VALUES = {"", "not provided", "na", "n/a", "none", "-"}

# The 6 fields used to decide whether a call actually gathered real answers.
_KEY_FIELDS = [
    "experience_years", "years_of_experiance", "current_job", "job_change",
    "current_location", "notice_period", "joining_time", "expected_ctc",
]


def _clean(value):
    if value is None:
        return None
    v = value.strip()
    return None if v.lower() in _MISSING_VALUES else v


def _parse_years(row):
    for key in ("experience_years", "years_of_experiance"):
        v = _clean(row.get(key))
        if v:
            match = re.search(r"(\d+(\.\d+)?)", v)
            if match:
                return float(match.group(1))
    return None


def _parse_ctc(value):
    v = _clean(value)
    if not v:
        return None
    match = re.search(r"(\d+(\.\d+)?)", v.replace(",", ""))
    return float(match.group(1)) if match else None


def _parse_notice_days(row):
    text = _clean(row.get("notice_period")) or _clean(row.get("joining_time")) or _clean(row.get("joining_status"))
    if not text:
        return None
    t = text.lower()
    if "immediate" in t or "today" in t or "asap" in t:
        return 0
    match = re.search(r"(\d+)\s*(day|week|month)", t)
    if not match:
        return None
    n, unit = int(match.group(1)), match.group(2)
    return n * 30 if unit == "month" else n * 7 if unit == "week" else n


def _has_red_flag_keyword(row):
    text = " ".join(filter(None, [
        _clean(row.get("job_change_reason")),
        _clean(row.get("full_conversation")),
    ])).lower()
    return next((kw for kw in RED_FLAG_KEYWORDS if kw in text), None)


def _extract_candidate_turns(full_conversation):
    """Pull out only the candidate's lines from a 'Bot: ... | User: ... |
    Bot: ...' transcript. Returns a list of the candidate's spoken turns."""
    if not full_conversation:
        return []
    turns = []
    for segment in full_conversation.split("|"):
        segment = segment.strip()
        if segment.lower().startswith("user:"):
            turns.append(segment.split(":", 1)[1].strip())
    return turns


def _compute_sentiment(candidate_text):
    """VADER sentiment over the candidate's own words. Returns (label, compound)."""
    if not candidate_text.strip():
        return None, None
    compound = _VADER.polarity_scores(candidate_text)["compound"]
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
    return label, compound


def _compute_communication_score(candidate_turns):
    """Rule-based confidence/fluency score (0-100) from the candidate's turns.
    Penalises filler words, hedging language, stammered fragments, and very
    short/low-substance answers. Returns (score, label) or (None, None) if
    there isn't enough candidate speech to judge."""
    if not candidate_turns:
        return None, None

    text = " ".join(candidate_turns)
    lower = text.lower()
    word_count = len(lower.split()) or 1

    filler_count = sum(len(re.findall(r"\b" + re.escape(w) + r"\b", lower)) for w in FILLER_WORDS)
    filler_per_100 = filler_count / word_count * 100

    hedge_count = sum(lower.count(p) for p in HEDGE_PHRASES)

    # Fragmented/stammered sentences: short (<=2 word) fragments ending a clause,
    # e.g. "I'm.  I'm.  I'm an." — a proxy for hesitation.
    fragments = [f.strip() for f in re.split(r"[.!?]", text) if f.strip()]
    short_fragments = [f for f in fragments if len(f.split()) <= 2]
    hesitation_ratio = len(short_fragments) / len(fragments) if fragments else 0

    avg_words_per_turn = word_count / len(candidate_turns)

    score = 100.0
    score -= min(40, filler_per_100 * 8)
    score -= min(30, hesitation_ratio * 100 * 0.6)
    score -= min(20, hedge_count * 5)
    if avg_words_per_turn < 3:
        score -= 15
    score = max(0, min(100, round(score)))

    if score >= 75:
        label = "Confident & Clear"
    elif score >= 50:
        label = "Adequate"
    else:
        label = "Hesitant"

    return score, label


def _count_answered_fields(row):
    return sum(1 for f in _KEY_FIELDS if _clean(row.get(f)))


def score_row(row):
    """Returns a dict with verdict, score, and flags for one sheet row."""
    flags = []

    call_status = (_clean(row.get("call_status")) or "").lower()
    duration = _parse_ctc(row.get("call_duration_in_seconds")) or 0
    answered_count = _count_answered_fields(row)

    if call_status != "completed" or duration < MIN_CALL_SECONDS or answered_count < 3:
        return {
            "verdict": "Incomplete", "score": None,
            "flags": ["Call didn't gather enough answers — needs a re-call"],
            "computed_sentiment": None, "communication_score": None, "communication_label": None,
        }

    job_change = (_clean(row.get("job_change")) or "").lower()
    if job_change in ("no", "not interested"):
        return {
            "verdict": "Not Suitable", "score": None,
            "flags": ["Not open to changing jobs"],
            "computed_sentiment": None, "communication_score": None, "communication_label": None,
        }

    candidate_turns = _extract_candidate_turns(row.get("full_conversation") or "")
    computed_sentiment, _ = _compute_sentiment(" ".join(candidate_turns))
    communication_score, communication_label = _compute_communication_score(candidate_turns)

    score = 50.0  # baseline once we know the call gathered real answers

    years = _parse_years(row)
    if years is not None:
        score += min(years, 8) * 3  # up to +24 for experience

    current_ctc = _parse_ctc(row.get("current_ctc"))
    expected_ctc = _parse_ctc(row.get("expected_ctc"))
    if current_ctc and expected_ctc:
        ratio = expected_ctc / current_ctc
        if ratio > CTC_JUMP_FLAG_RATIO:
            score -= 10
            flags.append(f"Large compensation jump requested ({ratio:.1f}x current CTC)")
        else:
            score += 5

    if (_clean(row.get("willing_to_relocate")) or "").lower() in ("yes", "y"):
        score += 8

    if computed_sentiment == "Positive":
        score += 10
    elif computed_sentiment == "Negative":
        score -= 15
        flags.append("Negative call sentiment")

    if communication_score is not None:
        score += (communication_score - 50) * 0.3  # up to ±15, one weighted factor among the rest
        if communication_label == "Hesitant":
            flags.append("Hesitant / low-confidence communication style")

    notice_days = _parse_notice_days(row)
    if notice_days is not None:
        if notice_days > NOTICE_PERIOD_FLAG_DAYS:
            score -= 8
            flags.append(f"Long notice period (~{notice_days} days)")
        else:
            score += 5

    red_flag = _has_red_flag_keyword(row)
    if red_flag:
        flags.append(f"Mentioned potential red flag: \"{red_flag}\"")

    score = max(0, min(100, round(score)))

    if score >= SCORE_READY:
        verdict = "Ready for Interview"
    elif score >= SCORE_MANUAL_REVIEW:
        verdict = "Manual Review"
    else:
        verdict = "Not Suitable"

    if (computed_sentiment == "Negative" or red_flag or communication_label == "Hesitant") and verdict == "Ready for Interview":
        verdict = "Manual Review"

    return {
        "verdict": verdict, "score": score, "flags": flags,
        "computed_sentiment": computed_sentiment,
        "communication_score": communication_score,
        "communication_label": communication_label,
    }


def fetch_and_score(timeout=10):
    """Fetches the sheet, scores every row, returns (candidates, error)."""
    try:
        with urllib.request.urlopen(SHEET_CSV_URL, timeout=timeout, context=_SSL_CONTEXT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return [], f"Could not reach the screening sheet: {e}"

    reader = csv.DictReader(io.StringIO(raw))
    candidates = []
    for row in reader:
        if not _clean(row.get("candidate_name")) and not _clean(row.get("phone_number")):
            continue
        result = score_row(row)
        candidates.append({
            "name": _clean(row.get("candidate_name")) or "Unknown",
            "phone": _clean(row.get("phone_number")) or "—",
            "call_date": _clean(row.get("call_date")) or "",
            "current_job": _clean(row.get("current_job")) or "—",
            "years_experience": _parse_years(row),
            "current_ctc": _clean(row.get("current_ctc")) or "—",
            "expected_ctc": _clean(row.get("expected_ctc")) or "—",
            "current_location": _clean(row.get("current_location")) or "—",
            "willing_to_relocate": _clean(row.get("willing_to_relocate")) or "—",
            "notice_period": _clean(row.get("notice_period")) or _clean(row.get("joining_time")) or "—",
            "sentiment": _clean(row.get("sentiment")) or "—",
            "job_change_reason": _clean(row.get("job_change_reason")) or "—",
            "summary": _clean(row.get("summary")) or "",
            "full_conversation": _clean(row.get("full_conversation")) or "",
            "recording_url": _clean(row.get("recording_url")) or "",
            **result,
        })

    # Ready/Manual Review/Not Suitable sorted by score desc; Incomplete last.
    candidates.sort(key=lambda c: (c["score"] is None, -(c["score"] or 0)))
    return candidates, None
