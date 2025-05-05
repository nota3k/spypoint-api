from datetime import datetime
from typing import Dict, Any, List, Optional

from spypointapi import Camera
from spypointapi.cameras.camera import Coordinates, Plan, Subscription


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
            name=config.get('name', ''),
            model=status.get('model', ''),
            modem_firmware=status.get('modemFirmware', ''),
            camera_firmware=status.get('version', ''),
            last_update_time=datetime.fromisoformat(status['lastUpdate'][:-1]).replace(tzinfo=datetime.now().astimezone().tzinfo),
            signal=status.get('signal', {}).get('processed', {}).get('percentage', None),
            temperature=CameraApiResponse.temperature_from_json(status.get('temperature', None)),
            battery=CameraApiResponse.battery_from_json(status.get('batteries', None)),
            battery_type=status.get('batteryType', None),
            memory=CameraApiResponse.memory_from_json(status.get('memory', None)),
            memory_size=CameraApiResponse.memory_size_from_json(status.get('memory', None)),
            notifications=CameraApiResponse.notifications_from_json(status.get('notifications', None)),
            owner=CameraApiResponse.owner_from_json(data),
            coordinates=CameraApiResponse.coordinates_from_json(status.get('coordinates', None)),
            subscriptions=CameraApiResponse.subscriptions_from_json(data.get('subscriptions', [])),
            capture_mode=config.get('captureMode', None),
            motion_delay=config.get('motionDelay', None),
            multi_shot=config.get('multiShot', None),
            operation_mode=config.get('operationMode', None),
            quality=config.get('quality', None),
            sensibility=config.get('sensibility', None),
            time_format=config.get('timeFormat', None),
            time_lapse=config.get('timeLapse', None),
            transmit_auto=config.get('transmitAuto', None),
            transmit_freq=config.get('transmitFreq', None),
            transmit_time=config.get('transmitTime', None),
        )

    @classmethod
    def temperature_from_json(cls, temperature: Optional[Dict[str, Any]]) -> Optional[int]:
        if not temperature:
            return None
        if temperature['unit'] == 'C':
            return temperature['value']
        return int((temperature['value'] - 32) * 5 / 9)

    @classmethod
    def battery_from_json(cls, batteries: Optional[Dict[str, Any]]) -> Optional[str]:
        if not batteries:
            return None
        return max(batteries)

    @classmethod
    def memory_from_json(cls, memory: Optional[Dict[str, Any]]) -> Optional[float]:
        if not memory:
            return None
        if memory.get('size', 0) == 0:
            return None
        return round(memory.get('used') / memory.get('size') * 100, 2)

    @classmethod
    def memory_size_from_json(cls, memory: Optional[Dict[str, Any]]) -> Optional[int]:
        if not memory or 'size' not in memory:
            return None
        return memory.get('size')

    @classmethod
    def notifications_from_json(cls, notifications: Optional[Dict[str, Any]]) -> Optional[List[str]]:
        if notifications is None:
            return None
        return [str(notification) for notification in notifications]

    @classmethod
    def owner_from_json(cls, data):
        owner = data.get('ownerFirstName', None)
        if owner is None:
            return None
        return owner.strip()

    @classmethod
    def coordinates_from_json(cls, coordinates: Optional[List[Any]]) -> Optional[Coordinates]:
        if (coordinates is None
                or len(coordinates) < 1
                or coordinates[0].get('position', {}).get('type', '') != 'Point'
                or len(coordinates[0].get('position', {}).get('coordinates', [])) != 2):
            return None
        lat_lon = coordinates[0]['position']['coordinates']
        return Coordinates(latitude=lat_lon[1], longitude=lat_lon[0])

    @classmethod
    def subscriptions_from_json(cls, subscriptions: List[Dict[str, Any]]) -> List[Subscription]:
        return [
            Subscription(
                payment_frequency=sub.get('paymentFrequency', ''),
                is_free=sub.get('isFree', False),
                start_date_billing_cycle=datetime.fromisoformat(sub['startDateBillingCycle']),
                end_date_billing_cycle=datetime.fromisoformat(sub['endDateBillingCycle']),
                month_end_billing_cycle=datetime.fromisoformat(sub['monthEndBillingCycle']),
                photo_count=sub.get('photoCount', 0),
                hd_photo_count=sub.get('hdPhotoCount', 0),
                photo_limit=sub.get('photoLimit', 0),
                hd_photo_limit=sub.get('hdPhotoLimit', 0),
                is_auto_renew=sub.get('isAutoRenew', False),
                plan=CameraApiResponse.plan_from_json(sub.get('plan', {})),  # Add this line to parse the plan
            )
            for sub in subscriptions
        ]

    @classmethod
    def plan_from_json(cls, plan: Dict[str, Any]) -> Plan:
        return Plan(
            name=plan.get('name', ''),
            is_active=plan.get('isActive', False),
            is_free=plan.get('isFree', False),
            photo_count_per_month=plan.get('photoCountPerMonth', 0),
        )
