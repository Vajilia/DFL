"""150-season structural replay without a football engine.

Scores are synthetic test fixtures, NOT NFL-calibrated results.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import ed815_calendar as CAL
import ed815_cycle as CYC


def sample_results(structure, world_seed=73):
    result = []
    for fixture in structure.fixtures:
        key = (f"{world_seed}|{structure.season}|{fixture['week']}|"
               f"{fixture['game']}|{fixture['home']}|{fixture['away']}")
        n = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],"big")
        # Intentional rare tied games to test standings behavior.
        a,b = (17,17) if n % 301 == 0 else (7 + (n % 38), 3 + ((n >> 12) % 38))
        result.append({**fixture, "home_score":a, "away_score":b})
    return result


def initial():
    seeded = {div:[f"{i}/{rank}" for rank in range(1,6)]
              for i,div in enumerate(CAL.DIVISION_ORDER)}
    ambassadors = {div:f"{i}/amb" for i,div in enumerate(CAL.DIVISION_ORDER)}
    return CYC.build_structure(1,seeded,ambassadors)


def check_validation():
    struct = initial()
    games = sample_results(struct)
    try:
        CYC.finalize_structure(struct,games[:-1],73)
    except ValueError:
        pass
    else:
        raise AssertionError("partial season incorrectly completed")
    bad = [dict(row) for row in games]
    bad[0]["home"] = bad[1]["home"]
    try:
        CYC.finalize_structure(struct,bad,73)
    except ValueError:
        pass
    else:
        raise AssertionError("mismatched fixture incorrectly completed")
    bad = [dict(row) for row in games]
    bad[0]["home_score"] = -1
    try:
        CYC.finalize_structure(struct,bad,73)
    except ValueError:
        pass
    else:
        raise AssertionError("negative score incorrectly accepted")
    successor, summary = CYC.finalize_structure(struct,games,73)
    reverse, summary2 = CYC.finalize_structure(struct,list(reversed(games)),73)
    assert successor.seeded_divisions == reverse.seeded_divisions
    assert successor.ambassadors == reverse.ambassadors
    assert summary["playoff_seeds"] == summary2["playoff_seeds"]


def check_150_seasons():
    current = initial()
    first_clubs = {club for ids in current.seeded_divisions.values() for club in ids}
    first_clubs.update(current.ambassadors.values())
    assert len(first_clubs) == 48
    appeared = Counter()
    for season in range(1,151):
        assert current.season == season
        previous = current
        next_state, summary = CYC.finalize_structure(
            current,sample_results(current),73)
        assert len(summary["exiled_clubs"]) == 8
        assert len(set(summary["exiled_clubs"].values())) == 8
        for div in CAL.DIVISION_ORDER:
            assert next_state.seeded_divisions[div][-1] == previous.ambassadors[div]
            assert next_state.ambassadors[div] in previous.seeded_divisions[div]
            appeared[next_state.ambassadors[div]] += 1
            assert next_state.ambassadors[div] not in next_state.seeded_divisions[div]
            assert len(next_state.seeded_divisions[div]) == 5
        every = {club for ids in next_state.seeded_divisions.values() for club in ids}
        every.update(next_state.ambassadors.values())
        assert every == first_clubs
        for conf,seeds in summary["playoff_seeds"].items():
            assert len(seeds) == len(set(seeds)) == 7
            assert all(seeds[i] not in summary["exiled_clubs"].values() for i in range(7))
        current = next_state
    assert sum(appeared.values()) == 150*8


if __name__ == "__main__":
    check_validation()
    check_150_seasons()
    print("Edition 8.15 recursive schedule/exile: 150 synthetic seasons passed")
