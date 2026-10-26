"""Run the check scripts in tiers (the Commissioner approved the split, 2026-10-12).

  python engine/run_checks.py            the fast tier: every script that finishes in a few minutes; run it after every change
  python engine/run_checks.py --slow     the slow tier: the long simulations (fairness over 16 leagues, the drive-engine, decisions, store round-trips); run it
                                         before a milestone push or overnight
  python engine/run_checks.py --all      both
  python engine/run_checks.py --list     show the tiers

Anything not named below defaults to the slow tier, so a new script never silently goes unrun. The tiers come from the measured durations of the last full run.
Add -j 2 to run two scripts at a time on a two-core machine (the fairness job needs a core of its own, so leave it at 1 while one is running).
"""
import argparse
import glob
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
FAST = """ed815_spatial_trace ed815_game_final_ledger ed815_event_store ed815_public_results ed815_build_mode ed815_site_preview ed815_open_items ed815_phase1_gate ed815_public_view ed815_migration ed815_cross_rotation ed815_independent ed815_tables ed815_waiver_ledger ed815_draft_roster ed815_free_agents ed815_handoff ed815_league_store ed815_storage ed815_settlement ed815_transactions ed815_reference ed815_compensation ed815_waivers ed815_picks ed815_contracts ed815_cap ed815_market ed815_calendar ed815_cycle ed815_standings agents autotrade calendar cards ceo chronicle contracts coordinators elevations enrichment extensions founding gm_roster governance injuries live movement phase0 phase1 playlog
prospects relations rosters rulebook service service_pay site skeleton tiebreaks ties transactions verdicts""".split()


def scripts():
    names = sorted(os.path.basename(p)[6:-3] for p in glob.glob(os.path.join(HERE, "check_*.py")))
    fast = [n for n in names if n in FAST]
    slow = [n for n in names if n not in FAST]
    return fast, slow


def run_one(name, timeout):
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, f"check_{name}.py")], capture_output=True, text=True, timeout=timeout)
        code, tail = r.returncode, (r.stdout + r.stderr).strip().splitlines()[-3:]
    except subprocess.TimeoutExpired:
        code, tail = 124, ["timed out"]
    return name, code, time.time() - t0, tail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slow", action="store_true", help="the slow tier only")
    ap.add_argument("--all", action="store_true", help="both tiers")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("-j", type=int, default=1)
    a = ap.parse_args()
    fast, slow = scripts()
    if a.list:
        print("fast:", " ".join(fast)); print("slow:", " ".join(slow)); return 0
    todo = [(n, 900) for n in fast] * (not a.slow) + [(n, 7200) for n in slow] * (a.slow or a.all)
    with ThreadPoolExecutor(max_workers=a.j) as ex:
        results = list(ex.map(lambda t: run_one(*t), todo))
    bad = [r for r in results if r[1] != 0]
    for name, code, secs, tail in results:
        print(f"{'ok  ' if code == 0 else 'FAIL'} {name:14s} {secs:7.0f}s")
    for name, code, secs, tail in bad:
        print(f"\n--- {name} (exit {code})"); print("\n".join(tail))
    print(f"\n{len(results) - len(bad)} of {len(results)} passed, {sum(r[2] for r in results):.0f}s")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
