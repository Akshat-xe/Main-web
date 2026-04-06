#!/usr/bin/env python3
"""Serve the EVERSTAR static site from ./site (index at /)."""
import errno
import http.server
import os
import socketserver
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
HOST = os.environ.get("HOST", "127.0.0.1")
os.chdir(SITE)


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".json": "application/json",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
    }

    def end_headers(self):
        # Cache static assets for 30 days
        path = self.path.lower()
        if path.endswith(('.js', '.css', '.webp', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.woff', '.woff2', '.ttf')):
            self.send_header("Cache-Control", "public, max-age=2592000")
        else:
            # HTML pages: revalidate every hour
            self.send_header("Cache-Control", "public, max-age=3600, must-revalidate")
        super().end_headers()

    def do_GET(self):
        if self.path in ("/", ""):
            if (SITE / "everstart.html").is_file():
                self.path = "/everstart.html"
            elif (SITE / "main page.html").is_file():
                self.path = "/main page.html"
            elif (SITE / "index.html").is_file():
                self.path = "/index.html"
        return super().do_GET()

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")


if __name__ == "__main__":
    if not SITE.is_dir():
        raise SystemExit(f"Missing {SITE} — run: python3 tools/build_site.py")
    start = int(os.environ.get("PORT", "8080"))
    for port in range(start, start + 100):
        try:
            httpd = ReusableTCPServer((HOST, port), Handler)
            break
        except OSError as e:
            if e.errno != errno.EADDRINUSE:
                raise
    else:
        raise SystemExit(
            f"No free port in {start}–{start + 99} — stop other servers or set PORT."
        )
    if port != start:
        print(f"Port {start} is in use — using {port} instead.")
    with httpd:
        print(f"EVERSTAR → http://{HOST}:{port}/  (root: {SITE})")
        httpd.serve_forever()
