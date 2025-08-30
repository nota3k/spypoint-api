"""
Archived: spypointapi.download

This file was moved to the archive directory as part of the repository cleanup (OPTION B).
It is retained here for historical/reference purposes. Do not import from archive in production code.
"""

from pathlib import Path
from typing import Any
import httpx

from spypointapi.models.photo import SignedGet


async def download(signed: SignedGet, dest_path: Path, client: httpx.AsyncClient, *, chunk: int = 1 << 20) -> None:
    scheme = "https"
    host = signed.host
    path = signed.path.lstrip("/")
    url = f"{scheme}://{host}/{path}"

    headers = {h.name: h.value for h in (signed.headers or [])}

    resp = await client.get(url, headers=headers, timeout=60.0)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk_bytes in resp.iter_bytes(chunk):
            f.write(chunk_bytes)
