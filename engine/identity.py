"""The clubs' real identities and the first season's schedule, from the Commissioner's workbook (data/teams.csv, data/schedule_2000.csv; engine/import_workbook.py
made them).

A club is its city and nickname ("Oklahoma City Outlaws"), its abbreviation, venue, location and three colours. Each division lists its five clubs by their
2000 seeding and the club that starts in exile, and that is how the founding league is laid out: engine team ids run in the workbook's order, six to a
division (seeds 1 to 5, then the exile), the first season's tiers are the seeds, and the eight exiled clubs start in exile. The first season's schedule is the
workbook's own (it is checked against the rulebook here).

The workbook's schedule is a SKELETON: every game is between two slots (conference, division, seed), not two named clubs. The first seeds were drawn by chance;
from then on each division's clubs are re-seeded by the previous season's final division rankings (the engine's `next_tiers`, with the eight returning exiles
placed by the rulebook), and the same slot layout is filled by whoever now holds each seed. So the template is fixed, it is endless, and the NFL's rules are
adapted to it rather than the other way round. `slot_template` makes it; `schedule.build_schedule` fills it every season. Nothing about a club's identity is
read by any rule; it is how the league is shown and told.
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict
from typing import Dict, List

import rules as R

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_teams() -> List[dict]:
    """The 48 clubs in engine order: Western then Eastern, divisions in the workbook's order, seeds 1 to 5 and then the exile."""
    with open(os.path.join(DATA, "teams.csv"), newline="") as f:
        rows = list(csv.DictReader(f))
    order_c = {c: i for i, c in enumerate(R.CONFERENCES)}
    divs: Dict[tuple, int] = {}
    for r in rows:                                   # divisions keep the workbook's order within each conference
        divs.setdefault((r["conference"], r["division"]), len(divs))
    for r in rows:
        r["club_id"] = int(r["club_id"])
        r["name"] = f"{r['city']} {r['nickname']}"
        r["exile"] = r["seed"] == "Exile"
        r["seed"] = 6 if r["exile"] else int(r["seed"])
    rows.sort(key=lambda r: (order_c[r["conference"]], divs[(r["conference"], r["division"])], r["seed"]))
    return rows


def apply(teams: list) -> None:
    """Lay the identities over a new league's 48 team objects (before the rosters are made): names, seeds as tiers, the eight exiles."""
    rows = load_teams()
    assert len(rows) == len(teams) == R.TOTAL_TEAMS
    for t, r in zip(teams, rows):
        assert t.conf == R.CONFERENCES.index(r["conference"]), "the workbook's conference order must match the engine's"
        t.name = r["name"]
        t.identity = {k: r[k] for k in ("club_id", "abbr", "city", "nickname", "venue", "location", "conference", "division",
                                         "primary", "primary_hex", "secondary", "secondary_hex", "tertiary", "tertiary_hex")}
        if r["exile"]:
            t.status, t.tier = "exiled", None
        else:
            t.status, t.tier = "active", r["seed"]


def first_season_games(teams: list) -> List[tuple]:
    """The workbook's first-season schedule as (week, home id, away id, kind), with the engine's own team ids; kind follows the rulebook's blocks."""
    by_name = {t.name: t for t in teams}
    out = []
    with open(os.path.join(DATA, "schedule_2000.csv"), newline="") as f:
        for r in csv.DictReader(f):
            if not r["season"]:
                continue
            w = int(r["week"])
            a, h = by_name[r["away"]], by_name[r["home"]]
            if w <= R.WEEKS_NON_CONFERENCE[1]:
                kind = "nonconf"
            elif a.division_id == h.division_id:
                kind = "division"
            else:
                kind = "tier"
            out.append((w, h.id, a.id, kind))
    return out


def slot_template(teams: list) -> List[tuple]:
    """The workbook's first season as a fixed slot template: (week, home slot, away slot, kind), slot = (conference, division, seed). Call after `apply`."""
    slot = {t.id: (t.conf, t.div, t.tier) for t in teams if t.status == "active"}
    return [(w, slot[h], slot[a], k) for w, h, a, k in first_season_games(teams)]


def slot_times(teams: list) -> Dict[tuple, tuple]:
    """(week, home slot, away slot) -> (game number, day offset from the week's Saturday, kickoff), the workbook's timing for each slot game. Call after `apply`."""
    import datetime as dt
    import calendar_dfl as CAL
    by_name = {t.name: t for t in teams}
    out = {}
    with open(os.path.join(DATA, "schedule_2000.csv"), newline="") as f:
        for r in csv.DictReader(f):
            if not r["season"]:
                continue
            w = int(r["week"])
            h, a = by_name[r["home"]], by_name[r["away"]]
            day = dt.date.fromisoformat(r["date"]) - CAL.week_saturday(2000, w)
            out[(w, (h.conf, h.div, h.tier), (a.conf, a.div, a.tier))] = (int(r["game"]), day.days, r["kickoff"])
    return out


def game_times() -> Dict[tuple, tuple]:
    """(week, game number) -> (date, kickoff, away name, home name), from the workbook, for showing the first season."""
    out = {}
    with open(os.path.join(DATA, "schedule_2000.csv"), newline="") as f:
        for r in csv.DictReader(f):
            if r["season"]:
                out[(int(r["week"]), int(r["game"]))] = (r["date"], r["kickoff"], r["away"], r["home"])
    return out
