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
    tender_reach: float = 1.5             # a restricted player worth more than this many times her tender is signed at the market (or lost), not tendered
    exile_veteran_dice: bool = True       # an exiled club's expiring veteran (4+ accrued seasons, restricted only by the exile rule) is tendered only if the club wants her, by the same dice as any re-signing
    rfa_offer_prob: float = 0.10          # chance a tendered restricted free agent worth well over her tender draws an offer sheet from a club that can afford one (offer sheets are rare)
    contract_tables: bool = True          # step 6i: the club's value-to-price rule decides who is kept and important deals are made at a table; False = the old re-signing dice
    keep_g0: float = -12.0                # the value rule: kept when her gain to the club is at least g0 + g1 x her price (+ the general manager's shift)
    keep_g1: float = 0.3
    keep_gm_shift: float = 20.0
    cap_headroom: float = 3.0             # $ millions a club keeps back from its limit when it re-signs and signs free agents (NFL clubs rarely spend to the last dollar)
    table_min_ovr: float = 70.0           # players rated this or better are signed at a contract table
    ext_prob: float = 0.40                # chance a club extends an eligible player (final contract year ahead, rated ext_min_ovr or better) before her deal runs out
    ext_min_ovr: float = 66.0
    ext_max_age: int = 30
    trade_sell_prob: float = 0.80         # offseason trade window: chance a club sells a player for picks (autotrade.py)
    trade_swap_prob: float = 0.25         # and chance it trades up the board (two picks for one earlier one)
    trade_week_prob: float = 0.15         # each in-season window (weeks 3 and 6): chance a club sells a player
    tag_prob: float = 0.35                # chance a club tags its best expiring unrestricted player rated tag_min_ovr or better (a tag is a premium one-year deal)
    tag_min_ovr: float = 70.0
    tag_franchise_ovr: float = 78.0       # a tagged player rated this or better gets the franchise tag; below it, the transition tag
    tag_offer_prob: float = 0.05          # chance a franchise- or transition-tagged player worth at least her tag price draws an offer sheet
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
