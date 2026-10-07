"""Players: persistent identities with a position, age, ratings and injury state.

A player is called P00001 until cards.py gives her a card (name, personality, archetypes). Ratings are 1-100.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import rules as R
from positions import ATTRS, OVR_WEIGHTS, POSITIONS, ROSTER_COUNTS, STARTERS

# ---- PLACEHOLDER talent numbers (dials, not rules) -------------------------------------
STARTER_OVR_MEAN = 64.0
STARTER_OVR_SD = 8.0
BACKUP_OVR_MEAN = 52.0
BACKUP_OVR_SD = 7.0
ATTR_SPREAD = 7.0           # how far one rating can sit from the player's overall
TEAM_OFFSET_SD = 1.0        # extra team-wide quality on top of the player-by-player spread
AGES = list(range(22, 36))
AGE_WEIGHTS = [8, 10, 11, 11, 10, 9, 8, 7, 5, 4, 3, 2, 1, 1]


def clamp(x, lo=R.RATING_MIN, hi=R.RATING_MAX):
    return lo if x < lo else hi if x > hi else x


@dataclass
class Player:
    id: int
    pos: str
    age: int
    ratings: Dict[str, float]
    team_id: Optional[int] = None        # None = free agent or retired
    weeks_out: int = 0                   # injured: games still to miss
    draft_year: Optional[int] = None
    draft_pick: Optional[int] = None
    years_in_league: int = 0
    accrued_seasons: Optional[int] = None # six qualifying games; None migrates founding/older players
    credited_seasons: Optional[int] = None # three qualifying games; used by future salary integration
    service_year: Optional[int] = None
    service_weeks: List[int] = field(default_factory=list)
    service_settled_year: Optional[int] = None
    retired: bool = False
    fa_years: int = 0                    # seasons spent unsigned
    ovr: float = 0.0
    card: object = None                  # cards.PlayerCard, attached by cards.ensure_cards
    display_name: str = ""               # the card's name once the card exists
    salary: float = 0.0                  # $ millions a year (economy.py)
    years_left: int = 0                  # seasons left on the contract; at 0 she is re-signed or reaches the market
    bonus: float = 0.0                   # the year's share of her signing bonus (part of `salary`, the cap number)
    bonus_years: int = 0                 # years of that bonus still to be spread out
    guaranteed: float = 0.0              # base pay still guaranteed, $ millions in all (economy.py)
    ir_games: int = 0                    # games since she went on injured reserve
    ir_designated: bool = False          # designated to return from injured reserve this season (uses one of the team's 8)

    def __post_init__(self):
        # Prior game histories are unavailable for founding players and pre-step-6 saves.
        # Preserve their existing service estimate; subsequent service is earned from games.
        if self.accrued_seasons is None:
            self.accrued_seasons = self.years_in_league
        if self.credited_seasons is None:
            self.credited_seasons = self.years_in_league
        self.recompute()

    @property
    def name(self) -> str:
        return self.display_name or f"P{self.id:05d}"

    @property
    def label(self) -> str:
        return f"{self.name} ({self.pos})"

    def recompute(self):
        w = OVR_WEIGHTS[self.pos]
        a = ATTRS[self.pos]
        self.ovr = sum(wi * self.ratings[ai] for wi, ai in zip(w, a))


def make_player(rng: random.Random, pid: int, pos: str, ovr: float, age: int, team_id: Optional[int] = None,
                draft_year: Optional[int] = None, draft_pick: Optional[int] = None) -> Player:
    ratings = {a: clamp(ovr + rng.gauss(0.0, ATTR_SPREAD)) for a in ATTRS[pos]}
    return Player(id=pid, pos=pos, age=age, ratings=ratings, team_id=team_id, draft_year=draft_year,
                  draft_pick=draft_pick, years_in_league=max(0, age - 22))


def random_age(rng: random.Random) -> int:
    return rng.choices(AGES, AGE_WEIGHTS)[0]


class IdSource:
    def __init__(self, start: int = 1):
        self.next = start

    def __call__(self) -> int:
        v = self.next
        self.next += 1
        return v


def build_practice_squad(rng: random.Random, new_id: IdSource, team_id: int, team_offset: float) -> List[Player]:
    """A founding team's practice squad: 16 young players, mostly in their first or second season, well below the roster's backups."""
    out: List[Player] = []
    for i in range(R.PRACTICE_SQUAD_SIZE):
        pos = POSITIONS[i % len(POSITIONS)] if i < len(POSITIONS) else rng.choices(POSITIONS, [ROSTER_COUNTS[x] for x in POSITIONS])[0]
        age = rng.choice((22, 22, 23, 23, 24))
        p = make_player(rng, new_id(), pos, clamp(rng.gauss(46.0, 5.0) + team_offset * 0.25, 30, 70), age, team_id)
        p.years_in_league = age - 22
        p.accrued_seasons = p.credited_seasons = 0
        out.append(p)
    return out


def build_roster(rng: random.Random, new_id: IdSource, team_id: int, team_offset: float) -> List[Player]:
    players: List[Player] = []
    for pos in POSITIONS:
        for slot in range(ROSTER_COUNTS[pos]):
            if slot < STARTERS[pos]:
                ovr = rng.gauss(STARTER_OVR_MEAN, STARTER_OVR_SD) + team_offset
            else:
                ovr = rng.gauss(BACKUP_OVR_MEAN, BACKUP_OVR_SD) + team_offset * 0.5
            players.append(make_player(rng, new_id(), pos, clamp(ovr, 30, 95), random_age(rng), team_id))
    return players
