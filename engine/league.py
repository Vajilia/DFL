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
    fans: object = None       # fan_media_cards.FanbaseCard (belongs to the franchise, outlives its owners)
    bank: float = 0.0         # cap room banked from last season, $ millions (economy.py)

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
        self.fans_on = True                # fanbase and media cards decide owner approval (turn off for the old placeholder model)
        self.interactions_on = True        # Required interactions are written up as scenes (never changes an outcome)
        self.prev_pct: dict = {}           # last season's win% by team, for the scenes' evidence
        self.driver = None                 # who makes the choices (decisions.py); None means the autopilot
        self.choice_log: list = []         # every choice anyone made, the canonical record of the league's history
        self.passed_over: list = []        # candidate cards that were not hired (the Archive keeps them)
        self._cand_ids = 0
        self.free_coaches: list = []       # coaches between jobs (fired or passed over): they live on and can be offered again
        self.free_gms: list = []
        self.refs: dict = {}               # the league's average coach and GM ratings (living.refresh_refs): effects are measured against these
        self.hall: list = []               # the Hall of Fame, in the order people were inducted
        self.fanbases: list = []
        self.media: list = []              # every media outlet ever founded, folded ones included
        self._media_ids = 0
        self._owner_ids = 0
        self._gm_ids = 0
        self.pool = 0.0                    # the league's cap pool: forfeited room and floor shortfalls in, exiled teams' absorbed payroll out (economy.py)

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


def new_league(rng: random.Random, rosters: bool = False, coaches: bool = True, staff: bool = True, fans: bool = True, interactions: bool = True) -> League:
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
    lg.fans_on = lg.staff_on and fans      # fanbases and media; they feed owner approval
    lg.interactions_on = lg.staff_on and interactions   # scenes for firings, recall votes and exile determinations
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
    import economy
    economy.init_contracts(lg)
    refresh_strengths(lg)
    for div_id in range(R.TOTAL_DIVISIONS):
        act = sorted(lg.active_in_division(div_id), key=lambda t: -t.strength)
        for rank, t in enumerate(act, start=1):
            t.tier = rank


def refresh_strengths(lg: League):
    import living
    living.refresh_refs(lg)
    from lineup import build_lineup
    import power_rating as PR
    for t in lg.teams:
        t.strength = PR.rating(build_lineup(t.id, t.roster, t.coach))
