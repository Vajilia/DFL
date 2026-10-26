"""Edition 8.15 stateful one-day waivers layered on the financial ledger.

A waived nonvested player is unavailable on the field while her contract stays
on the releasing club's ledger until claim resolution. A legal claimant takes
unpaid salary/guarantees, not the former club's original signing bonus.
Vested releases go directly to the unsigned free-agent pool.
"""
from __future__ import annotations
from dataclasses import dataclass,replace
from datetime import datetime
import ed815_waivers as W
import ed815_calendar as CAL
import ed815_contracts as C
import ed815_roster as R
import ed815_compensation as COMP
import ed815_cap as CAP
import ed815_free_agents as F

@dataclass(frozen=True)
class ClaimIntent:
    claim: W.Claim
    status: str="main"
    def __post_init__(self):
        if self.status not in {"main","practice","camp"}:
            raise ValueError("invalid waiver destination category")

@dataclass(frozen=True)
class PendingWaiver:
    notice: W.Waiver
    player: R.Player
    claims: tuple[ClaimIntent,...]=()
    def __post_init__(self):
        if self.player.player_id!=self.notice.player_id:
            raise ValueError("waiver notice and player identity mismatch")

def _year(league):
    if league.structure is None:
        raise ValueError("active league season required")
    return CAL.civil_year(league.structure.season)

def _holds(league,year,club):
    return COMP.rookie_holds_by_owner(
        year,league.ordinary,league.compensation).get(club,())

def _check(before,after,year,action,post_cut,holds):
    current={y:C.projection(before,y,post_cut=post_cut,
                 rookie_holds=holds if y==year else ()) for y in range(year,year+6)}
    future={y:C.projection(after,y,post_cut=post_cut,
                 rookie_holds=holds if y==year else ()) for y in range(year,year+6)}
    verdict=CAP.assess_transaction(current,future,action=action)
    if not verdict.allowed:
        raise ValueError("; ".join(verdict.reasons))

def begin_release(league,club_id,player_id,*,at:datetime,post_cut=False):
    W._utc(at)
    year=_year(league)
    if league.pending is not None:
        raise ValueError("trade reservation blocks waiver")
    if club_id not in league.clubs or player_id in league.waivers:
        raise ValueError("unknown club or player already on waivers")
    club=league.clubs[club_id]
    if player_id not in club.roster.players or player_id not in club.ledger.contracts:
        raise ValueError("released player must be rostered and contracted")
    player=club.roster.players[player_id]
    contract=club.ledger.contracts[player_id]
    if not contract.active_in(year):
        raise ValueError("player has no active contract this year")
    path=W.release_path(player_id,club_id,player.credited_seasons,at)
    players=dict(club.roster.players)
    del players[player_id]
    roster=replace(club.roster,players=players)
    R.validate(roster)
    pool=dict(league.free_agents)
    waivers=dict(league.waivers)
    if isinstance(path,W.Waiver):
        ledger=club.ledger # Contract stays counted until claim/clear.
        waivers[player_id]=PendingWaiver(path,player)
        event=("waiver_open",player_id,club_id,at.isoformat())
    else:
        ledger=C.release(club.ledger,player_id,year,post_cut=post_cut,
                          rookie_holds=_holds(league,year,club_id))
        if player_id in pool:
            raise ValueError("released player already in free-agent pool")
        pool[player_id]=F.FreeAgent(player,club_id,year)
        event=("vested_release",player_id,club_id,at.isoformat())
    clubs=dict(league.clubs)
    clubs[club_id]=replace(club,ledger=ledger,roster=roster)
    return replace(league,revision=league.revision+1,clubs=clubs,
              free_agents=pool,waivers=waivers,events=league.events+(event,))

