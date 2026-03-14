#!/usr/bin/env python3
"""Intentionally insecure local target server for VulnSight testing.

This service is for local security-tool testing only. Do not expose it publicly.
"""

from __future__ import annotations

import argparse
import html
import json
import sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


def init_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
            """
        )
        cur.execute("DELETE FROM products")
        cur.executemany(
            "INSERT INTO products (id, name, price) VALUES (?, ?, ?)",
            [
                (1, "Keyboard", 49.99),
                (2, "Mouse", 19.99),
                (3, "Monitor", 199.99),
            ],
        )
        conn.commit()
    finally:
        conn.close()


class InsecureTestHandler(BaseHTTPRequestHandler):
    server_version = "Apache/2.4.49"
    sys_version = ""

    def _set_headers(self, status: int = 200, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        # Intentionally weak cookie flags for scanner findings.
        self.send_header("Set-Cookie", "session=dev-session-token")
        self.send_header("X-Powered-By", "PHP/5.6.40")
        self.end_headers()

    def _write_html(self, body: str, status: int = 200) -> None:
        self._set_headers(status=status)
        self.wfile.write(body.encode("utf-8"))

    def _write_json(self, payload: dict, status: int = 200) -> None:
        self._set_headers(status=status, content_type="application/json")
        self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))

    def log_message(self, fmt: str, *args) -> None:
        # Keep default terminal logging concise and timestamped by HTTP server.
        super().log_message(fmt, *args)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            page = """
<!doctype html>
<html>
  <head><title>VulnSight Test Target</title></head>
  <body>
    <h1>VulnSight Test Target</h1>
    <p>Intentionally vulnerable local app for scanner validation.</p>
    <ul>
      <li><a href=\"/search?q=hello\">Reflected search</a></li>
      <li><a href=\"/product?id=1\">Product endpoint (SQL-like test)</a></li>
      <li><a href=\"/admin/\">Admin panel</a></li>
      <li><a href=\"/.env\">Leaked .env</a></li>
      <li><a href=\"/.git/config\">Leaked git config</a></li>
    </ul>
  </body>
</html>
            """.strip()
            self._write_html(page)
            return

        if path == "/search":
            # Intentionally reflected output to trigger scanner checks.
            term = query.get("q", [""])[0]
            page = f"<h2>Search Results</h2><p>You searched for: {term}</p>"
            self._write_html(page)
            return

        if path == "/product":
            # Intentionally unsafe SQL string concatenation for local testing.
            raw_id = query.get("id", ["1"])[0]
            conn = sqlite3.connect(self.server.db_path)
            try:
                cur = conn.cursor()
                sql = f"SELECT id, name, price FROM products WHERE id = {raw_id}"
                rows = cur.execute(sql).fetchall()
                self._write_json({"query": sql, "rows": rows})
            except Exception as exc:
                self._write_json(
                    {
                        "error": str(exc),
                        "hint": "Input is used directly in SQL query (intentional for testing).",
                    },
                    status=500,
                )
            finally:
                conn.close()
            return

        if path == "/admin/":
            self._write_html("<h1>Admin Panel</h1><p>Default credentials often used here.</p>")
            return

        if path == "/.env":
            self._set_headers(content_type="text/plain; charset=utf-8")
            self.wfile.write(
                b"DB_USER=dev\nDB_PASS=devpassword\nJWT_SECRET=super-secret-test-key\n"
            )
            return

        if path == "/.git/config":
            self._set_headers(content_type="text/plain; charset=utf-8")
            self.wfile.write(
                b"[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n[remote \"origin\"]\n\turl = https://example.invalid/repo.git\n"
            )
            return

        if path == "/healthz":
            self._write_json({"status": "ok"})
            return

        self._write_html("<h1>Not Found</h1>", status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/login":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            data = parse_qs(body)
            user = html.escape(data.get("username", [""])[0])
            # Intentionally weak auth behavior for scanner test surface.
            self._write_json({"message": f"Welcome {user}", "authenticated": True})
            return

        self._write_html("<h1>Not Found</h1>", status=HTTPStatus.NOT_FOUND)


class InsecureHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], handler_cls, db_path: str):
        super().__init__(server_address, handler_cls)
        self.db_path = db_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VulnSight local test target server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", default=8081, type=int, help="Bind port (default: 8081)")
    parser.add_argument(
        "--db-path",
        default="test_target/test_target.db",
        help="SQLite database path (default: test_target/test_target.db)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_db(args.db_path)
    server = InsecureHTTPServer((args.host, args.port), InsecureTestHandler, args.db_path)
    print(f"[test-target] Serving on http://{args.host}:{args.port}")
    print("[test-target] Suggested VulnSight targets:")
    print(f"  - http://{args.host}:{args.port}")
    print(f"  - http://{args.host}:{args.port}/product?id=1")
    server.serve_forever()


if __name__ == "__main__":
    main()
