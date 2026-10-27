"""The spatial run kernel derives yards and tackles from contact, not dice."""
from __future__ import annotations

import copy

import ed815_spatial_rush as RUN
import ed815_spatial_trace as TRACE


def squads(runner_x=30.0, defender_x=8.0):
    offense = [
        {"id": f"o-{i}", "x": 20.0, "y": float(i), "speed": 0.0}
        for i in range(10)
    ] + [{"id": "carrier", "x": runner_x, "y": 26.0, "speed": 10.0}]
    defense = [
        {"id": f"d-{i}", "x": defender_x, "y": float(i), "speed": 0.0}
        for i in range(11)
    ]
    return offense, defense

offense, defense = squads(runner_x=99.4)
copy_offense, copy_defense = copy.deepcopy(offense), copy.deepcopy(defense)
r1 = RUN.simulate_rush(offense, defense, "carrier", max_ticks=40)
r2 = RUN.simulate_rush(offense, defense, "carrier", max_ticks=40)
assert r1 == r2
assert offense == copy_offense and defense == copy_defense
assert r1.reason == "touchdown" and r1.touchdown and r1.yards == 0.6
assert r1.trace[-1]["decisive_events"] == ["goal-line-crossed"]
assert TRACE.unpack(TRACE.pack(r1.trace)) == r1.trace
assert len(r1.trace[0]["players"]) == 22

offense, defense = squads()
defense[0].update(x=30.2, y=26.0)
r = RUN.simulate_rush(offense, defense, "carrier", max_ticks=40)
assert r.reason == "tackle" and not r.touchdown
assert 0 <= r.yards <= 0.5
assert r.trace[-1]["decisive_events"] == ["tackle-contact"]
assert 1 <= r.ticks < 40

offense, defense = squads()
offense[-1]["speed"] = 0.0
r = RUN.simulate_rush(offense, defense, "carrier", max_ticks=12)
assert r.reason == "whistle" and not r.touchdown and r.yards == 0
assert r.ticks == 12 and len(r.trace) == 13
assert r.trace[-1]["decisive_events"] == ["play-whistle"]

def reject(o, d, cid="carrier", **kwargs):
    try:
        RUN.simulate_rush(o, d, cid, **kwargs)
    except ValueError:
        return
    raise AssertionError("invalid spatial roster or play parameters accepted")

offense, defense = squads()
reject(offense[:-1], defense)
reject(offense, defense + [defense[-1]])
reject(offense, defense, "not-on-field")
reject(offense, defense, "carrier", lane_y=100)
reject(offense, defense, "carrier", max_ticks=0)
wrong = copy.deepcopy(offense)
wrong[1]["id"] = wrong[0]["id"]
reject(wrong, defense)
wrong = copy.deepcopy(defense)
wrong[1]["id"] = "carrier"
reject(offense, wrong)
wrong = copy.deepcopy(offense)
wrong[-1]["speed"] = float("nan")
reject(wrong, defense)

print("OK: 22-agent rushing physics prototype, contact, touchdown, deterministic trace")
