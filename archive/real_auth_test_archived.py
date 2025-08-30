"""
Archived sensitive real auth test (renamed to avoid pytest collection).
"""

import asyncio
from aiohttp import ClientSession
from spypointapi import SpypointApi

USERNAME = "svomak@gmail.com"
PASSWORD = "prow-winkle-record"

async def main():
    async with ClientSession() as session:
        api = SpypointApi(USERNAME, PASSWORD, session)
        await api.async_authenticate()

        cameras = await api.get_cameras()
        print("Cameras:", cameras)

if __name__ == "__main__":
    asyncio.run(main())
