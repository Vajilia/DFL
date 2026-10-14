"""The 3D view of the animated field (site/stage3d.js): an option next to the 2D field, drawn from the same scenes.

  1  the poses of the 3D figures are finite for every pose the scenes use (node)
  2  with no way to fetch three.js the field stays 2D, says so, and the page shows no error
  3  with three.js: the sideline and the behind views draw (not a blank picture), every figure and the ball sit where the stage says they are, every kind of play draws
     at the start, middle and end of its scene, a replay runs with the view on, and the choice is remembered
  4  switching back to 2D removes the 3D picture

three.js is not part of the page (it is fetched from a CDN when somebody switches the view on), so this check serves its own copy: set DFL_THREE_JS to a three.min.js (release r128),
or let the check fetch it with npm.

    python engine/check_stage3d.py
"""
import functools, http.server, io, json, os, shutil, subprocess, sys, tempfile, threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site

failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok: failures.append(name)

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
# 1 ------------------------------------------------------------------------------------------------------------------------------
if shutil.which("node"):
    js = """const S = require(process.argv[1]); let bad = 0, n = 0;
for (const p of ["stand","stance","kneel","block","tackle","throw","catch","cele","kick","down","run","back","nonsense",undefined]) for (const ph of [0, 1.3, 77.7]) for (const c of [0, 3.1]) { const q = S.poseOf(p, ph, c); n++; for (const k of Object.keys(q)) if (k !== "down" && !Number.isFinite(q[k])) bad++; }
console.log(JSON.stringify({ n, bad }));"""
    r = subprocess.run(["node", "-e", js, os.path.join(ROOT, "site", "stage3d.js")], capture_output=True, text=True)
    try: o = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: o = {"n": 0, "bad": 1}
    check("every pose gives finite angles", o["n"] > 50 and o["bad"] == 0, r.stderr[-300:])
else:
    print("SKIP the poses are not checked here (node is not installed)")

three = os.environ.get("DFL_THREE_JS")
if not three or not os.path.exists(three):
    d = tempfile.mkdtemp()
    if shutil.which("npm"):
        subprocess.run(["npm", "install", "--prefix", d, "three@0.128.0", "--silent"], capture_output=True)
        three = os.path.join(d, "node_modules", "three", "build", "three.min.js")
try:
    from playwright.sync_api import sync_playwright
    from PIL import Image
except ImportError:
    print("SKIP the page is not checked here (playwright or PIL is not installed)"); sys.exit(1 if failures else 0)

def serve(root):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/index.html"
root = tempfile.mkdtemp(); build_site.build(os.path.join(root, "index.html"), 7, rules=5)
srv, url = serve(root)
ARGS = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
def colours(pg):
    im = Image.open(io.BytesIO(pg.query_selector("#stagewrap").screenshot())).convert("RGB").resize((200, 70))
    return len(set((r >> 4, g >> 4, b >> 4) for r, g, b in im.getdata()))
def open_game(pg):
    pg.goto(url); pg.wait_for_timeout(500)
    gid = pg.evaluate("D.games.find(g=>g.id).id"); pg.evaluate("location.hash=%s" % json.dumps("game-" + gid)); pg.wait_for_timeout(800)
    return gid

