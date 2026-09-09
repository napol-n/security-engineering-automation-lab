# Day 1 — Health Check Automation

## Objective

Automate end-to-end service health verification after completing manual troubleshooting and remediation.

## Script

`scripts/health_check.py`

## Method

The script validates:

1. HTTP connectivity
2. HTTP status code
3. JSON response validity
4. Application-reported health status

The script returns operating-system exit codes so it can be integrated with shell scripts, CI/CD pipelines, deployment verification, or monitoring workflows.

## Healthy Test

Command:

`python3 scripts/health_check.py`

Result:

`[OK] Service healthy | HTTP 200 | service=security-engineering-backend`

Exit code:

`0`

## Configurable Test

The script supports command-line parameters.

Example:

`python3 scripts/health_check.py --url http://localhost:8080/health --timeout 2`

This allows the target endpoint and request timeout to be changed without modifying the source code.

## Failure Test

Command:

`python3 scripts/health_check.py --url http://localhost:8080/not-found`

Result:

`[FAIL] HTTP error: 404 Not Found`

Expected exit code:

`1`

## Engineering Value

Manual troubleshooting identified the service dependencies and failure modes first.

Automation was added only after the healthy state, failure state, root cause, remediation, and verification process were understood.

This avoids automating an incorrect assumption about system health.

## Automation Flow

`HTTP Request → Status Validation → JSON Validation → Application Health Validation → Exit Code`

## Lessons Learned

A useful health check should validate more than whether a process or TCP port exists.

An HTTP service may be reachable while still returning an application error.

Exit codes allow the health-check result to be consumed by other automation systems.
