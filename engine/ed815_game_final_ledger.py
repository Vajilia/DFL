"""Edition 8.15 isolated fixture-bound final-result ledger.

Only a caller-supplied, completed game result may be recorded. This module
does not simulate games, advance the live clock, or publish results.
The entire event-chain and fixture uniqueness are checked under SQLite's
single-writer lock before insertion. The ledger is the source of truth.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping

import ed815_cycle as CYCLE
import ed815_event_store as EVENTS


def _fixtures(structure):
    by_key = {(int(f["week"]), int(f["game"])): f for f in structure.fixtures}
    if len(by_key) != 360:
        raise ValueError("expected 360 unique regular-season fixtures")
    return by_key


def _extract(structure, history):
    fixtures = _fixtures(structure)
    completed = {}
    for event in history:
        if event.get("kind") != "game_final":
            continue
        if event.get("rule_version") != EVENTS.RULE or event.get("season") != structure.season:
            raise ValueError("cross-season or wrong-version game final")
        if event.get("visibility") != "public":
            raise ValueError("completed game final must be public")
        week, game = event.get("week"), event.get("game")
        if (type(week) is not int or type(game) is not int
                or (week, game) not in fixtures or (week, game) in completed):
            raise ValueError("duplicate or invalid fixture final")
        fixture = fixtures[week, game]
        if event.get("home") != fixture["home"] or event.get("away") != fixture["away"]:
            raise ValueError("game final disagrees with immutable fixture")
        home_score, away_score = event.get("home_score"), event.get("away_score")
        if (type(home_score) is not int or type(away_score) is not int
                or home_score < 0 or away_score < 0):
            raise ValueError("game final has invalid scores")
        completed[week, game] = {
            "week": week, "game": game, "home": fixture["home"],
            "away": fixture["away"], "home_score": home_score,
            "away_score": away_score,
        }
    return completed


def record_final(conn: sqlite3.Connection, structure: CYCLE.SeasonStructure,
                 result: Mapping, *, simulated_time: str, random_key: str,
                 public_summary: str):
    """Persist one supplied result, rejecting duplicates even across writers."""
    if not isinstance(result, Mapping):
        raise TypeError("result must be a mapping")
    week, game = result.get("week"), result.get("game")
    fixtures = _fixtures(structure)
    if type(week) is not int or type(game) is not int or (week, game) not in fixtures:
        raise ValueError("unknown numbered fixture")
    fixture = fixtures[week, game]
    if result.get("home") != fixture["home"] or result.get("away") != fixture["away"]:
        raise ValueError("final participants do not match fixture")
    hs, aas = result.get("home_score"), result.get("away_score")
    if type(hs) is not int or type(aas) is not int or min(hs, aas) < 0:
        raise ValueError("final scores must be nonnegative integers")
    event = {
        "id": f"season-{structure.season}:regular:{week}:{game}:final",
        "kind": "game_final", "rule_version": EVENTS.RULE,
        "season": structure.season, "week": week, "game": game,
        "home": fixture["home"], "away": fixture["away"],
        "home_score": hs, "away_score": aas,
        "simulated_time": simulated_time,
        "ordering_key": f"season:{structure.season}:regular:{week}:{game}:final",
        "random_key": random_key,
        "participants": [fixture["home"], fixture["away"]],
        "visibility": "public",
        "public_summary": public_summary,
        "state_changes": {},
    }
    def guard(history):
        completed = _extract(structure, history)
        if (week, game) in completed:
            raise ValueError("fixture already finalized")
    return EVENTS.append(conn, event, check_existing=guard)


def recorded_results(conn: sqlite3.Connection, structure: CYCLE.SeasonStructure):
    """Replay verified events, ignoring unrelated non-game events."""
    completed = _extract(structure, EVENTS.load_verified(conn))
    return [completed[key] for key in sorted(completed)]


def finalize_recorded_season(conn: sqlite3.Connection,
                             structure: CYCLE.SeasonStructure, seed,
                             template_path=None):
    """No year-end handoff until every scheduled game has one verified final."""
    return CYCLE.finalize_structure(
        structure, recorded_results(conn, structure), seed, template_path
    )
