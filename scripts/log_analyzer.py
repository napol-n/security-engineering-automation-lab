#!/usr/bin/env python3

import argparse
import re
import sys
from datetime import datetime, timezone


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\S+)\s+"
    r"pid=(?P<pid>\d+)\s+"
    r"uid=(?P<uid>\d+)\s+"
    r"status=(?P<status>\S+)$"
)


def parse_log_line(line):
    match = LOG_PATTERN.match(line.strip())

    if not match:
        return None

    try:
        timestamp = datetime.fromisoformat(
            match.group("timestamp")
        )
    except ValueError:
        return None

    return {
        "timestamp": timestamp,
        "pid": int(match.group("pid")),
        "uid": int(match.group("uid")),
        "status": match.group("status"),
    }


def analyze(records, expected_uid, max_gap, max_age):
    findings = []

    for record in records:
        if record["uid"] != expected_uid:
            findings.append(
                f"Unexpected UID {record['uid']} "
                f"(expected {expected_uid})"
            )

        if record["status"] != "healthy":
            findings.append(
                f"Unhealthy status: {record['status']}"
            )

    for previous, current in zip(records, records[1:]):
        gap = (
            current["timestamp"] - previous["timestamp"]
        ).total_seconds()

        if gap > max_gap:
            findings.append(
                f"Heartbeat gap {gap:.1f}s exceeds "
                f"maximum {max_gap:.1f}s"
            )

    latest = records[-1]["timestamp"]

    if latest.tzinfo is None:
        latest = latest.replace(tzinfo=timezone.utc)

    age = (
        datetime.now(timezone.utc) - latest
    ).total_seconds()

    if max_age > 0 and age > max_age:
        findings.append(
            f"Latest heartbeat is stale: {age:.1f}s old "
            f"(maximum {max_age:.1f}s)"
        )

    return findings


def main():
    parser = argparse.ArgumentParser(
        description="Analyze security service heartbeat logs."
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Path to heartbeat log file",
    )

    parser.add_argument(
        "--expected-uid",
        type=int,
        default=1000,
        help="Expected service UID",
    )

    parser.add_argument(
        "--max-gap",
        type=float,
        default=10.0,
        help="Maximum allowed heartbeat gap in seconds",
    )

    parser.add_argument(
        "--max-age",
        type=float,
        default=15.0,
        help="Maximum age of the latest heartbeat",
    )

    parser.add_argument(
        "--tail",
        type=int,
        default=10,
        help="Number of latest records to analyze",
    )

    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as log_file:
            lines = [
                line.strip()
                for line in log_file
                if line.strip()
            ]

    except OSError as error:
        print(f"[FAIL] Cannot read log file: {error}")
        sys.exit(1)

    selected_lines = lines[-args.tail:]

    if not selected_lines:
        print("[FAIL] Log file contains no records")
        sys.exit(1)

    records = []

    for line_number, line in enumerate(
        selected_lines,
        start=1,
    ):
        record = parse_log_line(line)

        if record is None:
            print(
                f"[FAIL] Malformed log record "
                f"#{line_number}: {line}"
            )
            sys.exit(1)

        records.append(record)

    findings = analyze(
        records,
        args.expected_uid,
        args.max_gap,
        args.max_age,
    )

    pids = sorted(
        {record["pid"] for record in records}
    )

    if findings:
        for finding in findings:
            print(f"[FAIL] {finding}")

        print(
            f"[SUMMARY] records={len(records)} "
            f"pids={pids} findings={len(findings)}"
        )

        sys.exit(1)

    print(
        f"[OK] Log healthy | "
        f"records={len(records)} | "
        f"uid={args.expected_uid} | "
        f"pids={pids}"
    )

    sys.exit(0)


if __name__ == "__main__":
    main()
