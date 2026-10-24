from http.server import BaseHTTPRequestHandler, HTTPServer
import json

def assess_request(text):
    text = text.lower()

    emergency_terms = [
        "not breathing", "unconscious", "severe bleeding",
        "chest pain", "stroke", "suicide", "overdose"
    ]

    if any(term in text for term in emergency_terms):
        return {
            "route": "EMERGENCY_HELP",
            "urgency": "emergency",
            "message": "Seek emergency medical help now. Call 112 in India or your local emergency number.",
            "needs_human_review": True
        }

    return {
        "route": "CARE_NAVIGATION",
        "urgency": "needs_assessment",
        "message": "More information is needed before suggesting an appropriate care option.",
        "needs_human_review": True
    }

class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.send_json(200, {
                "app": "SwasthyaAI",
                "status": "running",
                "mode": "offline prototype"
            })
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/assess":
            self.send_json(404, {"error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length))
            text = data.get("text", "")

            if not isinstance(text, str) or not text.strip():
                self.send_json(400, {"error": "Please provide non-empty text"})
                return

            self.send_json(200, assess_request(text))
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"error": "Invalid JSON"})

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), Handler)
    print("SwasthyaAI offline prototype running at http://127.0.0.1:8000")
    server.serve_forever()
