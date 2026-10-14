"""A club's page keeps up with the league: the people and rosters of every year, each club's history, and how its coaches are doing.

  1  the live runner records every club's people and roster as each year begins, and how each club's year went when it ends (no change to a single game)
  2  on the page: a club's page shows the year on view (its roster and staff change from year to year), the season-by-season table, coaches judged by their results,
     the club's team statistics and each player's season line; a player has a page of her own, found by her id
  3  the founding season's page has the same sections from what it has

    python engine/check_team_pages.py
"""
import functools, http.server, json, os, sys, tempfile, threading, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site, live as L

failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok: failures.append(name)

# 1 ------------------------------------------------------------------------------------------------------------------------------
w = L.World(7, 0, pacing="blocks", rules=5)
s1 = L.Season(w, 1, start_ms=0, begin_ms=0); w.year, w.season = 1, s1
sf = s1.schedule_file(0); T1 = sf["teams"]
check("year 1 starts with the people and roster of all 48 clubs", len(T1) == 48 and all(len(t["p"]) == 5 and all(t["p"]) and 40 <= len(t["r"]) <= 60 for t in T1.values()), str(len(T1)))
found = w.founding_pids
check("a founding player's backstory is left out (the page has it), and every row has her id, name and position", all(len(r) == 10 for t in T1.values() for r in t["r"] if r[0] in found) and all(isinstance(r[0], int) and r[1] and r[2] for t in T1.values() for r in t["r"]))
sm = s1.summary()
check("the year's summary has all 48 clubs; the 8 in exile carry the Ambassador Season", len(sm) == 48 and sum(1 for r in sm.values() if r[7] == "exile") == 8, str(len(sm)))
act = {t: r for t, r in sm.items() if r[7] != "exile"}
check("every club that played has a full season, and points for equal points against across the league", all(r[0] + r[1] + r[2] == sum(1 for g in s1.res.games if str(g.home) == t or str(g.away) == t) for t, r in act.items()) and sum(r[3] for r in act.values()) == sum(r[4] for r in act.values()))
check("the coaches in the summary are the ones in the year's snapshot", all(sm[t][8] == T1[t]["p"][2][0] and sm[t][9] == T1[t]["p"][3][0] and sm[t][10] == T1[t]["p"][4][0] and sm[t][11] == T1[t]["p"][1][0] for t in sm))
w.history.append(dict(year=2000, champion=s1.res.champion, clubs=sm))
s2 = L.Season(w, 2, start_ms=1, begin_ms=1); T2 = s2.schedule_file(1)["teams"]
chg = sum(1 for t in T1 if [r[0] for r in T1[t]["r"]] != [r[0] for r in T2[t]["r"]]); new = [r for t in T2.values() for r in t["r"] if r[0] not in found]
check("the next year's rosters have changed (draft, retirements), and new players bring their own backstories (those who have one)", chg >= 40 and len(new) > 50 and sum(1 for r in new if len(r) == 11) >= 0.25 * len(new), f"{chg} clubs changed, {len(new)} new players, {sum(1 for r in new if len(r) == 11)} with a story")
w2 = L.World(7, 0, pacing="blocks", rules=5); a1 = L.Season(w2, 1, start_ms=0, begin_ms=0)
check("the same seed gives the same snapshot and summary", a1.snap == s1.snap and a1.summary() == sm)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP the page is not checked here (playwright is not installed)"); print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED")); sys.exit(1 if failures else 0)
def serve(root):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/index.html"

