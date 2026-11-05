import os
import time
import itertools
from threading import Lock


class GeminiKeySharder:
    """Round-robin API key rotator with automatic 60s cooldown on 429 rate limits."""

    def __init__(self) -> None:
        raw_keys = os.getenv("GEMINI_API_KEYS", "")
        self.keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        if not self.keys:
            raise ValueError("No keys found in GEMINI_API_KEYS environment variable.")
        self._cycle = itertools.cycle(range(len(self.keys)))
        self._cooldown_until: dict[int, float] = {}
        self._lock = Lock()

    def get_key(self) -> tuple[int, str]:
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
