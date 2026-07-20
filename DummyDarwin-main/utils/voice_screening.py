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
from datetime import datetime

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from database.models import Candidate, DarwinboxJob

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


SENTIMENT_RATING_LABELS = {
    5: "Very Positive",
    4: "Positive",
    3: "Neutral",
    2: "Negative",
    1: "Very Negative",
}

COMMUNICATION_RATING_LABELS = {
    5: "Outstanding",
    4: "Strong",
    3: "Satisfactory",
    2: "Needs Improvement",
    1: "Unsatisfactory",
}


def _sentiment_rating(compound):
    """Maps a VADER compound score (-1..1) to a 1-5 rating, 5 = most positive."""
    if compound >= 0.5:
        return 5
    if compound >= 0.05:
        return 4
    if compound > -0.05:
        return 3
    if compound > -0.5:
        return 2
    return 1


def _compute_sentiment(candidate_text):
    """VADER sentiment over the candidate's own words.
    Returns (label, compound, rating) — rating is 1-5, 5 = most positive.
    label/rating are None if there's no candidate text to analyse."""
    if not candidate_text.strip():
        return None, None, None
    compound = _VADER.polarity_scores(candidate_text)["compound"]
    rating = _sentiment_rating(compound)
    return SENTIMENT_RATING_LABELS[rating], compound, rating


def _communication_rating(score):
    """Maps the 0-100 internal communication score to a 1-5 rating, 5 = best."""
    if score >= 85:
        return 5
    if score >= 70:
        return 4
    if score >= 50:
        return 3
    if score >= 30:
        return 2
    return 1


def _compute_communication_score(candidate_turns):
    """Rule-based confidence/fluency score from the candidate's turns.
    Penalises filler words, hedging language, stammered fragments, and very
    short/low-substance answers. Returns (score_0_100, rating_1_5, label) —
    score_0_100 feeds the internal overall-score weighting, rating/label are
    for display. Returns (None, None, None) if there isn't enough candidate
    speech to judge."""
    if not candidate_turns:
        return None, None, None

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

    rating = _communication_rating(score)
    return score, rating, COMMUNICATION_RATING_LABELS[rating]


def _count_answered_fields(row):
    return sum(1 for f in _KEY_FIELDS if _clean(row.get(f)))



def _parse_recording_consent(row):
    """Reads OmniDimension Call_Recording_Consent (Yes/No).
    Returns 'Yes', 'No', or None if missing/unknown."""
    raw = None
    for key in (
        "Call_Recording_Consent",
        "call_recording_consent",
        "Call Recording Consent",
        "recording_consent",
    ):
        if key in row:
            raw = _clean(row.get(key))
            break
    if raw is None:
        # Case-insensitive fallback for sheet header drift
        for k, v in row.items():
            if k and "recording" in k.lower() and "consent" in k.lower():
                raw = _clean(v)
                break
    if not raw:
        return None
    t = raw.lower()
    if t in ("yes", "y", "true", "1", "consented", "granted"):
        return "Yes"
    if t in ("no", "n", "false", "0", "declined", "denied", "refused"):
        return "No"
    return None


