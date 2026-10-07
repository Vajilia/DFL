"""PLACEHOLDER dials for how rosters change from year to year.

Like placeholder_model.py these are tuning numbers, not league rules. They are calibrated so
the league stays competitive over many seasons and so a team returning from exile has the
potential to compete for about 3rd in its division (the Commissioner's confirmed design intent).
"""
from dataclasses import dataclass


@dataclass
class RosterModel:
    # free agency
    fa_entry_rate: float = 0.15           # share of each roster whose contract runs out and who reach the market
    fa_star_protect: float = 0.5          # high-rated players are this much likelier to be re-signed
    fa_priority_noise: float = 0.5        # randomness in the order teams pick (rating points)
    undrafted_per_year: int = 1000        # undrafted rookies each year: the market for camp invitations (the camp holds 90, so most camp places go to them)
    market_size: int = 700                # the best of the unsigned who stay on the market for next year (the rest leave football)
    camp_vet_max_ovr: float = 56.0        # camp invitations to unsigned veterans go only to players no better than this (better ones are paid the market price in free agency)
    undrafted_mean: float = 42.0
    undrafted_sd: float = 6.0
    # exile relief: signing priority and a number of premium signings for a team coming back
    exile_fa_priority: bool = False       # returners pick first in free agency (else ordered like any other team)
    exile_premium_signings: float = 0.0   # was 0.05, a stand-in for the 50% cap relief; the relief is now real (economy.close_season), so this is 0
    # draft: one rookie per team per year; quality by pick
    rookie_base: float = 49.0
    rookie_span: float = 25.0
    rookie_decay: float = 14.0
    rookie_late_drop: float = 11.0        # the floor under the rookie curve slides this far from pick 1 to pick 336 (toward an undrafted player's rating)
    rookie_sd: float = 6.0
    # progression
    prog_noise: float = 2.2
    prog_attr_noise: float = 1.5
