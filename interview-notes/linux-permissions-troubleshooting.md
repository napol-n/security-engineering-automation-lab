# Linux Permission Troubleshooting

## Explain in 30 Seconds

I built a Linux service running as a non-root user and simulated a filesystem permission failure. The application could no longer write its log and returned a permission-denied error.

I verified the process identity and inspected every component of the filesystem path with `namei`. The log file itself was writable by the service user, but its parent directory had been changed to `root:root` with mode `700`. I restored the intended ownership and `750` permissions, reran the application as the non-root user, and verified that log writing and exit status returned to normal.

## How I Tested It

I used:

* `id` to verify process identity
* `ls -ld` to inspect directory ownership and permissions
* `namei -l` to inspect the complete filesystem path
* application exit codes to identify failure and recovery
* `tail` to verify actual log writes

## Evidence

`evidence/day02-linux-permission-incident.md`

## Security Impact

Incorrect ownership or permissions can cause service outages.

Overly permissive remediation such as `chmod 777` may restore functionality but unnecessarily increases access and violates least-privilege principles.

## Remediation

Restore the intended service account ownership and apply the minimum permissions necessary for the application to operate.

## Interview Questions

Q: Why could the application not write the file even though it owned `service.log`?

A: Linux must traverse every directory in a pathname before accessing the target file. The parent directory was owned by root with mode 700, so the application user had no execute permission on that directory and could not reach the file.

Q: What does the execute bit mean on a directory?

A: It allows a user to traverse the directory and access entries within it when the names are known.

Q: Why not use `chmod 777`?

A: It would grant read, write, and execute permissions to everyone. I prefer restoring the intended owner and minimum required permissions to preserve least privilege.

Q: What was useful about `namei -l`?

A: It displayed ownership and permissions for every component in the pathname, which made it clear that the failure was at the parent-directory layer rather than the final log file.
