"""A stand-in for real agents, to test the machinery around them (batching, the guard, notes, seats) without a model.

A real agent is any function that takes the plain-data view of one decision (decisions.DecisionPoint.public()) and returns
{"choice": option id, "reason": text, "note": text}. This one is a small rulebook that reads ONLY that view (the deciding card's
traits, ratings, notes and the options on offer, with the perceived ratings a CEO would see), never the engine's true state, so it
is a fair rehearsal for a model: it can be wrong, and different cards choose differently.

    from agents import StandIn, seats
    lg.driver = decisions.AgentDriver(StandIn(), workers=12)            # an agent in every CEO's seat
    lg.driver = seats(range(1, 13), StandIn())                          # agents in 12 seats; the autopilot keeps the rest

Everything it can do is a legal option; the guard would reject anything else.
"""
from __future__ import annotations

import random
import time

import decisions as D

# how patient each kind of CEO is with a struggling coach or GM (more = more patient), and how she weighs a candidate
PATIENCE = {"Patient Steward": 0.30, "Legacy Builder": 0.15, "Local Hero": 0.10, "Penny-Pincher": 0.25, "Opportunist": -0.05,
            "Showwoman": -0.10, "Glory Hunter": -0.20, "Meddler": -0.15}
LOOKS_FOR = {                                     # CEO trait -> what she weights in a candidate (offense, defense, development, gamecraft, discipline, motivation)
    "Glory Hunter": (1.0, 1.0, 0.2, 0.5, 0.2, 0.3), "Patient Steward": (0.3, 0.3, 1.0, 0.3, 0.6, 0.6), "Legacy Builder": (0.6, 0.6, 1.0, 0.4, 0.4, 0.4),
    "Showwoman": (1.0, 0.4, 0.2, 0.3, 0.1, 1.0), "Meddler": (0.5, 0.5, 0.3, 1.0, 0.9, 0.3), "Penny-Pincher": (0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
    "Local Hero": (0.4, 0.4, 0.6, 0.4, 0.6, 1.0), "Opportunist": (0.8, 0.8, 0.2, 0.6, 0.2, 0.2)}
OFFER_OPEN = {"Patient Steward": 1, "Legacy Builder": 1, "Local Hero": 1, "Penny-Pincher": 0, "Opportunist": 0, "Showwoman": 0, "Glory Hunter": 0, "Meddler": 0}   # what a CEO opens with
OFFER_LIMIT = {"Patient Steward": 3, "Legacy Builder": 2, "Local Hero": 2, "Penny-Pincher": 1, "Opportunist": 1, "Showwoman": 1, "Glory Hunter": 0, "Meddler": 0}   # the most she will give
GM_VIEW = ("scouting", "negotiation", "evaluation", "trades", "cap_sense")


class StandIn:
    """The stand-in agent. `delay` simulates the time a real agent takes to answer (seconds)."""

    def __init__(self, delay: float = 0.0, notes: bool = True):
        self.delay, self.notes = delay, notes
        self.calls = 0

    def __call__(self, payload: dict) -> dict:
        if self.delay:
            time.sleep(self.delay)
        self.calls += 1
        me = payload["decider"]
        r = random.Random(f"standin-{payload['id']}")
        if payload["kind"] == "staff_review":
            return self._review(payload, me, r)
        if payload["kind"].startswith("interview") or payload["kind"].startswith("contract"):
            return getattr(self, "_" + payload["kind"])(payload, me, r)
        if payload["kind"] == "fan_demand":
            return self._fan_demand(payload, r)
        if payload["kind"] == "ceo_pledge":
            return self._ceo_pledge(payload, me)
        if payload["kind"] == "ceo_boycott":
            return self._ceo_boycott(payload, me)
        return self._hire(payload, me, r)

    # ---- the fans' yearly ask: press hard on an unpopular CEO, ease off a popular one
    def _fan_demand(self, p, r):
        ap = p["context"]["ceo_approval"]
        pick = "demanding" if ap < 0.45 else "modest" if ap > 0.70 else "fair"
        return dict(choice=pick, reason=f"approval of the CEO is {ap:.0%}", note=f"asked for the {pick} level in {p['year']}" if self.notes else "")

    # ---- the CEO's yearly pledge: an ambitious CEO with restless fans gives more, a business-minded one with happy fans keeps more
    def _ceo_pledge(self, p, me):
        ap, rt = p["context"]["fan_approval_of_you"], me["ratings"]
        pick = "generous" if rt["ambition"] >= 65 and ap < 0.55 else "lean" if rt["business"] >= 70 and ap > 0.65 else "standard"
        return dict(choice=pick, reason=f"approval {ap:.0%}", note=f"pledged {pick} in {p['year']}" if self.notes else "")

    # ---- her answer to a boycott: step aside near the end of her tenure, concede if she cares about the club, else hold
    def _ceo_boycott(self, p, me):
        ctx = p["context"]
        left = ctx.get("your_tenure_ends_in")
        pick = "step_aside" if left is not None and left <= 2 else "concede" if me["ratings"]["ambition"] >= 50 else "hold"
        return dict(choice=pick, reason=f"boycott level {ctx['boycott_level']:.2f}", note=f"answered the boycott with {pick} in {p['year']}" if self.notes else "")

    # ---- the yearly review: keep, or fire the coach, the GM or both
    def _review(self, p, me, r):
        ctx, opts = p["context"], {o["id"] for o in p["options"]}
        patience = PATIENCE.get(me["trait"], 0.0) + (me["ratings"]["patience"] - 50.0) / 250.0
        # she fires when the season was worse than she is willing to wait for (a winning season never costs a job unless she is restless)
        bad = 0.5 - ctx["record_this_season"] - patience
        angry_fans = ctx["fan_approval_of_you"] < 0.45 or ctx["facing_a_recall_vote_this_year"]
        wants = []
        for who in ("coach", "gm"):
            c = ctx.get(who)
            if c is None or not c.get("can_be_fired", True):
                continue
            heat = c["pressure_on_her"]
            cut = bad + 0.25 * heat + (0.08 if angry_fans else 0.0) + (0.10 if ctx["you_are_a_new_ceo"] else 0.0) - (0.15 if c["reputation"] in ("legend", "Hall of Famer") else 0.0) + r.gauss(0.0, 0.03)
            if cut > 0.12:
                wants.append(who)
        pick = "keep_all" if not wants else ("fire_both" if len(wants) == 2 and "fire_both" in opts else f"fire_{wants[0]}")
        if pick not in opts:
            pick = "keep_all"
        note = ""
        if self.notes:
            note = {"keep_all": f"Stood pat after a {ctx['record_this_season']:.3f} season; look again if it slips.",
                    "fire_coach": "Let the coach go; the new one gets two seasons.", "fire_gm": "Let the GM go; watch the next draft.",
                    "fire_both": "Cleaned house; I own whatever comes next."}[pick]
        return dict(choice=pick, reason=f"{me['trait']}: record {ctx['record_this_season']:.3f}, fans {ctx['fan_approval_of_you']:.2f}", note=note)

    # ---- a hire: the best candidate for what she looks for, as she perceives them
    def _hire(self, p, me, r):
        is_coach = p["kind"] == "hire_coach"
        w = LOOKS_FOR.get(me["trait"], (0.5,) * 6)
        best, best_score = None, -1e9
        for o in p["options"]:
            v = o["view"]
            if is_coach:
                score = sum(wi * v["perceived"][a] for wi, a in zip(w, ("offense", "defense", "development", "gamecraft", "discipline", "motivation")))
            else:
                score = sum(v["perceived"][a] for a in GM_VIEW) / len(GM_VIEW) * 3.0
            score += {"legend": 12, "Hall of Famer": 12, "star": 6, "respected": 3}.get(v["reputation"], 0) * (1.0 if me["trait"] in ("Showwoman", "Glory Hunter") else 0.4)
            score += 3.0 * sum(v["honors"].values()) ** 0.5
            score += r.gauss(0.0, 2.0)
            if o["tags"].get("between_jobs") and me["trait"] in ("Penny-Pincher", "Patient Steward"):
                score += 3.0                                    # a familiar, cheaper face
            if score > best_score:
                best, best_score = o, score
        note = f"Hired {best['view']['name']} ({best['view']['reputation']})." if self.notes else ""
        return dict(choice=best["id"], reason=f"{me['trait']} weighed the candidates", note=note)

    # ---- the job interview (interviews.py): the CEO's side
    def _owner_limit(self, me, candidate, alternatives) -> int:
        """The most guaranteed seasons this CEO will give: patient CEOs give more, and everyone gives more to a famous name or when no one else is left."""
        base = OFFER_LIMIT.get(me["trait"], 1)
        famous = candidate.get("reputation") in ("legend", "Hall of Famer", "star")
        return max(0, min(3, base + (1 if famous else 0) + (1 if alternatives == 0 else 0)))

    # ---- the contract table (step 6i): a stand-in that bargains a little, always inside the options the rep leaves
    def _contract_offer(self, p, me, r):
        ctx = p["context"]
        std = ctx["standard_length_years"]
        have = {(o["tags"]["pct"], o["tags"]["years"]) for o in p["options"]}
        cheap = me["trait"] in ("Penny-Pincher", "Opportunist")
        pct = 90 if cheap and (90, std) in have else 100 if (100, std) in have else max(c for c, _ in have)
        pick = f"offer_{pct}_{std}" if (pct, std) in have else f"offer_{pct}_{next(y for c, y in sorted(have) if c == pct)}"
        return dict(choice=pick, reason=f"{me['trait']} opens at {pct}%", note=f"Offered {pct}% to {ctx['player']['position']} rated {ctx['player']['rating']}." if self.notes else "")

    def _contract_reply(self, p, me, r):
        offer = next(o["tags"]["pct"] for o in p["options"] if o["id"] == "accept")
        counters = sorted(o["tags"]["pct"] for o in p["options"] if o["id"].startswith("counter_"))
        if offer >= 100 or not counters:
            pick = "accept"
        elif offer <= 90 and me["pressure"].get("contract", 50) >= 70 and r.random() < 0.2:
            pick = "walk"
        else:
            pick = f"counter_{counters[0]}"
        return dict(choice=pick, reason=f"offered {offer}%", note=f"Bargained over pay: {pick}." if self.notes else "")

    def _contract_counter(self, p, me, r):
        ask = next(o["tags"]["pct"] for o in p["options"] if o["id"] == "accept")
        pick = "accept" if ask <= 100 else "hold"
        return dict(choice=pick, reason=f"she asks {ask}%", note="")

    def _contract_final(self, p, me, r):
        offer = next(o["tags"]["pct"] for o in p["options"] if o["id"] == "accept")
        return dict(choice="accept" if offer >= 90 else "walk", reason=f"held at {offer}%", note="")

    def _interview_offer(self, p, me, r):
        ctx = p["context"]
        alts = 0 if "no one else" in ctx["if_she_walks"] else 1
        g = max(0, min(3, OFFER_OPEN.get(me["trait"], 0) + (1 if ctx["candidate"].get("reputation") in ("legend", "Hall of Famer", "star") else 0) + (1 if not alts else 0)
                       + (1 if r.random() < 0.15 else 0)))
        return dict(choice=f"offer_{g}", reason=f"{me['trait']} opens with {g}", note=f"Offered {ctx['candidate']['name']} {g} guaranteed season(s)." if self.notes else "")

    def _interview_counter(self, p, me, r):
        ctx = p["context"]
        ask = next(o["tags"]["guaranteed"] for o in p["options"] if o["id"] == "accept")
        offer = next(o["tags"]["guaranteed"] for o in p["options"] if o["id"] == "hold")
        alts = 0 if "no one else" in ctx["if_she_walks"] else 1
        limit = self._owner_limit(me, ctx["candidate"], alts)
        if ask <= limit:
            pick = "accept"
        elif ask - offer >= 3 and alts and r.random() < 0.3:
            pick = "walk"
        else:
            pick = "hold"
        return dict(choice=pick, reason=f"{me['trait']}: she wants {ask}, I will go to {limit}", note=f"Bargained over guaranteed seasons: {pick}." if self.notes else "")

    # ---- the job interview: the candidate's side
    def _wants(self, me, job) -> int:
        """How many guaranteed seasons she wants before she takes this job: more for an impatient or trigger-happy CEO and a struggling team, and for
        someone with a name or who is anxious about contracts."""
        o = job["owner"]
        last = job["team_record_last_season"]
        want = (0.4 * o["fired_coaches_or_gms_here_in_the_last_5_years"] + (55.0 - o["patience_as_you_read_her"]) / 25.0 + (0.5 - (0.5 if last is None else last)) * 3.0
                + (me["pressure"]["contract"] - 50.0) / 50.0 + (0.8 if me["reputation"] in ("legend", "Hall of Famer", "star") else 0.0) - (0.5 if o["new_owner"] else 0.0))
        return max(0, min(3, round(want)))

    def _interview_reply(self, p, me, r):
        job = p["context"]
        want = self._wants(me, job)
        offer = next(o["tags"]["guaranteed"] for o in p["options"] if o["id"] == "accept")
        counters = {o["tags"]["guaranteed"]: o["id"] for o in p["options"] if o["id"].startswith("counter_")}
        if offer >= want:
            pick, why = "accept", "enough security"
        elif want - offer >= 2 and job["other_candidates_the_owner_could_turn_to"] > 0 and r.random() < 0.4:
            pick, why = "walk", "not enough security for this CEO"
        else:
            pick, why = counters.get(want, "accept"), f"asks for {want}"
        note = {"accept": f"Took the {job['team']} job on {offer} guaranteed season(s).", "walk": f"Turned down {job['team']}: too little security.",
                }.get(pick, f"Asked {job['team']} for {want} guaranteed seasons.") if self.notes else ""
        return dict(choice=pick, reason=why, note=note)

    def _interview_final(self, p, me, r):
        job = p["context"]
        want = self._wants(me, job)
        offer = next(o["tags"]["guaranteed"] for o in p["options"] if o["id"] == "accept")
        pick = "accept" if offer >= want - 1 or r.random() < 0.5 else "walk"
        return dict(choice=pick, reason=f"wanted {want}, offered {offer}", note=(f"{'Took' if pick == 'accept' else 'Turned down'} {job['team']} after bargaining.") if self.notes else "")


class Flaky:
    """Wraps an agent so that about one answer in `every` is lost (an error) or invalid (not an option), to show the autopilot stepping in."""

    def __init__(self, agent, every: int = 4):
        self.agent, self.every = agent, every

    def __call__(self, payload: dict):
        h = random.Random(f"flaky-{payload['id']}").random()
        if h < 1.0 / self.every / 2:
            raise RuntimeError("the agent's answer was lost")
        if h < 1.0 / self.every:
            return {"choice": "not_an_option", "reason": "garbled"}
        return self.agent(payload)


def seats(team_ids, ask, workers: int = D.DEFAULT_WORKERS, timeout: float = 30.0):
    """Agents in some CEOs' seats and the autopilot in the rest."""
    agent = D.AgentDriver(ask, timeout=timeout, workers=workers)
    return D.PerTeamDriver({tid: agent for tid in team_ids})
