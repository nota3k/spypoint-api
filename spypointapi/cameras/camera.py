from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypeAlias, List, Dict, Any, Optional, Union

Percentage: TypeAlias = float
Celsius: TypeAlias = int
Degrees: TypeAlias = float


@dataclass()
class Coordinates:
    latitude: Degrees
    longitude: Degrees


@dataclass()
class Plan:
    name: str
    is_active: bool
    is_free: bool
    photo_count_per_month: Union[int, str]  # Updated type hint


@dataclass()
class Subscription:
    payment_frequency: str = ""
    is_free: bool = False
    start_date_billing_cycle: Optional[datetime] = None
    end_date_billing_cycle: Optional[datetime] = None
    month_end_billing_cycle: Optional[datetime] = None
    photo_count: int = 0
    hd_photo_count: int = 0
    photo_limit: int = 0
    hd_photo_limit: int = 0
    is_auto_renew: bool = False
    plan: Optional[Plan] = None

@dataclass
class Camera:
    id: str
    name: str
    model: str
    modem_firmware: str
    camera_firmware: str
    last_update_time: Optional[datetime]
    activation_date: Optional[datetime]
    creation_date: Optional[datetime]  
    install_date: Optional[datetime]  
    signal: Optional[float]
    temperature: Optional[Dict[str, Any]]  # Supports {"value": int, "unit": str}
    battery: Optional[int]
    battery_type: Optional[str]
    memory: Optional[float]
    memory_size: Optional[int]
    notifications: Optional[List[str]]
    owner: Optional[str]
    coordinates: Optional[Coordinates]  # Changed from Dict[str, float]
    subscriptions: Optional[List[Subscription]]  # Updated to ensure type safety
    capture_mode: Optional[str]
    motion_delay: Optional[str]
    # delay: Optional[int]
    multi_shot: Optional[int]
    operation_mode: Optional[str]
    quality: Optional[str]
    sensibility: Optional[Dict[str, Any]] # Changed from Optional[str]
    time_format: Optional[int]
    time_lapse: Optional[int]
    transmit_auto: Optional[bool]
    transmit_freq: Optional[int]
    transmit_time: Optional[str]

    @property
    def is_online(self) -> bool:
        now = datetime.now().astimezone()
        diff = now - self.last_update_time
        return diff <= timedelta(hours=24)

    def __str__(self) -> str:
        return f"Camera({self._format_attributes()})"

    def _format_attributes(self) -> str:
        attributes = [
            f"id={self.id}",
            f"name={self.name}",
            f"model={self.model}",
            f"modem_firmware={self.modem_firmware}",
            f"camera_firmware={self.camera_firmware}",
            f"last_update_time={self.last_update_time}",
            f"signal={self.signal}",
            f"temperature={self.temperature}",
            f"battery={self.battery}",
            f"battery_type={self.battery_type}",
            f"memory={self.memory}",
            f"memory_size={self.memory_size}",
            f"capture_mode={self.capture_mode}",
            f"motion_delay={self.motion_delay}",
            f"delay={self.delay}",
            f"multi_shot={self.multi_shot}",
            f"operation_mode={self.operation_mode}",
            f"quality={self.quality}",
            f"sensibility={self.sensibility}",
            f"time_format={self.time_format}",
            f"time_lapse={self.time_lapse}",
            f"transmit_auto={self.transmit_auto}",
            f"transmit_freq={self.transmit_freq}",
            f"transmit_time={self.transmit_time}",
            f"subscriptions={self.subscriptions}",
            f"notifications={self.notifications}",
            f"online={self.is_online}",
            f"owner={self.owner}",
            f"coordinates={self.coordinates}",
        ]
        return ", ".join(attributes)