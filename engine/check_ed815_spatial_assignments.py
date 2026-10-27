"""Spatial assignments: legality, causal behavior and immutable plans."""
import copy

import ed815_spatial_assignments as A
import ed815_spatial_rush as R
from check_ed815_spatial_rush import squads

offense, defense = squads()
offense[-1]["speed"] = 4.0
defense[0].update(x=29.0, y=26.0, speed=11.0)
baseline = R.simulate_rush(offense, defense, "carrier", max_ticks=30)
assert baseline.reason == "tackle"
hold = {"defense": {p["id"]: "hold" for p in defense}}
plan_snapshot = copy.deepcopy(hold)
free = R.simulate_rush(offense, defense, "carrier", max_ticks=30, plan=hold)
assert free.reason == "whistle" and free.yards > baseline.yards
assert hold == plan_snapshot
assert "hold" in {p["intent"] for p in free.trace[0]["players"]}
assert R.simulate_rush(offense, defense, "carrier", max_ticks=30, plan=hold) == free

plan = {"lane_y": 24.0, "blocks": {"o-0": "d-0"},
        "defense": {"d-0": "contain_lane"}}
named = R.simulate_rush(offense, defense, "carrier", max_ticks=30, plan=plan)
assert any(p["intent"] == "block:d-0" for p in named.trace[0]["players"])
assert any(p["intent"] == "contain_lane" for p in named.trace[0]["players"])

def must_reject(p, **kwargs):
    try:
        R.simulate_rush(offense, defense, "carrier", max_ticks=30, plan=p, **kwargs)
    except ValueError:
        return
    raise AssertionError("invalid play assignment accepted")

must_reject({"blocks": {"missing": "d-0"}})
must_reject({"blocks": {"carrier": "d-0"}})
must_reject({"blocks": {"o-0": "missing"}})
must_reject({"defense": {"o-0": "hold"}})
must_reject({"defense": {"d-0": "teleport"}})
must_reject({"lane_y": float("nan")})
must_reject({"new_secret_instruction": 1})
must_reject({"blocks": ["d-0"]})
must_reject({"lane_y": 20}, lane_y=21)
must_reject(7)
print("OK: legal pre-snap assignments direct causal spatial rush behavior")
