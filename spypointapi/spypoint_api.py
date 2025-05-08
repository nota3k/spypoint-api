import asyncio
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import List, Dict, Any
import jwt
from aiohttp import ClientSession, ClientResponse, ClientResponseError

from spypointapi import Camera
from spypointapi.cameras.camera_api_response import CameraApiResponse
from spypointapi.shared_cameras.shared_cameras_api_response import SharedCamerasApiResponse


class SpypointApiError(ClientResponseError):
    pass


class SpypointApiInvalidCredentialsError(SpypointApiError):
    pass


class SpypointApi:
    base_url = 'https://restapi.spypoint.com/api/v3'

    def __init__(self, username: str, password: str, session: ClientSession):
        self.username = username
        self.password = password
        self.session = session
        self.headers = {'Content-Type': 'application/json'}
        self.expires_at = datetime.now() - timedelta(seconds=1)

    async def async_authenticate(self):
        if datetime.now() < self.expires_at:
            return

        json = {'username': self.username, 'password': self.password}
        async with self.session.post(f'{self.base_url}/user/login', json=json, headers=self.headers) as response:
            self._raise_on_authenticate_error(response)
            body = await response.json()
            jwt_token = body['token']
            claimset = jwt.decode(jwt_token, options={"verify_signature": False})
            self.headers['Authorization'] = 'Bearer ' + jwt_token
            self.expires_at = datetime.fromtimestamp(claimset['exp'])

    @staticmethod
    def _raise_on_authenticate_error(response: ClientResponse):
        if response.status == HTTPStatus.UNAUTHORIZED:
            raise SpypointApiInvalidCredentialsError(response.request_info, response.history, status=response.status, message=response.reason, headers=response.headers)
        if not response.ok:
            raise SpypointApiError(response.request_info, response.history, status=response.status, message=response.reason, headers=response.headers)

    async def async_get_cameras(self) -> List[Camera]:
        """
        Fetches both own and shared cameras and returns a combined list of Camera objects.
        """
        own_cameras = await self.async_get_own_cameras()
        shared_cameras = await self.async_get_shared_cameras()
        return own_cameras + shared_cameras

    async def async_get_own_cameras(self) -> List[Camera]:
        """
        Fetches the user's own cameras and parses them into Camera objects.
        """
        await self.async_authenticate()
        async with self.session.get(f'{self.base_url}/camera/all', headers=self.headers) as response:
            self._raise_on_get_error(response)
            body = await response.json()
            return CameraApiResponse.from_json(body)

    async def async_get_shared_cameras(self) -> List[Camera]:
        """
        Fetches shared cameras and parses them into Camera objects.
        """
        await self.async_authenticate()
        async with self.session.get(f'{self.base_url}/shared-cameras/all', headers=self.headers) as response:
            self._raise_on_get_error(response)
            body = await response.json()
            camera_ids = SharedCamerasApiResponse.from_json(body)
            gets_by_id = [self._async_get_shared_camera(camera_id) for camera_id in camera_ids]
            return await asyncio.gather(*gets_by_id)

    async def _async_get_shared_camera(self, camera_id: str) -> Camera:
        """
        Fetches a single shared camera by its ID and parses it into a Camera object.
        """
        await self.async_authenticate()
        async with self.session.get(f'{self.base_url}/shared-cameras/{camera_id}', headers=self.headers) as response:
            self._raise_on_get_error(response)
            body = await response.json()
            body['id'] = camera_id
            return CameraApiResponse.camera_from_json(body)

    async def _async_fetch_camera_models_data(self) -> List[Dict[str, Any]]:
        """
        Helper method to fetch raw camera models data from the API.
        """
        await self.async_authenticate()
        async with self.session.get(f'{self.base_url}/camera/models', headers=self.headers) as response:
            self._raise_on_get_error(response)
            return await response.json()

    async def async_get_camera_model_details(self) -> List[Dict[str, str]]:
        """
        Fetches all the name and icon URLs from the /api/v3/camera/models endpoint.

        :return: A list of dictionaries containing name and iconUrl.
        """
        models_data = await self._async_fetch_camera_models_data()
        return [
            {"name": model.get("name", ""), "iconUrl": model.get("iconUrl", "")}
            for model in models_data
            if "name" in model and "iconUrl" in model
        ]

    async def async_get_camera_model_icons(self) -> List[str]:
        """
        Fetches all the icon URLs from the /api/v3/camera/models endpoint.

        :return: A list of icon URLs.
        """
        models_data = await self._async_fetch_camera_models_data()
        return [model.get('iconUrl', '') for model in models_data if 'iconUrl' in model]

    def _raise_on_get_error(self, response: ClientResponse):
        """
        Handles errors during GET requests.
        """
        if response.status == HTTPStatus.UNAUTHORIZED:
            self.expires_at = datetime.now() - timedelta(seconds=1)
            del self.headers['Authorization']

        if not response.ok:
            raise SpypointApiError(
                response.request_info,
                response.history,
                status=response.status,
                message=response.reason,
                headers=response.headers,
            )
