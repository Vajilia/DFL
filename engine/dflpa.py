"""The DFLPA representative (Step 8c): the person who sits beside every player and coach at a table.

The Commissioner's rulebook (Skeleton): no independent agents. The DFLPA gives every player and coach a representative who advises her and ensures DFL
rules, the CBA and fair competitiveness are respected; she may hold a deal back but never sets terms.

A representative is a light character: a name, an advocacy rating (how hard she protects her client's price) and a caution rating (how closely she reads
the rules). She is generated on demand from the league seed and the client's id, so she needs no storage and the same client always has the same
representative. Everything here is MODEL except the role itself.
"""
from __future__ import annotations

from dataclasses import dataclass

import cards as C

ADVOCACY_HOLD = 70.0         # a representative this protective holds back a deal priced under 95% of her client's market ...
HOLD_BELOW_PCT = 95          # ... (the table offers 90, 100 and 110 percent of market, so this removes the 90% offer)
SEED_OFFSET = 66221


@dataclass(frozen=True)
class Rep:
    rid: int
    name: str
    advocacy: float
    caution: float

    def holds_back(self, pct: int) -> bool:
        """She holds back an offer under HOLD_BELOW_PCT of her client's market price, if she is protective enough. She removes the option; she never names a price."""
        return self.advocacy >= ADVOCACY_HOLD and pct < HOLD_BELOW_PCT


def rep_for(lg, client_kind: str, client_id: int) -> Rep:
    """The representative of a player (kind "player") or a coach or GM (kind "coach" or "gm")."""
    rid = (hash_id(client_kind) * 1_000_003 + int(client_id)) % 900_000
    r = C._rng(lg.card_seed, "dflpa", client_kind, client_id)
    first, last = C.make_name(lg.card_seed + SEED_OFFSET, rid)
    return Rep(rid=rid, name=f"{first} {last}", advocacy=round(max(1.0, min(100.0, r.gauss(50.0, 18.0))), 1), caution=round(max(1.0, min(100.0, r.gauss(60.0, 15.0))), 1))


def hash_id(kind: str) -> int:
    return {"player": 1, "coach": 2, "gm": 3}.get(kind, 4)
