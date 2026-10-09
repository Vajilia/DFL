"""The Interaction system, first slice (Phase 4a): the three Required interactions as real scenes.

From the rules text (the Commissioner's skeleton): when two cards collide in an Interaction they act in their own interests, each party
gives its own claim, and the Archive records "Party A claims / Party B claims / Evidence supports". Evidence defaults to truth.
Required interactions include Firing and Exile Determination, and the Recall Vote is a Crisis; all three already happened in
the engine as plain log lines (staff_cards.py). This module turns each into a scene.

What a scene does (and does not):
  * It NEVER changes an outcome. The decisions (who is fired, who is recalled, who is exiled) are still made by the same
    rules as before; the scene explains them. The check script proves it: a league plays out identically with scenes on or off.
  * It gives every party a claim, shaded by that party's personality and by how it rates itself. A coach who blames the roster
    may be right or may be exaggerating; the evidence section says which, from the engine's own numbers.
  * It moves relationships (-100 to +100 between cards, stored on each card) and writes each decider's decision log.
  * It is code-generated and deterministic. Every random draw comes from a generator private to the scene, never from the engine's
    stream. A prose layer can be written over the top later; it can change wording but never facts.

Everything here that is not in the rules text is an AI placeholder (the frames, the thresholds, the relationship amounts).
Each is a named dial.
"""
from __future__ import annotations

import statistics as st
from typing import Dict, List, Optional

import cards as C
import fan_media_cards as FM

# ---- dials (PLACEHOLDER) ----------------------------------------------------------------------
UNDERPERFORMED_GAP = -0.06     # a team won at least this much less (win%) than its roster predicts: ~1 game over a 17-game season
THIN_ROSTER_Z = -0.4           # a roster this many standard deviations below the league's average talent counts as thin
IMPROVING_STEP = 0.05          # a team up at least this much (win%) on last year is "improving"
LOYAL_CAPITAL = 0.55           # fans with this much Fan Capital have goodwill to defend a CEO with
CALLED_IT = 0.08               # an outlet "called it" if its forecast was within this much (win%) of the result
PRESS_HURT = -0.01             # the press cost a CEO at least this much approval ("it was the press")
OPTIMISTIC_OWNERS = {"Showwoman": 0.08, "Glory Hunter": 0.08, "Legacy Builder": 0.06, "Meddler": 0.04, "Local Hero": 0.04,
                     "Penny-Pincher": -0.02, "Opportunist": -0.02, "Patient Steward": -0.03}   # how much a CEO thinks fans like her more than they do
# relationship amounts (points on the -100..100 scale), before scaling by the card's own pressure thresholds
REL_FIRED_TO_OWNER = -25
REL_OWNER_TO_FIRED = -10
REL_STAFF_WITNESS_TO_OWNER = -5
REL_FANS_ON_FIRING = 4           # fans who wanted a change warm to the CEO a little (cold if the firing was a sweep)
REL_RECALLED_OWNER_TO_FANS = -40
REL_FANS_TO_RECALLED_OWNER = -30
REL_SURVIVOR = 10
REL_ELECTED = 20
REL_EXILE_BLAME = -10
REL_FANS_EXILE = -15

KEY = {"owner": lambda c: f"owner:{c.oid}", "coach": lambda c: f"coach:{c.cid}", "gm": lambda c: f"gm:{c.gid}",
       "fans": lambda c: f"fans:{c.team_id}", "press": lambda c: f"press:{c.mid}"}


def key(kind: str, card) -> str:
    return KEY[kind](card)


def _bump(card, other: str, delta: float):
    cur = card.relationships.get(other, 0)
    card.relationships[other] = int(max(-100, min(100, round(cur + delta))))


def _break(card, other: str, delta: float):
    """A break in a relationship: old goodwill does not cancel it. The score falls to (at most zero) plus the blow."""
    cur = min(card.relationships.get(other, 0), 0)
    card.relationships[other] = int(max(-100, min(100, round(cur + delta))))


def _scale(pressure: int) -> float:
    """A card with a high threshold feels a blow more (0.5 at 1, 1.5 at 100)."""
    return 0.5 + pressure / 100.0


def _shade(r, truth: float, bias: float, sd: float) -> float:
    return truth + bias + r.gauss(0.0, sd)


