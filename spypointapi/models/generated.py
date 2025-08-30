"""Generated models re-export shim (moved from spypointapi/generated_models.py).

This file intentionally re-exports symbols from the generated models module.
It allows us to keep generated code colocated while keeping a stable import surface.
"""

from ._generated_impl import (
    ApiV3PhotoAllPostRequest,
    ApiV3PhotoAllPostResponse,
    ApiV3CameraAllGetResponse,
    ApiV3CameraAllGetResponseItem,
)

__all__ = [
    "ApiV3PhotoAllPostRequest",
    "ApiV3PhotoAllPostResponse",
    "ApiV3CameraAllGetResponse",
    "ApiV3CameraAllGetResponseItem",
]
"""Generated models from OpenAPI spec. Do not edit manually.
"""

from .. import generated_models as _gm

# re-export commonly used models
ApiV3PhotoAllPostRequest = _gm.ApiV3PhotoAllPostRequest
ApiV3PhotoAllPostResponse = _gm.ApiV3PhotoAllPostResponse
ApiV3CameraAllGetResponse = _gm.ApiV3CameraAllGetResponse
ApiV3CameraAllGetResponseItem = _gm.ApiV3CameraAllGetResponseItem

__all__ = [
    "ApiV3PhotoAllPostRequest",
    "ApiV3PhotoAllPostResponse",
    "ApiV3CameraAllGetResponse",
    "ApiV3CameraAllGetResponseItem",
]
