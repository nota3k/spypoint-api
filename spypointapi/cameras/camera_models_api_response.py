from typing import Any, Dict, List

from .camera_model import CameraModel


class CameraModelsApiResponse:

    @classmethod
    def from_json(cls, data: List[Dict[str, Any]]) -> List[CameraModel]:
        return [cls.camera_model_from_json(d) for d in data]

    @classmethod
    def camera_model_from_json(cls, data: Dict[str, Any]) -> CameraModel:
        return CameraModel(
            name=data["name"],
            icon_url=data["iconUrl"],
            variants=data.get("variants", []),
        )

