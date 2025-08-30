"""
ARCHIVE: archived filters helpers

Reference-only implementations of filter helpers. Kept under _archive for
historical reasons; they are intentionally lightweight and import-friendly so
they can be inspected without depending on the main package.
"""

from enum import Enum
from typing import List, Dict, Any
from datetime import datetime


class MediaType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"
    HD = "hd"
    HDVIDEO = "hdvideo"


class Species(str, Enum):
    DEER = "deer"
    BEAR = "bear"
    BIRD = "bird"


class TimeOfDay(str, Enum):
    DAY = "day"
    NIGHT = "night"
    DAWN = "dawn"
    DUSK = "dusk"


def make_photo_query(
    camera_ids: List[str] | None,
    *,
    from_dt: datetime | None,
    to_dt: datetime | None,
    filters: Dict[str, Any] | None,
    limit: int,
    cursor: str | None,
) -> Dict[str, Any]:
    query: Dict[str, Any] = {
        "limit": limit,
    }
    if camera_ids:
        query["camera"] = camera_ids
    if from_dt:
        query["dateStart"] = from_dt.isoformat()
    if to_dt:
        query["dateEnd"] = to_dt.isoformat()
    if filters:
        if "species" in filters:
            query["species"] = filters["species"]
        if "timeOfDay" in filters:
            query["timeOfDay"] = filters["timeOfDay"]
        if "mediaTypes" in filters:
            query["mediaTypes"] = filters["mediaTypes"]
        if "customTags" in filters:
            query["customTags"] = filters["customTags"]
    if cursor:
        query["cursor"] = cursor
    return query
