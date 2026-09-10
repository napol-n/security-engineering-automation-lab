# Security Engineering & Automation Lab — Architecture

## Overview

This project demonstrates security engineering troubleshooting across network, application, Linux system, process, filesystem, and automation layers.

The engineering workflow used throughout the project is:

`Problem → Investigation → Root Cause → Remediation → Verification → Automation`

---

## Lab 01 — Network and Service Architecture

```text
Client
  |
  | HTTP :8080
  v
Docker Host Port
  |
  v
Nginx Reverse Proxy :80
  |
  | Docker DNS: app
  | HTTP :8000
  v
Python Backend
  |
  +-- GET /
  +-- GET /health
```

### Healthy Request Path

```text
localhost:8080
      ↓
Nginx
      ↓
app:8000
      ↓
Python Backend
      ↓
HTTP 200 OK
```

### Simulated Failure

Nginx was intentionally configured to use:

```text
app:8001
```

while the Python backend continued listening on:

```text
app:8000
```

Result:

```text
Client
  ↓
Nginx
  ↓
app:8001
  ↓
Connection Refused
  ↓
HTTP 502 Bad Gateway
```

### Investigation Layers

The failure was isolated by validating each dependency separately:

1. Docker container state
2. Host TCP listener
3. Docker DNS resolution
4. Direct backend connectivity
5. Nginx error logs
6. Effective Nginx configuration
7. End-to-end HTTP behavior

This allowed the reverse-proxy configuration to be identified as the failing layer.

---

## Lab 02 — Linux Service Architecture

```text
Linux Container
     |
     +-- PID 1: sleep infinity
     |
     +-- secsvc (UID 1000)
             |
             v
         service.py
             |
             | heartbeat
             v
 /var/log/secsvc/service.log
```

The application process runs separately from the container's primary process.

This design allows the lab to demonstrate an important operational principle:

`Container Running ≠ Process Running ≠ Service Healthy`

---

## Linux Permission Model

### Healthy State

```text
secsvc process
      |
      v
/var/log/secsvc
owner: secsvc
group: secsvc
mode: 750
      |
      v
service.log
```

The non-root service account can traverse the directory and write heartbeat records.

### Simulated Failure

```text
secsvc process
      |
      X
/var/log/secsvc
owner: root
group: root
mode: 700
```

Although the final log file remained owned by `secsvc`, the service could not traverse the parent directory.

The application therefore failed with:

```text
Permission denied
```

The investigation demonstrated that filesystem troubleshooting must consider every directory in a pathname rather than only the final file.

---

## Process Failure Model

Normal state:

```text
Container
   |
   +-- sleep infinity
   |
   +-- service.py
          |
          +-- heartbeat every ~5 seconds
```

After sending `SIGTERM` to the application:

```text
Container: Up
service.py: Not Running
heartbeat: Stopped
```

This demonstrated that infrastructure state and application health must be validated independently.

---

## Automation Layer

Two Python tools convert manual verification procedures into repeatable checks.

### HTTP Health Check

```text
health_check.py
      |
      v
GET /health
      |
      +-- HTTP connectivity
      +-- response status
      +-- JSON validity
      +-- application health
      |
      v
exit 0 / exit 1
```

Script:

`scripts/health_check.py`

Healthy:

```text
exit 0
```

Failure:

```text
exit 1
```

---

### Heartbeat Log Analyzer

```text
service.log
     |
     v
log_analyzer.py
     |
     +-- log format
     +-- UID
     +-- health status
     +-- heartbeat gaps
     +-- heartbeat freshness
     +-- PID observation
     |
     v
exit 0 / exit 1
```

Script:

`scripts/log_analyzer.py`

The analyzer validates both operational and security-relevant runtime signals.

---

## Security Engineering Layers

The project follows a layered troubleshooting model:

```text
Network
   ↓
Reverse Proxy
   ↓
Application
   ↓
Process
   ↓
Execution Identity
   ↓
Filesystem
   ↓
Logs
   ↓
Automation
```

A healthy status at one layer is not treated as proof that the complete service is healthy.

Instead, each layer is independently validated using observable evidence.

---

## Engineering Principles Demonstrated

* Evidence-driven troubleshooting
* Failure-domain isolation
* Root-cause analysis
* Least-privilege remediation
* Functional verification
* Process and service health separation
* Network dependency analysis
* Security-relevant runtime validation
* Automation after understanding failure modes
