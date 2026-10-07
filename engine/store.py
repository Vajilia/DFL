"""Persistence: a league is saved to one SQLite file, the cards are the save, and it resumes exactly where it stopped.

Everything about a person lives on her own card, so the save is the cards:

  CARDS    one row per person who has ever lived in the league (players, coaches, GMs, owners) and per fanbase and media outlet,
           each a self-contained JSON record: her soul, ratings, trajectory, honors, career, her notes to herself and every
           decision she has made. A player's record also carries her body (position, ratings, age, contract years) so the card
           alone is the whole person. A single card can be exported and later placed in another league (export_card, import_card).
  LEAGUE   a small record: the teams and who sits where, the counters, the league's own flags, the Archive, the choice log, the
           Hall of Fame and the random-number state. Loading rebuilds the league from the cards and this record alone; nothing
           else is needed (proved in check_living.py and check_store.py: a league saved at season 20 and played to 40 equals the
           uninterrupted one, card for card).
  SNAPSHOTS (optional, save(..., snapshot=True)) a whole-league pickle kept per year so that an earlier year can be reopened. A
           snapshot is tied to the code that wrote it; the cards are not. The save is the cards by default.
  TABLES   people, honors and the other readable views of the same data for SQL, rewritten at every save.

The choice log plus the league seed is the canonical record of history; the cards are what each person remembers.

    import store
    store.save("dfl.db", league, rng, year)
    league, rng, year = store.load("dfl.db")                      # rebuilt from the cards
    store.save("dfl.db", league, rng, year, snapshot=True)        # also keep a snapshot of this year
    league, rng, year = store.load("dfl.db", year=20)             # needs that year's snapshot
    text = store.export_card(league, "coach", 17); store.import_card(other_league, text)   # a coach or GM changes leagues
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
CREATE TABLE IF NOT EXISTS cards(kind TEXT, id INTEGER, json TEXT, PRIMARY KEY(kind, id));
CREATE TABLE IF NOT EXISTS league(key TEXT PRIMARY KEY, json TEXT);
CREATE TABLE IF NOT EXISTS people(kind TEXT, id INTEGER, name TEXT, status TEXT, team INTEGER, age INTEGER, trait TEXT,
    soul_pos TEXT, soul_neg TEXT, esteem REAL, standing TEXT, PRIMARY KEY(kind, id));
CREATE TABLE IF NOT EXISTS honors(kind TEXT, id INTEGER, year INTEGER, honor TEXT, team INTEGER, detail TEXT);
CREATE TABLE IF NOT EXISTS archive(seq INTEGER PRIMARY KEY, year INTEGER, event TEXT, json TEXT);
CREATE TABLE IF NOT EXISTS choices(seq INTEGER PRIMARY KEY, id TEXT, year INTEGER, kind TEXT, team INTEGER, actor TEXT, chosen TEXT, driver TEXT,
    status TEXT, reason TEXT, json TEXT);
CREATE TABLE IF NOT EXISTS hall(seq INTEGER PRIMARY KEY, year INTEGER, kind TEXT, id INTEGER, name TEXT, esteem REAL, share REAL, honors TEXT, json TEXT);
CREATE TABLE IF NOT EXISTS teams(id INTEGER PRIMARY KEY, name TEXT, status TEXT, tier INTEGER, strength REAL, coach INTEGER, gm INTEGER, owner INTEGER);
"""
FORMAT = "2"                                   # version of the file layout; a different one is refused rather than guessed at

# what the league record holds beyond the lists of people: every plain attribute of the League, so a new one cannot be forgotten
PLAIN = ("has_rosters", "card_seed", "staff_on", "coaches_on", "fans_on", "interactions_on", "_coach_ids", "_owner_ids", "_gm_ids", "_cand_ids", "_media_ids", "pool")
LISTS = ("teams", "by_id", "free_agents", "new_id", "coaches", "retired_players", "owners", "gms", "archive", "driver", "choice_log", "passed_over",
         "free_coaches", "free_gms", "hall", "fanbases", "media", "refs", "prev_pct")
