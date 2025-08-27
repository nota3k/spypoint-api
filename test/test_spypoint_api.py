import unittest
from datetime import datetime
from http import HTTPStatus

import aiohttp
import jwt

from spypointapi import SpypointApi
from spypointapi.cameras.camera_api_response import CameraApiResponse
from spypointapi.cameras.camera_models_api_response import CameraModelsApiResponse
from spypointapi.media.media_api_response import MediaApiResponse
from spypointapi.spypoint_api import SpypointApiInvalidCredentialsError, SpypointApiError
from .spypoint_server_for_test import SpypointServerForTest


class TestSpypointApi(unittest.IsolatedAsyncioTestCase):
    username = 'username'
    password = 'password'

    async def test_authenticates_with_username_and_password(self):
        with SpypointServerForTest() as server:
            token = jwt.encode({'exp': 1627417600}, 'secret')
            server.prepare_login_response({'token': token})

            async with aiohttp.ClientSession() as session:
                api = SpypointApi(self.username, self.password, session)
                await api.async_authenticate()

                server.assert_called_with(url='/user/login',
                                          method='POST',
                                          headers={'Content-Type': 'application/json'},
                                          json={'username': self.username, 'password': self.password})

                self.assertEqual(api.headers.get('Authorization'), f'Bearer {token}')
                self.assertEqual(api.expires_at, datetime.fromtimestamp(1627417600))

    async def test_authenticate_invalid_credentials_error(self):
        with SpypointServerForTest() as server:
            server.prepare_login_response(status=HTTPStatus.UNAUTHORIZED)

            async with aiohttp.ClientSession() as session:
                api = SpypointApi(self.username, self.password, session)

                with self.assertRaises(SpypointApiInvalidCredentialsError):
                    await api.async_authenticate()

    async def test_authenticate_other_error(self):
        with SpypointServerForTest() as server:
            server.prepare_login_response(status=HTTPStatus.SERVICE_UNAVAILABLE)

            async with aiohttp.ClientSession() as session:
                api = SpypointApi(self.username, self.password, session)

                with self.assertRaises(SpypointApiError):
                    await api.async_authenticate()

    async def test_get_own_cameras(self):
        with SpypointServerForTest() as server:
            cameras_response = [
                {
                    "id": "1",
                    "config": {
                        "name": "camera 1",
                    },
                    "status": {
                        "model": "model",
                        "lastUpdate": "2024-10-30T02:03:48.716Z",
                    }
                },
                {
                    "id": "2",
                    "config": {
                        "name": "camera 2",
                    },
                    "status": {
                        "model": "model",
                        "lastUpdate": "2024-10-30T02:03:48.716Z",
                    }
                }
            ]

            token = server.prepare_login_response()
            server.prepare_cameras_response(cameras_response)

            async with aiohttp.ClientSession() as session:
                api = SpypointApi(self.username, self.password, session)
                cameras = await api.async_get_own_cameras()

                server.assert_called_with(
                    url='/camera/all',
                    method='GET',
                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

                expected_cameras = CameraApiResponse.from_json(cameras_response)
                self.assertEqual(cameras, expected_cameras)

    async def test_get_shared_cameras(self):
        with SpypointServerForTest() as server:
            token = server.prepare_login_response()

            camera_id = "id1"
            shared_cameras_response = [{"sharedCameras": [{"cameraId": camera_id}]}]
            server.prepare_shared_cameras_response(shared_cameras_response)

            shared_camera_response = {
                "config": {"name": "camera 1", },
                "status": {"model": "model", "lastUpdate": "2024-10-30T02:03:48.716Z", }
            }
            server.prepare_shared_camera_response(camera_id, shared_camera_response)

            async with aiohttp.ClientSession() as session:
                api = SpypointApi(self.username, self.password, session)
                cameras = await api.async_get_shared_cameras()

                server.assert_called_with(
                    url='/shared-cameras/all',
                    method='GET',
                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

                server.assert_called_with(
                    url=f'/shared-cameras/{camera_id}',
                    method='GET',
                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

                expected_camera = CameraApiResponse.camera_from_json({
                    "id": camera_id,
                    "config": {"name": "camera 1", },
                    "status": {"model": "model", "lastUpdate": "2024-10-30T02:03:48.716Z", }
                })
                self.assertEqual(cameras, [expected_camera])

    async def test_get_media(self):
        with SpypointServerForTest() as server:
            token = server.prepare_login_response()
            photos_response = {
                "photos": [
                    {
                        "id": "img1",
                        "camera": "c1",
                        "date": "2025-01-01T00:00:00.000Z",
                        "large": {"host": "s3.amazonaws.com", "path": "image1.jpg"},
                        "tag": ["day"],
                    },
                    {
                        "id": "vid1",
                        "camera": "c1",
                        "date": "2025-01-02T00:00:00.000Z",
                        "large": {"host": "s3.amazonaws.com", "path": "vid1.jpg"},
                        "preview": [
                            {"host": "s3.amazonaws.com", "path": "vid1.jpg"},
                            {"host": "s3.amazonaws.com", "path": "vid1_2.jpg"},
                            {"host": "s3.amazonaws.com", "path": "vid1_3.jpg"},
                        ],
                        "tag": ["day", "hdvideo"],
                        "hdVideo": {"host": "s3.amazonaws.com", "path": "vid1.mp4"},
                    },
                    {
                        "id": "prev1",
                        "camera": "c1",
                        "date": "2025-01-03T00:00:00.000Z",
                        "large": {"host": "s3.amazonaws.com", "path": "prev1.jpg"},
                        "preview": [
                            {"host": "s3.amazonaws.com", "path": "prev1.jpg"},
                            {"host": "s3.amazonaws.com", "path": "prev1_2.jpg"},
                            {"host": "s3.amazonaws.com", "path": "prev1_3.jpg"},
                        ],
                        "tag": ["preview"],
                    },
                ]
            }
            server.prepare_photos_response(photos_response)

            async with aiohttp.ClientSession() as session:
                api = SpypointApi(self.username, self.password, session)
                media = await api.async_get_media()

                server.assert_called_with(
                    url='/photo/all',
                    method='POST',
                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

                expected_media = MediaApiResponse.from_json(photos_response)
                self.assertEqual(media, expected_media)

    async def test_get_cameras_authentication_error(self):
        with SpypointServerForTest() as server:
            server.prepare_login_response()
            server.prepare_cameras_response(status=HTTPStatus.UNAUTHORIZED)

            async with aiohttp.ClientSession() as session:
                api = SpypointApi(self.username, self.password, session)

                with self.assertRaises(SpypointApiError):
                    await api.async_get_cameras()

                self.assertLess(api.expires_at, datetime.now())
                self.assertIsNone(api.headers.get('Authorization'))

    async def test_get_camera_models(self):
        with SpypointServerForTest() as server:
            token = server.prepare_login_response()

            models_response = [
                {"name": "CELL-LINK", "iconUrl": "https://icons/CELL-LINK.png", "variants": ["CELL-LINK-V"]},
                {"name": "FLEX", "iconUrl": "https://icons/FLEX.png", "variants": []},
            ]
            server.prepare_camera_models_response(models_response)

            async with aiohttp.ClientSession() as session:
                api = SpypointApi(self.username, self.password, session)
                models = await api.async_get_camera_models()

                server.assert_called_with(
                    url='/camera/models',
                    method='GET',
                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
                )

                expected_models = CameraModelsApiResponse.from_json(models_response)
                self.assertEqual(models, expected_models)
