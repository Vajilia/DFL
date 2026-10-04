"""The lottery and the 48-pick draft order."""
from __future__ import annotations

import random
from typing import Dict, List, Tuple

import rules as R
from standings import draft_worst_to_best

# playoff exit stage -> order of the picks 35-48 (earlier exit picks earlier)
EXIT_ORDER = ["wild_card", "divisional", "conference", "final_loss", "champion"]


def run_lottery(pool_worst_to_best: List[int], weights, rng: random.Random, draws: int = R.LOTTERY_DRAWN_PICKS) -> List[int]:
    """Team i holds weight weights[i] (worst record = most balls). `draws` balls decide picks 1..draws, drawn one at
    a time without replacement; the remaining teams take the following picks in order of record, worst first.
    So the worst team can fall no lower than pick draws + 1. Returns team ids in pick order."""
    assert len(pool_worst_to_best) == len(weights)
    remaining = list(range(len(pool_worst_to_best)))
    picks = []
    for _ in range(draws):
        total = sum(weights[i] for i in remaining)
        x = rng.random() * total
        acc = 0.0
        chosen = remaining[-1]
        for i in remaining:
            acc += weights[i]
            if x < acc:
                chosen = i
                break
        picks.append(pool_worst_to_best[chosen])
        remaining.remove(chosen)
    picks.extend(pool_worst_to_best[i] for i in remaining)           # picks draws+1.. in record order
    return picks


def worst_to_best(ids: List[int], stats, rng, log, context) -> List[int]:
    return draft_worst_to_best(ids, stats, rng, log, context)


def build_draft_order(*, new_exiles: List[int], returners: List[int], active_ids: List[int],
                      playoff_exits: Dict[int, str], stats, rng: random.Random, log: list,
                      lottery_pool: str, weights, returner_slot: str = "by_record") -> Tuple[List[Tuple[int, int, str]], List[int]]:
    """Returns ([(pick, team_id, band), ...] for all 48 picks, lottery pool worst->best)."""
    playoff_ids = set(playoff_exits)
    pool = new_exiles if lottery_pool == "just_finished_fifth" else returners
    if lottery_pool not in ("just_finished_fifth", "just_finished_exile"):
        raise ValueError(lottery_pool)
    pool_order = worst_to_best(pool, stats, rng, log, "lottery_order")
    lottery = run_lottery(pool_order, weights, rng)

    if returner_slot not in ("by_record", "end_of_band", "start_of_band"):
        raise ValueError(returner_slot)
    band_ids = [t for t in active_ids if t not in playoff_ids and t not in pool]
    ret_in_band = [t for t in returners if t not in pool]
    if returner_slot == "by_record":
        band = worst_to_best(band_ids + ret_in_band, stats, rng, log, "draft_band_order")
    else:
        # returners pick as a block (ordered among themselves by Ambassador record) at one end of the band
        main = worst_to_best(band_ids, stats, rng, log, "draft_band_order")
        block = worst_to_best(ret_in_band, stats, rng, log, "draft_returner_block_order")
        band = block + main if returner_slot == "start_of_band" else main + block

    top = []
    for stage in EXIT_ORDER:
        ids = [t for t, s in playoff_exits.items() if s == stage]
        top.extend(worst_to_best(ids, stats, rng, log, f"draft_{stage}_order"))

    order = []
    pick = 0
    for tid in lottery:
        pick += 1
        order.append((pick, tid, "exiled_lottery"))
    for tid in band:
        pick += 1
        order.append((pick, tid, "active_non_playoff"))
    for tid in top:
        pick += 1
        order.append((pick, tid, "playoff_teams"))
    return order, pool_order
