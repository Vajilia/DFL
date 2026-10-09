"""The CEO card's answers to her fans (Step A1).

The ring of accountability (the Commissioner, 2026-10-09): fans are where outside revenue enters the league; the CEO answers to the fans
for the money; coaches and GMs answer to the CEO. Until now the fans reached the CEO (approval, recall, the boycott) but she could only
answer through formulas. This module gives her three things, all small and capped, none of which touches a game:

  * two Decision Points. `ceo_pledge`: each year, how much of a profit she puts back into the club (lean, standard or generous: the autopilot
    keeps the old formula, standard). `ceo_boycott`: while her fans are boycotting she can hold firm, concede (invest more next year and the
    boycott eases) or step aside (retire early, and the next CEO starts without the boycott); the autopilot concedes if she is ambitious;
  * three meters that belong to her and end with her tenure (the fanbase's meters are the permanent ones): Fan Rapport (how well she reads
    these fans: moves approval by at most 1 point), Standing Among CEOs (what the other 47 think of her: moves the forced-sale vote against
    her by at most 15 points of probability) and Legacy (what she will be remembered for: cosmetic, it changes nothing);
  * the fans' memory passes to the next CEO: a new CEO's honeymoon is warmer where the fans remember glory and colder where they remember
    a boycott, an exile or a drought, by at most 5 points.

Everything here is MODEL; each dial is named so it can be changed in one place.
"""
from __future__ import annotations

from typing import Dict, List

import fan_media_cards as FM
import rules as R

# ---- dials (MODEL) --------------------------------------------------------------------------------------------------------------
PLEDGE = {"lean": 0.60, "standard": 1.00, "generous": 1.40}   # her usual reinvest share (5% + up to 25% by ambition) times this
REINVEST_MAX = 0.45               # she never puts back more than this share of a profit
CONCEDE_FACTOR = 0.60             # a conceded boycott keeps this share of its level
CONCEDE_BONUS = 0.10              # ... and she adds this to next year's reinvest share
CONCEDE_AMBITION = 55.0           # the autopilot concedes when her ambition is at least this
RAPPORT_APPROVAL = 0.010          # Fan Rapport moves approval by at most this
STANDING_SALE = 0.15              # Standing Among CEOs moves the chance another CEO votes to force her sale by at most this
INHERIT_CAP = 0.05                # the fans' memory moves a new CEO's honeymoon by at most this ...
INHERIT_GLOW = 0.02               # ... 2 points per unit of remembered glory (a title, a return) or scar (an exile, a drought, a boycott) ...
INHERIT_GRUDGE = 0.03             # ... and up to 3 points for the fans' Grudge meter

METERS = {
    "rapport":  dict(label="Fan Rapport", high="she knows exactly what these fans want", low="she and the fans talk past each other", rate=0.25),
    "standing": dict(label="Standing Among CEOs", high="the other CEOs would back her in a pinch", low="the other CEOs would not lift a finger", rate=0.30),
    "legacy":   dict(label="Legacy", high="her name will be on the wall", low="she will be forgotten", rate=0.20),
}
START = {"rapport": 50.0, "standing": 50.0, "legacy": 15.0}


def ensure(o):
    """Old saves have no meters: give her the starting levels."""
    if not getattr(o, "meters", None):
        o.meters = dict(START)
    return o.meters


def value(o, key: str) -> float:
    return ensure(o)[key]


def rapport_nudge(o) -> float:
    return RAPPORT_APPROVAL * (value(o, "rapport") - 50.0) / 50.0


def sale_shift(o) -> float:
    """Added to the chance another CEO votes to force her sale (a CEO the others respect is slower to be cast out)."""
    return -STANDING_SALE * (value(o, "standing") - 50.0) / 50.0


def reinvest_share(o, base: float) -> float:
    """Her share of a profit put back into the club this year: her formula times her pledge, plus any concession, capped."""
    return min(REINVEST_MAX, base * PLEDGE.get(getattr(o, "pledge", "standard"), 1.0) + getattr(o, "pledge_bonus", 0.0))


# ---- Decision Point: the pledge --------------------------------------------------------------------------------------------------
def pledge_decisions(lg, year: int, teams, lines, base_share) -> Dict[int, str]:
    """Every CEO whose club made a profit chooses her pledge for it (lean, standard, generous). The autopilot is standard."""
    import decisions as D
    dps = []
    for t in teams:
        o, fb = t.owner, t.fans
        if o is None or lines[t.id]["surplus"] <= 0.0:
            continue
        ctx = dict(profit_this_year=lines[t.id]["surplus"], your_usual_share=round(base_share(o), 3), fan_approval_of_you=round(o.approval, 3),
                   fans_usual_ask=None if fb is None else round(_ask(t), 2), boycott=None if fb is None else round(fb.boycott, 2),
                   fan_meters=None if fb is None else {FM.METERS[k]["label"]: round(m["value"]) for k, m in fb.meters.items()},
                   your_meters={METERS[k]["label"]: round(v) for k, v in ensure(o).items()}, draw_cap=100.0)
        opts = [dict(id=k, label=f"Put back {int(100 * v)}% of your usual share", tags={"share": round(min(REINVEST_MAX, base_share(o) * v), 3)}) for k, v in PLEDGE.items()]
        dps.append(D.DecisionPoint("ceo_pledge", year, t.id, "owner", o, ctx, opts, "standard", dict(team=t)))
    picks = D.decide_many(lg, dps)
    out = {}
    for dp, pick in zip(dps, picks):
        dp.actor.pledge = pick
        out[dp.team_id] = pick
        dp.actor.decision_log.append({"year": year, "interaction": "ceo_pledge", "action": f"pledged the {pick} share of profit to the club"})
    return out


