"""Iterate photos using the high-level helper iter_photos."""
import asyncio
from datetime import datetime, timezone, timedelta
from spypointapi import SpypointApi


async def main():
    async with SpypointApi() as api:
        since = datetime.now(timezone.utc) - timedelta(days=7)
        async for photo in api.iter_photos(["all"], since, limit=50):
            print(photo.id, photo.date)


if __name__ == '__main__':
    asyncio.run(main())
