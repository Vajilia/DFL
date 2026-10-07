"""Phase 2 checks: rosters, the drive engine, injuries and the roster offseason obey their invariants.

    python engine/check_phase2.py
"""
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R  # noqa: E402
from game_engine import simulate_game  # noqa: E402
from league import new_league  # noqa: E402
from lineup import build_lineup  # noqa: E402
from positions import ROSTER_COUNTS, ROSTER_SIZE, STARTERS  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---- rosters ----------------------------------------------------------------------------
rng = random.Random(3)
lg = new_league(rng, rosters=True)
check("every team has the right roster size", all(len(t.roster) == ROSTER_SIZE for t in lg.teams))
check("position counts are as configured",
      all(sum(1 for p in t.roster if p.pos == pos) == n for t in lg.teams for pos, n in ROSTER_COUNTS.items()))
ids = [p.id for t in lg.teams for p in t.roster]
check("player ids are unique", len(ids) == len(set(ids)))
check("ratings stay between 1 and 100",
      all(R.RATING_MIN <= v <= R.RATING_MAX for t in lg.teams for p in t.roster for v in p.ratings.values()))

# ---- one game ---------------------------------------------------------------------------
a, b = build_lineup(1, lg.by_id[1].roster), build_lineup(2, lg.by_id[2].roster)
bad_sum = bad_tie = bad_players = bad_clock = 0
N = 600
for i in range(N):
    r = simulate_game(a, b, random.Random(i))
    drive_pts = [0, 0]
    for d in r.drives:
        drive_pts[d["side"]] += d["pts"]
        drive_pts[1 - d["side"]] += d["def_pts"]
    if drive_pts != r.score and not r.coin_flip_tiebreak:
        bad_sum += 1
    if r.score[0] == r.score[1]:
        bad_tie += 1
    # player points-producing stats must agree with team passing/rushing yards
    for side in (0, 1):
        py = sum(d.get("pass_yds", 0) for d in r.players.values() if d["team"] == side)
        ry = sum(d.get("rush_yds", 0) for d in r.players.values() if d["team"] == side)
        if py != r.team[side]["pass_yds"] or ry != r.team[side]["rush_yds"]:
            bad_players += 1
    if sum(d["secs"] for d in r.drives) > 3600 + 60 * R.OVERTIME_MINUTES_POST * (r.ot_periods or 0) + 1:
        bad_clock += 1
check("drive points add up to the final score in every game", bad_sum == 0, f"{N} games")
check("no game ends in a tie", bad_tie == 0)
check("player yards add up to team yards", bad_players == 0)
check("drives never use more clock than the game has", bad_clock == 0)
same = [simulate_game(a, b, random.Random(7)).score for _ in range(2)]
check("same seed gives the same game", same[0] == same[1])
check("play-by-play is off by default and on when asked",
      simulate_game(a, b, random.Random(1)).plays is None and simulate_game(a, b, random.Random(1), record_plays=True).plays is not None)

# ---- a full season with the drive engine --------------------------------------------------
rng = random.Random(21)
lg = new_league(rng, rosters=True)
res = run_season(lg, 1, rng, Options(engine="drives"))
check("every regular-season game has a box score", all(g.result is not None for g in res.games))
check("every team played 18 regular-season games", all(s.games == 18 for s in res.stats.values()))
check("the Ambassador season and bowl were played", len(res.ambassador_games) == 28 and res.ambassador_bowl.home_pts is not None)
check("playoffs have 13 games", len(res.playoff_games) == 13)
check("no playoff injuries were rolled", all(w <= R.REGULAR_SEASON_WEEKS for w, *_ in res.runner.injury_log))
check("rosters are still full after the offseason", all(len(t.roster) == ROSTER_SIZE for t in lg.teams))
check("everyone is healthy at the start of a new season", all(p.weeks_out == 0 for t in lg.teams for p in t.roster))
rookies = [p for t in lg.teams for p in t.roster if p.draft_year == 1]
check("drafted rookies make rosters across the league (seven rounds, 336 picks)", len(rookies) <= R.DRAFT_ROUNDS * R.TOTAL_TEAMS and len({p.team_id for p in rookies}) >= 40,
      f"{len(rookies)} rookies still rostered")
picks = sorted(p.draft_pick for p in rookies)
check("draft picks on rosters are distinct", len(picks) == len(set(picks)))
sid = [p.id for t in lg.teams for p in t.roster] + [p.id for p in lg.free_agents]
check("a player is never on a team and in free agency at once", len(sid) == len(set(sid)))

# injuries really remove players from the lineup
t = lg.by_id[1]
star = build_lineup(1, t.roster).qb
star.weeks_out = 3
check("an injured starter is replaced in the lineup", build_lineup(1, t.roster).qb.id != star.id)
star.weeks_out = 0

# ---- determinism ---------------------------------------------------------------------------
def history(seed, n=3, engine="drives"):
    r = random.Random(seed)
    L = new_league(r, rosters=True)
    out = []
    for y in range(1, n + 1):
        s = run_season(L, y, r, Options(engine=engine, keep_boxes=False))
        out.append((s.champion, tuple(sorted(s.new_exiles)), round(sum(t.strength for t in L.teams), 6)))
    return out


check("same seed gives the identical roster-driven league", history(9) == history(9))
check("a different seed gives a different league", history(9) != history(10))

# ---- long-run stability --------------------------------------------------------------------
for eng in ("fast", "drives"):
    r = random.Random(33)
    L = new_league(r, rosters=True)
    sds, ovrs = [], []
    ok_tiers = True
    for y in range(1, 26):
        s = run_season(L, y, r, Options(engine=eng, keep_boxes=False))
        sds.append(st.pstdev([t.strength for t in L.teams]))
        ovrs.append(st.mean(p.ovr for t in L.teams for p in t.roster))
        ok_tiers &= len({(t.conf, t.div, t.tier) for t in L.active()}) == R.ACTIVE_TEAMS
    early, late = st.mean(ovrs[11:18]), st.mean(ovrs[18:])
    check(f"[{eng}] talent level settles and stays steady (seasons 12-18 vs 19-25)", abs(late - early) < 1.0 and max(ovrs[11:]) - min(ovrs[11:]) < 2.0,
          f"avg overall {early:.1f} -> {late:.1f}")
    check(f"[{eng}] the league keeps its parity (strength spread stays between 2 and 6 points)", 2.0 < min(sds[3:]) and max(sds) < 6.0,
          f"min {min(sds[3:]):.1f}, max {max(sds):.1f}")
    check(f"[{eng}] tier slots stay legal for 25 seasons", ok_tiers)

# ---- fair competitiveness (the project's test standard) ------------------------------------
import fairness  # noqa: E402
per, rows = fairness.run("fast", range(100, 116), 48)      # 16 leagues: the exile-effect measure is noisy, 6 leagues were not enough
for name, v, lo, hi, ok, a, b, meaning in rows:
    check(f"fair competitiveness: {name} inside {lo} to {hi}", ok, f"{v:.3f}")

print()
if failures:
    print(f"{len(failures)} Phase 2 check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All Phase 2 checks passed.")