INT_KEYED = ("forecasts",)                     # card fields whose keys are numbers (JSON turns them into text)


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
        for p in list(t.roster or ()) + list(t.practice_squad) + list(t.ir):
            if p.card is not None and once(p.card):
                yield "player", p.id, p.card, "active", p.team_id
    for p in lg.free_agents:
        if p.card is not None and once(p.card):
            yield "player", p.id, p.card, "free agent", None
    for p in lg.retired_players:
        if p.card is not None and once(p.card):
            yield "player", p.id, p.card, "retired", None


def _json(x) -> str:
    """Canonical text for comparing things (keys sorted)."""
    return json.dumps(x, default=lambda o: dataclasses.asdict(o) if dataclasses.is_dataclass(o) else str(o), sort_keys=True)


def _dump(x) -> str:
    """Text for storing things: keys keep their order, because the order of a card's ratings is part of the card."""
    return json.dumps(x, default=lambda o: dataclasses.asdict(o) if dataclasses.is_dataclass(o) else str(o))


def _plain(card) -> dict:
    return dataclasses.asdict(card)


def _classes() -> dict:
    import cards as C
    import fan_media_cards as FM
    import staff_cards as S
    return {"player": C.PlayerCard, "coach": C.CoachCard, "gm": S.GMCard, "owner": S.OwnerCard, "fans": FM.FanbaseCard, "media": FM.MediaCard}


def _key(kind, card) -> int:
    return {"player": lambda c: c.pid, "coach": lambda c: c.cid, "gm": lambda c: c.gid, "owner": lambda c: c.oid,
            "fans": lambda c: c.team_id, "media": lambda c: c.mid}[kind](card)


def _kind_of(card) -> str:
    for k, cls in _classes().items():
        if type(card) is cls:
            return k
    raise TypeError(f"no card kind for {type(card).__name__}")


def _card_from(kind: str, d: dict):
    d = dict(d)
    for f in INT_KEYED:
        if f in d:
            d[f] = {int(k): v for k, v in d[f].items()}
    return _classes()[kind](**d)


def _body(p) -> dict:
    """A player's body: everything the engine keeps about her that is not on her card."""
    return {f.name: getattr(p, f.name) for f in dataclasses.fields(p) if f.name not in ("card", "ovr")}


def _registry(lg) -> dict:
    """Every card in the league once, keyed (kind, id). Two different cards with one key would lose someone, so that is an error."""
    reg = {}

    def add(kind, card):
        k = (kind, _key(kind, card))
        if k in reg and reg[k] is not card:
            raise ValueError(f"two different {kind} cards share the id {k[1]}")
        reg[k] = card

    for c in list(lg.coaches) + list(lg.free_coaches) + [t.coach for t in lg.teams if t.coach] + [c for c in lg.passed_over if hasattr(c, "cid")]:
        add("coach", c)
    for g in list(lg.gms) + list(lg.free_gms) + [t.gm for t in lg.teams if t.gm] + [c for c in lg.passed_over if hasattr(c, "gid")]:
        add("gm", g)
    for o in list(lg.owners) + [t.owner for t in lg.teams if t.owner]:
        add("owner", o)
    for f in lg.fanbases:
        add("fans", f)
    for m in lg.media:
        add("media", m)
    return reg


def _players(lg):
    """(player, where) for every player who has ever been in the league: on a team, a free agent, or retired."""
    for t in lg.teams:
        for p in list(t.roster or ()) + list(t.practice_squad) + list(t.ir):
            yield p
    yield from lg.free_agents
    yield from lg.retired_players


