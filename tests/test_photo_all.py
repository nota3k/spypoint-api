import asyncio
from datetime import datetime, timedelta

import respx
import httpx
import pytest

from spypointapi.client import SpypointApi
from spypointapi.models.photo import PhotoAllResponse


@pytest.mark.asyncio
async def test_parse_photo_all_fixture():
    api = SpypointApi("a@b.com", "pw")
    # load fixture
    import json
    from pathlib import Path

    data = json.loads(Path("tests/fixtures/POST_api_v3_photo_all.json").read_text())
    resp = PhotoAllResponse.model_validate(data)
    assert resp.countPhotos == 1
    assert len(resp.photos) == 1
    p = resp.photos[0]
    p.raw_json = data["photos"][0]
    assert p.raw_json["id"] == p.id


@pytest.mark.asyncio
async def test_iter_photos_pages(respx_mock):
    api = SpypointApi("a@b.com", "pw")
    # stub login
    respx_mock.post("https://restapi.spypoint.com/api/v3/user/login").mock(return_value=httpx.Response(200, json={"token":"t","uuid":"u"}))

    # page 1
    page1 = {
        "cameraIds": ["c1"],
        "countPhotos": 2,
        "photos": [
            {"id": "p2", "camera": "c1", "date": (datetime.utcnow()).isoformat() + "Z", "small": {"verb":"GET","host":"h","path":"p2" ,"headers":[]}, "medium": {"verb":"GET","host":"h","path":"p2","headers":[]}, "large": {"verb":"GET","host":"h","path":"p2","headers":[]}},
            {"id": "p1", "camera": "c1", "date": (datetime.utcnow() - timedelta(seconds=1)).isoformat() + "Z", "small": {"verb":"GET","host":"h","path":"p1","headers":[]}, "medium": {"verb":"GET","host":"h","path":"p1","headers":[]}, "large": {"verb":"GET","host":"h","path":"p1","headers":[]}},
        ],
    }
    # page 2 empty
    page2 = {"cameraIds": ["c1"], "countPhotos": 0, "photos": []}

    respx_mock.post("https://restapi.spypoint.com/api/v3/photo/all").mock(side_effect=[httpx.Response(200, json=page1), httpx.Response(200, json=page2)])

    seen = []
    async for p in api.iter_photos(["c1"], datetime.utcnow() + timedelta(seconds=5), limit=2):
        seen.append(p.id)

    assert seen == ["p2", "p1"]
