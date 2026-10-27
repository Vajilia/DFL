"""Fixture-bound, exactly-once Edition 8.15 completed-game replay checks."""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import ed815_event_store as EVENTS
import ed815_game_final_ledger as LEDGER
from check_ed815_cycle import initial, sample_results

structure = initial()
results = sample_results(structure)
with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / "season.sqlite"
    conn = sqlite3.connect(db)
    EVENTS.initialize(conn)
    assert LEDGER.recorded_results(conn, structure) == []
    def record(result, **overrides):
        return LEDGER.record_final(
            conn, structure, result,
            simulated_time=overrides.get("simulated_time", "2000-07-02T20:00:00Z"),
            random_key="test-only-key",
            public_summary="Final score recorded",
        )
    for candidate in (
        {**results[0], "home": results[1]["home"]},
        {**results[0], "home_score": True},
        {**results[0], "away_score": -2},
        {**results[0], "week": 999},
    ):
        try:
            record(candidate)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid result accepted")
    assert not EVENTS.load_verified(conn)
    assert record(results[0]) == 1
    assert len(LEDGER.recorded_results(conn, structure)) == 1
    for candidate in (results[0], {**results[0], "home_score": 98}):
        try:
            record(candidate)
        except ValueError:
            pass
        else:
            raise AssertionError("fixture was finalized twice")
    assert len(EVENTS.load_verified(conn)) == 1
    try:
        LEDGER.finalize_recorded_season(conn, structure, 73)
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete season handed off")
    conn.close()
    conn = sqlite3.connect(db)
    EVENTS.initialize(conn)
    for index, result in enumerate(results[1:], 2):
        assert record(result) == index
    replay = LEDGER.recorded_results(conn, structure)
    assert len(replay) == 360
    assert set((r["week"], r["game"]) for r in replay) == set(
        (r["week"], r["game"]) for r in results
    )
    next_structure, summary = LEDGER.finalize_recorded_season(conn, structure, 73)
    assert next_structure.season == structure.season + 1
    assert summary["completed_season"] == structure.season
    assert len(summary["exiled_clubs"]) == 8
    assert len(EVENTS.load_verified(conn)) == 360
    conn.close()
    conn = sqlite3.connect(db)
    EVENTS.initialize(conn)
    assert len(LEDGER.recorded_results(conn, structure)) == 360
    other_structure = initial()
    other_structure = type(other_structure)(
        2, other_structure.seeded_divisions, other_structure.ambassadors, other_structure.fixtures
    )
    try:
        LEDGER.recorded_results(conn, other_structure)
    except ValueError:
        pass
    else:
        raise AssertionError("cross-season replay accepted")
    try:
        record(results[-1])
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate result accepted after restart")
    assert len(EVENTS.load_verified(conn)) == 360
    conn.close()
print("OK: 360 fixture-bound finals, duplicate rejection, crash/restart, verified handoff")
