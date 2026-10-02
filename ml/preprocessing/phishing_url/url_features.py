from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse


FEATURE_VERSION = "cyberguard-url-v1"

FEATURE_NAMES = [
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfObfuscatedChar",
    "ObfuscationRatio",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
]


def _clean_url(url: str) -> str:
    """
    Clean only surrounding whitespace.

    IMPORTANT:
    We do not add http:// or https:// because that would
    change URLLength and character-based features.
    """
    if not isinstance(url, str):
        raise TypeError("url must be a string")

    url = url.strip()

    if not url:
        raise ValueError("url cannot be empty")

    return url


def _parse_url(url: str):
    """
    Parse the URL without changing the original URL used
    for feature calculations.

    For URLs without a scheme, http:// is added only to
    the parsing copy.
    """
    parse_target = url

    if "://" not in parse_target:
        parse_target = "http://" + parse_target

    return urlparse(parse_target)


def _is_ip_address(host: str | None) -> int:
    if not host:
        return 0

    try:
        ipaddress.ip_address(host)
        return 1
    except ValueError:
        return 0


def _extract_tld(domain: str) -> str:
    if not domain:
        return ""

    domain = domain.rstrip(".")
    parts = domain.split(".")

    if len(parts) < 2:
        return ""

    return parts[-1]


def _count_subdomains(domain: str) -> int:
    if not domain:
        return 0

    parts = [part for part in domain.split(".") if part]

    if len(parts) <= 2:
        return 0

    return len(parts) - 2


def _count_obfuscated_characters(url: str) -> int:
    """
    Count percent-encoded characters such as:
    %20
    %2F
    %3A
    """
    return len(re.findall(r"%[0-9A-Fa-f]{2}", url))


def _count_other_special_characters(url: str) -> int:
    """
    Count characters that are neither letters nor digits
    and are not the main URL/query delimiters.

    Excluded delimiters:
        : / . - _ = ? &

    Other characters such as @, #, %, ~, [, ], etc.
    are counted as other special characters.
    """
    excluded = set(":/.-_= ?&".replace(" ", ""))

    return sum(
        1
        for char in url
        if not char.isalnum() and char not in excluded
    )


def extract_url_features(url: str) -> dict[str, float | int]:
    """
    Extract the canonical CyberGuard URL-only feature set.

    Feature version:
        cyberguard-url-v1

    The function is deterministic:
        same URL -> same feature values
    """

    original_url = _clean_url(url)
    parsed = _parse_url(original_url)

    domain = parsed.hostname or ""
    tld = _extract_tld(domain)

    url_length = len(original_url)

    letters = sum(char.isalpha() for char in original_url)
    digits = sum(char.isdigit() for char in original_url)

    equals = original_url.count("=")
    question_marks = original_url.count("?")
    ampersands = original_url.count("&")

    obfuscated_chars = _count_obfuscated_characters(original_url)
    has_obfuscation = int(obfuscated_chars > 0)

    other_special_characters = _count_other_special_characters(
        original_url
    )

    special_characters = sum(
        1 for char in original_url if not char.isalnum()
    )

    features = {
        "URLLength": url_length,

        "DomainLength": len(domain),

        "IsDomainIP": _is_ip_address(domain),

        "TLDLength": len(tld),

        "NoOfSubDomain": _count_subdomains(domain),

        "HasObfuscation": has_obfuscation,

        "NoOfObfuscatedChar": obfuscated_chars,

        "ObfuscationRatio": (
            obfuscated_chars / url_length
            if url_length
            else 0.0
        ),

        "NoOfLettersInURL": letters,

        "LetterRatioInURL": (
            letters / url_length
            if url_length
            else 0.0
        ),

        "NoOfDegitsInURL": digits,

        "DegitRatioInURL": (
            digits / url_length
            if url_length
            else 0.0
        ),

        "NoOfEqualsInURL": equals,

        "NoOfQMarkInURL": question_marks,

        "NoOfAmpersandInURL": ampersands,

        "NoOfOtherSpecialCharsInURL": other_special_characters,

        "SpacialCharRatioInURL": (
            special_characters / url_length
            if url_length
            else 0.0
        ),

        "IsHTTPS": int(parsed.scheme.lower() == "https"),
    }

    return features


def extract_feature_vector(url: str) -> list[float]:
    """
    Return features in the exact canonical FEATURE_NAMES order.

    This is the vector that will later be supplied to XGBoost.
    """

    features = extract_url_features(url)

    return [
        float(features[name])
        for name in FEATURE_NAMES
    ]