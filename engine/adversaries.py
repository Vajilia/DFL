"""Adversarial drivers: stand-ins for the worst legal behavior, used to test that the fairness bands hold whatever agents do.

They read the TRUE state through dp.internal (an agent never sees it), so they are stronger than any real agent could be.
Each plays only legal options; the guard would reject anything else. See decision_sweep.py for the study that uses them.
"""
from __future__ import annotations

import staff_cards as S


def coach_value(c) -> float:
    return c.offense_points + c.defense_points + c.development_points


def gm_value(g) -> float:
    return g.scouting_points / S.GM_SCOUTING_POINTS + (1.0 - g.retention_factor) / S.GM_RETENTION


def _best(dp, worst=False):
    val = coach_value if dp.kind == "hire_coach" else gm_value
    items = dp.internal["candidates"].items()
    key = (lambda kv: val(kv[1]))
    return (min if worst else max)(items, key=key)[0]


def _most_fires(dp):
    return max(dp.options, key=lambda o: o["tags"].get("fires", 0))["id"]


class StandPat:
    """Nobody is ever fired."""
    name = "stand-pat"

    def choose(self, dp):
        return ("keep_all" if dp.kind == "staff_review" else "candidate_0"), "stand pat"


class ChurnOracle:
    """Every owner fires everyone every year and always hires the truly best candidate. Hiring skill at its legal limit, league-wide."""
    name = "churn-oracle"

    def choose(self, dp):
        return (_most_fires(dp) if dp.kind == "staff_review" else _best(dp)), "churn and pick the best"


class EliteOracle:
    """Only the strongest teams churn and hire perfectly; everyone else stands pat. The most unequal use of hiring skill."""
    name = "elite-oracle"

    def __init__(self, top_n: int = 8):
        self.top_n = top_n

    def choose(self, dp):
        rank = dp.internal["strength_rank"]
        if rank <= self.top_n:
            return ChurnOracle().choose(dp)
        return StandPat().choose(dp)


class Polarized:
    """The strongest teams hire perfectly; the weakest hire the worst candidate every time (all churn). Maximum spread of staff quality."""
    name = "polarized"

    def __init__(self, n: int = 8):
        self.n = n

    def choose(self, dp):
        rank = dp.internal["strength_rank"]
        if dp.kind == "staff_review":
            return _most_fires(dp), "churn"
        if rank <= self.n:
            return _best(dp), "best"
        if rank > 48 - self.n:
            return _best(dp, worst=True), "worst"
        return "candidate_0", "default"


class StarHunter:
    """Everybody fires every coach who is not already a star in the media's eyes, and hires the most famous candidate on offer,
    else the best. The worst case for reputation: every owner chases fame, and the carousel recycles the famous."""
    name = "star-hunter"

    def choose(self, dp):
        if dp.kind == "staff_review":
            c = dp.internal["coach"]
            offered = dp.option_ids
            if c is not None and c.standing not in ("legend", "Hall of Famer", "star") and "fire_coach" in offered:
                return ("fire_both" if "fire_both" in offered else "fire_coach"), "hunt"
            return dp.default, "default"
        if dp.kind == "hire_coach":
            k, c = max(dp.internal["candidates"].items(), key=lambda kc: kc[1].esteem)
            if c.esteem > 0:
                return k, "the most famous"
        return _best(dp), "best"


class CarouselRider:
    """Always hires a person who is between jobs when one is on offer (every owner recycles the same people), else the best."""
    name = "carousel-rider"

    def choose(self, dp):
        if dp.kind in ("hire_coach", "hire_gm"):
            vets = [o["id"] for o in dp.options if o["tags"].get("between_jobs")]
            if vets:
                return vets[0], "a familiar face"
            return _best(dp), "best"
        return dp.default, "default"
