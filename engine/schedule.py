"""Schedule generator.

The 18-game schedule is built from tier "slots" (conference, division, tier), because
every division always holds exactly one team of each tier 1-5. The slot template is
random but always satisfies the rules; it is then mapped onto the real teams.

Weeks 1-4    non-conference: tier t plays tier t from the other conference.
Weeks 5-14   conference: 4 division games + 6 tier-based games, one game every week.
Weeks 15-19  division: the other 4 division games; each team has one bye.
"""
from __future__ import annotations

import itertools
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import rules as R

Slot = Tuple[int, int, int]   # (conference, division, tier)


@dataclass
class Game:
    week: int
    home: int                     # team id
    away: int                     # team id
    kind: str                     # nonconf | division | tier | ambassador | ambassador_bowl | playoff_*
    home_pts: Optional[int] = None
    away_pts: Optional[int] = None
    result: object = None             # box score (GameResult) when the drive engine kept it
    home_tds: Optional[int] = None    # touchdowns scored (drive engine); None = estimate as points // 7
    away_tds: Optional[int] = None

    @property
    def winner(self) -> int:
        return self.home if self.home_pts > self.away_pts else self.away

    @property
    def loser(self) -> int:
        return self.away if self.home_pts > self.away_pts else self.home


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def tiers_may_meet(t1: int, t2: int) -> bool:
    return t2 in R.TIER_OPPONENTS[t1]


def _matchable_tuples() -> List[Tuple[int, ...]]:
    """4-tuples of tiers (one free team per division) that can be split into two
    tier-based games using only allowed tier pairings."""
    ok = []
    for tup in itertools.product(R.TIERS, repeat=R.DIVISIONS_PER_CONFERENCE):
        if _pairings(tup):
            ok.append(tup)
    return ok


def _pairings(tup: Tuple[int, ...]) -> List[List[Tuple[int, int]]]:
    """All ways to split indices 0..3 into two allowed pairs."""
    res = []
    for pairs in ([(0, 1), (2, 3)], [(0, 2), (1, 3)], [(0, 3), (1, 2)]):
        if all(tiers_may_meet(tup[a], tup[b]) for a, b in pairs):
            res.append(pairs)
    return res


_MATCHABLE = None


def matchable_tuples():
    global _MATCHABLE
    if _MATCHABLE is None:
        _MATCHABLE = _matchable_tuples()
    return _MATCHABLE


def euler_orient(edges: List[Tuple], rng: random.Random) -> Dict[int, Tuple]:
    """Orient every edge so each vertex has as many outgoing (home) as incoming (away)
    edges. Needs every vertex to have even degree. Returns edge index -> (home, away)."""
    adj = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        adj[u].append(i)
        adj[v].append(i)
    for v, lst in adj.items():
        if len(lst) % 2:
            raise ValueError(f"vertex {v} has odd degree {len(lst)}")
    used = [False] * len(edges)
    out: Dict[int, Tuple] = {}
    verts = list(adj)
    rng.shuffle(verts)
    ptr = {v: 0 for v in verts}

    def next_edge(v):
        lst = adj[v]
        while ptr[v] < len(lst) and used[lst[ptr[v]]]:
            ptr[v] += 1
        return lst[ptr[v]] if ptr[v] < len(lst) else None

    for start in verts:
        while next_edge(start) is not None:
            cur = start
            while True:
                e = next_edge(cur)
                if e is None:
                    break
                used[e] = True
                u, v = edges[e]
                nxt = v if cur == u else u
                out[e] = (cur, nxt)
                cur = nxt
    return out


def edge_color(edges: List[Tuple], ncolors: int, rng: random.Random, node_limit: int = 30000) -> Optional[List[int]]:
    """Give every edge a colour so that no two edges at a vertex share one."""
    n = len(edges)
    color = [-1] * n
    at = defaultdict(set)          # vertex -> colours used there
    nodes = [0]

    def avail(i):
        u, v = edges[i]
        return [c for c in range(ncolors) if c not in at[u] and c not in at[v]]

    def solve(remaining):
        if not remaining:
            return True
        nodes[0] += 1
        if nodes[0] > node_limit:
            return False
        best, best_av = None, None
        for i in remaining:
            av = avail(i)
            if not av:
                return False
            if best is None or len(av) < len(best_av):
                best, best_av = i, av
                if len(av) == 1:
                    break
        rng.shuffle(best_av)
        u, v = edges[best]
        rest = [i for i in remaining if i != best]
        for c in best_av:
            color[best] = c
            at[u].add(c)
            at[v].add(c)
            if solve(rest):
                return True
            at[u].discard(c)
            at[v].discard(c)
            color[best] = -1
            if nodes[0] > node_limit:
                return False
        return False

    return color if solve(list(range(n))) else None


