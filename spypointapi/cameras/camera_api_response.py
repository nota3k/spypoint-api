from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union

from spypointapi import Camera
from spypointapi.cameras.camera import Coordinates, Plan, Subscription


class CameraApiResponse:
    """Handles parsing of camera-related API responses."""

    @classmethod
    def from_json(cls, data: List[Dict[str, Any]]) -> List[Camera]:
        """Parses a list of cameras from JSON."""
        return [cls.camera_from_json(d) for d in data]

    @classmethod
    def camera_from_json(cls, data: Dict[str, Any]) -> Camera:
        """Parses a single camera from JSON."""
        config = data.get("config", {})
        status = data.get("status", {})

        return Camera(
            id=data["id"],
            name=cls._parse_config_field(config, "name", default=""),
            model=cls._parse_status_field(status, "model", default=""),
            modem_firmware=cls._parse_status_field(status, "modemFirmware", default=""),
            camera_firmware=cls._parse_status_field(status, "version", default=""),
            last_update_time=cls._parse_datetime(cls._parse_status_field(status, "lastUpdate")),
            activation_date=cls._parse_datetime(data.get("activationDate")), # Get from top-level data & parse
            creation_date=cls._parse_datetime(data.get("creationDate")),   # Get from top-level data & parse
            install_date=cls._parse_datetime(data.get("installDate")), # Get from top-level data & parse
            signal=cls._parse_signal(status),
            temperature=cls.temperature_from_json(status.get("temperature")),
            battery=cls.battery_from_json(status.get("batteries")),
            battery_type=cls._parse_status_field(status, "batteryType"),
            memory=cls.memory_from_json(status.get("memory")),
            memory_size=cls.memory_size_from_json(status.get("memory")),
            notifications=cls.notifications_from_json(status.get("notifications")),
            owner=cls.owner_from_json(data),
            coordinates=cls.coordinates_from_json(status.get("coordinates")),
            subscriptions=cls.subscriptions_from_json(data.get("subscriptions", [])),  
            capture_mode=cls._parse_config_field(config, "captureMode"),
            # delay=cls._parse_config_field(config, "delay"),
            motion_delay=cls._parse_config_field(config, "motionDelay"),
            multi_shot=cls._parse_config_field(config, "multiShot"),
            operation_mode=cls._parse_config_field(config, "operationMode"),
            quality=cls._parse_config_field(config, "quality"),
            sensibility=cls._parse_config_field(config, "sensibility"),
            time_format=cls._parse_config_field(config, "timeFormat"),
            time_lapse=cls._parse_config_field(config, "timeLapse"),
            transmit_auto=cls._parse_config_field(config, "transmitAuto"),
            transmit_freq=cls._parse_config_field(config, "transmitFreq"),
            transmit_time=cls._parse_transmit_time(config.get("transmitTime")),  
        )

    @staticmethod
    def _parse_config_field(config: Dict[str, Any], field: str, default: Any = None) -> Any:
        """Safely parses a field from the config dictionary."""
        return config.get(field, default)

    @staticmethod
    def _parse_status_field(status: Dict[str, Any], field: str, default: Any = None) -> Any:
        """Safely parses a field from the status dictionary."""
        return status.get(field, default)

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        """Parses an ISO 8601 datetime string."""
        if not value:
            return None
        try:
            # Handles "Z" suffix by stripping it before parsing
            # and then making it timezone-aware (UTC)
            if value.endswith("Z"):
                return datetime.fromisoformat(value[:-1]).replace(tzinfo=timezone.utc)
            return datetime.fromisoformat(value).replace(tzinfo=timezone.utc) # Assuming UTC if no Z
        except (ValueError, TypeError):
            # Consider logging this error if it's important to know about malformed dates
            # print(f"Invalid ISO 8601 datetime string: {value}") 
            return None

    @staticmethod
    def _parse_signal(status: Dict[str, Any]) -> Optional[float]:
        """Parses the signal strength from the status dictionary."""
        return status.get("signal", {}).get("processed", {}).get("percentage")

    @classmethod
    def temperature_from_json(cls, temperature: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Parses the temperature field and supports both Fahrenheit (F) and Celsius (C).

        :param temperature: A dictionary containing temperature data.
        :return: A dictionary with the temperature value and its unit, or None if not available.
        """
        if not temperature:
            return None
        return {
            "value": temperature.get("value"),
            "unit": temperature.get("unit", "C")  # Default to Celsius if the unit is missing
        }

    @classmethod
    def battery_from_json(cls, batteries: Optional[List[int]]) -> Optional[int]:
        """Parses the battery field."""
        if not batteries:
            return None
        return max(batteries)

    @classmethod
    def memory_from_json(cls, memory: Optional[Dict[str, Any]]) -> Optional[float]:
        """Parses the memory usage as a percentage."""
        if not memory or memory.get("size", 0) == 0:
            return None
        return round(memory.get("used", 0) / memory["size"] * 100, 2)

    @classmethod
    def memory_size_from_json(cls, memory: Optional[Dict[str, Any]]) -> Optional[int]:
        """Parses the memory size."""
        return memory.get("size") if memory else None

    @classmethod
    def notifications_from_json(cls, notifications: Optional[List[Any]]) -> Optional[List[str]]:
        """Parses the notifications field."""
        if not notifications:
            return None
        return [str(notification) for notification in notifications]

    @classmethod
    def owner_from_json(cls, data: Dict[str, Any]) -> Optional[str]:
        """Parses the owner field."""
        owner = data.get("ownerName")
        return owner.strip() if owner else None

    @classmethod
    def coordinates_from_json(cls, coordinates: Optional[List[Dict[str, Any]]]) -> Optional[Coordinates]:
        """Parses the coordinates field."""
        if not coordinates or len(coordinates) < 1:
            return None
        position = coordinates[0].get("position", {})
        if position.get("type") != "Point":
            return None
        lat_lon = position.get("coordinates", [])
        if len(lat_lon) != 2:
            return None
        return Coordinates(latitude=lat_lon[1], longitude=lat_lon[0])

    @classmethod
    def subscriptions_from_json(cls, subscriptions: List[Dict[str, Any]]) -> List[Subscription]:
        """Parses the subscriptions field."""
        result = []
        for sub in subscriptions:
            plan_data = sub.get("plan")
            parsed_plan = cls.plan_from_json(plan_data) if plan_data else None

            subscription_item = Subscription(
                # Plan related
                plan=parsed_plan,
                # Photo counts and limits
                photo_count=sub.get("photoCount", 0),
                photo_limit=sub.get("photoLimit", 0),
                hd_photo_count=sub.get("hdPhotoCount", 0),
                hd_photo_limit=sub.get("hdPhotoLimit", 0),
                # Billing cycle dates
                start_date_billing_cycle=cls._parse_datetime(sub.get("startDateBillingCycle")),
                end_date_billing_cycle=cls._parse_datetime(sub.get("endDateBillingCycle")),
                month_end_billing_cycle=cls._parse_datetime(sub.get("monthEndBillingCycle")),
                # Payment and renewal
                payment_frequency=sub.get("paymentFrequency", ""),
                is_auto_renew=sub.get("isAutoRenew", False),
                is_free=sub.get("isFree", False),
            )
            result.append(subscription_item)
        return result

    @classmethod
    def plan_from_json(cls, plan: Dict[str, Any]) -> Plan:
        """Parses the plan field."""
        photo_count = plan.get("photoCountPerMonth", 0)
        return Plan(
            name=plan.get("name", ""),
            is_active=plan.get("isActive", False),
            is_free=plan.get("isFree", False),
            photo_count_per_month="Unlimited" if photo_count == 0 else photo_count,
        )

    @staticmethod
    def _parse_transmit_time(transmit_time: Optional[Dict[str, int]]) -> Optional[str]:
        """Parses the transmit_time field and formats it as military time (e.g., '18:30')."""
        if not transmit_time:
            return None
        hour = transmit_time.get("hour", 0)
        minute = transmit_time.get("minute", 0)
        return f"{hour:02}:{minute:02}"  # Formats as 'HH:MM'
