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

## Simulated Incident

### Problem

A previously healthy application running as the non-root user `secsvc` failed to write to:

`/var/log/secsvc/service.log`

The application returned:

`Permission denied`

Exit code:

`1`

## Investigation

### Process Identity

The application was confirmed to run as:

`uid=1000(secsvc) gid=1000(secsvc)`

This confirmed that the process was not running with root privileges.

### Filesystem Path Analysis

The complete filesystem path was inspected using `namei -l`.

The parent paths `/`, `/var`, and `/var/log` allowed traversal.

However:

`/var/log/secsvc`

had:

* Owner: `root`
* Group: `root`
* Mode: `700`
* Permissions: `rwx------`

The application user `secsvc` therefore had no execute/traverse permission on the log directory.

### File Observation

The existing `service.log` file remained owned by:

`secsvc:secsvc`

with mode:

`644`

However, correct file-level permissions were insufficient because the application could not traverse the parent directory.

## Root Cause

The log directory ownership and permissions had been changed from:

`secsvc:secsvc / 750`

to:

`root:root / 700`

This prevented the non-root application user from traversing the directory and accessing its log file.

## Root Cause Classification

Linux filesystem permission / ownership misconfiguration.

## Remediation

The intended ownership was restored:

`secsvc:secsvc`

The intended directory mode was restored:

`750`

This provided the service owner with the required access while avoiding unnecessarily broad permissions.

## Verification

The directory was re-inspected after remediation.

The application was then executed again as `secsvc`.

Before remediation:

`[FAIL] Permission denied`

Exit code:

`1`

After remediation:

`[OK] heartbeat written`

Exit code:

`0`

The application log contained a new heartbeat with:

`uid=1000 status=healthy`

## Lessons Learned

Linux file access depends on both the target file permissions and the permissions of every directory in the path.

For directories, the execute bit represents the ability to traverse the directory.

Checking only the final file can therefore miss the actual permission failure.

Using `chmod 777` would have restored access but violated least-privilege principles. Restoring the intended owner and minimum required permissions was the more appropriate remediation.
