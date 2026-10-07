"""NFL-style tiebreaking procedures (the Commissioner, 2026-10-04: "all tie-breaking scenarios mirror the NFL").

The procedures follow the NFL's published ones (checked against nfl.com on 2026-10-04):

  division ties         head-to-head, division record, common games, conference record, strength of victory,
                        strength of schedule, combined ranking in points among conference teams, then among all
                        teams, net points in common games, net points in all games, net touchdowns, coin toss
  wild card / seeding   head-to-head (sweep when three or more), conference record, common games (at least four),
                        strength of victory, strength of schedule, combined ranking (conference, all), net points
                        in conference games, net points in all games, net touchdowns, coin toss
  draft order           strength of schedule (the lower one picks first), then the division or conference
                        procedure, then head-to-head, common games (at least four), strength of victory, combined
                        ranking, net points, net touchdowns, coin toss. The worse team picks first at each step.

Rules that go beyond what the NFL has to deal with are ADAPTED (the rulebook label):
  * three or more clubs: a step keeps the clubs with the best value; when two remain the two-club list restarts
    from step 1 (the NFL's restart rule); the process is repeated to rank everyone, not just pick a winner;
  * wild-card ties among clubs of one division are first settled by the division procedure;
  * the Ambassador Season (8 teams from different divisions, each playing the others once) uses head-to-head,
    strength of victory, strength of schedule, net points, net touchdowns, coin toss;
  * where a game's touchdown count was not kept (the fast and placeholder engines) it is estimated as points // 7.
"""
from __future__ import annotations

import random
from collections import defaultdict
from fractions import Fraction
from typing import Callable, Dict, List, Optional

import rules as R


class Ledger:
    """Every game of a set of teams, ready for tiebreak arithmetic."""

    def __init__(self, league, games, team_ids):
        self.league = league
        self.ids = list(team_ids)
        self.idset = set(self.ids)
        # tid -> list of (opp, pf, pa, tdf, tda)
        self.g: Dict[int, List[tuple]] = {t: [] for t in self.ids}
        for g in games:
            if g.home_pts is None:
                continue
            htd = g.home_tds if getattr(g, "home_tds", None) is not None else g.home_pts // 7
            atd = g.away_tds if getattr(g, "away_tds", None) is not None else g.away_pts // 7
            if g.home in self.idset:
                self.g[g.home].append((g.away, g.home_pts, g.away_pts, htd, atd))
            if g.away in self.idset:
                self.g[g.away].append((g.home, g.away_pts, g.home_pts, atd, htd))
        # win credit: a win is 1, a tie is 1/2
        self.wins = {t: self._credit(self.g[t]) for t in self.ids}
        self.n = {t: len(self.g[t]) for t in self.ids}
        self._rank_cache: Dict[tuple, Dict[int, int]] = {}

    # basic helpers --------------------------------------------------------------
    @staticmethod
    def _credit(games) -> Fraction:
        return sum((Fraction(1) if pf > pa else Fraction(1, 2) if pf == pa else Fraction(0) for _, pf, pa, _, _ in games), Fraction(0))

    def pct(self, wins, n: int) -> Fraction:
        return Fraction(wins) / n if n else Fraction(1, 2)

    def conf(self, t):
        return self.league.by_id[t].conf

    def div(self, t):
        return self.league.by_id[t].division_id

    def games_vs(self, t, opps) -> List[tuple]:
        s = set(opps)
        return [x for x in self.g[t] if x[0] in s]

    def record_pct(self, games: List[tuple]) -> Fraction:
        return self.pct(self._credit(games), len(games))

    # metrics (higher = better) ------------------------------------------------------
    def m_h2h(self, t, group):
        gs = self.games_vs(t, [o for o in group if o != t])
        return None if not gs else self.record_pct(gs)

    def m_div(self, t, group):
        return self.record_pct([x for x in self.g[t] if self.div(x[0]) == self.div(t)])

    def m_conf(self, t, group):
        return self.record_pct([x for x in self.g[t] if self.conf(x[0]) == self.conf(t)])

    def common_opps(self, group):
        sets = [set(x[0] for x in self.g[t]) for t in group]
        return set.intersection(*sets) - set(group)

    def m_common(self, t, group, minimum=0):
        co = self.common_opps(group)
        counts = [len(self.games_vs(u, co)) for u in group]
        if not co or min(counts) < minimum:
            return None
        return self.record_pct(self.games_vs(t, co))

    def m_sov(self, t, group):
        beaten = [x[0] for x in self.g[t] if x[1] > x[2]]
        if not beaten:
            return Fraction(0)
        w = sum(self.wins[o] for o in beaten)
        n = sum(self.n[o] for o in beaten)
        return self.pct(w, n)

    def m_sos(self, t, group):
        opps = [x[0] for x in self.g[t]]
        w = sum(self.wins[o] for o in opps)
        n = sum(self.n[o] for o in opps)
        return self.pct(w, n)

    def _ranks(self, scope: str, which: str) -> Dict[int, int]:
        key = (scope, which)
        if key in self._rank_cache:
            return self._rank_cache[key]
        out = {}
        for c in ([None] if scope == "all" else sorted({self.conf(t) for t in self.ids})):
            members = self.ids if c is None else [t for t in self.ids if self.conf(t) == c]
            vals = {t: sum(x[1] if which == "pf" else x[2] for x in self.g[t]) for t in members}
            for t in members:
                out[t] = 1 + sum(1 for v in vals.values() if (v > vals[t] if which == "pf" else v < vals[t]))
        self._rank_cache[key] = out
        return out

    def m_rank_conf(self, t, group):
        return -(self._ranks("conf", "pf")[t] + self._ranks("conf", "pa")[t])

    def m_rank_all(self, t, group):
        return -(self._ranks("all", "pf")[t] + self._ranks("all", "pa")[t])

    def m_net_common(self, t, group):
        co = self.common_opps(group)
        return sum(pf - pa for _, pf, pa, _, _ in self.games_vs(t, co)) if co else None

    def m_net_conf(self, t, group):
        return sum(pf - pa for o, pf, pa, _, _ in self.g[t] if self.conf(o) == self.conf(t))

    def m_net_all(self, t, group):
        return sum(pf - pa for _, pf, pa, _, _ in self.g[t])

    def m_net_td(self, t, group):
        return sum(tf - ta for _, _, _, tf, ta in self.g[t])


