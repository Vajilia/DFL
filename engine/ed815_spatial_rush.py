"""Experimental Edition 8.15 spatial rushing-play kernel.

This is intentionally narrower than a football game: 22 positional agents,
one ball carrier, simple pursuit/block contact, and a tackle or touchdown.
It produces causal yards and trace ticks; no invented final scores, passing,
realistic blocking physics, penalties, substitutions, or NFL calibration.
"""
from __future__ import annotations

import copy
import math
from collections.abc import Mapping
from dataclasses import dataclass

import ed815_spatial_trace as TRACE
import ed815_spatial_assignments as ASSIGN

DT = 0.05
DECISION_TICKS = 2  # reconsider pursuits every 0.10 simulated seconds
TACKLE_RADIUS = 0.8
BLOCK_RADIUS = 1.2
MAX_TICKS = 600  # 30 simulated seconds of this experimental one-play kernel


@dataclass(frozen=True)
class RushResult:
    yards: float
    touchdown: bool
    reason: str
    ticks: int
    trace: list


def _validate_side(players, side):
    if not isinstance(players, list) or len(players) != 11:
        raise ValueError("a spatial side must have 11 rostered players")
    names = []
    for p in players:
        if not isinstance(p, dict) or not isinstance(p.get("id"), str) or not p["id"]:
            raise ValueError("every player requires a stable ID")
        for key in ("x", "y", "speed"):
            v = p.get(key)
            if type(v) not in (float, int) or not math.isfinite(v):
                raise ValueError("finite position and speed required")
        if not 0 <= p["x"] <= 100 or not 0 <= p["y"] <= 53.333333:
            raise ValueError("player starts outside field")
        if not 0 <= p["speed"] <= 12:
            raise ValueError("speed must be a plausible yards-per-second parameter")
        names.append(p["id"])
    if len(set(names)) != 11:
        raise ValueError("player ID repeated on " + side)


def _dist(a, b):
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def _step(p, aim_x, aim_y, speed):
    dx, dy = aim_x - p["x"], aim_y - p["y"]
    length = math.hypot(dx, dy)
    if length == 0:
        return
    advance = min(length, speed * DT)
    p["x"] = round(max(0.0, min(100.0, p["x"] + advance * dx / length)), 6)
    p["y"] = round(max(0.0, min(53.333333, p["y"] + advance * dy / length)), 6)


def simulate_rush(offense, defense, carrier_id, *, lane_y=None, max_ticks=MAX_TICKS, plan=None):
    """Move all 22 agents; outcome comes from tackle contact or goal-line crossing."""
    _validate_side(offense, "offense")
    _validate_side(defense, "defense")
    if type(carrier_id) is not str:
        raise ValueError("carrier ID required")
    if type(max_ticks) is not int or not (1 <= max_ticks <= MAX_TICKS):
        raise ValueError("invalid simulation tick limit")
    home = {p["id"]: copy.deepcopy(p) for p in offense}
    away = {p["id"]: copy.deepcopy(p) for p in defense}
    if set(home).intersection(away) or carrier_id not in home:
        raise ValueError("22 distinct IDs and offense ball carrier required")
    runner = home[carrier_id]
    if isinstance(plan, Mapping) and lane_y is not None and "lane_y" in plan:
        raise ValueError("run lane specified twice")
    assignments = ASSIGN.compile_rush_plan(
        plan, home, away, carrier_id, runner["y"] if lane_y is None else lane_y
    )
    lane = assignments["lane_y"]
    start_x = runner["x"]
    frames = []
    orders = {}
    def snapshot(tick, decisive):
        units = []
        for side, roster in (("home", home), ("away", away)):
            for pid in sorted(roster):
                p = roster[pid]
                units.append({"id": pid, "side": side, "x": p["x"], "y": p["y"],
                              "intent": "carry" if pid == carrier_id else
                              ("block:" + assignments["blocks"][pid]
                               if pid in assignments["blocks"] else "block")
                              if side == "home" else assignments["defense"][pid]})
        frames.append({"tick": tick, "players": units,
                       "ball": {"x": runner["x"], "y": runner["y"], "z": 1.0,
                                "holder": carrier_id},
                       "decisive_events": decisive})
    snapshot(0, ["handoff"])
    reason = "whistle"
    ended = False
    for tick in range(1, max_ticks + 1):
        if (tick - 1) % DECISION_TICKS == 0:
            # Pure, deterministic decision layer; later playbooks replace these aims.
            for pid, p in away.items():
                mode = assignments["defense"][pid]
                orders[pid] = ((p["x"], p["y"]) if mode == "hold" else
                               (runner["x"], lane) if mode == "contain_lane" else
                               (runner["x"], runner["y"]))
        for pid in sorted(away):
            p = away[pid]
            engaged = any(_dist(p, block) <= BLOCK_RADIUS
                          for bid, block in home.items() if bid != carrier_id)
            aim_x, aim_y = orders[pid]
            _step(p, aim_x, aim_y, p["speed"] * (0.30 if engaged else 1.0))
        # Offensive blockers move to screen their closest defender.
        for pid in sorted(home):
            if pid == carrier_id:
                continue
            p = home[pid]
            target = (away[assignments["blocks"][pid]]
                      if pid in assignments["blocks"] else
                      min(away.values(), key=lambda d: (_dist(p, d), d["id"])))
            _step(p, target["x"], target["y"], p["speed"] * 0.45)
        _step(runner, 100, lane, runner["speed"])
        decisive = []
        if runner["x"] >= 100:
            reason, ended = "touchdown", True
            decisive = ["goal-line-crossed"]
        elif any(_dist(runner, p) <= TACKLE_RADIUS for p in away.values()):
            reason, ended = "tackle", True
            decisive = ["tackle-contact"]
        elif tick == max_ticks:
            decisive = ["play-whistle"]
        snapshot(tick, decisive)
        if ended:
            break
    TRACE.validate(frames)
    return RushResult(round(runner["x"] - start_x, 3),
                      reason == "touchdown", reason, len(frames) - 1, frames)
