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
from sim import GameRunner
from roster_model import RosterModel
from standings import Stats, compute_stats, rank_by_style


@dataclass
class Options:
    model: PM.Model = field(default_factory=PM.Model)
    lottery_pool: str = R.LOTTERY_POOL
    lottery_weights: tuple = R.LOTTERY_WEIGHTS
    returner_slot: str = R.RETURNER_DRAFT_SLOT   # where teams back from exile pick in the 9-34 band: by_record | end_of_band | start_of_band
    validate_schedule: bool = True
    engine: str = "auto"               # "placeholder" | "fast" | "drives"; auto = drives if the league has rosters
    roster_model: RosterModel = field(default_factory=RosterModel)
    engine_params: object = None       # game_engine.EngineParams, or None for the defaults
    keep_boxes: bool = True            # keep each game's box score (turn off for long studies)
    injuries: bool = True
    record_plays: bool = False         # option 3: full play-by-play. Off by default.


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
    runner: object = None               # GameRunner: player and team stat totals, injury log
    offseason: dict = None              # what the roster offseason did


def run_season(league: League, year: int, rng: random.Random, opt: Options = None) -> SeasonResult:
    opt = opt or Options()
    model = opt.model
    start = league.snapshot()
    active = league.active()
    active_ids = [t.id for t in active]
    returners = [t.id for t in league.exiled()]

    # ---- regular season and Ambassador Season, played week by week so injuries can run
    runner = GameRunner(league, rng, model, opt.engine, opt.engine_params, opt.injuries, opt.keep_boxes,
                        opt.record_plays)
    if league.has_rosters:
        from league import refresh_strengths
        refresh_strengths(league)          # fresh power ratings for the placeholder-style readers
    games = build_schedule(league, rng)
    if opt.validate_schedule:
        errs = check_schedule(league, games)
        if errs:
            raise AssertionError(f"year {year}: illegal schedule: {errs[:3]}")
    amb_games = build_ambassador_schedule(returners, rng)
    by_week: Dict[int, List[Game]] = {}
    for g in games + amb_games:
        by_week.setdefault(g.week, []).append(g)
    log: list = []
    bowl = None
    for week in range(1, R.REGULAR_SEASON_WEEKS + 1):
        if week == R.AMBASSADOR_BOWL_WEEK:
            # the two best Ambassador records meet once the 28 round-robin games are done
            amb_rank = rank_by_style("ambassador", returners, compute_stats(league, amb_games, returners),
                                     rng, log, "ambassador")
            bowl = Game(R.AMBASSADOR_BOWL_WEEK, amb_rank[0], amb_rank[1], "ambassador_bowl")
            by_week.setdefault(week, []).append(bowl)
        for g in by_week.get(week, []):
            runner.play(g, neutral=(g.kind == "ambassador_bowl"))
        runner.end_week()
    stats = compute_stats(league, games, active_ids)
    amb_stats = compute_stats(league, amb_games, returners)

    # ---- division standings (decides exile)
    division_ranks: Dict[int, List[int]] = {}
    for div_id in range(R.TOTAL_DIVISIONS):
        ids = [t.id for t in league.active_in_division(div_id)]
        division_ranks[div_id] = rank_by_style("division", ids, stats, rng, log, "division")
    new_exiles = [ranks[R.EXILE_TRIGGER_FINISH - 1] for ranks in division_ranks.values()]

    # ---- playoffs (ASSUMED: no new injuries in the playoffs; existing injuries stay as they are)
    seeds, playoff_games, exits, champion = play_playoffs(league, division_ranks, stats, rng, runner, log)

    # ---- draft
    all_stats = compute_stats(league, games + amb_games, active_ids + returners)   # one table so tiebreaks see every game
    draft, pool_order = build_draft_order(
        new_exiles=new_exiles, returners=returners, active_ids=active_ids, playoff_exits=exits,
        stats=all_stats, rng=rng, log=log, lottery_pool=opt.lottery_pool, weights=opt.lottery_weights,
        returner_slot=opt.returner_slot)

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
    off_log = None
    if league.has_rosters:
        from offseason import run_roster_offseason
        before = [p for t in league.teams for p in t.roster] + list(league.free_agents)
        off_log = run_roster_offseason(league, rng, opt.roster_model, year, pick_of, returners)
        import cards
        league.retired_players.extend(p for p in before if p.retired)
        cards.offseason_cards(league, year)
    else:
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
        tiebreak_log=log, recall_division=recall_div, recall_votes=sorted(votes), next_tiers=next_tiers,
        runner=runner, offseason=off_log)