# ---- steps ------------------------------------------------------------------------------
# A step returns the set of clubs that stay in contention (best value), or None when it does not apply or
# does not separate anyone.
def _best(L: Ledger, fn: Callable, group: List[int], invert: bool = False) -> Optional[List[int]]:
    vals = {t: fn(t, group) for t in group}
    if any(v is None for v in vals.values()):
        return None
    if len(set(vals.values())) == 1:
        return None
    target = min(vals.values()) if invert else max(vals.values())
    return [t for t in group if vals[t] == target]


def _sweep(L: Ledger, group: List[int], invert: bool) -> Optional[List[int]]:
    """Head-to-head sweep (three or more clubs): a club that beat all the others advances; a club that lost
    to all the others is eliminated. Applies only if every pair has met."""
    won_all, lost_all = [], []
    for t in group:
        others = [o for o in group if o != t]
        rec = [L.games_vs(t, [o]) for o in others]
        if any(not r for r in rec):
            return None
        if all(all(x[1] > x[2] for x in r) for r in rec):
            won_all.append(t)
        if all(all(x[1] < x[2] for x in r) for r in rec):
            lost_all.append(t)
    if won_all and not invert:
        return won_all
    if lost_all and invert:
        return lost_all
    if lost_all and not invert:
        rest = [t for t in group if t not in lost_all]
        return rest if len(rest) < len(group) else None
    if won_all and invert:
        rest = [t for t in group if t not in won_all]
        return rest if len(rest) < len(group) else None
    return None


def _chain(kind: str, n: int):
    """Ordered steps: (name, function). The coin toss is added by the caller."""
    h2h = ("head_to_head", lambda L, t, g: L.m_h2h(t, g))
    div = ("division_record", lambda L, t, g: L.m_div(t, g))
    conf = ("conference_record", lambda L, t, g: L.m_conf(t, g))
    common0 = ("common_games", lambda L, t, g: L.m_common(t, g, 0))
    common4 = ("common_games_min4", lambda L, t, g: L.m_common(t, g, 4))
    sov = ("strength_of_victory", lambda L, t, g: L.m_sov(t, g))
    sos = ("strength_of_schedule", lambda L, t, g: L.m_sos(t, g))
    rkc = ("combined_rank_conference", lambda L, t, g: L.m_rank_conf(t, g))
    rka = ("combined_rank_all", lambda L, t, g: L.m_rank_all(t, g))
    ncom = ("net_points_common", lambda L, t, g: L.m_net_common(t, g))
    ncon = ("net_points_conference", lambda L, t, g: L.m_net_conf(t, g))
    nall = ("net_points_all", lambda L, t, g: L.m_net_all(t, g))
    ntd = ("net_touchdowns", lambda L, t, g: L.m_net_td(t, g))
    if kind == "division":
        return [h2h, div, common0, conf, sov, sos, rkc, rka, ncom, nall, ntd]
    if kind == "conference":
        first = [h2h] if n == 2 else [("head_to_head_sweep", None)]
        return first + [conf, common4, sov, sos, rkc, rka, ncon, nall, ntd]
    if kind == "draft_inter":
        return [h2h, common4, sov, rka, nall, ntd]
    if kind == "ambassador":
        return [h2h, sov, sos, nall, ntd]
    raise ValueError(kind)


