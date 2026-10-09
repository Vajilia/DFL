"""Discipline (Step 8c): conduct, substance and gambling policy, and penalties on clubs.

The Commissioner's rulebook (NFL): conduct, substance and gambling policy, tampering and cap-circumvention penalties (up to 10% of the cap in a season),
game-integrity penalties; every Commissioner penalty is a reduction and the autopilot applies the baseline.

What is built:
  * players: a small weekly chance (a private seeded stream, never the game's) that a player is suspended. The kind sets the baseline length; a conduct
    case can be reduced by the Commissioner but never lengthened (governance.reduce_penalty). A suspended player is unavailable to the lineup and keeps her
    place on the 53 (the NFL's suspended list is a later refinement). Rates and lengths are MODEL dials, "approximately the NFL": about 1.8% of players
    a year, mostly short.
  * clubs: rare tampering, cap-circumvention and game-integrity cases. The fine is paid to the Equalization Fund, comes out of the club's year (finance.py)
    and is limited to CAP_PENALTY_MAX_PCT of the cap in a season for any one club.
"""
from __future__ import annotations

import random
from typing import List

import economy as EC
import governance as GV
import rules as R

# ---- players (MODEL) ---------------------------------------------------------------------------------------------------------------
P_SUSPENSION_YEAR = 0.018          # share of players suspended in a year (a PFR-style count of about 45 suspensions in a 48-club league)
WEEKS = 19
KINDS = (                           # (kind, share, baseline games)
    ("conduct", 0.45, ((1, 2, 3, 4, 6), (30, 25, 20, 15, 10))),
    ("substance", 0.35, ((2, 4, 6, 10), (35, 30, 25, 10))),
    ("performance_enhancing", 0.17, ((6,), (100,))),
    ("gambling", 0.03, ((6, 17), (80, 20))),
)

# ---- clubs (MODEL) ---------------------------------------------------------------------------------------------------------------------
P_CLUB_YEAR = {"tampering": 0.010, "cap_circumvention": 0.004, "game_integrity": 0.002}     # chance of a case in a club-year
FINE_PCT = {"tampering": (0.005, 0.015), "cap_circumvention": (0.02, 0.08), "game_integrity": (0.01, 0.04)}       # baseline fine as a share of the cap (low, high)


def weekly(lg, year: int, week: int, log: List[tuple]) -> dict:
    """End of a regular-season week: suspensions run down, then a few new ones are handed out. Returns the counts."""
    out = dict(served=0, new=0, fines=0)
    for t in lg.teams:
        for p in t.roster or ():
            if p.suspended > 0:
                p.suspended -= 1
                out["served"] += 1
    rng = random.Random(f"{lg.card_seed}-discipline-{year}-{week}")
    per_week = P_SUSPENSION_YEAR / WEEKS
    for t in lg.teams:
        for p in sorted(t.roster or (), key=lambda q: q.id):
            if p.suspended > 0 or p.weeks_out > 0:
                continue
            if rng.random() < per_week:
                kind = rng.choices(KINDS, [k[1] for k in KINDS])[0]
                games = rng.choices(kind[2][0], kind[2][1])[0]
                p.suspended = games
                log.append((week, t.id, p.id, kind[0], games))
                out["new"] += 1
    for t in lg.teams:                                          # clubs: rare cases, at week 10 (after the trade deadline, when the league audits)
        if week != R.TRADE_DEADLINE_WEEK + 1:
            continue
        for kind, prob in P_CLUB_YEAR.items():
            r = random.Random(f"{lg.card_seed}-clubcase-{year}-{t.id}-{kind}")
            if r.random() < prob:
                lo, hi = FINE_PCT[kind]
                amt = EC.CAP * (lo + (hi - lo) * r.random())
                fine_team(lg, t, kind, amt, year)
                out["fines"] += 1
    return out


def fine_team(lg, t, kind: str, baseline: float, year: int, factor: float = 1.0) -> float:
    """Fine a club. `baseline` is the autopilot's amount; `factor` (0..1) is the Commissioner's reduction, never more than the baseline. A club's fines in a
    season never pass CAP_PENALTY_MAX_PCT of the cap. The fine goes to the Equalization Fund and is held against the club's year. Returns the amount."""
    ruling = GV.reduce_penalty(f"fine:{kind}", baseline, factor, "commissioner")
    assert GV.shrink_only(ruling)
    room = max(0.0, R.CAP_PENALTY_MAX_PCT * EC.CAP - t.fines)
    amt = round(min(ruling.after, room), 3)
    if amt > 0:
        t.fines = round(t.fines + amt, 3)
        lg.pool += amt
        import staff_cards as SC
        SC.log(lg, year, "discipline_fine", team=t.id, kind=kind, amount=amt, baseline=round(baseline, 3))
    return amt


def suspension_baseline(kind: str, games: int) -> int:
    return games


def reduce_suspension(p, factor: float) -> int:
    """The Commissioner may shorten a suspension that has not been served: never lengthen it. Returns the new number of games left."""
    ruling = GV.reduce_penalty("suspension", float(p.suspended), factor, "commissioner")
    assert GV.shrink_only(ruling)
    p.suspended = int(round(ruling.after))
    return p.suspended
