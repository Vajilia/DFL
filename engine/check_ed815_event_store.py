"""File-backed Edition 8.15 event chain, crash/reopen and public-reveal tests."""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import ed815_event_store as STORE
import ed815_site_preview as SITE

document = SITE.SOURCE.read_text(encoding="utf-8")
_, fixtures = SITE.founding_tables(document)
one, two = fixtures[:2]

def event(eid, visibility="public", fixture=one, score=(21, 17)):
    return {
        "id": eid,
        "simulated_time": "2000-07-01T20:00:00Z",
        "ordering_key": "regular:1:1:final",
        "rule_version": "DFL-Ed8.15",
        "random_key": "SECRET_RANDOM_KEY",
        "kind": "game_final",
        "participants": [fixture["home"], fixture["away"]],
        "visibility": visibility,
        "public_summary": "The game ended",
        "state_changes": {"SECRET_INTERNAL_STATE": 42},
        "week": int(fixture["week"]),
        "game": int(fixture["game"]),
        "home": fixture["home"], "away": fixture["away"],
        "home_score": score[0], "away_score": score[1],
    }

with tempfile.TemporaryDirectory() as td:
    db = Path(td) / "events.sqlite"
    conn = sqlite3.connect(db)
    STORE.initialize(conn)
    assert STORE.append(conn, event("e-1")) == 1
    assert STORE.append(conn, event("e-private", "private", two, (999, 888))) == 2
    conn.close()

    reopened = sqlite3.connect(db)
    STORE.initialize(reopened)
    assert len(STORE.load_verified(reopened)) == 2
    assert STORE.append(reopened, event("e-3", "public", two, (14, 10))) == 3
    before = STORE.load_verified(reopened)
    assert [e["sequence"] for e in before] == [1, 2, 3]
    assert [e["id"] for e in STORE.public_cursor(reopened, 2)] == ["e-1"]
    assert [e["id"] for e in STORE.public_cursor(reopened, 3)] == ["e-1", "e-3"]
    assert not STORE.public_cursor(reopened, 0)

    h1 = SITE.render_html(document, events=before, revealed_through_sequence=1)
    h2 = SITE.render_html(document, events=before, revealed_through_sequence=2)
    h3 = SITE.render_html(document, events=before, revealed_through_sequence=3)
    assert "17–21" in h1 and "14–10" not in h1
    assert "999" not in h2 and "888" not in h2
    assert "10–14" in h3
    assert "SECRET_INTERNAL_STATE" not in h3
    assert "SECRET_RANDOM_KEY" not in h3

    try:
        STORE.append(reopened, event("e-1"))
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("duplicate event ID committed")
    assert STORE.load_verified(reopened) == before
    try:
        reopened.execute("DELETE FROM ed815_events WHERE sequence=1")
    except sqlite3.DatabaseError:
        pass
    else:
        raise AssertionError("event deletion was permitted")
    reopened.rollback()
    try:
        reopened.execute("UPDATE ed815_events SET payload='tampered' WHERE sequence=1")
    except sqlite3.DatabaseError:
        pass
    else:
        raise AssertionError("event mutation was permitted")
    reopened.rollback()
    try:
        STORE.append(reopened, {**event("bad"), "rule_version": "old"})
    except ValueError:
        pass
    else:
        raise AssertionError("old rule version was accepted")
    assert STORE.load_verified(reopened) == before

    # Simulate disk corruption after deliberately removing the temp DB trigger.
    reopened.execute("DROP TRIGGER ed815_no_event_update")
    reopened.execute("UPDATE ed815_events SET payload='{}' WHERE sequence=1")
    reopened.commit()
    try:
        STORE.load_verified(reopened)
    except ValueError:
        pass
    else:
        raise AssertionError("tampered historical payload passed chain verification")
    reopened.close()
print("OK: immutable SQLite event chain, verified reopen, and no private/future public leakage")
