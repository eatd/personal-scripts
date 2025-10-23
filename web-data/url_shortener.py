#!/usr/bin/env python3
"""
Production-grade URL shortener with async support and multiple service backends.
Features retry logic, rate limiting, and comprehensive error handling.

Supports multiple URL shortening services with automatic fallback and caching.
"""

import argparse
import asyncio
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote, urlparse

try:
    import aiohttp

    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    import urllib.parse
    import urllib.request


@dataclass
class ShortenResult:
    """Result of URL shortening operation."""

    original_url: str
    short_url: Optional[str]
    service: str
    success: bool
    error: Optional[str] = None
    response_time: float = 0.0


class URLShortener:
    """Professional URL shortener with multiple backend support."""

    def __init__(self, cache_file: Optional[Path] = None, max_retries: int = 3):
        self.cache_file = cache_file or Path(".url_cache.json")
        self.max_retries = max_retries
        self.cache = self._load_cache()
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "successful": 0,
            "failed": 0,
        }

    def _load_cache(self) -> Dict[str, str]:
        """Load cached URL mappings."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cache: {e}", file=sys.stderr)

    def validate_url(self, url: str) -> tuple[bool, str]:
        """Validate URL format and add protocol if missing."""
        if not url or not url.strip():
            return False, "Empty URL provided"

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Validate URL structure
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "Invalid URL structure"
            return True, url
        except Exception as e:
            return False, f"URL validation error: {e}"

    async def shorten_tinyurl_async(self, url: str) -> ShortenResult:
        """Shorten URL using TinyURL service (async)."""
        start_time = time.time()
        api_url = f"http://tinyurl.com/api-create.php?url={quote(url)}"

        async with aiohttp.ClientSession() as session:
            for attempt in range(self.max_retries):
                try:
                    async with session.get(
                        api_url, timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            short_url = (await response.text()).strip()
                            response_time = time.time() - start_time
                            return ShortenResult(
                                original_url=url,
                                short_url=short_url,
                                service="TinyURL",
                                success=True,
                                response_time=response_time,
                            )
                        elif response.status == 429:  # Rate limited
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2**attempt)  # Exponential backoff
                                continue
                except asyncio.TimeoutError:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                except Exception as e:
                    return ShortenResult(
                        original_url=url,
                        short_url=None,
                        service="TinyURL",
                        success=False,
                        error=str(e),
                        response_time=time.time() - start_time,
                    )

        return ShortenResult(
            original_url=url,
            short_url=None,
            service="TinyURL",
            success=False,
            error="Max retries exceeded",
        )

    async def shorten_isgd_async(self, url: str) -> ShortenResult:
        """Shorten URL using is.gd service (async)."""
        start_time = time.time()
        api_url = "https://is.gd/create.php"
        data = {"format": "simple", "url": url}

        async with aiohttp.ClientSession() as session:
            for attempt in range(self.max_retries):
                try:
                    async with session.post(
                        api_url, data=data, timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            short_url = (await response.text()).strip()
                            if short_url.startswith("http"):
                                response_time = time.time() - start_time
                                return ShortenResult(
                                    original_url=url,
                                    short_url=short_url,
                                    service="is.gd",
                                    success=True,
                                    response_time=response_time,
                                )
                            else:
                                return ShortenResult(
                                    original_url=url,
                                    short_url=None,
                                    service="is.gd",
                                    success=False,
                                    error=short_url,
                                    response_time=time.time() - start_time,
                                )
                        elif response.status == 429:
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2**attempt)
                                continue
                except asyncio.TimeoutError:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                except Exception as e:
                    return ShortenResult(
                        original_url=url,
                        short_url=None,
                        service="is.gd",
                        success=False,
                        error=str(e),
                        response_time=time.time() - start_time,
                    )

        return ShortenResult(
            original_url=url,
            short_url=None,
            service="is.gd",
            success=False,
            error="Max retries exceeded",
        )

    def shorten_tinyurl_sync(self, url: str) -> ShortenResult:
        """Shorten URL using TinyURL service (synchronous fallback)."""
        start_time = time.time()
        api_url = f"http://tinyurl.com/api-create.php?url={quote(url)}"

        for attempt in range(self.max_retries):
            try:
                with urllib.request.urlopen(api_url, timeout=10) as response:
                    short_url = response.read().decode().strip()
                    return ShortenResult(
                        original_url=url,
                        short_url=short_url,
                        service="TinyURL",
                        success=True,
                        response_time=time.time() - start_time,
                    )
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < self.max_retries - 1:
                    time.sleep(2**attempt)
                    continue
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return ShortenResult(
                    original_url=url,
                    short_url=None,
                    service="TinyURL",
                    success=False,
                    error=str(e),
                    response_time=time.time() - start_time,
                )

        return ShortenResult(
            original_url=url,
            short_url=None,
            service="TinyURL",
            success=False,
            error="Max retries exceeded",
        )

    async def shorten_with_fallback_async(
        self, url: str, services: List[str] = None
    ) -> ShortenResult:
        """Try multiple services with automatic fallback."""
        services = services or ["is.gd", "tinyurl"]

        for service in services:
            if service.lower() == "is.gd":
                result = await self.shorten_isgd_async(url)
            elif service.lower() == "tinyurl":
                result = await self.shorten_tinyurl_async(url)
            else:
                continue

            if result.success:
                return result

        # All services failed
        return ShortenResult(
            original_url=url,
            short_url=None,
            service="all",
            success=False,
            error="All shortening services failed",
        )

    async def shorten_urls_batch_async(
        self, urls: List[str], service: str = "is.gd"
    ) -> List[ShortenResult]:
        """Shorten multiple URLs concurrently."""
        tasks = []

        for url in urls:
            # Check cache first
            if url in self.cache:
                self.stats["cache_hits"] += 1
                tasks.append(
                    asyncio.create_task(
                        asyncio.coroutine(
                            lambda: ShortenResult(
                                original_url=url,
                                short_url=self.cache[url],
                                service="cache",
                                success=True,
                                response_time=0.0,
                            )
                        )()
                    )
                )
            else:
                if service.lower() == "is.gd":
                    tasks.append(self.shorten_isgd_async(url))
                elif service.lower() == "tinyurl":
                    tasks.append(self.shorten_tinyurl_async(url))
                else:
                    tasks.append(self.shorten_with_fallback_async(url))

        results = await asyncio.gather(*tasks)

        # Update cache and stats
        for result in results:
            self.stats["total_requests"] += 1
            if result.success:
                self.stats["successful"] += 1
                if result.service != "cache":
                    self.cache[result.original_url] = result.short_url
            else:
                self.stats["failed"] += 1

        self._save_cache()
        return results

    def shorten_url_sync(self, url: str) -> ShortenResult:
        """Synchronous shortening for environments without async support."""
        self.stats["total_requests"] += 1

        # Check cache
        if url in self.cache:
            self.stats["cache_hits"] += 1
            self.stats["successful"] += 1
            return ShortenResult(
                original_url=url,
                short_url=self.cache[url],
                service="cache",
                success=True,
                response_time=0.0,
            )

        result = self.shorten_tinyurl_sync(url)

        if result.success:
            self.stats["successful"] += 1
            self.cache[result.original_url] = result.short_url
            self._save_cache()
        else:
            self.stats["failed"] += 1

        return result

    def print_stats(self):
        """Print usage statistics."""
        print("\n📊 URL Shortener Statistics")
        print(f"Total requests: {self.stats['total_requests']}")
        print(f"Cache hits: {self.stats['cache_hits']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        if self.stats["total_requests"] > 0:
            hit_rate = (self.stats["cache_hits"] / self.stats["total_requests"]) * 100
            print(f"Cache hit rate: {hit_rate:.1f}%")


async def main_async():
    """Async main function."""
    parser = argparse.ArgumentParser(
        description="Professional URL shortener with async support and caching"
    )
    parser.add_argument("urls", nargs="+", help="URLs to shorten")
    parser.add_argument(
        "--service",
        "-s",
        choices=["is.gd", "tinyurl", "auto"],
        default="is.gd",
        help="URL shortening service to use",
    )
    parser.add_argument("--output", "-o", type=Path, help="Save results to JSON file")
    parser.add_argument(
        "--cache", type=Path, help="Cache file location (default: .url_cache.json)"
    )
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--retries", type=int, default=3, help="Maximum retry attempts")
    parser.add_argument(
        "--stats", action="store_true", help="Show statistics after execution"
    )

    args = parser.parse_args()

    # Initialize shortener
    cache_file = None if args.no_cache else args.cache
    shortener = URLShortener(cache_file=cache_file, max_retries=args.retries)

    # Validate URLs
    validated_urls = []
    for url in args.urls:
        is_valid, result = shortener.validate_url(url)
        if is_valid:
            validated_urls.append(result)
        else:
            print(f"❌ Invalid URL '{url}': {result}", file=sys.stderr)

    if not validated_urls:
        print("❌ No valid URLs to shorten", file=sys.stderr)
        sys.exit(1)

    # Shorten URLs
    print(f"🔗 Shortening {len(validated_urls)} URLs using {args.service}...")
    results = await shortener.shorten_urls_batch_async(validated_urls, args.service)

    # Display results
    print("\n📋 Results:")
    for result in results:
        if result.success:
            print(f"✅ {result.original_url}")
            print(
                f"   → {result.short_url} ({result.service}, {result.response_time:.2f}s)"
            )
        else:
            print(f"❌ {result.original_url}")
            print(f"   Error: {result.error} ({result.service})")

    # Save to file if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        print(f"\n💾 Results saved to {args.output}")

    # Show statistics
    if args.stats:
        shortener.print_stats()

    # Exit with error code if any failures
    if any(not r.success for r in results):
        sys.exit(1)


def main_sync():
    """Synchronous fallback main function."""
    parser = argparse.ArgumentParser(
        description="URL shortener (sync mode - install aiohttp for async support)"
    )
    parser.add_argument("urls", nargs="+", help="URLs to shorten")
    parser.add_argument(
        "--cache", type=Path, help="Cache file location (default: .url_cache.json)"
    )
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")

    args = parser.parse_args()

    cache_file = None if args.no_cache else args.cache
    shortener = URLShortener(cache_file=cache_file)

    print(
        "⚠️  Running in sync mode. Install aiohttp for better performance:",
        file=sys.stderr,
    )
    print("   pip install aiohttp\n", file=sys.stderr)

    for url in args.urls:
        is_valid, validated_url = shortener.validate_url(url)
        if not is_valid:
            print(f"❌ Invalid URL '{url}': {validated_url}")
            continue

        result = shortener.shorten_url_sync(validated_url)

        if result.success:
            print(f"✅ {result.original_url}")
            print(f"   → {result.short_url}")
        else:
            print(f"❌ {result.original_url}")
            print(f"   Error: {result.error}")


def main():
    """Entry point with async/sync detection."""
    if ASYNC_AVAILABLE:
        asyncio.run(main_async())
    else:
        main_sync()


if __name__ == "__main__":
    main()
