"""Edition 8.15 isolated contract-ledger tests."""
from __future__ import annotations

from decimal import Decimal
import random
import ed815_contracts as C
import ed815_cap as CAP


def contract(pid="p",start=2000,bases=(20,30,40,50),guarantees=(10,10,0,0),bonus=100):
    return C.Contract(pid,start,bases,guarantees,C.D(bonus))


def check_release_and_split():
    original=C.Ledger("A")
    active=C.sign(original,contract(),2000)
    assert C.projection(active,2000,post_cut=False).cap_number == 45
    assert C.projection(active,2000,post_cut=False).strict_dead == 110
    normal=C.release(active,"p",2001)
    assert "p" not in normal.contracts
    assert normal.booked_dead[2001] == 85
    assert C.projection(normal,2001,post_cut=True).cap_number == 85
    assert normal.booked_dead[2002] == 0
    split=C.release(active,"p",2001,split=True)
    assert split.booked_dead[2001] == Decimal("47.5")
    assert split.booked_dead[2002] == Decimal("37.5")
    assert split.split_used == {2001}
    # The club cannot use the same year's special release again.
    two=C.sign(active,contract(pid="q",bases=(10,10),guarantees=(0,0),bonus=10),2000)
    once=C.release(two,"p",2001,split=True)
    try:
        C.release(once,"q",2001,split=True)
    except ValueError:
        pass
    else:
        raise AssertionError("second split allowed")
    assert active.contracts["p"].bonus == 100


def check_trade():
    a=C.sign(C.Ledger("A"),contract(),2000)
    b=C.Ledger("B")
    ao,bo=C.trade(a,b,"p",2001)
    assert "p" not in ao.contracts and "p" in bo.contracts
    assert ao.booked_dead[2001] == 75
    assert bo.contracts["p"].bonus == 0
    assert bo.contracts["p"].bases == a.contracts["p"].bases
    assert bo.contracts["p"].guarantees == a.contracts["p"].guarantees
    assert C.projection(bo,2001,post_cut=True).cap_number == 30
    assert C.projection(bo,2001,post_cut=True).strict_dead == 10
    # Atomic financial rejection: neither input ledger is ever mutated.
    rich=C.sign(b,contract(pid="r",bases=(990,),guarantees=(0,),bonus=0),2000,post_cut=True)
    try:
        C.trade(a,rich,"p",2000,post_cut=True)
    except ValueError:
        pass
    else:
        raise AssertionError("over-cap receiving club accepted a trade")
    assert "p" in a.contracts and "p" not in rich.contracts


def check_input_and_cap():
    try:
        contract(bases=(3,),guarantees=(0,),bonus=0)
    except ValueError:
        pass
    else:
        raise AssertionError("below-minimum contract")
    try:
        contract(bases=(5,)*6,guarantees=(0,)*6,bonus=0)
    except ValueError:
        pass
    else:
        raise AssertionError("six-year deal accepted")
    try:
        C.sign(C.Ledger("A"),contract(bases=(500,),guarantees=(500,),bonus=400),2000)
    except ValueError:
        pass
    else:
        raise AssertionError("contract exceeded strict-dead viability")


def check_bonus_conservation():
    rng=random.Random(1815)
    for i in range(5000):
        years=rng.randrange(1,6)
        bonus=CAP.D(rng.randrange(0,20001))/100
        bases=tuple(CAP.D(rng.randrange(5,100)) for _ in range(years))
        guarantees=tuple(CAP.D(0) for _ in range(years))
        c=contract(pid=str(i),bases=bases,guarantees=guarantees,bonus=bonus)
        elapsed=rng.randrange(years)
        release_year=2000+elapsed
        amortized=c.yearly_bonus*elapsed
        remaining=c.uncharged_bonus(release_year)
        assert amortized+remaining == bonus
        assert c.cap_hit(release_year) == bases[elapsed]+c.bonus_charge(release_year)
        assert sum((c.yearly_bonus for _ in range(elapsed)),CAP.D(0))+remaining == bonus
        # No part of the signing bonus can migrate to a receiving club.
        initial=C.Ledger("A",contracts={str(i):c})
        a,b=C.trade(initial,C.Ledger("B"),str(i),release_year)
        assert a.booked_dead[release_year] == remaining
        assert b.contracts[str(i)].bonus == 0
        assert sum(b.contracts[str(i)].guarantees) == 0


if __name__ == "__main__":
    check_release_and_split()
    check_trade()
    check_input_and_cap()
    check_bonus_conservation()
    print("Edition 8.15 contracts: settlement checks and 5,000 conservation cases passed")
