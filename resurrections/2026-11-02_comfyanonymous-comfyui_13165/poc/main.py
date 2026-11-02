import asyncio
import aiohttp
import collections
import logging
from typing import Any, Callable, Dict, Optional

# Simple logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LRUCache:
    """A tiny in‑memory LRU cache.
    Stores up to `maxsize` items; oldest accessed items are evicted.
    """
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self.cache: collections.OrderedDict[str, Any] = collections.OrderedDict()
        self.lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                logger.debug("Cache hit for %s", key)
                return self.cache[key]
            logger.debug("Cache miss for %s", key)
            return None

    async def set(self, key: str, value: Any) -> None:
        async with self.lock:
            self.cache[key] = value
            self.cache.move_to_end(key)
            if len(self.cache) > self.maxsize:
                evicted = self.cache.popitem(last=False)
                logger.debug("Cache evicted %s", evicted[0])

class AsyncResourceManager:
    """Manages asynchronous loading of resources with caching.
    Each request returns an asyncio.Future that resolves when the
    resource is available or fails with an exception.
    """
    def __init__(self, cache_size: int = 64):
        self.session = aiohttp.ClientSession()
        self.cache = LRUCache(maxsize=cache_size)
        self.pending: Dict[str, asyncio.Future] = {}
        self.error_callbacks: list[Callable[[str, Exception], None]] = []
        self.lock = asyncio.Lock()

    async def close(self) -> None:
        await self.session.close()

    def on_error(self, callback: Callable[[str, Exception], None]) -> None:
        """Register a callback to be invoked on load errors.
        Callback receives the URL and the exception instance.
        """
        self.error_callbacks.append(callback)

    async def fetch(self, url: str) -> Any:
        """Public method to fetch a resource.
        Returns the cached value or initiates a network request.
        """
        # Check cache first
        cached = await self.cache.get(url)
        if cached is not None:
            return cached

        async with self.lock:
            # If a request is already pending, reuse its future
            if url in self.pending:
                logger.info("Waiting for pending request: %s", url)
                return await self.pending[url]

            # Create a new future and store it
            future: asyncio.Future = asyncio.get_event_loop().create_future()
            self.pending[url] = future

        # Perform the actual network request outside the lock
        asyncio.create_task(self._load_resource(url, future))
        return await future

    async def _load_resource(self, url: str, future: asyncio.Future) -> None:
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    raise aiohttp.ClientResponseError(
                        request_info=resp.request_info,
                        history=resp.history,
                        status=resp.status,
                        message=f"Failed to fetch {url}, status {resp.status}",
                        headers=resp.headers,
                    )
                data = await resp.read()
                await self.cache.set(url, data)
                future.set_result(data)
                logger.info("Resource loaded successfully: %s", url)
        except Exception as e:
            logger.error("Error loading %s: %s", url, e)
            future.set_exception(e)
            for cb in self.error_callbacks:
                try:
                    cb(url, e)
                except Exception as cb_err:
                    logger.exception("Error in error callback: %s", cb_err)
        finally:
            async with self.lock:
                self.pending.pop(url, None)

# ---------------------------------------------------------------------------
# Example usage (would be called from UI code)
# ---------------------------------------------------------------------------
async def example_usage():
    manager = AsyncResourceManager(cache_size=32)

    # Register a simple error handler that could be wired to a Qt signal
    def error_handler(url: str, exc: Exception) -> None:
        print(f"[ERROR] Failed to load {url}: {exc}")

    manager.on_error(error_handler)

    test_urls = [
        "https://httpbin.org/bytes/64",
        "https://httpbin.org/status/404",  # intentional failure
        "https://httpbin.org/bytes/128",
    ]

    tasks = [manager.fetch(u) for u in test_urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for url, result in zip(test_urls, results):
        if isinstance(result, Exception):
            print(f"{url} -> error: {result}")
        else:
            print(f"{url} -> {len(result)} bytes")

    await manager.close()

# ---------------------------------------------------------------------------
# pytest‑asyncio based tests
# ---------------------------------------------------------------------------
import pytest

@pytest.mark.asyncio
async def test_successful_fetch(monkeypatch):
    manager = AsyncResourceManager(cache_size=2)
    url = "https://httpbin.org/bytes/16"
    data = await manager.fetch(url)
    assert isinstance(data, (bytes, bytearray))
    # Second fetch should hit the cache and not raise
    cached = await manager.fetch(url)
    assert cached == data
    await manager.close()

@pytest.mark.asyncio
async def test_failed_fetch(monkeypatch, capsys):
    manager = AsyncResourceManager()
    errors: list[tuple[str, Exception]] = []
    manager.on_error(lambda u, e: errors.append((u, e)))
    url = "https://httpbin.org/status/500"
    with pytest.raises(aiohttp.ClientResponseError):
        await manager.fetch(url)
    assert errors and errors[0][0] == url
    await manager.close()

# ---------------------------------------------------------------------------
# Entry point for manual run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(example_usage())