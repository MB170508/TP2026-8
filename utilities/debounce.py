"""Input debouncing utilities to prevent lag on rapid events."""

import threading
from typing import Callable, Any


class Debouncer:
    """Debounce rapid function calls to reduce processing overhead.

    Useful for text input predictions, search, autocomplete - anything that
    shouldn't fire on every keystroke but should fire after the user pauses.
    """

    def __init__(self, delay: float = 0.3):
        """Initialize debouncer.

        Args:
            delay: Delay in seconds before executing (default 300ms)
        """
        self.delay = delay
        self.timer = None

    def call(self, func: Callable, *args, **kwargs) -> None:
        """Call function with debounce.

        Cancels any pending call and schedules a new one.

        Args:
            func: Function to call
            *args, **kwargs: Arguments to pass
        """
        # Cancel previous pending call
        if self.timer:
            self.timer.cancel()

        # Schedule new call after delay
        self.timer = threading.Timer(self.delay, func, args=args, kwargs=kwargs)
        self.timer.start()

    def cancel(self) -> None:
        """Cancel any pending call."""
        if self.timer:
            self.timer.cancel()
            self.timer = None
