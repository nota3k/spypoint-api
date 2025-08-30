"""Example: download a photo using SignedGet info returned by the API."""
import asyncio
import httpx
from spypointapi import SpypointApi


async def download_example(camera_id: str, photo_id: str):
    async with SpypointApi() as api:
        signed = await api.get_signed_get(photo_id)
        async with httpx.AsyncClient() as client:
            headers = {h['name']: h['value'] for h in signed.headers}
            resp = await client.get(signed.host + signed.path, headers=headers, timeout=30)
            resp.raise_for_status()
            with open(photo_id + '.jpg', 'wb') as f:
                f.write(resp.content)


if __name__ == '__main__':
    import sys
    camera_id = sys.argv[1] if len(sys.argv) > 1 else ''
    photo_id = sys.argv[2] if len(sys.argv) > 2 else ''
    asyncio.run(download_example(camera_id, photo_id))