def rr5_rounds(order: List[Slot]) -> List[Tuple[Slot, List[Tuple[Slot, Slot]]]]:
    """Round-robin of five teams: five rounds, in round r the team order[r] has the bye
    and the other four play two games. Together the rounds cover all 10 pairs once."""
    rounds = []
    for r in range(5):
        pairs = [(order[(r + 1) % 5], order[(r + 4) % 5]), (order[(r + 2) % 5], order[(r + 3) % 5])]
        rounds.append((order[r], pairs))
    return rounds


# ---------------------------------------------------------------------------
# the slot template
# ---------------------------------------------------------------------------
def _free_team_plan(rng: random.Random) -> Optional[List[Tuple[int, ...]]]:
    """For the five division-game weeks of the conference block: which tier is the free
    (non-division-playing) team in each division. Returns five 4-tuples, one per week,
    such that every division frees each tier exactly once and each week's four free teams
    can be paired into two legal tier-based games."""
    cands = list(matchable_tuples())
    D = R.DIVISIONS_PER_CONFERENCE
    used = [set() for _ in range(D)]
    plan: List[Tuple[int, ...]] = []

    def dfs(week):
        if week == 5:
            return True
        order = cands[:]
        rng.shuffle(order)
        for tup in order:
            if any(tup[d] in used[d] for d in range(D)):
                continue
            for d in range(D):
                used[d].add(tup[d])
            plan.append(tup)
            if dfs(week + 1):
                return True
            plan.pop()
            for d in range(D):
                used[d].discard(tup[d])
        return False

    return plan if dfs(0) else None


def _conference_template(c: int, rng: random.Random):
    """Returns (division_games_block1, tier_games_by_week, division_games_block2) for one
    conference, as lists of (week, slotA, slotB). Orientation is decided later."""
    D = R.DIVISIONS_PER_CONFERENCE
    block1_weeks = list(R.CONFERENCE_BLOCK_DIVISION_WEEKS)
    all_block_weeks = list(range(R.WEEKS_CONFERENCE[0], R.WEEKS_CONFERENCE[1] + 1))
    tier_weeks = [w for w in all_block_weeks if w not in block1_weeks]

    while True:
        plan = _free_team_plan(rng)
        # -- division games, first block, and the tier games the free teams play
        div1: List[Tuple[int, Slot, Slot]] = []
        tier_games: List[Tuple[Optional[int], Slot, Slot]] = []   # week None = not yet placed
        order_by_div = []
        for d in range(D):
            # position w holds the tier that is free in round w
            order_by_div.append([(c, d, plan[w][d]) for w in range(5)])
        for w in range(5):
            week = block1_weeks[w]
            for d in range(D):
                _, pairs = rr5_rounds(order_by_div[d])[w]
                for a, b in pairs:
                    div1.append((week, a, b))
            tup = plan[w]
            pairing = rng.choice(_pairings(tup))
            for ia, ib in pairing:
                tier_games.append((week, (c, ia, tup[ia]), (c, ib, tup[ib])))

        # -- the remaining tier games, five perfect matchings for the five tier weeks
        used_pairs = {frozenset((a, b)) for _, a, b in tier_games}
        rest = []
        slots = [(c, d, t) for d in range(D) for t in R.TIERS]
        for a, b in itertools.combinations(slots, 2):
            if a[1] == b[1]:
                continue
            if not tiers_may_meet(a[2], b[2]):
                continue
            if frozenset((a, b)) in used_pairs:
                continue
            rest.append((a, b))
        colors = edge_color(rest, len(tier_weeks), rng)
        if colors is None:
            continue
        perm = tier_weeks[:]
        rng.shuffle(perm)
        for (a, b), col in zip(rest, colors):
            tier_games.append((perm[col], a, b))
        break

    # -- division games, second block: a fresh round-robin in weeks 15-19
    div2: List[Tuple[int, Slot, Slot]] = []
    for d in range(D):
        order = [(c, d, t) for t in R.TIERS]
        rng.shuffle(order)
        for r, (_, pairs) in enumerate(rr5_rounds(order)):
            for a, b in pairs:
                div2.append((R.WEEKS_DIVISIONAL[0] + r, a, b))
    return div1, tier_games, div2