def _ask(t) -> float:
    import finance as F
    return F.fan_want(t)


# ---- Decision Point: the answer to a boycott --------------------------------------------------------------------------------------
def boycott_decisions(lg, year: int, teams) -> Dict[int, str]:
    """Each CEO whose fans are boycotting answers: hold firm, concede, or step aside. Returns {team: choice}; the caller applies them."""
    import decisions as D
    dps = []
    for t in teams:
        o, fb = t.owner, t.fans
        if o is None or fb is None or fb.boycott < FM.BOYCOTT_START:
            continue
        ctx = dict(boycott_level=round(fb.boycott, 2), local_revenue_lost_share=round(FM.BOYCOTT_MAX * fb.boycott, 3), fan_approval_of_you=round(o.approval, 3),
                   seasons_in_the_chair=o.seasons_owned, your_tenure_ends_in=max(0, o.tenure - o.seasons_owned) if o.tenure else None,
                   what_the_fans_remember=[m["text"] for m in sorted(fb.memories, key=lambda m: -m["weight"])[:4]],
                   your_meters={METERS[k]["label"]: round(v) for k, v in ensure(o).items()})
        opts = [dict(id="hold", label="Hold firm: change nothing", tags={}),
                dict(id="concede", label=f"Concede: invest {int(100 * CONCEDE_BONUS)} points more of next year's profit; the boycott eases", tags={"eases": CONCEDE_FACTOR}),
                dict(id="step_aside", label="Step aside: retire now, and the next CEO starts without the boycott", tags={"ends_tenure": True})]
        default = "concede" if o.ratings["ambition"] >= CONCEDE_AMBITION else "hold"
        dps.append(D.DecisionPoint("ceo_boycott", year, t.id, "owner", o, ctx, opts, default, dict(team=t)))
    picks = D.decide_many(lg, dps)
    out = {}
    for dp, pick in zip(dps, picks):
        t, o = dp.internal["team"], dp.actor
        out[t.id] = pick
        if pick == "concede":
            t.fans.boycott = round(t.fans.boycott * CONCEDE_FACTOR, 3)
            o.pledge_bonus = CONCEDE_BONUS
            ensure(o)["rapport"] = min(100.0, o.meters["rapport"] + 4.0)
        o.decision_log.append({"year": year, "interaction": "ceo_boycott",
                               "action": {"hold": "held firm against the boycott", "concede": "conceded to the boycott", "step_aside": "stepped aside because of the boycott"}[pick]})
    return out


# ---- the meters -----------------------------------------------------------------------------------------------------------------------
def season(t, year: int, pct: float, playoffs: bool, champion: bool, exiled: bool):
    """The CEO's meters digest one season (called after the fans have). Rapport then moves approval by its small cap."""
    o, fb = t.owner, t.fans
    if o is None:
        return
    m = ensure(o)
    ln = (t.books[-1] if getattr(t, "books", None) else None) or {}
    ln = ln if ln.get("year") == year else {}
    boycott = 0.0 if fb is None else fb.boycott
    tenure_bonus = min(15.0, float(o.seasons_owned))
    t_rap = 50.0 + 80.0 * (o.approval - 0.5) + tenure_bonus - 20.0 * boycott
    paid, got = ln.get("subsidy_paid", 0.0) > 0, ln.get("subsidy_received", 0.0) > 0
    greedy = ln.get("nudge", 0.0) < -0.005 and ln.get("draw", 0.0) >= 80.0
    t_stand = 50.0 + (22.0 if paid else 0.0) - (25.0 if got else 0.0) - (12.0 if greedy else 0.0) + (8.0 if champion else 0.0)
    m["rapport"] = round(max(1.0, min(100.0, m["rapport"] + METERS["rapport"]["rate"] * (t_rap - m["rapport"]))), 1)
    m["standing"] = round(max(1.0, min(100.0, m["standing"] + METERS["standing"]["rate"] * (t_stand - m["standing"]))), 1)
    m["legacy"] = round(max(1.0, min(100.0, m["legacy"] + 10.0 * (pct - 0.5) + 14.0 * champion + 3.0 * playoffs - 6.0 * exiled)), 1)
    o.approval = max(0.0, min(1.0, o.approval + rapport_nudge(o)))
    if fb is not None:
        fb.approval = o.approval


def inherit(t, year: int):
    """A new CEO sits down in front of a fanbase with a memory: her honeymoon is shaped by it (capped)."""
    o, fb = t.owner, t.fans
    if o is None or fb is None:
        return
    adj = INHERIT_GLOW * FM.glow(fb, scars=("exile", "drought", "boycott"))
    g = fb.meters.get("grudge")
    if g is not None:
        adj -= INHERIT_GRUDGE * (g["value"] - 50.0) / 50.0
    adj = max(-INHERIT_CAP, min(INHERIT_CAP, adj))
    o.approval = max(0.0, min(1.0, o.approval + adj))
    fb.approval = o.approval
