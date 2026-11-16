"""
security.py — Security Utilities and Rate Limiting for BengaluruTrafficAI Backend.

Implements an in-memory sliding window rate limiter and strict payload
sanitization helpers to protect junction telemetry and control endpoints.
"""

from collections import defaultdict, deque
import re
import time
from typing import Any, Dict, Optional, Tuple


class SlidingWindowRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter per client identifier (IP).
    """

    def __init__(self, max_requests: int = 120, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clients: Dict[str, deque] = defaultdict(deque)

    def is_allowed(self, client_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if client_id is within allowed threshold.

        Returns:
            Tuple[bool, dict]: (is_permitted, status_dict)
        """
        now = time.time()
        window_start = now - self.window_seconds
        queue = self._clients[client_id]

        # Evict timestamps outside the sliding window
        while queue and queue[0] <= window_start:
            queue.popleft()

        current_count = len(queue)
        if current_count < self.max_requests:
            queue.append(now)
            return True, {
                "allowed": True,
                "current_count": current_count + 1,
                "limit": self.max_requests,
                "window_seconds": self.window_seconds,
                "remaining": self.max_requests - (current_count + 1),
            }

        return False, {
            "allowed": False,
            "current_count": current_count,
            "limit": self.max_requests,
            "window_seconds": self.window_seconds,
            "remaining": 0,
            "retry_after_seconds": max(1, int(queue[0] + self.window_seconds - now)),
        }

    def reset(self) -> None:
        """Reset rate limiter tracking buckets."""
        self._clients.clear()


# Default rate limiter: 120 requests per minute
global_rate_limiter = SlidingWindowRateLimiter(max_requests=120, window_seconds=60)


def sanitize_text(value: Any, max_length: int = 64, default: str = "") -> str:
    """
    Sanitize text input by removing control characters and restricting length.
    Allows alphanumeric characters, underscores, hyphens, and spaces.
    """
    if value is None:
        return default
    text = str(value).strip()
    # Strip dangerous HTML/script characters
    sanitized = re.sub(r"[^\w\s\-_.]", "", text)
    return sanitized[:max_length] if sanitized else default


def sanitize_integer(value: Any, min_val: int = 0, max_val: int = 10000, default: int = 0) -> int:
    """
    Cast and bound an integer input safely.
    """
    try:
        val = int(value)
        return max(min_val, min(max_val, val))
    except (ValueError, TypeError):
        return default


def sanitize_float(value: Any, min_val: float = 0.0, max_val: float = 100000.0, default: float = 0.0) -> float:
    """
    Cast and bound a floating-point input safely.
    """
    try:
        val = float(value)
        return round(max(min_val, min(max_val, val)), 4)
    except (ValueError, TypeError):
        return default


def sanitize_lane_counts(payload: Any, valid_lanes: Tuple[str, ...] = ("North", "South", "East", "West")) -> Dict[str, int]:
    """
    Sanitize a dictionary of lane vehicle counts.
    Ensures all recognized lanes exist with valid integer values within [0, 500].
    """
    result: Dict[str, int] = {}
    if not isinstance(payload, dict):
        return {lane: 0 for lane in valid_lanes}

    for lane in valid_lanes:
        raw_val = payload.get(lane, payload.get(lane.lower(), 0))
        result[lane] = sanitize_integer(raw_val, min_val=0, max_val=500, default=0)

    return result
