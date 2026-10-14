"""The website's data (site_export.py) agrees with the engine: every game has its date, the standings add up, the page builds."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_export, build_site, injuries

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
if sync_playwright is not None:
    # ---- rules version 2: penalties and timeouts are in the log, and the page's replay still gives the engine's totals back ----
    import game_engine
    out2 = os.path.join(tempfile.mkdtemp(), "g2.html"); build_site.build(out2, 7, rules=2)
    JS2 = """() => { const bad = []; let pens = 0, tos = 0; for (const id of Object.keys(D.box)) { const b = D.box[id], g = gameById[id], S = freshState(b);
      b.p.forEach((pl, i) => { if (pl[6] === "PN") pens++; if (pl[6] === "TO") tos++; applyPlay(S, b, pl); if (!b.p[i + 1] || b.p[i + 1][13] !== pl[13]) endDrive(S, b, pl[13]); }); b.dr.forEach((x, k) => { if (k >= S.drivesDone) endDrive(S, b, k); });
      for (const s of [0, 1]) { const t = S.tm[s], e = b.tm[s]; const mine = [t.plays, t.yards, t.pass_yds, t.rush_yds, t.first, t.to, t.sacks, t.punts, t.t3c, t.t3a, t.cmp, t.att, t.rush, t.fga, t.fgm, t.pen, t.penyds];
        const eng = [e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9], e[11], e[12], e[13], e[14], e[15], b.pen[s][0], b.pen[s][1]]; mine.forEach((v, k) => { if (v !== eng[k]) bad.push([id, s, k]); }); }
      if (!b.tb && (S.score[0] !== g.hp || S.score[1] !== g.ap)) bad.push([id, "score"]); }
      return { bad: bad.length, pens, tos, names: PEN.map(x => x[0]), afd: PEN_AFD, text: Object.keys(D.box).slice(0, 40).every(id => { const b = D.box[id]; return b.p.every(pl => { const r = playText(b, pl, { abbr: ["AAA", "BBB"] }); return r && typeof r[0] === "string" && !/undefined|NaN/.test(r[0]); }); }) }; }"""
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(); errs2 = []
        pg.on("pageerror", lambda e: errs2.append(str(e)))
        pg.goto("file://" + out2)
        r2 = pg.evaluate(JS2)
        pg.evaluate("location.hash='game-r1_25'"); pg.wait_for_timeout(300)
        txt2 = pg.evaluate("document.getElementById('app').innerText")
        br.close()
    check("rules 2: the page's replay of all 401 games gives the engine's totals, penalties and penalty yards included", r2["bad"] == 0 and r2["pens"] > 3000 and r2["tos"] > 500, str(r2["bad"]) + " " + str(r2["pens"]) + " " + str(r2["tos"]))
    check("rules 2: the page's penalty names and automatic-first-down list are the engine's", r2["names"] == list(game_engine.PENALTY_NAMES) and r2["afd"] == [i for i, p in enumerate(game_engine.PENALTIES) if p[3]], str(r2["names"][:3]))
    check("rules 2: every play of forty games reads as a sentence, and the game page opens without script errors", r2["text"] and not errs2 and "penalt" in txt2.lower(), str(errs2[:2]))
if sync_playwright is not None:
    # ---- the standings columns: Div, Conf, SOS and SOV are the engine's own tiebreak measures; GB and the magic number agree with the standings at every point of a season ----
    import types
    import tiebreak
    d7 = site_export.export(7, 1)
    gl = [types.SimpleNamespace(home=g["home"], away=g["away"], home_pts=g["hp"], away_pts=g["ap"]) for g in d7["games"]]
    did = {c["id"]: i // 6 for i, c in enumerate(d7["clubs"])}
    lg = types.SimpleNamespace(by_id={i: types.SimpleNamespace(conf=did[i] // 4, division_id=did[i]) for i in did})
    played = sorted({x for g in gl for x in (g.home, g.away)})
    L = tiebreak.Ledger(lg, gl, played)
    fmt = lambda f: ("%.3f" % float(f)).lstrip("0") if float(f) < 1 else "1.000"
    rec = lambda gs: "%d-%d%s" % (sum(1 for x in gs if x[1] > x[2]), sum(1 for x in gs if x[1] < x[2]), ("-%d" % sum(1 for x in gs if x[1] == x[2])) if any(x[1] == x[2] for x in gs) else "")
    want = {}
    for i in played:
        dv = [x for x in L.g[i] if lg.by_id[x[0]].division_id == lg.by_id[i].division_id]; cf = [x for x in L.g[i] if lg.by_id[x[0]].conf == lg.by_id[i].conf]
        want[i] = [rec(dv), rec(cf), fmt(L.m_sos(i, [])), fmt(L.m_sov(i, []))]
    outS = os.path.join(tempfile.mkdtemp(), "s.html"); build_site.build(outS, 7, rules=1)
    JSS = """(cuts) => { const X = standExtras(), res = { cols: {}, magic: [] };
      clubs.forEach(c => { const x = X[c.id]; res.cols[c.id] = [x.div, x.conf, x.sos, x.sov]; });
      const real = D.games.map(g => [g.hp, g.ap]);
      for (const cut of cuts) { D.games.forEach((g, i) => { if (g.week > cut) { g.hp = null; g.ap = null; } else { g.hp = real[i][0]; g.ap = real[i][1]; } });
        const Y = standExtras(), html = standings(), div = document.createElement("div"); div.innerHTML = html;
        const rows = [...div.querySelectorAll("table")].map(t => [...t.tBodies[0].rows].filter(r => !r.classList.contains("exile")));
        rows.forEach((rs, k) => { const ids = rs.map(r => clubs.find(c => r.cells[0].innerText.includes(c.name)).id), lead = ids[0], oth = ids.slice(1);
          const cell = rs[0].cells[5].innerText.trim(), bound = Math.max(...oth.map(i => Y[i].credit + Y[i].left)), clinched = Y[lead].credit > bound, done = ids.every(i => Y[i].left === 0);
          res.magic.push({ cut, cell, clinched, done, gb: rs.slice(1).map((r, j) => [r.cells[5].innerText.trim(), ((Y[lead].credit - Y[ids[j + 1]].credit) + (Y[ids[j + 1]].lossCredit - Y[lead].lossCredit)) / 2]) }); }); }
      return res; }"""
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(); errsS = []
        pg.on("pageerror", lambda e: errsS.append(str(e)))
        pg.goto("file://" + outS)
        rs = pg.evaluate(JSS, [4, 8, 12, 15, 17, 19])
        br.close()
    colbad = [i for i in played if rs["cols"][str(i)] != want[i]]
    check("standings: Div, Conf, SOS and SOV for all 40 active clubs equal the engine's tiebreak measures", not colbad and not errsS, str([(i, rs["cols"][str(i)], want[i]) for i in colbad[:2]] + errsS[:1]))
    bad = []
    for m in rs["magic"]:
        c = m["cell"]
        if m["done"]: ok = c == "Won"
        elif m["clinched"]: ok = c == "Clinched"
        else: ok = c.startswith("M ") and int(c[2:]) >= 1
        ok = ok and all(float(g[0]) == g[1] for g in m["gb"])
        if not ok: bad.append(m)
    check("standings: the leader's magic number reads Won, Clinched or M n exactly when the games left say so, at six points of the season, and GB is the half-game gap", not bad and sum(1 for m in rs["magic"] if m["cell"].startswith("M ")) > 10, str(bad[:2]))
    # ---- rules version 3: spikes and kneels (clock management) are in the log, and the page's replay still gives the engine's totals back ----
    out3 = os.path.join(tempfile.mkdtemp(), "g3.html"); build_site.build(out3, 7, rules=3)
    JS4 = JS2.replace("if (pl[6] === \"PN\") pens++;", "if (pl[6] === \"PN\") pens++; if (pl[6] === \"SP\") sps++; if (pl[6] === \"KN\") kns++;").replace("let pens = 0, tos = 0;", "let pens = 0, tos = 0, sps = 0, kns = 0;").replace("return { bad: bad.length, pens, tos,", "return { bad: bad.length, pens, tos, sps, kns,")
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(); errs4 = []
        pg.on("pageerror", lambda e: errs4.append(str(e)))
        pg.goto("file://" + out3)
        r4 = pg.evaluate(JS4)
        txt4 = pg.evaluate("Object.keys(D.box).slice(0, 400).flatMap(id => D.box[id].p.filter(pl => pl[6] === 'SP' || pl[6] === 'KN').slice(0, 1).map(pl => playText(D.box[id], pl, { abbr: ['AAA', 'BBB'] })[0])).join(' | ')")
        br.close()
    check("rules 3: the page's replay of all 401 games gives the engine's totals, spikes and kneels included", r4["bad"] == 0 and r4["sps"] > 100 and r4["kns"] > 300, f"{r4['bad']} bad, {r4['sps']} spikes, {r4['kns']} kneels")
    check("rules 3: spikes and kneels read as sentences, and the page runs without script errors", "spikes the ball" in txt4 and "takes a knee" in txt4 and r4["text"] and not errs4, str(errs4[:2]))
    # ---- rules version 4: players are hurt during the game and a backup comes in; the page's replay still gives the engine's totals back ----
    out5 = os.path.join(tempfile.mkdtemp(), "g4.html"); build_site.build(out5, 7, rules=4)
    JS5 = JS4.replace("if (pl[6] === \"KN\") kns++;", "if (pl[6] === \"KN\") kns++; if (pl[6] === \"IJ\") ijs++;").replace("let pens = 0, tos = 0, sps = 0, kns = 0;", "let pens = 0, tos = 0, sps = 0, kns = 0, ijs = 0;").replace("return { bad: bad.length, pens, tos, sps, kns,", "return { bad: bad.length, pens, tos, sps, kns, ijs, inj: INJ,")
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(); errs5 = []
        pg.on("pageerror", lambda e: errs5.append(str(e)))
        pg.goto("file://" + out5)
        r5 = pg.evaluate(JS5)
        txt5 = pg.evaluate("Object.keys(D.box).slice(0, 400).flatMap(id => D.box[id].p.filter(pl => pl[6] === 'IJ').slice(0, 1).map(pl => playText(D.box[id], pl, { abbr: ['AAA', 'BBB'] })[0])).slice(0, 6).join(' | ')")
        br.close()
    check("rules 4: the page's replay of all 401 games gives the engine's totals with players hurt in the log", r5["bad"] == 0 and r5["ijs"] > 800, f"{r5['bad']} bad, {r5['ijs']} injuries")
    check("rules 4: the page's injury names are the engine's, in the same order", r5["inj"] == list(injuries.KIND_NAMES), str(r5["inj"][:3]))
    check("rules 4: an injury reads as a sentence naming who is hurt and who comes in, and the page runs without script errors", "is hurt" in txt5 and "comes in" in txt5 and r5["text"] and not errs5 and "undefined" not in txt5, txt5[:200] + str(errs5[:2]))
if sync_playwright is not None:
    # ---- the Statistics tab: team and player tables add up to the same totals from the same replays ----
    JS3 = """async () => { const run = ++STATS.run; await statsLoad(statGames("reg"), run, () => {});
      const rs = statGames("reg").map(g => STATS.cache[g.id]).filter(Boolean), tr = teamRows(rs, "off"), td = teamRows(rs, "def"), sum = (L, f) => Math.round(L.reduce((a, r) => a + f(r), 0));
      const pass = playerRows(rs, "pass", ""), rec = playerRows(rs, "recv", ""), ru = playerRows(rs, "rush", ""), df = playerRows(rs, "def", ""), kk = playerRows(rs, "kick", "");
      return { games: rs.length, clubs: tr.length, gp: sum(tr, t => t.gp), pts: D.games.reduce((a, g) => a + g.hp + g.ap, 0), offPts: sum(tr, t => t.ppg * t.gp), defPts: sum(td, t => t.papg * t.gp),
        passP: sum(pass, r => r.yds), recP: sum(rec, r => r.yds), teamPass: sum(tr, t => t.pypg * t.gp), rushP: sum(ru, r => r.yds), teamRush: sum(tr, t => t.rypg * t.gp), sacks: sum(df, r => r.sacks), teamSacks: sum(td, t => t.sks * t.gp),
        fg: sum(kk, r => r.fgm), maxgp: Math.max(...pass.concat(ru, rec, df).map(r => r.gp)), pen: sum(tr, t => t.pen * t.gp) }; }"""
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(); errs3 = []
        pg.on("pageerror", lambda e: errs3.append(str(e)))
        pg.goto("file://" + out2)
        r3 = pg.evaluate(JS3)
        txts = []
        for hsh in ("stats", "stats-team", "stats-player"):
            pg.evaluate(f"location.hash='{hsh}'"); pg.wait_for_timeout(600); txts.append(pg.evaluate("document.getElementById('app').innerText"))
        rows = pg.evaluate("document.querySelectorAll('#sbody tbody tr').length")
        br.close()
    check("statistics: every one of the 360 regular-season games is counted, for 40 clubs, 18 games each", r3["games"] == 360 and r3["clubs"] == 40 and r3["gp"] == 720, str(r3))
    check("statistics: team points for and against add up to the games' scores", r3["offPts"] == r3["pts"] == r3["defPts"], str(r3))
    check("statistics: players' passing, receiving and rushing yards equal the teams', and sacks and field goals add up", r3["passP"] == r3["recP"] == r3["teamPass"] and r3["rushP"] == r3["teamRush"] and r3["sacks"] == r3["teamSacks"] and r3["fg"] > 500 and r3["pen"] > 3000, str(r3))
    check("statistics: no player appears in more than 18 regular-season games, so one player is one row", r3["maxgp"] <= 18, str(r3["maxgp"]))
    check("statistics: the fork page, the team page and the player page open without script errors", not errs3 and "team statistics" in txts[0].lower() and "player statistics" in txts[0].lower() and "pts/g" in txts[1].lower() and "yds" in txts[2].lower() and rows > 20, str(errs3[:2]))
out = os.path.join(tempfile.mkdtemp(), "i.html")
n = build_site.build(out, 7)
html = open(out, encoding="utf-8").read()
check("the page builds as one file with the data in it and no placeholder left", n > 1_000_000 and "__DATA__" not in html and "Diamond Football League" in html)
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
