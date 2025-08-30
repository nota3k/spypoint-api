import unittest
from datetime import datetime, timedelta

from spypointapi.models.camera import Camera


class CameraTest(unittest.TestCase):

    def test_camera_fields_present(self):
        payload = {"id": "id", "name": "name", "model": "model"}
        camera = Camera.model_validate(payload)
        self.assertEqual(camera.id, "id")
        self.assertEqual(camera.name, "name")
