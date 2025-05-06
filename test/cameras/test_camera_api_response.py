import unittest
from datetime import datetime, timezone
from typing import Optional

from spypointapi.cameras.camera import Coordinates
from spypointapi.cameras.camera_api_response import CameraApiResponse


class TestCameraApiResponse(unittest.TestCase):

    def test_parses_json(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "id": "id",
                "creationDate": "2023-01-01T12:00:00.000Z",
                "installDate": "2023-01-02T12:00:00.000Z",
                "config": {"name": "name"},
                "status": {
                    "model": "model",
                    "lastUpdate": "2024-10-30T02:03:48.716Z",
                    "temperature": {"value": 20, "unit": "C"},
                },
            }
        )
        self.assertEqual(
            camera.last_update_time,
            datetime(2024, 10, 30, 2, 3, 48, 716000, tzinfo=timezone.utc),
        )
        self.assertEqual(
            camera.creation_date,
            datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            camera.install_date,
            datetime(2023, 1, 2, 12, 0, 0, tzinfo=timezone.utc),
        )

    def test_parses_missing_fields(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "id": "id",
                "config": {
                    "name": "name",
                },
                "status": {
                    "model": "model",
                    "lastUpdate": "2024-10-30T02:03:48.716Z",
                }
            }
        )

        self.assertEqual(camera.signal, None)
        self.assertEqual(camera.temperature, None)
        self.assertEqual(camera.battery, None)
        self.assertEqual(camera.memory, None)
        self.assertEqual(camera.modem_firmware, '')
        self.assertEqual(camera.camera_firmware, '')

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

    def test_parses_notification_objects(self):
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
                    "notifications": [
                        "low_battery",
                        {"survivalModeStart": "2024-12-14T12:00:30.000-00:00"},
                        {"survivalModeEnd": "2024-12-15T08:00:58.000-00:00"}
                    ]
                }
            }
        )

        self.assertEqual(camera.notifications, ["low_battery", "{'survivalModeStart': '2024-12-14T12:00:30.000-00:00'}",
                                                "{'survivalModeEnd': '2024-12-15T08:00:58.000-00:00'}"])

    def test_parses_owner_field(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "ownerFirstName": "Philippe ",
                "id": "id",
                "config": {
                    "name": "name",
                },
                "status": {
                    "model": "model",
                    "lastUpdate": "2024-10-30T02:03:48.716Z",
                }
            }
        )

        self.assertEqual(camera.owner, "Philippe")

    def test_parses_point_coordinates(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "id": "id",
                "config": {
                    "name": "name",
                },
                "status": {
                    "model": "model",
                    "lastUpdate": "2024-10-30T02:03:48.716Z",
                    "coordinates": [{"position": {"type": "Point", "coordinates": [-70.1234, 45.123456]}}],
                }
            }
        )

        self.assertEqual(camera.coordinates, Coordinates(latitude=45.123456, longitude=-70.1234))

    def test_ignores_empty_point_coordinates(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "id": "id",
                "config": {
                    "name": "name",
                },
                "status": {
                    "model": "model",
                    "lastUpdate": "2024-10-30T02:03:48.716Z",
                    "coordinates": [{"position": {"type": "Point", "coordinates": []}}],
                }
            }
        )

        self.assertEqual(camera.coordinates, None)

    def test_ignores_other_coordinates_type(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "id": "id",
                "config": {
                    "name": "name",
                },
                "status": {
                    "model": "model",
                    "lastUpdate": "2024-10-30T02:03:48.716Z",
                    "coordinates": [{"position": {"type": "other"}}],
                }
            }
        )

        self.assertEqual(camera.coordinates, None)

    def test_parses_temperature_with_unit(self):
        camera = CameraApiResponse.camera_from_json(
            {
                "id": "id",
                "config": {"name": "name"},
                "status": {
                    "temperature": {"value": 68, "unit": "F"}
                },
            }
        )
        self.assertEqual(camera.temperature, {"value": 68, "unit": "F"})

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        """Parses an ISO 8601 datetime string."""
        if not value:
            return None
        try:
            # Parse the datetime directly, which handles offsets like -05:00
            return datetime.fromisoformat(value)
        except ValueError:
            # Log the error or handle it gracefully
            print(f"Invalid ISO 8601 datetime string: {value}")
            return None
