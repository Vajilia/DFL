"""Focused isolated tests for atomic roster/player/pick settlement."""
from datetime import datetime,timezone
from dataclasses import replace
import ed815_cap as CAP,ed815_contracts as C,ed815_roster as R
import ed815_picks as P,ed815_transactions as T,ed815_market as M

def contract(pid, salary=10,bonus=0):
    return C.Contract(pid,2000,(CAP.D(salary),),(CAP.D(0),),CAP.D(bonus))

def make_club(name,n=11,salary=10):
    contracts={}
    players={}
    for i in range(n):
        pid=f"{name}{i}"
        contracts[pid]=contract(pid,salary)
        players[pid]=R.Player(pid,"QB" if i<3 else "WR")
    return T.Club(C.Ledger(name,contracts),R.Roster(name,players))

a,b=make_club("A"),make_club("B")
clubs={"A":a,"B":b}
moment=datetime(2000,3,1,tzinfo=timezone.utc)
assert M.may_finalize_trade(1,moment)
leg=(T.TradeLeg("A","B",("A0",)),T.TradeLeg("B","A",("B0",)))
new,picks,comp=T.propose_trade(clubs,{},leg,season=1,moment=moment,post_cut=False,require_eleven=True)
assert "B0" in new["A"].roster.players and "A0" in new["B"].ledger.contracts
assert "A0" in a.roster.players and "B0" in b.ledger.contracts
try:
    T.propose_trade(clubs,{},(T.TradeLeg("A","B",("A0",)),),
                    season=1,moment=moment,post_cut=False,require_eleven=True)
except ValueError as e:
    assert "eleven" in str(e)
else: raise AssertionError("eleven fielding guard failed")
try:
    T.propose_trade(clubs,{},(T.TradeLeg("A","B",("A0","MISSING")),),
                    season=1,moment=moment,post_cut=False)
except ValueError: pass
else: raise AssertionError("missing player allowed")
assert "A0" in clubs["A"].ledger.contracts
try:
    T.propose_trade(clubs,{},leg,season=1,
                    moment=datetime(2000,1,10,tzinfo=timezone.utc),post_cut=False)
except ValueError: pass
else: raise AssertionError("closed market allowed")
p=P.Pick(2000,7,"A","A",1)
new,picks,comp=T.propose_trade(clubs,{p.identity:p},
    (T.TradeLeg("A","B",pick_ids=(p.identity,)),),
    season=1,moment=moment,post_cut=False)
assert picks[p.identity].owner=="B" and p.owner=="A"
assert len(new["A"].roster.players)==11
# A bundled salary swap may pass despite an intermediate overcap condition.
rich=make_club("X",11,10)
poor=make_club("Y",11,10)
rich_c=dict(rich.ledger.contracts); rich_c["X0"]=contract("X0",900)
poor_c=dict(poor.ledger.contracts); poor_c["Y0"]=contract("Y0",900)
rich=replace(rich,ledger=replace(rich.ledger,contracts=rich_c))
poor=replace(poor,ledger=replace(poor.ledger,contracts=poor_c))
bundle=(T.TradeLeg("X","Y",("X0",)),T.TradeLeg("Y","X",("Y0",)))
result,_,_=T.propose_trade({"X":rich,"Y":poor},{},bundle,
                       season=1,moment=moment,post_cut=False)
assert "Y0" in result["X"].ledger.contracts
# Single-sided $900 acquisition raises destination's over-cap position.
try:
    T.propose_trade({"X":rich,"Y":poor},{},(T.TradeLeg("X","Y",("X0",)),),
                     season=1,moment=moment,post_cut=False)
except ValueError as e:
    assert "cap overage" in str(e)
else: raise AssertionError("cap overage permitted")
# Multi-leg pick duplicate must fail atomically.
try:
    T.propose_trade(clubs,{p.identity:p},
        (T.TradeLeg("A","B",pick_ids=(p.identity,p.identity)),),
        season=1,moment=moment,post_cut=False)
except ValueError: pass
else: raise AssertionError("double spent pick")
assert R.coverage([R.Player(str(i),pos) for i,pos in enumerate(
    ["HB","HB","FB","QB","QB","QB"])])["WR"]==5
assert "HB" not in R.coverage([R.Player(str(i),pos) for i,pos in enumerate(
    ["HB","HB","FB","QB","QB","QB"])])
# Exact final-cut positional coverage and practice-squad veteran restrictions.
template={"K":1,"P":1,"QB":3,"HB":2,"FB":1,"WR":5,"TE":2,"LT":2,
          "LG":2,"C":1,"RG":2,"RT":2,"LE":2,"RE":2,"DT":3,"ROLB":2,
          "MLB":3,"LOLB":2,"CB":5,"FS":2,"SS":2,"LS":1}
full={}
for pos,count in template.items():
    for i in range(count):
        pid=f"{pos}{i}"
        full[pid]=R.Player(pid,pos)
assert len(full)==48, len(full)
for i in range(5):
    full[f"extra{i}"]=R.Player(f"extra{i}","WR")
roster=R.Roster("A",full)
assert R.validate(roster,final_cut=True)
bad=dict(full)
del bad["LS0"]
try: R.validate(R.Roster("A",bad),final_cut=True)
except ValueError: pass
else: raise AssertionError("invalid final cut accepted")
for i in range(7):
    bad[f"ps{i}"]=R.Player(f"ps{i}","WR","practice",3)
try: R.validate(R.Roster("A",bad))
except ValueError as e: assert "veteran" in str(e)
else: raise AssertionError("practice veteran limit failed")

# Compensation picks carry the same rookie holds and ownership constraints.
import ed815_compensation as COMP
cp=COMP.CompPick(2000,1,"A","A","freeagent1",CAP.D(100))
comp_leg=(T.TradeLeg("A","B",comp_pick_ids=(cp.identity,)),)
changed,unchanged,comp_after=T.propose_trade(clubs,{},comp_leg,season=1,
    moment=moment,post_cut=False,compensation=(cp,))
assert unchanged=={} and comp_after[0].owner=="B" and cp.owner=="A"
try:
    T.propose_trade(clubs,{},(T.TradeLeg("A","B",comp_pick_ids=(cp.identity,cp.identity)),),
        season=1,moment=moment,post_cut=False,compensation=(cp,))
except ValueError: pass
else: raise AssertionError("double spent comp pick")
try:
    T.propose_trade(clubs,{},(T.TradeLeg("A","B",comp_pick_ids=(cp.identity,)),),
        season=1,moment=moment,post_cut=False,compensation=(replace(cp,reserved=True),))
except ValueError: pass
else: raise AssertionError("reserved comp pick transferred")
# A pick arriving at an over-cap club must be included in AFTER cap holds.
f=make_club("F",11,89)
g=make_club("G",11,10)
# F is at 979 in contracts and 5+ rookie reservation would increase over-cap
# only once a pre-existing 25 hold is included.
p1=P.Pick(2000,1,"G","G",1)
try:
    T.propose_trade({"F":f,"G":g},{p1.identity:p1},
       (T.TradeLeg("G","F",pick_ids=(p1.identity,)),),
       season=1,moment=moment,post_cut=False)
except ValueError as e:
    assert "cap overage" in str(e)
else: raise AssertionError("incoming first-round rookie hold not counted")

print("Edition 8.15 atomic trade + roster + compensation focused tests passed")
