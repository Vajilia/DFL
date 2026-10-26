"""Edition 8.15 monetary guardrails (isolated reference, not a contract ledger).

Scope: §11 cap timing and the viability inequality for current/future years.
Amounts are in DFL dollars (not millions of real USD). Decimal arithmetic is
used to avoid accepting an illegal cent-sized overage via float rounding.

Contract creation, guarantees, bonus acceleration and payment clocks MUST
supply correct year projections; this module does not invent those amounts.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

CAP = Decimal("1000")
RESERVE = Decimal("25")
MINIMUM_SALARY = Decimal("5")
REQUIRED_PLACES = 48
TOP_COUNT_PRECUT = 69
BASE_REQUIRED = MINIMUM_SALARY * REQUIRED_PLACES
MAX_STRICT_DEAD = CAP - BASE_REQUIRED - RESERVE


def D(value) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean is not an amount")
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValueError("invalid amount") from exc
    if not result.is_finite():
        raise ValueError("non-finite amount")
    return result


@dataclass(frozen=True)
class YearProjection:
    """One club, one league year; no prior-year cap carryover exists.

    `contract_hits` are per-contract current-year cap numbers (including PS).
    `booked_dead` are already charged dead amounts, not included in hits.
    `rookie_holds` are still-unmade owned draft picks at their required scale.
    `strict_dead` is the §11 worst-case dead liability if every contract were
    released at start of that year, inclusive of already booked dead charges.
    `remaining_paid_fraction` prorates the *viability minimum replacement*
    cost in the current year; future years normally use 1.
    """
    contract_hits: tuple
    booked_dead: Decimal
    rookie_holds: tuple
    strict_dead: Decimal
    remaining_paid_fraction: Decimal = Decimal("1")
    post_cut: bool = False

    def __post_init__(self):
        values = tuple(D(x) for x in self.contract_hits)
        holds = tuple(D(x) for x in self.rookie_holds)
        dead = D(self.booked_dead)
        strict = D(self.strict_dead)
        fraction = D(self.remaining_paid_fraction)
        if any(v < 0 for v in values + holds) or dead < 0 or strict < 0:
            raise ValueError("negative cap liability")
        if strict < dead:
            raise ValueError("strict dead cannot be below already-booked dead")
        if not Decimal("0") <= fraction <= Decimal("1"):
            raise ValueError("remaining paid fraction out of range")
        object.__setattr__(self, "contract_hits", values)
        object.__setattr__(self, "rookie_holds", holds)
        object.__setattr__(self, "booked_dead", dead)
        object.__setattr__(self, "strict_dead", strict)
        object.__setattr__(self, "remaining_paid_fraction", fraction)

    @property
    def cap_number(self) -> Decimal:
        ordered = sorted(self.contract_hits, reverse=True)
        counted = ordered if self.post_cut else ordered[:TOP_COUNT_PRECUT]
        return self.booked_dead + sum(counted, Decimal("0")) + sum(self.rookie_holds, Decimal("0"))

    @property
    def strict_dead_limit(self) -> Decimal:
        return CAP - BASE_REQUIRED * self.remaining_paid_fraction - RESERVE

    @property
    def viability_margin(self) -> Decimal:
        return self.strict_dead_limit - self.strict_dead


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    reasons: tuple[str, ...]


def assess_transaction(before: Mapping[int, YearProjection],
                       after: Mapping[int, YearProjection], *,
                       action: str, final_cut: bool = False) -> Verdict:
    """Check all committed years atomically, without changing either ledger.

    A pre-existing overage may be reduced. An action cannot *increase* an
    over-cap amount, except cap check on release; releases still face §11's
    strict-dead viability guard. Final cuts require unconditional cap legality.
    """
    if set(before) != set(after) or not before:
        raise ValueError("same nonempty committed years required before/after")
    if action not in {"sign", "claim", "trade", "release", "restructure", "cut"}:
        raise ValueError("unknown action")
    reasons = []
    for year in sorted(before):
        a, b = before[year], after[year]
        if not isinstance(a, YearProjection) or not isinstance(b, YearProjection):
            raise ValueError("all year values must be YearProjection")
        if b.strict_dead > b.strict_dead_limit and b.strict_dead > a.strict_dead:
            reasons.append(f"{year}: strict-dead viability would worsen")
        if final_cut and year == min(before) and b.cap_number > CAP:
            reasons.append(f"{year}: final cut would exceed cap")
        elif action != "release" and b.cap_number > CAP and b.cap_number > a.cap_number:
            reasons.append(f"{year}: cap overage would increase")
    return Verdict(not reasons, tuple(reasons))
