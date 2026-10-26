"""Atomic two-club Edition 8.15 player/pick trade reference (§§11–12).

This is a pure proposal/commit calculation: no write occurs if validation fails.
It handles pre-payment-year contract transfers, roster membership and ordinary
pick ownership; compensation picks may be supplied for cap reservations but
are not yet tradable through this particular interface.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Mapping
import ed815_cap as CAP
import ed815_contracts as CONTRACTS
import ed815_picks as PICKS
import ed815_roster as ROSTER
import ed815_compensation as COMP
import ed815_market as MARKET
import ed815_calendar as CAL

@dataclass(frozen=True)
class Club:
    ledger: CONTRACTS.Ledger
    roster: ROSTER.Roster
    def __post_init__(self):
        if self.ledger.club_id!=self.roster.club_id:
            raise ValueError("club roster/ledger identity mismatch")

@dataclass(frozen=True)
class TradeLeg:
    from_club: str
    to_club: str
    player_ids: tuple[str,...] = ()
    pick_ids: tuple[tuple,...] = ()

def propose_trade(clubs: Mapping[str,Club], ordinary: Mapping,
                  legs: tuple[TradeLeg,...], *, season: int, moment: datetime,
                  post_cut: bool, compensation=(), require_eleven=False):
    """Return (new_clubs,new_picks) only if the ENTIRE bundle is legal.

    Final-roster positional minimums are intentionally not enforced for an
    in-season trade: §11 permits temporary shortfalls. Kickoff viability can
    be requested using require_eleven. Both ledgers are checked after *all*
    players and picks change hands, not after each intermediate swap.
    """
    if not MARKET.may_finalize_trade(season,moment):
        raise ValueError("outside Edition 8.15 trading window")
    if not legs:
        raise ValueError("trade cannot be empty")
    involved={club for leg in legs for club in (leg.from_club,leg.to_club)}
    if len(involved)!=2 or involved!=set(clubs):
        raise ValueError("exactly two participating clubs required")
    for name,club in clubs.items():
        if name != club.ledger.club_id:
            raise ValueError("club map identity mismatch")
        ROSTER.validate(club.roster,require_eleven=require_eleven)
    year=CAL.civil_year(season)
    before_holds=COMP.rookie_holds_by_owner(year,ordinary,compensation)
    new_contracts={k:dict(v.ledger.contracts) for k,v in clubs.items()}
    new_rosters={k:dict(v.roster.players) for k,v in clubs.items()}
    new_dead={k:{y:CAP.D(a) for y,a in v.ledger.booked_dead.items()} for k,v in clubs.items()}
    new_picks=dict(ordinary)
    moved_players=set()
    moved_picks=set()
    for leg in legs:
        src,dst=leg.from_club,leg.to_club
        if src not in clubs or dst not in clubs or src==dst:
            raise ValueError("trade leg clubs invalid")
        if not leg.player_ids and not leg.pick_ids:
            raise ValueError("empty trade leg")
        for pid in leg.player_ids:
            if pid in moved_players:
                raise ValueError("player cannot move twice in one trade")
            moved_players.add(pid)
            if pid not in new_contracts[src] or pid not in new_rosters[src]:
                raise ValueError("player must be on source contract and roster")
            if pid in new_contracts[dst] or pid in new_rosters[dst]:
                raise ValueError("duplicate receiving player")
            contract=new_contracts[src].pop(pid)
            if not contract.active_in(year):
                raise ValueError("player contract not active in trade year")
            # Original club retains only already-paid/unamortized bonus charge.
            new_dead[src][year]=new_dead[src].get(year,CAP.D(0))+contract.uncharged_bonus(year)
            new_contracts[dst][pid]=replace(contract,bonus=CAP.D(0))
            new_rosters[dst][pid]=new_rosters[src].pop(pid)
        for identity in leg.pick_ids:
            if identity in moved_picks:
                raise ValueError("pick cannot move twice in one trade")
            moved_picks.add(identity)
            new_picks=PICKS.transfer(new_picks,identity,from_club=src,to_club=dst,
                                     current_draft_year=year)
    after_holds=COMP.rookie_holds_by_owner(year,new_picks,compensation)
    result={}
    for name,club in clubs.items():
        ledger=replace(club.ledger,contracts=new_contracts[name],booked_dead=new_dead[name])
        roster=replace(club.roster,players=new_rosters[name])
        ROSTER.validate(roster,require_eleven=require_eleven)
        years=range(year,year+6)
        before={y:CONTRACTS.projection(club.ledger,y,post_cut=post_cut,
                   rookie_holds=before_holds.get(name,()) if y==year else ())
                for y in years}
        after={y:CONTRACTS.projection(ledger,y,post_cut=post_cut,
                   rookie_holds=after_holds.get(name,()) if y==season else ())
               for y in years}
        verdict=CAP.assess_transaction(before,after,action="trade")
        if not verdict.allowed:
            raise ValueError(name+": "+"; ".join(verdict.reasons))
        result[name]=Club(ledger,roster)
    return result,new_picks
