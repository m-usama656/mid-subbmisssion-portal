"""Local HTTP receiver: saves every posted test report as test-report.json."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 5001


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Added to prevent 501 errors if opened in a browser."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<h3>Test Report Receiver is Running!</h3>"
            b"<p>Waiting for GitHub Actions POST requests at <code>/report</code>.</p>"
        )

    def do_POST(self):
        if self.path != "/report":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
        except ValueError:
            self.send_error(400, "Invalid JSON")
            return
        with open("test-report.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("Saved test-report.json ->", data.get("overall_status"), str(data.get("commit_sha", ""))[:7])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"saved")

    def log_message(self, fmt, *args):
        pass  # keep the console readable


if __name__ == "__main__":
    print(f"Receiver listening on http://127.0.0.1:{PORT}/report  (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()