def score_row(row):
    """Returns a dict with verdict, score, and flags for one sheet row."""
    flags = []

    recording_consent = _parse_recording_consent(row)
    if recording_consent == "No":
        return {
            "verdict": "Needs Manual Call",
            "score": None,
            "flags": [
                "Declined AI call recording consent — recruit via alternate (manual) screening"
            ],
            "computed_sentiment": None,
            "sentiment_rating": None,
            "communication_score": None,
            "communication_rating": None,
            "communication_label": None,
            "recording_consent": "No",
            "needs_manual_call": True,
        }

    call_status = (_clean(row.get("call_status")) or "").lower()
    duration = _parse_ctc(row.get("call_duration_in_seconds")) or 0
    answered_count = _count_answered_fields(row)

    if call_status != "completed" or duration < MIN_CALL_SECONDS or answered_count < 3:
        return {
            "verdict": "Incomplete", "score": None,
            "flags": ["Call didn't gather enough answers — needs a re-call"],
            "computed_sentiment": None, "sentiment_rating": None,
            "communication_score": None, "communication_rating": None, "communication_label": None,
            "recording_consent": recording_consent,
            "needs_manual_call": False,
        }

    job_change = (_clean(row.get("job_change")) or "").lower()
    if job_change in ("no", "not interested"):
        return {
            "verdict": "Not Suitable", "score": None,
            "flags": ["Not open to changing jobs"],
            "computed_sentiment": None, "sentiment_rating": None,
            "communication_score": None, "communication_rating": None, "communication_label": None,
            "recording_consent": recording_consent,
            "needs_manual_call": False,
        }

    candidate_turns = _extract_candidate_turns(row.get("full_conversation") or "")
    computed_sentiment, _, sentiment_rating = _compute_sentiment(" ".join(candidate_turns))
    communication_score, communication_rating, communication_label = _compute_communication_score(candidate_turns)

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

    if sentiment_rating is not None:
        score += (sentiment_rating - 3) * 7.5  # 5->+15, 4->+7.5, 3->0, 2->-7.5, 1->-15
        if sentiment_rating <= 2:
            flags.append(f"{computed_sentiment} call sentiment ({sentiment_rating}/5)")

    if communication_score is not None:
        score += (communication_score - 50) * 0.3  # up to ±15, one weighted factor among the rest
        if communication_rating <= 2:
            flags.append(f"Communication: {communication_label} ({communication_rating}/5)")

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

    if (sentiment_rating <= 2 or red_flag or communication_rating <= 2) and verdict == "Ready for Interview":
        verdict = "Manual Review"

    return {
        "verdict": verdict, "score": score, "flags": flags,
        "computed_sentiment": computed_sentiment,
        "sentiment_rating": sentiment_rating,
        "communication_score": communication_score,
        "communication_rating": communication_rating,
        "communication_label": communication_label,
        "recording_consent": recording_consent,
        "needs_manual_call": False,
    }


def _phone_last10(phone):
    """Normalizes a phone number to its last 10 digits for cross-source matching
    (formats vary: '+91 98251 84700', '9825184700', '+919825184700', ...)."""
    if not phone:
        return None
    digits = re.sub(r"\D", "", str(phone))
    return digits[-10:] if len(digits) >= 10 else None


def _load_phone_lookup():
    """Builds {last-10-digit phone: {"role": role_title, "req_id": jd_id,
    "name": candidate_name}} by joining the `candidates` table (candidate ->
    darwinbox_job_id) with `darwinbox_jobs` (job_id -> role_title/jd_id). The
    voice-screening sheet has no role/job field of its own, and its own
    candidate_name is often blank (the call ended before OmniDimension's LLM
    extracted a name) — this join is the only way to know which role a call
    was screening for, and lets fetch_and_score() fall back to our own
    record of the candidate's name instead of showing "Unknown" for someone
    we actually do know."""
    try:
        candidates = [c.to_dict() for c in Candidate.query.all()]
        jobs = [j.to_dict() for j in DarwinboxJob.query.all()]
    except Exception:
        return {}

    job_map = {
        j["darwinbox_job_id"]: {"role": j.get("role_title", ""), "req_id": j.get("jd_id")}
        for j in jobs
        if j.get("darwinbox_job_id")
    }

    phone_lookup = {}
    for c in candidates:
        last10 = _phone_last10(c.get("phone"))
        job = job_map.get(c.get("darwinbox_job_id"))
        if last10 and job and job["role"]:
            phone_lookup[last10] = {"role": job["role"], "req_id": job["req_id"], "name": c.get("name")}
    return phone_lookup


def _mask_phone(phone):
    """Masks all but the country code and outer 2+2 digits, for rows whose
    call never actually completed — there's no verified interaction to
    justify showing the full number. e.g. '+919825184700' -> '+91 98••• •••00'."""
    if not phone or phone == "—":
        return "—"
    digits = re.sub(r"\D", "", str(phone))
    if len(digits) < 10:
        return "—"
    cc, num = digits[:-10], digits[-10:]
    masked = f"{num[:2]}••• •••{num[-2:]}"
    return f"+{cc} {masked}" if cc else masked


def _looks_like_phone(value):
    """OmniDimension logs web-widget test calls with junk values in the phone
    columns (e.g. phone_number="Web Call", to_number="Assistant") instead of
    a real number. Rejects anything without enough digits to be a real phone,
    so the UI shows '—' rather than a literal 'Assistant'/'Web Call' string."""
    if not value:
        return False
    digits = re.sub(r"\D", "", str(value))
    return len(digits) >= 7


