#!/usr/bin/env python3

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def check_health(url, timeout):
    request = Request(
        url,
        headers={"User-Agent": "security-engineering-health-check/1.0"},
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")

    except HTTPError as error:
        print(f"[FAIL] HTTP error: {error.code} {error.reason}")
        return 1

    except URLError as error:
        print(f"[FAIL] Connection error: {error.reason}")
        return 1

    except TimeoutError:
        print(f"[FAIL] Request timed out after {timeout} seconds")
        return 1

    if status_code != 200:
        print(f"[FAIL] Unexpected HTTP status: {status_code}")
        return 1

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print("[FAIL] Response was not valid JSON")
        return 1

    if data.get("status") != "healthy":
        print(
            f"[FAIL] Application reported unexpected status: "
            f"{data.get('status')}"
        )
        return 1

    print(
        f"[OK] Service healthy | "
        f"HTTP {status_code} | "
        f"service={data.get('service')} | "
        f"hostname={data.get('hostname')}"
    )

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Check the health of an HTTP service."
    )

    parser.add_argument(
        "--url",
        default="http://localhost:8080/health",
        help="Health endpoint URL",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Request timeout in seconds",
    )

    args = parser.parse_args()

    sys.exit(check_health(args.url, args.timeout))


if __name__ == "__main__":
    main()
