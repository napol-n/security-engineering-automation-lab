# Network and Service Troubleshooting

## Explain in 30 Seconds

Before troubleshooting a service failure, I validate the environment and identify the layers involved, including the host, process, port, container, network, DNS, application, and HTTP service.

I collect evidence before modifying configuration so I can distinguish the symptom from the actual root cause.

## How It Works

Troubleshooting follows the dependency chain from the client toward the backend service.

## How I Tested It

I validated:

- operating system architecture
- Python runtime
- Docker engine
- Docker Compose
- HTTP tooling
- DNS tooling
- TLS tooling

## Evidence

`evidence/day01-environment.md`

## Security Impact

Environment and dependency awareness helps distinguish application failures, network failures, and configuration issues during security investigations.

## Remediation

Not applicable yet. Service failure remediation will be documented during Lab 01.

## Interview Questions

### Q: Why validate the environment before troubleshooting?

A:

I want to reduce uncertainty before modifying the system. I confirm the architecture, runtime, services, and diagnostic tools first so I can distinguish an application issue from an environment or dependency issue.

## 502 Bad Gateway Case

### Explain in 30 Seconds

In my network troubleshooting lab, Nginx returned HTTP 502 even though both containers were running. I verified the host listener, Docker DNS, and backend connectivity and confirmed that the backend was healthy on port 8000.

The Nginx logs showed a connection refusal against upstream port 8001. I identified a proxy-to-backend port mismatch, corrected the configuration to port 8000, validated the configuration, and retested the original endpoint until it returned HTTP 200.

### How I Tested It

I used:

* `docker compose ps` for service state
* `lsof` for host listening ports
* `getent hosts` for Docker DNS resolution
* direct HTTP testing from Nginx to the backend
* Nginx access and error logs
* `nginx -t` for syntax validation
* end-to-end HTTP retesting

### Security / Operational Impact

The reverse proxy remained available while its upstream dependency was incorrectly configured.

This caused application unavailability even though container-level monitoring showed both services as running.

### Remediation

The incorrect upstream port was corrected, the configuration was validated, and the original failing request was repeated to verify recovery.

### Interview Questions

Q: Why didn't you assume Nginx itself was down when you saw HTTP 502?

A: Because receiving an HTTP response from Nginx already showed that the client could reach the proxy. I focused next on the upstream dependency path.

Q: What did `Connection refused` tell you?

A: It indicated that the destination was reachable but the TCP connection was not being accepted on the requested port. That directed the investigation toward the listening port and upstream configuration.

Q: Why wasn't `nginx -t` enough to prove the problem was fixed?

A: `nginx -t` validates configuration syntax. It does not prove that the configured backend exists or that the complete application path works, so I also performed an end-to-end HTTP retest.
