"""Governance (Step 8c): the CEOs' votes, the Competition Committee and the Commissioner's shrink-only powers.

The Commissioner's rulebook:
  * votes (Adapted from the NFL): three-quarters of the clubs (36 of 48) for rule, bylaw and playing-rule changes; two-thirds (32 of 48) to choose a
    Commissioner's successor; an eight-member Competition Committee, one CEO per division;
  * the Commissioner (Skeleton): every power is shrink-only: reject, cap, delay or reduce; never add. She reviews every trade and contract against the
    cap and the fair-competitiveness bands. The first Commissioner is the league's human operator.

What is built: the vote counting and the seats are exact; how a CEO votes is a MODEL formula (named dials); the autopilot makes no proposals (the
league's rules change only when a person or an agent proposes), so the autopilot league is unchanged by this module except for the committee's seating,
which is a private, seeded, read-only record. A Commissioner action is a `Ruling`; `shrink_only` is the audit that rejects any ruling that gives a club
more than it asked for.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

import cards as C
import rules as R

# ---- model dials (MODEL) -----------------------------------------------------------------------------------------------------
BASE_SUPPORT = 0.55            # chance a CEO backs a proposal that touches her club neither way
TILT_WEIGHT = 0.35             # a proposal that favours small markets (tilt -1) or big markets (+1) moves a vote by this much for CEOs at the extremes
COMMITTEE_BONUS = 0.20         # an endorsement from the Competition Committee adds this to every CEO's chance
COMMITTEE_SEAT_YEARS = 3       # a committee seat runs three years


def _market(t) -> float:
    return t.fans.market if getattr(t, "fans", None) is not None else 50.0


@dataclass
class Proposal:
    pid: int
    year: int
    kind: str                    # "rule" | "commissioner"
    text: str
    tilt: float = 0.0            # -1 favours small markets, +1 favours big ones
    endorsed: bool = False       # the Competition Committee's endorsement
    candidate: Optional[str] = None
    votes: Dict[int, bool] = field(default_factory=dict)
    result: str = "open"


def needed(kind: str) -> int:
    return R.RULE_CHANGE_VOTES if kind == "rule" else R.COMMISSIONER_VOTES


def owner_vote(lg, team, prop: Proposal) -> bool:
    """One CEO's vote. A formula by her card and her market; the seeded private stream gives each CEO her own consistent mood."""
    o = team.owner
    if o is None:
        return False
    r = C._rng(lg.card_seed, "vote", prop.pid, o.oid)
    stance = (_market(team) - 50.0) / 50.0                    # -1 small market ... +1 big market
    p = BASE_SUPPORT + TILT_WEIGHT * prop.tilt * stance + (COMMITTEE_BONUS if prop.endorsed else 0.0)
    p += 0.10 * (o.ratings.get("ambition", 50.0) - 50.0) / 50.0 if prop.kind == "rule" else 0.0
    return r.random() < max(0.02, min(0.98, p))


def hold_vote(lg, prop: Proposal, voters=None, recuse: Optional[int] = None) -> Proposal:
    """Count the vote. Every club has one vote; `recuse` is a club that does not vote (it still counts in the 48 the threshold is set against)."""
    for t in (voters or lg.teams):
        if t.id == recuse:
            continue
        prop.votes[t.id] = owner_vote(lg, t, prop)
    yes = sum(prop.votes.values())
    prop.result = "passed" if yes >= needed(prop.kind) else "failed"
    return prop


def propose(lg, year: int, kind: str, text: str, tilt: float = 0.0, endorsed: bool = False, candidate: Optional[str] = None) -> Proposal:
    lg.proposals_made += 1
    return Proposal(pid=lg.proposals_made, year=year, kind=kind, text=text, tilt=tilt, endorsed=endorsed, candidate=candidate)


# ---- the Competition Committee: one CEO per division ----------------------------------------------------------------------------
def seat_committee(lg, year: int) -> List[dict]:
    """Each division's six CEOs choose one of their number for the Competition Committee: the CEO others rate highest on a mix of popularity and business
    sense, with a private seeded jitter. Returns the eight seats. A seat is re-chosen each year (a three-year term is a later refinement)."""
    seats = []
    for div in range(R.TOTAL_DIVISIONS):
        best = None
        for t in lg.division(div):
            o = t.owner
            if o is None:
                continue
            r = C._rng(lg.card_seed, "committee", div, year, o.oid)
            score = 0.5 * o.ratings.get("popularity", 50.0) + 0.5 * o.ratings.get("business", 50.0) + r.gauss(0.0, 8.0)
            if best is None or score > best[0]:
                best = (score, t.id, o.oid, o.name)
        if best:
            seats.append(dict(division=div, team=best[1], owner=best[3], oid=best[2]))
    return seats


def annual_meeting(lg, year: int) -> dict:
    """The league's annual meeting: the committee is seated. The autopilot proposes nothing."""
    seats = seat_committee(lg, year)
    lg.committee = seats
    return dict(year=year, committee=[(s["division"], s["team"]) for s in seats], proposals=0)


# ---- the Commissioner: shrink-only ----------------------------------------------------------------------------------------------------
POWERS = ("reject", "cap", "delay", "reduce")


@dataclass
class Ruling:
    power: str                   # reject | cap | delay | reduce
    what: str
    before: float                # what the club asked for / was going to get (a price, a penalty, a number of picks, a number of days)
    after: float                 # what it gets after the ruling
    reason: str = ""


def shrink_only(ruling: Ruling, grants: bool = True) -> bool:
    """The audit: a Commissioner ruling may only shrink what a club gets. For a grant (a salary, a pick count, a number of days of freedom) `after` must not
    exceed `before`; for a burden (a fine, a penalty) the Commissioner may only reduce it, so `after` must not exceed `before` either. Both mean after <= before.
    A ruling with another power than the four is refused."""
    return ruling.power in POWERS and ruling.after <= ruling.before + 1e-9 and ruling.after >= 0.0


def reject(what: str, before: float, reason: str) -> Ruling:
    return Ruling("reject", what, before, 0.0, reason)


def cap(what: str, before: float, limit: float, reason: str) -> Ruling:
    return Ruling("cap", what, before, min(before, limit), reason)


def delay(what: str, days: float, reason: str) -> Ruling:
    """A delay shrinks the time a club has to act; it is recorded as `days` held back out of the window."""
    return Ruling("delay", what, days, 0.0, reason)


def reduce_penalty(what: str, baseline: float, factor: float, reason: str) -> Ruling:
    """A penalty may be reduced (factor 0..1) but never increased: a factor above 1 is clipped to 1."""
    return Ruling("reduce", what, baseline, baseline * max(0.0, min(1.0, factor)), reason)


def review_trade(lg, a, b, players_a, players_b, picks_a, picks_b, year, week=None, band_guard: Optional[Callable] = None) -> Optional[Ruling]:
    """The Commissioner's review of a trade: reject it if it breaks a rule (the cap, rosters, the deadline: transactions.check_trade names every reason) or if the
    fair-competitiveness guard (a callable returning a reason string, or None) objects. She can only stop a trade, never improve it for anyone.
    Returns None when she lets it stand."""
    import transactions as T
    why = T.check_trade(lg, a, b, players_a, players_b, picks_a, picks_b, year, week)
    if why:
        return reject("trade", 1.0, "; ".join(why))
    if band_guard is not None:
        reason = band_guard(lg, a, b, players_a, players_b, picks_a, picks_b)
        if reason:
            return reject("trade", 1.0, reason)
    return None
