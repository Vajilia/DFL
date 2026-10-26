"""Public Edition 8.15 game-final projection with strict reveal cursor.

Inputs are canonical schedule rows and events produced by a separate authoritative
simulation process. This module cannot authenticate event origins; the production
event store must do that before the viewer is connected.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import ed815_standings as ST

def revealed_finals(teams, fixtures, events, *, through_sequence):
    if isinstance(through_sequence, bool) or not isinstance(through_sequence, int) or through_sequence < 0:
        raise ValueError("public reveal cursor must be a nonnegative integer")
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        raise TypeError("event log must be ordered")
    by_key = {(int(g["week"]), int(g["game"])): g for g in fixtures}
    if len(by_key) != len(fixtures):
        raise ValueError("canonical schedule includes duplicate fixture keys")
    active = {t["team_city"]: t for t in teams if t["is_active"] == "true"}
    if len(active) != 40:
        raise ValueError("expected 40 active founding clubs")
    completed = {}
    last = 0
    for event in events:
        if not isinstance(event, Mapping):
            raise TypeError("event must be a mapping")
        seq = event["sequence"]
        if isinstance(seq, bool) or not isinstance(seq, int) or seq <= last:
            raise ValueError("event log sequence is not strictly increasing")
        last = seq
        if seq > through_sequence or event.get("visibility") != "public" or event.get("kind") != "game_final":
            continue
        key = (event.get("week"), event.get("game"))
        if key not in by_key or key in completed:
            raise ValueError("public game-final is unknown or duplicated")
        expected = by_key[key]
        if event.get("home") != expected["home"] or event.get("away") != expected["away"]:
            raise ValueError("public game-final participants do not match the fixture")
        hs, aas = event.get("home_score"), event.get("away_score")
        if (isinstance(hs, bool) or isinstance(aas, bool)
                or not isinstance(hs, int) or not isinstance(aas, int)
                or min(hs, aas) < 0):
            raise ValueError("public game-final scores must be nonnegative integers")
        completed[key] = {
            "id": key,
            "home": expected["home"], "away": expected["away"],
            "home_score": hs, "away_score": aas,
        }
    clubs = {city: {"conference": t["conference"], "division": t["division"]}
             for city, t in active.items()}
    records = ST.build_records(clubs, completed.values())
    if sum(r.wins for r in records.values()) != sum(r.losses for r in records.values()):
        raise AssertionError("public standings win/loss conservation failed")
    if sum(r.points_for for r in records.values()) != sum(r.points_against for r in records.values()):
        raise AssertionError("public standings points do not conserve")
    return completed, records

def public_totals(completed):
    ties = sum(x["home_score"] == x["away_score"] for x in completed.values())
    return {
        "final_games": len(completed),
        "ties": ties,
        "total_points": sum(x["home_score"] + x["away_score"] for x in completed.values()),
    }
