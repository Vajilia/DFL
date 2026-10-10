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


def _table(dp) -> bool:
    """A negotiation table's turn (interviews.py). The staffing adversaries below play only the CEO's review and hire choices and leave
    the tables to the rules."""
    return dp.kind.startswith(("interview", "contract", "fan_", "ceo_", "coord_", "scheme_", "gm_", "hire_coordinator"))


def _most_fires(dp):
    return max(dp.options, key=lambda o: o["tags"].get("fires", 0))["id"]


class StandPat:
    """Nobody is ever fired."""
    name = "stand-pat"

    def choose(self, dp):
        return ("keep_all" if dp.kind == "staff_review" else dp.default), "stand pat"


class ChurnOracle:
    """Every CEO fires everyone every year and always hires the truly best candidate. Hiring skill at its legal limit, league-wide."""
    name = "churn-oracle"

    def choose(self, dp):
        if _table(dp):
            return dp.default, "the rules"
        return (_most_fires(dp) if dp.kind == "staff_review" else _best(dp)), "churn and pick the best"


class EliteOracle:
    """Only the strongest teams churn and hire perfectly; everyone else stands pat. The most unequal use of hiring skill."""
    name = "elite-oracle"

    def __init__(self, top_n: int = 8):
        self.top_n = top_n

    def choose(self, dp):
        if _table(dp):
            return dp.default, "the rules"
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
        if _table(dp):
            return dp.default, "the rules"
        rank = dp.internal["strength_rank"]
        if dp.kind == "staff_review":
            return _most_fires(dp), "churn"
        if rank <= self.n:
            return _best(dp), "best"
        if rank > 48 - self.n:
            return _best(dp, worst=True), "worst"
        return dp.default, "default"


class StarHunter:
    """Everybody fires every coach who is not already a star in the media's eyes, and hires the most famous candidate on offer,
    else the best. The worst case for reputation: every CEO chases fame, and the carousel recycles the famous."""
    name = "star-hunter"

    def choose(self, dp):
        if _table(dp):
            return dp.default, "the rules"
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
    """Always hires a person who is between jobs when one is on offer (every CEO recycles the same people), else the best."""
    name = "carousel-rider"

    def choose(self, dp):
        if dp.kind in ("hire_coach", "hire_gm"):
            vets = [o["id"] for o in dp.options if o["tags"].get("between_jobs")]
            if vets:
                return vets[0], "a familiar face"
            return _best(dp), "best"
        return dp.default, "default"


class LockIn:
    """The worst case for guarantees. The strongest teams hire the truly best candidate and guarantee her the maximum (three reviews
    of safety, and every candidate accepts); the weakest hire the worst candidate on no guarantee, and everyone else follows the rules.
    Contracts used to widen the gap between the top and the bottom as far as the rules let them."""
    name = "lock-in"

    def __init__(self, n: int = 8):
        self.n = n

    def choose(self, dp):
        rank = dp.internal["strength_rank"]
        top, bottom = rank <= self.n, rank > 48 - self.n
        if dp.kind == "interview_offer":
            return ("offer_3" if top else "offer_0"), "lock in the best" if top else "no guarantee"
        if _table(dp):
            return ("accept" if "accept" in dp.option_ids else dp.default), "sign"
        if dp.kind in ("hire_coach", "hire_gm"):
            if top:
                return _best(dp), "best"
            if bottom:
                return _best(dp, worst=True), "worst"
        return dp.default, "default"


class EveryoneWalks:
    """Every candidate refuses every job. The league office fills every seat by the old rule, so the league should simply be the old one,
    but every table and every fallback is exercised."""
    name = "everyone-walks"

    def choose(self, dp):
        if dp.kind in ("interview_reply", "interview_final"):
            return "walk", "refuse"
        return dp.default, "default"


class HardBargain:
    """Every candidate asks for the most she can and walks if she does not get it; every CEO holds at her first offer (nothing).
    The CEOs keep choosing among who is left and the league office fills the seat if no one will sign."""
    name = "hard-bargain"

    def choose(self, dp):
        if dp.kind == "interview_reply":
            asks = [o["id"] for o in dp.options if o["id"].startswith("counter_")]
            return (asks[-1] if asks else "accept"), "ask for the most"
        if dp.kind == "interview_counter":
            return "hold", "hold the line"
        if dp.kind == "interview_final":
            return "walk", "no deal"
        return dp.default, "default"


class RosterOracle:
    """The worst case at the GM's desk. The `n` strongest clubs' GMs choose with perfect sight at every draft pick, re-signing, free-agent signing and
    trade (the draft position with the most role utility, the player who truly adds the most, the trade that truly gains the most); the `n` weakest
    clubs' GMs choose the worst legal option every time. Everyone else follows the rules. Roster skill pushed to its legal limit in both directions."""
    name = "roster-oracle"

    def __init__(self, n: int = 8):
        self.n = n

    def choose(self, dp):
        if not dp.kind.startswith(("gm_draft_pick", "gm_resign", "gm_free_agent", "gm_trade")):
            return dp.default, "the rules"
        rank = dp.internal["strength_rank"]
        top, bottom = rank <= self.n, rank > 48 - self.n
        if not (top or bottom):
            return dp.default, "the rules"
        pick = max if top else min
        if dp.kind == "gm_draft_pick":
            import roles
            t, true = dp.internal["team"], dp.internal["true"]
            return pick(dp.options, key=lambda o: roles.utility(t.roster, true[o["id"]][0], true[o["id"]][1]))["id"], "most true role utility" if top else "least"
        if dp.kind == "gm_resign":
            import roles
            p = dp.internal["player"]
            u = roles.utility(dp.internal["rest"], p.pos, p.ovr)
            good = "re_sign" if u > 0 else "let_walk"
            return (good if top else ("let_walk" if good == "re_sign" else "re_sign")), "true value"
        if dp.kind == "gm_free_agent":
            import roles
            t = dp.internal["team"]
            cands = dp.internal["candidates"]
            return pick(cands, key=lambda k: roles.utility(t.roster, cands[k].pos, cands[k].ovr)), "true best" if top else "true worst"
        gain = dp.internal["true_get"] - dp.internal["true_give"]
        return ("accept" if (gain >= 0) == top else "decline"), "true value"

