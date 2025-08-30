from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class Camera(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    id: str | None = None
    name: str | None = None
    raw_json: dict[str, Any] = Field(default_factory=dict, exclude=True)
