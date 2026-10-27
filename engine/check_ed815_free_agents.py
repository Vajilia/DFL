"""Edition 8.15 free-agent pool and atomic signing tests."""
from datetime import datetime,timezone
from decimal import Decimal
import sqlite3
from dataclasses import replace
import ed815_calendar as CAL
import ed815_cycle as CY
import ed815_league_store as L
import ed815_roster as R
import ed815_contracts as C
import ed815_free_agents as FA
import ed815_transactions as T
import ed815_picks as P

seeded={d:[f"{i}/{r}" for r in range(1,6)]
        for i,d in enumerate(CAL.DIVISION_ORDER)}
amb={d:f"{i}/amb" for i,d in enumerate(CAL.DIVISION_ORDER)}
structure=CY.build_structure(1,seeded,amb)
club_ids=[cid for ids in seeded.values() for cid in ids]+list(amb.values())
clubs={}
for i,name in enumerate(club_ids):
    contract_id=f"person-{i}"
    c=C.Contract(contract_id,2000,(Decimal(10),),(Decimal(0),))
    p=R.Player(contract_id,"QB","main",credited_seasons=3)
    clubs[name]=T.Club(C.Ledger(name,{contract_id:c}),
                       R.Roster(name,{contract_id:p}))
initial=L.League(0,clubs,{},(),None,(),structure)
results=[{**g,"home_score":14,"away_score":10} for g in structure.fixtures]
db=L.LeagueTradeStore(":memory:")
db.initialize(initial)
advanced=db.advance_season(results,expected_revision=0,seed=11,
                           coronation_complete=True)
assert len(advanced.free_agents)==48
assert all(len(c.ledger.contracts)==0 and len(c.roster.players)==0
           for c in advanced.clubs.values())
assert L.decode(L.encode(advanced))==advanced
pid=f"person-0"
target=club_ids[1]
deal=C.Contract(pid,2001,(Decimal(20),Decimal(20)),(Decimal(0),Decimal(0)))
signed=db.sign_free_agent(target,pid,deal,expected_revision=1)
assert pid in signed.clubs[target].roster.players and pid not in signed.free_agents
assert signed.clubs[target].roster.players[pid].position=="QB"
assert len(signed.free_agents)==47
assert L.decode(L.encode(signed))==signed
try:db.sign_free_agent(club_ids[2],pid,deal,expected_revision=2)
except ValueError:pass
else:raise AssertionError("same free agent signed twice")
assert db.load()==signed
overpriced=C.Contract("person-1",2001,(Decimal(1100),),(Decimal(0),),Decimal(0))
try:db.sign_free_agent(target,"person-1",overpriced,expected_revision=2)
except ValueError as e: assert "cap" in str(e)
else:raise AssertionError("over-cap free agent signing")
assert db.load()==signed
# Corrupting event insert must roll back the roster and pool edits together.
db.db.execute("""CREATE TRIGGER stop_sign BEFORE INSERT ON ed815_league_events
    BEGIN SELECT RAISE(ABORT,'forced'); END""")
deal2=C.Contract("person-2",2001,(Decimal(5),),(Decimal(0),))
try:db.sign_free_agent(target,"person-2",deal2,expected_revision=2)
except sqlite3.IntegrityError:pass
else:raise AssertionError("non-atomic pool/signing rollback")
assert db.load()==signed and "person-2" in signed.free_agents
db.db.execute("DROP TRIGGER stop_sign")
# A pool clock starts on entry, and retirement is at fourth subsequent opening.
survivors,retired=FA.retire_due(signed.free_agents,2004)
assert "person-1" in survivors and not retired
survivors,retired=FA.retire_due(signed.free_agents,2005)
assert len(retired)==47 and not survivors
try:FA.retire_due(signed.free_agents,2000)
except ValueError:pass
else:raise AssertionError("future pool entrants accepted")
print("Edition 8.15 free-agent contract/pool/retirement checks passed")
