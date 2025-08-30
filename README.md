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

### Regenerating models

The Pydantic models in this project are generated from the OpenAPI spec `spec/spypoint.openapi.json` using datamodel-code-generator. The repository separates auto-generated output from maintainer edits so generation is safe:

- Auto-generated file: `spypointapi/models/_generated_auto.py` (overwritten by the generator)
- Manual edits: `spypointapi/models/_generated_manual.py` (keep local edits here)
- Public import shim: `spypointapi/models/generated.py` — this prefers symbols from the manual file and falls back to the auto file.

Prerequisites

- Python virtualenv active (recommended). You can use the repository `make venv` target.
- Install the generator tool:

```sh
pip install datamodel-code-generator
```

Run the generator (recommended):

```sh
python scripts/regen_models.py
# or the equivalent helper
python tools/regen_models.py
```

What the generator does

- Writes generated Pydantic v2 models to `spypointapi/models/_generated_auto.py`.
- Do NOT directly edit `_generated_auto.py`; place any hand edits in `_generated_manual.py` so they are preserved across regenerations.

After regenerating

- Run the test suite and linter before committing:

```sh
make test
ruff .
```

- Commit only intentional changes. If regeneration produced many changes, prefer a dedicated branch and a focused PR that explains the model changes.

Notes

- The regen helpers in `scripts/regen_models.py` and `tools/regen_models.py` call `datamodel-codegen` with these important flags: `--output-model-type pydantic_v2.BaseModel`, `--openapi-scopes paths`, and `--extra-fields allow`. These are tuned for this repository's Pydantic v2 usage and to preserve unknown fields on parsed responses.
- If you need to change generation options, update the helper scripts and re-run the generator.
