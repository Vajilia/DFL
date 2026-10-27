"""Edition 8.15 waiver eligibility, ordering and timing checks."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random
import ed815_waivers as W


CLUBS=tuple(f"club-{i:02d}" for i in range(48))
TIME=datetime(2000,8,1,12,0,tzinfo=timezone.utc)


def check_boundary():
    for service in range(4):
        assert W.is_waiver_eligible(service)
        assert isinstance(W.release_path("p",CLUBS[0],service,TIME),W.Waiver)
    for service in (4,5,10,30):
        assert not W.is_waiver_eligible(service)
        assert W.release_path("p",CLUBS[0],service,TIME).status == "vested_free_agent"
    for week in range(1,5):
        assert W.priority_order(week,CLUBS,tuple(reversed(CLUBS))) == CLUBS
    assert W.priority_order(5,CLUBS,tuple(reversed(CLUBS))) == tuple(reversed(CLUBS))
    try:
        W.priority_order(5,CLUBS)
    except ValueError:
        pass
    else:
        raise AssertionError("missing standings order accepted")


def check_clock_and_claims():
    w=W.release_path("player",CLUBS[0],3,TIME)
    assert w.expires_at-TIME == timedelta(days=1)
    claim=W.Claim(CLUBS[2],TIME+timedelta(minutes=1))
    try:
        W.resolve_waiver(w,[claim],CLUBS,w.expires_at-timedelta(microseconds=1),lambda c,p:True)
    except ValueError:
        pass
    else:
        raise AssertionError("premature settlement")
    late=W.Claim(CLUBS[1],w.expires_at)
    # A claim in the final microsecond counts, one at expiry does not.
    final=W.Claim(CLUBS[3],w.expires_at-timedelta(microseconds=1))
    result=W.resolve_waiver(w,[late,claim,final],CLUBS,w.expires_at,lambda c,p:True)
    assert result.new_club == CLUBS[2]
    assert result.considered_claimants == (CLUBS[2],)
    result=W.resolve_waiver(w,[claim,final],CLUBS,w.expires_at,
                            lambda c,p:c!=CLUBS[2])
    assert result.new_club == CLUBS[3]
    assert result.considered_claimants == (CLUBS[2],CLUBS[3])
    assert W.resolve_waiver(w,[],CLUBS,w.expires_at,lambda c,p:True).status == "cleared"
    assert W.resolve_waiver(w,[W.Claim(CLUBS[0],TIME)],CLUBS,w.expires_at,
                            lambda c,p:True).status == "cleared"


def check_randomized():
    rng=random.Random(15815)
    w=W.release_path("player",CLUBS[0],2,TIME)
    for _ in range(10000):
        order=list(CLUBS)
        rng.shuffle(order)
        claimants=set(rng.sample(CLUBS[1:],rng.randrange(0,25)))
        claims=[W.Claim(c,TIME+timedelta(hours=4)) for c in claimants]
        eligible=set(rng.sample(CLUBS[1:],rng.randrange(0,25)))
        result=W.resolve_waiver(w,reversed(claims),order,w.expires_at,
                                lambda club,p:club in eligible)
        expected=next((c for c in order if c in claimants and c in eligible),None)
        assert result.new_club == expected
        assert result.status == ("claimed" if expected else "cleared")
        assert result.player_id == "player"


if __name__ == "__main__":
    check_boundary()
    check_clock_and_claims()
    check_randomized()
    print("Edition 8.15 waiver claims: boundaries and 10,000 randomized cases passed")
