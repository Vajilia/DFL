"""Past seasons on the live page: the feed keeps every year's schedule and results, and the page can look back at a finished season (standings, schedule, box scores, statistics) and return to the live one."""
import os, sys, time, json, threading, functools, http.server, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live as L, build_site
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP past seasons are not checked here (playwright is not installed)"); sys.exit(0)
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok: failures.append(name)
root = tempfile.mkdtemp()
build_site.build(os.path.join(root, "index.html"), 7, live=True, rules=2)
H = 3600 * 1000
meta = dict(seed=7, epoch_ms=0, pacing="blocks", real_per_game=L.BLOCK_REAL_PER_GAME, halftime=L.HALFTIME_PAUSE, parity="tight", rules=2)
now = int(time.time() * 1000); meta["epoch_ms"] = now - 200 * H
out = os.path.join(root, "live"); L.write_json(out + "/meta.json", meta)
run = L.Runner(out, 7, meta["epoch_ms"], meta)
yh = None
for h in range(1, 201, 2):                                  # the league lives through its hours, a tick every two
    run.tick(meta["epoch_ms"] + h * H)
    if yh is None and os.path.exists(out + "/season.json"):
        yh = json.load(open(out + "/season.json")).get("year_hours")
run.tick(now)
R = json.load(open(out + "/results.json")); hist = R["history"]
print("league year", R["year"], "history", hist, "year_hours", yh)
check("a season has been played out and the feed kept its files", R["year"] >= 2 and os.path.exists(out + "/season_1.json") and os.path.exists(out + "/results_1.json"), f"year {R['year']}")
R1 = json.load(open(out + "/results_1.json"))
check("the kept results of year 1 are final: every game decided, a champion named", R1.get("champion") is not None and len(R1["final"]) >= 360 and not R1["live"], f"{len(R1['final'])} {R1.get('champion')}")
gfiles = [json.load(open(os.path.join(out, "g", f))) for f in os.listdir(out + "/g") if f.startswith("1_")]
check("every game file of the finished year is complete, none left mid-game", len(gfiles) == len(R1["final"]) and not any(b.get("live") for b in gfiles), f"{len(gfiles)} files, {len(R1['final'])} finals")
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=root))
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
with sync_playwright() as pw:
    br = pw.chromium.launch(); pg = br.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url + "#seasons"); pg.wait_for_timeout(2500)
    tab = pg.inner_text("#tabs")
    rows = pg.eval_on_selector_all("#app tbody tr", "e=>e.length")
    check("the Seasons tab lists the season in progress and each finished one", "SEASONS" in tab.upper() and rows == 1 + len(hist) and pg.locator("a[href='#seasons-1']").count() == 1, f"{rows} {len(hist)}")
    cur_season = pg.evaluate("D.season"); cur_club = pg.evaluate("clubs.filter(c=>c.record.w+c.record.l+c.record.t>0).length")
    pg.click("a[href='#seasons-1']"); pg.wait_for_timeout(2500)
    s1 = pg.evaluate("D.season"); view = pg.evaluate("FEED.view"); h = pg.inner_text("#app")
    games = pg.evaluate("D.games.length"); fin = pg.evaluate("D.games.filter(g=>g.final).length")
    played = pg.evaluate("clubs.filter(c=>!c.exiled).reduce((a,c)=>a+c.record.w+c.record.l+c.record.t,0)")
    check("a finished season opens on its standings with a banner, every game final", view == 1 and s1 != cur_season and fin == games and "looking back at season" in h and "Back to live" in h, f"{view} {s1} {cur_season} {fin}/{games}")
    champ = hist[0]["champion"]
    check("its standings carry the champion and the full set of results", pg.evaluate("D.champion") == champ and played == 2 * fin, f"{pg.evaluate('D.champion')} {champ} {played} {fin}")
    gid = pg.evaluate("D.games.find(g=>g.final).id")
    pg.goto(url + "#game-" + gid); pg.wait_for_timeout(3000)
    gt = pg.inner_text("#app")
    check("a game of the past season opens as a final box score", "Final" in gt and "TEAM STATS" in gt.upper() and "Drive 1" in gt or "DRIVES" in gt.upper(), gt[:200])
    pg.goto(url + "#stats-team"); pg.wait_for_timeout(9000)
    prog = pg.inner_text("#sprog"); trows = pg.eval_on_selector_all("#sbody tbody tr", "e=>e.length")
    check("the statistics of the past season count its own games", trows >= 36 and f"{fin} finished games counted" in prog, f"{trows} {prog}")
    pg.click("#tabs a[href='#live']"); pg.wait_for_timeout(2500)
    back = pg.evaluate("[FEED.view, D.season]")
    check("Back to live returns to the current season", back[0] is None and back[1] == cur_season and "looking back" not in pg.inner_text("#app"), str(back))
    pg.goto(url + "#seasons-9"); pg.wait_for_timeout(2500)
    check("a season that does not exist says so instead of looping", "could not be loaded" in pg.inner_text("#app") and not errs, f"{errs[:2]}")
    br.close()
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED"))
sys.exit(1 if failures else 0)
