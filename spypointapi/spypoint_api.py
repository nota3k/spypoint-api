import asyncio
import logging
from datetime import datetime, timedelta
from http import HTTPStatus
from logging import Logger, getLogger
from typing import List
import jwt
from aiohttp import ClientSession, ClientResponse

from . import Camera, Media, SpypointApiError, SpypointApiInvalidCredentialsError
from .cameras.camera_model import CameraModel
from .cameras.camera_models_api_response import CameraModelsApiResponse
from .cameras.camera_api_response import CameraApiResponse
from .media.media_api_response import MediaApiResponse
from .shared_cameras.shared_cameras_api_response import SharedCamerasApiResponse

LOGGER: Logger = getLogger(__package__)


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
            await self._log('/user/login', response, self.headers, json)
            self._raise_on_authenticate_error(response)
            body = await response.json()
            jwt_token = body['token']
            claimset = jwt.decode(jwt_token, options={"verify_signature": False})
            self.headers['Authorization'] = 'Bearer ' + jwt_token
            self.expires_at = datetime.fromtimestamp(claimset['exp'])

    @staticmethod
    def _raise_on_authenticate_error(response: ClientResponse):
        if response.status == HTTPStatus.UNAUTHORIZED:
            raise SpypointApiInvalidCredentialsError(response)
        if not response.ok:
            raise SpypointApiError(response)

    async def async_get_cameras(self) -> List[Camera]:
        own_cameras = await self.async_get_own_cameras()
        shared_cameras = await self.async_get_shared_cameras()
        return own_cameras + shared_cameras

    async def async_get_own_cameras(self) -> List[Camera]:
        async with await self._get('/camera/all') as response:
            body = await response.json()
            return CameraApiResponse.from_json(body)

    async def async_get_shared_cameras(self) -> List[Camera]:
        async with await self._get('/shared-cameras/all') as response:
            body = await response.json()
            camera_ids = SharedCamerasApiResponse.from_json(body)
            gets_by_id = [self._async_get_shared_camera(camera_id) for camera_id in camera_ids]
            return await asyncio.gather(*gets_by_id)

    async def async_get_media(
        self,
        camera_ids: list[str] | None = None,
        before: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        offset: int | None = None,
        # Deprecated alias; prefer camera_ids
        cameras: list[str] | None = None,
    ) -> List[Media]:
        json = None
        # Map deprecated alias to camera_ids if provided
        if camera_ids is None and cameras:
            camera_ids = cameras

        if camera_ids or before or limit or page is not None or offset is not None:
            json = {}
            if camera_ids:
                json['cameraIds'] = camera_ids
            if before:
                json['before'] = before
            if limit:
                json['limit'] = limit
            if page is not None:
                json['page'] = page
            if offset is not None:
                json['offset'] = offset

        async with await self._post('/photo/all', json=json) as response:
            body = await response.json()
            return MediaApiResponse.from_json(body)

    async def async_get_camera_models(self) -> List[CameraModel]:
        async with await self._get('/camera/models') as response:
            body = await response.json()
            return CameraModelsApiResponse.from_json(body)

    async def _async_get_shared_camera(self, camera_id) -> Camera:
        async with await self._get(f'/shared-cameras/{camera_id}') as response:
            body = await response.json()
            body['id'] = camera_id
            return CameraApiResponse.camera_from_json(body)

    async def _get(self, url: str) -> ClientResponse:
        await self.async_authenticate()
        response = await self.session.get(f'{self.base_url}{url}', headers=self.headers)
        await self._log(url, response, self.headers)
        self._raise_on_get_error(response)
        return response

    async def _post(self, url: str, json: dict | None = None) -> ClientResponse:
        await self.async_authenticate()
        if json is None:
            response = await self.session.post(
                f'{self.base_url}{url}', headers=self.headers
            )
        else:
            response = await self.session.post(
                f'{self.base_url}{url}', headers=self.headers, json=json
            )
        await self._log(url, response, self.headers, json)
        self._raise_on_get_error(response)
        return response

    def _raise_on_get_error(self, response: ClientResponse):
        if response.status == HTTPStatus.UNAUTHORIZED:
            self.expires_at = datetime.now() - timedelta(seconds=1)
            self.headers.pop('Authorization', None)

        if not response.ok:
            raise SpypointApiError(response)

    @staticmethod
    async def _log(url: str, response: ClientResponse, headers: dict, json: dict = None) -> None:
        # Avoid overhead unless debug logging is enabled
        if not LOGGER.isEnabledFor(logging.DEBUG):
            return

        # Redact sensitive information
        redacted_headers = dict(headers or {})
        if 'Authorization' in redacted_headers:
            redacted_headers['Authorization'] = 'Bearer ****'

        redacted_body = None
        if isinstance(json, dict):
            redacted_body = json.copy()
            if 'password' in redacted_body:
                redacted_body['password'] = '****'
        else:
            redacted_body = json

        LOGGER.debug(
            f"{url} : Request[[ headers=[{redacted_headers}] body=[{redacted_body}] ]] - "
            f"Response[[ status=[{response.status}] headers=[{dict(response.headers)}] body=[{await response.text()}] ]]"
        )