def _league_record(lg, rng, year) -> dict:
    unknown = set(vars(lg)) - set(PLAIN) - set(LISTS)
    if unknown:
        raise ValueError(f"the league has state the save does not know about: {sorted(unknown)} (add it to store.PLAIN or store.LISTS)")
    st = rng.getstate()
    rec = {"year": year, "rng": [st[0], list(st[1]), st[2]], "next_id": lg.new_id.next, "refs": lg.refs, "prev_pct": {str(k): v for k, v in lg.prev_pct.items()}}
    rec.update({k: getattr(lg, k) for k in PLAIN})
    rec["teams"] = [dict(id=t.id, name=t.name, conf=t.conf, div=t.div, status=t.status, tier=t.tier, strength=t.strength, bank=t.bank,
                         roster=None if t.roster is None else [p.id for p in t.roster],
                         practice_squad=[p.id for p in t.practice_squad], ir=[p.id for p in t.ir], ir_returns=t.ir_returns,
                         dead_now=t.dead_now, dead_next=t.dead_next, designations=t.designations, cash=t.cash, topup=t.topup, fund_cash=t.fund_cash,
                         coach=t.coach.cid if t.coach else None, owner=t.owner.oid if t.owner else None, gm=t.gm.gid if t.gm else None,
                         fans=t.fans.team_id if t.fans else None) for t in lg.teams]
    rec["free_agents"] = [p.id for p in lg.free_agents]
    rec["retired_players"] = [p.id for p in lg.retired_players]
    rec["coaches"] = [c.cid for c in lg.coaches]
    rec["gms"] = [g.gid for g in lg.gms]
    rec["owners"] = [o.oid for o in lg.owners]
    rec["free_coaches"] = [c.cid for c in lg.free_coaches]
    rec["free_gms"] = [g.gid for g in lg.free_gms]
    rec["passed_over"] = [["coach", c.cid] if hasattr(c, "cid") else ["gm", c.gid] for c in lg.passed_over]
    rec["fanbases"] = [f.team_id for f in lg.fanbases]
    rec["media"] = [m.mid for m in lg.media]
    return rec


def _write_tables(db: sqlite3.Connection, lg, rng, year: int):
    for tbl in ("people", "cards", "honors", "archive", "choices", "hall", "teams", "league"):
        db.execute(f"DELETE FROM {tbl}")
    people, cards, honors = [], [], []
    reg = _registry(lg)
    for (kind, ident), card in reg.items():
        if kind in ("fans", "media"):
            cards.append((kind, ident, _dump({"card": _plain(card)})))
            continue
        status = {"coach": lambda c: "retired" if c.retired else "coaching" if c.team_id is not None else "between jobs",
                  "gm": lambda c: c.status, "owner": lambda c: c.status}[kind](card)
        people.append((kind, ident, card.name, status, card.team_id, card.age, card.trait, card.soul_pos, card.soul_neg, card.esteem, card.standing))
        cards.append((kind, ident, _dump({"card": _plain(card)})))
    for p in _players(lg):
        card = p.card
        if card is None:
            raise ValueError(f"player {p.id} has no card")
        status = "retired" if p in lg.retired_players else "free agent" if p.team_id is None else "active"
        people.append(("player", p.id, card.name, status, p.team_id, p.age, card.trait, card.archetype_pos, card.archetype_neg, card.esteem, card.standing))
        cards.append(("player", p.id, _dump({"card": _plain(card), "body": _body(p)})))
    for (kind, ident, text) in cards:
        rec = json.loads(text)
        for h in rec["card"].get("honors", ()):
            honors.append((kind, ident, h["year"], h["honor"], h.get("team"), _dump({k: v for k, v in h.items() if k not in ("year", "honor", "team")})))
    db.executemany("INSERT INTO people VALUES(?,?,?,?,?,?,?,?,?,?,?)", people)
    db.executemany("INSERT INTO cards VALUES(?,?,?)", cards)
    db.executemany("INSERT INTO honors VALUES(?,?,?,?,?,?)", honors)
    db.execute("INSERT INTO league VALUES('record', ?)", (_dump(_league_record(lg, rng, year)),))
    db.executemany("INSERT INTO archive VALUES(?,?,?,?)", [(i, e["year"], e["event"], _dump(e)) for i, e in enumerate(lg.archive)])
    db.executemany("INSERT INTO choices VALUES(?,?,?,?,?,?,?,?,?,?,?)", [(i, e["id"], e["year"], e["kind"], e["team"], e["actor"], e["chosen"], e["driver"],
                                                                         e["status"], e["reason"], _dump(e)) for i, e in enumerate(lg.choice_log)])
    db.executemany("INSERT INTO hall VALUES(?,?,?,?,?,?,?,?,?)", [(i, h["year"], h["kind"], h["id"], h["name"], h["esteem"], h["share"], _dump(h["honors"]), _dump(h))
                                                                  for i, h in enumerate(lg.hall)])
    db.executemany("INSERT INTO teams VALUES(?,?,?,?,?,?,?,?)", [(t.id, t.name, t.status, t.tier, t.strength,
                                                                 t.coach.cid if t.coach else None, t.gm.gid if t.gm else None, t.owner.oid if t.owner else None)
                                                                for t in lg.teams])


