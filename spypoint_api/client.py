"""Compatibility client wrapper exposing a modern API surface while delegating to legacy implementation.

This wrapper is intentionally small: it adapts the existing `spypointapi.client.SpypointApi`
to the `spypoint_api` package namespace, adds a simple config dataclass, and exposes
async context manager protocol for convenience.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Optional

from spypointapi.client import SpypointApi as _LegacySpypointApi

from ._version import __version__


@dataclass
class SpypointConfig:
    base_url: str = "https://restapi.spypoint.com"
    timeout: int = 30
    max_retries: int = 5
    concurrent_requests: int = 4


class SpypointApi:
    """Modern-facing API that delegates to the legacy implementation.

    This wrapper exists to provide a stable package entrypoint while we iterate on
    the full refactor. It will preserve previous method names and accept the same
    initializer signature as the legacy class.
    """

    def __init__(self, email: str | None = None, password: str | None = None, device_id: str | None = None, config: Optional[SpypointConfig] = None):
        self._config = config or SpypointConfig()
        # For now delegate to legacy implementation
        # Note: the legacy client expects email/password positional args
        self._legacy = _LegacySpypointApi(email or "", password or "", device_id, base_url=self._config.base_url)

    async def __aenter__(self) -> "SpypointApi":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self._legacy.close()

    # Delegate common methods
    async def login(self) -> None:
        return await self._legacy.login()

    async def list_cameras(self) -> list[Any]:
        return await self._legacy.get_cameras()

    async def iter_photos(self, *args, **kwargs):
        return self._legacy.iter_photos(*args, **kwargs)

    async def list_photos_page(self, *args, **kwargs):
        return await self._legacy.list_photos_page(*args, **kwargs)

    async def get_signed_get(self, photo_id: str):
        # legacy client may expose a helper under download; fallback not implemented here
        raise NotImplementedError("get_signed_get is not implemented in the compatibility wrapper")

    __all__ = ["SpypointApi", "SpypointConfig"]
