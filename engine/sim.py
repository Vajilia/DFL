"""Game simulation front end.

Three engines can decide a game (Options.engine in season.py):

  placeholder  the old scalar model: one strength number per team plus noise (Phase 1).
  fast         rosters -> team power rating -> margin plus noise. No box score. Used for studies.
  drives       the full drive-by-drive engine (game_engine.py): box score, player stats.

GameRunner owns everything that has to persist between games: the lineup cache, the injury
clock and the running player and team stat totals.
"""
from __future__ import annotations

import math
import random
from typing import Dict

import rules as R
import placeholder_model as PM
from schedule import Game


def win_probability(expected_margin: float, margin_sd: float) -> float:
    return 0.5 * (1.0 + math.erf(expected_margin / (margin_sd * math.sqrt(2.0))))


# Share of games level after regulation that are still level after a regular-season overtime (NFL rule: both teams possess, then
# sudden death, 10 minutes). Measured on the drive engine (24% of overtime games, about 1.5% of all games, with 6% of games reaching
# overtime); the placeholder and fast engines use it so ties arrive at the same rate whichever engine decides the game. KNOWN GAP: the
# NFL's rate is far lower (0.24% of games, 6% of overtime games under the 2012-24 rule), because NFL overtime drives score more often
# than the drive engine's. Re-fitting overtime scoring is step 9 of the build plan (reports/rulebook_status.md).
OT_TIE_SHARE = 0.24


def score_from_expected(game: Game, expected: float, rng: random.Random, margin_sd: float, allow_tie: bool = False) -> Game:
    """Fill in a score from an expected margin (home minus away). A game level after regulation is settled in overtime:
    by a field goal, or (regular season only) left as a tie at the measured rate."""
    margin = round(rng.gauss(expected, margin_sd))
    tie = False
    if margin == 0:
        if allow_tie and rng.random() < OT_TIE_SHARE:
            tie = True
        else:
            margin = 3 if rng.random() < win_probability(expected, margin_sd) else -3
    loser_pts = int(min(50, max(3, round(rng.gauss(PM.LOSER_POINTS_MEAN, PM.LOSER_POINTS_SD)))))
    winner_pts = loser_pts + abs(margin)
    if tie:
        game.home_pts = game.away_pts = loser_pts
    elif margin > 0:
        game.home_pts, game.away_pts = winner_pts, loser_pts
    else:
        game.home_pts, game.away_pts = loser_pts, winner_pts
    return game


def play_game(game: Game, league, rng: random.Random, model: PM.Model, neutral: bool = False) -> Game:
    """Phase 1 scalar game (uses Team.strength)."""
    hs = league.by_id[game.home].strength
    aw = league.by_id[game.away].strength
    expected = hs - aw + (0.0 if neutral else model.home_advantage)
    return score_from_expected(game, expected, rng, model.margin_sd, R.TIES_ALLOWED and game.counts_ties)