# ---- the evidence ---------------------------------------------------------------------------------
def snapshot(lg, year: int, pct: Dict[int, float]) -> dict:
    """Taken at the start of the season's accountability, before anyone is replaced. Holds the cards as they were."""
    strengths = {t.id: t.strength for t in lg.teams}
    mean = st.mean(strengths.values())
    sd = st.pstdev(strengths.values()) or 1.0
    prev = getattr(lg, "prev_pct", {})
    teams = {}
    for t in lg.teams:
        teams[t.id] = dict(owner=t.owner, coach=t.coach, gm=t.gm, fans=getattr(t, "fans", None),
                           strength=t.strength, z=(t.strength - mean) / sd, pct=pct.get(t.id, 0.5), prev=prev.get(t.id),
                           expected=0.5 + FM.FORECAST_SLOPE * t.strength, approval_before=t.owner.approval if t.owner else None)
    return dict(year=year, teams=teams, strengths=strengths)


def evidence(lg, ctx: dict, tid: int) -> dict:
    d = ctx["teams"][tid]
    ev = dict(record=round(d["pct"], 3), expected=round(d["expected"], 3), gap=round(d["pct"] - d["expected"], 3),
              strength_z=round(d["z"], 2), prev_record=None if d["prev"] is None else round(d["prev"], 3))
    div = lg.active_in_division(lg.by_id[tid].division_id)
    order = sorted((x.id for x in div), key=lambda i: -ctx["strengths"][i])
    ev["roster_rank_in_division"] = order.index(tid) + 1 if tid in order else None
    ev["division_size"] = len(order)
    fb = d["fans"]
    if fb is not None:
        ev["fan_capital"] = round(fb.capital, 3)
        ev["press_effect_on_approval"] = round(fb.last_sway, 3)
        ev["approval_before"] = None if d["approval_before"] is None else round(d["approval_before"], 3)
    ev["new_owner"] = False        # filled by the caller when a new CEO arrived this year
    outlet = _local_outlet(lg, tid)
    if outlet is not None and tid in outlet.forecasts:
        ev["local_forecast"] = round(outlet.forecasts[tid], 3)
        ev["local_forecast_miss"] = round(abs(outlet.forecasts[tid] - d["pct"]), 3)
    return ev


def supported(frame: str, ev: dict) -> bool:
    """Does the engine's own record back this frame? The only place that decides."""
    if frame == "results":
        return ev["record"] < 0.5
    if frame == "underperformed":
        return ev["gap"] <= UNDERPERFORMED_GAP
    if frame == "talent":
        return ev["strength_z"] <= THIN_ROSTER_Z
    if frame == "improving":
        return ev["prev_record"] is not None and ev["record"] >= ev["prev_record"] + IMPROVING_STEP
    if frame == "loyal":
        return ev.get("fan_capital", 0.0) >= LOYAL_CAPITAL
    if frame == "press":
        return ev.get("press_effect_on_approval", 0.0) <= PRESS_HURT
    if frame == "called_it":
        return ev.get("local_forecast_miss", 1.0) <= CALLED_IT
    if frame == "fresh_start":
        return bool(ev.get("new_owner"))
    return False


def _local_outlet(lg, tid):
    for m in getattr(lg, "media", []):
        if m.kind == "local" and m.team_id == tid and m.status == "active":
            return m
    return None


# ---- the scene record --------------------------------------------------------------------------------
def _scene(lg, year, kind, tid, trigger, ev, claims, outcome, verdict):
    n = sum(1 for e in lg.archive if e.get("event") == "interaction" and e["year"] == year and e["kind"] == kind and e["team"] == tid) + 1
    sc = dict(year=year, event="interaction", kind=kind, team=tid, id=f"{year}-{kind}-{tid:02d}-{n}", trigger=trigger,
              claims=[{k: v for k, v in c.items() if k != "card"} for c in claims], evidence=ev,
              supports=[c["role"] for c in claims if supported(c["frame"], ev)], verdict=verdict, outcome=outcome)
    lg.archive.append(sc)
    return sc


def _decide(card, sc, action: str):
    card.decision_log.append({"year": sc["year"], "interaction": sc["id"], "action": action})


def _fan_frame(fb) -> str:
    return "loyal" if fb.culture in ("Die-Hards", "Long-Suffering") else "results"


