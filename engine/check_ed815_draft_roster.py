"""Edition 8.15 ordinary/compensation draft signing integrated with league state."""
from decimal import Decimal
import sqlite3
import ed815_calendar as CAL
import ed815_cycle as CY
import ed815_league_store as L
import ed815_transactions as T
import ed815_contracts as C
import ed815_roster as R
import ed815_picks as P
import ed815_compensation as COMP
import ed815_draft_roster as D

seeded={d:tuple(f"{i}/{r}" for r in range(1,6))
        for i,d in enumerate(CAL.DIVISION_ORDER)}
amb={d:f"{i}/amb" for i,d in enumerate(CAL.DIVISION_ORDER)}
structure=CY.SeasonStructure(1,seeded,amb,())
names=[cid for x in seeded.values() for cid in x]+list(amb.values())
clubs={name:T.Club(C.Ledger(name),R.Roster(name,{})) for name in names}
first=names[0]; second=names[1]
ordinary=P.Pick(2000,1,first,first,1)
comp=COMP.CompPick(2000,1,second,second,"depart",Decimal(100))
candidates={
 "R1":D.Prospect(R.Player("R1","QB","camp"),2000),
 "C1":D.Prospect(R.Player("C1","LS","camp"),2000)}
initial=L.League(0,clubs,{ordinary.identity:ordinary},(comp,),None,(),structure,{},candidates)
assert L.decode(L.encode(initial))==initial
db=L.LeagueTradeStore(":memory:")
db.initialize(initial)
pick=db.select_rookie(first,"R1",ordinary.identity,expected_revision=0)
assert pick.revision==1 and pick.ordinary[ordinary.identity].used
assert pick.clubs[first].ledger.contracts["R1"].bases==(Decimal(25),)*4
assert "R1" not in pick.prospects and pick.clubs[first].roster.players["R1"].position=="QB"
try:db.select_rookie(first,"R1",ordinary.identity,expected_revision=1)
except ValueError:pass
else:raise AssertionError("drafted same rookie twice")
assert db.load()==pick
comp_signed=db.select_rookie(second,"C1",comp.identity,expected_revision=1)
assert comp_signed.compensation[0].used and not comp_signed.compensation[0].reserved
assert comp_signed.clubs[second].ledger.contracts["C1"].bases==(Decimal(5),)*4
assert L.decode(L.encode(comp_signed))==comp_signed
try:db.select_rookie(second,"R1",comp.identity,expected_revision=2)
except ValueError:pass
else:raise AssertionError("already-used pick accepted")
db.close()
# A failed event append cannot consume a pick or remove a prospect.
db=L.LeagueTradeStore(":memory:")
db.initialize(initial)
db.db.execute("""CREATE TRIGGER fail_draft BEFORE INSERT ON ed815_league_events
                 BEGIN SELECT RAISE(ABORT,'draft failure'); END""")
try:db.select_rookie(first,"R1",ordinary.identity,expected_revision=0)
except sqlite3.IntegrityError:pass
else:raise AssertionError("draft rollback missing")
assert db.load()==initial and db.committed_events()==()
db.db.execute("DROP TRIGGER fail_draft")
assert db.select_rookie(first,"R1",ordinary.identity,expected_revision=0).revision==1
print("Edition 8.15 rookie selection and cap-reservation checks passed")
