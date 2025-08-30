"""Quickstart example: login and list cameras asynchronously."""
import asyncio
import os
from spypoint_api import SpypointApi, __version__


async def main():
    username = os.environ.get("SPYPOINT_USERNAME")
    password = os.environ.get("SPYPOINT_PASSWORD")
    if not username or not password:
        print("Please set SPYPOINT_USERNAME and SPYPOINT_PASSWORD environment variables")
        return

    async with SpypointApi(username=username, password=password) as api:
        cams = await api.list_cameras()
        print(f"Found {len(cams)} cameras")
        for c in cams:
            print(c.id, getattr(c, 'ucid', None))


if __name__ == "__main__":
    asyncio.run(main())
