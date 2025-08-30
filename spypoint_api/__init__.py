"""Compatibility shim package for spypoint-api (new canonical package name).

This module re-exports the primary public API from the legacy `spypointapi` package
so consumers can import from `spypoint_api` while we migrate the codebase.

Keep this file minimal: it exposes `SpypointApi` and `__version__`.
"""
from importlib import metadata as _metadata
from typing import TYPE_CHECKING

try:
    # prefer the new local _version if installed as a package
    from ._version import __version__  # type: ignore
except Exception:  # pragma: no cover - fallback when used from source
    __version__ = "0.1.0"

from spypointapi.client import SpypointApi  # re-export the existing implementation

__all__ = ["SpypointApi", "__version__"]
