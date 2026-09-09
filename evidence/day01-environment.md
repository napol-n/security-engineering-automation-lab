# Day 1 — Environment Validation

## Objective

Validate the local environment required for the Security Engineering & Automation Lab.

## Host

- Platform: macOS
- Architecture: arm64 / Apple Silicon

## Tooling

| Tool | Version / Status |
|---|---|
| Git | 2.50.1 |
| Python | 3.9.6 |
| Docker | 29.7.2 |
| Docker Compose | v5.5.1 |
| Docker Engine | Running |
| curl | 8.7.1 |
| TLS Utility | LibreSSL 3.3.6 |
| DNS Utility | DiG 9.10.6 |

## Architecture Validation

Commands:

`uname -m`

Result:

`arm64`

`arch`

Result:

`arm64`

`file /usr/bin/curl`

Result:

The macOS curl binary is a universal Mach-O binary containing x86_64 and arm64e architectures.

## Analysis

The active shell environment is running natively on Apple Silicon.

The curl binary supporting both architectures is not treated as a fault because the host architecture is arm64 and networking functionality is operational.

## Environment Decision

Docker will provide an isolated and reproducible environment for network and service troubleshooting.

No Windows Server or additional x86 hardware is required for this lab.

## Verification

Docker Engine successfully responded to `docker info`.

## Lessons Learned

Validating architecture, runtime, container engine, and diagnostic utilities before troubleshooting reduces uncertainty when service failures occur later.
