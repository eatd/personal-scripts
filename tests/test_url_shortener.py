"""
Unit tests for URL shortener functionality.
Tests async operations, caching, retry logic, and error handling.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock aiohttp if not available
try:
    import aiohttp

    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "web-data"))

from url_shortener import ShortenResult, URLShortener


class TestURLValidation:
    """Test URL validation functionality."""

    def test_valid_url_with_protocol(self):
        shortener = URLShortener()
        is_valid, result = shortener.validate_url("https://www.example.com")
        assert is_valid
        assert result == "https://www.example.com"

    def test_valid_url_without_protocol(self):
        shortener = URLShortener()
        is_valid, result = shortener.validate_url("www.example.com")
        assert is_valid
        assert result == "https://www.example.com"

    def test_invalid_empty_url(self):
        shortener = URLShortener()
        is_valid, result = shortener.validate_url("")
        assert not is_valid
        assert "Empty" in result

    def test_invalid_malformed_url(self):
        shortener = URLShortener()
        is_valid, result = shortener.validate_url("not a url")
        assert not is_valid


class TestCaching:
    """Test caching functionality."""

    def test_cache_hit(self, tmp_path):
        cache_file = tmp_path / "test_cache.json"
        shortener = URLShortener(cache_file=cache_file)

        # Add to cache
        test_url = "https://www.example.com"
        test_short = "https://short.url/abc"
        shortener.cache[test_url] = test_short
        shortener._save_cache()

        # Create new instance and check cache hit
        shortener2 = URLShortener(cache_file=cache_file)
        result = shortener2.shorten_url_sync(test_url)

        assert result.success
        assert result.short_url == test_short
        assert result.service == "cache"

    def test_cache_persistence(self, tmp_path):
        cache_file = tmp_path / "test_cache.json"
        shortener = URLShortener(cache_file=cache_file)

        shortener.cache["https://test.com"] = "https://short.url/test"
        shortener._save_cache()

        # Reload cache
        loaded_cache = shortener._load_cache()
        assert "https://test.com" in loaded_cache
        assert loaded_cache["https://test.com"] == "https://short.url/test"


class TestStatistics:
    """Test statistics tracking."""

    def test_stats_initialization(self):
        shortener = URLShortener()
        assert shortener.stats["total_requests"] == 0
        assert shortener.stats["cache_hits"] == 0
        assert shortener.stats["successful"] == 0
        assert shortener.stats["failed"] == 0

    def test_stats_update_on_success(self):
        shortener = URLShortener()
        shortener.cache["https://test.com"] = "https://short.url/test"

        result = shortener.shorten_url_sync("https://test.com")

        assert shortener.stats["total_requests"] == 1
        assert shortener.stats["cache_hits"] == 1
        assert shortener.stats["successful"] == 1


@pytest.mark.skipif(not ASYNC_AVAILABLE, reason="aiohttp not available")
class TestAsyncOperations:
    """Test async URL shortening operations."""

    @pytest.mark.asyncio
    async def test_async_shortening_success(self):
        shortener = URLShortener()

        # Mock successful response
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="https://tinyurl.com/test")
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await shortener.shorten_tinyurl_async("https://www.example.com")

            assert result.success
            assert result.short_url == "https://tinyurl.com/test"
            assert result.service == "TinyURL"

    @pytest.mark.asyncio
    async def test_async_retry_on_rate_limit(self):
        shortener = URLShortener(max_retries=2)

        # Mock rate limit then success
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response_fail = AsyncMock()
            mock_response_fail.status = 429

            mock_response_success = AsyncMock()
            mock_response_success.status = 200
            mock_response_success.text = AsyncMock(
                return_value="https://tinyurl.com/retry"
            )

            mock_get.return_value.__aenter__.side_effect = [
                mock_response_fail,
                mock_response_success,
            ]

            result = await shortener.shorten_tinyurl_async("https://www.example.com")

            assert result.success
            assert mock_get.call_count == 2

    @pytest.mark.asyncio
    async def test_async_batch_shortening(self):
        shortener = URLShortener()
        urls = [
            "https://www.example1.com",
            "https://www.example2.com",
            "https://www.example3.com",
        ]

        with patch.object(shortener, "shorten_isgd_async") as mock_shorten:
            mock_shorten.side_effect = [
                ShortenResult(
                    "https://www.example1.com", "https://is.gd/1", "is.gd", True
                ),
                ShortenResult(
                    "https://www.example2.com", "https://is.gd/2", "is.gd", True
                ),
                ShortenResult(
                    "https://www.example3.com", "https://is.gd/3", "is.gd", True
                ),
            ]

            results = await shortener.shorten_urls_batch_async(urls, "is.gd")

            assert len(results) == 3
            assert all(r.success for r in results)


class TestSynchronousFallback:
    """Test synchronous operations when async not available."""

    def test_sync_shortening(self):
        shortener = URLShortener()

        # This will make actual network call or fail gracefully
        result = shortener.shorten_tinyurl_sync("https://www.example.com")

        # We can't guarantee success due to network, but check structure
        assert isinstance(result, ShortenResult)
        assert result.original_url == "https://www.example.com"
        assert result.service == "TinyURL"

    def test_sync_retry_logic(self):
        shortener = URLShortener(max_retries=3)

        with patch("urllib.request.urlopen") as mock_urlopen:
            # Simulate multiple failures then success
            mock_urlopen.side_effect = [
                Exception("Network error"),
                Exception("Network error"),
                MagicMock(
                    read=lambda: b"https://tinyurl.com/success",
                    __enter__=lambda self: self,
                    __exit__=lambda *args: None,
                ),
            ]

            result = shortener.shorten_tinyurl_sync("https://www.example.com")

            assert mock_urlopen.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
