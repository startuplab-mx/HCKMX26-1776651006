"""Nahual Legal — programmatic Mexican legal framework integration."""
from .framework import (
    ARTICLES,
    AUTHORITIES,
    Authority,
    LegalArticle,
    LegalContext,
    get_consent_text,
    get_legal_context,
    get_privacy_disclaimer,
    serialize_context,
)

__all__ = [
    "ARTICLES",
    "AUTHORITIES",
    "Authority",
    "LegalArticle",
    "LegalContext",
    "get_consent_text",
    "get_legal_context",
    "get_privacy_disclaimer",
    "serialize_context",
]
