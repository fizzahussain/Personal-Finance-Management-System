from copy import deepcopy
from threading import Lock
from time import monotonic
from typing import Any


class TtlCache:
    """Store values for a limited time"""

    def __init__(
        self,
        ttl_seconds: float = 30.0,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self._values: dict[
            tuple[object, ...],
            tuple[float, Any],
        ] = {}
        self._lock = Lock()

    def get(
        self,
        key: tuple[object, ...],
    ) -> Any | None:
        """Return a cached value when it is valid"""
        with self._lock:
            cached = self._values.get(key)

            if cached is None:
                return None

            expires_at, value = cached

            if monotonic() >= expires_at:
                self._values.pop(key, None)
                return None

            return deepcopy(value)

    def set(
        self,
        key: tuple[object, ...],
        value: Any,
    ) -> None:
        """Store a value in the cache"""
        with self._lock:
            self._values[key] = (
                monotonic() + self.ttl_seconds,
                deepcopy(value),
            )

    def delete_prefix(
        self,
        prefix: tuple[object, ...],
    ) -> None:
        """Delete keys beginning with a prefix"""
        with self._lock:
            matching_keys = [
                key
                for key in self._values
                if key[: len(prefix)] == prefix
            ]

            for key in matching_keys:
                self._values.pop(key, None)

    def clear(self) -> None:
        """Delete every cached value"""
        with self._lock:
            self._values.clear()


application_cache = TtlCache()