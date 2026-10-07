"""Step 6 foundation: earned service and classification at contract expiration.

NFL: six regular-season games earn accrued service, three earn credited service.
DFL: Ambassador round-robin games also qualify. Byes and postseason games do not.
The active/inactive roster and IR earn accrued service. Only the active/inactive
roster earns salary-credited service: CBA Article 26 Section 2 excludes IR.
Practice squads and unsigned time earn neither.
Sources: https://operations.nfl.com/calendar-events/nfl-free-agency/types-of-free-agents
https://nflpaweb.blob.core.windows.net/website/PDFs/CBA/March-15-2020-NFL-NFLPA-Collective-Bargaining-Agreement-Final-Executed-Copy.pdf

This module accounts for service only. Tenders and matching rights
are separate steps; classification alone does not enforce a club's retention rights.
"""
from __future__ import annotations

import rules as R


def record_game(lg, game, year: int):
    """Record full-pay status before the game changes injuries or roster lists.

Each week counts once, including if a player changes clubs within that week.
No random draws. Injured and game-day-inactive members of the 53 still qualify.
IR qualifies for accrued service, but not salary-credited service.
"""
    if not game.counts_ties or not lg.has_rosters:
        return
    for tid in (game.home, game.away):
        t = lg.by_id[tid]
        roster_ids = {p.id for p in t.roster}
        for p in list(t.roster) + list(t.ir):
            if p.service_settled_year is not None and year <= p.service_settled_year:
                raise ValueError("cannot record service for an already settled season")
            if p.service_year != year:
                p.service_year, p.service_weeks = year, []
                p.credited_service_weeks = []
            if game.week not in p.service_weeks:
                p.service_weeks.append(game.week)
            if p.id in roster_ids and game.week not in p.credited_service_weeks:
                p.credited_service_weeks.append(game.week)


def settle_season(lg, year: int):
    """Award at most one season per player, even after release or a club change.

Counters remain on each player's body and use the existing JSON save machinery.
Repeated settlement is harmless. Keep this year's weeks for audit and save/resume.
"""
    import rosters
    people = [p for t in lg.teams for p in rosters.squad(t)] + list(lg.free_agents) + list(lg.retired_players)
    seen = set()
    for p in people:
        if p.id in seen:
            continue
        seen.add(p.id)
        if p.service_year != year or p.service_settled_year == year:
            continue
        if p.service_settled_year is not None and year < p.service_settled_year:
            raise ValueError("cannot settle service backwards")
        games = len(p.service_weeks)
        p.accrued_seasons += games >= R.ACCRUED_SEASON_GAMES
        p.credited_seasons += len(p.credited_service_weeks) >= R.CREDITED_SEASON_GAMES
        p.service_settled_year = year


def expiry_class(p, *, exiled: bool = False) -> str:
    """Eligibility when a contract expires; not the status of a released player.

An exiled club's expiring players use DFL restricted treatment regardless of service.
A tender must still be offered before rights exist (not implemented in this slice).
"""
    if p.years_left > 0:
        raise ValueError("free-agent classification requires an expired contract")
    if exiled:
        return "restricted"
    if p.accrued_seasons >= R.UFA_SEASONS:
        return "unrestricted"
    if p.accrued_seasons == R.RFA_SEASONS:
        return "restricted"
    return "exclusive_rights"