def save(path: str, lg, rng: random.Random, year: int, note: str = "", snapshot: bool = False) -> int:
    """Write the league after `year`: every card, the league record, and the readable tables. With snapshot=True a whole-league
    snapshot of this year is kept as well. Returns the size of what was written in bytes (the snapshot's, if one was taken).
    The driver (who makes the choices) is a live object and is not saved; give the loaded league a driver again to continue
    with agents."""
    size = 0
    db = sqlite3.connect(path)
    try:
        db.executescript(SCHEMA)
        have = db.execute("SELECT value FROM meta WHERE key='format'").fetchone()
        if have and have[0] != FORMAT:
            raise ValueError(f"{path} is a version {have[0]} save; this code writes version {FORMAT}")
        db.execute("INSERT OR REPLACE INTO meta VALUES('format', ?)", (FORMAT,))
        if snapshot:
            driver, lg.driver = lg.driver, None
            try:
                blob = pickle.dumps({"league": lg, "rng_state": rng.getstate(), "year": year}, protocol=pickle.HIGHEST_PROTOCOL)
            finally:
                lg.driver = driver
            db.execute("INSERT OR REPLACE INTO snapshots VALUES(?,?,?,?)", (year, time.strftime("%Y-%m-%dT%H:%M:%S"), _code_version(), blob))
            size = len(blob)
        db.execute("INSERT OR REPLACE INTO meta VALUES('latest_year', ?)", (str(year),))
        db.execute("INSERT OR REPLACE INTO meta VALUES('card_seed', ?)", (str(lg.card_seed),))
        if note:
            db.execute("INSERT OR REPLACE INTO meta VALUES('note', ?)", (note,))
        _write_tables(db, lg, rng, year)
        db.commit()
    finally:
        db.close()
    return size or os.path.getsize(path)


def _rebuild(db: sqlite3.Connection):
    from league import League, Team
    from players import IdSource, Player
    row = db.execute("SELECT value FROM meta WHERE key='format'").fetchone()
    if not row or row[0] != FORMAT:
        raise ValueError(f"not a version {FORMAT} save")
    rec = json.loads(db.execute("SELECT json FROM league WHERE key='record'").fetchone()[0])
    cards = {(k, i): json.loads(j) for k, i, j in db.execute("SELECT kind, id, json FROM cards")}
    made = {}

    def card(kind, ident):
        if (kind, ident) not in made:
            made[(kind, ident)] = _card_from(kind, cards[(kind, ident)]["card"])
        return made[(kind, ident)]

    players = {}

    def player(pid):
        if pid not in players:
            d = cards[("player", pid)]
            p = Player(**d["body"])
            p.card = card("player", pid)
            players[pid] = p
        return players[pid]

    teams = []
    for t in rec["teams"]:
        tm = Team(id=t["id"], name=t["name"], conf=t["conf"], div=t["div"], status=t["status"], tier=t["tier"], strength=t["strength"])
        tm.bank = t["bank"]
        tm.roster = None if t["roster"] is None else [player(i) for i in t["roster"]]
        tm.practice_squad = [player(i) for i in t.get("practice_squad", ())]
        tm.ir = [player(i) for i in t.get("ir", ())]
        tm.ir_returns = t.get("ir_returns", 0)
        tm.dead_now, tm.dead_next, tm.designations = t.get("dead_now", 0.0), t.get("dead_next", 0.0), t.get("designations", 0)
        tm.cash, tm.topup, tm.fund_cash = list(t.get("cash", ())), list(t.get("topup", ())), t.get("fund_cash", 0.0)
        tm.coach = card("coach", t["coach"]) if t["coach"] is not None else None
        tm.owner = card("owner", t["owner"]) if t["owner"] is not None else None
        tm.gm = card("gm", t["gm"]) if t["gm"] is not None else None
        tm.fans = card("fans", t["fans"]) if t["fans"] is not None else None
        teams.append(tm)
    lg = League(teams)
    for k in PLAIN:
        setattr(lg, k, rec[k])
    lg.new_id = IdSource(rec["next_id"])
    lg.free_agents = [player(i) for i in rec["free_agents"]]
    lg.retired_players = [player(i) for i in rec["retired_players"]]
    lg.coaches = [card("coach", i) for i in rec["coaches"]]
    lg.gms = [card("gm", i) for i in rec["gms"]]
    lg.owners = [card("owner", i) for i in rec["owners"]]
    lg.free_coaches = [card("coach", i) for i in rec["free_coaches"]]
    lg.free_gms = [card("gm", i) for i in rec["free_gms"]]
    lg.passed_over = [card(k, i) for k, i in rec["passed_over"]]
    lg.fanbases = [card("fans", i) for i in rec["fanbases"]]
    lg.media = [card("media", i) for i in rec["media"]]
    lg.refs = rec["refs"]
    lg.prev_pct = {int(k): v for k, v in rec["prev_pct"].items()}
    lg.archive = [json.loads(j) for (j,) in db.execute("SELECT json FROM archive ORDER BY seq")]
    lg.choice_log = [json.loads(j) for (j,) in db.execute("SELECT json FROM choices ORDER BY seq")]
    lg.hall = [json.loads(j) for (j,) in db.execute("SELECT json FROM hall ORDER BY seq")]
    rng = random.Random()
    st = rec["rng"]
    rng.setstate((st[0], tuple(st[1]), st[2]))
    return lg, rng, rec["year"]


