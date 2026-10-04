"""Run a multi-season league with no AI: python engine/run_sim.py --seasons 20 --seed 1"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402


def simulate(seed: int, seasons: int, opt: Options = None):
    rng = random.Random(seed)
    league = new_league(rng)
    results = []
    for year in range(1, seasons + 1):
        results.append(run_season(league, year, rng, opt))
    return league, results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seasons", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    league, results = simulate(args.seed, args.seasons)
    for r in results:
        print(r.year, "champion Team", r.champion, "exiled", sorted(r.new_exiles))
