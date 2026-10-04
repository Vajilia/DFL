"""Injuries: decided by the engine, not by the AI, so every card sees the same facts.

PLACEHOLDER rates (dials): about one injury per team every three games.
"""
from __future__ import annotations

import random
from typing import Iterable, List, Tuple

from players import Player
from positions import STARTERS

P_STARTER = 0.012          # chance a player who played is hurt in a game
P_BACKUP = 0.003
DURATIONS = (1, 2, 3, 4, 6, 8, 12, 20)
DURATION_WEIGHTS = (42, 20, 12, 8, 8, 4, 3, 3)       # 20 = out for the season


def roll_injuries(roster: List[Player], starters: Iterable[Player], rng: random.Random) -> List[Tuple[Player, int]]:
    """Returns [(player, games_out)] for players hurt this game."""
    out = []
    start_ids = {p.id for p in starters}
    for p in roster:
        if p.weeks_out > 0:
            continue
        pr = P_STARTER if p.id in start_ids else P_BACKUP
        if rng.random() < pr:
            out.append((p, rng.choices(DURATIONS, DURATION_WEIGHTS)[0]))
    return out


def tick_week(players: Iterable[Player], newly_hurt_ids: set):
    for p in players:
        if p.weeks_out > 0 and p.id not in newly_hurt_ids:
            p.weeks_out -= 1
