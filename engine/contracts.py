"""Step 6i: the contract table, and the club's value-to-price rule.

A contract table is a short, bounded negotiation between a club (its general manager) and a player whose contract has run out and whom the club wants
back. Like the job interview it is made of Decision Points, so agents can take either seat and the autopilot's moves are the league's rule before tables:

  1. The club offers a PRICE (90%, 100% or 110% of the player's market salary) and a LENGTH (one year shorter or longer than the standard).
  2. The player accepts, asks for more pay, or walks (to the market).
  3. If she asked for more, the club accepts, holds at its last offer, or withdraws; if it held, the player accepts or walks.

The DFLPA representative sits at every table. She advises and holds back what the rules do not allow, and she never sets terms: she removes from each side's
options any term below the minimum salary, above the maximum contract, longer than five years, or that the club cannot fund under its cap, and says so in
the context both sides read. Nothing outside the rules can ever be chosen, whoever is choosing.

Autopilot: the club offers 100% for the standard length, the player accepts, and the deal is exactly what the road always did (her asking price is her market
price). Only an agent's choices change a deal, and only inside the band the rep guards.

The CLUB'S VALUE RULE decides whether the club wants her back at all (it replaces the old re-signing dice, a probability): she is kept when her gain to the
club (how much better the club is with her than with the next player at her position, in rating points, economy-style) clears a bar that rises with her price.
Who is an important deal (and gets a table) is a model dial: roster_model.table_min_ovr.

Known gaps (the rulebook row says so): extensions are made only when a contract expires (never mid-contract), the club's GM and the player have no say about
guarantees or bonus shares, and tables run one after another (an agent driver answers one table at a time rather than a dozen in parallel).
"""
from __future__ import annotations

from typing import Callable, List, Optional, Tuple

import decisions as D
import economy as EC
import tables as TB

PRICE_STEPS = (90, 100, 110)                # percent of the market salary; 100 is the autopilot's offer
YEAR_DELTAS = (-1, 0, 1)                    # one year shorter, standard, one year longer
KEEP_G0, KEEP_G1, KEEP_GM_SHIFT = -12.0, 0.3, 20.0       # defaults of the value rule (roster_model.keep_g0, keep_g1, keep_gm_shift)


def club_gain(roster, p) -> float:
    """How much she adds to the club: the offseason's gain measure (offseason._gain) against the rest of the roster."""
    import offseason as OFF
    return OFF._gain([q for q in roster if q is not p], p)


def club_wants(gain: float, cost: float, gm_factor: float = 1.0, g0: float = KEEP_G0, g1: float = KEEP_G1, shift: float = KEEP_GM_SHIFT) -> bool:
    """The value-to-price rule. A cheap depth player is kept for little; an expensive one only if she moves the club's lineup. A general manager who negotiates
    well (factor below 1) accepts a lower gain for the same price."""
    return gain >= g0 + g1 * cost + shift * (gm_factor - 1.0)


class _PlayerSeat:
    """A player as a Decision Point decider: the fields card_view reads, from her body and her card."""
    def __init__(self, p):
        c = p.card
        self.name, self.ratings, self.age = p.name, dict(p.ratings), p.age
        self.pressure = dict(c.pressure) if c is not None else {}
        self.trait, self.wants, self.fears = getattr(c, "trait", None), getattr(c, "wants", None), getattr(c, "fears", None)
        self.standing = getattr(c, "standing", "")
        self.honors = getattr(c, "honors", [])
        self.career = getattr(c, "career", [])
        self.decision_log = getattr(c, "decision_log", [])
        self.notes: list = []
        self.player = p


def _terms(pct: int, years: int) -> str:
    return f"{pct}% of her market salary for {years} year{'s' if years != 1 else ''}"


