"""Records, rankings and tiebreakers."""
from __future__ import annotations

import random
from collections import defaultdict
from fractions import Fraction
from typing import Dict, Iterable, List

import rules as R
from schedule import Game


class Stats:
    __slots__ = ("wins", "losses", "ties", "pf", "pa", "div_w", "div_l", "div_t", "conf_w", "conf_l", "conf_t", "h2h")

    def __init__(self):
        self.wins = self.losses = self.ties = self.pf = self.pa = 0
        self.div_w = self.div_l = self.div_t = self.conf_w = self.conf_l = self.conf_t = 0
        self.h2h: Dict[int, List[int]] = defaultdict(lambda: [0, 0, 0])     # [wins, losses, ties]

    @property
    def games(self) -> int:
        return self.wins + self.losses + self.ties

    @property
    def pct(self) -> Fraction:
        """Win percentage, a tie counting as half a win."""
        return Fraction(2 * self.wins + self.ties, 2 * self.games) if self.games else Fraction(0)

    @property
    def diff(self) -> int:
        return self.pf - self.pa

    @property
    def record(self) -> str:
        return f"{self.wins}-{self.losses}" + (f"-{self.ties}" if self.ties else "")


class StatsTable(dict):
    """team id -> Stats, plus the games behind them so the NFL tiebreakers can see every result."""
    league = None
    games: list = None

    @property
    def ledger(self):
        if getattr(self, "_ledger", None) is None:
            from tiebreak import Ledger
            self._ledger = Ledger(self.league, self.games, list(self.keys()))
        return self._ledger


def compute_stats(league, games: Iterable[Game], team_ids: Iterable[int]) -> Dict[int, Stats]:
    games = list(games)
    stats = StatsTable((tid, Stats()) for tid in team_ids)
    stats.league, stats.games = league, games
    for g in games:
        if g.home_pts is None:
            continue
        for tid, opp, pf, pa in ((g.home, g.away, g.home_pts, g.away_pts), (g.away, g.home, g.away_pts, g.home_pts)):
            if tid not in stats:
                continue
            s = stats[tid]
            k = 0 if pf > pa else 2 if pf == pa else 1        # 0 win, 1 loss, 2 tie
            s.pf += pf
            s.pa += pa
            if k == 0:
                s.wins += 1
            elif k == 1:
                s.losses += 1
            else:
                s.ties += 1
            s.h2h[opp][k] += 1
            a, b = league.by_id[tid], league.by_id[opp]
            if a.conf == b.conf:
                if k == 0:
                    s.conf_w += 1
                elif k == 1:
                    s.conf_l += 1
                else:
                    s.conf_t += 1
                if a.div == b.div:
                    if k == 0:
                        s.div_w += 1
                    elif k == 1:
                        s.div_l += 1
                    else:
                        s.div_t += 1
    return stats


def _pct(w, l, t=0):
    return Fraction(2 * w + t, 2 * (w + l + t)) if w + l + t else Fraction(1, 2)


def _metric(name: str, tid: int, group: List[int], stats: Dict[int, Stats]):
    s = stats[tid]
    if name == "head_to_head":
        w = sum(s.h2h[o][0] for o in group if o != tid and o in s.h2h)
        l = sum(s.h2h[o][1] for o in group if o != tid and o in s.h2h)
        t = sum(s.h2h[o][2] for o in group if o != tid and o in s.h2h)
        return _pct(w, l, t)
    if name == "division_record":
        return _pct(s.div_w, s.div_l, s.div_t)
    if name == "conference_record":
        return _pct(s.conf_w, s.conf_l, s.conf_t)
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


def rank_by_style(kind: str, ids: List[int], stats, rng: random.Random, log: list = None, context: str = "") -> List[int]:
    """Best to worst. kind: division | conference | ambassador. Uses the NFL procedures when
    R.TIEBREAK_STYLE == "nfl" and the stats table knows its games."""
    if R.TIEBREAK_STYLE == "nfl" and isinstance(stats, StatsTable) and stats.league is not None:
        import tiebreak as T
        fn = {"division": T.rank_division, "conference": T.rank_conference, "ambassador": T.rank_ambassador}[kind]
        return fn(stats.ledger, ids, rng, log, context or kind)
    crit = {"division": R.TIEBREAKERS, "conference": R.CROSS_DIVISION_TIEBREAKERS,
            "ambassador": R.RECORD_ONLY_TIEBREAKERS}[kind]
    return rank_teams(ids, stats, crit, rng, log, context or kind)


def draft_worst_to_best(ids: List[int], stats, rng: random.Random, log: list = None, context: str = "draft") -> List[int]:
    """Draft order for a group of teams: worst record picks first."""
    if R.TIEBREAK_STYLE == "nfl" and isinstance(stats, StatsTable) and stats.league is not None:
        import tiebreak as T
        return T.draft_order(stats.ledger, ids, rng, log, context)
    return rank_teams(ids, stats, R.RECORD_ONLY_TIEBREAKERS, rng, log, context)[::-1]
