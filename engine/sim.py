"""Placeholder game simulation: turns two strength ratings into a final score.

This is a stand-in (see placeholder_model.py). The real game model replaces it later.
"""
from __future__ import annotations

import math
import random

import rules as R
import placeholder_model as PM
from schedule import Game


def win_probability(expected_margin: float, margin_sd: float) -> float:
    return 0.5 * (1.0 + math.erf(expected_margin / (margin_sd * math.sqrt(2.0))))


def play_game(game: Game, league, rng: random.Random, model: PM.Model, neutral: bool = False) -> Game:
    """Fill in the score of a game."""
    hs = league.by_id[game.home].strength
    aw = league.by_id[game.away].strength
    expected = hs - aw + (0.0 if neutral else model.home_advantage)
    margin = round(rng.gauss(expected, model.margin_sd))
    if margin == 0:
        # ASSUMED: no ties. Overtime is settled by a field goal.
        margin = 3 if rng.random() < win_probability(expected, model.margin_sd) else -3
    loser_pts = int(min(50, max(3, round(rng.gauss(PM.LOSER_POINTS_MEAN, PM.LOSER_POINTS_SD)))))
    winner_pts = loser_pts + abs(margin)
    if margin > 0:
        game.home_pts, game.away_pts = winner_pts, loser_pts
    else:
        game.home_pts, game.away_pts = loser_pts, winner_pts
    return game
