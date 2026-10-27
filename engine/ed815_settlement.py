"""Edition 8.15 in-memory reserve/commit protocol for atomic two-club trades.

Reference protocol only. A durable store must make revision check and snapshot
replacement one database transaction. It must persist prepared reservations,
ledger states and event log before this is suitable for league production.
"""
from __future__ import annotations
from dataclasses import dataclass,replace
from datetime import datetime
import hashlib
import ed815_transactions as TX

@dataclass(frozen=True)
class Snapshot:
    revision: int
    clubs: dict
    ordinary: dict
    compensation: tuple = ()
    reservation: object = None
    events: tuple = ()

    def __post_init__(self):
        if self.revision < 0:
            raise ValueError("negative state revision")
        if len(self.clubs)!=2:
            raise ValueError("settlement snapshot requires exactly two clubs")

@dataclass(frozen=True)
class Reservation:
    token: str
    based_on: int
    locked_at: datetime
    season: int
    post_cut: bool
    legs: tuple
    require_eleven: bool
    fingerprint: str

def _fingerprint(snapshot: Snapshot) -> str:
    # Payload sorted deterministically, not Python's randomized hash().
    c=[]
    for name,club in sorted(snapshot.clubs.items()):
        contracts=tuple(sorted((pid,str(contract)) for pid,contract in club.ledger.contracts.items()))
        dead=tuple(sorted((str(y),str(amount)) for y,amount in club.ledger.booked_dead.items()))
        roster=tuple(sorted((pid,str(player)) for pid,player in club.roster.players.items()))
        c.append((name,contracts,dead,tuple(sorted(club.ledger.split_used)),roster))
    picks=tuple(sorted((str(k),str(p)) for k,p in snapshot.ordinary.items()))
    compensation=tuple(sorted((str(p.identity),str(p)) for p in snapshot.compensation))
    payload=repr((snapshot.revision,c,picks,compensation,snapshot.events)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def reserve(snapshot: Snapshot, legs: tuple, *, season: int,
            moment: datetime, post_cut: bool, require_eleven=False):
    if snapshot.reservation is not None:
        raise ValueError("assets already reserved by pending trade")
    # Validate against complete candidate before taking a reservation.
    TX.propose_trade(snapshot.clubs,snapshot.ordinary,legs,season=season,
                     moment=moment,post_cut=post_cut,
                     compensation=snapshot.compensation,require_eleven=require_eleven)
    digest=_fingerprint(snapshot)
    token=hashlib.sha256(repr((digest,legs,season,moment.isoformat(),
                              post_cut,require_eleven)).encode("utf-8")).hexdigest()
    reservation=Reservation(token,snapshot.revision,moment,season,
                            post_cut,tuple(legs),require_eleven,digest)
    return replace(snapshot,revision=snapshot.revision+1,reservation=reservation),reservation

def commit(snapshot: Snapshot, reservation: Reservation, *, moment: datetime):
    pending=snapshot.reservation
    if pending is None or pending!=reservation:
        raise ValueError("trade reservation not held")
    if snapshot.revision!=reservation.based_on+1:
        raise ValueError("stale reservation revision")
    base=replace(snapshot,revision=reservation.based_on,reservation=None)
    if _fingerprint(base)!=reservation.fingerprint:
        raise ValueError("underlying league state changed since reservation")
    clubs,ordinary,comp=TX.propose_trade(snapshot.clubs,snapshot.ordinary,
                reservation.legs,season=reservation.season,moment=moment,
                post_cut=reservation.post_cut,compensation=snapshot.compensation,
                require_eleven=reservation.require_eleven)
    event=("trade",reservation.token,reservation.season,moment.isoformat())
    return Snapshot(snapshot.revision+1,clubs,ordinary,comp,None,snapshot.events+(event,))

def cancel(snapshot: Snapshot, reservation: Reservation):
    if snapshot.reservation!=reservation or snapshot.revision!=reservation.based_on+1:
        raise ValueError("cannot cancel stale or unrelated reservation")
    return replace(snapshot,revision=snapshot.revision+1,reservation=None)
