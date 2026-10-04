"""Playoff seeding and bracket: 4 division winners + 3 wild cards per conference."""
from __future__ import annotations

import random
from typing import Dict, List

import rules as R
import placeholder_model as PM
from schedule import Game
from sim import GameRunner
from standings import rank_teams


def seed_conference(conf: int, league, division_ranks: Dict[int, List[int]], stats, rng: random.Random,
                    log: list) -> List[int]:
    """Seeds 1-7 for one conference (team ids, best seed first)."""
    div_ids = [conf * R.DIVISIONS_PER_CONFERENCE + d for d in range(R.DIVISIONS_PER_CONFERENCE)]
    winners = [division_ranks[d][0] for d in div_ids]
    ranked_winners = rank_teams(winners, stats, R.CROSS_DIVISION_TIEBREAKERS, rng, log, "division_winner_seeding")
    fifth = {division_ranks[d][-1] for d in div_ids}
    others = []
    for d in div_ids:
        for tid in division_ranks[d]:
            if tid in winners:
                continue
            if tid in fifth and not R.FIFTH_PLACE_WILD_CARD_ELIGIBLE:
                continue
            others.append(tid)
    ranked_wc = rank_teams(others, stats, R.CROSS_DIVISION_TIEBREAKERS, rng, log, "wild_card")
    return ranked_winners + ranked_wc[:R.WILD_CARDS_PER_CONFERENCE]


def _play(home: int, away: int, week: int, kind: str, runner, games, neutral=False) -> int:
    g = Game(week, home, away, kind)
    runner.play(g, neutral=neutral, injuries=False)
    games.append(g)
    return g.winner


def play_conference_bracket(seeds: List[int], runner, games: List[Game], exits: Dict[int, str]) -> int:
    """Seed 1 has a bye; wild card round is 2v7, 3v6, 4v5; the four survivors are
    re-seeded for the divisional round. Returns the conference champion's id."""
    s = {i + 1: tid for i, tid in enumerate(seeds)}
    seed_of = {tid: i for i, tid in s.items()}
    wc_winners = []
    for hi, lo in ((2, 7), (3, 6), (4, 5)):
        w = _play(s[hi], s[lo], R.WILD_CARD_WEEK, "playoff_wc", runner, games)
        loser = s[lo] if w == s[hi] else s[hi]
        exits[loser] = "wild_card"
        wc_winners.append(w)
    alive = sorted([s[1]] + wc_winners, key=lambda t: seed_of[t])
    div_winners = []
    for hi, lo in ((0, 3), (1, 2)):
        w = _play(alive[hi], alive[lo], R.DIVISIONAL_WEEK, "playoff_div", runner, games)
        exits[alive[lo] if w == alive[hi] else alive[hi]] = "divisional"
        div_winners.append(w)
    div_winners.sort(key=lambda t: seed_of[t])
    champ = _play(div_winners[0], div_winners[1], R.CHAMPIONSHIP_WEEK, "playoff_conf", runner, games)
    exits[div_winners[1] if champ == div_winners[0] else div_winners[0]] = "conference"
    return champ


def play_playoffs(league, division_ranks, stats, rng, runner, log):
    """Returns (seeds_by_conf, playoff_games, exits, champion_id)."""
    games: List[Game] = []
    exits: Dict[int, str] = {}
    seeds_by_conf, champs = {}, []
    for conf in range(len(R.CONFERENCES)):
        seeds = seed_conference(conf, league, division_ranks, stats, rng, log)
        assert len(seeds) == R.PLAYOFF_SEEDS_PER_CONFERENCE
        seeds_by_conf[conf] = seeds
        champs.append(play_conference_bracket(seeds, runner, games, exits))
    a, b = champs
    home, away = (a, b) if stats[a].pct >= stats[b].pct else (b, a)
    champion = _play(home, away, R.FINAL_WEEK, "playoff_final", runner, games,
                     neutral=R.FINAL_IS_NEUTRAL_SITE)
    exits[away if champion == home else home] = "final_loss"
    exits[champion] = "champion"
    return seeds_by_conf, games, exits, champion
