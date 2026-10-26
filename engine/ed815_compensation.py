"""Edition 8.15 post-round-seven compensation and rookie reservation reference.

Source: Design Bible §§0, 11–12. Only completed free-agent MOVEMENTS are
eligible. It does not infer snap qualification or invent first-year base pay.
The 336 ordinary picks remain in ed815_picks; compensation follows those picks.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Iterable, Mapping

import ed815_cap as CAP
import ed815_picks as PICKS
import ed815_contracts as CONTRACTS

THRESHOLD = CAP.D("75")
COMP_ROOKIE_SALARY = CAP.D("5")
MAX_COMP_LEAGUE = 48
MAX_COMP_CLUB = 2
ROOKIE_BY_ROUND = {1:CAP.D(25),2:CAP.D(18),3:CAP.D(14),4:CAP.D(11),
                   5:CAP.D(9),6:CAP.D(7),7:CAP.D(5)}
FIRST_ROUND_OPTION = CAP.D(35)


@dataclass(frozen=True)
class FreeAgentMove:
    player_id: str
    old_club: str
    new_club: str
    first_year_base: Decimal
    old_top_quarter_snaps: bool

    def __post_init__(self):
        if not self.player_id or not self.old_club or not self.new_club or self.old_club==self.new_club:
            raise ValueError("move requires one player and two distinct clubs")
        base=CAP.D(self.first_year_base)
        if base < CAP.MINIMUM_SALARY:
            raise ValueError("a signing cannot pay below minimum")
        if not isinstance(self.old_top_quarter_snaps,bool):
            raise ValueError("snap eligibility must be explicitly verified")
        object.__setattr__(self,"first_year_base",base)


@dataclass(frozen=True)
class CompPick:
    draft_year: int
    slot_after_round_seven: int
    original_club: str
    owner: str
    qualifying_player: str
    qualifying_base: Decimal
    used: bool = False
    reserved: bool = False

    def __post_init__(self):
        if self.draft_year < 2000 or not 1 <= self.slot_after_round_seven <= MAX_COMP_LEAGUE:
            raise ValueError("invalid compensation slot")
        if not self.original_club or not self.owner or not self.qualifying_player:
            raise ValueError("compensation identity incomplete")
        if self.used and self.reserved:
            raise ValueError("used pick cannot remain reserved")

    @property
    def identity(self):
        return self.draft_year, "post-R7", self.original_club, self.qualifying_player


def allocate_compensation(draft_year: int, movements: Iterable[FreeAgentMove],
                          previous_draft_order: Iterable[str]) -> tuple[CompPick,...]:
    order=tuple(previous_draft_order)
    if len(order)!=48 or len(set(order))!=48:
        raise ValueError("48 club prior-draft order required")
    rank={club:i for i,club in enumerate(order)}
    losses={c:[] for c in order}
    signings={c:[] for c in order}
    seen=set()
    for move in movements:
        if move.player_id in seen:
            raise ValueError("one completed free-agent movement per player")
        seen.add(move.player_id)
        if move.old_club not in rank or move.new_club not in rank:
            raise ValueError("movement references nonmember club")
        if move.first_year_base < THRESHOLD:
            continue
        signings[move.new_club].append(move)
        if move.old_top_quarter_snaps:
            losses[move.old_club].append(move)
    unmatched=[]
    for club in order:
        # Highest qualifying signing cancels highest qualifying departure.
        departures=sorted(losses[club],key=lambda m:(-m.first_year_base,m.player_id))
        acquisitions=sorted(signings[club],key=lambda m:(-m.first_year_base,m.player_id))
        remaining=departures[min(len(departures),len(acquisitions)):]
        for move in remaining:
            unmatched.append((move.first_year_base,club,move.player_id))
    unmatched.sort(key=lambda x:(-x[0],rank[x[1]],x[2]))
    result=[]
    granted={club:0 for club in order}
    for base,club,pid in unmatched:
        if granted[club]>=MAX_COMP_CLUB or len(result)>=MAX_COMP_LEAGUE:
            continue
        granted[club]+=1
        result.append(CompPick(draft_year,len(result)+1,club,club,pid,base))
    return tuple(result)


def transfer_comp(pick: CompPick, from_club: str,to_club: str,current_draft_year: int) -> CompPick:
    if pick.owner!=from_club or from_club==to_club or not to_club:
        raise ValueError("not a valid owner-to-owner transfer")
    if pick.used or pick.reserved:
        raise ValueError("reserved or selected compensation pick cannot move")
    if pick.draft_year not in range(current_draft_year,current_draft_year+3):
        raise ValueError("comp pick outside next three incomplete drafts")
    return replace(pick,owner=to_club)


def rookie_salary_for_round(round_number: int | str) -> Decimal:
    if round_number=="post-R7":
        return COMP_ROOKIE_SALARY
    if round_number not in ROOKIE_BY_ROUND:
        raise ValueError("only seven ordinary rounds plus post-R7 compensation")
    return ROOKIE_BY_ROUND[round_number]


def rookie_holds_by_owner(draft_year: int, ordinary: Mapping,
                          compensation: Iterable[CompPick]) -> dict[str,tuple[Decimal,...]]:
    holds={}
    for pick in ordinary.values():
        if pick.draft_year!=draft_year or pick.used:
            continue
        holds.setdefault(pick.owner,[]).append(rookie_salary_for_round(pick.round_number))
    for pick in compensation:
        if pick.draft_year!=draft_year or pick.used:
            continue
        holds.setdefault(pick.owner,[]).append(COMP_ROOKIE_SALARY)
    return {club:tuple(values) for club,values in holds.items()}


def fixed_rookie_contract(player_id: str, pick: PICKS.Pick | CompPick) -> CONTRACTS.Contract:
    salary=rookie_salary_for_round(
        pick.round_number if isinstance(pick,PICKS.Pick) else "post-R7")
    if not pick.used:
        raise ValueError("rookie contract requires completed selection")
    return CONTRACTS.Contract(player_id,pick.draft_year,(salary,)*4,(CAP.D(0),)*4,CAP.D(0))
