from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypeAlias

Percentage: TypeAlias = float
Celsius: TypeAlias = int


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
    memory: Percentage | None = None

    @property
    def status(self) -> str:
        if datetime.now() - self.last_update_time <= timedelta(hours=24):
            return 'Online'
        else:
            return 'Offline'

    def __str__(self) -> str:
        return (f"Camera(id={self.id}, name={self.name}, model={self.model}, "
                f"modem_firmware={self.modem_firmware}, camera_firmware={self.camera_firmware}, "
                f"last_update_time={self.last_update_time}, signal={self.signal}, "
                f"temperature={self.temperature}, battery={self.battery}, memory={self.memory}, "
                f"status={self.status})")
