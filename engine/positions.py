"""Positions, roster sizes, starters and the ratings each position carries.

The roster is the rulebook's 53 (rules.ROSTER_LIMIT), 48 of them active on game day, 90 in camp and 16 more on the practice squad
(see rosters.py). The position table is the DFL's own split of the 53 across the 11 positions the engine models (the NFL's long snappers
and fullbacks are folded into OL, TE and RB); starter counts are what the game engine puts on the field.
"""
import rules as R

POSITIONS = ("QB", "RB", "WR", "TE", "OL", "DL", "LB", "CB", "S", "K", "P")

# Players kept per position (53 in all)
ROSTER_COUNTS = {"QB": 3, "RB": 4, "WR": 6, "TE": 4, "OL": 9, "DL": 8, "LB": 6, "CB": 6, "S": 5, "K": 1, "P": 1}
ROSTER_SIZE = sum(ROSTER_COUNTS.values())
assert ROSTER_SIZE == R.ROSTER_LIMIT

# The fewest healthy players of each position a team keeps on its 48-man game-day list (the rest of the 48 are the best of everyone else)
ACTIVE_MINIMUMS = {"QB": 2, "RB": 2, "WR": 4, "TE": 2, "OL": 7, "DL": 5, "LB": 3, "CB": 4, "S": 3, "K": 1, "P": 1}
assert sum(ACTIVE_MINIMUMS.values()) <= R.ACTIVE_LIMIT

# Starters on the field (11 on offense, 11 on defense, plus kicker and punter)
STARTERS = {"QB": 1, "RB": 1, "WR": 3, "TE": 1, "OL": 5, "DL": 4, "LB": 2, "CB": 3, "S": 2, "K": 1, "P": 1}

# Ratings each position carries (all 1-100)
ATTRS = {
    "QB": ("accuracy", "arm", "awareness"),
    "RB": ("elusive", "power", "hands"),
    "WR": ("route", "hands", "speed"),
    "TE": ("route", "hands", "block"),
    "OL": ("pass_block", "run_block"),
    "DL": ("pass_rush", "run_stop"),
    "LB": ("pass_rush", "run_stop", "coverage"),
    "CB": ("coverage", "ball_skills", "tackling"),
    "S": ("coverage", "ball_skills", "tackling"),
    "K": ("power", "accuracy"),
    "P": ("power", "accuracy"),
}

# How the position's ratings blend into one overall number
OVR_WEIGHTS = {
    "QB": (0.45, 0.30, 0.25),
    "RB": (0.40, 0.40, 0.20),
    "WR": (0.35, 0.30, 0.35),
    "TE": (0.30, 0.30, 0.40),
    "OL": (0.50, 0.50),
    "DL": (0.55, 0.45),
    "LB": (0.25, 0.40, 0.35),
    "CB": (0.60, 0.25, 0.15),
    "S": (0.40, 0.25, 0.35),
    "K": (0.40, 0.60),
    "P": (0.60, 0.40),
}

assert all(len(ATTRS[p]) == len(OVR_WEIGHTS[p]) for p in POSITIONS)
assert all(abs(sum(OVR_WEIGHTS[p]) - 1.0) < 1e-9 for p in POSITIONS)
