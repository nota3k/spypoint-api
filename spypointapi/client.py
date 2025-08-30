from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, wait_exponential_jitter, stop_after_attempt

from .errors import (
    SpypointApiError,
    SpypointApiInvalidCredentialsError,
    SpypointApiRateLimitError,
    SpypointApiServerError,
)
from .models.photo import (
    PhotoAllRequest,
    PhotoAllResponse,
    PhotoItem,
)
from .models.camera import Camera
from ._utils import attach_raw_json_to_model

LOGGER = logging.getLogger(__name__)


class SpypointApi:
    def __init__(self, email: str, password: str, device_id: str | None = None, base_url: str = "https://restapi.spypoint.com"):
        self.email = email
        self.password = password
        self.device_id = device_id
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None
        self.token: str | None = None
        self.refresh: str | None = None
        self.uuid: str | None = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def login(self) -> None:
        client = await self._ensure_client()
        body = {"username": self.email, "password": self.password, "deviceID": self.device_id}
        # don't log password
        resp = await client.post("/api/v3/user/login", json=body)
        if resp.status_code == 401:
            raise SpypointApiInvalidCredentialsError(resp.status_code, "invalid credentials", resp.text)
        if not resp.is_success:
            raise SpypointApiError(resp.status_code, "login failed", resp.text)
        data = resp.json()
        self.token = data.get("token")
        self.refresh = data.get("refresh")
        self.uuid = data.get("uuid")

    def _auth_header(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _retry_decorator(self):
        return retry(
            retry=retry_if_exception_type((SpypointApiRateLimitError, SpypointApiServerError)),
            wait=wait_exponential_jitter(initial=0.5, max=10),
            stop=stop_after_attempt(4),
        )

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        client = await self._ensure_client()

        @self._retry_decorator()
        async def _do_request():
            headers = kwargs.pop("headers", {}) or {}
            headers.update(self._auth_header())
            try:
                r = await client.request(method, path, headers=headers, **kwargs)
            except httpx.RequestError as exc:
                raise SpypointApiError(0, f"request error: {exc}")

            if r.status_code == 401:
                # try to re-auth once
                LOGGER.debug("401 received, attempting re-login")
                await self.login()
                headers = kwargs.pop("headers", {}) or {}
                headers.update(self._auth_header())
                r = await client.request(method, path, headers=headers, **kwargs)
                if r.status_code == 401:
                    raise SpypointApiInvalidCredentialsError(401, "unauthorized after re-login", r.text)

            if r.status_code == 429:
                ra = r.headers.get("Retry-After")
                if ra:
                    try:
                        wait = int(ra)
                        await asyncio.sleep(wait)
                    except Exception:
                        pass
                raise SpypointApiRateLimitError(429, "rate limited", r.text)

            if 500 <= r.status_code < 600:
                raise SpypointApiServerError(r.status_code, "server error", r.text)

            if not r.is_success:
                raise SpypointApiError(r.status_code, "http error", r.text)

            try:
                return r.json()
            except Exception:
                return r.text

        return await _do_request()

    # endpoints
    async def get_cameras(self) -> list[Camera]:
        data = await self._request("GET", "/api/v3/camera/all")
        out: list[Camera] = []
        for item in data or []:
            cam = Camera.model_validate(item)
            attach_raw_json_to_model(cam, item)
            out.append(cam)
        return out

    async def get_custom_tags(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/api/v3/user/custom-tags")
        attach_raw_json_to_model(data, data)
        return data

    async def get_notifications(self, offset: int, limit: int, type: str) -> dict[str, Any]:
        params = {"offset": str(offset), "limit": str(limit), "type": type}
        data = await self._request("GET", "/api/v3/notification/all", params=params)
        attach_raw_json_to_model(data, data)
        return data

    async def get_subscriptions(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/api/v3/storage/subscription")
        attach_raw_json_to_model(data, data)
        return data

    async def get_plans(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/api/v3/storage/plan")
        attach_raw_json_to_model(data, data)
        return data

    async def get_hd(self) -> dict[str, Any]:
        data = await self._request("GET", "/api/v3/hd")
        attach_raw_json_to_model(data, data)
        return data

    async def get_shared_cameras(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/api/v3/shared-cameras/all")
        attach_raw_json_to_model(data, data)
        return data

    async def get_markers(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/api/v3/markers")
        attach_raw_json_to_model(data, data)
        return data

    async def get_photo_filters(self, cameraModel: str) -> dict[str, Any]:
        data = await self._request("GET", "/api/v3/photo/filters", params={"cameraModel": cameraModel})
        attach_raw_json_to_model(data, data)
        return data

    async def list_photos_page(
        self,
        camera: list[str],
        date_end,  # datetime
        limit: int = 100,
        media_types: list[Any] | None = None,
        species: list[Any] | None = None,
        time_of_day: list[Any] | None = None,
        custom_tags: list[Any] | None = None,
    ) -> PhotoAllResponse:
        req = PhotoAllRequest(
            camera=camera,
            dateEnd=date_end,
            limit=limit,
            mediaTypes=media_types or [],
            species=species or [],
            timeOfDay=time_of_day or [],
            customTags=custom_tags or [],
        )
        # Ensure datetimes are serialized to JSON-compatible strings
        import json as _json

        body_json = _json.loads(req.model_dump_json(by_alias=True))
        data = await self._request("POST", "/api/v3/photo/all", json=body_json)
        resp = PhotoAllResponse.model_validate(data)
        attach_raw_json_to_model(resp, data)
        photos_payload = data.get("photos", [])
        for p in resp.photos:
            # attach raw json
            attach_raw_json_to_model(p, next((d for d in photos_payload if d.get("id") == p.id), {}))
        return resp

    async def iter_photos(self, camera: list[str], start_from, limit: int = 100, **filters):
        from datetime import timedelta

        date_end = start_from
        seen = set()
        while True:
            page = await self.list_photos_page(camera, date_end, limit, **filters)
            if not page.photos:
                break
            for item in page.photos:
                if item.id in seen:
                    continue
                seen.add(item.id)
                yield item
            oldest = min(p.date for p in page.photos)
            if oldest.microsecond:
                date_end = oldest.replace(microsecond=max(0, oldest.microsecond - 1))
            else:
                date_end = oldest - timedelta(seconds=1)
            if len(page.photos) < limit:
                break
