"""The chalkboard (site/playcalls.js, site/chalk.js, data/playbook.json): a flat dot view of the field with the coordinators' calls drawn after each play.

  1  every run, pass, sack and try of the founding league: a call that fits the logged result, repeatable, on the field, 22 assignments, and the scene built with the call ends where the log says
     (engine/check_calls.js, run with node)
  2  on the page: the view can be chosen, a replay runs on it with no script error, the call is written under the board after a play, the other views still work, a phone fits
  3  the engine, the media and the coordinators never read the reconstruction: no engine file imports it or names it

    python engine/check_calls.py
"""
import functools, http.server, json, os, re, shutil, subprocess, sys, tempfile, threading

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_site, site_export

failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok: failures.append(name)

tmp = tempfile.mkdtemp()
# 1 ------------------------------------------------------------------------------------------------------------------------------
if shutil.which("node"):
    d = site_export.export(7, 5)
    bj = os.path.join(tmp, "box.json"); json.dump({"box": d["box"]}, open(bj, "w"), separators=(",", ":"))
    r = subprocess.run(["node", os.path.join(HERE, "check_calls.js"), bj], capture_output=True, text=True)
    try: o = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: o = {"plays": 0, "called": 0, "bad": [r.stdout[-300:] + r.stderr[-300:]]}
    check(f"every run, pass, sack and try ({o['plays']}) gets a call that fits what the log says, is the same every time, lines everyone up on the field and ends where the log says",
          r.returncode == 0 and o["plays"] > 40000 and o["called"] == o["plays"] and not o["bad"], str(o.get("bad"))[:400])
    byc, byd = o.get("byCall", {}), o.get("byDef", {})
    check("the calls vary: at least 12 offensive and 8 defensive calls are used, and no one call is more than 22% of its side",
          len(byc) >= 12 and len(byd) >= 8 and max(byc.values()) <= .22 * sum(byc.values()) and max(byd.values()) <= .22 * sum(byd.values()), f"{byc} {byd}")
else:
    print("SKIP the calls are not checked here (node is not installed)")
# 3 ------------------------------------------------------------------------------------------------------------------------------
bad = []
for f in sorted(os.listdir(HERE)):
    if f.endswith(".py") and f not in ("check_calls.py", "build_site.py", "run_checks.py"):
        t = open(os.path.join(HERE, f), encoding="utf-8").read()
        if re.search(r"playcalls|playbook\.json|chalk\.js|DFLCalls", t) and not f.startswith("check_"): bad.append(f)
check("no engine file reads the playbook or the reconstruction", not bad, str(bad))
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP the page is not checked here (playwright is not installed)")
    print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED")); sys.exit(1 if failures else 0)
# 2 ------------------------------------------------------------------------------------------------------------------------------
PIXELS = """() => { const c = document.getElementById('stage'), g = c.getContext('2d'), w = c.width, h = c.height, d = g.getImageData(0, 0, w, h).data, seen = new Set();
  for (let i = 0; i < d.length; i += 4 * 97) seen.add((d[i] >> 5) * 64 + (d[i + 1] >> 5) * 8 + (d[i + 2] >> 5)); return seen.size; }"""
root = tempfile.mkdtemp(); build_site.build(os.path.join(root, "index.html"), 7, rules=5)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=root))
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
with sync_playwright() as pw:
    br = pw.chromium.launch(); errs = []
    pg = br.new_page(viewport=dict(width=1100, height=1000))
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(500)
    gid = pg.evaluate("D.games.find(g=>g.id).id"); pg.evaluate("location.hash=%s" % json.dumps("game-" + gid)); pg.wait_for_timeout(800)
    for _ in range(5):
        if "chalk" in pg.inner_text("#view3d").lower(): break
        pg.click("#view3d"); pg.wait_for_timeout(300)
    check("the view button offers the chalkboard and the board is on", "chalk" in pg.inner_text("#view3d").lower() and pg.evaluate("!!REPLAY.stage().chalk && !document.getElementById('callline').hidden"))
    check("the board is drawn: turf, lines, 22 dots and a ball, not a blank field", pg.evaluate(PIXELS) > 12, str(pg.evaluate(PIXELS)))
    check("the choice is remembered", pg.evaluate("localStorage.getItem('dfl.view')") == "chalk")
    pg.select_option("#speed", "4"); pg.click("#watch"); txt = ""
    for _ in range(70):
        pg.wait_for_timeout(200); t = pg.inner_text("#callline")
        if "Offense" in t: txt = t; break
    pg.wait_for_timeout(3000); shown = pg.evaluate("REPLAY.state().i")
    check("a replay runs on the board and the calls are written under it after a play", shown >= 3 and "Offense" in txt and "Defense" in txt and "reconstruction" in txt, f"{shown} {txt[:200]}")
    kinds = pg.evaluate("""(gid) => { const b = D.box[gid], out = {}; b.p.forEach((p, i) => { if (!(p[6] in out)) out[p[6]] = i; }); return out; }""", gid)
    bad = pg.evaluate("""(kinds) => { const st = REPLAY.stage(), bad = []; for (const [k, i] of Object.entries(kinds)) { const sc = REPLAY.sceneFor(i); st.lu = sc.lu;
        for (const f of [0, .2, .5, .8, 1]) { try { st.showAt(sc, sc.dur * f); } catch (e) { bad.push(k + ': ' + e.message); } } } return bad; }""", kinds)
    check(f"every kind of play ({', '.join(sorted(kinds))}) draws on the board at the start, the middle and the end", not bad and len(kinds) >= 8, str(bad[:3]))
    nums = pg.evaluate("""() => { const i = D.box[%s].p.findIndex(p => p[6] === 'RU'), sc = REPLAY.sceneFor(i); return sc.lu.map(c => c.o.concat(c.d).filter(x => x && x.num != null).length); }""" % json.dumps(gid))
    check("each club has a number for each of its 22 jobs", nums == [22, 22], str(nums))
    pg.click("#view3d"); pg.wait_for_timeout(500)
    check("the next view is the sideline 3D view or falls back to the flat field, and the board's call line is gone", pg.evaluate("document.getElementById('callline').hidden"))
    pg.evaluate("document.getElementById('view3d').click()"); pg.evaluate("document.getElementById('view3d').click()"); pg.wait_for_timeout(400)
    check("cycling through the views comes back to the flat sprite field", "2d" in pg.inner_text("#view3d").lower() and pg.evaluate("!REPLAY.stage().chalk"), pg.inner_text("#view3d"))
    check("no script errors on the page", not errs, str(errs[:3]))
    pg.close()
    pg = br.new_page(viewport=dict(width=380, height=800)); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(500); pg.evaluate("location.hash=%s" % json.dumps("game-" + gid)); pg.wait_for_timeout(800)
    pg.evaluate("localStorage.setItem('dfl.view','chalk')"); pg.reload(); pg.wait_for_timeout(500); pg.evaluate("location.hash=%s" % json.dumps("game-" + gid)); pg.wait_for_timeout(900)
    on = pg.evaluate("!!REPLAY.stage() && !!REPLAY.stage().chalk")
    if not on: pg.click("#anim"); pg.wait_for_timeout(300); on = pg.evaluate("!!REPLAY.stage() && !!REPLAY.stage().chalk")
    ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("on a phone the board remembers the view, fits the screen and draws", on and ow <= 0 and pg.evaluate(PIXELS) > 12 and not errs, f"on {on} overflow {ow} {errs[:2]}")
    br.close()
srv.shutdown()
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED")); sys.exit(1 if failures else 0)
