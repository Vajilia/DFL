"""Edition 8.15 pick ownership and returning-lottery checks."""
from __future__ import annotations
from collections import Counter
import random
import ed815_picks as P


CLUBS=tuple(f"club-{i:02d}" for i in range(48))


def check_lottery():
    returning=CLUBS[:8]
    order=P.equal_lottery(returning,88)
    assert order == P.equal_lottery(reversed(returning),88)
    assert len(order)==len(set(order))==8
    counts=Counter()
    for seed in range(10000):
        counts[P.equal_lottery(returning,seed)[0]]+=1
    assert set(counts)==set(returning)
    assert all(abs(counts[club]-1250)<200 for club in returning),counts


def check_picks_and_transfers():
    picks=P.ordinary_picks(2000,CLUBS)
    assert len(picks)==336
    assert all(p.slot in range(1,49) for p in picks.values())
    identity=(2000,1,CLUBS[0])
    after=P.transfer(picks,identity,from_club=CLUBS[0],to_club=CLUBS[1],
                     current_draft_year=2000)
    assert picks[identity].owner==CLUBS[0]
    assert after[identity].owner==CLUBS[1]
    assert after[identity].original_club==CLUBS[0]
    assert after[identity].slot==picks[identity].slot
    held=P.reserve(after,identity,CLUBS[1])
    try:
        P.transfer(held,identity,from_club=CLUBS[1],to_club=CLUBS[2],
                   current_draft_year=2000)
    except ValueError:
        pass
    else:
        raise AssertionError("reserved pick was traded")
    free=P.unreserve(held,identity,CLUBS[1])
    used=P.select(free,identity,CLUBS[1])
    assert used[identity].used and not after[identity].used
    for action in (
        lambda:P.transfer(used,identity,from_club=CLUBS[1],to_club=CLUBS[2],
                          current_draft_year=2000),
        lambda:P.select(used,identity,CLUBS[1]),
        lambda:P.reserve(used,identity,CLUBS[1]),
    ):
        try:
            action()
        except ValueError:
            pass
        else:
            raise AssertionError("used pick moved or selected again")
    # Current draft plus two future drafts, not an unbounded horizon.
    future=P.ordinary_picks(2002,CLUBS)
    assert P.transfer(future,(2002,7,CLUBS[0]),from_club=CLUBS[0],
                      to_club=CLUBS[1],current_draft_year=2000)
    try:
        P.transfer(future,(2002,7,CLUBS[0]),from_club=CLUBS[0],
                   to_club=CLUBS[1],current_draft_year=1999)
    except ValueError:
        pass
    else:
        raise AssertionError("out-of-horizon trade allowed")


def check_randomized_identity_conservation():
    rng=random.Random(815)
    picks=P.ordinary_picks(2000,CLUBS)
    identities=list(picks)
    for _ in range(10000):
        key=rng.choice(identities)
        old=picks[key]
        destination=rng.choice([c for c in CLUBS if c!=old.owner])
        changed=P.transfer(picks,key,from_club=old.owner,to_club=destination,
                           current_draft_year=2000)
        assert changed[key].identity==key
        assert changed[key].original_club==old.original_club
        assert changed[key].slot==old.slot
        assert len(changed)==len(picks)==336
        picks=changed


if __name__ == "__main__":
    check_lottery()
    check_picks_and_transfers()
    check_randomized_identity_conservation()
    print("Edition 8.15 picks: 10,000 lottery draws and transfers passed")
