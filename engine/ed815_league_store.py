"""Edition 8.15 leaguewide 48-club SQLite trade reference.

A single SQLite transaction changes two participating clubs, global draft-pick
ownership and one event while preserving the other 46 clubs byte-for-byte.
The protocol intentionally permits only one pending league trade at a time:
safe serial operation first; scalable concurrent reservations are future work.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict,replace
from datetime import datetime
from decimal import Decimal
import hashlib
import json
import sqlite3

import ed815_storage as STORE
import ed815_transactions as TX
import ed815_picks as PICKS
import ed815_compensation as COMP

SCHEMA=1
CLUBS=48

@dataclass(frozen=True)
class PendingTrade:
    token: str
    clubs: tuple[str,str]
    legs: tuple[TX.TradeLeg,...]
    season: int
    post_cut: bool
    require_eleven: bool

@dataclass(frozen=True)
class League:
    revision: int
    clubs: dict
    ordinary: dict
    compensation: tuple=()
    pending: PendingTrade|None=None
    events: tuple=()

    def __post_init__(self):
        if self.revision<0 or len(self.clubs)!=CLUBS:
            raise ValueError("league must have 48 clubs and nonnegative revision")
        if any(club.ledger.club_id!=name for name,club in self.clubs.items()):
            raise ValueError("club map identity mismatch")
        seen=set()
        for club in self.clubs.values():
            for player in club.roster.players:
                if player in seen:
                    raise ValueError("player appears on multiple club rosters")
                seen.add(player)
        if any(p.owner not in self.clubs for p in self.ordinary.values()):
            raise ValueError("ordinary pick owner outside league")
        if any(p.owner not in self.clubs for p in self.compensation):
            raise ValueError("compensation owner outside league")

def _leg(leg):
    return dict(from_club=leg.from_club,to_club=leg.to_club,
       player_ids=list(leg.player_ids),
       pick_ids=[list(x) for x in leg.pick_ids],
       comp_pick_ids=[list(x) for x in leg.comp_pick_ids])

def _parse_leg(v):
    return TX.TradeLeg(v["from_club"],v["to_club"],tuple(v["player_ids"]),
       tuple(tuple(x) for x in v["pick_ids"]),
       tuple(tuple(x) for x in v["comp_pick_ids"]))

def encode(state: League):
    pending=None if state.pending is None else dict(
        token=state.pending.token,clubs=list(state.pending.clubs),
        legs=[_leg(x) for x in state.pending.legs],season=state.pending.season,
        post_cut=state.pending.post_cut,require_eleven=state.pending.require_eleven)
    payload=dict(schema=SCHEMA,revision=state.revision,
        clubs={k:STORE.encode_club(v) for k,v in sorted(state.clubs.items())},
        ordinary=[asdict(p) for p in sorted(state.ordinary.values(),key=lambda x:str(x.identity))],
        compensation=[{**asdict(p),"qualifying_base":str(p.qualifying_base)}
                      for p in state.compensation],
        pending=pending,events=[list(x) for x in state.events])
    return json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False)

def _tuple_tree(value):
    if isinstance(value,list):
        return tuple(_tuple_tree(x) for x in value)
    return value

def decode(payload):
    raw=json.loads(payload)
    if raw.get("schema")!=SCHEMA:
        raise ValueError("unsupported league snapshot schema")
    clubs={k:STORE.decode_club(v) for k,v in raw["clubs"].items()}
    ordinary={}
    for o in raw["ordinary"]:
        p=PICKS.Pick(**o)
        if p.identity in ordinary:
            raise ValueError("duplicate ordinary pick identity")
        ordinary[p.identity]=p
    compensation=tuple(COMP.CompPick(**{**c,"qualifying_base":Decimal(c["qualifying_base"])})
                       for c in raw["compensation"])
    if len({p.identity for p in compensation})!=len(compensation):
        raise ValueError("duplicate compensation identity")
    p=raw["pending"]
    pending=None if p is None else PendingTrade(p["token"],tuple(p["clubs"]),
                tuple(_parse_leg(x) for x in p["legs"]),
                p["season"],p["post_cut"],p["require_eleven"])
    return League(raw["revision"],clubs,ordinary,compensation,pending,
                  tuple(_tuple_tree(x) for x in raw["events"]))

class LeagueTradeStore:
    def __init__(self,path):
        if not path:
            raise ValueError("explicit database path required")
        self.db=sqlite3.connect(path,timeout=30,isolation_level=None)
        self.db.execute("PRAGMA busy_timeout=30000")
        if path!=":memory:":
            self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS ed815_league (
            id INTEGER PRIMARY KEY CHECK(id=1),revision INTEGER NOT NULL,payload TEXT NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS ed815_league_events (
            token TEXT PRIMARY KEY,revision INTEGER UNIQUE NOT NULL,event TEXT NOT NULL)""")

    def close(self):
        self.db.close()

    def load(self):
        row=self.db.execute("SELECT revision,payload FROM ed815_league WHERE id=1").fetchone()
        if row is None:
            raise ValueError("league storage not initialized")
        state=decode(row[1])
        if state.revision!=row[0]:
            raise ValueError("corrupt league revision")
        return state

    def initialize(self,state):
        if state.revision!=0 or state.pending is not None or state.events:
            raise ValueError("initial league state must be fresh")
        payload=encode(state)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.db.execute("INSERT INTO ed815_league(id,revision,payload) VALUES(1,?,?)",
                            (0,payload))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def _atomic(self,expected_revision,transform):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            before=self.load()
            if before.revision!=expected_revision:
                raise ValueError("stale league revision")
            after,event=transform(before)
            n=self.db.execute("""UPDATE ed815_league SET revision=?,payload=?
                  WHERE id=1 AND revision=?""",
                (after.revision,encode(after),expected_revision)).rowcount
            if n!=1:
                raise ValueError("concurrent league revision mismatch")
            if event is not None:
                self.db.execute("""INSERT INTO ed815_league_events(token,revision,event)
                      VALUES(?,?,?)""",(event[1],after.revision,json.dumps(event)))
            self.db.execute("COMMIT")
            return after
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def reserve(self,legs,*,expected_revision,season,moment:datetime,
                post_cut,require_eleven=False):
        legs=tuple(legs)
        def transform(s):
            if s.pending is not None:
                raise ValueError("league has a pending trade")
            names=tuple(sorted({n for x in legs for n in (x.from_club,x.to_club)}))
            if len(names)!=2 or any(n not in s.clubs for n in names):
                raise ValueError("trade requires two member clubs")
            pair={n:s.clubs[n] for n in names}
            TX.propose_trade(pair,s.ordinary,legs,season=season,moment=moment,
                             post_cut=post_cut,compensation=s.compensation,
                             require_eleven=require_eleven)
            basis=hashlib.sha256(encode(s).encode()).hexdigest()
            token=hashlib.sha256(repr((basis,legs,season,moment.isoformat(),
                    post_cut,require_eleven)).encode()).hexdigest()
            pending=PendingTrade(token,names,legs,season,post_cut,require_eleven)
            return replace(s,revision=s.revision+1,pending=pending),None
        outcome=self._atomic(expected_revision,transform)
        return outcome,outcome.pending

    def commit(self,pending:PendingTrade,*,expected_revision,moment:datetime):
        def transform(s):
            if s.pending!=pending:
                raise ValueError("trade reservation not held")
            pair={n:s.clubs[n] for n in pending.clubs}
            results,picks,comp=TX.propose_trade(pair,s.ordinary,pending.legs,
                          season=pending.season,moment=moment,
                          post_cut=pending.post_cut,compensation=s.compensation,
                          require_eleven=pending.require_eleven)
            updated=dict(s.clubs)
            updated.update(results)
            event=("trade",pending.token,pending.season,moment.isoformat(),
                   pending.clubs)
            return League(s.revision+1,updated,picks,comp,None,s.events+(event,)),event
        return self._atomic(expected_revision,transform)

    def cancel(self,pending:PendingTrade,*,expected_revision):
        def transform(s):
            if s.pending!=pending:
                raise ValueError("trade reservation not held")
            return replace(s,revision=s.revision+1,pending=None),None
        return self._atomic(expected_revision,transform)

    def committed_events(self):
        return tuple((token,revision,json.loads(event)) for token,revision,event
              in self.db.execute("SELECT token,revision,event FROM ed815_league_events ORDER BY revision"))
