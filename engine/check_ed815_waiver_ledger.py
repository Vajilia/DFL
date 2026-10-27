"""Atomic Edition 8.15 waiver release, claim, cap and clearance tests."""
from datetime import datetime,timedelta,timezone
from decimal import Decimal
import sqlite3
import ed815_calendar as CAL
import ed815_cycle as CY
import ed815_league_store as L
import ed815_transactions as T
import ed815_contracts as C
import ed815_roster as R

seeded={d:tuple(f"{i}/{r}" for r in range(1,6))
        for i,d in enumerate(CAL.DIVISION_ORDER)}
amb={d:f"{i}/amb" for i,d in enumerate(CAL.DIVISION_ORDER)}
structure=CY.SeasonStructure(1,seeded,amb,())
names=[cid for group in seeded.values() for cid in group]+list(amb.values())
clubs={}
for ci,name in enumerate(names):
    contracts={};players={}
    for i in range(11):
        pid=f"player-{ci}-{i}"
        special=(ci==0 and i==0)
        bonuses=Decimal(10) if special else Decimal(0)
        contracts[pid]=C.Contract(pid,2000,(Decimal(10),Decimal(10)),
                                   (Decimal(0),Decimal(0)),bonuses)
        players[pid]=R.Player(pid,"QB" if i<3 else "WR",
                              credited_seasons=4 if i==1 else 1)
    if ci==1:  # A saturated high-priority club will fail the 90-player limit.
        for j in range(79):
            pid=f"extra-{ci}-{j}"
            contracts[pid]=C.Contract(pid,2000,(Decimal(5),),(Decimal(0),))
            players[pid]=R.Player(pid,"WR","camp")
    clubs[name]=T.Club(C.Ledger(name,contracts),R.Roster(name,players))
initial=L.League(0,clubs,{},(),None,(),structure)
db=L.LeagueTradeStore(":memory:")
db.initialize(initial)
pid="player-0-0"
start=datetime(2000,3,1,tzinfo=timezone.utc)
opened=db.begin_waiver_release(names[0],pid,expected_revision=0,at=start)
assert pid in opened.waivers and pid not in opened.clubs[names[0]].roster.players
assert pid in opened.clubs[names[0]].ledger.contracts
assert L.decode(L.encode(opened))==opened
filed=db.file_waiver_claim(pid,names[1],expected_revision=1,
                            at=start+timedelta(hours=1))
filed=db.file_waiver_claim(pid,names[2],expected_revision=2,
                            at=start+timedelta(hours=2))
try:db.resolve_waiver(pid,expected_revision=3,at=start+timedelta(hours=23),
     week=1,previous_draft_priority=names)
except ValueError:pass
else:raise AssertionError("waiver resolved before one full day")
assert db.load()==filed
# Lose the atomic write after the state update to verify all-or-nothing.
db.db.execute("""CREATE TRIGGER stop_award BEFORE INSERT ON ed815_league_events
    BEGIN SELECT RAISE(ABORT,'waiver failure'); END""")
try:db.resolve_waiver(pid,expected_revision=3,at=start+timedelta(days=1),
     week=1,previous_draft_priority=names)
except sqlite3.IntegrityError:pass
else:raise AssertionError("partial waiver award committed")
assert db.load()==filed
db.db.execute("DROP TRIGGER stop_award")
awarded=db.resolve_waiver(pid,expected_revision=3,at=start+timedelta(days=1),
    week=1,previous_draft_priority=names)
assert pid not in awarded.waivers and pid in awarded.clubs[names[2]].roster.players
assert pid not in awarded.clubs[names[0]].ledger.contracts
assert awarded.clubs[names[0]].ledger.booked_dead[2000]==Decimal(10)
assert awarded.clubs[names[2]].ledger.contracts[pid].bonus==Decimal(0)
assert len(awarded.clubs[names[1]].roster.players)==90
assert L.decode(L.encode(awarded))==awarded
assert len(db.committed_events())==4  # open + two filed + award, same player
# A vested player goes immediately into the free-agent pool.
vested="player-0-1"
released=db.begin_waiver_release(names[0],vested,expected_revision=4,
                                  at=start+timedelta(days=2))
assert vested not in released.waivers and vested in released.free_agents
# Nonvested player with no claims clears after one day.
cleared_id="player-0-2"
opened=db.begin_waiver_release(names[0],cleared_id,expected_revision=5,
                                 at=start+timedelta(days=3))
cleared=db.resolve_waiver(cleared_id,expected_revision=6,
                          at=start+timedelta(days=4),week=1,
                          previous_draft_priority=names)
assert cleared_id in cleared.free_agents and cleared_id not in cleared.waivers
assert cleared_id not in cleared.clubs[names[0]].ledger.contracts
assert len(db.committed_events())==7
print("Edition 8.15 waiver award, clearance, priority and rollback tests passed")
