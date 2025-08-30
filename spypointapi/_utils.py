"""Utility helpers for model handling."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class RawPayload:
    """A tiny container to carry raw payloads for non-model responses."""

    def __init__(self, payload: object) -> None:
        self.payload = payload
        self.__raw_json__ = payload


def attach_raw_json_to_model(instance: Any, raw: Any) -> Any:
    """Attach raw JSON payload to a parsed model instance.

    - For BaseModel instances, set `.raw_json` if present.
    - For RootModel instances (or other values), set a private attribute `__raw_json__`.
    """
    try:
        if isinstance(instance, BaseModel):
            # many generated models include a raw_json field; set it when available
            if hasattr(instance, "raw_json"):
                try:
                    setattr(instance, "raw_json", raw)
                except Exception:
                    # best-effort; don't fail the parsing flow
                    pass
            else:
                try:
                    setattr(instance, "__raw_json__", raw)
                except Exception:
                    pass
        elif isinstance(instance, dict):
            # store raw on dict responses under a non-conflicting key
            try:
                instance["__raw_json__"] = raw
            except Exception:
                pass
        else:
            # try to set attribute if object supports it
            try:
                setattr(instance, "__raw_json__", raw)
            except Exception:
                pass
    except Exception:
        # defensive: never raise from this helper
        pass

    return instance
