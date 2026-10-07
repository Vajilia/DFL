"""Decision Points (Phase 4b): the one door every consequential choice goes through.

The principle (the Commissioner, 2026-10-04): the road, its guardrails and its traffic controls are code; the car is a card's capability
(its ratings); the driver is the agent that chooses what to do with it. Agents choose actions, never outcomes, and whatever
they choose, the league stays inside the fair-competitiveness bands.

How a choice is made
  1. The engine builds a DecisionPoint: who is deciding, what she perceives (not the truth), and the list of legal options.
     The options are enumerated by the engine, so a choice can only ever be one of them.
  2. A driver picks one option id (and may give a reason in plain words). Drivers: the autopilot (the rules the engine had before
     agents, kept as the default so a league never stalls), a random-legal driver and adversarial drivers (for testing the
     bands), a replay driver (re-plays a logged history), and an agent driver (calls out to a real agent, with a time limit).
  3. The guard checks the answer. Anything that is not one of the offered option ids, an error, or no answer in time, falls back
     to the autopilot's choice and is logged as such. A reason is stored as plain text (cut to a short length) and is never read
     as an instruction.
  4. The choice is applied by the engine and written to the choice log, the canonical record of the league's history: the same
     seed and the same choice log give the same league.

Many decisions in one season do not depend on each other (the 48 owners' yearly staff reviews, for example), so the engine hands them
to the guard together (decide_many) and a driver that can work in parallel answers them together: a dozen agents, each given one card and
one list of options at a time. An agent has no memory of its own. What a character remembers lives on her card: her career, her honors,
her recent decisions and a short, capped "notes to self" that she alone writes (through the guard) and alone reads back.

Everything an agent can do passes through a decision point built by the engine, so the guardrails are structural: the options on
offer, the caps on what an option can do, and the league-level rules. This module holds the machinery; the decisions themselves
are defined where they belong (staff_cards.py for the first pilot).
"""
from __future__ import annotations

import concurrent.futures
import random
from typing import Callable, Dict, List, Optional, Tuple

MAX_REASON = 400
MAX_NOTE = 240                       # a note to self is short plain text; the card keeps only the last NOTES_KEEP
NOTES_KEEP = 8
RECENT_SHOWN = 5                     # recent decisions shown back to an agent (the card keeps them all)
DEFAULT_WORKERS = 12                 # a dozen agents at a time


class DecisionPoint:
    """One choice waiting to be made. `internal` holds the true state for adversarial drivers and the engine; it is never
    shown to an agent (see public())."""

    def __init__(self, kind: str, year: int, team_id: int, actor_kind: str, actor, context: dict, options: List[dict],
                 default: str, internal: Optional[dict] = None):
        ids = [o["id"] for o in options]
        assert len(ids) == len(set(ids)) and default in ids, "options must be unique and include the autopilot's choice"
        self.kind, self.year, self.team_id, self.actor_kind, self.actor = kind, year, team_id, actor_kind, actor
        self.context, self.options, self.default = context, options, default
        self.internal = internal or {}
        self.id = ""                       # set by the guard

    @property
    def option_ids(self) -> List[str]:
        return [o["id"] for o in self.options]

    def public(self) -> dict:
        """What an agent is shown: the decider's own card (a bounded view of it), what she perceives, and the legal options.
        Nothing true-but-hidden."""
        a = self.actor
        return dict(id=self.id, kind=self.kind, year=self.year, team=self.team_id,
                    decider=card_view(self.actor_kind, a), context=self.context, options=[dict(o) for o in self.options],
                    instructions="Reply with the id of exactly one option, and optionally a short reason and a short note to yourself "
                                 "(plain words; the note is shown back to you at your next decision).")


