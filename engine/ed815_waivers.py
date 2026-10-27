"""Edition 8.15 one-day waiver eligibility, priority and claim adjudication.

Authority: pinned Design Bible §§0, 11. This is a pure resolution layer:
the calling roster/financial transaction must reserve and commit the actual
contract/roster move atomically. No game can call it mid-play.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable, Sequence

VESTED_CREDITED_SEASONS = 4
CLAIM_WINDOW = timedelta(days=1)


def _utc(moment: datetime) -> None:
    if moment.tzinfo is None or moment.utcoffset() != timedelta(0):
        raise ValueError("league timestamps must be explicit UTC")


def is_waiver_eligible(credited_seasons: int) -> bool:
    if not isinstance(credited_seasons,int) or isinstance(credited_seasons,bool) or credited_seasons < 0:
        raise ValueError("invalid credited seasons")
    return credited_seasons < VESTED_CREDITED_SEASONS


@dataclass(frozen=True)
class Waiver:
    player_id: str
    releasing_club: str
    released_at: datetime
    expires_at: datetime

    def __post_init__(self):
        _utc(self.released_at)
        _utc(self.expires_at)
        if not self.player_id or not self.releasing_club:
            raise ValueError("missing player/club")
        if self.expires_at != self.released_at + CLAIM_WINDOW:
            raise ValueError("claim period must be exactly one simulated day")


@dataclass(frozen=True)
class Claim:
    claimant: str
    filed_at: datetime

    def __post_init__(self):
        _utc(self.filed_at)
        if not self.claimant:
            raise ValueError("claimant required")


@dataclass(frozen=True)
class Outcome:
    status: str  # claimed, cleared, vested_free_agent
    player_id: str
    new_club: str | None
    considered_claimants: tuple[str,...]


def release_path(player_id: str, club: str, credited_seasons: int,
                 released_at: datetime) -> Waiver | Outcome:
    _utc(released_at)
    if not is_waiver_eligible(credited_seasons):
        return Outcome("vested_free_agent",player_id,None,())
    return Waiver(player_id,club,released_at,released_at+CLAIM_WINDOW)


def priority_order(league_week: int, previous_draft_priority: Sequence[str],
                   current_standings_priority: Sequence[str] | None = None) -> tuple[str,...]:
    """Week 1–4: previous draft order; week 5+: caller supplies current order.

    The current ordering must already incorporate active-team standings,
    Ambassador Tour placements in the previous draft bands, and Edition 8.15's
    tied-game treatment. No hidden strength rating is consulted here.
    """
    if not isinstance(league_week,int) or league_week < 1:
        raise ValueError("invalid league week")
    last=tuple(previous_draft_priority)
    if len(last)!=48 or len(set(last))!=48:
        raise ValueError("last draft priority must list all 48 clubs exactly once")
    if league_week <= 4:
        return last
    if current_standings_priority is None:
        raise ValueError("current standings priority required after week four")
    now=tuple(current_standings_priority)
    if len(now)!=48 or set(now)!=set(last):
        raise ValueError("current standings priority must contain the same 48 clubs")
    return now


def resolve_waiver(waiver: Waiver, claims: Iterable[Claim],
                   priority: Sequence[str], at: datetime,
                   can_receive: Callable[[str,str],bool]) -> Outcome:
    """Resolution is provisional until an external atomic contract move commits.

    Only timely claims count. If the highest-priority claiming club fails a
    cap/roster guard, proceed to the next legal claimant; no subjective veto.
    """
    _utc(at)
    if at < waiver.expires_at:
        raise ValueError("cannot settle before expiration")
    ranked=tuple(priority)
    if len(ranked)!=48 or len(set(ranked))!=48 or waiver.releasing_club not in ranked:
        raise ValueError("invalid 48-club priority")
    filed=set()
    for claim in claims:
        if claim.claimant not in ranked:
            raise ValueError("unknown claiming club")
        if claim.filed_at < waiver.released_at:
            raise ValueError("claim precedes release")
        if claim.filed_at >= waiver.expires_at:
            continue
        if claim.claimant != waiver.releasing_club:
            filed.add(claim.claimant)
    considered=[]
    for club in ranked:
        if club not in filed:
            continue
        considered.append(club)
        if can_receive(club,waiver.player_id):
            return Outcome("claimed",waiver.player_id,club,tuple(considered))
    return Outcome("cleared",waiver.player_id,None,tuple(considered))
