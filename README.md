[![Build, test and publish](https://github.com/happydev-ca/spypoint-api/actions/workflows/publish.yml/badge.svg)](https://github.com/happydev-ca/spypoint-api/actions/workflows/publish.yml)

# spypoint-api

Library to communicate with Spypoint REST API.

## Usage

````python
import asyncio
from spypointapi import SpypointClient

async def run():
    async with SpypointClient("your-email@example.com", "your-password") as client:
        cameras = await client.get_cameras()
        print(f"Found {len(cameras)} cameras")

        async for item in client.iter_media([c.id for c in cameras], filters={"mediaTypes": ["hd", "hdvideo"]}):
            print(item.id, item.is_video, item.variants.get("large") and item.variants["large"].expires_at)

asyncio.run(run())
Quick example:

```python
import asyncio
from datetime import datetime
from spypointapi import SpypointApi


async def main():
    api = SpypointApi("you@example.com", "password")
    await api.login()
    cams = await api.get_cameras()
    page = await api.list_photos_page([cams[0].id], datetime.utcnow())
    async for p in api.iter_photos([cams[0].id], datetime.utcnow()):
        print(p.id, p.date)

asyncio.run(main())
````

````

### Build and test locally

```shell
make venv
source .venv/bin/activate
make test
make build
````

### Logging

Enable debug level to log API requests and responses.

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Release version

```shell
make release bump=patch|minor|major
```
