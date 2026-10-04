"""Phase 1 checks: the league engine obeys the rules over many seeds and seasons.

    python engine/check_phase1.py            (quick: ~60 seasons x several leagues)
    python engine/check_phase1.py --long     (heavier: many more)
"""
import copy
import os
import random
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R  # noqa: E402
import schedule as S  # noqa: E402
from draft import EXIT_ORDER, run_lottery  # noqa: E402
from league import new_league  # noqa: E402
from run_sim import simulate  # noqa: E402
from season import Options  # noqa: E402
from standings import Stats, rank_teams  # noqa: E402

LONG = "--long" in sys.argv
failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---------------------------------------------------------------------------
# 1. Schedule checker catches broken schedules (so a pass means something)
# ---------------------------------------------------------------------------
rng = random.Random(7)
lg = new_league(rng)
good = S.build_schedule(lg, rng)
check("good schedule passes the schedule checker", S.check_schedule(lg, good) == [])

def broken(mut):
    g = copy.deepcopy(good)
    mut(g)
    return S.check_schedule(lg, g)

check("checker catches a missing game", len(broken(lambda g: g.pop(5))) > 0)
def double_book(g):
    x = g[0]
    y = next(i for i in g[1:] if (x.home in (i.home, i.away) or x.away in (i.home, i.away)) and i.week != x.week)
    y.week = x.week
check("checker catches a team playing twice in a week", len(broken(double_book)) > 0)
def swap_opponent(g):
    k = next(i for i, x in enumerate(g) if x.kind == "tier")
    other = next(i for i, x in enumerate(g) if x.kind == "tier" and i != k)
    g[k].away, g[other].away = g[other].away, g[k].away
check("checker catches wrong tier-based opponents", len(broken(swap_opponent)) > 0)
def flip_home(g):
    k = next(i for i, x in enumerate(g) if x.kind == "nonconf")
    g[k].home, g[k].away = g[k].away, g[k].home
check("checker catches broken home/away balance", len(broken(flip_home)) > 0)
def move_bye(g):
    k = next(i for i, x in enumerate(g) if x.kind == "division" and x.week >= 15)
    g[k].week = 3
check("checker catches a division game in the wrong block", len(broken(move_bye)) > 0)

# ---------------------------------------------------------------------------
# 2. Tiebreakers
# ---------------------------------------------------------------------------
def mk(wins, losses, pf=0, pa=0, h2h=None, div=(0, 0)):
    s = Stats()
    s.wins, s.losses, s.pf, s.pa = wins, losses, pf, pa
    s.div_w, s.div_l = div
    for opp, (w, l) in (h2h or {}).items():
        s.h2h[opp] = [w, l]
    return s

r = random.Random(1)
# two teams tied 9-9; team 2 beat team 1 twice
st = {1: mk(9, 9, h2h={2: (0, 2)}), 2: mk(9, 9, h2h={1: (2, 0)})}
log = []
check("two-way tie: head-to-head decides first", rank_teams([1, 2], st, R.TIEBREAKERS, r, log) == [2, 1]
      and log[0]["decided_by"] == "head_to_head")
# head-to-head level -> division record
st = {1: mk(9, 9, h2h={2: (1, 1)}, div=(5, 3)), 2: mk(9, 9, h2h={1: (1, 1)}, div=(4, 4))}
log = []
check("two-way tie: division record is next", rank_teams([2, 1], st, R.TIEBREAKERS, r, log) == [1, 2]
      and log[0]["decided_by"] == "division_record")
# everything level except points
st = {1: mk(9, 9, pf=400, pa=380, h2h={2: (1, 1)}, div=(4, 4)), 2: mk(9, 9, pf=390, pa=380, h2h={1: (1, 1)}, div=(4, 4))}
log = []
check("two-way tie: point differential is next", rank_teams([1, 2], st, R.TIEBREAKERS, r, log) == [1, 2]
      and log[0]["decided_by"] == "point_differential")
