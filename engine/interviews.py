"""The job interview: the first negotiation table.

Until now an owner chose a candidate and the candidate always said yes. Now the two sit at a table and each has her own say:

  1. The owner offers GUARANTEED SEASONS, 0 to 3: the owner cannot fire her in her first N reviews after she is hired (the engine
     removes the firing options from the owner's yearly choice while the guarantee lasts, whoever owns the team by then). The
     autopilot offers 0, which is the league as it was.
  2. The candidate accepts, asks for more guaranteed seasons, or walks away.
  3. If she asked for more, the owner accepts, holds at her last offer, or withdraws; if she held, the candidate accepts or walks.

A candidate who walks (or is withdrawn from) is not hired; the owner chooses again among the others, and each gets her own interview.
If all three refuse, the league office fills the seat by the old rule (the first candidate, no guarantee): a seat is never empty.
Only the terms are negotiable; what a guarantee does is small, bounded and applied by the engine (see staff_cards.season_end).

Money is not in the offer yet: coaches and GMs have no salary in the engine. When pay exists it becomes a second term here.
"""
from __future__ import annotations

import cards as C
import decisions as D
import tables as TB

MAX_GUARANTEE = 3                  # no one is ever guaranteed more than three reviews
REL_DEAL = 4                       # goodwill (-100..100) a signed deal adds each way
REL_COUNTER_DEAL = 2               # a little more if it took some bargaining
WINDOW = 5                         # years of an owner's firing record a candidate can see


def recent_fires(lg, year: int) -> dict:
    """(kind, team) -> how many coaches or GMs that team has fired in the last few years: public record every candidate can see."""
    out: dict = {}
    for e in lg.archive:
        if e["event"] in ("coach_fired", "gm_fired") and year - e["year"] < WINDOW:
            k = ("coach" if e["event"] == "coach_fired" else "gm", e["team"])
            out[k] = out.get(k, 0) + 1
    return out


def _s(n: int) -> str:
    return f"{n} guaranteed season{'s' if n != 1 else ''}"


