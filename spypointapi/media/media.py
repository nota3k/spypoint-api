from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass()
class Media:
    id: str
    camera: str
    date: datetime
    large: str | None
    tags: List[str]
    previews: List[str] | None = None
    hd_video: str | None = None
    medium: str | None = None
    small: str | None = None
    origin_date: datetime | None = None
    origin_name: str | None = None
    origin_size: int | None = None
