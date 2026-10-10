"""Autopilot trades: the baseline trade market that general managers run when no one is driving the club.

NFL basis: trades are a small part of the league's business (about 40 to 60 a year, most of them a veteran for a pick, a swap of picks around the draft,
and a handful of player-for-player deals). The league's draft-value chart prices picks; a team sells a player it does not need, or a veteran when it is
rebuilding, and a team buys when she would start for it and it can fit her under the cap. Everything here is a MODEL stand-in for that behaviour.

Two windows: the offseason (after the restricted market, before the draft) and the weeks before the trade deadline. A club sells at most one player or
makes one pick swap a window. Prices come from `pick_points` (a draft-value chart in the shape of the NFL's, stretched over 336 picks) and
`player_points` (the draft slot a player of her rating would have been, discounted for age, contract length and pay above market). A deal must be
within a few percent on that chart, legal under transactions.check_trade (cap, rosters, deadline, tenders), and not stopped by the Commissioner's
review (governance.review_trade, which can only reject). Exiled clubs do not trade.

Not built: conditional picks, cash, three-team deals, player-for-player trades, trades made by agents (the Commissioner can still reject them).
"""
from __future__ import annotations

import math
import random
from typing import List, Optional

import economy as EC
import rosters
import rules as R
import transactions as T
from positions import ACTIVE_MINIMUMS

# ---- the value chart (MODEL) ------------------------------------------------------------------------------------------------------------
CHART_TOP = 3000.0            # the first pick, as in the NFL's chart
CHART_SCALE = 224.0 / 336.0   # the NFL's 224 picks stretched over the DFL's 336
CHART_BASE = 9.0
CHART_POWER = 1.3             # shape: pick 32 of 224 is about 430 points, pick 64 about 200, pick 224 about 44 (NFL: 590, 270, 2)
FAIR_LOW, FAIR_HIGH = 0.85, 1.20     # what the buying club pays, as a share of the player's points
AGE_DISCOUNT = 0.88           # per year above AGE_FULL
AGE_FULL = 26
OVERPAID = 1.25               # pay above this many times her market price lowers her value
MIN_OVR = 60.0                # players rated below this are not worth a pick
MID_SLOT = 24                 # a pick whose slot is not known yet (next year's) counts as mid-round


def pick_points(overall: int) -> float:
    n = max(1.0, overall * CHART_SCALE)
    return CHART_TOP / (1.0 + (n - 1.0) / CHART_BASE) ** CHART_POWER


def pick_value(pk) -> float:
    slot = pk.slot if pk.slot is not None else (pk.rnd - 1) * R.DRAFT_PICKS_PER_ROUND + MID_SLOT
    return pick_points(slot)


def _rookie_expect(pick: int, rm) -> float:
    base = rm.rookie_base - rm.rookie_late_drop * min(1.0, (pick - 1) / (R.DRAFT_ROUNDS * R.TOTAL_TEAMS - 1))
    return base + rm.rookie_span * math.exp(-(pick - 1) / rm.rookie_decay)


def equivalent_pick(ovr: float, rm) -> int:
    """The draft slot at which a typical rookie is as good as she is."""
    for n in range(1, R.DRAFT_ROUNDS * R.TOTAL_TEAMS + 1):
        if _rookie_expect(n, rm) <= ovr:
            return n
    return R.DRAFT_ROUNDS * R.TOTAL_TEAMS


def player_points(p, rm) -> float:
    if p.ovr < MIN_OVR or p.years_left < 1:
        return 0.0
    v = pick_points(equivalent_pick(p.ovr, rm))
    v *= AGE_DISCOUNT ** max(0, p.age - AGE_FULL)
    v *= min(1.0, 0.55 + 0.15 * p.years_left)
    if p.salary > OVERPAID * EC.market_salary(p.pos, p.ovr, p.credited_seasons) + 0.5:
        v *= 0.6
    return v


# ---- the market ---------------------------------------------------------------------------------------------------------------------------
def _free_picks(lg, club: int, years) -> list:
    mv = lg.movement
    return [pk for pk in mv.picks.values() if pk.owner == club and pk.year in years and pk.selected is None and pk.reserved_by is None
            and pk.original < 100]


def _price(picks, target: float) -> Optional[list]:
    """The buyer's picks that pay for `target` points: one pick, else two, whose total is within FAIR_LOW to FAIR_HIGH of it; the cheapest total wins."""
    lo, hi = FAIR_LOW * target, FAIR_HIGH * target
    vals = sorted(((pick_value(pk), pk) for pk in picks), key=lambda x: (-x[0], x[1].key))
    best = None
    for v, pk in vals:
        if lo <= v <= hi and (best is None or v < best[0]):
            best = (v, [pk])
    if best:
        return best[1]
    small = [x for x in vals if x[0] < lo]
    for i, (v1, p1) in enumerate(small):
        for j, (v2, p2) in enumerate(small[i + 1:], i + 1):
            s = v1 + v2
            if lo <= s <= hi and (best is None or s < best[0]):
                best = (s, [p1, p2])
            elif s < lo:
                for v3, p3 in small[j + 1:]:
                    s3 = s + v3
                    if lo <= s3 <= hi and (best is None or s3 < best[0]):
                        best = (s3, [p1, p2, p3])
    return best[1] if best else None


