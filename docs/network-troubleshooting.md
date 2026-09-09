# Network Troubleshooting

## Troubleshooting Model

When a network-facing service fails, investigate from the observable symptom toward the dependency layers.

1. Client request
2. HTTP response
3. Listening port
4. Service/process state
5. DNS/service discovery
6. Network connectivity
7. Backend application
8. Proxy/service logs
9. Configuration
10. Remediation and verification

## Principle

Do not change configuration based only on assumptions.

Collect evidence, form a hypothesis, test it, identify the root cause, remediate the issue, and verify recovery.
