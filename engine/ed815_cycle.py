"""Isolated Edition 8.15 recursive season handoff for schedule and standings.

No football scores are invented here: results are supplied by a game engine or
test harness. This module enforces that they cover the exact current fixtures,
then ranks clubs and transmits the next season's seeds and ambassadors.

This is a structural reference path, not a production league/live runner.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
from typing import Mapping

import ed815_calendar as CAL
import ed815_standings as ST


@dataclass(frozen=True)
class SeasonStructure:
    season: int
    seeded_divisions: dict
    ambassadors: dict
    fixtures: tuple


def build_structure(season: int, seeded_divisions: dict,
                    ambassadors: dict, template_path=None) -> SeasonStructure:
    if season < 1:
        raise ValueError("season must be positive")
    if set(seeded_divisions) != set(CAL.DIVISION_ORDER) or set(ambassadors) != set(CAL.DIVISION_ORDER):
        raise ValueError("exactly eight canonical divisions required")
    ids = []
    for div in CAL.DIVISION_ORDER:
        active = list(seeded_divisions[div])
        if len(active) != 5 or len(set(active)) != 5:
            raise ValueError("five distinct active clubs required per division")
        if ambassadors[div] in active:
            raise ValueError("ambassador cannot be active")
        ids.extend(active + [ambassadors[div]])
    if len(ids) != len(set(ids)) or len(ids) != 48:
        raise ValueError("48 globally unique permanent clubs required")
    fixtures = CAL.fixtures_for_season(season, seeded_divisions, template_path)
    CAL.validate_fixture_counts(fixtures, seeded_divisions)
    return SeasonStructure(season, {d:tuple(seeded_divisions[d]) for d in CAL.DIVISION_ORDER},
                           dict(ambassadors), tuple(fixtures))


def finalize_structure(current: SeasonStructure, results: list[Mapping],
                       seed: int | str, template_path=None) -> tuple[SeasonStructure, dict]:
    """Require every fixture result exactly once, then hand off eight divisions.

    Results have week, game, home, away, home_score, away_score. A result for
    an unreleased or unmatched fixture is rejected. The caller controls time
    and may invoke this only when the season has actually completed.
    """
    fixtures = {(g["week"], g["game"]):g for g in current.fixtures}
    if len(results) != len(fixtures):
        raise ValueError("all 360 results required for year-end handoff")
    seen = set()
    games = []
    for result in results:
        key = (result["week"], result["game"])
        if key in seen or key not in fixtures:
            raise ValueError("duplicate or unknown fixture result")
        seen.add(key)
        expected = fixtures[key]
        if result["home"] != expected["home"] or result["away"] != expected["away"]:
            raise ValueError("result participants differ from immutable schedule")
        games.append({"id":key, "home":result["home"],"away":result["away"],
                      "home_score":result["home_score"],"away_score":result["away_score"]})
    clubs = {cid:{"conference":div[0],"division":div[1]}
             for div,ids in current.seeded_divisions.items() for cid in ids}
    records = ST.build_records(clubs,games)
    if sum(r.wins for r in records.values()) != sum(r.losses for r in records.values()):
        raise AssertionError("win-loss conservation failed")
    if sum(r.differential for r in records.values()) != 0:
        raise AssertionError("point-differential conservation failed")
    if any(r.games_played != 18 for r in records.values()):
        raise AssertionError("wrong number of games played")
    handoffs = ST.next_season_division_seeds(clubs, records, current.ambassadors, seed)
    next_seeded = {d:tuple(handoffs[d]["next_seeds"]) for d in CAL.DIVISION_ORDER}
    next_ambassadors = {d:handoffs[d]["next_ambassador"] for d in CAL.DIVISION_ORDER}
    next_struct = build_structure(current.season+1,next_seeded,next_ambassadors,template_path)
    summary = {"completed_season":current.season,
               "next_season":next_struct.season,
               "division_orders":ST.division_orders(clubs,records,seed),
               "playoff_seeds":ST.playoff_seeds(clubs,records,seed),
               "exiled_clubs":next_ambassadors,
               "returning_clubs":dict(current.ambassadors),
               "records":records}
    return next_struct, summary
