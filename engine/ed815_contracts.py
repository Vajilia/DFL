"""Edition 8.15 contract/dead-money reference ledger, isolated from legacy economy.

This implements basic pre-payment-year sign, release, and transfer settlement.
It intentionally does not yet implement weekly earned-base proration, free-agent
market clearing, roster legality, negotiated extensions or transactional locks.
All amounts are DFL dollars with Decimal arithmetic (Design Bible §11).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from decimal import Decimal
from typing import Mapping

import ed815_cap as CAP

D = CAP.D


@dataclass(frozen=True)
class Contract:
    player_id: str
    start_year: int
    bases: tuple
    guarantees: tuple
    bonus: Decimal = Decimal("0")

    def __post_init__(self):
        if not self.player_id or self.start_year < 2000:
            raise ValueError("invalid contract identity/date")
        bases = tuple(D(v) for v in self.bases)
        guarantees = tuple(D(v) for v in self.guarantees)
        if not 1 <= len(bases) <= 5 or len(guarantees) != len(bases):
            raise ValueError("contracts must cover 1..5 years")
        if any(b < CAP.MINIMUM_SALARY for b in bases):
            raise ValueError("base salary below Edition 8.15 minimum")
        if any(g < 0 or g > b for g,b in zip(guarantees,bases)):
            raise ValueError("guarantees exceed their year's base")
        bonus = D(self.bonus)
        if bonus < 0:
            raise ValueError("negative signing bonus")
        object.__setattr__(self,"bases",bases)
        object.__setattr__(self,"guarantees",guarantees)
        object.__setattr__(self,"bonus",bonus)

    @property
    def end_year(self) -> int:
        return self.start_year + len(self.bases)

    @property
    def yearly_bonus(self) -> Decimal:
        return self.bonus / len(self.bases)

    def active_in(self, year: int) -> bool:
        return self.start_year <= year < self.end_year

    def bonus_charge(self, year: int) -> Decimal:
        if not self.active_in(year):
            return D(0)
        idx = year-self.start_year
        return (self.bonus-self.yearly_bonus*(len(self.bases)-1)
                if idx == len(self.bases)-1 else self.yearly_bonus)

    def cap_hit(self, year: int) -> Decimal:
        return self.bases[year-self.start_year] + self.bonus_charge(year) if self.active_in(year) else D(0)

    def guarantee(self, year: int) -> Decimal:
        return self.guarantees[year-self.start_year] if self.active_in(year) else D(0)

    def uncharged_bonus(self, year: int) -> Decimal:
        if not self.active_in(year):
            return D(0)
        return self.bonus - sum((self.bonus_charge(y) for y in range(self.start_year,year)),D(0))


@dataclass(frozen=True)
class Ledger:
    club_id: str
    contracts: Mapping[str, Contract] = field(default_factory=dict)
    booked_dead: Mapping[int, Decimal] = field(default_factory=dict)
    split_used: frozenset[int] = frozenset()

    def __post_init__(self):
        if not self.club_id:
            raise ValueError("club ID required")
        if any(pid != c.player_id for pid,c in self.contracts.items()):
            raise ValueError("contract key does not match player ID")
        if any(D(v) < 0 for v in self.booked_dead.values()):
            raise ValueError("negative booked dead money")


def _post_dead(ledger: Ledger, increments: Mapping[int, Decimal]) -> Ledger:
    dead = {int(y):D(amount) for y,amount in ledger.booked_dead.items()}
    for year,amount in increments.items():
        dead[year] = dead.get(year,D(0)) + D(amount)
    return replace(ledger,booked_dead=dead)


def projection(ledger: Ledger, year: int, *, post_cut: bool,
               rookie_holds=(), remaining_paid_fraction=1) -> CAP.YearProjection:
    active = [c for c in ledger.contracts.values() if c.active_in(year)]
    booked = D(ledger.booked_dead.get(year,0))
    # At the start of a given year, earned base is zero. Guaranteed base for
    # that year and ALL unamortized signing bonus would become liability if all
    # contracts were released at that year's start.
    strict = booked + sum((c.guarantee(year)+c.uncharged_bonus(year) for c in active),D(0))
    return CAP.YearProjection(tuple(c.cap_hit(year) for c in active),booked,
                              tuple(rookie_holds),strict,
                              D(remaining_paid_fraction),post_cut)


def _years(current_year: int):
    return range(current_year,current_year+6)


def _approve(before: Ledger, after: Ledger, year: int, action: str,
             post_cut: bool, *, rookie_holds=(),rookie_holds_after=None):
    prev = {y:projection(before,y,post_cut=post_cut,rookie_holds=rookie_holds if y==year else ())
            for y in _years(year)}
    final_holds=rookie_holds if rookie_holds_after is None else rookie_holds_after
    next_ = {y:projection(after,y,post_cut=post_cut,rookie_holds=final_holds if y==year else ())
             for y in _years(year)}
    verdict=CAP.assess_transaction(prev,next_,action=action,final_cut=False)
    if not verdict.allowed:
        raise ValueError("; ".join(verdict.reasons))


def sign(ledger: Ledger, contract: Contract, year: int, *,
         post_cut=False, rookie_holds=(),rookie_holds_after=None) -> Ledger:
    if year != contract.start_year or contract.player_id in ledger.contracts:
        raise ValueError("sign at contract start; player cannot have two deals")
    updated=dict(ledger.contracts)
    updated[contract.player_id]=contract
    after=replace(ledger,contracts=updated)
    _approve(ledger,after,year,"sign",post_cut,rookie_holds=rookie_holds,
             rookie_holds_after=rookie_holds_after)
    return after


def release(ledger: Ledger, player_id: str, year: int, *,
            split=False,post_cut=False,rookie_holds=()) -> Ledger:
    if player_id not in ledger.contracts:
        raise ValueError("player not signed")
    contract=ledger.contracts[player_id]
    if not contract.active_in(year):
        raise ValueError("release must fall within contracted year")
    if split and year in ledger.split_used:
        raise ValueError("one split release per club per league year")
    bonus=contract.uncharged_bonus(year)
    increments = {y:contract.guarantee(y) for y in range(year,contract.end_year)}
    if split:
        increments[year]=increments.get(year,D(0))+bonus/2
        increments[year+1]=increments.get(year+1,D(0))+bonus/2
    else:
        increments[year]=increments.get(year,D(0))+bonus
    updated=dict(ledger.contracts)
    del updated[player_id]
    after=_post_dead(replace(ledger,contracts=updated,
                     split_used=ledger.split_used|({year} if split else set())),increments)
    _approve(ledger,after,year,"release",post_cut,rookie_holds=rookie_holds)
    return after


def trade(source: Ledger, destination: Ledger, player_id: str, year: int, *,
          post_cut=False, source_holds=(),destination_holds=()) -> tuple[Ledger,Ledger]:
    """Transfer unpaid base/guarantees; never transfer paid signing bonus."""
    if source.club_id == destination.club_id:
        raise ValueError("trade requires distinct clubs")
    if player_id not in source.contracts or player_id in destination.contracts:
        raise ValueError("missing/duplicate player")
    contract=source.contracts[player_id]
    if not contract.active_in(year):
        raise ValueError("trade outside contract")
    outbound=dict(source.contracts)
    del outbound[player_id]
    new_source=_post_dead(replace(source,contracts=outbound),{year:contract.uncharged_bonus(year)})
    inbound=dict(destination.contracts)
    inbound[player_id]=replace(contract,bonus=D(0))
    new_destination=replace(destination,contracts=inbound)
    # Both financial validations occur before either replacement is returned.
    _approve(source,new_source,year,"trade",post_cut,rookie_holds=source_holds)
    _approve(destination,new_destination,year,"trade",post_cut,rookie_holds=destination_holds)
    return new_source,new_destination
