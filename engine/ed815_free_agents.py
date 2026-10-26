"""Edition 8.15 durable identity free-agent pool and legal club signings.

The creator supplies player cards; this module neither invents players nor
uses hidden attributes. Pool retirement is the §13 fourth league-year-opening
rule. Only naturally expired contracts are placed here by the handoff module.
"""
from __future__ import annotations
from dataclasses import dataclass,replace
from typing import Mapping
import ed815_calendar as CAL
import ed815_contracts as CONTRACTS
import ed815_roster as ROSTER
import ed815_compensation as COMP

@dataclass(frozen=True)
class FreeAgent:
    player: ROSTER.Player
    last_club: str
    entered_year: int

    def __post_init__(self):
        if not self.last_club or self.entered_year<2000:
            raise ValueError("free-agent source and entry year required")

    @property
    def player_id(self):
        return self.player.player_id

def retire_due(pool: Mapping[str,FreeAgent],opening_year:int):
    """Remove unsigned players on the fourth opening AFTER their entry."""
    if opening_year<2000:
        raise ValueError("invalid league year")
    survivors={};retired=[]
    for pid,entry in pool.items():
        if pid!=entry.player_id:
            raise ValueError("free-agent pool identity mismatch")
        if opening_year<entry.entered_year:
            raise ValueError("pool entry is from the future")
        if opening_year>=entry.entered_year+4:
            retired.append(pid)
        else:
            survivors[pid]=entry
    return survivors,tuple(sorted(retired))

def sign(league,club_id:str,player_id:str,contract:CONTRACTS.Contract, *,
         status="main",post_cut=False):
    """Pure atomic proposal; caller persists resulting state in one commit."""
    if league.pending is not None:
        raise ValueError("cannot sign while trade is reserved")
    if league.structure is None:
        raise ValueError("active season structure required")
    if club_id not in league.clubs:
        raise ValueError("unknown club")
    if player_id not in league.free_agents:
        raise ValueError("player is not an available free agent")
    if contract.player_id!=player_id:
        raise ValueError("contract and player identity mismatch")
    year=CAL.civil_year(league.structure.season)
    if contract.start_year!=year:
        raise ValueError("new deal must begin this league year")
    if status not in {"main","practice","camp"}:
        raise ValueError("free agent must join an active club roster category")
    entry=league.free_agents[player_id]
    if year>=entry.entered_year+4 or year<entry.entered_year:
        raise ValueError("free-agent pool eligibility expired")
    club=league.clubs[club_id]
    if any(player_id in c.ledger.contracts or player_id in c.roster.players
           for c in league.clubs.values()):
        raise ValueError("player already on a club roster or contract")
    holds=COMP.rookie_holds_by_owner(year,league.ordinary,league.compensation)
    ledger=CONTRACTS.sign(club.ledger,contract,year,post_cut=post_cut,
             rookie_holds=holds.get(club_id,()))
    new_roster=dict(club.roster.players)
    new_roster[player_id]=replace(entry.player,status=status)
    roster=replace(club.roster,players=new_roster)
    ROSTER.validate(roster)
    clubs=dict(league.clubs)
    clubs[club_id]=replace(club,ledger=ledger,roster=roster)
    pool=dict(league.free_agents)
    del pool[player_id]
    event=("free_agent_sign",player_id,club_id,year)
    return replace(league,revision=league.revision+1,clubs=clubs,
                   free_agents=pool,events=league.events+(event,))
