"""API rate limiting using sliding window algorithm.

Prevents excessive API calls per service.
Default: 5 calls per 60 seconds per API.
"""

from collections import defaultdict
from time import time
from typing import Tuple

from utilities.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Sliding window rate limiter per API.

    Tracks call timestamps and enforces limits.
    """

    def __init__(self, calls_per_window: int = 5, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            calls_per_window: Max calls allowed in window (default 5)
            window_seconds: Time window in seconds (default 60)
        """
        self.calls_per_window = calls_per_window
        self.window_seconds = window_seconds
        # Track call times per API name: {api_name: [timestamp1, timestamp2, ...]}
        self.call_times = defaultdict(list)

    def is_allowed(self, api_name: str) -> Tuple[bool, float]:
        """Check if API call is allowed.

        Sliding window: only counts calls in the last window_seconds.

        Args:
            api_name: Name of API (e.g., 'wolfram', 'lunch')

        Returns:
            (is_allowed, wait_seconds_if_not_allowed)
            - If allowed: (True, 0.0)
            - If rate limited: (False, seconds_until_next_allowed)
        """
        now = time()

        # Remove calls outside the window
        self.call_times[api_name] = [
            ts for ts in self.call_times[api_name] if now - ts < self.window_seconds
        ]

        # Check if under limit
        if len(self.call_times[api_name]) < self.calls_per_window:
            # Record this call
            self.call_times[api_name].append(now)
            logger.debug(f"Rate limit: {api_name} allowed ({len(self.call_times[api_name])}/{self.calls_per_window})")
            return True, 0.0

        # Rate limited: calculate wait time until oldest call leaves window
        oldest_call = self.call_times[api_name][0]
        wait_seconds = self.window_seconds - (now - oldest_call)

        logger.warning(
            f"Rate limit: {api_name} blocked ({len(self.call_times[api_name])}/{self.calls_per_window}). "
            f"Wait {wait_seconds:.1f}s"
        )

        return False, max(wait_seconds, 0.1)

    def reset(self, api_name: str = None) -> None:
        """Reset rate limit for an API (for testing).

        Args:
            api_name: Specific API to reset, or None to reset all
        """
        if api_name:
            self.call_times[api_name] = []
            logger.debug(f"Reset rate limit for {api_name}")
        else:
            self.call_times.clear()
            logger.debug("Reset all rate limits")
