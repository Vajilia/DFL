"""The animated field (site/stage.js): it only ever shows what the play log says.

  1  every play of every game of the founding league builds a scene that stays on the field, can be sampled all along, and ends where the log says (engine/check_stage.js, run with node)
  2  on the page: a replay runs the scenes with no script error, the canvas is drawn, the switch turns it off and on, 'reduced motion' starts it off
  3  live: a play that arrives while the game page is open is animated, and the plays already shown are not

    python engine/check_stage.py
"""
import functools, http.server, json, os, shutil, subprocess, sys, tempfile, threading, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site, live as L, site_export

failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok: failures.append(name)

tmp = tempfile.mkdtemp()
# 1 ------------------------------------------------------------------------------------------------------------------------------
if shutil.which("node"):
    d = site_export.export(7, 2)
    bj = os.path.join(tmp, "box.json"); json.dump({"box": d["box"]}, open(bj, "w"), separators=(",", ":"))
    r = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_stage.js"), bj], capture_output=True, text=True)
    try: o = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: o = {"plays": 0, "bad": [r.stdout[-300:] + r.stderr[-300:]]}
    check(f"every play of every game ({o['plays']}) builds a scene that stays on the field and ends where the log says", r.returncode == 0 and o["plays"] > 50000 and not o["bad"], str(o.get("bad"))[:400])
    check("a scene lasts between 2 and 20 seconds, and every name tag names a player of the play", 2 <= o.get("minDur", 0) and o.get("maxDur", 99) < 20 and o.get("tagBad", 1) == 0, str(o))
else:
    print("SKIP the scenes are not checked here (node is not installed)")
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP the page is not checked here (playwright is not installed)")
    print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED")); sys.exit(1 if failures else 0)

def serve(root):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/index.html"
PIXELS = """() => { const c = document.getElementById('stage'), g = c.getContext('2d'), w = c.width, h = c.height, d = g.getImageData(0, 0, w, h).data, seen = new Set();
  for (let i = 0; i < d.length; i += 4 * 97) seen.add((d[i] >> 5) * 64 + (d[i + 1] >> 5) * 8 + (d[i + 2] >> 5)); return seen.size; }"""

# 2 ------------------------------------------------------------------------------------------------------------------------------
root = tempfile.mkdtemp(); build_site.build(os.path.join(root, "index.html"), 7, rules=2)
srv, url = serve(root)
with sync_playwright() as pw:
    br = pw.chromium.launch(); errs = []
    pg = br.new_page(viewport=dict(width=1100, height=900))
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(500)
    gid = pg.evaluate("D.games.find(g=>g.id).id"); pg.evaluate("location.hash=%s" % json.dumps("game-" + gid)); pg.wait_for_timeout(800)
    check("the game page opens with the animated field on and the strip hidden", pg.evaluate("!document.getElementById('stagewrap').hidden && document.getElementById('field').style.display === 'none' && !!REPLAY.stage()") and "on" in pg.inner_text("#anim").lower())
    check("the canvas is drawn: turf, lines, players and ball, not a blank field", pg.evaluate(PIXELS) > 12, str(pg.evaluate(PIXELS)))
    pg.select_option("#speed", "4"); pg.click("#watch"); pg.wait_for_timeout(9000)
    st = pg.evaluate("REPLAY.stage().stats"); shown = pg.evaluate("REPLAY.state().i")
    check("a replay at 4x runs plays on the field", st["animated"] >= 1 and shown >= 2, f"{st} {shown}")
    pg.select_option("#speed", "60"); pg.wait_for_timeout(6000)
    st2 = pg.evaluate("REPLAY.stage().stats")
    check("at 60x the plays are too quick to act out and are shown as results, with no error", st2["snapped"] >= 1 and not errs, f"{st2} {errs[:2]}")
    pg.click("#final"); pg.wait_for_timeout(400)
    check("skipping to the final leaves a drawn field and the final score", pg.evaluate(PIXELS) > 12 and pg.evaluate("REPLAY.state().i === D.box[%s].p.length" % json.dumps(gid)))
    # every kind of play, drawn at several instants of its scene
    kinds = pg.evaluate("""(gid) => { const b = D.box[gid], out = {}; b.p.forEach((p, i) => { if (!(p[6] in out)) out[p[6]] = i; }); return out; }""", gid)
    bad = pg.evaluate("""(kinds) => { const st = REPLAY.stage(), bad = []; for (const [k, i] of Object.entries(kinds)) { const sc = REPLAY.sceneFor(i);
        for (const f of [0, .2, .5, .8, 1]) { try { st.showAt(sc, sc.dur * f); } catch (e) { bad.push(k + ': ' + e.message); } } } return bad; }""", kinds)
    check(f"every kind of play ({', '.join(sorted(kinds))}) draws at the start, the middle and the end of its scene", not bad and len(kinds) >= 8, str(bad[:3]))
    pg.click("#anim"); off = pg.evaluate("[document.getElementById('stagewrap').hidden, document.getElementById('field').style.display, !!REPLAY.stage(), localStorage.getItem('dfl.anim')]")
    check("the switch turns the animation off: the strip is back, and the choice is remembered", off == [True, "", False, "0"], str(off))
    pg.reload(); pg.wait_for_timeout(500); pg.evaluate("location.hash=%s" % json.dumps("game-" + gid)); pg.wait_for_timeout(800)
    check("a viewer who switched it off finds it off on the next game page", pg.evaluate("document.getElementById('stagewrap').hidden && !REPLAY.stage()"))
    pg.click("#anim"); pg.wait_for_timeout(300)
    check("and on again", pg.evaluate("!document.getElementById('stagewrap').hidden && !!REPLAY.stage()") and pg.evaluate(PIXELS) > 12)
    check("no script errors on the page", not errs, str(errs[:3]))
    pg.close()
    pg = br.new_page(viewport=dict(width=380, height=800), reduced_motion="reduce"); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(500); pg.evaluate("location.hash=%s" % json.dumps("game-" + gid)); pg.wait_for_timeout(800)
    check("a viewer who asks for reduced motion starts with it off", pg.evaluate("document.getElementById('stagewrap').hidden && !REPLAY.stage()"))
    pg.click("#anim"); pg.wait_for_timeout(300)
    ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("on a phone the field fits the screen and draws", ow <= 0 and pg.evaluate(PIXELS) > 12 and not errs, f"overflow {ow} {errs[:2]}")
    br.close()