def _fan_text(fb, ev, owner, frame, trigger_kind) -> str:
    if frame == "loyal":
        return f"{fb.team_name} fans: \"We stand by our own, and we have {100 * ev['fan_capital']:.0f} points of goodwill banked. This town wanted {fb.wants}.\""
    return (f"{fb.team_name} fans: \"They finished {ev['record']:.0%}. We wanted {fb.wants} and we feared {fb.fears}; "
            f"{'that is what we got' if ev['record'] < 0.5 else 'we have no complaint about the record, but we are watching'}.\"")


def _press_claim(lg, tid, ev):
    m = _local_outlet(lg, tid)
    if m is None or "local_forecast" not in ev:
        return None
    text = (f"{m.name} ({m.voice}): \"We had them at {ev['local_forecast']:.0%}. They finished {ev['record']:.0%}. "
            f"{'We called it.' if ev['local_forecast_miss'] <= CALLED_IT else 'Nobody saw this coming.'}\"")
    return dict(role="press", name=m.name, frame="called_it", text=text, card=m)


# ---- Firing -------------------------------------------------------------------------------------
def firing_scene(lg, ctx, year, detail: dict):
    """detail: team, who ('coach' or 'gm'), card (the person fired), heat, CEO (card), reason."""
    tid, who, fired, owner = detail["team"], detail["who"], detail["card"], detail["owner"]
    d = ctx["teams"][tid]
    ev = evidence(lg, ctx, tid)
    ev["new_owner"] = detail["reason"] == "new CEO cleaned house"
    ev["heat"] = round(detail["heat"], 3)
    r = C._rng(lg.card_seed, "scene", "firing", tid, year, who)
    claims = []
    # the CEO
    if ev["new_owner"]:
        frame = "fresh_start"
        text = f"{owner.name} ({owner.trait}): \"New CEO, new staff. I wanted {owner.wants} and I wasn't going to ask {fired.name} for it.\""
    elif detail["reason"] == "CEO's judgment":
        frame = "results" if ev["record"] < 0.5 else "judgment"
        text = (f"{owner.name} ({owner.trait}): \"It was my call. I wanted {owner.wants}, and I did not think {fired.name} was the person to get it.\"")
    else:
        frame = "results" if owner.ratings["involvement"] >= 50 else "underperformed"
        gave = f"I gave her {fired.seasons_with_team + 1} season{'s' if fired.seasons_with_team else ''}" if who == "coach" else "I trusted her with the roster"
        patience = "I had no patience left" if owner.ratings["patience"] < 40 else "I was patient"
        what = (f"{ev['record']:.0%} is not what I bought this team for" if frame == "results"
                else f"the roster should have won about {ev['expected']:.0%} and they won {ev['record']:.0%}")
        text = f"{owner.name} ({owner.trait}): \"{what}. {gave}; {patience}.\""
    claims.append(dict(role="owner", name=owner.name, frame=frame, text=text, card=owner))
    # the person fired
    if who == "coach":
        improving = d["prev"] is not None and d["pct"] >= d["prev"] + IMPROVING_STEP
        frame = "improving" if improving else "talent"
        bias = (50.0 - fired.ratings["discipline"]) / 50.0 * 0.6          # a less disciplined coach blames the roster harder
        claimed = _shade(r, ev["strength_z"], -0.5 - bias, 0.2)
        text = (f"{fired.name} ({fired.trait}): \"We were up from {d['prev']:.0%} to {ev['record']:.0%}. You do not fire a team that is climbing.\"" if improving
                else f"{fired.name} ({fired.trait}): \"You gave me a roster {abs(claimed):.1f} deviations {'below' if claimed < 0 else 'above'} the league's average and expected a contender.\"")
    else:
        frame = "underperformed"
        text = f"{fired.name} ({fired.trait}): \"I built the roster and she lost games the roster should have won: {ev['record']:.0%} on a team that rates {ev['expected']:.0%}.\""
    claim = dict(role=who, name=fired.name, frame=frame, text=text, card=fired)
    if who == "coach" and frame == "talent":
        claim["claimed_z"] = round(claimed, 2)
    claims.append(claim)
    # the other half of the football staff
    other = d["gm"] if who == "coach" else d["coach"]
    if other is not None:
        frame = "underperformed" if who == "coach" else "talent"
        text = (f"{other.name} ({other.trait}): \"The roster was fine. The record was {ev['record']:.0%}, against {ev['expected']:.0%} on paper.\"" if who == "coach"
                else f"{other.name} ({other.trait}): \"I coached what I was handed, a roster {abs(ev['strength_z']):.1f} deviations {'below' if ev['strength_z'] < 0 else 'above'} average.\"")
        claims.append(dict(role="gm" if who == "coach" else "coach", name=other.name, frame=frame, text=text, card=other))
    fb = d["fans"]
    if fb is not None:
        frame = _fan_frame(fb)
        claims.append(dict(role="fans", name=f"{fb.team_name} fans", frame=frame, text=_fan_text(fb, ev, owner, frame, "firing"), card=fb))
        pc = _press_claim(lg, tid, ev)
        if pc:
            claims.append(pc)
    backed = supported(claims[0]["frame"], ev)
    if ev["new_owner"]:
        ruling = "sweep"
        verdict = (f"A sweep: the new CEO cleared the staff on arrival, whatever the record ({ev['record']:.0%} against {ev['expected']:.0%} on paper).")
    elif who == "coach" and supported("underperformed", ev) and backed:
        ruling = "fair"
        verdict = "The firing is backed by the record, and the roster does not excuse it: the team won well under what it was built to win."
    elif who == "gm" and supported("talent", ev) and backed:
        ruling = "fair"
        verdict = "The firing is backed by the record, and the roster does not excuse it: it was a thin roster."
    elif backed:
        ruling = "harsh"
        verdict = (f"A harsh firing: the record was poor ({ev['record']:.0%}), but "
                   + ("the roster explains it; the team won about what it was built to win." if who == "coach" else "the roster she built was not thin, so the shortfall was on the field."))
    else:
        ruling = "unfounded"
        verdict = "The firing is not backed by the record: the CEO's reason does not hold up."
    ev["ruling"] = ruling
    sc = _scene(lg, year, "firing", tid, f"CEO fired the {who} ({detail['reason']})", ev, claims,
                f"{fired.name} fired; replaced by a new {who}", verdict)
    # relationships: the fired person is hurt in proportion to how much loyalty matters to her
    me, oth = key(who, fired), key("owner", owner)
    _bump(fired, oth, REL_FIRED_TO_OWNER * _scale(fired.pressure["loyalty"]))
    _bump(owner, me, REL_OWNER_TO_FIRED * (0.5 if ev["new_owner"] else 1.0))
    if other is not None:
        _bump(other, oth, REL_STAFF_WITNESS_TO_OWNER * (2.0 if (other.pressure.get("loyalty", 50) > 60) else 1.0))
        _bump(other, me, 3 if not backed else 0)         # they feel for a colleague fired without cause
    if fb is not None:
        _bump(fb, oth, REL_FANS_ON_FIRING if (backed and not ev["new_owner"]) else -2)
        _bump(owner, key("fans", fb), 1 if backed else -1)
    _decide(owner, sc, f"fired {who} {fired.name} ({detail['reason']})")
    _decide(fired, sc, f"was fired by {owner.name}")
    return sc


