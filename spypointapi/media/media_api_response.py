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
        preview_data = data.get("preview")
        if preview_data and isinstance(preview_data, list):
            preview_urls = [cls._url_from_json(p) for p in preview_data]
            previews = [url for url in preview_urls if url is not None]
        hd_video = cls._url_from_json(data.get("hdVideo"))
        medium = cls._url_from_json(data.get("medium"))
        small = cls._url_from_json(data.get("small"))

        origin_date = None
        origin_date_value = data.get("originDate")
        if origin_date_value:
            origin_date_str = str(origin_date_value)
            origin_date = datetime.fromisoformat(origin_date_str.rstrip("Z")).replace(tzinfo=current_tz)

        return Media(
            id=data["id"],
            camera=data.get("camera", ""),
            date=date,
            large=large,
            tags=tags,
            previews=previews,
            hd_video=hd_video,
            medium=medium,
            small=small,
            origin_date=origin_date,
            origin_name=data.get("originName"),
            origin_size=data.get("originSize"),
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
