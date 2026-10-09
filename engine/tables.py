"""Negotiation tables: the few places where each party must have an independent say.

The Commissioner's design (2026-10-05): not every interaction needs a meeting space. A table exists only where two or more parties each act for
themselves and a deal needs both of them: a job interview, a contract negotiation, a trade. Team meetings, CEO lunches and the
relationships between a coach and her players stay generalized (the cards and the scenes in interactions.py carry them).

A table is a short, bounded conversation made of Decision Points, so it uses the same one door as every other choice:
  * each turn belongs to one party, who is shown her own card, what she perceives of the others, what has been said so far, and the
    moves the engine allows (never the truth about the others, never a move the rules do not allow);
  * the guard checks the answer and falls back to the autopilot's move if there is none, so a table always finishes;
  * every turn is in the choice log, so a table can be replayed exactly;
  * a deal happens only if both sides accepted something the engine's limits allow, and what it changes is applied by the engine.
The autopilot's moves at every table are the league's rules before tables existed, so with the autopilot a league plays out as it always did.

Many tables are open at once (the 48 CEOs' jobs do not depend on each other), so they run in lockstep: every table's next turn is
asked together (decide_many) and a dozen agents can answer at the same time. Inside one table the turns are in order.

A table subclass says what its turns are (next_point), what each move does (apply) and when it is over (done).
"""
from __future__ import annotations

from typing import List

MAX_TURNS = 12                    # a table is a short conversation; this only catches a bug that would never end


class Table:
    """Base class. A table is done when `done` is true; until then next_point() is the turn waiting to be taken."""
    kind = "table"

    def __init__(self):
        self.done = False
        self.turns = 0
        self.points: List[str] = []          # the ids of the decision points asked at this table, in order

    def next_point(self):
        raise NotImplementedError

    def apply(self, pick: str):
        raise NotImplementedError


def run_tables(lg, tables: List[Table]):
    """Run tables to the end, together: each round asks the next turn of every table that is still open."""
    import decisions as D
    live = [t for t in tables if not t.done]
    while live:
        points = [t.next_point() for t in live]
        picks = D.decide_many(lg, points)
        for t, dp, pick in zip(live, points, picks):
            t.turns += 1
            if t.turns > MAX_TURNS:
                raise RuntimeError(f"a {t.kind} table did not finish in {MAX_TURNS} turns")
            t.points.append(dp.id)
            t.apply(pick)
        live = [t for t in live if not t.done]
