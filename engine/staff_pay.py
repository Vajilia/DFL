"""Staff pay (Step 8b): what the football staff costs a club, outside the salary cap but inside two limits.

The Commissioner's rulebook (Fair): no single staff contract above 8% of the cap ($8M), the whole football staff (head coach, general manager and
assistants) no more than 20% of the cap ($20M). Everything else here is a MODEL formula (named dials): a coach or GM is paid by her level (the
average of her ratings) alone, not her fame (recognition must stay cosmetic: check_living proves it changes no outcome, and pay reaches the fans' approval through the
club's books); the assistants are a lump that grows with the market; the DFLPA representative's guard clamps any figure
that would break a limit (the guard is the same one that clamps player contracts; she never sets a price, she removes illegal ones).

Pay is a formula, not a negotiated term: the interview table still negotiates only guaranteed seasons. (Second term, later.)
"""
from __future__ import annotations

from typing import Dict

import economy as EC
import living as LV

COACH_MIN, COACH_MAX_RAW = 1.5, 9.0        # $ millions: a level-30 coach is paid COACH_MIN; the raw formula tops out here (the 8% limit clamps it)
GM_MIN, GM_MAX_RAW = 1.0, 6.5
LEVEL_LOW, LEVEL_HIGH = 30.0, 90.0         # the rating range the formulas span
PAY_EXPONENT = 1.6                         # stars are paid much more than starters
ASSISTANTS_BASE = 7.0                      # the assistant staff, $ millions, in a market-50 club
ASSISTANTS_PER_MARKET = 0.04               # plus this per market point above 50 (below 50: less)


def _level_share(card) -> float:
    x = (LV.level(card) - LEVEL_LOW) / (LEVEL_HIGH - LEVEL_LOW)
    return max(0.0, min(1.0, x)) ** PAY_EXPONENT


def coach_pay_raw(card) -> float:
    if card is None:
        return 0.0
    return (COACH_MIN + (COACH_MAX_RAW - COACH_MIN) * _level_share(card))


def gm_pay_raw(card) -> float:
    if card is None:
        return 0.0
    return (GM_MIN + (GM_MAX_RAW - GM_MIN) * _level_share(card))


def assistants_pay(team) -> float:
    market = team.fans.market if getattr(team, "fans", None) is not None else 50.0
    return ASSISTANTS_BASE + ASSISTANTS_PER_MARKET * (market - 50.0)


def staff_payroll(team) -> Dict[str, float]:
    """The club's football-staff pay for the year, after the DFLPA guard: each contract at most 8% of the cap, the whole staff at most 20%.
    Returns coach, gm, assistants, total and `clamped` (how many figures the guard had to cut)."""
    one = EC.STAFF_CONTRACT_MAX_PCT * EC.CAP
    total_max = EC.STAFF_PAYROLL_MAX_PCT * EC.CAP
    clamped = 0
    coach, gm = coach_pay_raw(team.coach), gm_pay_raw(team.gm)
    asst = assistants_pay(team)
    if coach > one:
        coach, clamped = one, clamped + 1
    if gm > one:
        gm, clamped = one, clamped + 1
    if coach + gm + asst > total_max:                      # the assistants give way first: they are the guard's budget, not a person's contract
        asst, clamped = max(0.0, total_max - coach - gm), clamped + 1
    return dict(coach=round(coach, 3), gm=round(gm, 3), assistants=round(asst, 3), total=round(coach + gm + asst, 3), clamped=clamped)
