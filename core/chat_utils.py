"""
Utility functions for the chat lead capture pipeline.

Responsibilities:
  - Phone normalization & validation
  - Language detection from conversation
  - Smart summary generation from conversation JSON
  - Transcript formatting for Telegram
"""
import logging
import re
import html

logger = logging.getLogger(__name__)


# ── Phone ─────────────────────────────────────────────────────────────────────

# Very liberal E.164-ish allowlist: 7–15 digits, optional leading +
_PHONE_RE = re.compile(r'^\+?[\d\s\-().]{7,20}$')


def normalize_phone(raw: str) -> str:
    """
    Normalize a user-entered phone number.
    - Strips whitespace
    - Keeps leading + if present
    - Removes spaces / hyphens / parentheses from the rest
    - Returns the cleaned string (never raises)
    """
    raw = raw.strip()
    if not raw:
        return ''
    has_plus = raw.startswith('+')
    digits_only = re.sub(r'[\s\-().]+', '', raw)
    if has_plus:
        return '+' + re.sub(r'\D', '', digits_only)
    return re.sub(r'\D', '', digits_only)


def is_valid_phone(raw: str) -> bool:
    """Return True if raw looks like a real phone number."""
    if not raw:
        return False
    cleaned = normalize_phone(raw)
    if not cleaned:
        return False
    digits = re.sub(r'\D', '', cleaned)
    return 7 <= len(digits) <= 15


# ── Language detection ────────────────────────────────────────────────────────

_FA_CHARS = re.compile(r'[\u0600-\u06FF]')   # Arabic/Persian script
_EL_CHARS = re.compile(r'[\u0370-\u03FF]')   # Greek script


def detect_language(conversation: list) -> str:
    """
    Heuristically detect visitor language from user messages.
    Returns an uppercase 2-letter code: EN, FA, EL, or '' for unknown.
    """
    user_text = ' '.join(
        m.get('text', '') or m.get('content', '')
        for m in conversation
        if m.get('role') == 'user'
    )
    if _FA_CHARS.search(user_text):
        return 'FA'
    if _EL_CHARS.search(user_text):
        return 'EL'
    # Default to EN if Latin characters are present
    if re.search(r'[a-zA-Z]', user_text):
        return 'EN'
    return ''


# ── Summary generation ────────────────────────────────────────────────────────

# (label, keywords to search in user messages)
_INTEREST_TOPICS = [
    ('Greece Golden Visa',   ['golden visa', 'visa', 'residency', 'residence', 'permit']),
    ('property investment',  ['property', 'properties', 'apartment', 'house', 'real estate', 'buy']),
    ('investment amount',    ['invest', 'price', 'cost', 'amount', '€', 'euro', '250', '400', '800']),
    ('application process',  ['process', 'step', 'how does', 'how to', 'procedure', 'timeline']),
    ('Greek citizenship',    ['citizen', 'passport', 'nationality']),
    ('partnership',          ['partner', 'agent', 'cooperation', 'broker']),
    ('company / Adonis',     ['about', 'who are', 'company', 'adonis']),
]

_INTENT_PATTERNS = [
    ('requested a callback',     ['call me', 'callback', 'call back', 'zang', 'tamas']),
    ('requested a consultation', ['consultation', 'consult', 'schedule', 'meeting', 'moshavere']),
    ('asked for contact info',   ['contact', 'whatsapp', 'email', 'phone', 'reach']),
]


def generate_chat_summary(conversation: list) -> str:
    """
    Produce a clean 1–3 sentence summary from a conversation JSON.

    conversation: list of dicts with keys 'role' ('user'|'bot'|'agent') and
                  'text' or 'content'.
    """
    if not conversation:
        return 'Visitor contacted support via chat widget.'

    user_msgs = [
        (m.get('text', '') or m.get('content', '')).lower()
        for m in conversation
        if m.get('role') == 'user'
    ]
    if not user_msgs:
        return 'Visitor opened the chat widget but sent no messages.'

    full_text = ' '.join(user_msgs)

    # Collect matched topic labels
    matched_topics = [
        label for label, kws in _INTEREST_TOPICS
        if any(kw in full_text for kw in kws)
    ]

    # Collect matched intents
    matched_intents = [
        label for label, kws in _INTENT_PATTERNS
        if any(kw in full_text for kw in kws)
    ]

    parts = []
    if matched_topics:
        topic_str = ', '.join(matched_topics[:3])
        parts.append(f'Visitor asked about {topic_str}')

    if matched_intents:
        parts.append(' and '.join(matched_intents[:2]))

    if not parts:
        # Fallback: take first user message, strip to 100 chars
        first = user_msgs[0][:120].strip()
        return f'Visitor said: "{first}"'

    summary = '. '.join(parts).strip()
    if not summary.endswith('.'):
        summary += '.'
    return summary


def format_transcript_excerpt(conversation: list, max_lines: int = 6) -> str:
    """
    Return a short plain-text excerpt of the last `max_lines` messages,
    safe for Telegram HTML (entities escaped).
    """
    if not conversation:
        return ''

    recent = conversation[-max_lines:]
    lines = []
    for m in recent:
        role    = m.get('role', 'user')
        content = m.get('text', '') or m.get('content', '')
        content = html.escape(str(content)[:200])
        icon    = '👤' if role == 'user' else ('🧑‍💼' if role == 'agent' else '🤖')
        lines.append(f'{icon} <i>{content}</i>')

    return '\n'.join(lines)


def sanitize_text(value: str, max_len: int = 2000) -> str:
    """Strip dangerous characters and cap length. Used before DB storage."""
    if not isinstance(value, str):
        value = str(value)
    # Remove null bytes and control chars (keep newlines/tabs)
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    return value[:max_len].strip()
