"""In-memory optimistic trade reservation and replay guards."""
from datetime import datetime,timezone
from dataclasses import replace
import ed815_cap as CAP
import ed815_contracts as C
import ed815_roster as R
import ed815_transactions as T
import ed815_settlement as S
import ed815_compensation as COMP
import ed815_picks as P

def club(name):
    contracts={}
    roster={}
    for i in range(11):
        pid=f"{name}{i}"
        contracts[pid]=C.Contract(pid,2000,(CAP.D(10),),(CAP.D(0),))
        roster[pid]=R.Player(pid,"QB" if i<3 else "WR")
    return T.Club(C.Ledger(name,contracts),R.Roster(name,roster))

a,b=club("A"),club("B")
cp=COMP.CompPick(2000,1,"A","A","lost1",CAP.D(100))
p=P.Pick(2000,7,"B","B",1)
base=S.Snapshot(0,{"A":a,"B":b},{p.identity:p},(cp,))
leg=(T.TradeLeg("A","B",("A0",),comp_pick_ids=(cp.identity,)),
     T.TradeLeg("B","A",("B0",),pick_ids=(p.identity,)))
now=datetime(2000,3,1,tzinfo=timezone.utc)
reserved,token=S.reserve(base,leg,season=1,moment=now,post_cut=False,require_eleven=True)
assert base.revision==0 and base.reservation is None
assert reserved.revision==1 and reserved.reservation==token
try:S.reserve(reserved,leg,season=1,moment=now,post_cut=False)
except ValueError as e:assert "reserved" in str(e)
else:raise AssertionError("duplicate reservation accepted")
done=S.commit(reserved,token,moment=now)
assert done.revision==2 and done.reservation is None and len(done.events)==1
assert done.compensation[0].owner=="B" and done.ordinary[p.identity].owner=="A"
assert "B0" in done.clubs["A"].ledger.contracts and "A0" in base.clubs["A"].ledger.contracts
try:S.commit(done,token,moment=now)
except ValueError:pass
else:raise AssertionError("replay accepted")
try:S.commit(replace(reserved,revision=9),token,moment=now)
except ValueError:pass
else:raise AssertionError("stale revision accepted")
# Mutation of underlying maps without revision advance must be detected.
corrupt=replace(reserved,ordinary={})
try:S.commit(corrupt,token,moment=now)
except ValueError as e:assert "changed" in str(e)
else:raise AssertionError("stale contents accepted")
stopped=S.cancel(reserved,token)
assert stopped.reservation is None and stopped.revision==2
assert base.ordinary[p.identity].owner=="B"
print("Edition 8.15 reserve/commit/replay focused checks passed")