# dead level -> coin flip, repeatable from the seed
st = {1: mk(9, 9, h2h={2: (1, 1)}, div=(4, 4)), 2: mk(9, 9, h2h={1: (1, 1)}, div=(4, 4))}
a = rank_teams([1, 2], st, R.TIEBREAKERS, random.Random(5), [])
b = rank_teams([1, 2], st, R.TIEBREAKERS, random.Random(5), [])
check("coin flip is repeatable from the seed", a == b)
seen = {tuple(rank_teams([1, 2], st, R.TIEBREAKERS, random.Random(i), [])) for i in range(40)}
check("coin flip can go either way", len(seen) == 2)
# three-way tie: head-to-head separates team 3 out, then 1 v 2 start again
st = {1: mk(9, 9, h2h={2: (1, 1), 3: (0, 2)}, div=(5, 3)),
      2: mk(9, 9, h2h={1: (1, 1), 3: (0, 2)}, div=(4, 4)),
      3: mk(9, 9, h2h={1: (2, 0), 2: (2, 0)}, div=(1, 7))}
out = rank_teams([1, 2, 3], st, R.TIEBREAKERS, r, [])
check("three-way tie: one team separated, the other two start again", out == [3, 1, 2], str(out))
# better record always beats a tiebreaker
st = {1: mk(10, 8), 2: mk(9, 9, h2h={1: (2, 0)}, div=(6, 2))}
check("record outranks tiebreakers", rank_teams([2, 1], st, R.TIEBREAKERS, r, []) == [1, 2])

# ---------------------------------------------------------------------------
# 3. Lottery
# ---------------------------------------------------------------------------
N = 40000 if LONG else 20000
firsts = Counter()
lot_rng = random.Random(11)
valid = True
for _ in range(N):
    picks = run_lottery(list(range(8)), R.LOTTERY_WEIGHTS, lot_rng)
    valid &= sorted(picks) == list(range(8))
    firsts[picks[0]] += 1
check("lottery always returns each of the 8 teams exactly once", valid)
tot_balls = sum(R.LOTTERY_WEIGHTS)
maxdev = max(abs(firsts[i] / N * 100 - 100 * R.LOTTERY_WEIGHTS[i] / tot_balls) for i in range(8))
check("pick 1 chances match the ball counts", maxdev < 1.0, f"largest gap {maxdev:.2f} percentage points over {N} draws")
check("worst team wins pick 1 most often", firsts[0] == max(firsts.values()))
# picks 5-8 follow the record, and no team falls more than four places from where its record puts it
fall_ok = order_ok = True
worst_pick = 0
for _ in range(4000):
    p = run_lottery(list(range(8)), R.LOTTERY_WEIGHTS, lot_rng)
    tail = p[R.LOTTERY_DRAWN_PICKS:]
    order_ok &= tail == sorted(tail)
    worst_pick = max(worst_pick, p.index(0) + 1)
check("picks 5-8 go to the remaining teams worst record first", order_ok)
check("the worst team can fall no lower than 5th", worst_pick == R.LOTTERY_DRAWN_PICKS + 1, f"lowest seen: pick {worst_pick}")

# ---------------------------------------------------------------------------
# 4. Whole seasons, many leagues
# ---------------------------------------------------------------------------
LEAGUES = 12 if LONG else 6
SEASONS = 40 if LONG else 12
configs = [("lottery for teams that just finished 5th", Options()),
           ("lottery for teams that just served exile", Options(lottery_pool="just_finished_exile"))]
all_ok = defaultdict(lambda: True)
msgs = {}

def flag(name, ok, detail=""):
    if not ok and all_ok[name]:
        msgs[name] = detail
    all_ok[name] &= ok

