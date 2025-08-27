from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass()
class Media:
    id: str
    camera: str
    date: datetime
    large: str
    tags: List[str]
    previews: List[str] | None = None
    hd_video: str | None = None