# ---- Recall vote ----------------------------------------------------------------------------------
def recall_scene(lg, ctx, year, detail: dict):
    """detail: team, trigger, approval, share, result, CEO (old card), new_owner (card or None), candidates (cards)."""
    tid, owner = detail["team"], detail["owner"]
    d = ctx["teams"][tid]
    ev = evidence(lg, ctx, tid)
    ev["new_owner"] = False
    ev["recall_share"] = round(detail["share"], 3)
    ev["approval_at_vote"] = round(detail["approval"], 3)
    r = C._rng(lg.card_seed, "scene", "recall", tid, year)
    recalled = detail["result"] == "recalled"
    fb = d["fans"]
    claims = []
    # the CEO: believes fans like her more than they do, by an amount that depends on who she is
    thinks = max(0.0, min(1.0, _shade(r, detail["approval"], OPTIMISTIC_OWNERS.get(owner.trait, 0.0), 0.02)))
    if recalled and owner.pressure.get("media", 50) >= 55:
        frame, text = "press", f"{owner.name} ({owner.trait}): \"I thought we were at {thinks:.0%}. This is what the papers did to me, not what I did to this team.\""
    elif recalled:
        frame, text = "results", f"{owner.name} ({owner.trait}): \"I thought we were at {thinks:.0%}. The team lost, and the fans are blaming the person they can vote on.\""
    else:
        frame, text = "loyal", f"{owner.name} ({owner.trait}): \"I told you we were at {thinks:.0%}. The fans know what I stand for: {owner.wants}.\""
    claims.append(dict(role="owner", name=owner.name, frame=frame, text=text, card=owner))
    taste = fb.taste if fb is not None else "popularity"
    if fb is not None:
        frame = _fan_frame(fb)
        extra = (f" We wanted a CEO strong on {taste} and we chose {detail['new_owner'].name}." if recalled and detail.get("new_owner") is not None else "")
        claims.append(dict(role="fans", name=f"{fb.team_name} fans", frame=frame,
                           text=_fan_text(fb, ev, owner, frame, "recall") + extra, card=fb))
        pc = _press_claim(lg, tid, ev)
        if pc:
            claims.append(pc)
    new = detail.get("new_owner")
    if new is not None:
        cands = detail["candidates"]
        top = max(cands, key=lambda c: c.ratings[taste])
        claims.append(dict(role="new_owner", name=new.name, frame="mandate" if new is top else "chosen",
                           text=f"{new.name} ({new.trait}): \"Five of us stood. The fans wanted strength on {taste} and picked me. I want {new.wants}.\"", card=new))
        ev["elected_is_best_on_taste"] = new is top
    verdict = (f"{100 * detail['share']:.1f}% voted to recall (a majority of the 1,000,000 fans is needed): "
               + ("recalled." if recalled else "the CEO survives."))
    sc = _scene(lg, year, "recall_vote", tid, f"vote triggered by {detail['trigger']}", ev, claims,
                f"{owner.name} {'recalled; ' + new.name + ' elected from 5 candidates' if recalled else 'survives'}", verdict)
    # a mandate frame is supported by the data: the winner topped the candidates on the fans' taste
    if new is not None and ev.get("elected_is_best_on_taste") and "new_owner" not in sc["supports"]:
        sc["supports"].append("new_owner")
    if fb is not None:
        if recalled:
            _break(owner, key("fans", fb), REL_RECALLED_OWNER_TO_FANS * _scale(owner.pressure.get("recall", 50)))
            _break(fb, key("owner", owner), REL_FANS_TO_RECALLED_OWNER * _scale(fb.pressure.get("losing", 50)))
            if new is not None:
                _bump(fb, key("owner", new), REL_ELECTED)
                _bump(new, key("fans", fb), REL_ELECTED)
        else:
            warmth = max(0.2, 1.0 - 2.0 * detail["share"])          # surviving by a hair warms no one; a landslide does
            _bump(owner, key("fans", fb), REL_SURVIVOR * warmth)
            _bump(fb, key("owner", owner), REL_SURVIVOR * warmth / 2)
        _decide(fb, sc, "voted to recall the CEO" if recalled else "kept the CEO")
    _decide(owner, sc, "was recalled" if recalled else "survived a recall vote")
    if new is not None:
        _decide(new, sc, f"was elected by the fans of team {tid}")
    return sc


