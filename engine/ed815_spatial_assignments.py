"""Experimental pre-snap assignment vocabulary for a single spatial rush.

These are instructions to the simulation, not DFL constitutional rules.
The coach may select a lane and individual block/pursuit assignments from
legal on-field identities; no score, success chance, or outcome is prescribed.
"""
from __future__ import annotations

from collections.abc import Mapping
import math

DEFENSIVE_ACTIONS = frozenset(("pursue", "hold", "contain_lane"))


def compile_rush_plan(plan, offense_ids, defense_ids, carrier_id, fallback_lane):
    off, deff = set(offense_ids), set(defense_ids)
    if carrier_id not in off or off & deff or len(off) != 11 or len(deff) != 11:
        raise ValueError("plan needs 22 distinct on-field identities")
    if plan is None:
        plan = {}
    if not isinstance(plan, Mapping) or set(plan) - {"lane_y", "blocks", "defense"}:
        raise ValueError("invalid rush plan keys")
    lane = plan.get("lane_y", fallback_lane)
    if type(lane) not in (float, int) or not math.isfinite(lane) or not 0 <= lane <= 53.333333:
        raise ValueError("run lane outside playable field")
    blocks = plan.get("blocks", {})
    actions = plan.get("defense", {})
    if not isinstance(blocks, Mapping) or not isinstance(actions, Mapping):
        raise ValueError("assignment maps required")
    if any(p not in off or p == carrier_id or target not in deff
           for p, target in blocks.items()):
        raise ValueError("block assignment references ineligible player")
    if any(p not in deff or action not in DEFENSIVE_ACTIONS
           for p, action in actions.items()):
        raise ValueError("defensive assignment references ineligible player")
    return {
        "lane_y": lane,
        "blocks": dict(blocks),
        "defense": {p: actions.get(p, "pursue") for p in deff},
    }
