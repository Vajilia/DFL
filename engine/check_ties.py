"""Checks for the NFL overtime rule and ties: regular-season games may end level after one 10-minute overtime and count as half a win;
postseason games play 15-minute periods until someone wins; standings, tiebreakers and the seasons that use them handle a tie.

    python engine/check_ties.py
"""
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game_engine as GE  # noqa: E402
import rules as R  # noqa: E402
import standings as S  # noqa: E402
from league import new_league  # noqa: E402
from schedule import Game  # noqa: E402
from season import Options, run_season  # noqa: E402
from sim import GameRunner  # noqa: E402
import placeholder_model as PM  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---- the overtime rule, with scripted drives ------------------------------------------------------------------------------
class FakeGame:
    """Stands in for the drive engine: each scripted drive is (points for the team on offense, defensive points, seconds)."""
    def __init__(self, script):
        self.script = list(script)
        self.score = [0, 0]
        self.res = GE.GameResult()
        self.in_ot = False
        self.t = 0
        self.period_over = False
        self.next_off = 0
        self.next_start = 30
        self.drives_played = []

    def _kick_start(self):
        return 30

    def drive(self, off, start):
        pts, dpts, secs = self.script.pop(0)
        self.score[off] += pts
        self.score[1 - off] += dpts
        self.t -= secs
        if self.t <= 0:
            self.period_over = True
        self.next_off, self.next_start = 1 - off, 30
        self.drives_played.append(off)
        return {"result": "INT_TD" if dpts else "TD" if pts >= 6 else "FG" if pts else "PUNT", "secs": secs}


def run_ot(script, allow_tie, seed=1):
    g = FakeGame(script)
    GE._overtime(g, random.Random(seed), allow_tie)
    return g


g = run_ot([(7, 0, 200), (3, 0, 150), (0, 0, 100)], True)
check("regular season: a first-possession touchdown does not end it, the other team gets its possession",
      len(g.drives_played) == 2 and g.score[g.drives_played[0]] == 7 and g.score[g.drives_played[1]] == 3 and g.script == [(0, 0, 100)])
g = run_ot([(7, 0, 200), (7, 0, 150), (3, 0, 100), (0, 0, 100)], True)
check("level after both possessions: sudden death, the next score wins", len(g.drives_played) == 3 and g.score[g.drives_played[2]] == 3 + 7
      and g.script == [(0, 0, 100)])
g = run_ot([(3, 0, 100), (0, 0, 100), (0, 0, 100)], True)
check("a field goal then a stop ends it with the field goal ahead", len(g.drives_played) == 2 and g.script == [(0, 0, 100)])
g = run_ot([(0, 7, 100), (0, 0, 100)], True)
check("a defensive touchdown on the first possession ends it at once", len(g.drives_played) == 1 and g.script == [(0, 0, 100)])
g = run_ot([(0, 0, 200), (0, 0, 200), (0, 0, 150), (0, 0, 100)], True)
check("regular season: still level when the 10 minutes run out is a tie (one period, no kick-off decider)",
      g.score[0] == g.score[1] and g.res.ot_periods == 1 and not g.res.coin_flip_tiebreak and g.script == [])
g = run_ot([(0, 0, 400), (0, 0, 400), (0, 0, 200), (3, 0, 100), (0, 0, 100)], False)
check("postseason: a scoreless first period plays on into a second, 15 minutes each, until someone leads",
      g.res.ot_periods >= 2 and g.score[0] != g.score[1] and not g.res.coin_flip_tiebreak)
check("overtime lengths come from the rules", GE.OT_SECS == R.OVERTIME_MINUTES_REGULAR * 60 and GE.OT_SECS_POST == R.OVERTIME_MINUTES_POST * 60
      and (R.OVERTIME_MINUTES_REGULAR, R.OVERTIME_MINUTES_POST) == (10, 15))

