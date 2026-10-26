"""Edition 8.15 full structural season -> financial roster handoff checks."""
from datetime import datetime,timezone
from decimal import Decimal
from dataclasses import replace
import hashlib
import sqlite3
import ed815_calendar as CAL
import ed815_cycle as CYCLE
import ed815_contracts as CONTRACTS
import ed815_roster as R
import ed815_transactions as T
import ed815_league_store as L
import ed815_picks as PICKS
import ed815_handoff as H

seeded={d:[f"{i}/{r}" for r in range(1,6)]
        for i,d in enumerate(CAL.DIVISION_ORDER)}
ambassadors={d:f"{i}/amb" for i,d in enumerate(CAL.DIVISION_ORDER)}
structure=CYCLE.build_structure(1,seeded,ambassadors)
clubs={}
for i,club_id in enumerate([cid for v in seeded.values() for cid in v]+list(ambassadors.values())):
    contracts={};roster={}
    for n in range(11):
        pid=f"id{i}-P{n}"
        # Player zero remains on a two-year deal; other ten expire.
        bases=(Decimal(10),Decimal(10)) if n==0 else (Decimal(10),)
        guarantees=(Decimal(0),)*len(bases)
        contracts[pid]=CONTRACTS.Contract(pid,2000,bases,guarantees)
        roster[pid]=R.Player(pid,"QB" if n<3 else "WR")
    clubs[club_id]=T.Club(CONTRACTS.Ledger(club_id,contracts),R.Roster(club_id,roster))
assert len(clubs)==48
first=next(iter(clubs))
pick=PICKS.Pick(2001,3,first,first,1)
initial=L.League(0,clubs,{pick.identity:pick},(),None,(),structure)
assert L.decode(L.encode(initial))==initial
results=[]
for g in structure.fixtures:
    key=f'{g["week"]}|{g["game"]}|{g["home"]}|{g["away"]}'
    n=int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],"big")
    results.append({**g,"home_score":7+n%31,"away_score":3+(n>>10)%31})
try:H.advance(initial,results,seed=41,coronation_complete=False)
except ValueError as e:assert "Coronation" in str(e)
else:raise AssertionError("premature handoff")
try:H.advance(initial,results[:-1],seed=41,coronation_complete=True)
except ValueError:pass
else:raise AssertionError("missing result accepted")
advanced,report=H.advance(initial,results,seed=41,coronation_complete=True)
assert report["completed"]==1 and report["next"]==2
assert advanced.structure.season==2 and advanced.revision==1
assert len(report["expired_players"])==48*10
assert len(advanced.clubs)==48
assert all(len(c.roster.players)==1 and len(c.ledger.contracts)==1
           for c in advanced.clubs.values())
assert advanced.ordinary[pick.identity].owner==first
assert all(advanced.clubs[c].ledger.contracts[f"id{i}-P0"].end_year==2002
           for i,c in enumerate(clubs))
assert len({cid for v in advanced.structure.seeded_divisions.values() for cid in v}
           | set(advanced.structure.ambassadors.values()))==48
assert L.decode(L.encode(advanced))==advanced
db=L.LeagueTradeStore(":memory:")
db.initialize(initial)
try:db.advance_season(results,expected_revision=0,seed=41,
                      coronation_complete=False)
except ValueError:pass
else:raise AssertionError("premature DB handoff")
assert db.load()==initial
db.db.execute("""CREATE TRIGGER break_handoff BEFORE INSERT ON ed815_league_events
    BEGIN SELECT RAISE(ABORT,'simulate lost commit'); END""")
try:db.advance_season(results,expected_revision=0,seed=41,coronation_complete=True)
except sqlite3.IntegrityError:pass
else:raise AssertionError("event failure did not rollback handoff")
assert db.load()==initial and db.committed_events()==()
db.db.execute("DROP TRIGGER break_handoff")
saved=db.advance_season(results,expected_revision=0,seed=41,coronation_complete=True)
assert saved==advanced and db.load()==advanced and len(db.committed_events())==1
try:db.advance_season(results,expected_revision=1,seed=41,coronation_complete=True)
except ValueError:pass
else:raise AssertionError("same fixtures advanced a second season")
# A pending reservation blocks the boundary.
db2=L.LeagueTradeStore(":memory:")
db2.initialize(initial)
ids=list(clubs)
leg=(T.TradeLeg(ids[0],ids[1],(f"id0-P0",)),)
reserved,token=db2.reserve(leg,expected_revision=0,season=1,
                           moment=datetime(2000,3,1,tzinfo=timezone.utc),
                           post_cut=False)
try:db2.advance_season(results,expected_revision=1,seed=41,coronation_complete=True)
except ValueError as e:assert "outstanding" in str(e)
else:raise AssertionError("trade lock did not block season")
assert db2.load()==reserved
print("Edition 8.15 financial/structural season handoff checks passed")