def generate_template(rng: random.Random) -> List[Tuple[int, Slot, Slot, str]]:
    """A full season of slot-level games: (week, home_slot, away_slot, kind)."""
    D = R.DIVISIONS_PER_CONFERENCE
    assert R.NON_CONFERENCE_GAMES == D, "non-conference scheme assumes one game per other-conference division"
    games: List[Tuple[int, Slot, Slot, str]] = []

    # weeks 1-4: tier t of conference 0 vs tier t of conference 1
    nc_edges, nc_weeks = [], []
    for k in range(R.NON_CONFERENCE_GAMES):
        for t in R.TIERS:
            for i in range(D):
                nc_edges.append(((0, i, t), (1, (i + k) % D, t)))
                nc_weeks.append(R.WEEKS_NON_CONFERENCE[0] + k)
    for idx, (h, a) in euler_orient(nc_edges, rng).items():
        games.append((nc_weeks[idx], h, a, "nonconf"))

    for c in range(len(R.CONFERENCES)):
        div1, tier_games, div2 = _conference_template(c, rng)
        # tier games: balance home/away across the whole conference
        t_edges = [(a, b) for _, a, b in tier_games]
        for idx, (h, a) in euler_orient(t_edges, rng).items():
            games.append((tier_games[idx][0], h, a, "tier"))
        # division games: each pair meets twice, once at each ground
        first_home = {}
        for week, a, b in div1:
            h, aw = (a, b) if rng.random() < 0.5 else (b, a)
            first_home[frozenset((a, b))] = h
            games.append((week, h, aw, "division"))
        for week, a, b in div2:
            h1 = first_home[frozenset((a, b))]
            h, aw = (b, a) if h1 == a else (a, b)
            games.append((week, h, aw, "division"))
    return games


def build_schedule(league, rng: random.Random) -> List[Game]:
    """The 18-game regular-season schedule for the 40 active teams."""
    slot_team = league.slot_map()
    games = []
    for week, hs, aws, kind in generate_template(rng):
        games.append(Game(week, slot_team[hs].id, slot_team[aws].id, kind))
    games.sort(key=lambda g: (g.week, g.home))
    return games


