from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, ConfigDict


class PhotoAllRequest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    camera: list[str]
    dateEnd: datetime
    limit: int = 100
    mediaTypes: list[Any] = []
    species: list[Any] = []
    timeOfDay: list[Any] = []
    customTags: list[Any] = []


class HeaderKV(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    name: str
    value: str


class SignedGet(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    verb: Literal["GET"]
    host: str
    path: str
    headers: list[HeaderKV]


class PhotoItem(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    id: str
    camera: str
    date: datetime
    originDate: datetime | None = None
    originName: str | None = None
    originSize: int | None = None
    small: SignedGet
    medium: SignedGet
    large: SignedGet
    preview: list[Any] = []
    tag: list[str] = []
    hdUploaded: bool | None = None
    hd: SignedGet | None = None
    raw_json: dict[str, Any] = Field(default_factory=dict, exclude=True)


class PhotoAllResponse(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    cameraId: str | None = None
    cameraIds: list[str] = []
    countPhotos: int = 0
    photos: list[PhotoItem] = []
    raw_json: dict[str, Any] = Field(default_factory=dict, exclude=True)
