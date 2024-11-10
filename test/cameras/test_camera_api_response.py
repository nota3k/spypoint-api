import unittest
from datetime import datetime

from spypointapi.cameras.camera_api_response import CameraApiResponse


class TestCameraApiResponse(unittest.TestCase):

    def test_parses_json(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "id": "id",
                "config": {
                    "name": "name",
                },
                "status": {
                    "model": "model",
                    "modemFirmware": "modemFirmware",
                    "version": "version",
                    "lastUpdate": "2024-10-30T02:03:48.716Z",
                    "signal": {
                        "processed": {
                            "percentage": 77,
                        }
                    },
                    "temperature": {
                        "unit": "C",
                        "value": 20,
                    },
                    "batteries": [0, 90, 0],
                    "batteryType": "12V",
                    "memory": {
                        "used": 100,
                        "size": 1000,
                    },
                    "notifications": [
                        "missing_sd_card"
                    ]
                },
            })

        self.assertEqual(camera.id, "id")
        self.assertEqual(camera.name, "name")
        self.assertEqual(camera.model, "model")
        self.assertEqual(camera.modem_firmware, "modemFirmware")
        self.assertEqual(camera.camera_firmware, "version")
        current_timezone = datetime.now().astimezone().tzinfo
        self.assertEqual(camera.last_update_time, datetime(2024, 10, 30, 2, 3, 48, 716000, current_timezone))
        self.assertEqual(camera.signal, 77)
        self.assertEqual(camera.temperature, 20)
        self.assertEqual(camera.battery, 90)
        self.assertEqual(camera.battery_type, "12V")
        self.assertEqual(camera.memory, 10)
        self.assertEqual(camera.notifications, ["missing_sd_card"])

    def test_parses_missing_fields(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "id": "id",
                "config": {
                    "name": "name",
                },
                "status": {
                    "model": "model",
                    "modemFirmware": "modemFirmware",
                    "version": "version",
                    "lastUpdate": "2024-10-30T02:03:48.716Z",
                }
            }
        )

        self.assertEqual(camera.signal, None)
        self.assertEqual(camera.temperature, None)
        self.assertEqual(camera.battery, None)
        self.assertEqual(camera.memory, None)

    def test_parses_missing_memory_size(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "id": "id",
                "config": {
                    "name": "name",
                },
                "status": {
                    "model": "model",
                    "modemFirmware": "modemFirmware",
                    "version": "version",
                    "lastUpdate": "2024-10-30T02:03:48.716Z",
                    "memory": {
                        "used": 0,
                        "size": 0,
                    }
                }
            }
        )

        self.assertEqual(camera.memory, None)

    def test_converts_f_temperature_to_c(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "id": "id",
                "config": {
                    "name": "name",
                },
                "status": {
                    "model": "model",
                    "modemFirmware": "modemFirmware",
                    "version": "version",
                    "lastUpdate": "2024-10-30T02:03:48.716Z",
                    "temperature": {
                        "unit": "F",
                        "value": 17,
                    },
                },
            }
        )

        self.assertEqual(camera.temperature, -8)
