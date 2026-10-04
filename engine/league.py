"""League state: the 48 teams, their divisions, tiers, status and strength."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

import rules as R
import placeholder_model as PM


@dataclass
class Team:
    id: int
    name: str
    conf: int                 # 0 or 1 (index into R.CONFERENCES)
    div: int                  # 0..3 inside the conference
    status: str               # "active" or "exiled"
    tier: Optional[int]       # 1..5 while active; None while exiled
    strength: float           # PLACEHOLDER talent rating (points better than average)

    @property
    def division_id(self) -> int:
        """0..7, unique across the league."""
        return self.conf * R.DIVISIONS_PER_CONFERENCE + self.div

    @property
    def division_name(self) -> str:
        return f"{R.CONFERENCES[self.conf]} {self.div + 1}"


class League:
    def __init__(self, teams: List[Team]):
        self.teams: List[Team] = teams
        self.by_id: Dict[int, Team] = {t.id: t for t in teams}

    # -- lookups ---------------------------------------------------------
    def division(self, division_id: int) -> List[Team]:
        return [t for t in self.teams if t.division_id == division_id]

    def active_in_division(self, division_id: int) -> List[Team]:
        return [t for t in self.division(division_id) if t.status == "active"]

    def exiled(self) -> List[Team]:
        return [t for t in self.teams if t.status == "exiled"]

    def active(self) -> List[Team]:
        return [t for t in self.teams if t.status == "active"]

    def slot_map(self) -> Dict[tuple, Team]:
        """(conf, div, tier) -> the active team holding that tier slot."""
        m = {}
        for t in self.active():
            key = (t.conf, t.div, t.tier)
            if key in m:
                raise ValueError(f"two teams share tier slot {key}")
            m[key] = t
        return m

    def snapshot(self) -> dict:
        return {t.id: (t.status, t.tier, round(t.strength, 3)) for t in self.teams}


def new_league(rng: random.Random) -> League:
    """ASSUMED starting league: random strengths, one random team per division starts
    in exile, and the rest take tiers 1-5 in order of strength."""
    teams: List[Team] = []
    n = 0
    for conf in range(len(R.CONFERENCES)):
        for div in range(R.DIVISIONS_PER_CONFERENCE):
            members = []
            for _ in range(R.TEAMS_PER_DIVISION):
                n += 1
                members.append(Team(
                    id=n, name=f"Team {n:02d}", conf=conf, div=div, status="active",
                    tier=None, strength=rng.gauss(0.0, PM.INITIAL_STRENGTH_SD)))
            exile_idx = rng.randrange(len(members))
            exiled = members.pop(exile_idx)
            exiled.status = "exiled"
            exiled.tier = None
            members.sort(key=lambda t: -t.strength)
            for rank, t in enumerate(members, start=1):
                t.tier = rank
            teams.extend(members + [exiled])
    teams.sort(key=lambda t: t.id)
    return League(teams)