def build_ambassador_schedule(exiled_ids: List[int], rng: random.Random) -> List[Game]:
    """7-game round-robin among the 8 exiled teams (circle method), weeks 1-7."""
    ids = exiled_ids[:]
    rng.shuffle(ids)
    n = len(ids)
    assert n == R.AMBASSADOR_ROUND_ROBIN_TEAMS
    games = []
    arr = ids[:]
    for r in range(n - 1):
        for i in range(n // 2):
            a, b = arr[i], arr[n - 1 - i]
            home, away = (a, b) if (r + i) % 2 == 0 else (b, a)
            games.append(Game(R.AMBASSADOR_WEEKS[0] + r, home, away, "ambassador"))
        arr = [arr[0]] + [arr[-1]] + arr[1:-1]
    return games


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------
def check_schedule(league, games: List[Game]) -> List[str]:
    """Return a list of rule violations (empty list = the schedule is legal)."""
    errs: List[str] = []
    active = {t.id: t for t in league.active()}
    played = defaultdict(list)                     # team id -> [(week, opp, home?, kind)]
    for g in games:
        if g.home not in active or g.away not in active:
            errs.append(f"week {g.week}: game involves a non-active team")
            continue
        played[g.home].append((g.week, g.away, True, g.kind))
        played[g.away].append((g.week, g.home, False, g.kind))

    for tid, t in active.items():
        gl = played[tid]
        if len(gl) != R.GAMES_PER_TEAM:
            errs.append(f"{t.name}: {len(gl)} games, expected {R.GAMES_PER_TEAM}")
        weeks = [w for w, *_ in gl]
        if len(set(weeks)) != len(weeks):
            errs.append(f"{t.name}: plays twice in one week")
        if any(w < 1 or w > R.REGULAR_SEASON_WEEKS for w in weeks):
            errs.append(f"{t.name}: game outside weeks 1-{R.REGULAR_SEASON_WEEKS}")
        bye_weeks = [w for w in range(1, R.REGULAR_SEASON_WEEKS + 1) if w not in weeks]
        if len(bye_weeks) != 1 or not (R.WEEKS_DIVISIONAL[0] <= bye_weeks[0] <= R.WEEKS_DIVISIONAL[1]):
            errs.append(f"{t.name}: bye weeks {bye_weeks}, expected exactly one in weeks "
                        f"{R.WEEKS_DIVISIONAL[0]}-{R.WEEKS_DIVISIONAL[1]}")
        homes = sum(1 for g in gl if g[2])
        if homes * 2 != R.GAMES_PER_TEAM:
            errs.append(f"{t.name}: {homes} home games of {len(gl)}")
        by_kind = defaultdict(list)
        for w, opp, h, kind in gl:
            by_kind[kind].append((w, opp, h))
        o = active
        # non-conference
        nc = by_kind["nonconf"]
        if len(nc) != R.NON_CONFERENCE_GAMES or not all(
                R.WEEKS_NON_CONFERENCE[0] <= w <= R.WEEKS_NON_CONFERENCE[1] for w, _, _ in nc):
            errs.append(f"{t.name}: non-conference games wrong ({len(nc)})")
        if len({opp for _, opp, _ in nc}) != len(nc):
            errs.append(f"{t.name}: repeats a non-conference opponent")
        for _, opp, _ in nc:
            if o[opp].conf == t.conf or o[opp].tier != t.tier:
                errs.append(f"{t.name}: non-conference opponent {o[opp].name} is wrong")
        # division
        dv = by_kind["division"]
        rivals = [x for x in league.active_in_division(t.division_id) if x.id != tid]
        if len(dv) != R.DIVISION_GAMES_FIRST_BLOCK + R.DIVISION_GAMES_SECOND_BLOCK:
            errs.append(f"{t.name}: {len(dv)} division games")
        for r in rivals:
            meets = [(w, h) for w, opp, h in dv if opp == r.id]
            if len(meets) != 2:
                errs.append(f"{t.name} meets {r.name} {len(meets)} times, expected 2")
                continue
            (w1, h1), (w2, h2) = sorted(meets)
            if not (R.WEEKS_CONFERENCE[0] <= w1 <= R.WEEKS_CONFERENCE[1]
                    and R.WEEKS_DIVISIONAL[0] <= w2 <= R.WEEKS_DIVISIONAL[1]):
                errs.append(f"{t.name} v {r.name}: meetings in wrong blocks (weeks {w1}, {w2})")
            if h1 == h2:
                errs.append(f"{t.name} v {r.name}: same ground both times")
        if sum(1 for w, _, _ in dv if R.WEEKS_CONFERENCE[0] <= w <= R.WEEKS_CONFERENCE[1]) != R.DIVISION_GAMES_FIRST_BLOCK:
            errs.append(f"{t.name}: wrong number of division games in weeks 5-14")
        # tier-based
        tg = by_kind["tier"]
        if len(tg) != R.TIER_BASED_GAMES:
            errs.append(f"{t.name}: {len(tg)} tier-based games")
        if not all(R.WEEKS_CONFERENCE[0] <= w <= R.WEEKS_CONFERENCE[1] for w, _, _ in tg):
            errs.append(f"{t.name}: tier-based game outside weeks 5-14")
        want = {x.id for x in active.values()
                if x.conf == t.conf and x.division_id != t.division_id and x.tier in R.TIER_OPPONENTS[t.tier]}
        got = [opp for _, opp, _ in tg]
        if set(got) != want or len(got) != len(set(got)):
            errs.append(f"{t.name}: tier-based opponents wrong")
        # every conference week 5-14 has a game
        wk = {w for w, *_ in gl}
        for w in range(R.WEEKS_CONFERENCE[0], R.WEEKS_CONFERENCE[1] + 1):
            if w not in wk:
                errs.append(f"{t.name}: idle in conference week {w}")
    return errs
