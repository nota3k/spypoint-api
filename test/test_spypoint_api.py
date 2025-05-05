import unittest
from datetime import datetime
from http import HTTPStatus

import aiohttp
import jwt

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from spypointapi import SpypointApi
from spypointapi.cameras.camera_api_response import CameraApiResponse
from spypointapi.spypoint_api import SpypointApiInvalidCredentialsError, SpypointApiError
from test.spypoint_server_for_test import SpypointServerForTest


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
                    "activationDate": "2023-05-22T03:01:24.575Z",
                    "config": {
                        "name": "camera 1",
                        "captureMode": "photo",
                        "motionDelay": 60,
                        "multiShot": 1,
                        "operationMode": "standard",
                        "quality": "high",
                        "sensibility": {
                            "high": 9,
                            "level": "low",
                            "low": 35,
                            "medium": 20
                        },
                        "timeFormat": 12,
                        "timeLapse": 3600,
                        "transmitAuto": True,
                        "transmitFreq": 6,
                        "transmitTime": {
                            "hour": 6,
                            "minute": 30
                        },
                    },
                    "status": {
                        "model": "model",
                        "lastUpdate": "2024-10-30T02:03:48.716Z",
                        "batteries": [73],
                        "temperature": {"value": 51, "unit": "C"},  # Added "unit" key
                        "signal": {"processed": {"percentage": 77}},
                    },
                    "isCellular": True,
                    "subscriptions": [
                        {
                            "paymentFrequency": "annual",
                            "isFree": True,
                            "startDateBillingCycle": "2024-09-04T12:54:53.421Z",
                            "monthEndBillingCycle": "2025-06-04T12:32:26.000Z",
                            "endDateBillingCycle": "2025-09-04T12:32:26.000Z",
                            "photoCount": 1,
                            "plan": {
                                "name": "Basic",
                                "isActive": True,
                                "isFree": True,
                                "photoCountPerMonth": 250,
                            },
                        }
                    ],
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

                # Validate new fields
                camera = cameras[0]
                self.assertEqual(camera.capture_mode, "photo")
                self.assertEqual(camera.motion_delay, 60)
                self.assertEqual(camera.multi_shot, 1)
                self.assertEqual(camera.operation_mode, "standard")
                self.assertEqual(camera.quality, "high")
                self.assertEqual(camera.sensibility, {
                    "high": 9,
                    "level": "low",
                    "low": 35,
                    "medium": 20
                })
                self.assertEqual(camera.time_format, 12)
                self.assertEqual(camera.time_lapse, 3600)
                self.assertTrue(camera.transmit_auto)
                self.assertEqual(camera.transmit_freq, 6)
                self.assertEqual(camera.transmit_time, {"hour": 6, "minute": 30})
                self.assertEqual(camera.temperature, 51)  # Validate temperature

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

    async def test_parse_camera_with_subscriptions(self):
        camera_json = {
            "id": "1",
            "config": {"name": "Test Camera"},
            "status": {"model": "Model1", "lastUpdate": "2025-05-04T16:50:03.000Z"},
            "subscriptions": [
                {
                    "paymentFrequency": "annual",
                    "isFree": True,
                    "startDateBillingCycle": "2024-09-04T12:54:53.421Z",
                    "endDateBillingCycle": "2025-09-04T12:32:26.000Z",
                    "monthEndBillingCycle": "2025-06-04T12:32:26.000Z",
                    "photoCount": 1,
                    "hdPhotoCount": 0,
                    "photoLimit": 250,
                    "hdPhotoLimit": 0,
                    "isAutoRenew": False,
                    "plan": {
                        "name": "Basic",
                        "isActive": True,
                        "isFree": True,
                        "photoCountPerMonth": 250,
                    },
                }
            ],
        }

        camera = CameraApiResponse.camera_from_json(camera_json)
        self.assertEqual(camera.id, "1")
        self.assertEqual(camera.name, "Test Camera")
        self.assertEqual(len(camera.subscriptions), 1)

        subscription = camera.subscriptions[0]
        self.assertEqual(subscription.payment_frequency, "annual")
        self.assertTrue(subscription.is_free)
        self.assertEqual(subscription.photo_count, 1)
        self.assertEqual(subscription.plan.name, "Basic")
        self.assertTrue(subscription.plan.is_active)
        self.assertEqual(subscription.plan.photo_count_per_month, 250)

    async def test_parse_camera_with_new_fields(self):
        camera_json = {
            "id": "1",
            "config": {
                "name": "Test Camera",
                "captureMode": "photo",
                "motionDelay": 60,
                "multiShot": 1,
                "operationMode": "standard",
                "quality": "high",
                "sensibility": {
                    "high": 9,
                    "level": "low",
                    "low": 35,
                    "medium": 20
                },
                "timeFormat": 12,
                "timeLapse": 3600,
                "transmitAuto": True,
                "transmitFreq": 6,
                "transmitTime": {
                    "hour": 6,
                    "minute": 30
                },
            },
            "status": {
                "model": "Model1",
                "lastUpdate": "2025-05-04T16:50:03.000Z",
            },
        }

        camera = CameraApiResponse.camera_from_json(camera_json)
        self.assertEqual(camera.id, "1")
        self.assertEqual(camera.name, "Test Camera")
        self.assertEqual(camera.capture_mode, "photo")
        self.assertEqual(camera.motion_delay, 60)
        self.assertEqual(camera.multi_shot, 1)
        self.assertEqual(camera.operation_mode, "standard")
        self.assertEqual(camera.quality, "high")
        self.assertEqual(camera.sensibility, {
            "high": 9,
            "level": "low",
            "low": 35,
            "medium": 20
        })
        self.assertEqual(camera.time_format, 12)
        self.assertEqual(camera.time_lapse, 3600)
        self.assertTrue(camera.transmit_auto)
        self.assertEqual(camera.transmit_freq, 6)
        self.assertEqual(camera.transmit_time, {"hour": 6, "minute": 30})
