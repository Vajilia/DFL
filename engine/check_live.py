"""The live runner (2026-10-12): the feed never runs ahead of the clock, a game's final equals the engine's box score, a restart changes nothing,
and every year's games find their kickoff times, rotation included.

    python engine/check_live.py
"""
import datetime as dt
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live as L

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def read(out, *p):
    return json.load(open(os.path.join(out, *p)))


EPOCH = int(dt.datetime(2026, 10, 13, 0, 0).timestamp() * 1000)
HR = 3600 * 1000
out = tempfile.mkdtemp()
r = L.Runner(out, 7, EPOCH)
s1 = r.world.advance_to(1)
regs = [g for g in s1.games if g["group"] == "reg"]
check("all 360 regular games, 28 Ambassador games and 13 playoff games are on the clock", len(regs) == 360 and sum(g["group"] == "amb" for g in s1.games) == 28 and sum(g["group"] == "po" for g in s1.games) == 13)
check("a game's real start follows its league date and kickoff, in order", all(a["start"] <= b["start"] for a, b in zip(sorted(regs, key=lambda g: g["when"]), sorted(regs, key=lambda g: g["when"])[1:])))
check("the first kickoff is the workbook's opener (Saturday 1 July 2000, 5:30pm)", min(regs, key=lambda g: g["start"])["when"] == "2000-07-01T17:30")
check("the Coronation ends before the next league year begins", s1.final_end < L.year_start_ms(EPOCH, 2) - 0.5 * HR, f"{(s1.final_end - L.year_start_ms(EPOCH, 2)) / HR:.2f} h")
check("a game takes about 36 real minutes", all(30 <= (g["end"] - g["start"]) / 60000 <= 45 for g in regs))
wins = sorted(s1.window_start.values())
check("kickoff windows keep the league's order and are at least 38 real minutes apart (the Sunday windows no longer overlap)", all(b - a >= L.SLOT_GAP_MS for a, b in zip(wins, wins[1:])) and sorted(s1.window_start, key=s1.window_start.get) == sorted(s1.window_start))
late = [g["id"] for g in s1.games if g["group"] != "amb" and any(w > g["start"] and w < g["end"] - 5 * 60000 for w in wins)]
check("every game is over before the next window opens (an overtime game may spill up to five minutes into it)", not late, str(late[:5]))
check("Ambassador games play inside a window", all(g["start"] in wins for g in s1.games if g["group"] == "amb"))
margins = []
for n in (2, 5, 6, 9):
    margins.append((L.year_start_ms(EPOCH, n + 1) - r.world.advance_to(n).final_end) / HR)
check("in every year tried the Coronation is over more than half an hour before the next year begins", min(margins) > 0.5, str(margins))
check("years 2, 5, 6 and 9 (the first swap of conferences, and a full cycle) find a kickoff for every game", r.world.year == 9)
check("the clock and the opener agree: the epoch chosen for an opener puts the first kickoff there", abs(L.real_ms(L.opener_epoch(dt.datetime(2026, 10, 13, 9, 0)), 1, dt.datetime(2000, 7, 1, 17, 30)) - dt.datetime(2026, 10, 13, 9, 0).timestamp() * 1000) < 1000)

# ---- nothing runs ahead of the clock (a fresh runner on year 1) ------------------------------------------------------------------
out = tempfile.mkdtemp()
r = L.Runner(out, 7, EPOCH)
s = r.world.advance_to(1)
res0 = r.tick(EPOCH - HR)
check("before Founding Day the feed is empty", res0 is None and read(out, "results.json")["final"] == {} and not os.path.exists(os.path.join(out, "g")))
first = min(regs, key=lambda g: g["start"])
res = r.tick(first["start"] - 60000)
check("before the first kickoff there are no finals, no live games, no game files and no seeds", res["final"] == {} and res["live"] == [] and not os.path.exists(os.path.join(out, "g")) and "seeds" not in res)
sch = read(out, "season.json")
check("the schedule carries no scores and no playoff matchups", all(len(x) == 7 for x in sch["games"]) and all(len(x) == 4 for x in sch["po"]) and '"champion"' not in json.dumps(sch))
mid = first["start"] + 10 * 60 * 1000
res = r.tick(mid)
live_ids = res["live"]
files = {i: read(out, "g", f"1_{i}.json") for i in live_ids}
ok_prefix = True
for i, f in files.items():
    g = s.by_id[i]
    k = s.revealed(g, mid)
    ok_prefix = ok_prefix and f["live"] and len(f["p"]) == k and f["p"] == g["box"]["p"][:k] and all(L.play_offset_ms(p) <= mid - g["start"] for p in f["p"]) and "tm" not in f and "hp" not in f
