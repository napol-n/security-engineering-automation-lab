from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket


class RequestHandler(BaseHTTPRequestHandler):

    def send_json(self, status_code, payload):
        body = json.dumps(payload, indent=2).encode()

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(
                200,
                {
                    "status": "healthy",
                    "service": "security-engineering-backend",
                    "hostname": socket.gethostname()
                },
            )

        elif self.path == "/":
            self.send_json(
                200,
                {
                    "message": "Security Engineering Lab",
                    "backend": "python",
                    "status": "running"
                },
            )

        else:
            self.send_json(
                404,
                {
                    "error": "not found",
                    "path": self.path
                },
            )


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), RequestHandler)

    print("Backend listening on 0.0.0.0:8000", flush=True)

    server.serve_forever()
