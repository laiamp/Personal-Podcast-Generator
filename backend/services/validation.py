from __future__ import annotations

from typing import Any
import re


def validate_script(script: Any) -> None:
    """Validate the generated podcast script.

    Raises a ValueError or TypeError when the script does not meet basic quality checks.
    Checks performed:
    - script is a string and not empty/whitespace
    - minimum word and character counts
    - contains sentence-ending punctuation
    - does not contain obvious placeholder tokens
    """
    if not isinstance(script, str):
        raise TypeError("Generated script must be a string")

    cleaned = script.strip()
    if not cleaned:
        raise ValueError("Generated script is empty or whitespace")

    # Basic size checks
    MIN_WORDS = 2
    MIN_CHARS = 10
    MAX_CHARS = 200_000

    words = len(re.findall(r"\w+", cleaned))
    chars = len(cleaned)

    if words < MIN_WORDS or chars < MIN_CHARS:
        raise ValueError(f"Generated script too short ({words} words, {chars} chars); expected at least {MIN_WORDS} words and {MIN_CHARS} chars.")

    if chars > MAX_CHARS:
        raise ValueError(f"Generated script too long ({chars} chars)")

    # Must contain at least one sentence terminator
    if not re.search(r"[\.\?\!]", cleaned):
        raise ValueError("Generated script appears to lack sentence punctuation")

    # Placeholder token checks
    placeholders = ["{{", "}}", "<TITLE>", "TODO", "REPLACE_ME"]
    for token in placeholders:
        if token in cleaned:
            raise ValueError(f"Generated script contains placeholder token: {token}")