def _pick(L: Ledger, group: List[int], kind: str, rng: random.Random, log, context: str, invert: bool = False) -> int:
    """Pick the single club that comes first (best, or with invert=True the worst / earliest draft pick)."""
    cands = list(group)
    if len(cands) == 1:
        return cands[0]
    chain = _chain(kind, len(cands))
    i = 0
    while i < len(chain):
        name, fn = chain[i]
        if name == "head_to_head_sweep":
            keep = _sweep(L, cands, invert) if len(cands) > 2 else None
        else:
            keep = _best(L, lambda t, g, fn=fn: fn(L, t, g), cands, invert)
        i += 1
        if keep is None:
            continue
        if log is not None:
            log.append({"context": context, "size": len(cands), "decided_by": name, "teams": cands[:]})
        if len(keep) == 1:
            return keep[0]
        was = len(cands)
        cands = keep
        if len(cands) == 2 and was > 2:
            chain, i = _chain(kind, 2), 0                  # NFL restart rule
        elif len(cands) == 3 and was > 3 and kind == "division":
            chain, i = _chain(kind, 3), 0                  # NFL: three remain after a fourth is eliminated, start the three-club list again
    if log is not None:
        log.append({"context": context, "size": len(cands), "decided_by": "seeded_coin_flip", "teams": cands[:]})
    return rng.choice(cands)


def _order(L: Ledger, group: List[int], kind: str, rng, log, context, invert=False, reduce_by_division=False):
    """Rank a whole tied group by picking the best (or worst) again and again."""
    rest = list(group)
    out = []
    while rest:
        pool = rest
        if reduce_by_division:
            by_div = defaultdict(list)
            for t in rest:
                by_div[L.div(t)].append(t)
            # NFL: clubs from the same division are first separated by the division procedure,
            # and only the best of each division goes into the wild-card comparison
            pool = [v[0] if len(v) == 1 else _pick(L, v, "division", rng, log, context + ":division")
                    for v in by_div.values()]
        pick = _pick(L, pool, kind, rng, log, context, invert)
        out.append(pick)
        rest.remove(pick)
    return out


# ---- public entry points -----------------------------------------------------------------
def _pct_groups(L: Ledger, ids: List[int]) -> Dict[Fraction, List[int]]:
    g = defaultdict(list)
    for t in ids:
        g[L.pct(L.wins[t], L.n[t])].append(t)
    return g


def rank_division(L: Ledger, ids: List[int], rng, log=None, context="division") -> List[int]:
    out = []
    groups = _pct_groups(L, ids)
    for p in sorted(groups, reverse=True):
        out += _order(L, groups[p], "division", rng, log, context)
    return out


def rank_conference(L: Ledger, ids: List[int], rng, log=None, context="conference") -> List[int]:
    """Division winners among themselves, or wild-card candidates from several divisions."""
    out = []
    groups = _pct_groups(L, ids)
    for p in sorted(groups, reverse=True):
        out += _order(L, groups[p], "conference", rng, log, context, reduce_by_division=True)
    return out


def _draft_kind(L: Ledger, group: List[int]) -> str:
    if len({L.div(t) for t in group}) == 1:
        return "division"
    if len({L.conf(t) for t in group}) == 1:
        return "conference"
    return "draft_inter"


def draft_order(L: Ledger, ids: List[int], rng, log=None, context="draft") -> List[int]:
    """Worst record first. Ties: the lower strength of schedule picks first, then the division / conference /
    inter-conference procedure with the worse club picking first, then a coin toss."""
    out = []
    groups = _pct_groups(L, ids)
    for p in sorted(groups):                                    # lowest win percentage first
        rest = list(groups[p])
        while rest:
            if len(rest) == 1:
                out.append(rest.pop())
                continue
            sos = {t: L.m_sos(t, rest) for t in rest}
            low = min(sos.values())
            first = [t for t in rest if sos[t] == low]
            if len(first) < len(rest):
                if log is not None:
                    log.append({"context": context, "size": len(rest), "decided_by": "strength_of_schedule", "teams": rest[:]})
                rest_sorted = first
            else:
                rest_sorted = rest
            if len(rest_sorted) == 1:
                pick = rest_sorted[0]
            else:
                kind = _draft_kind(L, rest_sorted)
                pick = _pick(L, rest_sorted, kind, rng, log, context, invert=True)
            out.append(pick)
            rest.remove(pick)
    return out


def rank_ambassador(L: Ledger, ids: List[int], rng, log=None, context="ambassador") -> List[int]:
    out = []
    groups = _pct_groups(L, ids)
    for p in sorted(groups, reverse=True):
        out += _order(L, groups[p], "ambassador", rng, log, context)
    return out
