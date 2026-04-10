"""Shared utilities for V2Ray share link conversion."""

from __future__ import annotations

import base64
import random


class ParseError(Exception):
    """Raised when a share link cannot be parsed.

    Only this exception is caught by the parser — all other exceptions
    propagate, preserving the "skip malformed links" behaviour without
    swallowing unrelated errors.
    """


def base64_raw_std_decode(encoded: str) -> str:
    return base64.b64decode(encoded + "=" * (-len(encoded) % 4)).decode("utf-8")


def base64_raw_url_decode(encoded: str) -> str:
    return base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode("utf-8")


def url_safe(string: str) -> str:
    return string.replace("+", "-").replace("/", "_")


_USER_AGENTS: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
]


def rand_user_agent() -> str:
    return _USER_AGENTS[random.randint(0, len(_USER_AGENTS) - 1)]