def window(lg, rng: random.Random, rm, year: int, week: Optional[int], sell_prob: float, swap_prob: float, draft_year: int, rounds: int = 1) -> List[dict]:
    """One trade window. `week` is None in the offseason, else the regular-season weeks finished; `draft_year` is the draft whose picks are tradable first.
    Returns what was done: [{clubs, players, picks, points, week}]."""
    import governance as GV
    import offseason as OFF
    done: List[dict] = []
    clubs = [t for t in lg.teams if t.status != "exiled" and t.roster]
    quick = {t.id: OFF._quick_strength(t.roster) for t in clubs}
    order = sorted(quick, key=lambda i: (quick[i], i))
    rank = {tid: i for i, tid in enumerate(order)}                       # 0 = weakest
    years = (draft_year, draft_year + 1)
    for _ in range(rounds):
        rng.shuffle(clubs)
        for t in list(clubs):
            if rng.random() >= sell_prob + swap_prob:
                continue
            if rng.random() < sell_prob / (sell_prob + swap_prob):
                deal = _sale(lg, rng, rm, t, clubs, rank, years, year, week)
            else:
                deal = _swap(lg, rng, t, clubs, years, year, week)
            if deal is None:
                continue
            a, b, pa, pb, ka, kb, pts, victim = deal
            import gm_roster
            if not gm_roster.trade_ok(lg, rm, a, b, pa, pb, ka, kb, pts, year, week):      # both GMs have to agree (the rule's answer is yes)
                continue
            if victim is not None:                                     # in season the buying club is at 53: it releases its weakest surplus player first
                rosters._release(lg, lg.by_id[b], victim)
            if GV.review_trade(lg, a, b, pa, pb, ka, kb, year, week) is not None:
                continue
            T.trade(lg, a, b, pa, pb, ka, kb, year, week)
            if week is not None:
                for tid in (a, b):
                    rosters.fill_roster(lg, lg.by_id[tid], rng)         # a club that sold a player signs a replacement at once
            done.append(dict(clubs=(a, b), players=(list(pa), list(pb)), picks=(list(ka), list(kb)), points=round(pts), week=week))
    return done


def _sale(lg, rng, rm, t, clubs, rank, years, year, week):
    """Club `t` sells one player for picks."""
    import offseason as OFF
    mv = lg.movement
    rebuilding = rank[t.id] < len(clubs) // 3
    cands = []
    have = rosters.counts(t.roster)
    for p in t.roster:
        if have[p.pos] <= ACTIVE_MINIMUMS[p.pos]:
            continue                                                   # a club never sells its last kicker or a thin position
        if p.years_left < 1 or p.ovr < MIN_OVR or p.weeks_out > 0 or p.suspended > 0:
            continue
        right = mv.rights.get((year, p.id))
        if right is not None and right.status == "tendered":
            continue
        rest = [q for q in t.roster if q is not p]
        needed = OFF._gain(rest, p) > 0                                # she would start for her own club
        if (not needed) or (rebuilding and p.age >= 27):
            pts = player_points(p, rm)
            if pts > 0:
                cands.append((pts, p))
    if not cands:
        return None
    pts, p = max(cands, key=lambda x: (x[0], x[1].id))
    buyers = [b for b in clubs if b.id != t.id and rank[b.id] >= len(clubs) // 3 and OFF._gain(b.roster, p) >= 6.0]
    rng.shuffle(buyers)
    for b in buyers[:12]:
        keys = _price(_free_picks(lg, b.id, years), pts)
        if keys is None:
            continue
        ks = [k.key for k in keys]
        victim = None
        if week is not None and len(b.roster) >= R.ROSTER_LIMIT:
            victim = rosters._weakest_surplus(b)
            b.roster.remove(victim)
        why = T.check_trade(lg, t.id, b.id, [p.id], [], [], ks, year, week)
        if victim is not None:
            b.roster.append(victim)
        if why:
            continue
        return t.id, b.id, [p.id], [], [], ks, pts, victim
    return None


def _swap(lg, rng, t, clubs, years, year, week):
    """Club `t` moves up the draft: it gives two picks for one earlier one (the other club collects)."""
    mine = _free_picks(lg, t.id, years)
    others = [c for c in clubs if c.id != t.id]
    rng.shuffle(others)
    for c in others[:6]:
        theirs = [pk for pk in _free_picks(lg, c.id, years) if pk.year == years[0] and pk.rnd <= 3]
        if not theirs:
            continue
        want = rng.choice(theirs)
        keys = _price(mine, pick_value(want))
        if keys is None:
            continue
        ks = [k.key for k in keys]
        if T.check_trade(lg, t.id, c.id, [], [], ks, [want.key], year, week):
            continue
        return t.id, c.id, [], [], ks, [want.key], pick_value(want), None
    return None
