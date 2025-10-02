"""Custom exception types for the HarmonyKit package."""

from __future__ import annotations


class HarmonyKitError(Exception):
    """Base class for HarmonyKit-specific errors."""


class InvalidPieceIdError(HarmonyKitError):
    """Raised when a piece identifier fails basic validation."""


class PieceNotFoundError(HarmonyKitError):
    """Raised when no annotation file exists for the requested piece."""


class MultipleMatchesError(HarmonyKitError):
    """Raised when more than one annotation file matches a requested piece."""


__all__ = [
    "HarmonyKitError",
    "InvalidPieceIdError",
    "PieceNotFoundError",
    "MultipleMatchesError",
]