def fetch_and_score(timeout=10):
    """Fetches the sheet, scores every row, returns (candidates, error)."""
    try:
        with urllib.request.urlopen(SHEET_CSV_URL, timeout=timeout, context=_SSL_CONTEXT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return [], f"Could not reach the screening sheet: {e}"

    phone_lookup = _load_phone_lookup()

    reader = csv.DictReader(io.StringIO(raw))
    candidates = []
    for row in reader:
        if not _clean(row.get("candidate_name")) and not _clean(row.get("phone_number")):
            continue
        result = score_row(row)
        # phone_number is OmniDimension's own outbound line (near-constant across
        # every row) — the actual candidate number is to_number for outbound calls.
        # Web-widget test calls log junk like "Web Call"/"Assistant" here instead
        # of a real number — _looks_like_phone() keeps those from being displayed
        # or matched as if they were one.
        raw_phone = _clean(row.get("to_number")) or _clean(row.get("phone_number"))
        phone_valid = _looks_like_phone(raw_phone)
        candidate_phone = raw_phone if phone_valid else "—"
        match = phone_lookup.get(_phone_last10(raw_phone)) if phone_valid else None

        # The sheet's own candidate_name is frequently blank/"Not provided" —
        # the call ended before OmniDimension's LLM captured a name. Fall back
        # to our own record of this candidate (matched by phone) rather than
        # showing "Unknown" for someone we actually do know.
        sheet_name = _clean(row.get("candidate_name"))
        if sheet_name and sheet_name.lower() == "not provided":
            sheet_name = None
        name = sheet_name or (match.get("name") if match else None) or "Unknown"

        candidates.append({
            "name": name,
            "phone": candidate_phone,
            "masked_phone": _mask_phone(candidate_phone),
            "role": (match.get("role") if match else None) or "Unknown Role",
            "req_id": match.get("req_id") if match else None,
            "call_date": _clean(row.get("call_date")) or "",
            "current_job": _clean(row.get("current_job")) or "—",
            "years_experience": _parse_years(row),
            "current_ctc": _clean(row.get("current_ctc")) or "—",
            "expected_ctc": _clean(row.get("expected_ctc")) or "—",
            "current_location": _clean(row.get("current_location")) or "—",
            "willing_to_relocate": _clean(row.get("willing_to_relocate")) or "—",
            "job_change": _clean(row.get("job_change")) or "—",
            "notice_period": _clean(row.get("notice_period")) or _clean(row.get("joining_time")) or "—",
            "sentiment": _clean(row.get("sentiment")) or "—",
            "job_change_reason": _clean(row.get("job_change_reason")) or "—",
            "summary": _clean(row.get("summary")) or "",
            "full_conversation": _clean(row.get("full_conversation")) or "",
            "recording_url": _clean(row.get("recording_url")) or "",
            **result,
            "recording_consent": result.get("recording_consent") or _parse_recording_consent(row),
            "needs_manual_call": bool(result.get("needs_manual_call")),
        })

    # Needs Manual Call first, then Ready/Manual/Not Suitable by score desc; Incomplete last.
    _order = {"Needs Manual Call": 0, "Ready for Interview": 1, "Manual Review": 2, "Not Suitable": 3, "Incomplete": 4}
    candidates.sort(key=lambda c: (_order.get(c["verdict"], 9), c["score"] is None, -(c["score"] or 0)))
    return candidates, None


def fetch_call_results_by_phone(timeout=10):
    """Same call data as fetch_and_score(), keyed by the candidate's last-10-digit
    phone number -> every logged call to that number, most-recent-first, so
    callers (e.g. the Calling pages) can join it onto candidate rows sourced
    from the `candidates` table without re-fetching the sheet.

    Returns a LIST per phone rather than picking one "best" call here —
    this sheet's phone numbers are heavily reused test/demo data (confirmed:
    one number alone logged calls under half a dozen different candidate
    names — Kashish, "Kashish Bhagat", Rohit Malhotra, and several blank
    names — spanning weeks). Picking "the most recent call to this number"
    without checking WHO made it would silently attribute a totally
    different person's call to this candidate. The caller
    (_call_info_for_candidate() in routes/dashboard.py) is responsible for
    picking the right entry from the list by matching the candidate's own
    name, not just their phone."""
    candidates, error = fetch_and_score(timeout=timeout)
    if error:
        return {}, error

    by_phone = {}
    for c in candidates:
        last10 = _phone_last10(c.get("phone"))
        if not last10:
            continue
        by_phone.setdefault(last10, []).append(c)

    def _sort_key(call):
        try:
            return datetime.fromisoformat(call.get("call_date") or "")
        except ValueError:
            return datetime.min

    for last10 in by_phone:
        by_phone[last10].sort(key=_sort_key, reverse=True)

    return by_phone, None
