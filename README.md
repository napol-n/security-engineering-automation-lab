# Security Engineering & Automation Lab

Hands-on security engineering project demonstrating evidence-driven troubleshooting, root-cause analysis, remediation, verification, and Python-based automation.

## Objective

This project extends SOC investigation experience toward a Security Engineering mindset.

The engineering workflow used throughout the project is:

`Problem → Investigation → Root Cause → Remediation → Verification → Automation`

Rather than focusing only on alerts or tool usage, each lab requires identifying why a system failed, applying a targeted remediation, and proving that the service recovered.

---

## Project Scope

This project covers:

* Network and service troubleshooting
* HTTP and reverse-proxy failures
* Docker networking and DNS
* Linux system administration
* Linux filesystem permissions
* Process and service troubleshooting
* Least-privilege remediation
* Operational log analysis
* Python security automation
* Machine-readable health verification

---

## Architecture

See:

[`docs/architecture.md`](docs/architecture.md)

The project contains two primary troubleshooting labs and an automation layer.

```text
Client
  ↓
Nginx Reverse Proxy
  ↓
Docker Network
  ↓
Python Backend

        +

Linux Service
  ↓
Non-root service account
  ↓
Filesystem / Process / Logs

        ↓

Python Automation
├── health_check.py
└── log_analyzer.py
```

---

# Lab 01 — Network & Service Troubleshooting

## Environment

A containerized application consisting of:

```text
Client
  ↓
localhost:8080
  ↓
Nginx :80
  ↓
Docker DNS / Network
  ↓
Python Backend :8000
```

A healthy baseline was established before introducing a controlled failure.

## Simulated Incident

The Nginx upstream port was intentionally changed from:

`app:8000`

to:

`app:8001`

The client then received:

`HTTP/1.1 502 Bad Gateway`

## Investigation

The investigation verified:

* Container state with Docker Compose
* Host TCP listener with `lsof`
* Docker DNS resolution with `getent`
* Direct backend connectivity
* Application health endpoint
* Nginx error logs
* Effective Nginx configuration

The backend remained healthy on port `8000`, while Nginx attempted to connect to port `8001`.

Nginx reported:

`Connection refused`

## Root Cause

The reverse proxy configuration referenced the wrong backend TCP port.

```text
Nginx → app:8001 ❌

Python → listening on app:8000 ✅
```

## Remediation

The upstream configuration was restored to:

`app:8000`

The Nginx configuration was validated and the original request was repeated.

## Verification

Before remediation:

`HTTP 502 Bad Gateway`

After remediation:

`HTTP 200 OK`

This demonstrated that container availability alone does not guarantee complete service availability.

---

# Lab 02 — Linux System Troubleshooting

The Linux lab runs a Python service using a dedicated non-root account:

`secsvc`

The service writes heartbeat records to:

`/var/log/secsvc/service.log`

Example:

```text
2026-09-10T12:43:23+00:00 pid=80 uid=1000 status=healthy
```

## Incident 1 — Filesystem Permission Failure

### Healthy State

```text
Owner: secsvc
Group: secsvc
Mode: 750
```

### Simulated Failure

The log directory was changed to:

```text
Owner: root
Group: root
Mode: 700
```

The application then returned:

`Permission denied`

with exit code:

`1`

### Investigation

The investigation used:

* `id`
* `ls -ld`
* `namei -l`
* UID/GID analysis
* Unix permission bits
* application exit codes

The log file itself remained owned by `secsvc`, but the application could not traverse its parent directory.

### Root Cause

`/var/log/secsvc` was owned by `root:root` with mode `700`.

The non-root service account therefore had no execute/traverse permission on the directory.

### Remediation

The intended state was restored:

```text
Owner: secsvc
Group: secsvc
Mode: 750
```

This restored application functionality without using unnecessarily broad permissions such as `777`.

### Verification

Before remediation:

```text
Permission denied
exit 1
```

After remediation:

```text
heartbeat written
exit 0
```

---

## Incident 2 — Application Process Termination

A continuously running Python service generated heartbeat records approximately every five seconds.

Initial application process:

`PID 13`

The process was terminated using:

`SIGTERM`

## Investigation

After termination:

* The Docker container remained `Up`
* `pgrep` no longer found the Python process
* `ps` showed only the container's primary process
* heartbeat logs stopped updating

This demonstrated:

`Container Running ≠ Process Running ≠ Service Healthy`

## Remediation

The application was restarted using the intended non-root service account.

The new process received:

`PID 80`

## Verification

Heartbeat logging resumed approximately every five seconds.

This confirmed both process recovery and functional recovery.

---

# Automation

## HTTP Health Check

Script:

[`scripts/health_check.py`](scripts/health_check.py)

The script validates:

* HTTP connectivity
* HTTP response status
* JSON response validity
* application-reported health status

Behavior:

```text
Healthy   → exit 0
Failure   → exit 1
```

This makes the check usable by:

* shell scripts
* CI/CD pipelines
* deployment verification
* monitoring workflows

---

## Log Analyzer

Script:

[`scripts/log_analyzer.py`](scripts/log_analyzer.py)

The analyzer parses heartbeat records and validates:

* Log structure
* Service UID
* Application status
* Heartbeat gaps
* Heartbeat freshness
* Process IDs

### Test Cases

| Scenario                                    | Expected Result |
| ------------------------------------------- | --------------- |
| Real healthy heartbeat log                  | Exit `0`        |
| Synthetic unexpected UID / unhealthy status | Exit `1`        |
| Synthetic malformed log                     | Exit `1`        |

The anomaly and malformed samples are explicitly synthetic test data.

The real healthy sample was collected from the Linux service lab.

---

# Evidence

Technical evidence is stored under:

[`evidence/`](evidence/)

Key evidence includes:

* `day01-environment.md`
* `day01-network-service-incident.md`
* `day01-health-check-automation.md`
* `day02-linux-permission-incident.md`
* `day02-linux-process-incident.md`
* `day04-log-analysis-automation.md`

Evidence follows the general structure:

`Problem → Investigation → Root Cause → Remediation → Verification`

---

# Interview Notes

Hands-on interview notes are stored under:

[`interview-notes/`](interview-notes/)

Topics include:

* Network and service troubleshooting
* Linux permission troubleshooting
* Linux process troubleshooting
* Log-analysis automation

The explanations are based on the actual lab work rather than memorized definitions.

---

# Tools & Technologies

* macOS / Apple Silicon
* Docker Desktop
* Linux containers
* Nginx
* Python
* Git
* curl
* lsof
* getent
* ps
* pgrep
* namei
* chmod
* chown

---

# Security Engineering Principles Demonstrated

## Evidence-Driven Troubleshooting

Configuration changes were made only after collecting evidence and narrowing the failure domain.

## Root-Cause Analysis

Symptoms such as HTTP 502 or permission-denied errors were separated from their actual underlying causes.

## Least Privilege

Linux permissions were remediated by restoring the minimum intended access instead of applying broad permissions.

## Functional Verification

A process being present or a container being online was not treated as sufficient proof of application health.

## Automation After Understanding

Health and log-analysis automation were created after the system behavior and failure modes had been manually investigated.

---

# Key Takeaways

This project demonstrates the ability to move beyond alert triage toward a Security Engineering workflow:

```text
Observe
  ↓
Investigate
  ↓
Isolate
  ↓
Root Cause
  ↓
Remediate
  ↓
Verify
  ↓
Automate
```

The primary lesson is that system availability must be validated across multiple layers — network, process, configuration, permissions, logs, and application behavior — rather than relying on a single status indicator.
