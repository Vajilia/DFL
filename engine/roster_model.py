"""PLACEHOLDER dials for how rosters change from year to year.

Like placeholder_model.py these are tuning numbers, not league rules. They are calibrated so
the league stays competitive over many seasons and so a team returning from exile has the
potential to compete for about 3rd in its division (Jeph's confirmed design intent).
"""
from dataclasses import dataclass


@dataclass
class RosterModel:
    # free agency
    fa_entry_rate: float = 0.15           # share of each roster whose contract runs out and who reach the market
    fa_star_protect: float = 0.5          # high-rated players are this much likelier to be re-signed
    fa_priority_noise: float = 2.0        # randomness in the order teams pick (rating points)
    undrafted_per_year: int = 170         # new unsigned players added to the market each year
    undrafted_mean: float = 50.0
    undrafted_sd: float = 6.0
    # exile relief: signing priority and a number of premium signings for a team coming back
    exile_fa_priority: bool = False       # returners pick first in free agency (else ordered like any other team)
    exile_premium_signings: float = 0.25  # average number (fractions are chances) of top-of-market signings
    # draft: one rookie per team per year; quality by pick
    rookie_base: float = 52.0
    rookie_span: float = 22.0
    rookie_decay: float = 14.0
    rookie_sd: float = 6.0
    # progression
    prog_noise: float = 2.2
    prog_attr_noise: float = 1.5
