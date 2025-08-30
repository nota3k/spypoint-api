import httpx
import respx
import pytest

from spypointapi.client import SpypointApi


@pytest.mark.asyncio
async def test_login_then_401_relogin(respx_mock):
    api = SpypointApi("a@b.com", "pw")
    # first login
    respx_mock.post("https://restapi.spypoint.com/api/v3/user/login").mock(return_value=httpx.Response(200, json={"token":"t","uuid":"u"}))
    # first photo call returns 401, second after relogin returns 200
    route = respx_mock.post("https://restapi.spypoint.com/api/v3/photo/all")
    route.side_effect = [httpx.Response(401), httpx.Response(200, json={"cameraIds":[],"countPhotos":0,"photos":[]})]

    # should not raise
    await api.list_photos_page(["c"], "2025-01-01T00:00:00Z")


@pytest.mark.asyncio
async def test_rate_limit_retry(respx_mock):
    api = SpypointApi("a@b.com", "pw")
    respx_mock.post("https://restapi.spypoint.com/api/v3/user/login").mock(return_value=httpx.Response(200, json={"token":"t","uuid":"u"}))
    # force 429 then success
    r = respx_mock.post("https://restapi.spypoint.com/api/v3/photo/all")
    r.side_effect = [httpx.Response(429, headers={"Retry-After": "0"}), httpx.Response(200, json={"cameraIds":[],"countPhotos":0,"photos":[]})]

    res = await api.list_photos_page(["c"], "2025-01-01T00:00:00Z")
    assert res.countPhotos == 0
