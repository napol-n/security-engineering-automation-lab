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

The simulated Nginx upstream port mismatch was remediated by restoring the correct backend port, validating the effective configuration, and repeating the original HTTP request to verify recovery.

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

## Health Check Automation

### Explain in 30 Seconds

After manually troubleshooting and recovering the service, I automated the verification process with Python.

The script sends an HTTP request to the health endpoint, validates the HTTP status, parses the JSON response, checks the application health state, and returns exit code 0 for healthy or 1 for failure. This makes the check usable by shell automation, CI/CD, or monitoring workflows.

### How I Tested It

Healthy endpoint:

`http://localhost:8080/health`

Result:

`HTTP 200`, application status `healthy`, exit code `0`.

Failure endpoint:

`http://localhost:8080/not-found`

Result:

`HTTP 404`, exit code `1`.

### Evidence

`scripts/health_check.py`

`evidence/day01-health-check-automation.md`

### Security / Operational Impact

Automated service verification can identify application-path failures that basic process or container monitoring may miss.

### Interview Questions

Q: Why didn't you automate the troubleshooting from the beginning?

A: I wanted to understand the service dependencies and failure modes first. After establishing the healthy baseline, investigating the failure, identifying the root cause, and verifying the remediation manually, I automated the repeatable verification step.

Q: Why use exit codes?

A: Exit codes provide a machine-readable result. Exit code 0 represents success and a non-zero code represents failure, allowing shell scripts, CI/CD pipelines, and monitoring systems to make decisions based on the result.

Q: Why check the JSON health status if HTTP 200 already succeeded?

A: HTTP 200 proves the endpoint responded successfully at the HTTP layer, but it does not necessarily prove that the application considers itself healthy. Checking both provides stronger application-level validation.
