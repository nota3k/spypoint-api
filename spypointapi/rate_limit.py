import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import time


class QPSLimiter:
    def __init__(self, qps: float):
        self.qps = qps
        self.interval = 1.0 / qps
        self.last_call = 0.0

    async def __aenter__(self):
        now = time.monotonic()
        elapsed = now - self.last_call
        if elapsed < self.interval:
            await asyncio.sleep(self.interval - elapsed)
        self.last_call = time.monotonic()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@asynccontextmanager
async def qps_guard(qps: float) -> AsyncGenerator[QPSLimiter, None]:
    limiter = QPSLimiter(qps)
    async with limiter:
        yield limiter
