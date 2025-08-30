"""Generated models re-export shim.

This shim prefers maintainer edits in `_generated_manual.py`. If a symbol is
not present there, it falls back to the auto-generated `_generated_auto.py`.
This keeps manual edits safe across regenerations.
"""

from importlib import import_module
from typing import Any


def _load_symbol(name: str) -> Any:
    # Try manual file first, then the auto-generated file.
    for module in ("._generated_manual", "._generated_auto"):
        try:
            m = import_module(module, __package__)
        except Exception:
            continue
        if hasattr(m, name):
            return getattr(m, name)
    raise ImportError(f"symbol {name} not found in manual or auto-generated modules")


# Re-export commonly used models
ApiV3PhotoAllPostRequest = _load_symbol("ApiV3PhotoAllPostRequest")
ApiV3PhotoAllPostResponse = _load_symbol("ApiV3PhotoAllPostResponse")
ApiV3CameraAllGetResponse = _load_symbol("ApiV3CameraAllGetResponse")
ApiV3CameraAllGetResponseItem = _load_symbol("ApiV3CameraAllGetResponseItem")

__all__ = [
    "ApiV3PhotoAllPostRequest",
    "ApiV3PhotoAllPostResponse",
    "ApiV3CameraAllGetResponse",
    "ApiV3CameraAllGetResponseItem",
]
