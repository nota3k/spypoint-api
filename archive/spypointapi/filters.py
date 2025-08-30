"""
Archived: spypointapi.filters

Retained for reference during cleanup. Do not import from archive in production code.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class Filters(BaseModel):
    model_config = ConfigDict(extra="allow")
    species: List[str]


class Notifications(BaseModel):
    model_config = ConfigDict(extra="allow")
    species: List[str]
