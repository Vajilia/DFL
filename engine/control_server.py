"""The league's pause switch for the website (2026-10-13). A tiny local web service: the page's Pause / Resume button calls it, it writes control.json into the live feed
folder, and the runner (live.py) reads that file on every tick. It listens on 127.0.0.1 only; Caddy forwards /api/* to it AFTER the website login, so only someone who is
logged in to the site can reach it.

    GET  /api/state    -> {"paused": bool, "pacing": "blocks"|"legacy", "pausable": bool}
    POST /api/pause    -> same, after pausing   (needs the header  X-DFL: 1  and a JSON content type, so a page on another site cannot trigger it)
    POST /api/resume   -> same, after resuming

Only a blocks league can be paused (a legacy league's clock is the calendar). Run:  python engine/control_server.py --out /var/www/dfl/live [--port 8081]
"""
import argparse
import json
import os
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_json(path, obj):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f)
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def state(out):
    pacing = read_json(os.path.join(out, "meta.json")).get("pacing", "legacy")
    return dict(paused=bool(read_json(os.path.join(out, "control.json")).get("paused")), pacing=pacing, pausable=pacing == "blocks")


def make_handler(out):
    class H(BaseHTTPRequestHandler):
        server_version = "dfl-control"

        def log_message(self, *a):          # keep the journal quiet
            pass

        def _send(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path.split("?")[0] == "/api/state":
                return self._send(200, state(out))
            self._send(404, dict(error="not found"))

        def do_POST(self):
            path = self.path.split("?")[0]
            if path not in ("/api/pause", "/api/resume"):
                return self._send(404, dict(error="not found"))
            if self.headers.get("X-DFL") != "1" or "application/json" not in (self.headers.get("Content-Type") or ""):
                return self._send(403, dict(error="missing header"))
            origin, host = self.headers.get("Origin"), self.headers.get("Host")
            if origin and host and origin.split("://", 1)[-1] != host:
                return self._send(403, dict(error="another site"))
            n = int(self.headers.get("Content-Length") or 0)
            if n:
                self.rfile.read(min(n, 1024))
            s = state(out)
            if not s["pausable"]:
                return self._send(409, dict(s, error="this league cannot be paused"))
            write_json(os.path.join(out, "control.json"), dict(paused=path == "/api/pause"))
            self._send(200, state(out))
    return H


def serve(out, port, host="127.0.0.1"):
    return ThreadingHTTPServer((host, port), make_handler(out))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=8081)
    a = ap.parse_args(argv)
    srv = serve(a.out, a.port)
    print(f"pause switch on 127.0.0.1:{a.port} for {a.out}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
