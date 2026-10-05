"""Decision Points (Phase 4b): the one door every consequential choice goes through.

The principle (Jeph, 2026-10-04): the road, its guardrails and its traffic controls are code; the car is a card's capability
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

Everything an agent can do passes through a decision point built by the engine, so the guardrails are structural: the options on
offer, the caps on what an option can do, and the league-level rules. This module holds the machinery; the decisions themselves
are defined where they belong (staff_cards.py for the first pilot).
"""
from __future__ import annotations

import concurrent.futures
import random
from typing import Callable, Dict, List, Optional, Tuple

MAX_REASON = 400


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
        """What an agent is shown: the decider's own card, what she perceives, and the legal options. Nothing true-but-hidden."""
        a = self.actor
        return dict(id=self.id, kind=self.kind, year=self.year, team=self.team_id,
                    decider=dict(role=self.actor_kind, name=a.name, trait=getattr(a, "trait", None), wants=getattr(a, "wants", None),
                                 fears=getattr(a, "fears", None), ratings=dict(a.ratings), pressure=dict(a.pressure)),
                    context=self.context, options=[dict(o) for o in self.options],
                    instructions="Reply with the id of exactly one option, and optionally a short reason in plain words.")


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
        self.by_id = {e["id"]: e["chosen"] for e in log}

    def choose(self, dp: DecisionPoint):
        return self.by_id.get(dp.id, dp.default), "replayed"


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
    """Calls a real agent. `ask` receives dp.public() (plain data) and returns {"choice": option id, "reason": text} or a bare
    option id. If it raises or takes longer than `timeout` seconds the guard falls back to the autopilot."""
    name = "agent"

    def __init__(self, ask: Callable[[dict], object], timeout: float = 30.0):
        self.ask, self.timeout = ask, timeout
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=8)

    def choose(self, dp: DecisionPoint):
        fut = self._pool.submit(self.ask, dp.public())
        return fut.result(timeout=self.timeout)


# ---- the guard ------------------------------------------------------------------------------------------
def _parse(res) -> Tuple[object, str]:
    if isinstance(res, dict):
        return res.get("choice"), res.get("reason", "")
    if isinstance(res, tuple) and len(res) == 2:
        return res
    return res, ""


def decide(lg, dp: DecisionPoint) -> str:
    """Run one decision through the driver and the guard. Returns the id of the option that is applied."""
    n = sum(1 for e in lg.choice_log if e["year"] == dp.year and e["kind"] == dp.kind and e["team"] == dp.team_id) + 1
    dp.id = f"{dp.year}-{dp.kind}-{dp.team_id:02d}-{n}"
    driver = getattr(lg, "driver", None) or PolicyDriver()
    if hasattr(driver, "driver_for"):
        driver = driver.driver_for(dp)                       # the log names the driver that actually decided
    status, reason = "ok", ""
    try:
        choice, reason = _parse(driver.choose(dp))
    except concurrent.futures.TimeoutError:
        choice, status = None, "no_answer"
    except Exception as e:                                   # a broken driver never stops the league
        choice, status = None, f"driver_error:{type(e).__name__}"
    if status == "ok" and not (isinstance(choice, str) and choice in dp.option_ids):
        status = "invalid_choice"
    chosen = choice if status == "ok" else dp.default
    reason = reason if isinstance(reason, str) else ""
    reason = " ".join(reason.split())[:MAX_REASON]            # plain text, short; stored, never obeyed
    lg.choice_log.append(dict(id=dp.id, year=dp.year, kind=dp.kind, team=dp.team_id, actor=dp.actor_kind, options=dp.option_ids,
                              default=dp.default, chosen=chosen, driver=getattr(driver, "name", "driver"), status=status, reason=reason))
    return chosen