class Interview(TB.Table):
    kind = "interview"

    def __init__(self, lg, year, team, kind: str, owner, cand, vet: bool, alternatives: int, fires: int, view):
        super().__init__()
        self.lg, self.year, self.team, self.job_kind, self.owner, self.cand = lg, year, team, kind, owner, cand
        self.vet, self.alternatives, self.fires, self.owner_sees = vet, alternatives, fires, view
        self.step, self.offer, self.ask, self.outcome = "offer", None, None, None
        self.steps = []

    # ---- what each side is shown
    def _job(self) -> dict:
        """The candidate's view of the job: public facts plus how patient the owner looks to HER (the truth plus her own blind spots)."""
        t, o, lg = self.team, self.owner, self.lg
        r = C._rng(lg.card_seed, "readowner", o.oid, self.year, self.cand.first, self.cand.last)
        last = lg.prev_pct.get(t.id)
        return dict(team=t.name, job="head coach" if self.job_kind == "coach" else "general manager",
                    team_record_last_season=None if last is None else round(last, 3), fan_approval_of_the_owner=round(o.approval, 2),
                    owner=dict(trait=o.trait, patience_as_you_read_her=round(max(1.0, min(100.0, o.ratings["patience"] + r.gauss(0.0, 8.0))), 0),
                               new_owner=o.seasons_owned <= 1, fired_coaches_or_gms_here_in_the_last_5_years=self.fires),
                    you_were_between_jobs=self.vet, other_candidates_the_owner_could_turn_to=self.alternatives,
                    what_a_guarantee_means="the owner cannot fire you in your first N yearly reviews, whoever owns the team by then")

    def _said(self) -> list:
        return [dict(by=s["by"], move=s["move"]) for s in self.steps]

    def next_point(self):
        t, lg, year = self.team, self.lg, self.year
        internal = dict(team=t, owner=self.owner, candidate=self.cand, offer=self.offer, table=self, strength_rank=1 + sum(1 for x in lg.teams if x.strength > t.strength))
        if self.step == "offer":
            opts = [dict(id=f"offer_{g}", label=f"Offer {_s(g)}", tags={"guaranteed": g}) for g in range(MAX_GUARANTEE + 1)]
            ctx = dict(job="head coach" if self.job_kind == "coach" else "general manager", candidate=self.owner_sees, candidate_was_between_jobs=self.vet,
                       if_she_walks=f"you choose again among {self.alternatives} other candidate(s)" if self.alternatives else "no one else is left; the league office will fill the seat",
                       said_so_far=self._said())
            return D.DecisionPoint("interview_offer", year, t.id, "owner", self.owner, ctx, opts, "offer_0", internal)
        if self.step == "counter":                     # the owner's turn: she sees what she is told and what she knows of the candidate, not the candidate's read of her
            ctx = dict(job="head coach" if self.job_kind == "coach" else "general manager", candidate=self.owner_sees, candidate_was_between_jobs=self.vet,
                       she_asks_for=_s(self.ask), your_last_offer=_s(self.offer), said_so_far=self._said(),
                       if_she_walks=f"you choose again among {self.alternatives} other candidate(s)" if self.alternatives else "no one else is left; the league office will fill the seat")
            opts = [dict(id="accept", label=f"Agree to {_s(self.ask)}", tags={"guaranteed": self.ask}),
                    dict(id="hold", label=f"Hold at {_s(self.offer)}", tags={"guaranteed": self.offer}),
                    dict(id="walk", label="Withdraw the offer", tags={})]
            return D.DecisionPoint("interview_counter", year, t.id, "owner", self.owner, ctx, opts, "accept", internal)
        ctx = dict(self._job(), the_offer_on_the_table=_s(self.offer), said_so_far=self._said())
        if self.step == "reply":
            opts = [dict(id="accept", label=f"Accept {_s(self.offer)}", tags={"guaranteed": self.offer})]
            opts += [dict(id=f"counter_{g}", label=f"Ask for {_s(g)}", tags={"guaranteed": g}) for g in range(self.offer + 1, MAX_GUARANTEE + 1)]
            opts.append(dict(id="walk", label="Walk away from the job", tags={}))
            return D.DecisionPoint("interview_reply", year, t.id, self.job_kind, self.cand, ctx, opts, "accept", internal)
        opts = [dict(id="accept", label=f"Accept {_s(self.offer)}", tags={"guaranteed": self.offer}), dict(id="walk", label="Walk away from the job", tags={})]
        ctx = dict(ctx, the_owner_held_at=_s(self.offer))
        return D.DecisionPoint("interview_final", year, t.id, self.job_kind, self.cand, ctx, opts, "accept", internal)

    # ---- what each move does
    def _say(self, by: str, move: str):
        self.steps.append(dict(by=by, move=move))

    def _end(self, deal=None, walked_by=None):
        self.outcome = ("deal", deal) if deal is not None else ("walk", walked_by)
        self.done = True

    def apply(self, pick: str):
        if self.step == "offer":
            self.offer = int(pick.split("_")[1])
            self._say("owner", f"offers {_s(self.offer)}")
            self.step = "reply"
        elif self.step == "reply":
            if pick == "accept":
                self._say("candidate", "accepts")
                self._end(deal=self.offer)
            elif pick == "walk":
                self._say("candidate", "walks away")
                self._end(walked_by="candidate")
            else:
                self.ask = int(pick.split("_")[1])
                self._say("candidate", f"asks for {_s(self.ask)}")
                self.step = "counter"
        elif self.step == "counter":
            if pick == "accept":
                self._say("owner", f"agrees to {_s(self.ask)}")
                self._end(deal=self.ask)
            elif pick == "walk":
                self._say("owner", "withdraws the offer")
                self._end(walked_by="owner")
            else:
                self._say("owner", f"holds at {_s(self.offer)}")
                self.step = "final"
        else:
            if pick == "accept":
                self._say("candidate", "accepts")
                self._end(deal=self.offer)
            else:
                self._say("candidate", "walks away")
                self._end(walked_by="candidate")

    def plain(self) -> bool:
        """True if nothing happened that the old rule would not have: offered nothing, accepted at once."""
        return self.outcome == ("deal", 0) and len(self.steps) == 2

    def summary(self) -> dict:
        o = self.outcome
        return dict(candidate=self.cand.name, steps=[f"{s['by']} {s['move']}" for s in self.steps],
                    outcome=f"deal: {_s(o[1])}" if o[0] == "deal" else f"no deal: {o[1]} walked")