# 2 ------------------------------------------------------------------------------------------------------------------------------
root = tempfile.mkdtemp(); build_site.build(os.path.join(root, "index.html"), 7, live=True, rules=5)
H = 3600 * 1000; now = int(time.time() * 1000)
meta = dict(seed=7, epoch_ms=now - 150 * H, pacing="blocks", real_per_game=L.BLOCK_REAL_PER_GAME, halftime=L.HALFTIME_PAUSE, parity="tight", rules=5)
out = os.path.join(root, "live"); L.write_json(out + "/meta.json", meta)
run = L.Runner(out, 7, meta["epoch_ms"], meta)
for h in range(1, 151, 3): run.tick(meta["epoch_ms"] + h * H)
run.tick(now); url = serve(root)
R = json.load(open(out + "/results.json")); hist = R["history"]
check("two years or more have been played and the history carries each club's year", len(hist) >= 2 and all(len(x["clubs"]) == 48 for x in hist), str(len(hist)))
S1 = json.load(open(out + "/season_1.json")); S2 = json.load(open(out + "/season_2.json")); cur = json.load(open(out + "/season.json"))
check("each year's file keeps its own snapshot, and the current one is the latest", S1["teams"] == T1 and S2["teams"] != S1["teams"] and cur["teams"] == json.load(open(out + "/season_%d.json" % R["year"]))["teams"])
cid = next(t for t in S2["teams"] if hist[0]["clubs"][t][7] != "exile" and hist[1]["clubs"][t][7] != "exile")
with sync_playwright() as pw:
    br = pw.chromium.launch(); errs = []
    pg = br.new_page(viewport=dict(width=1100, height=900)); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(3500)
    ab = pg.evaluate("byId[%s].abbr" % cid)
    pg.evaluate("location.hash='#club-%s'" % ab); pg.wait_for_timeout(2500)
    ct = S2["teams"] if R["year"] == 2 else cur["teams"]
    names = pg.evaluate("byId[%s].roster.map(p => p.name)" % cid)
    check("the club page's roster is the year on view's: the snapshot of the current year", names == [r[1] for r in cur["teams"][cid]["r"]] and names != [r[1] for r in S1["teams"][cid]["r"]], str(names[:3]))
    hc = pg.evaluate("byId[%s].people.head_coach.name" % cid)
    check("and so are its coaches", hc == cur["teams"][cid]["p"][2][0], hc)
    rows = pg.evaluate("document.querySelectorAll('#app h2')"); sec = pg.evaluate("[...document.querySelectorAll('#app h2')].map(h => h.textContent.trim())")
    check("the page has coaching staff, season by season, team statistics, schedule and players", all(x in sec for x in ["Coaching staff", "Season by season", "Team statistics", "Schedule and results", "Players"]), str(sec))
    nrow = pg.evaluate("document.querySelectorAll('#app table')[0].closest('.stack') && [...document.querySelectorAll('#app h2')].find(h => h.textContent.trim() === 'Season by season').parentElement.querySelectorAll('tbody tr').length")
    check("season by season has this year and every year over", nrow == len(hist) + 1, f"{nrow} {len(hist)}")
    # the head coach's record with the DFL equals her seasons in the history, added up
    cards = pg.evaluate("[...document.querySelectorAll('#app .card')].filter(c => c.querySelector('.eyebrow') && c.querySelector('.eyebrow').textContent === 'Head coach').map(c => c.innerText.replace(/\\s+/g, ' '))")
    wl = [0, 0, 0]
    for x in hist:
        for r in x["clubs"].values():
            if r[8] == hc and r[7] != "exile": wl = [wl[0] + r[0], wl[1] + r[1], wl[2] + r[2]]
    cur_rec = pg.evaluate("(() => { const r = byId[%s].record; return [r.w, r.l, r.t]; })()" % cid)
    if hc == cur["teams"][cid]["p"][2][0] and not any(x["year"] == pg.evaluate("D.season") for x in hist): wl = [wl[0] + cur_rec[0], wl[1] + cur_rec[1], wl[2] + cur_rec[2]]
    txt = f"{wl[0]}-{wl[1]}" + (f"-{wl[2]}" if wl[2] else "")
    check("the head coach's record with the DFL is her seasons added up", cards and (txt in cards[0] or sum(wl) == 0), f"{txt} | {cards[0] if cards else ''}"[:200])
    oc = pg.evaluate("[...document.querySelectorAll('#app .card')].filter(c => c.querySelector('.eyebrow') && c.querySelector('.eyebrow').textContent === 'Offensive coordinator').map(c => c.innerText.replace(/\\s+/g, ' '))")
    check("the offensive coordinator is judged by points scored a game and the league rank", oc and "points scored a game" in oc[0] and " of " in oc[0], str(oc)[:200])
    pg.wait_for_timeout(6000)
    st = pg.evaluate("[document.getElementById('cprog').textContent, document.querySelectorAll('#cstat table').length]")
    check("the club's team statistics (offense and defense) appear as its games are loaded", st[1] == 2 and "games counted" in st[0], str(st))
    lines = pg.evaluate("[...document.querySelectorAll('[data-pl]')].filter(td => td.textContent.trim()).length")
    check("players' season lines are filled in from the box scores", lines >= 10, str(lines))
    # a player's page by id
    pid = pg.evaluate("byId[%s].roster.find(p => p.pos === 'QB').pid" % cid)
    pg.evaluate("location.hash='#player-%s'" % pid)
    try: pg.wait_for_function("(() => { const t = document.getElementById('pprog'); return t && / counted\\.$/.test(t.textContent); })()", timeout=40000)
    except Exception: pass
    body = pg.inner_text("#app")
    check("a player has a page found by her id, with her season's passing line", "Passing" in body and "backstory" in body.lower() and "game" in pg.inner_text("#pprog"), pg.inner_text("#pprog") + " | " + pg.inner_text("#pstat")[:150])
    # a coach hired after year 1 is found by search
    newc = next((cur["teams"][t]["p"][2][0] for t in cur["teams"] if cur["teams"][t]["p"][2][0] != S1["teams"][t]["p"][2][0]), None)
    if newc:
        pg.evaluate("location.hash='#search'"); pg.wait_for_timeout(400); pg.select_option("#st", "staff"); pg.fill("#sq", newc); pg.wait_for_timeout(300)
        check("a coach hired since year 1 is found by search", newc in pg.inner_text("#sbody"), newc)
    # looking back: the club's page shows the old year's roster, and returns to the current
    pg.evaluate("location.hash='#seasons-1'"); pg.wait_for_timeout(3500)
    pg.evaluate("location.hash='#club-%s'" % ab); pg.wait_for_timeout(1500)
    names1 = pg.evaluate("byId[%s].roster.map(p => p.name)" % cid)
    check("looking back at year 1 shows year 1's roster", names1 == [r[1] for r in S1["teams"][cid]["r"]], str(names1[:3]))
    pg.click("[data-live]") if pg.evaluate("!!document.querySelector('[data-live]')") else None; pg.wait_for_timeout(2500)
    pg.evaluate("location.hash='#club-%s'" % ab); pg.wait_for_timeout(1500)
    check("and going back to live shows the current roster again", pg.evaluate("byId[%s].roster.map(p => p.name)" % cid) == [r[1] for r in cur["teams"][cid]["r"]])
    check("no script error", not errs, str(errs[:2]))
    br.close()

