"""One full DFL year: regular season, Ambassador Season, playoffs, exile, lottery, draft,
and the offseason that sets up next year's tiers and teams."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import rules as R
import placeholder_model as PM
from draft import build_draft_order
from league import League
from playoffs import play_playoffs
from schedule import Game, build_ambassador_schedule, build_schedule, check_schedule
from sim import play_game
from standings import Stats, compute_stats, rank_teams


@dataclass
class Options:
    model: PM.Model = field(default_factory=PM.Model)
    lottery_pool: str = R.LOTTERY_POOL
    lottery_weights: tuple = R.LOTTERY_WEIGHTS
    validate_schedule: bool = True


@dataclass
class SeasonResult:
    year: int
    start: dict                         # team id -> (status, tier, strength) at kickoff
    games: List[Game]
    ambassador_games: List[Game]
    ambassador_bowl: Optional[Game]
    playoff_games: List[Game]
    stats: Dict[int, Stats]             # active teams, regular season
    ambassador_stats: Dict[int, Stats]
    division_ranks: Dict[int, List[int]]
    new_exiles: List[int]
    returners: List[int]
    seeds: Dict[int, List[int]]
    exits: Dict[int, str]
    champion: int
    lottery_pool_order: List[int]
    draft: List[tuple]                  # (pick, team id, band)
    tiebreak_log: list
    recall_division: int
    recall_votes: List[int]
    next_tiers: Dict[int, int]


def run_season(league: League, year: int, rng: random.Random, opt: Options = None) -> SeasonResult:
    opt = opt or Options()
    model = opt.model
    start = league.snapshot()
    active = league.active()
    active_ids = [t.id for t in active]
    returners = [t.id for t in league.exiled()]

    # ---- regular season
    games = build_schedule(league, rng)
    if opt.validate_schedule:
        errs = check_schedule(league, games)
        if errs:
            raise AssertionError(f"year {year}: illegal schedule: {errs[:3]}")
    for g in games:
        play_game(g, league, rng, model)
    stats = compute_stats(league, games, active_ids)

    # ---- division standings (decides exile)
    log: list = []
    division_ranks: Dict[int, List[int]] = {}
    for div_id in range(R.TOTAL_DIVISIONS):
        ids = [t.id for t in league.active_in_division(div_id)]
        division_ranks[div_id] = rank_teams(ids, stats, R.TIEBREAKERS, rng, log, f"division")
    new_exiles = [ranks[R.EXILE_TRIGGER_FINISH - 1] for ranks in division_ranks.values()]

    # ---- Ambassador Season (the teams exiled this year)
    amb_games = build_ambassador_schedule(returners, rng)
    for g in amb_games:
        play_game(g, league, rng, model)
    amb_stats = compute_stats(league, amb_games, returners)
    amb_rank = rank_teams(returners, amb_stats, R.RECORD_ONLY_TIEBREAKERS, rng, log, "ambassador")
    bowl = Game(R.AMBASSADOR_BOWL_WEEK, amb_rank[0], amb_rank[1], "ambassador_bowl")
    play_game(bowl, league, rng, model, neutral=True)

    # ---- playoffs
    seeds, playoff_games, exits, champion = play_playoffs(league, division_ranks, stats, rng, model, log)

    # ---- draft
    all_stats = dict(stats)
    all_stats.update(amb_stats)
    draft, pool_order = build_draft_order(
        new_exiles=new_exiles, returners=returners, active_ids=active_ids, playoff_exits=exits,
        stats=all_stats, rng=rng, log=log, lottery_pool=opt.lottery_pool, weights=opt.lottery_weights)

    # ---- owner recall workload (ASSUMED rotation: division 0, 1, ... 7, repeat)
    recall_div = (year - 1) % R.TOTAL_DIVISIONS
    votes = {t.id for t in league.division(recall_div)}
    if R.RECALL_ON_EXILE:
        votes |= set(new_exiles)

    # ---- offseason: talent, exile and return, new tiers
    next_tiers: Dict[int, int] = {}
    for div_id, ranks in division_ranks.items():
        survivors = ranks[:R.EXILE_TRIGGER_FINISH - 1]
        for tier, tid in enumerate(survivors, start=1):
            next_tiers[tid] = tier
    for tid in returners:
        next_tiers[tid] = R.EXILE_RETURN_TIER

    pick_of = {tid: pick for pick, tid, _ in draft}
    assert len(pick_of) == R.TOTAL_TEAMS
    for t in league.teams:
        s = model.retention * t.strength + model.pick_value(pick_of[t.id]) + rng.gauss(0.0, model.offseason_noise_sd)
        if t.id in returners:
            s += model.exile_return_bonus
        t.strength = s
    mean = sum(t.strength for t in league.teams) / len(league.teams)
    for t in league.teams:
        t.strength -= mean            # strength is relative to the league average

    for t in league.teams:
        if t.id in new_exiles:
            t.status, t.tier = "exiled", None
        elif t.id in returners:
            t.status, t.tier = "active", R.EXILE_RETURN_TIER
        else:
            t.tier = next_tiers[t.id]

    return SeasonResult(
        year=year, start=start, games=games, ambassador_games=amb_games, ambassador_bowl=bowl,
        playoff_games=playoff_games, stats=stats, ambassador_stats=amb_stats,
        division_ranks=division_ranks, new_exiles=new_exiles, returners=returners, seeds=seeds,
        exits=exits, champion=champion, lottery_pool_order=pool_order, draft=draft,
        tiebreak_log=log, recall_division=recall_div, recall_votes=sorted(votes), next_tiers=next_tiers)
