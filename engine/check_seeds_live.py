"""Playoff seeds and division order all season long (2026-10-14): while the regular season is played the feed carries the division order and the seven seeds a conference
as they would stand if the season ended now, by the league's own tiebreak procedures, and the standings page shows them (seed badges, order of clubs) and moves them
as games end. When the regular season is over the real seeds take over.

    python engine/check_seeds_live.py
"""
import functools, http.server, json, os, shutil, sys, tempfile, threading, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site, live as L

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP playwright is not installed"); sys.exit(0)

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def serve(root):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/index.html"


H = 3600 * 1000
root = tempfile.mkdtemp(); build_site.build(os.path.join(root, "index.html"), 7, live=True, rules=2)
now = int(time.time() * 1000)
meta = dict(seed=7, epoch_ms=now - 26 * H, pacing="blocks", real_per_game=L.BLOCK_REAL_PER_GAME, halftime=L.HALFTIME_PAUSE, parity="tight", rules=2)
out = os.path.join(root, "live"); os.makedirs(out); L.write_json(out + "/meta.json", meta)
run = L.Runner(out, 7, meta["epoch_ms"], meta)
res = lambda: json.load(open(out + "/results.json"))

# ---- the feed ---------------------------------------------------------------------------------------------------------------------
run.tick(meta["epoch_ms"] + 1000)
S = run.world.season
check("before any game is final there is no table to show", "now_seeds" not in res() and "now_ranks" not in res())
run.tick(now)
R = res(); fin = [i for i in R["final"] if i.startswith("r")]
check("part way through the season the feed has a division order and seeds as they would stand now, and no final seeds", len(fin) > 20 and "now_seeds" in R and "now_ranks" in R and "seeds" not in R and "division_ranks" not in R, str(len(fin)))
seeds = R["now_seeds"]; ranks = R["now_ranks"]
check("seven distinct clubs a conference and fourteen in all, five clubs a division", all(len(set(v)) == 7 for v in seeds.values()) and all(len(v) == 5 for v in ranks.values()) and len({x for v in seeds.values() for x in v}) == 14)
winners = {c: {ranks[str(4 * c + d)][0] for d in range(4)} for c in (0, 1)}
check("the top four seeds of a conference are its four division leaders", all(set(seeds[str(c)][:4]) == winners[c] for c in (0, 1)))
check("the same finals give the same table twice (a coin toss is tossed with a fixed seed)", S.table_now([i for i in R["final"] if i.startswith("r")]) == (ranks, seeds))
# with every regular game final the table is the real one
allreg = [g["id"] for g in S.games if g["group"] == "reg"]
S._now_key = None
check("with every regular season game final the table equals the real division order and seeds", S.table_now(allreg) == ({str(k): v for k, v in S.res.division_ranks.items()}, {str(k): v for k, v in S.res.seeds.items()}))

# ---- the page ---------------------------------------------------------------------------------------------------------------------
BADGES = """() => ({ seedOf: JSON.stringify(Object.entries(seedOf).sort()), now: seedNow, shown: [...document.querySelectorAll('.seed:not(.gold)')].map(b => b.textContent.trim()).length,
  titles: [...new Set([...document.querySelectorAll('.seed:not(.gold)')].map(b => /if the regular season ended now/.test(b.title)))],
  order: [...document.querySelectorAll('h3 + .tablewrap tbody')].map(tb => [...tb.rows].filter(r => !r.classList.contains('exile')).map(r => r.querySelector('a.club .nm').textContent)) })"""
srv, url = serve(root)
with sync_playwright() as pw:
    br = pw.chromium.launch(); pg = br.new_page(viewport=dict(width=1100, height=900)); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url + "#standings"); pg.wait_for_timeout(5000)
    names = {c["id"]: c["name"] for c in pg.evaluate("clubs.map(c => ({ id: c.id, name: c.name }))")}
    got = pg.evaluate(BADGES)
    check("the standings show a badge on each of the 14 clubs that would qualify, with the seed the engine gives, marked as 'if it ended now'", got["now"] and got["shown"] == 14 and json.loads(got["seedOf"]) == [[a, b] for a, b in sorted(([str(i), k + 1] for v in seeds.values() for k, i in enumerate(v)), key=lambda x: x[0])] and got["titles"] == [True], str(got["shown"]) + str(got["titles"]))
    expect_order = [[names[i] for i in ranks[str(d)]] for d in range(8)]
    check("the clubs in each division stand in the engine's order", got["order"] == expect_order, str(got["order"][:1]) + str(expect_order[:1]))
    # more games end while the page is open: the badges and the order move with them, no reload
    run.tick(now + 9 * H); pg.wait_for_timeout(7000)
    R2 = res(); fin2 = [i for i in R2["final"] if i.startswith("r")]
    got2 = pg.evaluate(BADGES)
    check("more games have ended while the page was open", len(fin2) > len(fin), f"{len(fin)} -> {len(fin2)}")
    check("the page's seeds and order moved to the new ones, matching the feed", json.loads(got2["seedOf"]) == sorted(([str(i), k + 1] for v in R2["now_seeds"].items() for k, i in enumerate(v[1])), key=lambda x: x[0]) and got2["order"] == [[names[i] for i in R2["now_ranks"][str(d)]] for d in range(8)], str(got2["order"][:1]))
    # the regular season is over: the real seeds replace the projection
    run.tick(S.reg_end + 1000); pg.wait_for_timeout(7000)
    R3 = res(); got3 = pg.evaluate(BADGES)
    check("when the regular season ends the real seeds take over (no 'if it ended now')", "seeds" in R3 and "now_seeds" not in R3 and not got3["now"] and got3["titles"] in ([False], []) and json.loads(got3["seedOf"]) == sorted(([str(i), k + 1] for v in R3["seeds"].items() for k, i in enumerate(v[1])), key=lambda x: x[0]))
    check("no script errors", not errs, str(errs[:3]))
    br.close()
srv.shutdown()
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED"))
sys.exit(1 if failures else 0)