# ---- Exile determination ----------------------------------------------------------------------------
def exile_scene(lg, ctx, year, tid: int):
    d = ctx["teams"][tid]
    owner, coach, gm = d["owner"], d["coach"], d["gm"]
    ev = evidence(lg, ctx, tid)
    ev["new_owner"] = False
    r = C._rng(lg.card_seed, "scene", "exile", tid, year)
    claims = []
    blames_coach = (coach.heat >= gm.heat)
    frame = "underperformed" if blames_coach else "talent"
    target = coach if blames_coach else gm
    claims.append(dict(role="owner", name=owner.name, frame=frame, card=owner,
                       text=(f"{owner.name} ({owner.trait}): \"Fifth in the division, and I will say who is to blame: {target.name}. "
                             + (f"The roster rated {ev['expected']:.0%} and they won {ev['record']:.0%}." if blames_coach
                                else f"She built a roster that was {abs(ev['strength_z']):.1f} deviations {'below' if ev['strength_z'] < 0 else 'above'} the league's average.") + "\"")))
    improving = d["prev"] is not None and d["pct"] >= d["prev"] + IMPROVING_STEP
    bias = (50.0 - coach.ratings["discipline"]) / 50.0 * 0.6
    claimed = _shade(r, ev["strength_z"], -0.5 - bias, 0.2)
    claims.append(dict(role="coach", name=coach.name, frame="improving" if improving else "talent", card=coach,
                       **({} if improving else {"claimed_z": round(claimed, 2)}),
                       text=(f"{coach.name} ({coach.trait}): \"We went from {d['prev']:.0%} to {ev['record']:.0%}. Exile is a cruel verdict on a team that is climbing.\"" if improving
                             else f"{coach.name} ({coach.trait}): \"I was handed a roster {abs(claimed):.1f} deviations {'below' if claimed < 0 else 'above'} average and the schedule did the rest.\"")))
    claims.append(dict(role="gm", name=gm.name, frame="underperformed", card=gm,
                       text=f"{gm.name} ({gm.trait}): \"The roster was {ev['roster_rank_in_division']} of {ev['division_size']} in this division on paper. The record, {ev['record']:.0%}, was {abs(ev['gap']):.0%} {'below' if ev['gap'] < 0 else 'above'} what it should have been.\""))
    fb = d["fans"]
    if fb is not None:
        frame = _fan_frame(fb)
        claims.append(dict(role="fans", name=f"{fb.team_name} fans", frame=frame, text=_fan_text(fb, ev, owner, frame, "exile"), card=fb))
        pc = _press_claim(lg, tid, ev)
        if pc:
            claims.append(pc)
    cause = []
    if supported("talent", ev):
        cause.append("a thin roster")
    if supported("underperformed", ev):
        cause.append("under-delivery against the roster")
    verdict = ("Exile followed " + " and ".join(cause) + "." if cause else
               f"Neither a thin roster nor under-delivery explains it: the roster rated {ev['roster_rank_in_division']} of {ev['division_size']} in the division and the record is within {abs(ev['gap']):.0%} of expectation. Bad breaks.")
    sc = _scene(lg, year, "exile_determination", tid, "finished fifth in the division", ev, claims,
                f"Team {tid} is exiled for next season", verdict)
    _bump(owner, key("coach", coach), REL_EXILE_BLAME * (1.5 if blames_coach else 0.5))
    _bump(owner, key("gm", gm), REL_EXILE_BLAME * (0.5 if blames_coach else 1.5))
    _bump(coach, key("owner", owner), -5)
    _bump(gm, key("owner", owner), -5)
    if fb is not None:
        _bump(fb, key("owner", owner), REL_FANS_EXILE * _scale(fb.ratings["passion"]))
    _decide(owner, sc, f"blamed {target.name} for the exile")
    _decide(coach, sc, "was exiled with her team")
    _decide(gm, sc, "was exiled with her team")
    return sc