class ContractTable(TB.Table):
    kind = "contract"

    def __init__(self, lg, year: int, team, p, market: float, standard_years: int, fits: Callable[[float], bool]):
        super().__init__()
        self.lg, self.year, self.team, self.p = lg, year, team, p
        self.market, self.standard_years, self.fits = market, standard_years, fits
        self.club_seat = team.gm if team.gm is not None else team.owner
        self.club_role = "gm" if team.gm is not None else "owner"
        self.seat = _PlayerSeat(p)
        self.step, self.offer, self.ask, self.outcome = "offer", None, None, None
        self.steps: list = []
        self.held_back: list = []

    # ---- the rep's guard
    def salary(self, pct: int) -> float:
        return round(min(EC.MAX_SALARY, max(EC.min_salary(self.p.credited_seasons), self.market * pct / 100.0)), 2)

    def years_ok(self, y: int) -> bool:
        return 1 <= y <= EC.CONTRACT_YEARS_MAX

    def pays(self) -> List[int]:
        """The prices the rep lets onto the table: fundable under the club's cap."""
        out = []
        for pct in PRICE_STEPS:
            if self.fits(self.salary(pct)):
                out.append(pct)
            elif f"{pct}%" not in self.held_back:
                self.held_back.append(f"{pct}%")
        return out

    def lengths(self) -> List[int]:
        return [self.standard_years + d for d in YEAR_DELTAS if self.years_ok(self.standard_years + d)]

    def _ctx(self, **kw) -> dict:
        p = self.p
        return dict(dict(player=dict(position=p.pos, rating=round(p.ovr, 1), age=p.age, accrued_seasons=p.accrued_seasons),
                         market_salary_millions=self.market, standard_length_years=self.standard_years,
                         rep_note="the DFLPA representative has removed every term the rules or the club's cap do not allow: " +
                                  (f"prices {', '.join(self.held_back)} are unaffordable" if self.held_back else "nothing needed removing"),
                         said_so_far=[dict(by=s["by"], move=s["move"]) for s in self.steps]), **kw)

    def next_point(self):
        t, lg, year, p = self.team, self.lg, self.year, self.p
        internal = dict(team=t, player=p, table=self, offer=self.offer)
        pays = self.pays()
        if self.step == "offer":
            opts = [dict(id=f"offer_{pct}_{y}", label="Offer " + _terms(pct, y), tags={"pct": pct, "years": y, "salary": self.salary(pct)}) for pct in pays for y in self.lengths()]
            default = f"offer_100_{self.standard_years}"
            return D.DecisionPoint("contract_offer", year, t.id, self.club_role, self.club_seat, self._ctx(if_she_walks="she reaches the market and you fill the place from it"),
                                   opts, default, internal)
        pct, y = self.offer
        if self.step == "counter":
            ask_pct = self.ask
            opts = [dict(id="accept", label=f"Agree to {_terms(ask_pct, y)}", tags={"pct": ask_pct, "years": y}),
                    dict(id="hold", label=f"Hold at {_terms(pct, y)}", tags={"pct": pct, "years": y}),
                    dict(id="walk", label="Withdraw the offer", tags={})]
            return D.DecisionPoint("contract_counter", year, t.id, self.club_role, self.club_seat,
                                   self._ctx(she_asks_for=_terms(ask_pct, y), your_last_offer=_terms(pct, y)), opts, "accept", internal)
        seat_ctx = self._ctx(the_offer_on_the_table=_terms(pct, y))
        if self.step == "reply":
            opts = [dict(id="accept", label=f"Accept {_terms(pct, y)}", tags={"pct": pct, "years": y})]
            opts += [dict(id=f"counter_{c}", label=f"Ask for {_terms(c, y)}", tags={"pct": c, "years": y}) for c in pays if c > pct]
            opts.append(dict(id="walk", label="Walk away to the market", tags={}))
            default = "accept" if pct >= 100 or 100 not in pays else "counter_100"
            return D.DecisionPoint("contract_reply", year, t.id, "player", self.seat, seat_ctx, opts, default, internal)
        opts = [dict(id="accept", label=f"Accept {_terms(pct, y)}", tags={"pct": pct, "years": y}), dict(id="walk", label="Walk away to the market", tags={})]
        return D.DecisionPoint("contract_final", year, t.id, "player", self.seat, dict(seat_ctx, the_club_held_at=_terms(pct, y)), opts, "accept", internal)

    # ---- what each move does
    def _say(self, by: str, move: str):
        self.steps.append(dict(by=by, move=move))

    def _end(self, deal=None, walked_by=None):
        self.outcome = ("deal", deal) if deal is not None else ("walk", walked_by)
        self.done = True

    def apply(self, pick: str):
        if self.step == "offer":
            _, pct, y = pick.split("_")
            self.offer = (int(pct), int(y))
            self._say("club", "offers " + _terms(*self.offer))
            self.step = "reply"
        elif self.step == "reply":
            if pick == "accept":
                self._say("player", "accepts")
                self._end(deal=self.offer)
            elif pick == "walk":
                self._say("player", "walks away")
                self._end(walked_by="player")
            else:
                self.ask = int(pick.split("_")[1])
                self._say("player", f"asks for {self.ask}%")
                self.step = "counter"
        elif self.step == "counter":
            if pick == "accept":
                self._say("club", f"agrees to {self.ask}%")
                self._end(deal=(self.ask, self.offer[1]))
            elif pick == "walk":
                self._say("club", "withdraws the offer")
                self._end(walked_by="club")
            else:
                self._say("club", f"holds at {self.offer[0]}%")
                self.step = "final"
        else:
            if pick == "accept":
                self._say("player", "accepts")
                self._end(deal=self.offer)
            else:
                self._say("player", "walks away")
                self._end(walked_by="player")

    # ---- the result
    @property
    def deal(self) -> Optional[Tuple[float, int]]:
        """(salary, years) of the agreed contract, or None."""
        if self.outcome is None or self.outcome[0] != "deal":
            return None
        pct, y = self.outcome[1]
        return self.salary(pct), y

    def plain(self) -> bool:
        """True if nothing happened the old rule would not have: the market price for the standard length, accepted at once."""
        return self.outcome == ("deal", (100, self.standard_years)) and len(self.steps) == 2

    def summary(self) -> dict:
        return dict(player=self.p.id, club=self.team.id, outcome=self.outcome, steps=list(self.steps), held_back=list(self.held_back))
