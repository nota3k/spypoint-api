from dataclasses import dataclass
from typing import List


@dataclass()
class CameraModel:
    name: str
    icon_url: str
    variants: List[str]

