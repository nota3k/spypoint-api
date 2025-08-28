from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .media import Media


@dataclass()
class MediaResponse:
    camera_id: Optional[str]
    camera_ids: List[str]
    count_photos: Optional[int]
    photos: List[Media]


class MediaApiResponse:
    @staticmethod
    def _url_from_json(data: Dict[str, Any] | None) -> str | None:
        if not data:
            return None
        host = data.get("host")
        path = data.get("path")
        if not host or not path:
            return None
        return f"https://{host}/{path}"

    @classmethod
    def media_from_json(cls, data: Dict[str, Any]) -> Media:
        date_str = data.get("date", "")
        current_tz = datetime.now().astimezone().tzinfo
        date = datetime.fromisoformat(date_str.rstrip("Z")).replace(tzinfo=current_tz)
        tags = data.get("tag", [])
        large = cls._url_from_json(data.get("large"))
        previews = None
        if data.get("preview"):
            previews = [cls._url_from_json(p) for p in data.get("preview")]
        hd_video = cls._url_from_json(data.get("hdVideo"))
        return Media(
            id=data["id"],
            camera=data.get("camera", ""),
            date=date,
            large=large,
            tags=tags,
            previews=previews,
            hd_video=hd_video,
        )

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> MediaResponse:
        photos_data = data.get("photos", [])
        photos = [cls.media_from_json(photo) for photo in photos_data]
        return MediaResponse(
            camera_id=data.get("cameraId"),
            camera_ids=data.get("cameraIds", []) or [],
            count_photos=data.get("countPhotos"),
            photos=photos,
        )
