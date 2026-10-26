"""Edition 8.15 isolated season handoff: validated football results -> next year.

No automated player generation, free-agent agreements or draft selections.
Only naturally expired contracts are removed; identities, salaries on continuing
deals, pick ownership and past dead charges persist. The next structure is
computed from all 360 actual result records; a Coronation-completed signal is
required independently because its postseason is not in the fixture list.
"""
from __future__ import annotations
from dataclasses import replace
import hashlib
import json
import ed815_cycle as CYCLE
import ed815_calendar as CAL
import ed815_league_store as LEAGUE
import ed815_free_agents as FREE

def advance(state: LEAGUE.League,results,*,seed,coronation_complete,
            template_path=None):
    if coronation_complete is not True:
        raise ValueError("Coronation must be complete before league-year handoff")
    if state.pending is not None:
        raise ValueError("cannot advance season with an outstanding trade reservation")
    if state.structure is None:
        raise ValueError("validated active season structure required for handoff")
    current=state.structure
    incoming_year=CAL.civil_year(current.season+1)
    # Validates every exact game slot and constructs next seeded divisional beds.
    next_struct,summary=CYCLE.finalize_structure(
        current,results,seed,template_path=template_path)
    if next_struct.season!=current.season+1:
        raise AssertionError("non-consecutive season handoff")
    next_clubs={}
    expired=[]
    pool,retired=FREE.retire_due(state.free_agents,incoming_year)
    for club_id,club in sorted(state.clubs.items()):
        surviving={}
        for pid,contract in club.ledger.contracts.items():
            if contract.end_year<=incoming_year:
                if pid not in club.roster.players:
                    raise ValueError("expired contract lacks a player roster identity")
                if pid in pool:
                    raise ValueError("expired player already in free-agent pool")
                expired.append((club_id,pid))
                pool[pid]=FREE.FreeAgent(club.roster.players[pid],club_id,incoming_year)
            else:
                surviving[pid]=contract
        remaining_roster={pid:p for pid,p in club.roster.players.items() if pid not in
                          {pid for owner,pid in expired if owner==club_id}}
        next_ledger=replace(club.ledger,contracts=surviving)
        next_roster=replace(club.roster,players=remaining_roster)
        next_clubs[club_id]=replace(club,ledger=next_ledger,roster=next_roster)
    # Stale ordinary picks are historical, not silently destroyed; unmade picks
    # for the next draft must be supplied by the draft-order/selection module.
    canonical=[(r["week"],r["game"],r["home"],r["away"],
                r["home_score"],r["away_score"]) for r in results]
    digest=hashlib.sha256(json.dumps(sorted(canonical),separators=(",",":")).encode()).hexdigest()
    event=("season_handoff",current.season,next_struct.season,digest,
           tuple(sorted(expired)),retired)
    updated=LEAGUE.League(state.revision+1,next_clubs,state.ordinary,
            state.compensation,None,state.events+(event,),next_struct,pool,state.prospects)
    report=dict(completed=current.season,next=next_struct.season,
                expired_players=tuple(sorted(expired)),retired_players=retired,
                exiled=summary["exiled_clubs"],returning=summary["returning_clubs"],
                result_digest=digest)
    return updated,report
