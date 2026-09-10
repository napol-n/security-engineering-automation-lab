# Day 2 — Linux Process and Service Troubleshooting

## Objective

Simulate an application-process failure inside a running Linux container, investigate the difference between container state and application state, restart the service, and verify recovery.

## Healthy Baseline

The Linux container remained running with:

`sleep infinity`

as its main process.

The Python application was started separately as the non-root user:

`secsvc`

The application process was:

`PID 13`

Command:

`python /opt/secsvc/service.py --interval 5`

The application wrote a heartbeat to:

`/var/log/secsvc/service.log`

approximately every five seconds.

## Simulated Incident

The application process was terminated using:

`SIGTERM`

The signal was sent to:

`PID 13`

## Investigation

### Container State

The Docker container remained in the:

`Up`

state.

This demonstrated that container-level availability did not prove that the application process was still running.

### Process Verification

`pgrep` no longer returned the Python service process.

The process check returned exit code:

`1`

indicating that no matching process was found.

### Process Table

`ps -ef` showed the container's main process:

`sleep infinity`

but the Python application process was absent.

### Functional Verification

The service normally wrote heartbeat entries every five seconds.

After process termination, the latest heartbeat remained unchanged even after waiting longer than the configured interval.

The final heartbeat from the terminated process was associated with:

`pid=13`

This confirmed that application functionality had stopped.

## Root Cause

The Python application process had been terminated.

The Docker container itself remained running because the application's process was not the container's primary process.

## Root Cause Classification

Application process termination / service availability failure.

## Remediation

The application was restarted as the non-root service account:

`secsvc`

A new process was created with:

`PID 80`

## Verification

After restart:

* the Python process was visible again with `pgrep`
* the process ran as the intended service account
* heartbeat entries resumed
* the heartbeat interval returned to approximately five seconds
* new log entries contained `pid=80`

## Before and After

Before failure:

`PID 13 → heartbeat updating`

During failure:

`Container Up → application process missing → heartbeat stale`

After remediation:

`PID 80 → heartbeat updating`

## Lessons Learned

Container status alone is not sufficient for determining application health.

A container can remain operational while an application process inside it has stopped.

Process presence should be combined with functional checks such as log activity, application health endpoints, or other service-level verification.

A process ID is a runtime identifier and may change whenever an application is restarted.
