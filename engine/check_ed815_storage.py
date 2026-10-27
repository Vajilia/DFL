"""SQLite Edition 8.15 trade transaction checks: durability and rollback."""
from datetime import datetime,timezone
from decimal import Decimal
from dataclasses import replace
import sqlite3
import tempfile
from pathlib import Path
import ed815_cap as CAP,ed815_contracts as C,ed815_roster as R
import ed815_picks as P,ed815_compensation as COMP
import ed815_transactions as T,ed815_settlement as S,ed815_storage as DB

def club(name):
    contracts={};players={}
    for i in range(11):
        pid=f"{name}{i}"
        contracts[pid]=C.Contract(pid,2000,(Decimal("10"),),(Decimal("0"),))
        players[pid]=R.Player(pid,"QB" if i<3 else "WR")
    return T.Club(C.Ledger(name,contracts),R.Roster(name,players))

a,b=club("A"),club("B")
pick=P.Pick(2000,1,"B","B",1)
comp=COMP.CompPick(2000,1,"A","A","lost",Decimal("95"))
base=S.Snapshot(0,{"A":a,"B":b},{pick.identity:pick},(comp,))
assert DB.decode(DB.encode(base))==base
legs=(T.TradeLeg("A","B",("A0",),comp_pick_ids=(comp.identity,)),
      T.TradeLeg("B","A",("B0",),pick_ids=(pick.identity,)))
moment=datetime(2000,3,1,tzinfo=timezone.utc)
db=DB.SQLiteTradeStore(":memory:")
db.initialize(base)
try:db.initialize(base)
except ValueError:pass
else:raise AssertionError("double initialize")
reserved,token=db.reserve(legs,expected_revision=0,season=1,moment=moment,
                          post_cut=False,require_eleven=True)
assert DB.decode(DB.encode(reserved))==reserved
try:db.reserve(legs,expected_revision=0,season=1,moment=moment,post_cut=False)
except ValueError:pass
else:raise AssertionError("stale reservation")
assert db.load()==reserved
done=db.commit(token,expected_revision=1,moment=moment)
assert DB.decode(DB.encode(done))==done
assert done.compensation[0].owner=="B" and done.ordinary[pick.identity].owner=="A"
assert len(db.committed_events())==1
try:db.commit(token,expected_revision=2,moment=moment)
except ValueError:pass
else:raise AssertionError("duplicate commit")
assert db.load()==done and len(db.committed_events())==1
db.close()
# Simulate failed second write within commit: full transaction must roll back.
db=DB.SQLiteTradeStore(":memory:")
db.initialize(base)
reserved,token=db.reserve(legs,expected_revision=0,season=1,moment=moment,
                          post_cut=False)
db.db.execute("""CREATE TRIGGER fail_trade BEFORE INSERT ON ed815_commits
                 BEGIN SELECT RAISE(ABORT,'injected storage failure'); END""")
try:db.commit(token,expected_revision=1,moment=moment)
except sqlite3.IntegrityError:pass
else:raise AssertionError("injected failure did not abort")
assert db.load()==reserved and db.committed_events()==()
db.db.execute("DROP TRIGGER fail_trade")
assert db.commit(token,expected_revision=1,moment=moment).revision==2
db.close()
# On-disk reopen must recover identical persisted bytes/state.
with tempfile.TemporaryDirectory() as temporary:
    path=str(Path(temporary)/"dfl_transaction_test.sqlite")
    db=DB.SQLiteTradeStore(path)
    db.initialize(base)
    reserved,token=db.reserve(legs,expected_revision=0,season=1,moment=moment,
                              post_cut=False)
    db.close()
    db=DB.SQLiteTradeStore(path)
    assert db.load()==reserved
    completed=db.commit(token,expected_revision=1,moment=moment)
    db.close()
    reopened=DB.SQLiteTradeStore(path)
    assert reopened.load()==completed and len(reopened.committed_events())==1
    reopened.close()
print("Edition 8.15 SQLite snapshot/atomic rollback/reopen checks passed")
