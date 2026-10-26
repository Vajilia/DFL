"""Property/boundary checks for Edition 8.15 monetary guards."""
from __future__ import annotations

from decimal import Decimal
import random
import ed815_cap as C


def state(hits=(), booked=0, strict=0, holds=(), fraction=1, cut=False):
    return C.YearProjection(tuple(hits), C.D(booked), tuple(holds),
                            C.D(strict), C.D(fraction), post_cut=cut)


def check_constants_and_count():
    assert (C.CAP, C.RESERVE, C.MINIMUM_SALARY, C.BASE_REQUIRED,
            C.MAX_STRICT_DEAD, C.TOP_COUNT_PRECUT) == (1000,25,5,240,735,69)
    pre = state(hits=[10]*70, holds=[25])
    post = state(hits=[10]*70, holds=[25],cut=True)
    assert pre.cap_number == 715
    assert post.cap_number == 725
    assert state(hits=[10]*69,booked=10).cap_number == 700
    assert state(strict=735).viability_margin == 0
    assert state(strict=735.01).viability_margin < 0
    assert state(strict=800,fraction=Decimal("0.5")).viability_margin == 55


def check_actions():
    good = state(hits=[600],strict=100)
    over = state(hits=[1000.01],strict=100)
    assert not C.assess_transaction({2000:good},{2000:over},action="sign").allowed
    assert C.assess_transaction({2000:over},{2000:good},action="restructure").allowed
    assert C.assess_transaction({2000:good},{2000:over},action="release").allowed
    assert not C.assess_transaction({2000:good},{2000:over},action="cut",final_cut=True).allowed
    safe = state(strict=735)
    unsafe = state(strict=735.01)
    assert not C.assess_transaction({2000:safe},{2000:unsafe},action="release").allowed
    assert C.assess_transaction({2000:unsafe},{2000:safe},action="release").allowed
    # Unchanged old violation cannot freeze a club in perpetuity.
    assert C.assess_transaction({2000:unsafe},{2000:unsafe},action="restructure").allowed
    # Commitments in a later year are binding independently of current-year room.
    before = {2000:good,2001:good}
    after = {2000:good,2001:state(hits=[1001],strict=100)}
    assert not C.assess_transaction(before,after,action="sign").allowed
    # There is no rollover: current-year unspent 400 changes nothing in 2001.
    assert after[2001].cap_number == 1001


def check_precision_and_errors():
    before=state(hits=[1000])
    after=state(hits=[Decimal("1000.000000000001")])
    assert not C.assess_transaction({2000:before},{2000:after},action="claim").allowed
    for bad in [-1,float("nan"),float("inf"),True]:
        try:
            state(hits=[bad])
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid amount {bad}")
    for bad in [-0.01,1.01]:
        try:
            state(fraction=bad)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted invalid paid fraction")


def check_randomized_properties():
    rng=random.Random(88)
    for _ in range(10000):
        hits=[C.D(rng.randrange(0,15000))/100 for _ in range(rng.randrange(0,100))]
        holds=[C.D(rng.randrange(500,3501))/100 for _ in range(rng.randrange(0,10))]
        s=state(hits=hits, holds=holds, booked=0, strict=0, cut=False)
        t=state(hits=hits, holds=holds, booked=0, strict=0, cut=True)
        assert s.cap_number <= t.cap_number
        assert s.cap_number == sum(sorted(hits,reverse=True)[:69],Decimal(0)) + sum(holds,Decimal(0))
        assert s.strict_dead_limit == 735
        # Adding a liability cannot lower the cap number.
        plus=state(hits=hits+[100],holds=holds)
        assert plus.cap_number >= s.cap_number


if __name__ == "__main__":
    check_constants_and_count()
    check_actions()
    check_precision_and_errors()
    check_randomized_properties()
    print("Edition 8.15 cap guards: boundaries and 10,000 randomized cases passed")
