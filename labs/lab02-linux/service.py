#!/usr/bin/env python3

import argparse
import datetime
import os
import sys
import time


LOG_FILE = "/var/log/secsvc/service.log"


def write_heartbeat():
    timestamp = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()

    message = (
        f"{timestamp} "
        f"pid={os.getpid()} "
        f"uid={os.getuid()} "
        f"status=healthy\n"
    )

    try:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(message)

    except PermissionError:
        print(
            f"[FAIL] Permission denied writing to {LOG_FILE}",
            file=sys.stderr,
        )
        return 1

    print(
        f"[OK] heartbeat written | "
        f"pid={os.getpid()} | uid={os.getuid()}"
    )

    return 0


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--once",
        action="store_true",
        help="Write one heartbeat and exit",
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Heartbeat interval in seconds",
    )

    args = parser.parse_args()

    if args.once:
        sys.exit(write_heartbeat())

    while True:
        result = write_heartbeat()

        if result != 0:
            sys.exit(result)

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
