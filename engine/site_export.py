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
from schedule import rotation
import parity
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


def _short(name: str) -> str:
    """'Kiara Johnson' -> 'K. Johnson' for the play feed."""
    parts = name.split()
    return name if len(parts) < 2 else f"{parts[0][0]}. {' '.join(parts[1:])}"


TURN = {False: 0, None: 0, "INT": 1, "FUMBLE": 2}
OT_REG, OT_POST = 600, 900


def _box(res, names: dict) -> dict:
    """One game's record for the page: players, team totals, drives and the play log, all from the engine's own box score. The page keeps no football rules:
    it replays this log and adds up what the engine recorded (engine/check_playlog.py proves the replay gives the box score back)."""
    ids = sorted(res.players)
    idx = {pid: i for i, pid in enumerate(ids)}
    pl = [[names.get(pid, f"P{pid:05d}"), res.players[pid]["pos"], res.players[pid]["team"], pid] for pid in ids]      # the id lets the Statistics page add one player up across games
    tm = [[t["plays"], t["yards"], t["pass_yds"], t["rush_yds"], t["first_downs"], t["turnovers"], t["sacks"], t["punts"], t["third_conv"], t["third_att"],
           int(round(t["top_secs"])), t["pass_cmp"], t["pass_att"], t["rush_att"], t["fga"], t["fgm"]] for t in res.team]
    dr = [[d["side"], d["quarter"], d["start"], d["plays"], d["yards"], d["secs"], d["result"], d["pts"], d["def_pts"]] for d in res.drives]
    plays, prev_left, period, last_gt = [], None, 0, 0
    v2 = bool(res.plays) and len(res.plays[0]) > 15                     # rules version 2 carries each side's timeouts left after the play
    for rec in res.plays:
        (off, q, down, to_go, pos, yds, to, kind, a, b, c, q2, left, ot, di) = rec[:15]
        if not ot:
            gt = (q2 - 1) * 900 + (900 - left)
        else:
            if prev_left is None or left > prev_left:                 # a new overtime period begins
                period += 1
                gt = max(last_gt, 3600) + 20
            else:
                gt = last_gt + max(1, prev_left - left)
            prev_left = left
        gt = max(gt, last_gt)
        last_gt = gt
        if kind in ("PN", "TO"):                                          # a penalty (number, side fouled, offender) or a timeout (team, timeouts left): numbers, not players
            row = [off, down, to_go, pos, yds, 0, kind, a, b, idx.get(c, -1) if c is not None and c >= 0 else -1, q2, left, 1 if ot else 0, di, gt]
        else:
            row = [off, down, to_go, pos, yds, TURN[to], kind, idx.get(a, -1) if a is not None else -1, idx.get(b, -1) if (b is not None and kind != "FG") else (b if b is not None else -1),
                   idx.get(c, -1) if (c is not None and kind != "FG") else (c if c is not None else -1), q2, left, 1 if ot else 0, di, gt]
        plays.append(row + (list(rec[15:17]) if v2 else []))
    out = dict(n=res.ot_periods, tb=1 if res.coin_flip_tiebreak else 0, pl=pl, tm=tm, dr=dr, p=plays)
    if v2:
        out["v"] = 2                                                      # rules version 2: penalties and timeouts are in the log
        out["pen"] = [[t["pen"], t["pen_yds"]] for t in res.team]
    return out


def calendar_for(cal_year: int) -> dict:
    """One year's calendar as the page wants it (dates as ISO strings)."""
    po = K.playoffs(cal_year)
    return dict(year=cal_year, opener=K.opener(cal_year).isoformat(), trade_deadline=K.trade_deadline(cal_year).isoformat(), coronation=K.coronation(cal_year).isoformat(),
                playoff_dates={k: po[k].isoformat() for k in ("wild_card", "divisional", "conference", "coronation")},
                week_saturdays={w: K.week_saturday(cal_year, w).isoformat() for w in range(1, K.REGULAR_WEEKS + 1)},
                offseason=[dict(name=e.name, start=e.start.isoformat(), end=e.end.isoformat(), note=e.note) for e in K.offseason(cal_year)],
                season=[dict(name=e.name, start=e.start.isoformat(), end=e.end.isoformat(), note=e.note) for e in K.in_season(cal_year)])


