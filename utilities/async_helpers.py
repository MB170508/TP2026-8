"""Async helpers for non-blocking I/O in Flet.

Bridges asyncio and Flet's single-threaded event loop using thread pool.
Prevents UI freezes during long-running operations.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from utilities.logger import get_logger

logger = get_logger(__name__)

# Thread pool for blocking I/O operations
# Max 3 workers to prevent resource exhaustion
executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="ittoolbox")


async def run_in_thread(func: Callable, *args, **kwargs) -> Any:
    """Run blocking function in thread pool without blocking UI.

    Transfers execution to a background thread, allowing event loop to continue.
    Useful for network calls, file I/O, etc.

    Args:
        func: Blocking function to call
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Return value of func
    """
    loop = asyncio.get_event_loop()
    try:
        logger.debug(f"Running {func.__name__} in thread pool")
        result = await loop.run_in_executor(executor, func, *args)
        logger.debug(f"Thread pool: {func.__name__} completed")
        return result
    except Exception as e:
        logger.error(f"Thread pool error in {func.__name__}: {e}", exc_info=True)
        raise