def load(path: str, year: int = None) -> Tuple[object, random.Random, int]:
    """Open a saved league. By default it is rebuilt from the cards (the latest save); year=N opens that year's snapshot instead,
    if one was kept. Returns (league, rng, year)."""
    db = sqlite3.connect(path)
    try:
        if year is None:
            return _rebuild(db)
        row = db.execute("SELECT year, blob FROM snapshots WHERE year=?", (year,)).fetchone()
        if row is None:
            raise KeyError(f"no snapshot for year {year} in {path} (save with snapshot=True to keep one)")
    finally:
        db.close()
    state = pickle.loads(row[1])
    rng = random.Random()
    rng.setstate(state["rng_state"])
    return state["league"], rng, state["year"]


def years(path: str) -> List[int]:
    """The years that can be reopened: the latest save and every kept snapshot."""
    db = sqlite3.connect(path)
    try:
        ys = {r[0] for r in db.execute("SELECT year FROM snapshots")}
        latest = db.execute("SELECT value FROM meta WHERE key='latest_year'").fetchone()
        if latest:
            ys.add(int(latest[0]))
        return sorted(ys)
    finally:
        db.close()


def export_card(lg, kind: str, ident: int) -> str:
    """One person as self-contained JSON text (her card, and for a player her body)."""
    if kind == "player":
        for p in _players(lg):
            if p.id == ident:
                return _dump({"kind": "player", "card": _plain(p.card), "body": _body(p)})
        raise KeyError(f"no player {ident}")
    card = _registry(lg).get((kind, ident))
    if card is None:
        raise KeyError(f"no {kind} {ident}")
    return _dump({"kind": kind, "card": _plain(card)})


def import_card(lg, text: str):
    """Place an exported coach or GM in this league's pool of people between jobs, under a fresh id. She keeps everything else:
    her soul, ratings, trajectory, honors, career and notes. She is hired like anyone else, when an owner's list includes her."""
    rec = json.loads(text)
    kind = rec["kind"]
    if kind not in ("coach", "gm"):
        raise ValueError("only a coach or a GM can change leagues")
    c = _card_from(kind, rec["card"])
    c.team_id = None
    c.seasons_with_team = 0
    c.idle_years = 0
    c.heat = 0.0
    c.ref = None
    if kind == "coach":
        c.cid = lg.new_coach_id()
        c.retired = False
        lg.coaches.append(c)
        lg.free_coaches.append(c)
    else:
        c.gid = lg.new_gm_id()
        c.status = "fired"
        lg.gms.append(c)
        lg.free_gms.append(c)
    c.career.append({"year": 0, "event": "joined_league"})
    return c