# ---- the real drive engine ------------------------------------------------------------------------------------------------
rng = random.Random(21)
lg = new_league(rng, rosters=True)
runner = GameRunner(lg, rng, PM.Model(), engine="drives")
ids = [t.id for t in lg.teams]
reg_tied = reg_ot = post_tied = post_ot = 0
multi_period = 0
N = 2500
for _ in range(N):
    a, b = rng.sample(ids, 2)
    r = GE.simulate_game(runner.lineup(a), runner.lineup(b), rng, None, False, False, True)
    reg_ot += bool(r.ot_periods)
    reg_tied += r.score[0] == r.score[1]
    multi_period += r.ot_periods > 1
for _ in range(N):
    a, b = rng.sample(ids, 2)
    r = GE.simulate_game(runner.lineup(a), runner.lineup(b), rng, None, False, False, False)
    post_ot += bool(r.ot_periods)
    post_tied += r.score[0] == r.score[1]
check("drive engine, regular season: some games end level after overtime", reg_tied > 0, f"{reg_tied} of {N}")
check("drive engine, regular season: every overtime is a single period", multi_period == 0, f"{multi_period} longer")
check("drive engine, postseason: no game ends level", post_tied == 0, f"{post_ot} overtime games, {post_tied} level")
check("about 4% to 9% of games reach overtime (NFL: about 6%)", 0.04 <= reg_ot / N <= 0.09, f"{reg_ot / N:.3f}")

# ---- standings and tiebreakers with a tie ---------------------------------------------------------------------------------
lg2 = new_league(random.Random(3))
a, b, c, d = [t.id for t in lg2.teams if t.conf == lg2.teams[0].conf and t.div == lg2.teams[0].div][:4]
games = [Game(1, a, b, "division", 20, 20), Game(2, a, c, "division", 24, 17), Game(3, b, c, "division", 10, 17),
         Game(4, a, d, "nonconf", 3, 10)]
games[0].home_tds = games[0].away_tds = 2
st = S.compute_stats(lg2, games, [a, b, c, d])
check("a tie counts as half a win in the percentage", st[a].pct == Fraction(1, 2) and st[b].pct == Fraction(1, 4) and st[c].pct == Fraction(1, 2),
      f"{st[a].record} {st[a].pct}; {st[b].record} {st[b].pct}")
check("the record reads W-L-T when there is a tie, W-L when there is not", st[a].record == "1-1-1" and st[b].record == "0-1-1" and st[c].record == "1-1")
check("the tie is in the division and head-to-head records", st[a].div_t == 1 and st[a].h2h[b] == [0, 0, 1] and st[b].h2h[a] == [0, 0, 1])
check("games = wins + losses + ties", all(s.games == s.wins + s.losses + s.ties for s in st.values()))
check("a tied Game has no winner or loser and is not a playoff game", games[0].winner is None and games[0].loser is None and games[0].tied
      and games[0].counts_ties and not Game(20, a, b, "playoff_wc", 1, 0).counts_ties and not Game(8, a, b, "ambassador_bowl", 1, 0).counts_ties)
L = st.ledger
check("the tiebreak ledger credits a tie as half a win", L.wins[b] == Fraction(1, 2) + Fraction(0) and L.record_pct(L.g[a][:1]) == Fraction(1, 2))
order = S.rank_by_style("division", [a, b, c, d], st, random.Random(1), [], "t")
check("ranking a division with a tie in it still ranks every team once", sorted(order) == sorted([a, b, c, d]))

# ---- whole seasons --------------------------------------------------------------------------------------------------------
tot_ties = tot_games = bad = 0
for seed in range(1, 6):
    rg = random.Random(seed)
    lgx = new_league(rg, rosters=True)
    res = run_season(lgx, 1, rg, Options(engine="fast", keep_boxes=False))
    for tid, s in res.stats.items():
        if s.games != R.GAMES_PER_TEAM or s.wins + s.losses + s.ties != s.games:
            bad += 1
    tot_ties += sum(g.tied for g in res.games)
    tot_games += len(res.games)
    check(f"season {seed}: no playoff game ends level", all(not g.tied for g in res.playoff_games))
check("every team plays 18 games with wins + losses + ties = 18", bad == 0)
check("ties appear in seasons at about the NFL's rate (under 1.2%)", 0 < tot_ties / tot_games < 0.012, f"{tot_ties} in {tot_games}")

print()
if failures:
    print(f"{len(failures)} tie check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All tie checks passed.")
