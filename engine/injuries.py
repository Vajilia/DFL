"""Injuries: decided by the engine, not by the AI, so every card sees the same facts.

Step 8 (rates at about the NFL's): a player who plays can be hurt in any game; the chance depends on whether she starts and on her position;
what hurts is drawn from a short table of injury kinds, each with its own lengths. The weekly injury report lists everyone out.

NFL basis (Pro Football Reference "games lost to injury", as reported by Rotowire for 2024): a club loses about 95 to 250 player-games a season to
injury, the most injured ten between 190 and 254 with 37 to 56 injuries each, the least injured around 100. The model aims at about 30 injuries
and 135 player-games lost per club over 17 games (the DFL plays 18). Concussions are about 7% of injuries (the NFL's is 6 to 8%). All rates and
lengths below are MODEL dials, "approximately the NFL" (the Commissioner, 2026-10-08: only the rates need to be about right).

Known simplifications: a player hurt in a game plays out that game; a concussion is removed from the NEXT game only (the NFL removes mid-game, which
the drive engine does not model), and a concussion always misses at least one game (the protocol's mandatory removal).
"""
from __future__ import annotations

import random
from typing import Dict, Iterable, List, Optional, Tuple

from players import Player

P_STARTER = 0.064          # chance a starter who played is hurt (and misses at least one game) in a game
P_BACKUP = 0.016           # the same for a player who is not a starter
# relative risk by position (mean about 1 over a roster; QBs, kickers and punters are hurt less often)
POS_RISK = {"QB": 0.55, "RB": 1.35, "WR": 1.20, "TE": 1.00, "OL": 0.95, "DL": 1.15, "LB": 1.15, "CB": 1.25, "S": 1.10, "K": 0.25, "P": 0.25}

# (kind, share of injuries, ((games out), (weights)))
KINDS = (
    ("knee",       0.13, ((2, 4, 6, 8, 12, 20), (5, 12, 20, 18, 20, 25))),
    ("ankle",      0.18, ((1, 2, 3, 4, 6, 8), (20, 24, 20, 16, 12, 8))),
    ("hamstring",  0.15, ((1, 2, 3, 4, 6), (22, 28, 22, 16, 12))),
    ("shoulder",   0.09, ((1, 2, 4, 6, 8, 12, 20), (12, 16, 18, 14, 16, 14, 10))),
    ("concussion", 0.07, ((1, 2, 3, 4), (55, 25, 12, 8))),
    ("foot",       0.08, ((1, 2, 3, 6, 8, 12, 20), (18, 18, 14, 14, 14, 12, 10))),
    ("back",       0.07, ((1, 2, 3, 4, 8, 20), (18, 20, 18, 14, 14, 16))),
    ("groin",      0.06, ((1, 2, 3, 4, 8), (22, 28, 22, 16, 12))),
    ("ribs",       0.05, ((1, 2, 3, 4, 6), (30, 28, 20, 12, 10))),
    ("hand",       0.06, ((1, 2, 3, 4, 8), (28, 28, 20, 14, 10))),
    ("neck",       0.02, ((1, 2, 4, 8, 20), (24, 24, 20, 16, 16))),
    ("other",      0.04, ((1, 2, 3, 4, 6), (30, 26, 20, 14, 10))),
)
KIND_NAMES = tuple(k[0] for k in KINDS)
CONCUSSION = "concussion"
MIN_GAMES_CONCUSSION = 1


def mean_games_out() -> float:
    total = 0.0
    for _, share, (ds, ws) in KINDS:
        total += share * sum(d * w for d, w in zip(ds, ws)) / sum(ws)
    return total / sum(k[1] for k in KINDS)


def draw_kind(rng: random.Random) -> Tuple[str, int]:
    kind = rng.choices(KINDS, [k[1] for k in KINDS])[0]
    games = rng.choices(kind[2][0], kind[2][1])[0]
    if kind[0] == CONCUSSION:
        games = max(MIN_GAMES_CONCUSSION, games)
    return kind[0], games


def roll_injuries(roster: List[Player], starters: Iterable[Player], rng: random.Random) -> List[Tuple[Player, int, str]]:
    """Returns [(player, games_out, kind)] for players hurt this game."""
    out = []
    start_ids = {p.id for p in starters}
    for p in roster:
        if p.weeks_out > 0:
            continue
        pr = (P_STARTER if p.id in start_ids else P_BACKUP) * POS_RISK.get(p.pos, 1.0)
        if rng.random() < pr:
            kind, games = draw_kind(rng)
            out.append((p, games, kind))
    return out


def tick_week(players: Iterable[Player], newly_hurt_ids: set):
    for p in players:
        if p.weeks_out > 0 and p.id not in newly_hurt_ids:
            p.weeks_out -= 1
            if p.weeks_out == 0:
                p.injury = ""


def injury_report(lg, week: int) -> List[dict]:
    """The weekly injury report: every player who is out, on the roster or on injured reserve, with what hurt her and for how long.
    Status is "out" (misses this week) or "IR" (on injured reserve). Games out is what is left, counting the coming game."""
    rows = []
    for t in lg.teams:
        for lst, status in ((t.roster or [], "out"), (t.ir, "IR")):
            for p in lst:
                if p.weeks_out > 0:
                    rows.append(dict(week=week, team=t.id, player=p.id, pos=p.pos, kind=p.injury or "other", games_left=p.weeks_out, status=status))
    return rows


def report_summary(rows: List[dict]) -> Dict[int, int]:
    """Players out per team in one week's report."""
    c: Dict[int, int] = {}
    for r in rows:
        c[r["team"]] = c.get(r["team"], 0) + 1
    return c