srv.shutdown()

# 3 ------------------------------------------------------------------------------------------------------------------------------
H = 3600 * 1000
root = tempfile.mkdtemp(); build_site.build(os.path.join(root, "index.html"), 7, live=True, rules=2)
now = int(time.time() * 1000)
meta = dict(seed=7, epoch_ms=0, pacing="blocks", real_per_game=L.BLOCK_REAL_PER_GAME, halftime=L.HALFTIME_PAUSE, parity="tight", rules=2)
out = os.path.join(root, "live"); live_id = None; epoch = None
for hrs in range(2, 60):                                     # find a moment when a game is being played
    meta["epoch_ms"] = now - hrs * H - 600 * 1000 * 3
    shutil.rmtree(out, ignore_errors=True); L.write_json(out + "/meta.json", meta)
    run = L.Runner(out, 7, meta["epoch_ms"], meta); run.tick(now)
    R = json.load(open(out + "/results.json"))
    lv = [g for g in (R["live"] if isinstance(R["live"], list) else list(R["live"]))]
    if lv: live_id = lv[0]; epoch = meta["epoch_ms"]; break
check("the live league has a game in progress to look at", live_id is not None, "none found")
if live_id is not None:
    srv, url = serve(root)
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(viewport=dict(width=1100, height=900)); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url + "#game-" + str(live_id)); pg.wait_for_timeout(4500)
        n0 = pg.evaluate("D.box[%s] ? D.box[%s].p.length : -1" % (json.dumps(live_id), json.dumps(live_id)))
        st0 = pg.evaluate("REPLAY && REPLAY.stage() ? REPLAY.stage().stats : null")
        check("a live game opens with its plays shown as they stand, none acted out", n0 > 0 and st0 is not None and st0["animated"] == 0, f"{n0} {st0}")
        run.tick(now + 4 * 60 * 1000); pg.wait_for_timeout(7000)
        n1 = pg.evaluate("D.box[%s].p.length" % json.dumps(live_id)); st1 = pg.evaluate("REPLAY && REPLAY.stage() ? REPLAY.stage().stats : null")
        check("a play that arrives while the page is open is run on the field", n1 > n0 and st1 is not None and (st1["animated"] + st1["snapped"]) >= 1, f"{n0}->{n1} {st1}")
        check("no script errors while the game is live", not errs, str(errs[:3]))
        br.close()
    srv.shutdown()
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED"))
sys.exit(1 if failures else 0)
