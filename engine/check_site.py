"""The website's data (site_export.py) agrees with the engine: every game has its date, the standings add up, the page builds."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_export, build_site

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


d = site_export.export(7)
cl = {c["id"]: c for c in d["clubs"]}
act = [c for c in d["clubs"] if not c["exiled"]]
check("48 clubs, 8 in exile, 40 playing, 53 players each", len(d["clubs"]) == 48 and len(act) == 40 and all(len(c["roster"]) == 53 for c in d["clubs"]))
check("360 regular-season games, each with a date and a kickoff", len(d["games"]) == 360 and all(g["date"] and g["time"] for g in d["games"]))
check("every playing club has 18 results and its record matches its games", all(
    c["record"]["w"] + c["record"]["l"] + c["record"]["t"] == 18 and c["record"]["w"] == sum(1 for g in d["games"] if (g["home"] == c["id"] and g["hp"] > g["ap"]) or (g["away"] == c["id"] and g["ap"] > g["hp"])) for c in act))
check("wins equal losses across the league (ties count once each side)", sum(c["record"]["w"] for c in act) == sum(c["record"]["l"] for c in act))
check("the eight clubs in exile each played seven Ambassador games", all(sum(c["ambassador"][k] for k in "wlt") == 7 for c in d["clubs"] if c["exiled"]) and len(d["ambassador"]) == 28)
check("thirteen playoff games and a champion among the 14 playoff clubs", len(d["playoffs"]) == 13 and d["champion"] in {t for s in d["seeds"].values() for t in s} and sum(len(s) for s in d["seeds"].values()) == 14)
check("the same seed gives the same site data", site_export.export(7)["games"] == d["games"] and site_export.export(7)["champion"] == d["champion"])
ev = d["evolution"]
check("forty seasons of the schedule (2000 to 2039), year 1 in order, the pattern repeating every eight years, every season a permutation of the eight divisions",
      len(ev) == 40 and ev[0]["slots"] == list(range(1, 9)) and all(ev[i]["slots"] == ev[i + 8]["slots"] for i in range(32)) and all(sorted(e["slots"]) == list(range(1, 9)) for e in ev)
      and ev[1]["slots"][:4] == [4, 1, 2, 3] and ev[4]["slots"] == [5, 6, 7, 8, 1, 2, 3, 4])
# ---- game pages: every game carries the engine's own record, and the page's replay adds it up to the box score ----
import re
allg = d["games"] + d["ambassador"] + d["playoffs"]
check("every game has an id and a box (play log, drives, team totals): 360 + 28 + 13", len(allg) == 401 and all(g.get("id") in d["box"] for g in allg) and len(d["box"]) == 401)
def drive_score(b):
    sc = [0, 0]
    for side, q, st, pl, yd, sec, res_, pts, dpts in b["dr"]:
        sc[side] += pts; sc[1 - side] += dpts
    return sc
check("each game's drives add up to its final score (a seeded kick-off decision aside)", all(drive_score(d["box"][g["id"]]) == [g["hp"], g["ap"]] for g in allg if not d["box"][g["id"]]["tb"]))
check("every play points at a real drive and a real player; the clock never runs backward", all(
    all(0 <= p[13] < len(b["dr"]) and (p[7] < len(b["pl"])) and (p[8] < len(b["pl"]) or p[6] == "FG") for p in b["p"]) and all(x[14] <= y[14] for x, y in zip(b["p"], b["p"][1:])) for b in d["box"].values()))
check("no player appears in a box score by a placeholder number", not any(re.match(r"^P\d{5}$", q[0]) for b in d["box"].values() for q in b["pl"]))
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None
if sync_playwright is None:
    print("SKIP the page's replay is not checked here (playwright is not installed)")
else:
    out0 = os.path.join(tempfile.mkdtemp(), "g.html"); build_site.build(out0, 7)
    JS = """() => { const bad = []; for (const id of Object.keys(D.box)) { const b = D.box[id], g = gameById[id], S = freshState(b);
      b.p.forEach((pl, i) => { applyPlay(S, b, pl); if (!b.p[i + 1] || b.p[i + 1][13] !== pl[13]) endDrive(S, b, pl[13]); }); b.dr.forEach((x, k) => { if (k >= S.drivesDone) endDrive(S, b, k); });
      for (const s of [0, 1]) { const t = S.tm[s], e = b.tm[s]; const mine = [t.plays, t.yards, t.pass_yds, t.rush_yds, t.first, t.to, t.sacks, t.punts, t.t3c, t.t3a, t.cmp, t.att, t.rush, t.fga, t.fgm];
        const eng = [e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9], e[11], e[12], e[13], e[14], e[15]]; mine.forEach((v, k) => { if (v !== eng[k]) bad.push([id, s, k]); }); if (Math.abs(t.top - e[10]) > b.dr.length) bad.push([id, s, "top"]); }
      if (!b.tb && (S.score[0] !== g.hp || S.score[1] !== g.ap)) bad.push([id, "score"]); } return bad.length; }"""
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://" + out0)
        nbad = pg.evaluate(JS)
        pg.evaluate("location.hash='game-r1_25'"); pg.wait_for_timeout(300)
        txt = pg.evaluate("document.getElementById('app').innerText")
        br.close()
    check("the page's own replay of all 401 games gives the engine's team totals and final score", nbad == 0, f"{nbad} mismatches")
    check("a game page opens on the finished game with a scoreboard, play by play, leaders and drives, and no script errors", not errs and "play by play" in txt.lower() and "drives" in txt.lower() and "leaders" in txt.lower(), str(errs[:2]))
out = os.path.join(tempfile.mkdtemp(), "i.html")
n = build_site.build(out, 7)
html = open(out, encoding="utf-8").read()
check("the page builds as one file with the data in it and no placeholder left", n > 1_000_000 and "__DATA__" not in html and "Diamond Football League" in html)
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
