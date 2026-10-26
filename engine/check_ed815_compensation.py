"""Edition 8.15 compensatory-pick netting and rookie cap reservation checks."""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
import random
import ed815_picks as P
import ed815_compensation as C
import ed815_cap as CAP


CLUBS=tuple(f"club-{i:02d}" for i in range(48))


def move(n,from_club,to_club,base=100,top=True):
    return C.FreeAgentMove(str(n),from_club,to_club,CAP.D(base),top)


def check_netting():
    assert C.allocate_compensation(2000,[],CLUBS)==()
    # Three high-value losses cannot earn more than two picks.
    departures=[move(i,CLUBS[0],CLUBS[1],100+i,True) for i in range(3)]
    awards=C.allocate_compensation(2000,departures,CLUBS)
    assert len(awards)==2
    assert all(p.original_club==CLUBS[0] for p in awards)
    assert [p.qualifying_base for p in awards]==[102,101]
    # A qualifying acquisition cancels the most valuable loss first.
    transactions=[move("a",CLUBS[0],CLUBS[2],100,True),
                  move("b",CLUBS[0],CLUBS[2],90,True),
                  move("c",CLUBS[3],CLUBS[0],75,False)]
    awards=C.allocate_compensation(2000,transactions,CLUBS)
    assert [p.qualifying_player for p in awards if p.original_club==CLUBS[0]] == ["b"]
    assert not any(p.original_club==CLUBS[3] for p in awards)
    # Below threshold and below top quarter do not create departures.
    assert not C.allocate_compensation(2000,[move("x",CLUBS[0],CLUBS[1],74.99,True)],CLUBS)
    assert not C.allocate_compensation(2000,[move("y",CLUBS[0],CLUBS[1],75,False)],CLUBS)
    assert C.allocate_compensation(2000,list(reversed(transactions)),CLUBS)==awards


def check_ownership_and_reservations():
    picks=P.ordinary_picks(2000,CLUBS)
    holds=C.rookie_holds_by_owner(2000,picks,[])
    assert len(holds)==48
    expected=sum(C.ROOKIE_BY_ROUND.values())
    assert all(sum(h)==expected for h in holds.values())
    ident=(2000,1,CLUBS[0])
    traded=P.transfer(picks,ident,from_club=CLUBS[0],to_club=CLUBS[1],
                      current_draft_year=2000)
    changed=C.rookie_holds_by_owner(2000,traded,[])
    assert sum(changed[CLUBS[0]])==expected-25
    assert sum(changed[CLUBS[1]])==expected+25
    # Selection releases a reserve; the actual fixed four-year contract replaces it.
    selected=P.select(traded,ident,CLUBS[1])
    after=C.rookie_holds_by_owner(2000,selected,[])
    assert sum(after[CLUBS[1]])==expected
    contract=C.fixed_rookie_contract("rookie-a",selected[ident])
    assert contract.bases==(Decimal(25),)*4
    assert contract.guarantees==(Decimal(0),)*4
    assert contract.bonus==0
    assert C.FIRST_ROUND_OPTION==35
    awards=C.allocate_compensation(2000,[move("a",CLUBS[0],CLUBS[2],90)],CLUBS)
    cap=C.rookie_holds_by_owner(2000,selected,awards)
    assert sum(cap[CLUBS[0]])==sum(after[CLUBS[0]])+5
    transferred=C.transfer_comp(awards[0],CLUBS[0],CLUBS[1],2000)
    assert transferred.original_club==CLUBS[0]
    assert transferred.owner==CLUBS[1]
    assert transferred.identity==awards[0].identity


def check_randomized():
    rng=random.Random(81515)
    for run in range(2000):
        shuffled=list(CLUBS)
        rng.shuffle(shuffled)
        moves=[]
        for i in range(rng.randrange(0,100)):
            a,b=rng.sample(CLUBS,2)
            moves.append(move(f"{run}-{i}",a,b,rng.randrange(5,150),rng.choice([True,False])))
        awards=C.allocate_compensation(2000,moves,shuffled)
        assert len(awards)<=48
        assert len(set(p.identity for p in awards))==len(awards)
        assert all(C.rookie_salary_for_round("post-R7")==5 for p in awards)
        assert all(p.slot_after_round_seven==i for i,p in enumerate(awards,1))
        count={}
        for award in awards:
            count[award.owner]=count.get(award.owner,0)+1
        assert all(v<=2 for v in count.values())
        assert C.allocate_compensation(2000,reversed(moves),shuffled)==awards


if __name__ == "__main__":
    check_netting()
    check_ownership_and_reservations()
    check_randomized()
    print("Edition 8.15 compensation: 2,000 randomized movement sets passed")