# ---- the hook ----------------------------------------------------------------------------------------
def season_scenes(lg, year: int, ctx: dict, out: dict, new_exiles) -> list:
    """Called at the end of staff_cards.season_end. Builds every scene for the season, in a fixed order."""
    scenes = []
    for tid in sorted(new_exiles):
        scenes.append(exile_scene(lg, ctx, year, tid))
    for v in out.get("vote_details", []):
        scenes.append(recall_scene(lg, ctx, year, v))
    for f in out.get("firing_details", []):
        scenes.append(firing_scene(lg, ctx, year, f))
    lg.prev_pct = {tid: d["pct"] for tid, d in ctx["teams"].items()}
    return scenes


# ---- the Archive's format ----------------------------------------------------------------------------
def render_scene(sc: dict, lg=None) -> str:
    team = lg.by_id[sc["team"]].name if lg is not None else f"Team {sc['team']}"
    L = [f"EVENT {sc['id']}  ({team}; {sc['kind'].replace('_', ' ')}; {sc['trigger']})"]
    for c in sc["claims"]:
        mark = "supported by the record" if c["role"] in sc["supports"] else "not supported by the record"
        if c["role"] in sc["supports"] and "claimed_z" in c and c["claimed_z"] - sc["evidence"]["strength_z"] < -0.5:
            mark = "supported, but overstated"
        label = {"gm": "GM", "fans": "The fans", "new_owner": "New CEO"}.get(c["role"], c["role"].title())
        L.append(f"├── {label} {'claim' if c['role'] == 'fans' else 'claims'}: {c['text']}  [{mark}]")
    e = sc["evidence"]
    facts = f"record {e['record']:.0%}, roster predicts {e['expected']:.0%}, roster {e['strength_z']:+.1f} deviations from average"
    L.append(f"└── Evidence supports: {sc['verdict']}  ({facts})")
    L.append(f"    Outcome: {sc['outcome']}")
    return "\n".join(L)
