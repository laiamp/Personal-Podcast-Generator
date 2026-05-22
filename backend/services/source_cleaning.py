from __future__ import annotations

from typing import Any
import html
import re


_WHITESPACE_RE = re.compile(r"\s+")
_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _truncate_at_sentence(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text

    cutoff = text.rfind(".", 0, max_chars)
    if cutoff < max_chars * 0.6:
        cutoff = text.rfind("!", 0, max_chars)
    if cutoff < max_chars * 0.6:
        cutoff = text.rfind("?", 0, max_chars)
    if cutoff < max_chars * 0.6:
        cutoff = max_chars

    return text[:cutoff].rstrip()


def clean_source_summary(summary: Any, *, max_chars: int = 900) -> str:
    """Convert a noisy source summary into compact agent-ready context."""
    if summary is None:
        return ""

    text = str(summary)
    text = html.unescape(text)
    text = _CODE_FENCE_RE.sub(" ", text)
    text = _MARKDOWN_LINK_RE.sub(r"\1", text)
    text = _HTML_TAG_RE.sub(" ", text)
    text = text.replace("\r", " ").replace("\n", " ")
    text = _WHITESPACE_RE.sub(" ", text).strip()

    if not text:
        return ""

    return _truncate_at_sentence(text, max_chars)


def clean_source_for_agent(source: dict[str, Any], *, max_summary_chars: int = 900) -> dict[str, Any]:
    """Return a shallow, agent-ready version of a source document."""
    cleaned = dict(source)
    cleaned["summary"] = clean_source_summary(source.get("summary"), max_chars=max_summary_chars)
    return cleaned
