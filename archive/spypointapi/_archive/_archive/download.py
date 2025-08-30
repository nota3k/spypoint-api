"""
ARCHIVE: archived download helpers

Lightweight utilities for building media URLs and downloading media. Kept for
reference; use production implementations from the main package when available.
"""

from pathlib import Path
from typing import Dict, Any
import aiohttp
from datetime import datetime, timedelta


class MediaUrl:
    def __init__(self, url: str, content_type: str | None = None, expires_at: datetime | None = None):
        self.url = url
        self.content_type = content_type
        self.expires_at = expires_at

    @classmethod
    def from_variant_dict(cls, variant_dict: Dict[str, Any]) -> "MediaUrl":
        # Assuming variant_dict has 'host', 'path', 'verb', 'headers', etc.
        host = variant_dict.get("host")
        path = variant_dict.get("path")
        headers = variant_dict.get("headers", {})
        query = variant_dict.get("query", {})

        url = f"https://{host}/{path}"
        if query:
            url += "?" + "&".join(f"{k}={v}" for k, v in query.items())

        content_type = headers.get("Content-Type")
        expires_at = None
        if "X-Amz-Expires" in query:
            expires_at = datetime.now() + timedelta(seconds=int(query["X-Amz-Expires"]))

        return cls(url, content_type, expires_at)


async def download(url: MediaUrl, dest_path: Path, session: aiohttp.ClientSession, *, chunk: int = 1 << 20) -> None:
    async with session.get(url.url, headers={"Accept": url.content_type} if url.content_type else None) as response:
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            async for chunk_data in response.content.iter_chunked(chunk):
                f.write(chunk_data)