def file_claim(league,player_id,claimant,*,at:datetime,status="main"):
    W._utc(at)
    if league.pending is not None or player_id not in league.waivers:
        raise ValueError("waiver claim not available")
    pending=league.waivers[player_id]
    notice=pending.notice
    if claimant not in league.clubs or claimant==notice.releasing_club:
        raise ValueError("invalid claiming club")
    if not notice.released_at<=at<notice.expires_at:
        raise ValueError("claim outside one-day window")
    if any(x.claim.claimant==claimant for x in pending.claims):
        raise ValueError("club may only file one claim")
    intent=ClaimIntent(W.Claim(claimant,at),status)
    waivers=dict(league.waivers)
    waivers[player_id]=replace(pending,claims=pending.claims+(intent,))
    event=("waiver_claim_filed",player_id,claimant,at.isoformat())
    return replace(league,revision=league.revision+1,
                  waivers=waivers,events=league.events+(event,))

def _claimed(league,pending,recipient,*,year,post_cut,status):
    old=pending.notice.releasing_club
    pid=pending.player.player_id
    former=league.clubs[old]
    target=league.clubs[recipient]
    contract=former.ledger.contracts[pid]
    if pid in target.ledger.contracts or pid in target.roster.players:
        raise ValueError("destination already has player")
    src_contracts=dict(former.ledger.contracts)
    del src_contracts[pid]
    dead=dict(former.ledger.booked_dead)
    dead[year]=CAP.D(dead.get(year,0))+contract.uncharged_bonus(year)
    old_ledger=replace(former.ledger,contracts=src_contracts,booked_dead=dead)
    dst_contracts=dict(target.ledger.contracts)
    dst_contracts[pid]=replace(contract,bonus=CAP.D(0))
    new_ledger=replace(target.ledger,contracts=dst_contracts)
    target_roster=dict(target.roster.players)
    target_roster[pid]=replace(pending.player,status=status)
    new_roster=replace(target.roster,players=target_roster)
    R.validate(new_roster)
    _check(former.ledger,old_ledger,year,"release",post_cut,
           _holds(league,year,old))
    _check(target.ledger,new_ledger,year,"claim",post_cut,
           _holds(league,year,recipient))
    clubs=dict(league.clubs)
    clubs[old]=replace(former,ledger=old_ledger)
    clubs[recipient]=replace(target,ledger=new_ledger,roster=new_roster)
    return clubs

def resolve(league,player_id,*,at:datetime,week:int,
            previous_draft_priority,current_standings_priority=None,
            post_cut=False):
    W._utc(at)
    year=_year(league)
    if league.pending is not None or player_id not in league.waivers:
        raise ValueError("waiver cannot be resolved now")
    pending=league.waivers[player_id]
    priority=W.priority_order(week,previous_draft_priority,
                             current_standings_priority)
    statuses={x.claim.claimant:x.status for x in pending.claims}
    staged={}
    def legal(club,pid):
        try:
            staged[club]=_claimed(league,pending,club,year=year,post_cut=post_cut,
                                  status=statuses[club])
            return True
        except ValueError:
            return False
    outcome=W.resolve_waiver(pending.notice,[x.claim for x in pending.claims],
                             priority,at,legal)
    waivers=dict(league.waivers)
    del waivers[player_id]
    pool=dict(league.free_agents)
    if outcome.status=="claimed":
        clubs=staged[outcome.new_club]
        event=("waiver_awarded",player_id,outcome.new_club,at.isoformat(),
               outcome.considered_claimants)
    else:
        old=pending.notice.releasing_club
        former=league.clubs[old]
        ledger=C.release(former.ledger,player_id,year,post_cut=post_cut,
                         rookie_holds=_holds(league,year,old))
        clubs=dict(league.clubs)
        clubs[old]=replace(former,ledger=ledger)
        pool[player_id]=F.FreeAgent(pending.player,old,year)
        event=("waiver_cleared",player_id,old,at.isoformat(),
               outcome.considered_claimants)
    return replace(league,revision=league.revision+1,clubs=clubs,
                   free_agents=pool,waivers=waivers,
                   events=league.events+(event,))
