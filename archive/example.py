"""
Archived example script.
Moved to `examples/example.py` during cleanup.
"""

import aiohttp
import asyncio
import os

from spypointapi import SpypointApi


async def run():
    async with aiohttp.ClientSession() as session:
        api = SpypointApi(os.environ['EMAIL'], os.environ['PASSWORD'], session)

        cameras = await api.get_cameras()
        for camera in cameras:
            print(camera)


if __name__ == "__main__":
    asyncio.run(run())
