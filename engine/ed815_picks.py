"""Edition 8.15 draft-pick identities, equal-chance lottery and transfer guards.

Source: pinned Design Bible §§0, 12. No actual draft selection, college
ratings or contract signing occurs here; rookie cap reservations are handled
by the accounting ledger that owns each unmade pick.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Pick:
    draft_year: int
    round_number: int
    original_club: str
    owner: str
    slot: int
    reserved: bool = False
    used: bool = False

    def __post_init__(self):
        if self.draft_year < 2000 or not 1 <= self.round_number <= 7 or not 1 <= self.slot <= 48:
            raise ValueError("invalid ordinary pick year, round or slot")
        if not self.original_club or not self.owner:
            raise ValueError("pick clubs must be identified")
        if self.reserved and self.used:
            raise ValueError("selected pick cannot remain reserved")

    @property
    def identity(self) -> tuple[int,int,str]:
        return self.draft_year,self.round_number,self.original_club


def equal_lottery(returning_ambassadors: Iterable[str], seed: str | int) -> tuple[str,...]:
    """An eight-way seeded uniform permutation, independent of pick ownership."""
    clubs=tuple(returning_ambassadors)
    if len(clubs)!=8 or len(set(clubs))!=8:
        raise ValueError("exactly eight distinct returning ambassador clubs required")
    # Per-club deterministic keys; 256-bit collisions are resolved by club ID.
    def lottery_key(club):
        raw=f"{seed}|ed815-returning-lottery|{club}".encode("utf-8")
        return (hashlib.sha256(raw).digest(),club)
    return tuple(sorted(clubs,key=lottery_key))


def ordinary_picks(draft_year: int, ordered_original_clubs: Iterable[str]) -> dict:
    ordered=tuple(ordered_original_clubs)
    if len(ordered)!=48 or len(set(ordered))!=48:
        raise ValueError("draft order requires all 48 original clubs")
    picks={}
    for round_number in range(1,8):
        for slot,club in enumerate(ordered,1):
            pick=Pick(draft_year,round_number,club,club,slot)
            picks[pick.identity]=pick
    assert len(picks)==336
    return picks


def transfer(picks: Mapping[tuple,Pick], identity: tuple, *,
             from_club: str,to_club: str,current_draft_year: int) -> dict:
    if identity not in picks:
        raise ValueError("pick not found")
    pick=picks[identity]
    if pick.owner!=from_club or from_club==to_club or not to_club:
        raise ValueError("transfer ownership invalid")
    if pick.used or pick.reserved:
        raise ValueError("selected or reserved pick cannot transfer")
    if pick.draft_year not in range(current_draft_year,current_draft_year+3):
        raise ValueError("only next three incomplete drafts may be traded")
    updated=dict(picks)
    updated[identity]=replace(pick,owner=to_club)
    return updated


def reserve(picks: Mapping[tuple,Pick], identity: tuple, owner: str) -> dict:
    pick=picks[identity]
    if pick.owner!=owner or pick.used or pick.reserved:
        raise ValueError("pick cannot be reserved")
    updated=dict(picks)
    updated[identity]=replace(pick,reserved=True)
    return updated


def unreserve(picks: Mapping[tuple,Pick], identity: tuple, owner: str) -> dict:
    pick=picks[identity]
    if pick.owner!=owner or not pick.reserved:
        raise ValueError("owner does not control active reservation")
    updated=dict(picks)
    updated[identity]=replace(pick,reserved=False)
    return updated


def select(picks: Mapping[tuple,Pick], identity: tuple, owner: str) -> dict:
    pick=picks[identity]
    if pick.owner!=owner or pick.used or pick.reserved:
        raise ValueError("pick cannot be selected")
    updated=dict(picks)
    updated[identity]=replace(pick,used=True)
    return updated
