import os
import time
import itertools
from threading import Lock
from typing import List, Optional, Tuple


class GeminiKeySharder:
    """Round-robin API key rotator with automatic 60s cooldown on 429 rate limits."""

    def __init__(self, keys: Optional[List[str]] = None) -> None:
        if keys is not None:
            self.keys = [k.strip() for k in keys if k.strip()]
        else:
            raw_keys = os.getenv("GEMINI_API_KEYS", "")
            self.keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        if not self.keys:
            raise ValueError("No keys found in GEMINI_API_KEYS environment variable.")
        self._cycle = itertools.cycle(range(len(self.keys)))
        self._cooldown_until: dict[int, float] = {}
        self._lock = Lock()

    def get_key(self) -> Tuple[int, str]:
        with self._lock:
            now = time.monotonic()
            for _ in range(len(self.keys)):
                idx = next(self._cycle)
                if self._cooldown_until.get(idx, 0.0) <= now:
                    return idx, self.keys[idx]
            # If all keys are cooling down, pick the one whose cooldown expires soonest
            soonest_idx = min(self._cooldown_until, key=self._cooldown_until.get)
            return soonest_idx, self.keys[soonest_idx]

    def mark_rate_limited(self, key_index: int, cooldown_seconds: float = 60.0) -> None:
        with self._lock:
            self._cooldown_until[key_index] = time.monotonic() + cooldown_seconds


_global_sharder: Optional[GeminiKeySharder] = None
_sharder_init_lock = Lock()


def get_sharder() -> GeminiKeySharder:
    """Returns the singleton instance of GeminiKeySharder, initializing on demand."""
    global _global_sharder
    if _global_sharder is None:
        with _sharder_init_lock:
            if _global_sharder is None:
                _global_sharder = GeminiKeySharder()
    return _global_sharder


def get_sharded_gemini_key() -> Tuple[int, str]:
    """
    Returns (key_index, api_key) from the round-robin Gemini key pool.
    If GEMINI_API_KEYS is unset (e.g. during contract unit tests), returns a safe dev placeholder.
    """
    try:
        sharder = get_sharder()
        return sharder.get_key()
    except ValueError:
        return 0, "dev_gemini_key_placeholder"

