#!/usr/bin/env python3
"""Measure download speed by fetching the same URL ten times in sequence."""

import argparse
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024
TIMEOUT_SECONDS = 30


def download_once(url: str) -> tuple[int, float]:
    """Download the full response and return its byte count and elapsed seconds."""
    request = Request(url, headers={"User-Agent": "simple-speedtest/1.0"})
    byte_count = 0
    started_at = time.perf_counter()

    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        while chunk := response.read(CHUNK_SIZE):
            byte_count += len(chunk)

    elapsed_seconds = time.perf_counter() - started_at
    return byte_count, elapsed_seconds


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure download speed by downloading a URL ten times in sequence."
    )
    parser.add_argument("url", help="URL of the file or resource to download")
    args = parser.parse_args()

    total_bytes = 0
    total_seconds = 0.0

    try:
        for number in range(1, REQUEST_COUNT + 1):
            byte_count, elapsed_seconds = download_once(args.url)
            total_bytes += byte_count
            total_seconds += elapsed_seconds
            print(
                f"Request {number}/{REQUEST_COUNT}: "
                f"{byte_count:,} bytes in {elapsed_seconds:.3f} s"
            )
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        print(f"Download failed: {error}", file=sys.stderr)
        return 1

    average_seconds = total_seconds / REQUEST_COUNT
    megabytes_per_second = total_bytes / total_seconds / 1_000_000

    print(f"\nRequests completed: {REQUEST_COUNT}")
    print(f"Total downloaded: {total_bytes:,} bytes ({total_bytes / 1_000_000:.3f} MB)")
    print(f"Average request time: {average_seconds:.3f} s")
    print(f"Average download speed: {megabytes_per_second:.3f} MB/s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