class GameRunner:
    def __init__(self, league, rng: random.Random, model: PM.Model, engine: str = "auto", params=None,
                 injuries: bool = True, keep_boxes: bool = True, record_plays: bool = False):
        if engine == "auto":
            engine = "drives" if league.has_rosters else "placeholder"
        if engine not in ("placeholder", "fast", "drives"):
            raise ValueError(f"unknown engine {engine!r}")
        if engine != "placeholder" and not league.has_rosters:
            raise ValueError(f"engine {engine!r} needs a league built with rosters=True")
        self.league, self.rng, self.model, self.engine = league, rng, model, engine
        self.params = params
        self.injuries = injuries and league.has_rosters
        self.keep_boxes = keep_boxes
        self.record_plays = record_plays          # option 3: keep every play (off by default)
        self._cache: Dict[int, object] = {}
        self._new_hurt: set = set()
        self.injury_log: list = []                # (week, team id, player id, games out)
        self.player_totals: Dict[int, dict] = {}  # season totals, drive engine only
        self.team_totals: Dict[int, dict] = {}
        self.games_played = 0
        self.service_year = None                  # set by run_season; direct game calls need no service accounting
        self.week = 0                             # regular-season weeks finished (the injured-reserve calendar)
        self.ir_log: list = []                    # one rosters.manage_week summary per week

    # ---- lineups ----------------------------------------------------------
    def lineup(self, tid: int):
        lu = self._cache.get(tid)
        if lu is None:
            from lineup import build_lineup
            import rosters
            team = self.league.by_id[tid]
            lu = self._cache[tid] = build_lineup(tid, rosters.game_roster(team), team.coach)
        return lu

    def power(self, tid: int) -> float:
        import power_rating as PR
        return PR.rating(self.lineup(tid))

    # ---- one game ---------------------------------------------------------
    def play(self, game: Game, neutral: bool = False, injuries: bool = True) -> Game:
        if self.service_year is not None:
            import service
            service.record_game(self.league, game, self.service_year)
        if self.engine == "placeholder":
            if self.league.has_rosters:
                pass                              # uses Team.strength as last refreshed
            return play_game(game, self.league, self.rng, self.model, neutral)
        if self.engine == "fast":
            import power_rating as PR
            expected = self.power(game.home) - self.power(game.away) + (0.0 if neutral else PR.HOME_EDGE)
            score_from_expected(game, expected, self.rng, PR.RESIDUAL_SD, R.TIES_ALLOWED and game.counts_ties)
        else:
            from game_engine import simulate_game
            res = simulate_game(self.lineup(game.home), self.lineup(game.away), self.rng, self.params,
                                neutral=neutral, record_plays=self.record_plays,
                                allow_tie=R.TIES_ALLOWED and game.counts_ties)
            game.home_pts, game.away_pts = res.score
            tds = [0, 0]
            for d in res.drives:
                if d["result"] == "TD":
                    tds[d["side"]] += 1
                elif d["result"] in ("INT_TD", "FUMBLE_TD"):
                    tds[1 - d["side"]] += 1
            game.home_tds, game.away_tds = tds
            game.result = res if self.keep_boxes else None
            self._accumulate(game, res)
        self.games_played += 1
        if self.injuries and injuries:
            self._roll_injuries(game)
        return game

    def _accumulate(self, game: Game, res):
        for i, tid in enumerate((game.home, game.away)):
            tt = self.team_totals.setdefault(tid, {"games": 0})
            tt["games"] += 1
            for k, v in res.team[i].items():
                tt[k] = tt.get(k, 0) + v
            tt["pf"] = tt.get("pf", 0) + res.score[i]
            tt["pa"] = tt.get("pa", 0) + res.score[1 - i]
        for pid, d in res.players.items():
            tot = self.player_totals.setdefault(pid, {"games": 0, "pos": d["pos"]})
            tot["games"] += 1
            for k, v in d.items():
                if k in ("pos", "team"):
                    continue
                tot[k] = tot.get(k, 0) + v

    def _roll_injuries(self, game: Game):
        from injuries import roll_injuries
        for tid in (game.home, game.away):
            lu = self.lineup(tid)
            starters = ([lu.qb, lu.te, lu.k, lu.p] + lu.rbs + lu.wrs + lu.ol + lu.dl + lu.lb + lu.cb + lu.s)
            import rosters
            for p, n in roll_injuries(rosters.active_list(self.league.by_id[tid]), starters, self.rng):
                p.weeks_out = n
                self._new_hurt.add(p.id)
                self.injury_log.append((game.week, tid, p.id, n))

    # ---- the weekly clock ---------------------------------------------------
    def end_week(self):
        """MODEL: injuries are counted in weeks. Everyone who was already hurt heals one week."""
        if self.league.has_rosters:
            from injuries import tick_week
            import rosters
            for t in self.league.teams:
                tick_week(list(t.roster) + list(t.ir), self._new_hurt)
            self.week += 1
            self.ir_log.append(rosters.manage_week(self.league, self.rng, R.REGULAR_SEASON_WEEKS - self.week))
        self._new_hurt = set()
        self._cache.clear()
