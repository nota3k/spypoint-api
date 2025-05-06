import unittest
from datetime import datetime, timedelta
from spypointapi.cameras.camera import Camera


class CameraTest(unittest.TestCase):

    def test_is_offline_when_last_status_is_past_24_hours(self):
        camera = Camera(
            id="id",
            name="name",
            model="model",
            modem_firmware="modem_firmware",
            camera_firmware="camera_firmware",
            last_update_time=datetime.now().astimezone() - timedelta(hours=24, minutes=0, seconds=1),
            activation_date=None,
            creation_date=None,  # Add this
            install_date=None,  # Add this
            signal=100,
            temperature={"value": 20, "unit": "C"},
            battery=200,
            battery_type=None,
            memory=100,
            memory_size=None,
            notifications=None,
            owner=None,
            coordinates=None,
            subscriptions=None,
            capture_mode=None,
            motion_delay=None,
            multi_shot=None,
            operation_mode=None,
            quality=None,
            sensibility=None,
            time_format=None,
            time_lapse=None,
            transmit_auto=None,
            transmit_freq=None,
            transmit_time=None,
        )
        self.assertTrue(camera.last_update_time < datetime.now().astimezone() - timedelta(hours=24))

    def test_is_online_when_last_status_is_within_24_hours(self):
        camera = Camera(
            id="id",
            name="name",
            model="model",
            modem_firmware="modem_firmware",
            camera_firmware="camera_firmware",
            last_update_time=datetime.now().astimezone() - timedelta(hours=23, minutes=59, seconds=59),
            activation_date=None,
            creation_date=None,  # Add this
            install_date=None,  # Add this
            signal=100,
            temperature={"value": 20, "unit": "C"},
            battery=200,
            battery_type=None,
            memory=100,
            memory_size=None,
            notifications=None,
            owner=None,
            coordinates=None,
            subscriptions=None,
            capture_mode=None,
            motion_delay=None,
            multi_shot=None,
            operation_mode=None,
            quality=None,
            sensibility=None,
            time_format=None,
            time_lapse=None,
            transmit_auto=None,
            transmit_freq=None,
            transmit_time=None,
        )
        self.assertTrue(camera.last_update_time >= datetime.now().astimezone() - timedelta(hours=24))