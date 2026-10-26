"""Edition 8.15 roster limits and position coverage (§11), isolated reference."""
from __future__ import annotations
from dataclasses import dataclass, replace
from collections import Counter
from typing import Mapping

POSITIONS = frozenset("K P QB HB FB WR TE LT LG C RG RT LE RE DT ROLB MLB LOLB CB FS SS LS".split())
REQUIRED = {"K":1,"P":1,"QB":3,"WR":5,"TE":2,"LT":2,"LG":2,"C":1,
            "RG":2,"RT":2,"LE":2,"RE":2,"DT":3,"ROLB":2,"MLB":3,
            "LOLB":2,"CB":5,"FS":2,"SS":2,"LS":1}
MAIN_MAX = 53
PRACTICE_MAX = 16
CAMP_MAX = 90
PS_VETERANS_MAX = 6

@dataclass(frozen=True)
class Player:
    player_id: str
    position: str
    status: str = "main"  # main, practice, camp, injured, suspended
    credited_seasons: int = 0
    medically_available: bool = True

    def __post_init__(self):
        if not self.player_id or self.position not in POSITIONS:
            raise ValueError("invalid player identity or permanent position")
        if self.status not in {"main","practice","camp","injured","suspended"}:
            raise ValueError("invalid roster category")
        if self.credited_seasons < 0:
            raise ValueError("negative credited seasons")

@dataclass(frozen=True)
class Roster:
    club_id: str
    players: Mapping[str, Player]

    def __post_init__(self):
        if not self.club_id or any(k!=v.player_id for k,v in self.players.items()):
            raise ValueError("roster identity mismatch")

def coverage(players):
    counts=Counter(p.position for p in players if p.status=="main")
    missing={position:max(0,count-counts[position]) for position,count in REQUIRED.items()}
    if counts["HB"]>=3 or (counts["HB"]>=2 and counts["FB"]>=1):
        missing["HB"]=0
    else:
        missing["HB"]=min(max(0,3-counts["HB"]), max(0,2-counts["HB"])+max(0,1-counts["FB"]))
    return {k:v for k,v in missing.items() if v}

def validate(roster: Roster, *, final_cut=False, require_eleven=False):
    players=tuple(roster.players.values())
    counts=Counter(p.status for p in players)
    if len(players)>CAMP_MAX:
        raise ValueError("more than 90 club players")
    if counts["main"]>MAIN_MAX or counts["practice"]>PRACTICE_MAX:
        raise ValueError("main or practice roster size exceeded")
    veterans=sum(p.credited_seasons>2 for p in players if p.status=="practice")
    if veterans>PS_VETERANS_MAX:
        raise ValueError("too many veteran practice-squad players")
    if final_cut:
        if counts["main"]!=MAIN_MAX:
            raise ValueError("final cut requires exactly 53 main players")
        if counts["practice"]>PRACTICE_MAX or counts["camp"]:
            raise ValueError("final cut leaves camp players")
        missing=coverage(players)
        if missing:
            raise ValueError("final cut positional shortfall: "+str(missing))
    if require_eleven and sum(p.status=="main" and p.medically_available for p in players)<11:
        raise ValueError("cannot field eleven medically available players")
    return True
