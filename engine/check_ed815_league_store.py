"""48-club leaguewide atomic SQLite trade checks."""
from datetime import datetime,timezone
from decimal import Decimal
from dataclasses import replace
import sqlite3
import tempfile
from pathlib import Path
import ed815_contracts as C
import ed815_roster as R
import ed815_transactions as T
import ed815_picks as P
import ed815_compensation as COMP
import ed815_league_store as L

def club(name):
    contracts={};players={}
    for i in range(11):
        pid=f"{name}_P{i}"
        contracts[pid]=C.Contract(pid,2000,(Decimal(10),),(Decimal(0),))
        players[pid]=R.Player(pid,"QB" if i<3 else "WR")
    return T.Club(C.Ledger(name,contracts),R.Roster(name,players))

names=tuple(f"T{i:02d}" for i in range(48))
clubs={name:club(name) for name in names}
pick=P.Pick(2000,1,names[1],names[1],1)
comp=COMP.CompPick(2000,1,names[0],names[0],"lost",Decimal(95))
initial=L.League(0,clubs,{pick.identity:pick},(comp,))
assert L.decode(L.encode(initial))==initial
moment=datetime(2000,3,1,tzinfo=timezone.utc)
legs=(T.TradeLeg(names[0],names[1],(f"{names[0]}_P0",),comp_pick_ids=(comp.identity,)),
      T.TradeLeg(names[1],names[0],(f"{names[1]}_P0",),pick_ids=(pick.identity,)))
db=L.LeagueTradeStore(":memory:")
db.initialize(initial)
reserved,token=db.reserve(legs,expected_revision=0,season=1,moment=moment,
                          post_cut=False,require_eleven=True)
assert reserved.pending==token and L.decode(L.encode(reserved))==reserved
try:db.reserve(legs,expected_revision=1,season=1,moment=moment,post_cut=False)
except ValueError:pass
else:raise AssertionError("overlapping reservation allowed")
result=db.commit(token,expected_revision=1,moment=moment)
assert result.revision==2 and result.pending is None
assert all(result.clubs[n]==clubs[n] for n in names[2:])
assert result.ordinary[pick.identity].owner==names[0]
assert result.compensation[0].owner==names[1]
assert len(db.committed_events())==1
assert L.decode(L.encode(result))==result
try:db.commit(token,expected_revision=2,moment=moment)
except ValueError:pass
else:raise AssertionError("replayed commit")
assert db.load()==result
db.close()
# Rollback event-write failure after all 48 clubs have been staged.
db=L.LeagueTradeStore(":memory:")
db.initialize(initial)
reserved,token=db.reserve(legs,expected_revision=0,season=1,moment=moment,
                          post_cut=False)
db.db.execute("""CREATE TRIGGER break_event BEFORE INSERT ON ed815_league_events
    BEGIN SELECT RAISE(ABORT,'injected failure'); END""")
try:db.commit(token,expected_revision=1,moment=moment)
except sqlite3.IntegrityError:pass
else:raise AssertionError("failed event write should abort transaction")
assert db.load()==reserved and db.committed_events()==()
db.db.execute("DROP TRIGGER break_event")
assert db.commit(token,expected_revision=1,moment=moment).revision==2
db.close()
# File-backed restart test must run on a writable filesystem / CI.
with tempfile.TemporaryDirectory() as temp:
    database=str(Path(temp)/"league.sqlite")
    db=L.LeagueTradeStore(database)
    db.initialize(initial)
    reserved,token=db.reserve(legs,expected_revision=0,season=1,moment=moment,
                              post_cut=False)
    db.close()
    db=L.LeagueTradeStore(database)
    assert db.load()==reserved
    done=db.commit(token,expected_revision=1,moment=moment)
    db.close()
    db=L.LeagueTradeStore(database)
    assert db.load()==done and len(db.committed_events())==1
    db.close()
print("Edition 8.15 leaguewide snapshot/atomic transaction checks passed")
