import os, json
from http.server import HTTPServer, BaseHTTPRequestHandler
import pymssql

APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")
CONN_STR = os.getenv("ConnectionStrings__DefaultConnection", "")

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "Healthy"})
        elif self.path == "/version":
            self._send_json(200, {"name": "IsLabApp", "version": APP_VERSION})
        elif self.path == "/db/ping":
            try:
                params = dict(item.split("=", 1) for item in CONN_STR.split(";") if "=" in item)
                server = params.get("Server", "mssql")
                user = params.get("User Id", "sa")
                pwd = params.get("Password", "")
                db = params.get("Database", "IsLabDb")
                conn = pymssql.connect(server=server, user=user, password=pwd, database=db, timeout=5)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM Notes")
                count = cursor.fetchone()[0]
                conn.close()
                self._send_json(200, {"database": "Healthy", "status": "Connected", "notes_count": count})
            except Exception as e:
                self._send_json(500, {"database": "Unhealthy", "status": "Error", "error": str(e)})
        else:
            self._send_json(404, {"error": "Not Found"})

    def log_message(self, format, *args):
        print(f"[{APP_VERSION}] {args[0]} {args[1]} -> {args[2]}")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 5000), Handler)
    print(f"Starting IsLabApp {APP_VERSION} on port 5000...")
    server.serve_forever()
