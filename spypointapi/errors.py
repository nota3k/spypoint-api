from typing import Any


class SpypointApiError(Exception):
    """Generic API error wrapper."""

    def __init__(self, status_code: int, message: str | None = None, payload: Any | None = None):
        self.status_code = status_code
        self.message = message or "spypoint api error"
        self.payload = payload
        super().__init__(f"{status_code}: {self.message}")


class SpypointApiInvalidCredentialsError(SpypointApiError):
    pass


class SpypointApiRateLimitError(SpypointApiError):
    pass


class SpypointApiServerError(SpypointApiError):
    pass
