"""Positions, roster sizes, starters and the ratings each position carries.

Roster sizes and starter counts are structural choices for the game engine, not league rules
Jeph has stated. They are tagged assumed in docs/decisions.md.
"""

POSITIONS = ("QB", "RB", "WR", "TE", "OL", "DL", "LB", "CB", "S", "K", "P")

# Players kept per position (47 in all)
ROSTER_COUNTS = {"QB": 3, "RB": 4, "WR": 6, "TE": 3, "OL": 8, "DL": 7, "LB": 5, "CB": 5, "S": 4, "K": 1, "P": 1}
ROSTER_SIZE = sum(ROSTER_COUNTS.values())

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
