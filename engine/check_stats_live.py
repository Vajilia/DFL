"""The Statistics tab on the live page: it downloads each finished game's file from the feed, replays it, and the tables fill in (a league 30 hours in)."""
import os, sys, time, json, threading, functools, http.server, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live as L, build_site
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP the live statistics are not checked here (playwright is not installed)"); sys.exit(0)
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok: failures.append(name)
root = tempfile.mkdtemp()
build_site.build(os.path.join(root, "index.html"), 7, live=True)
now = int(time.time() * 1000)
meta = dict(seed=7, epoch_ms=now - 30 * 3600 * 1000, pacing="blocks", real_per_game=L.BLOCK_REAL_PER_GAME, halftime=L.HALFTIME_PAUSE, parity="tight", rules=2)
out = os.path.join(root, "live"); L.write_json(out + "/meta.json", meta)
L.Runner(out, 7, meta["epoch_ms"], meta).tick(now)
R = json.load(open(out + "/results.json"))
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=root))
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
with sync_playwright() as pw:
    br = pw.chromium.launch(); pg = br.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url + "#stats-team"); pg.wait_for_timeout(7000)
    prog = pg.inner_text("#sprog"); rows = pg.eval_on_selector_all("#sbody tbody tr", "e=>e.length")
    n_reg = pg.evaluate("statGames('reg').length")
    pg.goto(url + "#stats-player"); pg.wait_for_timeout(2500)
    prow = pg.eval_on_selector_all("#sbody tbody tr", "e=>e.length")
    pg.goto(url + "#live"); pg.wait_for_timeout(2500)
    n8 = pg.eval_on_selector_all("#app a.gamelink", "e=>e.length")
    pg.click("[data-more]"); pg.wait_for_timeout(500)
    n28 = pg.eval_on_selector_all("#app a.gamelink", "e=>e.length")
    br.close()
check("live page: finished games are not capped at the latest 8; 'Show 20 more' reveals earlier ones", n28 - n8 == 20 and n8 >= 9, f"{n8} -> {n28}")
check("the feed keeps each year's schedule and results", os.path.exists(out + "/season_1.json") and os.path.exists(out + "/results_1.json") or os.path.exists(out + f"/season_{R['year']}.json") and os.path.exists(out + f"/results_{R['year']}.json"))
check("live statistics: the team table lists the 40 clubs once the finished games are downloaded", rows == 40 and f"{n_reg} finished games counted" in prog and len(R["final"]) >= n_reg > 100, f"{rows} {prog} {n_reg}")
check("live statistics: the player table fills in and there are no script errors", prow > 20 and not errs, f"{prow} {errs[:2]}")
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED"))
sys.exit(1 if failures else 0)
