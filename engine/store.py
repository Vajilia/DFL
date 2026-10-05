"""Persistence (Phase 4c): a league is saved to one SQLite file and can be resumed exactly where it stopped.

Two things are stored, for two different jobs:

  SNAPSHOTS  the whole league (every card, the Archive, the choice log, the engine's random-number state) as one blob per saved
             year. Loading a snapshot and playing on gives EXACTLY the league that playing without stopping would have (proved in
             check_living.py). A snapshot is tied to the code that wrote it (the code version is stored beside it): it is for
             resuming, not for archives that must outlive the code.
  TABLES     the same league written out as plain rows anyone can query with SQL, human-readable and independent of the code:
             people (every player, coach, GM and owner who has ever lived, with their soul, standing and esteem), their full
             cards as JSON, honors, the Archive, the choice log, the Hall of Fame, fanbases and media outlets. These are rewritten
             at every save, so they always describe the latest saved state.

The choice log plus the league seed is the canonical record of history; the tables are a convenient view of it.

    import store
    store.save("dfl.db", league, rng, year)
    league, rng, year = store.load("dfl.db")           # the latest snapshot, or load("dfl.db", year=20)
"""
from __future__ import annotations

import dataclasses
import json
import os
import pickle
import random
import sqlite3
import subprocess
import time
from typing import List, Tuple

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS snapshots(year INTEGER PRIMARY KEY, saved_at TEXT, code_version TEXT, blob BLOB);
CREATE TABLE IF NOT EXISTS people(kind TEXT, id INTEGER, name TEXT, status TEXT, team INTEGER, age INTEGER, trait TEXT,
    soul_pos TEXT, soul_neg TEXT, esteem REAL, standing TEXT, PRIMARY KEY(kind, id));
CREATE TABLE IF NOT EXISTS cards(kind TEXT, id INTEGER, json TEXT, PRIMARY KEY(kind, id));
CREATE TABLE IF NOT EXISTS honors(kind TEXT, id INTEGER, year INTEGER, honor TEXT, team INTEGER, detail TEXT);
CREATE TABLE IF NOT EXISTS archive(seq INTEGER PRIMARY KEY, year INTEGER, event TEXT, json TEXT);
CREATE TABLE IF NOT EXISTS choices(id TEXT PRIMARY KEY, year INTEGER, kind TEXT, team INTEGER, actor TEXT, chosen TEXT, driver TEXT,
    status TEXT, reason TEXT, json TEXT);
