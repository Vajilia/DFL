"""Edition 8.15 creator-supplied draft prospects and atomic rookie signing.

The creator owns prospect identities. The draft engine consumes one listed
prospect and one owned, unmade selection; no new player card is generated here.
"""
from __future__ import annotations
from dataclasses import dataclass,replace
import ed815_calendar as CAL
import ed815_roster as ROSTER
import ed815_compensation as COMP
import ed815_contracts as CONTRACTS
import ed815_picks as PICKS

@dataclass(frozen=True)
class Prospect:
    player: ROSTER.Player
    draft_year: int

    def __post_init__(self):
        if self.draft_year<2000:
            raise ValueError("invalid draft class year")
        if self.player.status!="camp":
            raise ValueError("unselected prospect must carry camp entry category")

    @property
    def player_id(self):
        return self.player.player_id

def select_rookie(league,*,club_id,player_id,pick_identity,post_cut=False):
    if league.pending is not None:
        raise ValueError("draft blocked by reserved trade")
    if league.structure is None:
        raise ValueError("active season required")
    if club_id not in league.clubs or player_id not in league.prospects:
        raise ValueError("club or creator prospect not found")
    year=CAL.civil_year(league.structure.season)
    prospect=league.prospects[player_id]
    if prospect.draft_year!=year:
        raise ValueError("prospect from wrong draft class")
    if any(player_id in c.roster.players or player_id in c.ledger.contracts
           for c in league.clubs.values()) or player_id in league.free_agents:
        raise ValueError("prospect identity already rostered or unsigned")
    club=league.clubs[club_id]
    before=COMP.rookie_holds_by_owner(year,league.ordinary,league.compensation)
    ordinary=dict(league.ordinary)
    comps=list(league.compensation)
    if pick_identity in ordinary:
        selected=PICKS.select(ordinary,pick_identity,club_id)
        pick=selected[pick_identity]
        ordinary=selected
    else:
        matches=[(index,p) for index,p in enumerate(comps) if p.identity==pick_identity]
        if len(matches)!=1:
            raise ValueError("draft pick does not exist")
        index,pick=matches[0]
        if pick.owner!=club_id or pick.used or pick.reserved or pick.draft_year!=year:
            raise ValueError("compensatory pick not available for this club/year")
        pick=replace(pick,used=True)
        comps[index]=pick
    if pick.draft_year!=year:
        raise ValueError("pick belongs to a different draft year")
    after=COMP.rookie_holds_by_owner(year,ordinary,comps)
    contract=COMP.fixed_rookie_contract(player_id,pick)
    ledger=CONTRACTS.sign(club.ledger,contract,year,post_cut=post_cut,
        rookie_holds=before.get(club_id,()),
        rookie_holds_after=after.get(club_id,()))
    players=dict(club.roster.players)
    players[player_id]=prospect.player
    roster=replace(club.roster,players=players)
    ROSTER.validate(roster)
    clubs=dict(league.clubs)
    clubs[club_id]=replace(club,ledger=ledger,roster=roster)
    remaining=dict(league.prospects)
    del remaining[player_id]
    event=("rookie_pick",player_id,club_id,year,tuple(pick_identity))
    return replace(league,revision=league.revision+1,clubs=clubs,
                   ordinary=ordinary,compensation=tuple(comps),
                   prospects=remaining,events=league.events+(event,))