def card_view(role: str, a) -> dict:
    """The decider's card as an agent sees it: who she is, what she is like, what she has done lately, and her own notes. Long lists
    on the card (career, honors, decisions) are summarized and the latest entries shown; the card itself keeps everything."""
    honors = {}
    for e in getattr(a, "honors", ()):
        honors[e["honor"]] = honors.get(e["honor"], 0) + 1
    career = getattr(a, "career", ())
    return dict(role=role, name=a.name, trait=getattr(a, "trait", None), wants=getattr(a, "wants", None), fears=getattr(a, "fears", None),
                ratings=dict(a.ratings), pressure=dict(a.pressure), age=getattr(a, "age", None),
                reputation=getattr(a, "standing", "") or "unknown", honors=honors,
                career_summary=dict(jobs=sum(1 for e in career if e.get("event") in ("hired", "bought", "elected")),
                                    fired=sum(1 for e in career if e.get("event") == "fired"), recalled=sum(1 for e in career if e.get("event") == "recalled")),
                recent_decisions=[dict(year=d["year"], did=d["action"]) for d in getattr(a, "decision_log", ())[-RECENT_SHOWN:]],
                notes_to_self=[dict(year=n["year"], note=n["text"]) for n in getattr(a, "notes", ())])


# ---- drivers ------------------------------------------------------------------------------------------
class PolicyDriver:
    """The autopilot: whatever the engine's own rule says. This is how the league ran before agents."""
    name = "autopilot"

    def choose(self, dp: DecisionPoint):
        return dp.default, "autopilot"


class RandomLegalDriver:
    """Picks any legal option at random. The pick depends only on (seed, decision id), so it is replayable in any order."""
    name = "random-legal"

    def __init__(self, seed: int = 0):
        self.seed = seed

    def choose(self, dp: DecisionPoint):
        r = random.Random(f"{self.seed}-{dp.id}")
        return r.choice(dp.option_ids), "random legal choice"


class ReplayDriver:
    """Plays back a recorded choice log; a decision that is not in the log goes to the autopilot."""
    name = "replay"

    def __init__(self, log: List[dict]):
        self.by_id = {e["id"]: e for e in log}

    def choose(self, dp: DecisionPoint):
        e = self.by_id.get(dp.id)
        if e is None:
            return dp.default, "replayed"
        return dict(choice=e["chosen"], reason=e.get("reason", ""), note=e.get("note", ""))      # reason and note come back too, so the cards are identical


class PerTeamDriver:
    """Different drivers for different teams (for example, agents for some owners and the autopilot for the rest)."""
    name = "per-team"

    def __init__(self, drivers: Dict[int, object], default=None):
        self.drivers, self.fallback = drivers, default or PolicyDriver()

    def driver_for(self, dp: DecisionPoint):
        return self.drivers.get(dp.team_id, self.fallback)

    def choose(self, dp: DecisionPoint):
        return self.driver_for(dp).choose(dp)


class AgentDriver:
    """Calls real agents, up to `workers` at a time. `ask` receives dp.public() (plain data) and returns {"choice": option id,
    "reason": text, "note": text} or a bare option id. If it raises or takes longer than `timeout` seconds the guard falls back to
    the autopilot. Decisions that do not depend on each other arrive together (choose_many) and are answered in parallel."""
    name = "agent"

    def __init__(self, ask: Callable[[dict], object], timeout: float = 30.0, workers: int = DEFAULT_WORKERS):
        self.ask, self.timeout, self.workers = ask, timeout, workers
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=workers)

    def choose(self, dp: DecisionPoint):
        fut = self._pool.submit(self.ask, dp.public())
        return fut.result(timeout=self.timeout)

    def choose_many(self, dps: List[DecisionPoint]) -> list:
        """One answer per decision, in order: a result, or the exception that stopped it (a timeout counts as no answer)."""
        out: list = [None] * len(dps)
        for s in range(0, len(dps), self.workers):
            futs = {i: self._pool.submit(self.ask, dps[i].public()) for i in range(s, min(len(dps), s + self.workers))}
            done, _ = concurrent.futures.wait(list(futs.values()), timeout=self.timeout)
            for i, f in futs.items():
                if f in done:
                    try:
                        out[i] = f.result()
                    except Exception as e:                              # noqa: BLE001
                        out[i] = e
                else:
                    f.cancel()
                    out[i] = concurrent.futures.TimeoutError()
        return out


