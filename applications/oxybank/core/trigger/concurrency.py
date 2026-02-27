"""Concurrency control for trigger system.

This module provides rate limiting and concurrency control for HTTP callbacks
to prevent overwhelming downstream APIs and system resources.
"""
import asyncio
import time
from typing import Awaitable, TypeVar

from loguru import logger

T = TypeVar("T")


class TokenBucket:
    """Token bucket rate limiter implementation.

    Uses token bucket algorithm to limit request rate (QPS).
    Tokens are refilled at a constant rate over time.

    Args:
        rate: Maximum requests per second (QPS)
    """

    def __init__(self, rate: int):
        self.rate = rate  # tokens per second
        self.tokens = float(rate)  # current token count
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a token, waiting if necessary.

        If no tokens are available, waits until the next token is available.
        """
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_refill

            # Refill tokens based on elapsed time
            self.tokens = min(
                self.rate,
                self.tokens + (elapsed * self.rate)
            )
            self.last_refill = now

            # If no tokens available, calculate wait time
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

    def get_available_tokens(self) -> float:
        """Get current available token count (for monitoring)."""
        now = time.time()
        elapsed = now - self.last_refill
        return min(self.rate, self.tokens + (elapsed * self.rate))


class ConcurrencyManager:
    """Manages concurrency control for trigger HTTP execution.

    Combines Semaphore (concurrent request limit) with TokenBucket (rate limit)
    to provide dual-layer protection against overwhelming downstream APIs.

    Args:
        max_concurrent: Maximum number of concurrent HTTP requests
        max_qps: Maximum queries per second for each URL
    """

    def __init__(self, max_concurrent: int = 10, max_qps: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limiter = TokenBucket(max_qps)
        self.max_concurrent = max_concurrent
        self.max_qps = max_qps

    async def execute(self, coro: Awaitable[T]) -> T:
        """Execute coroutine with concurrency and rate limiting.

        Args:
            coro: Coroutine to execute

        Returns:
            Result of the coroutine

        Example:
            >>> result = await concurrency_manager.execute(http_client.post(url))
        """
        async with self.semaphore:
            await self.rate_limiter.acquire()
            return await coro

    def get_stats(self) -> dict:
        """Get current concurrency statistics for monitoring.

        Returns:
            Dictionary with concurrency and rate limiter stats
        """
        return {
            "max_concurrent": self.max_concurrent,
            "max_qps": self.max_qps,
            "available_tokens": self.rate_limiter.get_available_tokens(),
            "semaphore_locked": self.semaphore.locked()
        }
