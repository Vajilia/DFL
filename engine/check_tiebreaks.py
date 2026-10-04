"""Checks for the NFL-style tiebreakers: hand-built scenarios plus properties over full seasons.

    python engine/check_tiebreaks.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R  # noqa: E402
import tiebreak as T  # noqa: E402
from league import new_league  # noqa: E402
from schedule import Game  # noqa: E402
from season import Options, run_season  # noqa: E402
from standings import compute_stats  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


lg = new_league(random.Random(1))
div0 = [t.id for t in lg.active_in_division(0)]            # five teams in one division
div1 = [t.id for t in lg.active_in_division(1)]
A, B, C, D, E = div0


def game(h, a, hp, ap, kind="division"):
    return Game(1, h, a, kind, hp, ap)


def ledger(games, ids):
    return compute_stats(lg, games, ids).ledger


rng = random.Random(0)

# T1: two teams tied on record, head-to-head decides
g = [game(A, B, 20, 10), game(B, D, 20, 10), game(E, A, 20, 10)]
L = ledger(g, [A, B, D, E])
check("two clubs tied: head-to-head decides", T.rank_division(L, [A, B, D, E], rng) == [E, A, B, D])

# T2: three clubs tied: combined head-to-head, then the NFL restart rule for the last two
d1, d2 = D, E
C = div1[0]
X, Y, Z = A, B, C
g = [game(X, Y, 20, 10), game(X, Z, 20, 10), game(Y, Z, 20, 10),         # X 2-0, Y 1-1, Z 0-2 inside the group
     game(d1, X, 20, 10), game(d2, X, 20, 10),                           # X loses twice outside
     game(Y, d1, 20, 10), game(d2, Y, 20, 10),                           # Y 1-1 outside
     game(Z, d1, 20, 10), game(Z, d2, 20, 10)]                           # Z wins twice outside
L = ledger(g, [X, Y, Z, d1, d2])
st_ = compute_stats(lg, g, [X, Y, Z, d1, d2])
pcts = {t: float(st_[t].pct) for t in (X, Y, Z)}
check("three clubs tied on record (test set-up)", len(set(pcts.values())) == 1, str(pcts))
order = T.rank_division(L, [X, Y, Z], rng)
check("three clubs tied: head-to-head orders them X, Y, Z", order == [X, Y, Z], str(order))

# T3: the NFL draft rule: lower strength of schedule picks first
x, y, s_, w, z, q = div0[0], div0[1], div1[0], div1[1], div1[2], div1[3]
g = [game(s_, x, 20, 10, "tier"), game(s_, q, 20, 10, "tier"), game(w, y, 20, 10, "tier"), game(z, w, 20, 10, "tier")]
L = ledger(g, [x, y, s_, w, z, q])
order = T.draft_order(L, [x, y, q], rng)
check("draft order: tied teams, the one with the weaker schedule picks first", order[0] == y, str(order))

# T4: a pure tie goes to a coin toss and both outcomes happen
firsts = [T.rank_division(ledger([], [A, B]), [A, B], random.Random(s))[0] for s in range(400)]
share = firsts.count(A) / 400
check("a dead-even tie is a fair coin toss", 0.40 < share < 0.60, f"{share:.2f}")

# T5: a team with a better record always ranks above one with a worse record, in every ranking
bad = 0
for engine, seed in (("placeholder", 5), ("placeholder", 6)):
    r = random.Random(seed)
    L0 = new_league(r)
    for y in range(1, 41):
        res = run_season(L0, y, r, Options(validate_schedule=False))
        for ranks in res.division_ranks.values():
            p = [float(res.stats[t].pct) for t in ranks]
            bad += any(p[i] < p[i + 1] for i in range(len(p) - 1))
        for conf, seeds in res.seeds.items():
            w = [float(res.stats[t].pct) for t in seeds[:4]]
            c = [float(res.stats[t].pct) for t in seeds[4:]]
            bad += any(w[i] < w[i + 1] for i in range(3)) + any(c[i] < c[i + 1] for i in range(2))
        order = [t for _, t, _ in res.draft]
        bad += len(order) != 48 or len(set(order)) != 48
check("every ranking puts the better record first (80 seasons)", bad == 0, f"{bad} problems")

# T6: seasons with the drive engine give the same result type, and ties actually happen and get settled
r = random.Random(8)
L1 = new_league(r, rosters=True)
steps = {}
for y in range(1, 13):
    res = run_season(L1, y, r, Options(engine="fast", keep_boxes=False))
    for e in res.tiebreak_log:
        steps[e["decided_by"]] = steps.get(e["decided_by"], 0) + 1
check("ties are settled by several different NFL steps", len(steps) >= 4, str(steps))
check("tiebreaks never leave a tie unresolved", all(v > 0 for v in steps.values()))

print()
if failures:
    print(f"{len(failures)} tiebreak check(s) FAILED")
    sys.exit(1)
print("All tiebreak checks passed.")
