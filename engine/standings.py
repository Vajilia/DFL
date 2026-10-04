"""Records, rankings and tiebreakers."""
from __future__ import annotations

import random
from collections import defaultdict
from fractions import Fraction
from typing import Dict, Iterable, List

import rules as R
from schedule import Game


class Stats:
    __slots__ = ("wins", "losses", "pf", "pa", "div_w", "div_l", "conf_w", "conf_l", "h2h")

    def __init__(self):
        self.wins = self.losses = self.pf = self.pa = 0
        self.div_w = self.div_l = self.conf_w = self.conf_l = 0
        self.h2h: Dict[int, List[int]] = defaultdict(lambda: [0, 0])

    @property
    def games(self) -> int:
        return self.wins + self.losses

    @property
    def pct(self) -> Fraction:
        return Fraction(self.wins, self.games) if self.games else Fraction(0)

    @property
    def diff(self) -> int:
        return self.pf - self.pa

    @property
    def record(self) -> str:
        return f"{self.wins}-{self.losses}"


def compute_stats(league, games: Iterable[Game], team_ids: Iterable[int]) -> Dict[int, Stats]:
    stats = {tid: Stats() for tid in team_ids}
    for g in games:
        if g.home_pts is None:
            continue
        for tid, opp, pf, pa in ((g.home, g.away, g.home_pts, g.away_pts), (g.away, g.home, g.away_pts, g.home_pts)):
            if tid not in stats:
                continue
            s = stats[tid]
            won = pf > pa
            s.pf += pf
            s.pa += pa
            if won:
                s.wins += 1
            else:
                s.losses += 1
            s.h2h[opp][0 if won else 1] += 1
            a, b = league.by_id[tid], league.by_id[opp]
            if a.conf == b.conf:
                if won:
                    s.conf_w += 1
                else:
                    s.conf_l += 1
                if a.div == b.div:
                    if won:
                        s.div_w += 1
                    else:
                        s.div_l += 1
    return stats


def _pct(w, l):
    return Fraction(w, w + l) if w + l else Fraction(1, 2)


def _metric(name: str, tid: int, group: List[int], stats: Dict[int, Stats]):
    s = stats[tid]
    if name == "head_to_head":
        w = sum(s.h2h[o][0] for o in group if o != tid and o in s.h2h)
        l = sum(s.h2h[o][1] for o in group if o != tid and o in s.h2h)
        return _pct(w, l)
    if name == "division_record":
        return _pct(s.div_w, s.div_l)
    if name == "conference_record":
        return _pct(s.conf_w, s.conf_l)
    if name == "point_differential":
        return Fraction(s.diff, s.games) if s.games else Fraction(0)    # per game, so 7- and 18-game records compare
    raise ValueError(name)


def rank_teams(ids: List[int], stats: Dict[int, Stats], criteria, rng: random.Random,
               log: list = None, context: str = "") -> List[int]:
    """Order teams best to worst: win percentage first, then the tiebreakers in order.
    When a tiebreaker separates only some of a tied group, the remaining tied teams
    start the tiebreakers again from the top. Every tiebreak that was needed is logged."""
    out: List[int] = []
    by_pct = defaultdict(list)
    for tid in ids:
        by_pct[stats[tid].pct].append(tid)
    for pct in sorted(by_pct, reverse=True):
        out.extend(_resolve(by_pct[pct], stats, criteria, rng, log, context))
    return out


def _resolve(group, stats, criteria, rng, log, context):
    if len(group) == 1:
        return group
    for crit in criteria:
        if crit == "seeded_coin_flip":
            shuffled = group[:]
            rng.shuffle(shuffled)
            if log is not None:
                log.append({"context": context, "size": len(group), "decided_by": crit, "teams": group[:]})
            return shuffled
        vals = {t: _metric(crit, t, group, stats) for t in group}
        if len(set(vals.values())) == 1:
            continue
        if log is not None:
            log.append({"context": context, "size": len(group), "decided_by": crit, "teams": group[:]})
        out = []
        for v in sorted(set(vals.values()), reverse=True):
            sub = [t for t in group if vals[t] == v]
            out.extend(_resolve(sub, stats, criteria, rng, log, context))
        return out
    # no coin flip in the list and nothing separated them: keep the order given
    return group
