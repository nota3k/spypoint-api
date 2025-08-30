"""Typed exceptions for the spypoint_api package.

These are lightweight wrappers used by the client implementation.
"""
from __future__ import annotations

from typing import Any


class SpypointApiError(Exception):
    """Base exception for all spypoint api errors."""

    def __init__(self, status: int | None, message: str | None = None, data: Any | None = None) -> None:
        super().__init__(message or "spypoint api error")
        self.status = status
        self.message = message
        self.data = data


class SpypointApiInvalidCredentialsError(SpypointApiError):
    pass


class SpypointApiRateLimitError(SpypointApiError):
    pass


class SpypointApiServerError(SpypointApiError):
    pass
