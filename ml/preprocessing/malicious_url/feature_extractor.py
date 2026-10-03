"""
Canonical URL-only feature extraction for CyberGuard.

The model uses only features that can be calculated directly from a URL.
No target website needs to be visited.
"""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

import pandas as pd


URL_FEATURES = [
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


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _is_ip_address(domain: str) -> int:
    if not domain:
        return 0

    try:
        ipaddress.ip_address(domain)
        return 1
    except ValueError:
        return 0


def _count_subdomains(domain: str) -> int:
    if not domain:
        return 0

    parts = domain.lower().strip(".").split(".")

    if len(parts) <= 2:
        return 0

    return len(parts) - 2


def _count_obfuscated_characters(url: str) -> int:
    """
    Count common encoded/obfuscated URL sequences.

    Examples:
        %20
        %2F
        0x41
    """
    percent_encoded = len(
        re.findall(r"%[0-9a-fA-F]{2}", url)
    )

    hexadecimal_sequences = len(
        re.findall(r"0x[0-9a-fA-F]+", url, flags=re.IGNORECASE)
    )

    return percent_encoded + hexadecimal_sequences


def _count_other_special_characters(url: str) -> int:
    """
    Count special characters other than the normal URL structure.

    Normal URL delimiters are excluded:
        / : . ? & = # -
    """
    normal_url_characters = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "/:?.&#=-_"
    )

    return sum(
        1
        for char in url
        if char not in normal_url_characters
    )


def extract_url_features(url: str) -> dict[str, float]:
    """
    Extract the canonical CyberGuard URL feature vector.
    """
    if not isinstance(url, str):
        raise TypeError("URL must be a string.")

    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty.")

    normalized_url = url

    if not re.match(
        r"^[a-zA-Z][a-zA-Z0-9+.-]*://",
        normalized_url,
    ):
        normalized_url = "http://" + normalized_url

    parsed = urlparse(normalized_url)

    domain = parsed.hostname or ""

    url_length = len(url)

    letters = sum(char.isalpha() for char in url)
    digits = sum(char.isdigit() for char in url)

    equals_count = url.count("=")
    question_count = url.count("?")
    ampersand_count = url.count("&")

    other_special_characters = _count_other_special_characters(url)

    obfuscated_characters = _count_obfuscated_characters(url)

    tld_length = 0

    if "." in domain:
        tld = domain.rsplit(".", 1)[-1]
        tld_length = len(tld)

    return {
        "URLLength": url_length,
        "DomainLength": len(domain),
        "IsDomainIP": _is_ip_address(domain),
        "TLDLength": tld_length,
        "NoOfSubDomain": _count_subdomains(domain),
        "HasObfuscation": int(obfuscated_characters > 0),
        "NoOfObfuscatedChar": obfuscated_characters,
        "ObfuscationRatio": _safe_ratio(
            obfuscated_characters,
            url_length,
        ),
        "NoOfLettersInURL": letters,
        "LetterRatioInURL": _safe_ratio(
            letters,
            url_length,
        ),
        "NoOfDegitsInURL": digits,
        "DegitRatioInURL": _safe_ratio(
            digits,
            url_length,
        ),
        "NoOfEqualsInURL": equals_count,
        "NoOfQMarkInURL": question_count,
        "NoOfAmpersandInURL": ampersand_count,
        "NoOfOtherSpecialCharsInURL": other_special_characters,
        "SpacialCharRatioInURL": _safe_ratio(
            other_special_characters,
            url_length,
        ),
        "IsHTTPS": int(parsed.scheme.lower() == "https"),
    }


def extract_url_features_dataframe(
    urls: pd.Series,
) -> pd.DataFrame:
    """Extract URL features for a pandas Series."""
    rows = [
        extract_url_features(url)
        for url in urls
    ]

    return pd.DataFrame(
        rows,
        columns=URL_FEATURES,
    )