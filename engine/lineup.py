"""Who is on the field: healthy depth chart and the unit ratings the game engine uses."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import accumulate
from typing import Dict, List

from positions import POSITIONS, STARTERS
from players import Player


def depth_chart(roster: List[Player]) -> Dict[str, List[Player]]:
    """Healthy players by position, best first. If too few are healthy the best injured
    players fill in (they play hurt at the same rating); that should be very rare."""
    chart: Dict[str, List[Player]] = {}
    for pos in POSITIONS:
        at = sorted((p for p in roster if p.pos == pos), key=lambda p: -p.ovr)
        healthy = [p for p in at if p.weeks_out == 0 and p.suspended == 0]
        hurt = [p for p in at if p.weeks_out > 0 or p.suspended > 0]
        chart[pos] = healthy + hurt
    return chart


def _mean(xs):
    return sum(xs) / len(xs)


@dataclass
class Lineup:
    team_id: int
    qb: Player
    rbs: List[Player]
    wrs: List[Player]
    te: Player
    ol: List[Player]
    dl: List[Player]
    lb: List[Player]
    cb: List[Player]
    s: List[Player]
    k: Player
    p: Player
    # unit ratings (1-100 scale, league average about 60)
    qb_acc: float = 0.0
    qb_arm: float = 0.0
    qb_aware: float = 0.0
    rec: float = 0.0
    pass_block: float = 0.0
    run_block: float = 0.0
    rb_run: float = 0.0
    pass_rush: float = 0.0
    coverage: float = 0.0
    ball_skills: float = 0.0
    run_stop: float = 0.0
    k_acc: float = 0.0
    k_pow: float = 0.0
    p_pow: float = 0.0
    p_acc: float = 0.0
    # attribution lists for box scores
    targets: List[Player] = None
    target_cum: List[float] = None
    carriers: List[Player] = None
    carry_cum: List[float] = None
    rushers: List[Player] = None
    rush_cum: List[float] = None
    tacklers: List[Player] = None
    tackle_cum: List[float] = None
    pickers: List[Player] = None
    pick_cum: List[float] = None

    FEATURES = ("qb_acc", "qb_arm", "qb_aware", "rec", "pass_block", "run_block", "rb_run",
                "pass_rush", "coverage", "ball_skills", "run_stop", "k_acc", "k_pow", "p_pow")

    def features(self):
        return [getattr(self, f) for f in self.FEATURES]


def _rec_rating(p: Player) -> float:
    r = p.ratings
    if p.pos == "WR":
        return (r["route"] + r["hands"] + r["speed"]) / 3.0
    if p.pos == "TE":
        return (r["route"] + r["hands"]) / 2.0
    return r["hands"]                                   # RB


def build_lineup(team_id: int, roster: List[Player], coach=None, team=None) -> Lineup:
    ch = depth_chart(roster)
    qb, k, p = ch["QB"][0], ch["K"][0], ch["P"][0]
    rbs, wrs, te = ch["RB"][:2], ch["WR"][:3], ch["TE"][0]
    ol, dl, lb, cb, s = ch["OL"][:5], ch["DL"][:4], ch["LB"][:2], ch["CB"][:3], ch["S"][:2]
    L = Lineup(team_id, qb, rbs, wrs, te, ol, dl, lb, cb, s, k, p)

    L.qb_acc, L.qb_arm, L.qb_aware = qb.ratings["accuracy"], qb.ratings["arm"], qb.ratings["awareness"]
    # receivers: three WRs, the TE and the lead RB, weighted by how often they are targeted
    recs = [(wrs[0], 0.28), (wrs[1], 0.24), (wrs[2], 0.17), (te, 0.17), (rbs[0], 0.14)]
    L.targets = [r for r, _ in recs]
    L.target_cum = list(accumulate(w for _, w in recs))
    L.rec = sum(_rec_rating(r) * w for r, w in recs)
    L.pass_block = 0.92 * _mean([o.ratings["pass_block"] for o in ol]) + 0.08 * te.ratings["block"]
    L.run_block = 0.85 * _mean([o.ratings["run_block"] for o in ol]) + 0.15 * te.ratings["block"]
    rb_w = [0.65, 0.35]
    L.rb_run = sum(((r.ratings["elusive"] + r.ratings["power"]) / 2.0) * w for r, w in zip(rbs, rb_w))
    L.carriers = list(rbs)
    L.carry_cum = list(accumulate(rb_w))

    L.pass_rush = 0.8 * _mean([d.ratings["pass_rush"] for d in dl]) + 0.2 * _mean([b.ratings["pass_rush"] for b in lb])
    L.coverage = (0.5 * _mean([c.ratings["coverage"] for c in cb]) + 0.3 * _mean([x.ratings["coverage"] for x in s])
                  + 0.2 * _mean([b.ratings["coverage"] for b in lb]))
    L.ball_skills = _mean([c.ratings["ball_skills"] for c in cb] + [x.ratings["ball_skills"] for x in s])
    L.run_stop = (0.45 * _mean([d.ratings["run_stop"] for d in dl]) + 0.30 * _mean([b.ratings["run_stop"] for b in lb])
                  + 0.15 * _mean([x.ratings["tackling"] for x in s]) + 0.10 * _mean([c.ratings["tackling"] for c in cb]))
    L.k_acc, L.k_pow = k.ratings["accuracy"], k.ratings["power"]
    L.p_pow, L.p_acc = p.ratings["power"], p.ratings["accuracy"]

    if coach is not None or (team is not None and (getattr(team, "oc", None) is not None or getattr(team, "dc", None) is not None)):
        # the coaches: a small capped lift to the offensive or defensive units. The head coach's own (cards.COACH_POINTS_AT_100) is blended with
        # the coordinator who calls the plays, plus the fit of this season's scheme (coordinators.lifts)
        if team is not None:
            import coordinators
            o, d = coordinators.lifts(coach, team)
        else:
            o, d = coach.offense_points, coach.defense_points
        for f in ("qb_acc", "qb_arm", "qb_aware", "rec", "pass_block", "run_block", "rb_run"):
            setattr(L, f, getattr(L, f) + o)
        for f in ("pass_rush", "coverage", "ball_skills", "run_stop"):
            setattr(L, f, getattr(L, f) + d)

    # who gets credit: sacks go to pass rushers, interceptions to ball hawks, tackles to everyone
    rush = [(d, d.ratings["pass_rush"]) for d in dl] + [(b, 0.5 * b.ratings["pass_rush"]) for b in lb]
    L.rushers = [x for x, _ in rush]
    L.rush_cum = list(accumulate(w for _, w in rush))
    picks = [(c, c.ratings["ball_skills"]) for c in cb] + [(x, 1.1 * x.ratings["ball_skills"]) for x in s]
    L.pickers = [x for x, _ in picks]
    L.pick_cum = list(accumulate(w for _, w in picks))
    tack = ([(b, 1.6 * 60.0) for b in lb] + [(x, 1.2 * 60.0) for x in s] + [(c, 0.8 * 60.0) for c in cb]
            + [(d, 0.8 * 60.0) for d in dl])
    L.tacklers = [x for x, _ in tack]
    L.tackle_cum = list(accumulate(w for _, w in tack))
    return L