# 3 ------------------------------------------------------------------------------------------------------------------------------
root = tempfile.mkdtemp(); build_site.build(os.path.join(root, "index.html"), 7, rules=5); url = serve(root)
with sync_playwright() as pw:
    br = pw.chromium.launch(); errs = []
    pg = br.new_page(viewport=dict(width=1100, height=900)); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(600)
    ab = pg.evaluate("clubs.find(c => !c.exiled).abbr"); pg.evaluate("location.hash='#club-%s'" % ab); pg.wait_for_timeout(4500)
    sec = pg.evaluate("[...document.querySelectorAll('#app h2')].map(h => h.textContent.trim())")
    check("the founding season's club page has the same sections", all(x in sec for x in ["Coaching staff", "Season by season", "Team statistics", "Schedule and results", "Players"]), str(sec))
    check("its team statistics carry the league rank (every game of the season is in)", pg.evaluate("document.querySelectorAll('#cstat table').length") == 2 and pg.evaluate("/\\d(st|nd|rd|th)/.test(document.getElementById('cstat').innerText)"))
    check("its season by season has the one season", pg.evaluate("[...document.querySelectorAll('#app h2')].find(h => h.textContent.trim() === 'Season by season').parentElement.querySelectorAll('tbody tr').length") == 1)
    hcard = pg.evaluate("[...document.querySelectorAll('#app .card')].find(c => c.querySelector('.eyebrow') && c.querySelector('.eyebrow').textContent === 'Defensive coordinator').innerText.replace(/\\s+/g, ' ')")
    check("the defensive coordinator is judged by points allowed a game", "points allowed a game" in hcard, hcard[:160])
    pid = pg.evaluate("clubs.find(c => !c.exiled).roster.find(p => p.pos === 'WR').pid"); pg.evaluate("location.hash='#player-%s'" % pid); pg.wait_for_timeout(3000)
    check("a player's page is found by her id and is lit under the DFL tab", pg.evaluate("document.querySelector('#app h1').textContent.length") > 3 and pg.evaluate("document.querySelector('#tabs [aria-current]').textContent.trim()") == "DFL")
    check("the older player address (club and number) still works", (pg.evaluate("location.hash='#player-%s-3'" % ab), pg.wait_for_timeout(500), pg.evaluate("document.querySelector('#app h1').textContent.length"))[2] > 3)
    check("no script error", not errs, str(errs[:2]))
    br.close()
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED")); sys.exit(1 if failures else 0)
