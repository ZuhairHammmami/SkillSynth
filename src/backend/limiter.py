import os
import time
import threading
from collections import defaultdict
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

MODE = os.getenv("MODE", "dev")


class InMemoryRateStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._buckets: dict[str, dict[str, list[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

    def get(self, key: str) -> int | None:
        return None

    def set(self, key: str, value: int, ttl: int = 60) -> None:
        pass

    def increment(self, key: str, expiry: int = 60) -> int:
        now = time.time()
        with self._lock:
            self._buckets[key][now] = 1
            cutoff = now - expiry
            for ts in list(self._buckets[key]):
                if ts < cutoff:
                    del self._buckets[key][ts]
            return sum(self._buckets[key].values())


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=os.getenv("REDIS_URL") if MODE == "prod" else None,
)

auth_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10/minute"],
    storage_uri=os.getenv("REDIS_URL") if MODE == "prod" else None,
)

admin_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    storage_uri=os.getenv("REDIS_URL") if MODE == "prod" else None,
)

DEFAULT_RATE_LIMIT = "100/minute"
AUTH_RATE_LIMIT = "10/minute"
ADMIN_RATE_LIMIT = "60/minute"
