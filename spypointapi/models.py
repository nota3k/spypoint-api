from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class CameraPlan:
    name: str
    is_free: bool = False
    photo_limit: Optional[int] = None
    photo_count: Optional[int] = None


@dataclass
class Camera:
    id: str
    name: str
    model: str
    firmware: str
    battery_percent: Optional[float] = None
    signal_percent: Optional[float] = None
    plan: Optional[CameraPlan] = None
    last_update: datetime = field(default_factory=datetime.now)
    raw_status: Optional[Dict[str, Any]] = None
    raw_config: Optional[Dict[str, Any]] = None


@dataclass
class MediaUrl:
    url: str
    content_type: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class MediaItem:
    id: str
    camera_id: str
    date: datetime
    origin_name: str
    is_video: bool
    tags: List[str]
    variants: Dict[str, MediaUrl]
    expires_at: Optional[datetime] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_ms: Optional[int] = None
