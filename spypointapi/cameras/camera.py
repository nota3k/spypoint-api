from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypeAlias, List, Dict, Any

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
    photo_count_per_month: int


@dataclass()
class Subscription:
    payment_frequency: str
    is_free: bool
    start_date_billing_cycle: datetime
    end_date_billing_cycle: datetime
    month_end_billing_cycle: datetime
    photo_count: int
    hd_photo_count: int
    photo_limit: int
    hd_photo_limit: int
    is_auto_renew: bool
    plan: Plan | None = None  # Add this line to include the plan details


@dataclass()
class Camera:
    id: str
    name: str
    model: str
    modem_firmware: str
    camera_firmware: str
    last_update_time: datetime
    signal: Percentage | None = None
    temperature: Celsius | None = None
    battery: Percentage | None = None
    battery_type: str | None = None
    memory: Percentage | None = None
    memory_size: int | None = None
    notifications: List[str] | None = None
    owner: str | None = None
    coordinates: Coordinates | None = None
    subscriptions: List[Subscription] | None = None
    capture_mode: str | None = None
    motion_delay: int | None = None
    multi_shot: int | None = None
    operation_mode: str | None = None
    quality: str | None = None
    sensibility: Dict[str, Any] | None = None
    time_format: int | None = None
    time_lapse: int | None = None
    transmit_auto: bool | None = None
    transmit_freq: int | None = None
    transmit_time: Dict[str, int] | None = None  # Add these fields

    @property
    def is_online(self) -> bool:
        now = datetime.now().astimezone()
        diff = now - self.last_update_time
        return diff <= timedelta(hours=24)

    def __str__(self) -> str:
        return (f"Camera(id={self.id}, name={self.name}, model={self.model}, "
                f"modem_firmware={self.modem_firmware}, camera_firmware={self.camera_firmware}, "
                f"last_update_time={self.last_update_time}, signal={self.signal}, "
                f"temperature={self.temperature}, battery={self.battery}, battery_type={self.battery_type}, "
                f"memory={self.memory}, memory_size={self.memory_size}, "
                f"capture_mode={self.capture_mode}, motion_delay={self.motion_delay}, "
                f"multi_shot={self.multi_shot}, operation_mode={self.operation_mode}, "
                f"quality={self.quality}, sensibility={self.sensibility}, "
                f"time_format={self.time_format}, time_lapse={self.time_lapse}, "
                f"transmit_auto={self.transmit_auto}, transmit_freq={self.transmit_freq}, "
                f"transmit_time={self.transmit_time}, "
                f"subscriptions={self.subscriptions}, "
                f"notifications={self.notifications}, online={self.is_online}), "
                f"owner={self.owner}, coordinates={self.coordinates})")