tiebreak_counts = Counter()
n_seasons = 0
exile_counts_per_div_year = Counter()
for cfg_name, opt in configs:
    for seed in range(LEAGUES):
        league, results = simulate(seed, SEASONS, opt)
        recall_seen = Counter()
        for res in results:
            n_seasons += 1
            tag = f"{cfg_name} / seed {seed} / year {res.year}"
            # league shape at kickoff
            start = res.start
            active = [t for t, (s, tier, _) in start.items() if s == "active"]
            exiled = [t for t, (s, tier, _) in start.items() if s == "exiled"]
            flag("40 active and 8 exiled teams at every kickoff", len(active) == 40 and len(exiled) == 8, tag)
            ok = True
            for d in range(R.TOTAL_DIVISIONS):
                mem = [t for t in range(1, 49) if (t - 1) // 6 == d]
                act = [t for t in mem if start[t][0] == "active"]
                ok &= len(act) == 5 and sorted(start[t][1] for t in act) == [1, 2, 3, 4, 5]
                ok &= sum(1 for t in mem if start[t][0] == "exiled") == 1
            flag("every division has tiers 1-5 once each plus one exiled team", ok, tag)
            # regular season
            flag("every active team plays 18 games",
                 all(s.games == 18 for s in res.stats.values()), tag)
            tw = sum(s.wins for s in res.stats.values())
            tl = sum(s.losses for s in res.stats.values())
            flag("league wins = league losses = 360", tw == tl == 360, f"{tag}: {tw}/{tl}")
            flag("no tied games", all(g.home_pts != g.away_pts for g in res.games + res.playoff_games), tag)
            # exile
            flag("8 teams exiled, exactly one 5th-place team per division",
                 len(res.new_exiles) == 8 and len(set(res.new_exiles)) == 8 and
                 all(res.division_ranks[d][4] in res.new_exiles for d in range(8)), tag)
            flag("each division ranks exactly its 5 active teams",
                 all(len(r) == 5 and len(set(r)) == 5 for r in res.division_ranks.values()), tag)
            # Ambassador
            pairs = Counter(frozenset((g.home, g.away)) for g in res.ambassador_games)
            flag("Ambassador: 28 games, every pair once", len(res.ambassador_games) == 28 and set(pairs.values()) == {1}
                 and len(pairs) == 28, tag)
            flag("Ambassador: 7 games per team", all(s.games == 7 for s in res.ambassador_stats.values()), tag)
            flag("Ambassador Bowl is between two exiled teams",
                 {res.ambassador_bowl.home, res.ambassador_bowl.away} <= set(exiled), tag)
            # playoffs
            for conf in (0, 1):
                seeds = res.seeds[conf]
                winners = [res.division_ranks[conf * 4 + d][0] for d in range(4)]
                flag("7 seeds per conference: 4 division winners then 3 wild cards",
                     len(seeds) == 7 and len(set(seeds)) == 7 and set(seeds[:4]) == set(winners), tag)
                flag("seeds belong to the right conference", all(start and (t - 1) // 24 == conf for t in seeds), tag)
            flag("no exiled team makes the playoffs", not (set(res.exits) & set(res.new_exiles)), tag)
            kinds = Counter(g.kind for g in res.playoff_games)
            flag("13 playoff games (6 wild card, 4 divisional, 2 championship, 1 final)",
                 kinds == Counter({"playoff_wc": 6, "playoff_div": 4, "playoff_conf": 2, "playoff_final": 1}), f"{tag}: {kinds}")
            flag("14 playoff teams, one champion", len(res.exits) == 14 and list(res.exits.values()).count("champion") == 1, tag)
            flag("seed 1 always gets a bye",
                 all(res.seeds[c][0] not in {g.home for g in res.playoff_games if g.kind == "playoff_wc"} |
                     {g.away for g in res.playoff_games if g.kind == "playoff_wc"} for c in (0, 1)), tag)
            # bracket matchups: 2v7, 3v6, 4v5, then highest remaining seed v lowest
            ok = True
            for conf in (0, 1):
                sd = res.seeds[conf]
                seed_no = {t: i + 1 for i, t in enumerate(sd)}
                wc = [g for g in res.playoff_games if g.kind == "playoff_wc" and g.home in seed_no and g.away in seed_no]
                ok &= {frozenset((g.home, g.away)) for g in wc} == {frozenset((sd[1], sd[6])), frozenset((sd[2], sd[5])),
                                                                     frozenset((sd[3], sd[4]))}
                ok &= all(seed_no[g.home] < seed_no[g.away] for g in wc)
                alive = sorted([sd[0]] + [g.winner for g in wc], key=lambda t: seed_no[t])
                dv = [g for g in res.playoff_games if g.kind == "playoff_div" and g.home in seed_no and g.away in seed_no]
                ok &= {frozenset((g.home, g.away)) for g in dv} == {frozenset((alive[0], alive[3])), frozenset((alive[1], alive[2]))}
                ok &= all(seed_no[g.home] < seed_no[g.away] for g in dv)
            flag("bracket matchups follow the seeds (2v7, 3v6, 4v5, then re-seeded)", ok, tag)
            # draft
            picks = [p for p, _, _ in res.draft]
            ids = [t for _, t, _ in res.draft]
            flag("draft has picks 1-48, each team once", picks == list(range(1, 49)) and sorted(ids) == list(range(1, 49)), tag)
            bands = {b: [t for p, t, bb in res.draft if bb == b] for b in R.DRAFT_PICKS}
            flag("lottery band is picks 1-8 and holds the lottery pool",
                 [p for p, _, b in res.draft if b == "exiled_lottery"] == list(range(1, 9))
                 and set(bands["exiled_lottery"]) == set(res.lottery_pool_order), tag)
            flag("picks 9-34 hold 26 teams", len(bands["active_non_playoff"]) == 26 and
                 [p for p, _, b in res.draft if b == "active_non_playoff"] == list(range(9, 35)), tag)
            flag("picks 35-48 are the playoff teams", set(bands["playoff_teams"]) == set(res.exits), tag)
            order = [EXIT_ORDER.index(res.exits[t]) for t in bands["playoff_teams"]]
            flag("playoff teams pick in order of how far they went", order == sorted(order), tag)
            expect_pool = set(res.new_exiles) if opt.lottery_pool == "just_finished_fifth" else set(res.returners)
            flag("lottery pool is the configured group", set(res.lottery_pool_order) == expect_pool, tag)
            # next year's tiers
            for d in range(8):
                ranks = res.division_ranks[d]
                for i, tid in enumerate(ranks[:4], start=1):
                    flag("tiers follow last division finish (1st = Tier 1 ... 4th = Tier 4)", res.next_tiers[tid] == i, tag)
            flag("returning exiled teams come back as Tier 5", all(res.next_tiers[t] == 5 for t in res.returners), tag)
            # recall
            recall_seen[res.recall_division] += 1
            flag("recall votes cover the rotating division and every exiled team",
                 {t for t in range(1, 49) if (t - 1) // 6 == res.recall_division} <= set(res.recall_votes)
                 and set(res.new_exiles) <= set(res.recall_votes), tag)
            for rec in res.tiebreak_log:
                if rec["context"] == "division":
                    tiebreak_counts[rec["decided_by"]] += 1
        # every division comes up once per 8 years
        first8 = Counter(res.recall_division for res in results[:8])
        flag("every division faces owner recall once in each 8-year cycle",
             set(first8) == set(range(8)) and set(first8.values()) == {1}, f"{cfg_name} / seed {seed}")

for name, ok in all_ok.items():
    check(name, ok, msgs.get(name, ""))
print(f"\n  ({n_seasons} full seasons simulated across {len(configs) * LEAGUES} leagues)")

# ---------------------------------------------------------------------------
# 5. Repeatability
# ---------------------------------------------------------------------------
_, r1 = simulate(42, 6)
_, r2 = simulate(42, 6)
check("same seed gives the identical league history",
      [(x.champion, x.new_exiles, [(g.week, g.home, g.away, g.home_pts, g.away_pts) for g in x.games]) for x in r1] ==
      [(x.champion, x.new_exiles, [(g.week, g.home, g.away, g.home_pts, g.away_pts) for g in x.games]) for x in r2])
_, r3 = simulate(43, 6)
check("a different seed gives a different history", [x.champion for x in r1] != [x.champion for x in r3] or
      [x.new_exiles for x in r1] != [x.new_exiles for x in r3])

print("\nHow often each division tiebreaker was needed:", dict(tiebreak_counts))
print()
if failures:
    print(f"{len(failures)} check(s) FAILED")
    sys.exit(1)
print("All Phase 1 checks passed.")
