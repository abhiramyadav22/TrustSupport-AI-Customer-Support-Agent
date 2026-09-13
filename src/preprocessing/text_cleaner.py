"""Text cleaning and normalization utilities for Twitter customer support messages."""

import re
from typing import Tuple


USER_MENTION_PATTERN = re.compile(r"@\w+")
CUSTOMER_NUMERIC_ID_PATTERN = re.compile(r"@\d+")
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
WHITESPACE_PATTERN = re.compile(r"\s+")
SPECIAL_CHARS_PATTERN = re.compile(r"[^\w\s.,?!'\"]+")


def clean_tweet_text(
    text: str,
    strip_brand_mentions: bool = True,
    normalize_urls: bool = True,
    brand_handle: str = "",
) -> str:
    """Cleans noisy tweet text for NLP classification and retrieval.

    Args:
        text: Raw tweet text
        strip_brand_mentions: Whether to remove the brand handle prefix
        normalize_urls: Whether to replace urls with [URL] token
        brand_handle: Specific brand handle (e.g., 'AppleSupport' or 'AmazonHelp')

    Returns:
        Normalized text string
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    cleaned = text.strip()

    # Normalize customer anonymized IDs e.g. @115712 -> @customer
    cleaned = CUSTOMER_NUMERIC_ID_PATTERN.sub("@customer", cleaned)

    # Optionally strip specific brand handle e.g. @AppleSupport
    if brand_handle:
        pattern = re.compile(rf"@{re.escape(brand_handle)}\b", re.IGNORECASE)
        cleaned = pattern.sub("", cleaned)

    if strip_brand_mentions:
        # Remove remaining brand mentions at the very start of the tweet
        cleaned = re.sub(r"^(@\w+\s*)+", "", cleaned)

    if normalize_urls:
        cleaned = URL_PATTERN.sub("[URL]", cleaned)

    # Normalize excessive whitespace and line breaks
    cleaned = WHITESPACE_PATTERN.sub(" ", cleaned).strip()

    return cleaned


def assess_message_quality(text: str) -> Tuple[bool, str]:
    """Evaluates whether a customer message contains enough substance to classify/auto-handle.

    Returns:
        (is_sufficient, reason)
    """
    cleaned = clean_tweet_text(text)
    words = cleaned.split()

    if len(cleaned) < 10 or len(words) < 2:
        return False, "Message is too short to establish intent context."

    if len(words) > 100:
        return False, "Message exceeds standard single-issue length; requires multi-turn review."

    # Check for pure gibberish or symbols
    alpha_chars = sum(1 for c in cleaned if c.isalpha())
    if alpha_chars / max(len(cleaned), 1) < 0.4:
        return False, "Message contains high proportion of non-alphabetic noise."

    return True, "Valid message quality."