check("a game in progress shows only the plays the clock has reached, with no totals and no score", bool(live_ids) and ok_prefix, str(live_ids[:3]))
check("a game in progress is not yet a final", all(i not in res["final"] for i in live_ids))
dr_ok = all(len(f["dr"]) <= (f["p"][-1][13] if f["p"] else 0) + 0 for f in files.values())
check("only finished drives are in a game in progress", dr_ok)
after = first["end"] + 1000
res = r.tick(after)
g = first
f = read(out, "g", f"1_{g['id']}.json")
check("at the final whistle the game is final, in the feed and equal to the engine's box score", g["id"] in res["final"] and res["final"][g["id"]] == [g["hp"], g["ap"], g["ot"]] and not f["live"]
      and f["p"] == g["box"]["p"] and f["dr"] == g["box"]["dr"] and f["tm"] == g["box"]["tm"])
# the playoffs are announced shortly before they are played, and the season's outcome only when it is decided
po = [g for g in s.games if g["group"] == "po"]
wc = min(po, key=lambda g: g["start"])
res = r.tick(s.reg_end - 1000)
check("before the last regular game ends there are no seeds and no division ranks", "seeds" not in res and "division_ranks" not in res)
res = r.tick(s.reg_end + 1000)
check("once the regular season is over the seeds and division ranks are known", "seeds" in res and "division_ranks" in res and "champion" not in res)
res = r.tick(wc["start"] - L.ANNOUNCE - 60000)
check("a playoff matchup is not announced until shortly before kickoff", wc["id"] not in res["po"] and all(i not in res["po"] for i in [g["id"] for g in po if g["start"] > wc["start"] + 6 * HR]))
res = r.tick(wc["start"] - L.ANNOUNCE + 1000)
check("and then it is", res["po"].get(wc["id"]) == [wc["home"], wc["away"]])
res = r.tick(s.final_end - 1000)
check("the champion is not known until the Coronation is over", "champion" not in res and "exits" not in res)
res = r.tick(s.final_end + 1000)
check("then the champion and the playoff exits are", res.get("champion") == s.res.champion and "exits" in res)
check("a finished year's finals add up to its box scores", len(res["final"]) == 360 + 28 + 13 and all(res["final"][g["id"]][:2] == [g["hp"], g["ap"]] for g in s.games))

# ---- a restart changes nothing ---------------------------------------------------------------------------------------------------
t2 = L.year_start_ms(EPOCH, 2) + 90 * HR
a = r.tick(t2)
out2 = tempfile.mkdtemp()
b = L.Runner(out2, 7, EPOCH).tick(t2)
check("a runner started afresh at a later time writes exactly what the one that ran all along writes (history of champions included)", a == b and a["history"] and a["year"] == 2, str(a["history"]))
# ---- the live page build holds no result of the autopilot season -------------------------------------------------------------------
import re
import build_site
pg = tempfile.mktemp(suffix=".html")
build_site.build(pg, 7, live=True)
html = open(pg, encoding="utf-8").read()
m_ = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
D = json.loads(m_.group(1).replace("<\\/", "</")) if m_ else None
check("the live page can be read back and is marked live", D is not None and D.get("live") is True)
if D:
    check("the live page holds no game, no play, no seed, no champion and no club record", not D["games"] and not D["ambassador"] and not D["playoffs"] and not D["box"] and not D["seeds"]
          and not D["division_ranks"] and D["champion"] is None and all(c["record"]["w"] == c["record"]["l"] == c["record"]["pf"] == 0 for c in D["clubs"]))
os.unlink(pg)
# --init writes the meta file and nothing else, and the service then carries on from it
out3 = tempfile.mkdtemp()
L.main(["--out", out3, "--opener-at", "2026-10-17T09:00", "--init", "--pacing", "legacy"])
m = read(out3, "meta.json")
check("--init fixes the opener in meta.json and starts nothing", sorted(os.listdir(out3)) == ["meta.json"] and m["epoch_ms"] == L.opener_epoch(dt.datetime(2026, 10, 17, 9, 0)))
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
