"""League state: the 48 teams, their divisions, tiers, status and strength."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

import rules as R
import placeholder_model as PM
from players import IdSource, Player, build_roster


@dataclass
class Team:
    id: int
    name: str
    conf: int                 # 0 or 1 (index into R.CONFERENCES)
    div: int                  # 0..3 inside the conference
    status: str               # "active" or "exiled"
    tier: Optional[int]       # 1..5 while active; None while exiled
    strength: float           # talent rating in points better than average (placeholder scalar, or the roster's power rating)
    roster: List[Player] = None
    coach: object = None      # cards.CoachCard, the head coach
    owner: object = None      # staff_cards.OwnerCard
    gm: object = None         # staff_cards.GMCard

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
        self.free_agents: List[Player] = []
        self.new_id: IdSource = IdSource()
        self.has_rosters = False
        self.card_seed = 0                 # seeds every character card; set from the league's own seed
        self.staff_on = True               # owners, GMs, recalls, firings
        self.coaches_on = True             # head coaches nudge team strength (turn off to compare)
        self.coaches: list = []            # every head coach ever hired (the Archive keeps them)
        self.retired_players: list = []    # retired players keep their cards
        self._coach_ids = 0
        self.owners: list = []             # every owner and recall candidate ever generated
        self.gms: list = []
        self.archive: list = []            # plain-fact event log (recalls, firings, hirings); the Archive proper comes later
        self._owner_ids = 0
        self._gm_ids = 0

    def new_owner_id(self) -> int:
        self._owner_ids += 1
        return self._owner_ids

    def new_gm_id(self) -> int:
        self._gm_ids += 1
        return self._gm_ids

    def new_coach_id(self) -> int:
        self._coach_ids += 1
        return self._coach_ids

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


def new_league(rng: random.Random, rosters: bool = False, coaches: bool = True, staff: bool = True) -> League:
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
    lg = League(teams)
    lg.card_seed = hash(rng.getstate()[1]) % (2 ** 31)    # reads the generator without drawing from it
    lg.coaches_on = coaches
    lg.staff_on = coaches and staff        # owners and GMs (and firing); needs the coaches
    if rosters:
        give_rosters(lg, rng)
    return lg


def give_rosters(lg: League, rng: random.Random):
    """Build 47-player rosters. Each team's scalar strength is then replaced by its roster's
    power rating, and tiers follow that rating inside each division."""
    from lineup import build_lineup
    import power_rating as PR
    from players import TEAM_OFFSET_SD
    for t in lg.teams:
        t.roster = build_roster(rng, lg.new_id, t.id, rng.gauss(0.0, TEAM_OFFSET_SD))
    lg.has_rosters = True
    import cards
    cards.init_league_cards(lg, 0)
    refresh_strengths(lg)
    for div_id in range(R.TOTAL_DIVISIONS):
        act = sorted(lg.active_in_division(div_id), key=lambda t: -t.strength)
        for rank, t in enumerate(act, start=1):
            t.tier = rank


def refresh_strengths(lg: League):
    from lineup import build_lineup
    import power_rating as PR
    for t in lg.teams:
        t.strength = PR.rating(build_lineup(t.id, t.roster, t.coach))
