"""The general manager's plan for the offseason (Step B of the ring of accountability).

The GM scouts and assembles the team. Two of her choices are now hers, through Decision Points; each has a default that is exactly the
rule the engine used before, so a league on the autopilot is unchanged by them:

  * `gm_draft_focus`: how she picks positions in the draft. "needs" (the old rule) leans toward the positions where the roster is short;
    "best_player" ignores need and takes the position by its weight in the lineup (the kickers and punters rule still applies).
  * `gm_cap_plan`: how much room she keeps back from the cap when she re-signs and signs free agents. "balanced" is the old three
    million; "tight" keeps more back, which banks room for next year (up to the $25M bank) at the risk of missing the payroll floor;
    "all_in" spends nearer to the limit. The hard cap and the floor are the engine's: a plan only moves the club's own margin.

Both are small and bounded; neither can break a cap rule, and the fairness bands are re-tested with agents choosing at random.
"""
from __future__ import annotations

FOCUS = ("needs", "best_player")
CAP_PLANS = {"tight": 3.0, "balanced": 0.0, "all_in": -2.0}      # added to the club's margin below the limit (roster_model.cap_headroom, $M)


def plans(lg, year: int) -> dict:
    """{team id: {"draft": focus, "headroom": added margin}} for the coming offseason, after the GMs have chosen."""
    import decisions as D
    dps, meta = [], []
    for t in lg.teams:
        g = t.gm
        if g is None:
            continue
        rank = 1 + sum(1 for x in lg.teams if x.strength > t.strength)
        floor_note = "about $90M over four seasons"
        last_pay = round(t.cash[-1], 1) if t.cash else None
        dps.append(D.DecisionPoint("gm_draft_focus", year, t.id, "gm", g,
                                   dict(picks="your own and the ones you hold", short_positions=sorted(_short(t)),
                                        your_team_strength_rank=rank),
                                   [dict(id="needs", label="Draft for need (lean toward the positions the roster is short at)", tags={}),
                                    dict(id="best_player", label="Draft the best player (ignore need)", tags={})],
                                   "needs", dict(team=t, strength_rank=rank)))
        dps.append(D.DecisionPoint("gm_cap_plan", year, t.id, "gm", g,
                                   dict(cap=100.0, payroll_floor=floor_note, banked_room=round(t.bank, 1), last_payroll=last_pay,
                                        your_team_strength_rank=rank),
                                   [dict(id="tight", label="Keep extra room back (bank it for next year)", tags={"extra_margin_m": 3.0}),
                                    dict(id="balanced", label="Keep the usual margin", tags={"extra_margin_m": 0.0}),
                                    dict(id="all_in", label="Spend closer to the limit", tags={"extra_margin_m": -2.0})],
                                   "balanced", dict(team=t, strength_rank=rank)))
        meta.append(t)
    picks = D.decide_many(lg, dps) if dps else []
    out = {t.id: {"draft": "needs", "headroom": 0.0} for t in lg.teams}
    for i, t in enumerate(meta):
        focus, cap = picks[2 * i], picks[2 * i + 1]
        out[t.id] = {"draft": focus, "headroom": CAP_PLANS[cap]}
        if (focus, cap) != ("needs", "balanced"):
            t.gm.decision_log.append({"year": year, "action": f"planned the offseason: draft {focus.replace('_', ' ')}, cap {cap.replace('_', ' ')}"})
    return out


def _short(t) -> list:
    from positions import ROSTER_COUNTS
    counts = {}
    for p in t.roster or ():
        counts[p.pos] = counts.get(p.pos, 0) + 1
    return [pos for pos in ROSTER_COUNTS if counts.get(pos, 0) < ROSTER_COUNTS[pos]]
