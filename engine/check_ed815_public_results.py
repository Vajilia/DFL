"""No hidden or unrevealed game result may reach public DFL standings."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import ed815_public_results as PUBLIC
import ed815_site_preview as SITE

doc = SITE.SOURCE.read_text(encoding="utf-8")
teams, fixtures = SITE.founding_tables(doc)
first = fixtures[0]
second = fixtures[1]
def final(fixture, sequence, a, b, visibility="public"):
    return {
        "id": f"e-{sequence}", "sequence": sequence, "kind": "game_final",
        "visibility": visibility, "public_summary": "Final recorded",
        "simulated_time": "2000-07-01T20:00:00Z",
        "week": int(fixture["week"]), "game": int(fixture["game"]),
        "home": fixture["home"], "away": fixture["away"],
        "home_score": a, "away_score": b,
    }
log = [
    final(first, 1, 17, 17),
    final(second, 2, 999, 888, visibility="private"),
    final(second, 3, 777, 666),
]
none, records0 = PUBLIC.revealed_finals(teams, fixtures, log, through_sequence=0)
assert not none
assert all(x.games_played == 0 for x in records0.values())
one, records1 = PUBLIC.revealed_finals(teams, fixtures, log, through_sequence=1)
assert len(one) == 1 and PUBLIC.public_totals(one) == {"final_games": 1, "ties": 1, "total_points": 34}
assert sum(x.games_played for x in records1.values()) == 2
assert sum(x.wins for x in records1.values()) == 0
assert sum(x.losses for x in records1.values()) == 0
assert sum(x.points_for for x in records1.values()) == 34
three, records3 = PUBLIC.revealed_finals(teams, fixtures, log, through_sequence=3)
assert len(three) == 2 and three[(int(second["week"]),int(second["game"]))]["home_score"] == 777
assert PUBLIC.public_totals(three)["total_points"] == 1477
assert sum(x.wins for x in records3.values()) == 1
assert sum(x.losses for x in records3.values()) == 1
assert PUBLIC.revealed_finals(teams, fixtures, list(log), through_sequence=1)[0] == one

def fails(events, cursor=999):
    try:
        PUBLIC.revealed_finals(teams, fixtures, events, through_sequence=cursor)
    except (ValueError, TypeError):
        return
    raise AssertionError("invalid public final was accepted")

fails([final(first, 1, 10, 7), final(first, 2, 10, 7)])
fails([final(first, 1, True, 0)])
fails([{**final(first, 1, 10, 7), "home": "unknown"}])
fails([final(first, 2, 10, 7), final(second, 1, 3, 5)])
fails(log, cursor=-1)
fails([{**final(first, 1, 10, 7), "game": 999}])
print("OK: strict reveal cursor; private/unreleased scores cannot change public standings")
