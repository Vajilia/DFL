"""The data behind the read-only website (the Commissioner, 2026-10-12): the founding league as it stood on Founding Day, and its first season as played.

`export(seed)` builds a plain dictionary (JSON-safe, nothing the engine needs back) and `write(path, seed)` saves it. The site shows this and nothing else: it holds no
rules, so it cannot disagree with the engine. The first season is played with the engine's own rules on the autopilot; rosters are the Founding Day rosters (taken before
the season), and results, standings and the playoffs are the season's. Dates come from the Commissioner's workbook (the regular season) and calendar_dfl (the playoffs
and the Coronation).
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calendar_dfl as K
import founding as F
import identity as ID
import rules as R
from season import Options, run_season

POS_ORDER = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "CB", "S", "K", "P"]


def _person(c):
    if c is None:
        return None
    return dict(name=f"{c.first} {c.last}", trait=c.trait, hometown=c.hometown, age=c.age)


def _player(p):
    o = p.origin or {}
    c = p.card
    return dict(name=p.display_name or f"{c.first} {c.last}", pos=p.pos, age=p.age, ovr=round(p.ovr), college=o.get("college", ""), hometown=o.get("hometown", c.hometown),
                salary=round(p.salary, 2), years=p.years_left, trait=c.trait, bio=c.bio or "")


def export(seed: int = 7) -> dict:
    lg, rng = F.open_league(seed)
    fnd = lg.founding
    clubs = []
    for t in lg.teams:
        i = t.identity
        roster = sorted(t.roster, key=lambda p: (POS_ORDER.index(p.pos) if p.pos in POS_ORDER else 99, -p.ovr))
        story = fnd["teams"][str(t.id)]
        clubs.append(dict(
            id=t.id, abbr=i["abbr"], name=t.name, city=i["city"], nickname=i["nickname"], venue=i["venue"], location=i["location"],
            conference=i["conference"], division=i["division"], colors=[i["primary_hex"], i["secondary_hex"], i["tertiary_hex"]],
            color_names=[i["primary"], i["secondary"], i["tertiary"]], exiled=t.status == "exiled", seed=t.tier,
            founding_order=story["slot"], story=story["story"],
            people=dict(ceo=_person(t.owner), gm=_person(t.gm), head_coach=_person(t.coach), offensive_coordinator=_person(t.oc), defensive_coordinator=_person(t.dc)),
            roster=[_player(p) for p in roster], practice_squad=len(t.practice_squad), record=None))
    by_id = {c["id"]: c for c in clubs}
    times = {}
    with open(os.path.join(ID.DATA, "schedule_2000.csv"), newline="") as f:
        for r in csv.DictReader(f):
            if r["season"]:
                times[(int(r["week"]), r["home"], r["away"])] = (r["date"], r["kickoff"], int(r["game"]))
    res = run_season(lg, 1, rng, Options(engine="fast", keep_boxes=False))
    games = []
    for g in sorted(res.games, key=lambda g: (g.week, g.home)):
        h, a = by_id[g.home], by_id[g.away]
        d, k, n = times[(g.week, h["name"], a["name"])]
        games.append(dict(week=g.week, game=n, date=d, time=k, home=h["id"], away=a["id"], kind=g.kind, hp=g.home_pts, ap=g.away_pts))
    amb = [dict(week=g.week, home=g.home, away=g.away, hp=g.home_pts, ap=g.away_pts) for g in sorted(res.ambassador_games, key=lambda g: (g.week, g.home))]
    po = playoffs = K.playoffs(2000)
    stage_date = {"wild_card": po["wild_card"], "divisional": po["divisional"], "conference": po["conference"], "coronation": po["coronation"]}
    pgames = [dict(kind=g.kind, home=g.home, away=g.away, hp=g.home_pts, ap=g.away_pts) for g in res.playoff_games]
    for tid, s in res.stats.items():
        c = by_id[tid]
        c["record"] = dict(w=s.wins, l=s.losses, t=s.ties, pf=s.pf, pa=s.pa, exit=res.exits.get(tid, ""))
    for tid, s in res.ambassador_stats.items():            # the clubs in exile play the seven-game Ambassador Season
        by_id[tid]["ambassador"] = dict(w=s.wins, l=s.losses, t=s.ties, pf=s.pf, pa=s.pa)
    ranks = {did: ids for did, ids in res.division_ranks.items()}
    for did, ids in ranks.items():
        for pos, tid in enumerate(ids, start=1):
            by_id[tid]["record"]["div_rank"] = pos
    for tid in {t for s in res.seeds.values() for t in s}:
        by_id[tid]["record"]["playoffs"] = True
    seeds = {str(k): v for k, v in res.seeds.items()}
    cal = dict(year=2000, opener=K.opener(2000).isoformat(), trade_deadline=K.trade_deadline(2000).isoformat(), coronation=K.coronation(2000).isoformat(),
               playoff_dates={k: v.isoformat() for k, v in stage_date.items()},
               week_saturdays={w: K.week_saturday(2000, w).isoformat() for w in range(1, K.REGULAR_WEEKS + 1)},
               offseason=[dict(name=e.name, start=e.start.isoformat(), end=e.end.isoformat(), note=e.note) for e in K.offseason(2000)],
               season=[dict(name=e.name, start=e.start.isoformat(), end=e.end.isoformat(), note=e.note) for e in K.in_season(2000)])
    return dict(
        league="Diamond Football League", season=2000, champion=res.champion, seeds=seeds, division_ranks={str(k): v for k, v in ranks.items()},
        founding=dict(date=fnd["date"], class_of=fnd["class_of"], provenance=fnd["provenance"], events=fnd["events"], first_game=fnd["first_game"]),
        clubs=clubs, games=games, ambassador=amb, playoffs=pgames, calendar=cal, conferences=list(R.CONFERENCES),
        divisions=[dict(conference=c["conference"], name=c["division"]) for c in clubs[::6]])


def write(path: str, seed: int = 7) -> dict:
    d = export(seed)
    with open(path, "w") as f:
        json.dump(d, f, separators=(",", ":"))
    return d


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "site_data.json"
    d = write(out, int(sys.argv[2]) if len(sys.argv) > 2 else 7)
    print(out, os.path.getsize(out), "bytes;", len(d["clubs"]), "clubs;", len(d["games"]), "games;", len(d["playoffs"]), "playoff games")
