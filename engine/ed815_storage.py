"""SQLite-backed atomic persistence for Edition 8.15 two-club trade snapshots.

This is an isolated reference adapter, NOT wired into the official season runner.
One SQLite BEGIN IMMEDIATE transaction persists the entire revision, reservations,
cap/roster/pick state, and event log. WAL + FULL durability for on-disk files.
"""
from __future__ import annotations
from dataclasses import asdict
from decimal import Decimal
import json
import sqlite3

import ed815_contracts as CONTRACTS
import ed815_roster as ROSTER
import ed815_picks as PICKS
import ed815_compensation as COMP
import ed815_settlement as SETTLEMENT
import ed815_transactions as TX

SCHEMA_VERSION = 1

def _contract(c):
    return dict(player_id=c.player_id,start_year=c.start_year,
                bases=[str(x) for x in c.bases],
                guarantees=[str(x) for x in c.guarantees],bonus=str(c.bonus))

def _ledger(l):
    return dict(club_id=l.club_id,
                contracts={k:_contract(v) for k,v in sorted(l.contracts.items())},
                booked_dead={str(y):str(v) for y,v in l.booked_dead.items()},
                split_used=sorted(l.split_used))

def _roster(r):
    return dict(club_id=r.club_id,
                players={k:asdict(v) for k,v in sorted(r.players.items())})

def _reservation(r):
    if r is None:
        return None
    return dict(token=r.token,based_on=r.based_on,locked_at=r.locked_at.isoformat(),
                season=r.season,post_cut=r.post_cut,require_eleven=r.require_eleven,
                fingerprint=r.fingerprint,
                legs=[dict(from_club=leg.from_club,to_club=leg.to_club,
                           player_ids=list(leg.player_ids),
                           pick_ids=[list(p) for p in leg.pick_ids],
                           comp_pick_ids=[list(p) for p in leg.comp_pick_ids])
                      for leg in r.legs])

def encode(snapshot: SETTLEMENT.Snapshot) -> str:
    clubs={name:dict(ledger=_ledger(c.ledger),roster=_roster(c.roster))
           for name,c in sorted(snapshot.clubs.items())}
    ordinary=[asdict(p) for _,p in sorted(snapshot.ordinary.items(),key=lambda kv:str(kv[0]))]
    compensation=[dict(draft_year=p.draft_year,slot_after_round_seven=p.slot_after_round_seven,
       original_club=p.original_club,owner=p.owner,qualifying_player=p.qualifying_player,
       qualifying_base=str(p.qualifying_base),used=p.used,reserved=p.reserved)
       for p in snapshot.compensation]
    body=dict(schema=SCHEMA_VERSION,revision=snapshot.revision,clubs=clubs,
              ordinary=ordinary,compensation=compensation,
              reservation=_reservation(snapshot.reservation),
              events=[list(e) for e in snapshot.events])
    return json.dumps(body,sort_keys=True,separators=(",",":"),allow_nan=False)

def decode(payload: str) -> SETTLEMENT.Snapshot:
    from datetime import datetime
    raw=json.loads(payload)
    if raw.get("schema")!=SCHEMA_VERSION:
        raise ValueError("unsupported Edition 8.15 snapshot schema")
    clubs={}
    for name,obj in raw["clubs"].items():
        l=obj["ledger"]
        contracts={pid:CONTRACTS.Contract(**c) for pid,c in l["contracts"].items()}
        ledger=CONTRACTS.Ledger(l["club_id"],contracts,
                  {int(y):Decimal(x) for y,x in l["booked_dead"].items()},
                  frozenset(l["split_used"]))
        r=obj["roster"]
        roster=ROSTER.Roster(r["club_id"],
                     {pid:ROSTER.Player(**p) for pid,p in r["players"].items()})
        clubs[name]=TX.Club(ledger,roster)
    ordinary={}
    for p in raw["ordinary"]:
        pick=PICKS.Pick(**p)
        if pick.identity in ordinary:
            raise ValueError("duplicate stored ordinary pick")
        ordinary[pick.identity]=pick
    compensation=tuple(COMP.CompPick(**p) for p in raw["compensation"])
    if len({p.identity for p in compensation})!=len(compensation):
        raise ValueError("duplicate stored compensatory pick")
    r=raw["reservation"]
    pending=None
    if r is not None:
        legs=tuple(TX.TradeLeg(x["from_club"],x["to_club"],tuple(x["player_ids"]),
                tuple(tuple(p) for p in x["pick_ids"]),
                tuple(tuple(p) for p in x["comp_pick_ids"])) for x in r["legs"])
        pending=SETTLEMENT.Reservation(r["token"],r["based_on"],
              datetime.fromisoformat(r["locked_at"]),r["season"],r["post_cut"],
              legs,r["require_eleven"],r["fingerprint"])
    return SETTLEMENT.Snapshot(raw["revision"],clubs,ordinary,compensation,
                              pending,tuple(tuple(e) for e in raw["events"]))