CREATE TABLE IF NOT EXISTS hall(seq INTEGER PRIMARY KEY, year INTEGER, kind TEXT, id INTEGER, name TEXT, esteem REAL, share REAL, honors TEXT);
CREATE TABLE IF NOT EXISTS teams(id INTEGER PRIMARY KEY, name TEXT, status TEXT, tier INTEGER, strength REAL, coach INTEGER, gm INTEGER, owner INTEGER);
"""


def _code_version() -> str:
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=here, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "unknown"


def _everyone(lg):
    """(kind, id, card, status, team) for every person who has ever lived in the league, once each."""
    seen = set()

    def once(card):
        if id(card) in seen:
            return False
        seen.add(id(card))
        return True

    for c in lg.coaches:
        if once(c):
            yield "coach", c.cid, c, ("retired" if c.retired else "coaching" if c.team_id is not None else "between jobs"), c.team_id
    for c in lg.passed_over:
        if hasattr(c, "cid") and once(c):
            yield "coach", c.cid, c, ("retired" if c.retired else "coaching" if c.team_id is not None else "between jobs"), c.team_id
    for g in lg.gms:
        if once(g):
            yield "gm", g.gid, g, g.status, g.team_id
    for g in lg.passed_over:
        if hasattr(g, "gid") and once(g):
            yield "gm", g.gid, g, g.status, g.team_id
    for o in lg.owners:
        if once(o):
            yield "owner", o.oid, o, o.status, o.team_id
    for t in lg.teams:
        for p in t.roster or ():
            if p.card is not None and once(p.card):
                yield "player", p.id, p.card, "active", p.team_id
    for p in lg.free_agents:
        if p.card is not None and once(p.card):
            yield "player", p.id, p.card, "free agent", None
    for p in lg.retired_players:
        if p.card is not None and once(p.card):
            yield "player", p.id, p.card, "retired", None


def _json(x) -> str:
    return json.dumps(x, default=lambda o: dataclasses.asdict(o) if dataclasses.is_dataclass(o) else str(o), sort_keys=True)


def _write_tables(db: sqlite3.Connection, lg, year: int):
    for tbl in ("people", "cards", "honors", "archive", "choices", "hall", "teams"):
        db.execute(f"DELETE FROM {tbl}")
    people, cards, honors = [], [], []
    for kind, ident, card, status, team in _everyone(lg):
        people.append((kind, ident, card.name, status, team, getattr(card, "age", None), getattr(card, "trait", None),
                       getattr(card, "soul_pos", None) or getattr(card, "archetype_pos", None),
                       getattr(card, "soul_neg", None) or getattr(card, "archetype_neg", None),
                       getattr(card, "esteem", 0.0), getattr(card, "standing", "")))
        cards.append((kind, ident, _json(card)))
        for h in getattr(card, "honors", ()):
            honors.append((kind, ident, h["year"], h["honor"], h.get("team"), _json({k: v for k, v in h.items() if k not in ("year", "honor", "team")})))
    db.executemany("INSERT OR REPLACE INTO people VALUES(?,?,?,?,?,?,?,?,?,?,?)", people)
    db.executemany("INSERT OR REPLACE INTO cards VALUES(?,?,?)", cards)
    db.executemany("INSERT INTO honors VALUES(?,?,?,?,?,?)", honors)
    for i, e in enumerate(lg.fanbases):
        db.execute("INSERT OR REPLACE INTO cards VALUES(?,?,?)", ("fans", e.team_id, _json(e)))
    for m in lg.media:
        db.execute("INSERT OR REPLACE INTO cards VALUES(?,?,?)", ("media", m.mid, _json(m)))
    db.executemany("INSERT INTO archive VALUES(?,?,?,?)", [(i, e["year"], e["event"], _json(e)) for i, e in enumerate(lg.archive)])
    db.executemany("INSERT INTO choices VALUES(?,?,?,?,?,?,?,?,?,?)", [(e["id"], e["year"], e["kind"], e["team"], e["actor"], e["chosen"], e["driver"],
                                                                       e["status"], e["reason"], _json(e)) for e in lg.choice_log])
    db.executemany("INSERT INTO hall VALUES(?,?,?,?,?,?,?,?)", [(i, h["year"], h["kind"], h["id"], h["name"], h["esteem"], h["share"], _json(h["honors"]))
                                                                for i, h in enumerate(lg.hall)])
    db.executemany("INSERT INTO teams VALUES(?,?,?,?,?,?,?,?)", [(t.id, t.name, t.status, t.tier, t.strength,
                                                                 t.coach.cid if t.coach else None, t.gm.gid if t.gm else None, t.owner.oid if t.owner else None)
                                                                for t in lg.teams])


def save(path: str, lg, rng: random.Random, year: int, note: str = "") -> int:
    """Write a snapshot of the league after `year` and refresh the queryable tables. Returns the snapshot's size in bytes.
    The driver (who makes the choices) is a live object and is not saved; give the loaded league a driver again to continue
    with agents."""
    driver, lg.driver = lg.driver, None
    try:
        blob = pickle.dumps({"league": lg, "rng_state": rng.getstate(), "year": year}, protocol=pickle.HIGHEST_PROTOCOL)
    finally:
        lg.driver = driver
    db = sqlite3.connect(path)
    try:
        db.executescript(SCHEMA)
        db.execute("INSERT OR REPLACE INTO snapshots VALUES(?,?,?,?)", (year, time.strftime("%Y-%m-%dT%H:%M:%S"), _code_version(), blob))
        db.execute("INSERT OR REPLACE INTO meta VALUES('latest_year', ?)", (str(year),))
        db.execute("INSERT OR REPLACE INTO meta VALUES('card_seed', ?)", (str(lg.card_seed),))
        if note:
            db.execute("INSERT OR REPLACE INTO meta VALUES('note', ?)", (note,))
        _write_tables(db, lg, year)
        db.commit()
    finally:
        db.close()
    return len(blob)


def load(path: str, year: int = None) -> Tuple[object, random.Random, int]:
    """Load a snapshot (the latest by default). Returns (league, rng, year)."""
    db = sqlite3.connect(path)
    try:
        if year is None:
            row = db.execute("SELECT year, blob FROM snapshots ORDER BY year DESC LIMIT 1").fetchone()
        else:
            row = db.execute("SELECT year, blob FROM snapshots WHERE year=?", (year,)).fetchone()
        if row is None:
            raise KeyError(f"no snapshot{'' if year is None else ' for year ' + str(year)} in {path}")
    finally:
        db.close()
    state = pickle.loads(row[1])
    rng = random.Random()
    rng.setstate(state["rng_state"])
    return state["league"], rng, state["year"]


def years(path: str) -> List[int]:
    db = sqlite3.connect(path)
    try:
        return [r[0] for r in db.execute("SELECT year FROM snapshots ORDER BY year")]
    finally:
        db.close()
