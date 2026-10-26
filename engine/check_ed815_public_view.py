"""Contract tests for Edition 8.15's stateless read-only viewer boundary."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ed815_public_view as V

def expect_error(fn, exception=Exception):
    try:
        fn()
    except exception:
        return
    raise AssertionError("expected exception")

card = {
    "id": "P-001", "name": "Jane Example", "role": "player",
    "position": "QB", "birth_year": 1977, "height": 70,
    "weight": 155, "look": {"hair_color": "gold", "eye_color": "green",
                              "hidden_talent": 99, "private": {"fear": 50}},
    "attributes": {"throwing": 99}, "traits": {"greed": 73},
    "memories": ["secret"], "relationships": {"rival": 100},
    "overall": 99, "salary": 123,
}
events = [
    {"id": "ev-1", "sequence": 1, "simulated_time": "2000-01-01T00:00:00Z",
     "visibility": "public", "public_summary": "Team formed",
     "state_changes": {"private_plan": 88}, "random_key": "secret"},
    {"id": "ev-2", "sequence": 2, "simulated_time": "2000-01-02T00:00:00Z",
     "visibility": "private", "public_summary": "Should not appear",
     "state_changes": {"private_talent": 99}},
    {"id": "ev-3", "sequence": 3, "simulated_time": "2000-01-03T00:00:00Z",
     "visibility": "public", "public_summary": "Practice begins",
     "participants": ["P-001"], "internal_note": "secret"},
]
before = json.dumps([card, events], sort_keys=True)
p = V.public_packet(cards=[card], events=events, season_year=2000)
assert p["rule_version"] == "DFL-Ed8.15"
assert p["tabs"] == ["Home", "Teams", "Players", "Schedule", "Standings", "Statistics"]
assert set(p["characters"][0]) == {"id", "name", "role", "position", "height", "weight", "look", "age"}
assert p["characters"][0]["age"] == 23
assert p["characters"][0]["look"] == {"eye_color": "green", "hair_color": "gold"}
assert [e["id"] for e in p["event_digest"]] == ["ev-1", "ev-3"]
assert all(set(e) == {"id", "sequence", "simulated_time", "public_summary"} for e in p["event_digest"])
assert [e["id"] for e in V.public_digest(events, since_sequence=1)] == ["ev-3"]
assert V.public_digest(events, since_sequence=3) == []
assert json.dumps([card, events], sort_keys=True) == before
assert V.public_packet(cards=[card], events=events, season_year=2000) == p
p["characters"][0]["look"]["hair_color"] = "modified"
p["event_digest"][0]["public_summary"] = "modified"
assert card["look"]["hair_color"] == "gold"
assert events[0]["public_summary"] == "Team formed"
assert "secret" not in json.dumps(V.public_packet(cards=[card], events=events, season_year=2000))
expect_error(lambda: V.public_character(card, season_year=1770), ValueError)
expect_error(lambda: V.public_digest(events, since_sequence=-1), ValueError)
expect_error(lambda: V.public_digest([events[1], events[0]]), ValueError)
expect_error(lambda: V.public_digest([{**events[0], "sequence": 0}]), ValueError)
expect_error(lambda: V.public_digest([{**events[0], "public_summary": {"secret": 1}}]), ValueError)
expect_error(lambda: V.public_character({**card, "look": {"hair_color": {"secret": 1}}}, season_year=2000), ValueError)
expect_error(lambda: V.public_character({**card, "name": {"secret": "Jane"}}, season_year=2000), ValueError)
expect_error(lambda: V.public_packet(cards="not cards", events=events, season_year=2000), TypeError)
print("OK: Edition 8.15 viewer is stateless, public-only, deterministic and copy-isolated")