class SQLiteTradeStore:
    def __init__(self, path: str):
        if not path:
            raise ValueError("explicit database path required")
        self.db=sqlite3.connect(path,timeout=30,isolation_level=None)
        self.db.execute("PRAGMA busy_timeout=30000")
        if path != ":memory:":
            self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS ed815_state (
              id INTEGER PRIMARY KEY CHECK(id=1),
              revision INTEGER NOT NULL,
              payload TEXT NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS ed815_commits (
              token TEXT PRIMARY KEY,
              revision INTEGER NOT NULL UNIQUE,
              event TEXT NOT NULL)""")

    def close(self):
        self.db.close()

    def load(self):
        row=self.db.execute("SELECT revision,payload FROM ed815_state WHERE id=1").fetchone()
        if row is None:
            raise ValueError("trade database not initialized")
        result=decode(row[1])
        if result.revision!=row[0]:
            raise ValueError("corrupt revision/payload pair")
        return result

    def initialize(self, snapshot):
        payload=encode(snapshot)
        if snapshot.reservation is not None or snapshot.events or snapshot.revision!=0:
            raise ValueError("initial snapshot must be unreserved at revision zero")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            if self.db.execute("SELECT 1 FROM ed815_state WHERE id=1").fetchone():
                raise ValueError("trade database is already initialized")
            self.db.execute("INSERT INTO ed815_state(id,revision,payload) VALUES(1,?,?)",
                            (snapshot.revision,payload))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def _change(self, expected_revision, operation):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            current=self.load()
            if current.revision!=expected_revision:
                raise ValueError("stale stored revision")
            next_state,event=operation(current)
            payload=encode(next_state)
            count=self.db.execute("""UPDATE ed815_state
                    SET revision=?,payload=? WHERE id=1 AND revision=?""",
                    (next_state.revision,payload,expected_revision)).rowcount
            if count!=1:
                raise ValueError("concurrent revision mismatch")
            if event is not None:
                self.db.execute("INSERT INTO ed815_commits(token,revision,event) VALUES(?,?,?)",
                               (event[1],next_state.revision,json.dumps(event)))
            self.db.execute("COMMIT")
            return next_state
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def reserve(self, legs, *, expected_revision, season, moment, post_cut,
                require_eleven=False):
        captured=[]
        def operation(s):
            staged,token=SETTLEMENT.reserve(s,tuple(legs),season=season,moment=moment,
                                            post_cut=post_cut,
                                            require_eleven=require_eleven)
            captured.append(token)
            return staged,None
        result=self._change(expected_revision,operation)
        return result,captured[0]

    def commit(self, token, *, expected_revision, moment):
        def operation(s):
            after=SETTLEMENT.commit(s,token,moment=moment)
            return after,after.events[-1]
        return self._change(expected_revision,operation)

    def cancel(self, token, *, expected_revision):
        return self._change(expected_revision,
                            lambda s:(SETTLEMENT.cancel(s,token),None))

    def committed_events(self):
        return tuple((token,revision,json.loads(event)) for token,revision,event
                     in self.db.execute("SELECT token,revision,event FROM ed815_commits ORDER BY revision"))