with sync_playwright() as pw:
    # 2 --------------------------------------------------------------------------------------------------------------------------
    br = pw.chromium.launch(args=ARGS); errs = []
    pg = br.new_page(viewport=dict(width=1100, height=900)); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/cdnjs.cloudflare.com/**", lambda r: r.abort())
    gid = open_game(pg)
    check("the page offers the 3D view next to the animation switch", pg.evaluate("!document.getElementById('view3d').hidden && document.getElementById('view3d').textContent === 'View: 2D'"))
    pg.click("#view3d"); pg.wait_for_timeout(1500)
    st = pg.evaluate("[REPLAY.stage().mode, document.getElementById('view3d').textContent, document.getElementById('animnote').textContent, !!document.querySelector('canvas.gl')]")
    check("when three.js cannot be fetched the field stays 2D and says so", st[0] == "2d" and st[1] == "View: 2D" and "3D" in st[2] and not st[3] and not errs, f"{st} {errs[:2]}")
    br.close()
    if not three or not os.path.exists(three):
        print("SKIP the 3D drawing is not checked here (no copy of three.js: set DFL_THREE_JS)"); print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED")); sys.exit(1 if failures else 0)
    # 3 --------------------------------------------------------------------------------------------------------------------------
    THREE = open(three, "rb").read()
    br = pw.chromium.launch(args=ARGS); errs = []
    pg = br.new_page(viewport=dict(width=1100, height=900)); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" and "ERR_" not in m.text and "Failed to load resource" not in m.text else None)
    pg.route("**/cdnjs.cloudflare.com/**", lambda r: r.fulfill(status=200, content_type="application/javascript", body=THREE))
    gid = open_game(pg)
    pg.click("#view3d"); pg.wait_for_timeout(2500)
    m = pg.evaluate("[REPLAY.stage().mode, document.getElementById('view3d').textContent, !!document.querySelector('canvas.gl'), localStorage.getItem('dfl.view')]")
    check("the first click starts the 3D sideline view, and the choice is remembered", m == ["side", "View: 3D sideline", True, "side"], str(m))
    plays = pg.evaluate("D.box[%s].p" % json.dumps(gid))
    ri = next(i for i, p in enumerate(plays) if p[6] == "PC" and i > 5)
    pg.evaluate("([i]) => { const sc = REPLAY.sceneFor(i); REPLAY.stage().showAt(sc, sc.dur * .5); }", [ri]); pg.wait_for_timeout(300)
    check("the sideline view draws a picture (turf, stands, players), not a blank", colours(pg) > 40, str(colours(pg)))
    # every figure and the ball stand where the stage says
    off = pg.evaluate("""() => { const st = REPLAY.stage(), r = st.r3, cur = st.cur0 || st.current(); let worst = 0;
        cur.act.forEach((a, i) => { const p = r.fig[i].root.position; worst = Math.max(worst, Math.abs(p.x - a.x), Math.abs(p.z - a.y), Math.abs(p.y)); });
        const b = cur.ball, q = r.ballG.position; return [worst, Math.abs(q.x - b.x), Math.abs(q.z - b.y), Math.abs(q.y - (b.z + .26))]; }""")
    check("all 22 figures and the ball stand where the stage puts them", max(off) < 1e-4, str(off))
    pr = pg.evaluate("() => { const st = REPLAY.stage(), p = st.r3.project(60, 26, 0); return [p.x, p.y, st.W, st.Hh, p.ok]; }")
    check("a point of the field projects onto the picture", 0 <= pr[0] <= pr[2] and 0 <= pr[1] <= pr[3] and pr[4], str(pr))
    pg.click("#view3d"); pg.wait_for_timeout(300)
    m = pg.evaluate("[REPLAY.stage().mode, document.getElementById('view3d').textContent]")
    pg.evaluate("([i]) => { const sc = REPLAY.sceneFor(i); REPLAY.stage().showAt(sc, sc.dur * .5); }", [ri]); pg.wait_for_timeout(300)
    check("the second click moves the camera behind the offense and still draws", m == ["behind", "View: 3D behind the offense"] and colours(pg) > 40, f"{m} {colours(pg)}")
    kinds = pg.evaluate("""(gid) => { const b = D.box[gid], out = {}; b.p.forEach((p, i) => { if (!(p[6] in out)) out[p[6]] = i; }); return out; }""", gid)
    bad = pg.evaluate("""(kinds) => { const st = REPLAY.stage(), bad = []; for (const v of ['side', 'behind']) { st.set3d(v); for (const [k, i] of Object.entries(kinds)) { const sc = REPLAY.sceneFor(i);
        for (const f of [0, .2, .5, .8, 1]) { try { st.showAt(sc, sc.dur * f); } catch (e) { bad.push(v + ' ' + k + ': ' + e.message); } } } } return bad; }""", kinds)
    check(f"every kind of play ({', '.join(sorted(kinds))}) draws in both views at the start, the middle and the end", not bad and len(kinds) >= 8, str(bad[:3]))
    pg.select_option("#speed", "4"); pg.click("#watch"); pg.wait_for_timeout(8000)
    st = pg.evaluate("[REPLAY.stage().stats, REPLAY.state().i, REPLAY.stage().mode]")
    check("a replay at 4x runs with the 3D view on and no error", st[0]["animated"] >= 1 and st[1] >= 2 and st[2] != "2d" and not errs, f"{st} {errs[:2]}")
    pg.reload(); pg.wait_for_timeout(500); pg.evaluate("location.hash=%s" % json.dumps("game-" + gid)); pg.wait_for_timeout(3000)
    check("a viewer who chose 3D finds it on the next game page", pg.evaluate("REPLAY.stage().mode") in ("side", "behind") and pg.evaluate("!!document.querySelector('canvas.gl')"))
    # 4 --------------------------------------------------------------------------------------------------------------------------
    while pg.evaluate("REPLAY.stage().mode") != "2d": pg.click("#view3d"); pg.wait_for_timeout(300)
    r = pg.evaluate("[!!document.querySelector('canvas.gl'), document.getElementById('stage').style.position, localStorage.getItem('dfl.view')]")
    check("back to 2D the 3D picture is gone and the flat field is drawn again", r == [False, "", "2d"] and colours(pg) > 40, f"{r} {colours(pg)}")
    br.close()
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED")); sys.exit(1 if failures else 0)
