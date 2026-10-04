"""PLACEHOLDER MODEL. These numbers are NOT league rules and NOT design decisions.

They are stand-ins so the league can run end to end before the real game simulation
exists. Every value is a guess chosen to make a football-like league (about 4 points of
spread between good and bad teams, typical NFL-style scoring). The real talent and game
model replaces this file in a later phase. Results that depend on these numbers (notably
whether exile "pays") must be read as sensitivity tests, not facts.
"""

# ---- Games -----------------------------------------------------------------
HOME_ADVANTAGE = 2.0          # points
MARGIN_SD = 13.5              # spread of a game's final margin around its expectation
LOSER_POINTS_MEAN = 19.0
LOSER_POINTS_SD = 7.0

# ---- Talent (one number per team: points better/worse than an average team) -
INITIAL_STRENGTH_SD = 3.7
RETENTION = 0.80              # share of strength kept from one season to the next
OFFSEASON_NOISE_SD = 2.2      # random year-to-year drift

# ---- Draft value -------------------------------------------------------------
# Strength a team gains from the draft pick it holds: pick 1 is worth DRAFT_PICK1_VALUE,
# falling off by a factor of exp(-1/DRAFT_DECAY) per pick.
# Calibrated 2026-10-04 so a team returning from exile averages about 3rd-to-4th in its division
# (see calibrate_exile.py and reports/exile_calibration.md). A dial, not a rule.
DRAFT_PICK1_VALUE = 1.0
DRAFT_DECAY = 12.0

# ---- Exile ----------------------------------------------------------------
# Extra strength a team gets in the offseason it returns, standing in for 50% cap relief.
EXILE_RETURN_BONUS = 0.5       # calibrated together with DRAFT_PICK1_VALUE; a dial, not a rule


def draft_value(pick: int, pick1_value: float = DRAFT_PICK1_VALUE, decay: float = DRAFT_DECAY) -> float:
    import math
    return pick1_value * math.exp(-(pick - 1) / decay)


from dataclasses import dataclass


@dataclass
class Model:
    """The placeholder numbers bundled together so a study can change them."""
    home_advantage: float = HOME_ADVANTAGE
    margin_sd: float = MARGIN_SD
    retention: float = RETENTION
    offseason_noise_sd: float = OFFSEASON_NOISE_SD
    draft_pick1_value: float = DRAFT_PICK1_VALUE
    draft_decay: float = DRAFT_DECAY
    exile_return_bonus: float = EXILE_RETURN_BONUS

    def pick_value(self, pick: int) -> float:
        return draft_value(pick, self.draft_pick1_value, self.draft_decay)
