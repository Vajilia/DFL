"""Check the game engine produces football-like numbers.

    python engine/calibrate_engine.py [--games 6000]

The targets are rough NFL-style figures chosen by the AI as a stand-in for "looks like
football". They are not league rules and not the Commissioner's decisions.
"""
import argparse
import os
import random
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_engine import EngineParams, simulate_game  # noqa: E402
from lineup import build_lineup  # noqa: E402
from players import IdSource, build_roster  # noqa: E402

# (label, target, tolerance) per team per game unless noted
TARGETS = {
    "points": (22.0, 1.5),
    "plays": (63.5, 3.0),
    "pass_att": (33.5, 2.0),
    "completion_pct": (65.0, 2.0),
    "yards_per_attempt": (6.9, 0.5),
    "rush_att": (26.5, 2.0),
    "yards_per_carry": (4.3, 0.3),
    "total_yards": (340.0, 25.0),
    "sacks_taken": (2.5, 0.5),
    "interceptions": (0.75, 0.2),
    "fumbles_lost": (0.5, 0.2),
    "punts": (4.3, 0.8),
    "fg_attempts": (1.9, 0.5),
    "fg_pct": (84.0, 5.0),
    "third_down_pct": (40.0, 4.0),
    "first_downs": (20.0, 2.5),
    "drives": (11.0, 1.2),
    "time_of_possession_min": (30.0, 1.5),
    "game_margin_sd": (13.5, 1.5),
    "home_win_pct": (54.0, 3.0),
    "overtime_pct": (6.0, 3.0),
}


def league_sample(n_games: int, seed: int = 1, params: EngineParams = None, team_offset_sd: float = 0.0, teams: int = 32):
    rng = random.Random(seed)
    ids = IdSource()
    lineups = []
    for t in range(teams):
        off = rng.gauss(0.0, team_offset_sd)
        lineups.append(build_lineup(t + 1, build_roster(rng, ids, t + 1, off)))
    stats = defaultdict(list)
    margins = []
    home_wins = ot = 0
    for g in range(n_games):
        a, b = rng.sample(range(teams), 2)
        res = simulate_game(lineups[a], lineups[b], rng, params)
        margins.append(res.score[0] - res.score[1])
        home_wins += res.score[0] > res.score[1]
        ot += res.ot_periods > 0
        for i in (0, 1):
            t = res.team[i]
            stats["points"].append(res.score[i])
            stats["plays"].append(t["plays"] + t["sack_yds"] * 0 + 0)
            stats["pass_att"].append(t["pass_att"])
            stats["completions"].append(t["pass_cmp"])
            stats["pass_yds"].append(t["pass_yds"])
            stats["rush_att"].append(t["rush_att"])
            stats["rush_yds"].append(t["rush_yds"])
            stats["total_yards"].append(t["yards"])
            stats["sacks_taken"].append(res.team[1 - i]["sacks"])
            stats["turnovers"].append(t["turnovers"])
            stats["punts"].append(t["punts"])
            stats["fg_attempts"].append(t["fga"])
            stats["fg_made"].append(t["fgm"])
            stats["third_att"].append(t["third_att"])
            stats["third_conv"].append(t["third_conv"])
            stats["first_downs"].append(t["first_downs"])
            stats["drives"].append(t["drives"])
            stats["top"].append(t["top_secs"] / 60.0)
        for pid, d in res.players.items():
            stats["ints_thrown"].append(d.get("pass_int", 0))
            stats["fumbles_lost_p"].append(d.get("fumbles_lost", 0))
    n = len(stats["points"])
    S = lambda k: sum(stats[k]) / n
    out = {
        "points": S("points"), "plays": S("plays"), "pass_att": S("pass_att"),
        "completion_pct": 100 * sum(stats["completions"]) / max(1, sum(stats["pass_att"])),
        "yards_per_attempt": sum(stats["pass_yds"]) / max(1, sum(stats["pass_att"])),
        "rush_att": S("rush_att"),
        "yards_per_carry": sum(stats["rush_yds"]) / max(1, sum(stats["rush_att"])),
        "total_yards": S("total_yards"), "sacks_taken": S("sacks_taken"),
        "interceptions": sum(stats["ints_thrown"]) / n,
        "fumbles_lost": sum(stats["fumbles_lost_p"]) / n,
        "punts": S("punts"), "fg_attempts": S("fg_attempts"),
        "fg_pct": 100 * sum(stats["fg_made"]) / max(1, sum(stats["fg_attempts"])),
        "third_down_pct": 100 * sum(stats["third_conv"]) / max(1, sum(stats["third_att"])),
        "first_downs": S("first_downs"), "drives": S("drives"), "time_of_possession_min": S("top"),
        "game_margin_sd": statistics.pstdev(margins),
        "home_win_pct": 100 * home_wins / n_games, "overtime_pct": 100 * ot / n_games,
    }
    out["_points_sd"] = statistics.pstdev(stats["points"])
    out["_n"] = n_games
    return out


def report(out) -> str:
    L = ["| Measure (per team per game unless noted) | This engine | Target | Within range? |", "| --- | --- | --- | --- |"]
    ok_all = True
    for k, (target, tol) in TARGETS.items():
        v = out[k]
        ok = abs(v - target) <= tol
        ok_all &= ok
        L.append(f"| {k.replace('_', ' ')} | {v:.2f} | {target:.2f} (+/- {tol}) | {'yes' if ok else 'NO'} |")
    return "\n".join(L), ok_all


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=6000)
    a = ap.parse_args()
    out = league_sample(a.games)
    text, ok = report(out)
    print(text)
    print("\nscore sd per team:", round(out["_points_sd"], 2))
