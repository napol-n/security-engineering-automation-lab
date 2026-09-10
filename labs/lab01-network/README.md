# Lab 01 — Network and Service Troubleshooting

## Objective

Build a small containerized application, establish a healthy baseline, introduce a controlled reverse-proxy failure, investigate the problem systematically, identify the root cause, remediate it, and verify recovery.

The troubleshooting workflow used in this lab is:

`Problem → Investigation → Root Cause → Remediation → Verification`

---

## Architecture

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

The backend is accessible internally through the Docker network.

Only Nginx exposes a port to the host.

---

## Components

### Python Backend

Application:

`app/app.py`

The Python HTTP service listens on:

```text
0.0.0.0:8000
```

Available endpoints:

```text
/
```

and:

```text
/health
```

The health endpoint returns JSON containing application status and container hostname.

---

### Nginx Reverse Proxy

Nginx receives client traffic on container port:

```text
80
```

Docker Compose publishes the service to the host as:

```text
localhost:8080
```

Healthy upstream configuration:

```text
app:8000
```

Docker's internal DNS resolves the hostname:

```text
app
```

to the backend container.

---

## Healthy Baseline

Start the environment:

```bash
docker compose up -d
```

### Command Explanation

`docker compose`

Uses Docker Compose to manage the multi-container application.

`up`

Creates and starts the services defined in `docker-compose.yml`.

`-d`

Runs the containers in detached mode so the terminal remains available.

---

Check container status:

```bash
docker compose ps
```

The expected state is that both the application and Nginx containers are running.

---

Test the service from the host:

```bash
curl -i http://localhost:8080/health
```

### Command Explanation

`curl`

Sends an HTTP request.

`-i`

Includes HTTP response headers in the output.

Healthy result:

```text
HTTP/1.1 200 OK
```

with application health information in the response body.

---

## Dependency Validation

The lab validates multiple layers separately rather than assuming that a running container means the application is healthy.

### Docker DNS

From the Nginx container:

```bash
docker compose exec nginx getent hosts app
```

`docker compose exec nginx`

Runs a command inside the existing Nginx container.

`getent hosts app`

Queries the system name-resolution database for the hostname `app`.

A successful result proves that Docker DNS can resolve the backend service name.

---

### Direct Backend Connectivity

From the Nginx container:

```bash
docker compose exec nginx wget -qO- http://app:8000/health
```

`wget`

Makes an HTTP request.

`-q`

Quiet mode.

`-O-`

Writes the downloaded response to standard output instead of saving it to a file.

This test bypasses Nginx proxying and verifies that:

```text
Nginx container → Docker network → Python backend
```

is working.

---

### Host TCP Listener

On macOS:

```bash
lsof -nP -iTCP:8080 -sTCP:LISTEN
```

`lsof`

Lists open files and network sockets.

`-n`

Prevents hostname resolution.

`-P`

Displays numeric port numbers instead of service names.

`-iTCP:8080`

Filters for TCP port 8080.

`-sTCP:LISTEN`

Shows only listening TCP sockets.

This verifies that something on the host is accepting connections on port `8080`.

---

# Controlled Failure

The Nginx upstream was intentionally changed from:

```text
app:8000
```

to:

```text
app:8001
```

The backend itself continued listening on:

```text
8000
```

After restarting Nginx, the client request returned:

```text
HTTP/1.1 502 Bad Gateway
```

---

## Investigation

The troubleshooting process checked each layer independently.

### 1. Container State

```bash
docker compose ps
```

Both containers remained running.

This ruled out a simple container shutdown.

---

### 2. Host Listener

Port `8080` remained in the `LISTEN` state.

This showed that the host-to-Nginx entry point was still available.

---

### 3. Docker DNS

The hostname:

```text
app
```

still resolved correctly from the Nginx container.

This ruled out Docker DNS failure.

---

### 4. Direct Backend Connectivity

A direct request to:

```text
http://app:8000/health
```

still returned a healthy response.

This proved that:

* the backend process was running
* Docker networking was working
* the backend was listening on port 8000

---

### 5. Nginx Error Logs

Nginx reported:

```text
connect() failed (111: Connection refused) while connecting to upstream
```

and attempted to reach:

```text
app:8001
```

This strongly narrowed the failure domain to the reverse-proxy upstream configuration.

---

### 6. Configuration Syntax Validation

The configuration was checked with:

```bash
nginx -t
```

The syntax test succeeded.

This demonstrated an important lesson:

```text
Syntax-valid ≠ Operationally-correct
```

The configuration file could be syntactically valid while still containing an incorrect backend port.

---

### 7. Effective Configuration

The active configuration was inspected with:

```bash
nginx -T
```

This confirmed that Nginx had loaded:

```text
app:8001
```

rather than the intended:

```text
app:8000
```

---

# Root Cause

The root cause was an incorrect reverse-proxy upstream port.

Configured:

```text
app:8001
```

Actual backend listener:

```text
app:8000
```

The resulting request path was:

```text
Client
  ↓
Nginx
  ↓
app:8001
  ↓
Connection Refused
  ↓
HTTP 502
```

---

# Remediation

The Nginx upstream configuration was restored to:

```text
app:8000
```

The configuration was validated again before functional testing.

A secondary Docker bind-mount issue occurred during remediation after the host-side configuration file was replaced.

The Nginx container was recreated using Docker Compose to restore the expected bind-mounted configuration.

This secondary issue was separate from the original HTTP 502 root cause.

---

# Verification

The original client request was repeated:

```bash
curl -i http://localhost:8080/health
```

Result:

```text
HTTP/1.1 200 OK
```

This verified end-to-end recovery.

The validation sequence therefore became:

```text
Failure reproduced
      ↓
Dependencies tested
      ↓
Failure domain isolated
      ↓
Root cause identified
      ↓
Configuration corrected
      ↓
Original request repeated
      ↓
HTTP 200 verified
```

---

## Key Lessons

* A running container does not prove that the complete service is healthy.
* HTTP 502 is a symptom, not the root cause.
* Troubleshooting should validate each dependency independently.
* DNS success does not guarantee TCP connectivity.
* Configuration syntax validation does not prove operational correctness.
* Logs are most useful when correlated with network and configuration evidence.
* Verification should repeat the original failing condition after remediation.

---

## Related Evidence

Detailed investigation evidence:

`../../evidence/day01-network-service-incident.md`

Automation evidence:

`../../evidence/day01-health-check-automation.md`

Interview notes:

`../../interview-notes/network-service-troubleshooting.md`
