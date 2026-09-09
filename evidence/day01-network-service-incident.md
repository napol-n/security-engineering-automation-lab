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