import aiohttp


class SpypointApiError(aiohttp.ClientResponseError):
    def __init__(self, error_response: aiohttp.ClientResponse):
        self.request_info = error_response.request_info
        self.history = error_response.history
        self.status = error_response.status
        # aiohttp may provide None for reason; ensure message is always a str
        self.message = error_response.reason or ""
        self.headers = error_response.headers


class SpypointApiInvalidCredentialsError(SpypointApiError):
    pass
