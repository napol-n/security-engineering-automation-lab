# Day 2 — Linux System and Permission Troubleshooting

## Objective

Build a Linux service running as a non-root user, establish a healthy baseline, introduce a controlled filesystem permission failure, investigate the failure, remediate it, and verify recovery.

## Environment

- Container platform: Docker
- Operating system: Linux
- Architecture: aarch64
- Service user: `secsvc`
- UID: `1000`
- Application: `/opt/secsvc/service.py`
- Log directory: `/var/log/secsvc`
- Log file: `/var/log/secsvc/service.log`

## Healthy Baseline

### Container State

The Linux container was running successfully.

### Service Identity

The application user was:

`uid=1000(secsvc) gid=1000(secsvc)`

The application was executed explicitly as `secsvc`, not root.

### Log Directory

Ownership:

`secsvc:secsvc`

Permissions:

`drwxr-x---`

Equivalent numeric mode:

`750`

### Application Verification

Command:

`python /opt/secsvc/service.py --once`

Result:

`[OK] heartbeat written`

Exit code:

`0`

### Log Verification

The application successfully created heartbeat entries containing:

- timestamp
- process ID
- user ID
- health status

Example:

`pid=55 uid=1000 status=healthy`

## Healthy State Conclusion

The non-root service had sufficient permission to access its required log directory and successfully write application logs.
