"""The website's pause switch (2026-10-13): only a logged-in page's own calls change anything, a legacy league cannot be paused, and the runner obeys the switch.

    python engine/check_control.py
"""
import json
import os
import sys
import tempfile
import threading
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import control_server as C
import live as L

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def call(port, method, path, headers=None, body=b"{}"):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=body if method == "POST" else None, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


OK = {"X-DFL": "1", "Content-Type": "application/json"}
out = tempfile.mkdtemp()
OPEN = 1_800_000_000_000
meta = dict(seed=7, epoch_ms=OPEN, pacing="blocks", real_per_game=L.BLOCK_REAL_PER_GAME, halftime=L.HALFTIME_PAUSE)
json.dump(meta, open(os.path.join(out, "meta.json"), "w"))
srv = C.serve(out, 0)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

check("the state of a new league: running, pausable", call(port, "GET", "/api/state") == (200, dict(paused=False, pacing="blocks", pausable=True)))
check("a call without the header is refused and changes nothing", call(port, "POST", "/api/pause", {"Content-Type": "application/json"})[0] == 403 and not os.path.exists(os.path.join(out, "control.json")))
check("a call without a JSON content type is refused (a plain form from another site)", call(port, "POST", "/api/pause", {"X-DFL": "1", "Content-Type": "text/plain"})[0] == 403 and not os.path.exists(os.path.join(out, "control.json")))
check("a call that names another site as its origin is refused", call(port, "POST", "/api/pause", dict(OK, Origin="https://evil.example", Host="league.example"))[0] == 403)
check("pause writes control.json and reports it", call(port, "POST", "/api/pause", OK) == (200, dict(paused=True, pacing="blocks", pausable=True)) and json.load(open(os.path.join(out, "control.json"))) == {"paused": True})
check("the state then says paused", call(port, "GET", "/api/state")[1]["paused"] is True)
r = L.Runner(out, 7, OPEN, dict(meta))
a = r.tick(OPEN + 10 * 60000)
b = r.tick(OPEN + 3 * 3600000)
check("the runner obeys the switch: the league stands still", a["paused"] and b["paused"] and a["t"] == b["t"])
check("resume writes control.json and the runner picks up where it stopped", call(port, "POST", "/api/resume", OK)[1]["paused"] is False and r.tick(OPEN + 3 * 3600000 + 60000)["t"] == a["t"] and not r.paused())
check("unknown paths are 404", call(port, "GET", "/api/other")[0] == 404 and call(port, "POST", "/api/other", OK)[0] == 404)
legacy = tempfile.mkdtemp()
json.dump(dict(seed=7, epoch_ms=OPEN), open(os.path.join(legacy, "meta.json"), "w"))
srv2 = C.serve(legacy, 0)
threading.Thread(target=srv2.serve_forever, daemon=True).start()
p2 = srv2.server_address[1]
check("a legacy league reports it cannot be paused, and a pause is refused", call(p2, "GET", "/api/state")[1]["pausable"] is False and call(p2, "POST", "/api/pause", OK)[0] == 409 and not os.path.exists(os.path.join(legacy, "control.json")))
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
