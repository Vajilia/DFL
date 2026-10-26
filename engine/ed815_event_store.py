"""Edition 8.15 isolated append-only, integrity-checked event ledger.

SQLite is the single writer here. Hash chaining detects accidental/on-disk
corruption, not a malicious writer capable of rewriting the full database.
The live engine and credentialed publication boundary are not connected.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Mapping

RULE = "DFL-Ed8.15"
GENESIS = "0" * 64

def initialize(conn: sqlite3.Connection):
    conn.execute("""CREATE TABLE IF NOT EXISTS ed815_events (
        sequence INTEGER PRIMARY KEY,
        event_id TEXT NOT NULL UNIQUE,
        payload TEXT NOT NULL,
        previous_hash TEXT NOT NULL,
        event_hash TEXT NOT NULL
    )""")
    conn.execute("""CREATE TRIGGER IF NOT EXISTS ed815_no_event_update
        BEFORE UPDATE ON ed815_events BEGIN
            SELECT RAISE(ABORT, 'Edition 8.15 event log is append-only');
        END""")
    conn.execute("""CREATE TRIGGER IF NOT EXISTS ed815_no_event_delete
        BEFORE DELETE ON ed815_events BEGIN
            SELECT RAISE(ABORT, 'Edition 8.15 event log is append-only');
        END""")
    conn.commit()

def _validate(event):
    if not isinstance(event, Mapping):
        raise TypeError("event must be a mapping")
    required = ("id", "simulated_time", "ordering_key", "rule_version",
                "random_key", "kind", "participants", "visibility", "state_changes")
    for key in required:
        if key not in event:
            raise ValueError("missing event field: " + key)
    for key in ("id", "simulated_time", "ordering_key", "random_key", "kind"):
        if not isinstance(event[key], str) or not event[key]:
            raise ValueError("invalid event text field: " + key)
    if event["rule_version"] != RULE:
        raise ValueError("wrong Edition 8.15 rule version")
    if event["visibility"] not in ("public", "private"):
        raise ValueError("invalid event visibility")
    if not isinstance(event["participants"], list) or any(
            not isinstance(p, str) or not p for p in event["participants"]):
        raise ValueError("invalid participant identities")
    if not isinstance(event["state_changes"], dict):
        raise ValueError("state_changes must be a mapping")
    if event["visibility"] == "public":
        if not isinstance(event.get("public_summary"), str) or not event["public_summary"]:
            raise ValueError("public events require a public_summary")
    if "sequence" in event:
        raise ValueError("the event store assigns sequence numbers")
    try:
        return json.dumps(dict(event), sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("event is not canonical JSON") from exc

def _digest(previous, sequence, payload):
    return hashlib.sha256(
        (previous + "\n" + str(sequence) + "\n" + payload).encode("utf-8")
    ).hexdigest()

def append(conn: sqlite3.Connection, event):
    """One event becomes durable with its sequence and hash in one transaction."""
    payload = _validate(event)
    if conn.in_transaction:
        raise ValueError("event append requires ownership of the SQLite transaction")
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT sequence, event_hash FROM ed815_events ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        seq, previous = (row[0] + 1, row[1]) if row else (1, GENESIS)
        digest = _digest(previous, seq, payload)
        conn.execute(
            "INSERT INTO ed815_events(sequence,event_id,payload,previous_hash,event_hash)"
            " VALUES(?,?,?,?,?)",
            (seq, event["id"], payload, previous, digest),
        )
        conn.commit()
        return seq
    except Exception:
        conn.rollback()
        raise

def load_verified(conn: sqlite3.Connection):
    """Verify the entire chain before releasing any event to a viewer adapter."""
    rows = conn.execute(
        "SELECT sequence,event_id,payload,previous_hash,event_hash "
        "FROM ed815_events ORDER BY sequence"
    ).fetchall()
    previous = GENESIS
    out = []
    for expected, (seq, event_id, payload, prev, digest) in enumerate(rows, 1):
        if seq != expected or prev != previous or digest != _digest(prev, seq, payload):
            raise ValueError("event ledger sequence/hash chain mismatch")
        try:
            event = json.loads(payload)
            canonical = _validate(event)
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid stored event payload") from exc
        if canonical != payload or event["id"] != event_id:
            raise ValueError("event ledger payload identity differs")
        event["sequence"] = seq
        out.append(event)
        previous = digest
    return out

def public_cursor(conn: sqlite3.Connection, through_sequence: int):
    if (isinstance(through_sequence, bool) or not isinstance(through_sequence, int)
            or through_sequence < 0):
        raise ValueError("invalid public reveal cursor")
    verified = load_verified(conn)
    return [e for e in verified
            if e["sequence"] <= through_sequence and e["visibility"] == "public"]