# ---- the guard ------------------------------------------------------------------------------------------
def _parse(res) -> Tuple[object, str, str]:
    if isinstance(res, dict):
        return res.get("choice"), res.get("reason", ""), res.get("note", "")
    if isinstance(res, tuple) and len(res) == 3:
        return res
    if isinstance(res, tuple) and len(res) == 2:
        return res[0], res[1], ""
    return res, "", ""


def _plain(x, limit: int) -> str:
    """Whatever an agent says is stored as short plain text, never obeyed."""
    if not isinstance(x, str):
        return ""
    return " ".join("".join(ch for ch in x if ch.isprintable() or ch.isspace()).split())[:limit]


def _next_id(lg, dp: DecisionPoint, taken: set) -> str:
    n = sum(1 for e in lg.choice_log if e["year"] == dp.year and e["kind"] == dp.kind and e["team"] == dp.team_id) + 1
    while f"{dp.year}-{dp.kind}-{dp.team_id:02d}-{n}" in taken:
        n += 1
    return f"{dp.year}-{dp.kind}-{dp.team_id:02d}-{n}"


def decide_many(lg, dps: List[DecisionPoint]) -> List[str]:
    """Run decisions that do not depend on each other through the drivers and the guard, together. Returns the id of the option
    applied for each, in order. The answers are applied and logged in the order given, so the history is the same however the
    drivers were scheduled."""
    taken: set = set()
    for dp in dps:
        dp.id = _next_id(lg, dp, taken)
        taken.add(dp.id)
    base = getattr(lg, "driver", None) or PolicyDriver()
    drivers = [base.driver_for(dp) if hasattr(base, "driver_for") else base for dp in dps]
    answers: list = [None] * len(dps)
    for drv in {id(d): d for d in drivers}.values():
        idx = [i for i, d in enumerate(drivers) if d is drv]
        if hasattr(drv, "choose_many") and len(idx) > 1:
            for i, a in zip(idx, drv.choose_many([dps[i] for i in idx])):
                answers[i] = a
        else:
            for i in idx:
                try:
                    answers[i] = drv.choose(dps[i])
                except Exception as e:                                  # noqa: BLE001
                    answers[i] = e
    picks = []
    for dp, drv, ans in zip(dps, drivers, answers):
        status, reason, note = "ok", "", ""
        if isinstance(ans, concurrent.futures.TimeoutError):
            choice, status = None, "no_answer"
        elif isinstance(ans, BaseException):                            # a broken driver never stops the league
            choice, status = None, f"driver_error:{type(ans).__name__}"
        else:
            try:
                choice, reason, note = _parse(ans)
            except Exception as e:                                      # noqa: BLE001
                choice, status = None, f"driver_error:{type(e).__name__}"
        if status == "ok" and not (isinstance(choice, str) and choice in dp.option_ids):
            status = "invalid_choice"
        chosen = choice if status == "ok" else dp.default
        reason, note = _plain(reason, MAX_REASON), _plain(note, MAX_NOTE)
        entry = dict(id=dp.id, year=dp.year, kind=dp.kind, team=dp.team_id, actor=dp.actor_kind, options=dp.option_ids,
                     default=dp.default, chosen=chosen, driver=getattr(drv, "name", "driver"), status=status, reason=reason)
        if note:
            entry["note"] = note
            _keep_note(dp.actor, dp.year, dp.kind, note)
        lg.choice_log.append(entry)
        picks.append(chosen)
    return picks


def _keep_note(actor, year: int, kind: str, text: str):
    """A note to self goes on the card of the one who wrote it, capped. The engine never reads it."""
    notes = getattr(actor, "notes", None)
    if notes is None:
        return
    notes.append(dict(year=year, kind=kind, text=text))
    del notes[:-NOTES_KEEP]


def decide(lg, dp: DecisionPoint) -> str:
    """Run one decision through the driver and the guard. Returns the id of the option that is applied."""
    return decide_many(lg, [dp])[0]
