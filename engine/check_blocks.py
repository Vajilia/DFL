"""The blocks pacing (2026-10-13): a league that runs block after block, about 30-minute games, 2 minutes between blocks and 5 between weeks, a pause button that costs the
league nothing but the time it was paused, and a restart that changes nothing.

    python engine/check_blocks.py
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


MIN, HR = 60000, 3600 * 1000
OPEN = int(dt.datetime(2026, 10, 17, 19, 0).timestamp() * 1000)
META = dict(seed=7, epoch_ms=OPEN, pacing="blocks", real_per_game=L.BLOCK_REAL_PER_GAME, halftime=L.HALFTIME_PAUSE)

out = tempfile.mkdtemp()
r = L.Runner(out, 7, OPEN, dict(META))
w = r.world
s1 = w.season_at(OPEN)
check("the first kickoff is the epoch", min(g["start"] for g in s1.games) == OPEN)
check("before the epoch there is no season", L.World(7, OPEN, "blocks").season_at(OPEN - 1) is None)
regs = [g for g in s1.games if g["group"] == "reg"]
check("all 360 regular games, 28 Ambassador games and 13 playoff games are placed", len(regs) == 360 and sum(g["group"] == "amb" for g in s1.games) == 28 and sum(g["group"] == "po" for g in s1.games) == 13)
wins = sorted(s1.window_start.values())
check("103 blocks in a year", len(wins) == 103, str(len(wins)))
blocks = {}
for g in s1.games:
    blocks.setdefault(min(x for x in wins if x <= g["start"] + 1) if False else g["start"], []).append(g)
check("every block's games start together", len(blocks) == 103)
ends = [max(g["end"] for g in blocks[t]) for t in sorted(blocks)]
starts = sorted(blocks)
gaps = [(b - a) / MIN for a, b in zip(ends, starts[1:])]
# a game that spills into overtime still ends before the next block: gap is exactly 2 or 5 minutes measured from the longest game of the block
check("blocks follow one another by exactly 2 minutes, or 5 minutes between weeks and playoff rounds", all(abs(x - 2) < 1e-6 or abs(x - 5) < 1e-6 for x in gaps) and sum(abs(x - 5) < 1e-6 for x in gaps) >= 20, str(sorted(set(round(x, 3) for x in gaps))))
check("no game runs into the next block", all(g["end"] <= s for t in starts[:-1] for g in blocks[t] for s in [starts[starts.index(t) + 1]]))
lens = [(g["end"] - g["start"]) / MIN for g in regs]
mean_block = sum((e - s) / MIN for s, e in zip(starts, ends)) / len(starts)
check("a regular game takes about 30 real minutes (25 to 40)", 25 <= sum(lens) / len(lens) <= 35 and all(20 <= x <= 50 for x in lens), f"{sum(lens) / len(lens):.1f} {min(lens):.1f} {max(lens):.1f}")
check("the mean block takes about 30 minutes", 28 <= mean_block <= 33, f"{mean_block:.1f}")
yh = (s1.final_end - OPEN) / HR
check("a season takes 54 to 60 hours", 54 <= yh <= 60, f"{yh:.1f}")
sch = s1.schedule_file(OPEN)
check("season.json carries the pace the page needs", sch["pacing"] == "blocks" and sch["real_per_game"] == L.BLOCK_REAL_PER_GAME and sch["halftime"] == L.HALFTIME_PAUSE and abs(sch["year_hours"] - yh) < 0.06, str(sch["year_hours"]))
s2 = w.season_at(s1.final_end + L.WRAP_UP_MS + 1)
check("year 2 begins WRAP_UP after the Coronation and its first kickoff is OFFSEASON after the Coronation", w.year == 2 and min(g["start"] for g in s2.games) == s1.final_end + L.OFFSEASON_MS)
check("a year does not begin before the Coronation is over", L.World(7, OPEN, "blocks").season_at(s1.final_end + L.WRAP_UP_MS - 1).n == 1)
check("the champion of year 1 is in the history", w.history and w.history[0]["champion"] == s1.res.champion)

# ---- the feed never runs ahead of the clock -------------------------------------------------------------------------------
out = tempfile.mkdtemp()
r = L.Runner(out, 7, OPEN, dict(META))
res = r.tick(OPEN - HR)
check("before the first kickoff the feed is empty", res is None and read(out, "results.json")["final"] == {} and not os.path.exists(os.path.join(out, "g")))
res = r.tick(OPEN + 10 * MIN)
check("ten minutes in, the first block is live and nothing is final", len(res["live"]) > 0 and res["final"] == {} and res["year"] == 1 and res["paused"] is False and res["shift"] == 0)
s = r.world.season

# ---- pause --------------------------------------------------------------------------------------------------------------------
T0 = OPEN + 10 * MIN
ctl = os.path.join(out, "control.json")
json.dump({"paused": True}, open(ctl, "w"))
a = r.tick(T0 + 5 * MIN)                     # 5 minutes after the first look: paused at the effective 15 minutes
b = r.tick(T0 + 8 * HR)                      # eight hours later it is still paused
check("a paused league does not move: the same moment, the same plays, a new real time", a["t"] == b["t"] == T0 + 5 * MIN and a["paused"] and b["paused"] and a["live"] == b["live"] and a["final"] == b["final"], f"{a['t']} {b['t']}")
check("the pause is recorded in meta.json", read(out, "meta.json")["pauses"] == [[T0 + 5 * MIN, None]])
json.dump({"paused": False}, open(ctl, "w"))
c = r.tick(T0 + 8 * HR + 10 * MIN)
c2 = r.tick(T0 + 8 * HR + 20 * MIN)
check("resuming picks up exactly where it stopped, and then a minute is a minute", c["t"] == a["t"] and c2["t"] == a["t"] + 10 * MIN and not c["paused"], f"{c['t'] - a['t']} {c2['t'] - a['t']}")
check("the page is told how much real time was lost to pauses", c2["shift"] == 8 * HR + 5 * MIN, str(c2["shift"] / HR))
# a restart in the middle of all this changes nothing: the pauses are in meta.json
r2 = L.Runner(out, 7, OPEN, read(out, "meta.json"))
d = r2.tick(T0 + 9 * HR)
e = r.tick(T0 + 9 * HR)
check("a runner restarted from meta.json (pauses included) writes what the one that ran all along writes", d == e and d["shift"] == e["shift"], f"{d['t']} {e['t']}")
# a pause that is still on when the service restarts stays on
json.dump({"paused": True}, open(ctl, "w"))
r.tick(T0 + 10 * HR)
r3 = L.Runner(out, 7, OPEN, read(out, "meta.json"))
f1 = r3.tick(T0 + 11 * HR)
check("a pause that was on when the service restarted is still on", f1["paused"] and f1["t"] == r.tick(T0 + 12 * HR)["t"])
json.dump({"paused": False}, open(ctl, "w"))
g1 = r3.tick(T0 + 12 * HR)
g2 = r3.tick(T0 + 12 * HR + MIN)
check("and ends when the button is released", not g1["paused"] and g1["t"] == f1["t"] and g2["t"] == g1["t"] + MIN, f"{g1['t'] - f1['t']} {g2['t'] - g1['t']}")

# ---- nothing is ahead of the clock, a game's final equals the engine's box score ----------------------------------------------
out = tempfile.mkdtemp()
r = L.Runner(out, 7, OPEN, dict(META))
s = r.world.season_at(OPEN)
first = min(s.games, key=lambda g: (g["start"], g["id"]))
res = r.tick(first["end"] + 1000)
f = read(out, "g", f"1_{first['id']}.json")
check("at the final whistle the game is final and equal to the engine's box score", res["final"][first["id"]] == [first["hp"], first["ap"], first["ot"]] and f["p"] == first["box"]["p"] and not f["live"])
res = r.tick(s.final_end + 1000)
check("the champion is known only when the Coronation is over, and the year's finals add up", res.get("champion") == s.res.champion and len(res["final"]) == 360 + 28 + 13)

# ---- a restart changes nothing ---------------------------------------------------------------------------------------------------
t2 = s.final_end + L.OFFSEASON_MS + 5 * HR
a = r.tick(t2)
b = L.Runner(tempfile.mkdtemp(), 7, OPEN, dict(META)).tick(t2)
check("a runner started afresh at a later time writes exactly what the one that ran all along writes", a == b and a["year"] == 2 and a["history"], str(a.get("history")))

# ---- --init for a new league ----------------------------------------------------------------------------------------------------
out3 = tempfile.mkdtemp()
L.main(["--out", out3, "--opener-at", "2026-10-17T19:00", "--init"])
m = read(out3, "meta.json")
check("--init makes a blocks league whose first kickoff is the opener", sorted(os.listdir(out3)) == ["meta.json"] and m["pacing"] == "blocks" and m["epoch_ms"] == OPEN and m["real_per_game"] == L.BLOCK_REAL_PER_GAME and "engine_commit" in m, str(m))

# ---- the page reads its pace from season.json -----------------------------------------------------------------------------------
tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "template.html"), encoding="utf-8").read()
check("the page takes the pace from season.json, and shows pauses", "FEED.cur.S.real_per_game" in tpl and "wallShift" in tpl and "paused" in tpl)

print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
