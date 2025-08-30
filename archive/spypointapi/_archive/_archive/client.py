"""
ARCHIVE: experimental high-level client (clean, self-contained reference)

This archived file is a compact, import-friendly reference of the high-level
client prototype. It intentionally does not rely on relative package imports
so it can be inspected or imported without pulling in the full project.
Do not use this copy in production; prefer the package's canonical implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Dict, Optional, AsyncIterator
import asyncio
from contextlib import asynccontextmanager
import importlib

# Optional HTTP client import; this file is a reference and importing aiohttp is
# optional. If aiohttp is unavailable, code paths that require it won't run.
try:
    import aiohttp  # type: ignore
except Exception:  # pragma: no cover - archival fallback
    aiohttp = None  # type: ignore


@dataclass
class Camera:
    id: str
    name: str
    model: Optional[str] = None
    camera_firmware: Optional[str] = None


@dataclass
class MediaUrl:
    url: str
    content_type: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class MediaItem:
    id: str
    camera: str
    date: Optional[datetime]
    large: Optional[str] = None
    medium: Optional[str] = None
    small: Optional[str] = None
    hd_video: Optional[str] = None
    tags: Optional[List[str]] = None


class _StubSpypointApi:
    """Minimal stub of the low-level API used by the archived client."""

    def __init__(self, *args, **kwargs):
        pass

    async def async_get_cameras(self) -> List[Camera]:
        return []

    async def async_get_media(self, **kwargs) -> Any:
        return type("Resp", (), {"photos": []})()


def make_photo_query(camera_ids: Optional[List[str]] = None, *, from_dt: Optional[datetime] = None, to_dt: Optional[datetime] = None, filters: Optional[Dict[str, Any]] = None, limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]:
    q: Dict[str, Any] = {"limit": limit}
    if camera_ids:
        q["camera"] = camera_ids
    if from_dt:
        q["dateStart"] = from_dt.isoformat()
    if to_dt:
        q["dateEnd"] = to_dt.isoformat()
    if filters:
        for k in ("species", "timeOfDay", "mediaTypes", "customTags"):
            if k in filters:
                q[k] = filters[k]
    if cursor:
        q["cursor"] = cursor
    return q


@asynccontextmanager
async def qps_guard(qps: float):
    # Very small, local QPS guard used in the archived example. This is not
    # production-grade; it's only here so the reference code can run safely.
    if qps <= 0:
        yield
        return
    interval = 1.0 / qps
    await asyncio.sleep(interval)
    try:
        yield
    finally:
        return


# tenacity-like fallbacks
_tenacity = None
try:
    _tenacity = importlib.import_module("tenacity")
except Exception:
    _tenacity = None

if _tenacity is not None:
    retry = _tenacity.retry
    stop_after_attempt = _tenacity.stop_after_attempt
    wait_exponential = _tenacity.wait_exponential
    retry_if_exception_type = _tenacity.retry_if_exception_type
else:
    def retry(*_args, **_kwargs):
        def _decorator(f):
            return f

        return _decorator


    def stop_after_attempt(_n):
        return None


    def wait_exponential(*_args, **_kwargs):
        return None


    def retry_if_exception_type(_exc):
        return None


class SpypointClient:
    """Small, self-contained archived reference of a high-level Spypoint client."""

    def __init__(self, email: str, password: str, session: Any = None, *, qps: float = 3.0):
        self.email = email
        self.password = password
        self.session = session
        self.own_session = session is None
        self.qps = qps
        # Use the low-level API stub in this archived copy.
        self._api = _StubSpypointApi()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # If we created a session here we'd close it; archived copy keeps it simple.
        return False

    @retry()
    async def _api_call(self, coro):
        async with qps_guard(self.qps):
            return await coro

    async def get_cameras(self) -> List[Camera]:
        raw = await self._api_call(self._api.async_get_cameras())
        return [self._map_camera(r) for r in raw]

    def _map_camera(self, raw: Any) -> Camera:
        # Raw mapping in the archived reference: expect an object with attributes.
        return Camera(id=getattr(raw, "id", ""), name=getattr(raw, "name", ""), model=getattr(raw, "model", None), camera_firmware=getattr(raw, "camera_firmware", None))

    async def list_media(self, camera_ids: Optional[List[str]] = None, *, from_dt: Optional[datetime] = None, to_dt: Optional[datetime] = None, limit: int = 100, filters: Optional[Dict[str, Any]] = None, cursor: Optional[str] = None) -> tuple[List[MediaItem], Optional[str]]:
        query = make_photo_query(camera_ids, from_dt=from_dt, to_dt=to_dt, filters=filters, limit=limit, cursor=cursor)
        resp = await self._api_call(self._api.async_get_media(**query))
        items = [self._map_media_item(p) for p in getattr(resp, "photos", [])]
        return items, None

    async def iter_media(self, camera_ids: Optional[List[str]] = None, *, from_dt: Optional[datetime] = None, to_dt: Optional[datetime] = None, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> AsyncIterator[MediaItem]:
        cursor = None
        while True:
            items, next_cursor = await self.list_media(camera_ids, from_dt=from_dt, to_dt=to_dt, limit=limit, filters=filters, cursor=cursor)
            for it in items:
                yield it
            if not next_cursor:
                break
            cursor = next_cursor

    def _map_media_item(self, raw: Any) -> MediaItem:
        return MediaItem(id=getattr(raw, "id", ""), camera=getattr(raw, "camera", ""), date=None, large=getattr(raw, "large", None), medium=getattr(raw, "medium", None), small=getattr(raw, "small", None), hd_video=getattr(raw, "hd_video", None), tags=getattr(raw, "tags", None))

