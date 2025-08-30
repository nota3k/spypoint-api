from datetime import datetime
from spypointapi.models.camera import Camera
from spypointapi.models.photo import PhotoItem
from spypointapi.models.camera import Camera as CameraModel


def test_camera_model():
    # Minimal test for the new Pydantic Camera model
    camera = Camera.model_validate({
        "id": "cam1",
        "name": "Test Cam",
        "model": "Model X",
        "firmware": "2.0.0",
    })
    assert camera.id == "cam1"


def test_photo_item_model():
    payload = {
        "id": "item1",
        "camera": "cam1",
        "date": "2023-10-01T10:00:00Z",
        "small": {"verb": "GET", "host": "h", "path": "/p", "headers": []},
        "medium": {"verb": "GET", "host": "h", "path": "/p", "headers": []},
        "large": {"verb": "GET", "host": "h", "path": "/p", "headers": []},
    }
    item = PhotoItem.model_validate(payload)
    assert item.id == "item1"
