## Healthy Baseline

### Service State

Both application and Nginx containers were running.

### Application Listener

The Python backend reported:

`Backend listening on 0.0.0.0:8000`

### External HTTP Verification

Request:

`curl -i http://localhost:8080/health`

Result:

`HTTP/1.1 200 OK`

### Internal Service Verification

Nginx could communicate directly with:

`app:8000`

### DNS Verification

Docker DNS resolved:

`app → 172.18.0.2`

### Host Port Verification

Docker Desktop was listening on host TCP port 8080.

### Baseline Conclusion

The complete request path was operational:

Client → Docker Port 8080 → Nginx → Docker Network → Python App Port 8000

This healthy baseline will be used for comparison during the simulated service incident.

## Simulated Incident

### Problem

The previously healthy service began returning:

`HTTP/1.1 502 Bad Gateway`

The incident was intentionally introduced in the authorized local lab to practice systematic service troubleshooting.

### Investigation

#### 1. Container State

Both the Nginx proxy and Python backend containers remained in the `Up` state.

This ruled out an obvious container crash but did not prove that application communication was healthy.

#### 2. Host Port

TCP port `8080` remained in the `LISTEN` state through Docker Desktop.

This confirmed that the host-facing service path was still available.

#### 3. DNS Resolution

From the Nginx container:

`app` resolved successfully to `172.18.0.2`.

This ruled out Docker service-name resolution as the cause.

#### 4. Backend Verification

A direct request from the Nginx container to:

`http://app:8000/health`

returned a healthy application response.

This verified:

* Docker DNS
* container network connectivity
* TCP port 8000
* Python backend availability
* HTTP application functionality

#### 5. Proxy Logs

Nginx reported:

`connect() failed (111: Connection refused) while connecting to upstream`

The upstream destination was:

`172.18.0.2:8001`

while the backend application was verified to be listening on port `8000`.

### Root Cause

The Nginx upstream configuration referenced backend port `8001`, while the Python application was listening on port `8000`.

The resulting port mismatch caused the proxy connection to be refused and Nginx returned HTTP 502 to the client.

### Root Cause Classification

Configuration error / service dependency mismatch.

### Key Observation

The Nginx configuration remained syntactically valid. The failure was therefore a runtime configuration problem rather than a configuration syntax error.

### Impact

Requests routed through the reverse proxy could not reach the backend application, resulting in service unavailability to clients.

The backend application itself remained operational.
