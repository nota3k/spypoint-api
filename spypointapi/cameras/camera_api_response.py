from datetime import datetime
from typing import Dict, Any, List

from spypointapi import Camera


class CameraApiResponse:

    @classmethod
    def from_json(cls, data: List[Dict[str, Any]]) -> List[Camera]:
        return [CameraApiResponse.camera_from_json(d) for d in data]

    @classmethod
    def camera_from_json(cls, data: Dict[str, Any]) -> Camera:
        config = data.get('config', {})
        status = data.get('status', {})
        return Camera(
            id=data['id'],
            name=config['name'],
            model=status['model'],
            modem_firmware=status['modemFirmware'],
            camera_firmware=status['version'],
            last_update_time=datetime.fromisoformat(status['lastUpdate'][:-1]).replace(tzinfo=datetime.now().astimezone().tzinfo),
            signal=status.get('signal', {}).get('processed', {}).get('percentage', None),
            temperature=CameraApiResponse.temperature_from_json(status.get('temperature', None)),
            battery=CameraApiResponse.battery_from_json(status.get('batteries', None)),
            battery_type=status.get('batteryType', None),
            memory=CameraApiResponse.memory_from_json(status.get('memory', None)),
            notifications=status.get('notifications', None),
        )

    @classmethod
    def temperature_from_json(cls, temperature: Dict[str, Any] | None) -> int | None:
        if not temperature:
            return None
        if temperature['unit'] == 'C':
            return temperature['value']
        return int((temperature['value'] - 32) * 5 / 9)

    @classmethod
    def battery_from_json(cls, batteries: Dict[str, Any] | None) -> str | None:
        if not batteries:
            return None
        return max(batteries)

    @classmethod
    def memory_from_json(cls, memory: Dict[str, Any] | None) -> float | None:
        if not memory:
            return None
        if memory.get('size', 0) == 0:
            return None
        return round(memory.get('used') / memory.get('size') * 100, 2)