def play_season(lg, rng, year: int, rules: int = 1):
    """Play one league year with the drive engine and the play log on. Returns (result, {player id: full name}): every player who took part is named, the way her card
    would name her if she has no card yet (a released player is gone from every list by the season's end, so names are taken as each game is played)."""
    import game_engine
    seen, real_sim = {}, game_engine.simulate_game
    def spy(home, away, *a, **k):                         # remember who played, by name, as each game is played (a released player is gone from every list by season's end)
        for lu in (home, away):
            for grp in (lu.qb, lu.rbs, lu.wrs, lu.te, lu.ol, lu.dl, lu.lb, lu.cb, lu.s, lu.k, lu.p):
                for q in (grp if isinstance(grp, list) else [grp]):
                    seen.setdefault(q.id, q.display_name or (f"{q.card.first} {q.card.last}" if q.card else f"P{q.id:05d}"))
        return real_sim(home, away, *a, **k)
    game_engine.simulate_game = spy
    try:
        res = run_season(lg, year, rng, Options(engine="drives", keep_boxes=True, record_plays=True, engine_params=(game_engine.EngineParams(rules=rules) if rules >= 2 else None), **parity.options()))
    finally:
        game_engine.simulate_game = real_sim
    everyone = [q for t in lg.teams for q in list(t.roster) + list(t.practice_squad)] + list(lg.free_agents) + list(getattr(lg, "retired_players", ()))
    names = {p.id: (p.display_name or (f"{p.card.first} {p.card.last}" if p.card else f"P{p.id:05d}")) for p in everyone}
    names.update({pid: n for pid, n in seen.items() if not (n[0] == "P" and n[1:].isdigit())})
    import cards as CD
    for r_ in [g.result for g in res.games + res.ambassador_games + res.playoff_games if g.result is not None]:
        for pid in r_.players:                              # a player with no card yet (or already gone from every list) is named the way her card would be
            if names.get(pid, "P0")[0] == "P" and names.get(pid, "P0")[1:].isdigit() or pid not in names:
                names[pid] = " ".join(CD.make_name(lg.card_seed, pid))
    return res, names


def export(seed: int = 7, rules: int = 1) -> dict:
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
    res, names = play_season(lg, rng, 1, rules)
    box = {}
    def keep(gid, g):
        if g.result is not None and g.result.plays is not None:
            box[gid] = _box(g.result, {pid: _short(n) for pid, n in names.items()})
        return gid
    games = []
    for g in sorted(res.games, key=lambda g: (g.week, g.home)):
        h, a = by_id[g.home], by_id[g.away]
        d, k, n = times[(g.week, h["name"], a["name"])]
        games.append(dict(id=keep(f"r{g.week}_{g.home}", g), week=g.week, game=n, date=d, time=k, home=h["id"], away=a["id"], kind=g.kind, hp=g.home_pts, ap=g.away_pts, ot=g.result.ot_periods if g.result else 0))
    amb = [dict(id=keep(f"a{g.week}_{g.home}", g), week=g.week, home=g.home, away=g.away, hp=g.home_pts, ap=g.away_pts) for g in sorted(res.ambassador_games, key=lambda g: (g.week, g.home))]
    po = playoffs = K.playoffs(2000)
    stage_date = {"wild_card": po["wild_card"], "divisional": po["divisional"], "conference": po["conference"], "coronation": po["coronation"]}
    pgames = [dict(id=keep(f"p{i}", g), kind=g.kind, home=g.home, away=g.away, hp=g.home_pts, ap=g.away_pts) for i, g in enumerate(res.playoff_games)]
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
    cal = calendar_for(2000)
    evolution = []
    for y in range(2000, 2040):                           # forty seasons of the schedule: the calendar and which division fills each slot division
        flip, shift = rotation(y - 1999)
        D4 = R.DIVISIONS_PER_CONFERENCE
        evolution.append(dict(year=y, opener=K.opener(y).isoformat(), coronation=K.coronation(y).isoformat(), trade_deadline=K.trade_deadline(y).isoformat(),
                              offseason_days=K.offseason_days(y), swapped=bool(flip), shift=shift,
                              slots=[(c ^ flip) * D4 + (d - shift) % D4 + 1 for c in range(2) for d in range(D4)]))
    return dict(
        league="Diamond Football League", season=2000, champion=res.champion, seeds=seeds, division_ranks={str(k): v for k, v in ranks.items()},
        founding=dict(date=fnd["date"], class_of=fnd["class_of"], provenance=fnd["provenance"], events=fnd["events"], first_game=fnd["first_game"]),
        clubs=clubs, evolution=evolution, box=box, games=games, ambassador=amb, playoffs=pgames, calendar=cal, conferences=list(R.CONFERENCES),
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
