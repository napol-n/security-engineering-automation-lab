# Linux Process and Service Troubleshooting

## Explain in 30 Seconds

I simulated a Linux application-process failure inside a Docker container. The container remained Up, but the Python service stopped producing heartbeat logs.

I used `pgrep` and `ps` to confirm that the application process was missing, while the container's main process was still running. I restarted the application using the intended non-root service account and verified recovery by confirming a new PID and resumed heartbeat logs.

## How I Tested It

I used:

* `ps -ef` to inspect the process table
* `pgrep -af` to locate the application process
* PID inspection to identify the running service
* `SIGTERM` to simulate controlled process termination
* application logs to verify functional failure
* a process restart followed by log verification

## Evidence

`evidence/day02-linux-process-incident.md`

## Security / Operational Impact

Monitoring only container or host availability can miss application-level failures.

Service monitoring should verify both process state and actual application functionality.

## Remediation

Restart the failed application using the correct service identity and verify both process presence and functional activity.

## Interview Questions

Q: What is the difference between a running container and a healthy service?

A: A container can remain running because its primary process is still alive while another application process inside it has stopped. I therefore verify both the process state and the application's actual functionality.

Q: What is the difference between SIGTERM and SIGKILL?

A: SIGTERM requests a graceful shutdown and can be handled by the application. SIGKILL forces the kernel to terminate the process immediately and cannot be handled or ignored, so I prefer SIGTERM first.

Q: What does `pgrep` exit code 1 mean?

A: It means no process matched the supplied search pattern.

Q: Why did the PID change from 13 to 80?

A: PID values identify individual runtime process instances. Restarting the application created a new process, so the operating system assigned a different PID.

Q: Why did you check the heartbeat log after restarting the process?

A: Process presence alone does not prove that the application is functioning correctly. The resumed heartbeat demonstrated that the service had returned to its expected operational behavior.
