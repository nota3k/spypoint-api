"""
ARCHIVE: archived rate limiting helpers

Simple QPS limiter used during experimentation. Kept as reference; prefer the
production implementation in the main package.
"""

import asyncio
from contextlib import asynccontextmanager


class QPSLimiter:
    def __init__(self, qps: float):
        self._qps = qps
        self._interval = 1.0 / qps if qps > 0 else 0
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def acquire(self):
        async with self._lock:
            import time
            now = time.monotonic()
            wait = max(0.0, self._interval - (now - self._last))
            if wait > 0:
                await asyncio.sleep(wait)
            self._last = time.monotonic()


@asynccontextmanager
async def qps_guard(qps: float):
    limiter = QPSLimiter(qps)
    await limiter.acquire()
    try:
        yield
    finally:
        return
