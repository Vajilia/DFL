"""Founding Day: 1 January 2000, when the league opens (the Commissioner, 2026-10-11 and 12).

Every player begins as a rookie fresh from college (a college career and a one-paragraph backstory on her card, nothing else; no pro past), and so does
every career in the league: a CEO, a GM, a head coach and two coordinators are seated at each club, and the roster and practice squad are assigned from
the candidate pools by a seeded draw. No agent decides anything on Founding Day and none is needed: nothing here has a history yet for a choice to turn on.
The leftover candidates are the league's first coaching pool and its first free agents. From the first season on, the decisions belong to the agents.

This module writes the RECORD of that assignment, as a dated story: the order in which the clubs were completed (a seeded lottery), when each person was
named (spread across the offseason windows of calendar_dfl.py: the hiring window, the draft days, the camp and the cutdown) and a short account of each
club. Every sentence is written from facts on the cards; nothing in it is a reason that was invented, so the cards can inherit it as backstory without
the agents ever acting on a motive that never existed. The provenance is stated plainly in the record: a seeded assignment, no decision made. The engine
never reads it.

    lg, rng = open_league(seed)        # a rookie league with its Founding Day record
"""
from __future__ import annotations

import datetime as dt
import random
from typing import Tuple

import calendar_dfl as K
import cards as C
import prospects as PR

YEAR = 2000
PROVENANCE = ("Founding Day: a seeded assignment from the candidate pools. No agent and no rule made a choice; there was nothing yet to choose on. "
              "The coaches left over became the first coaching pool.")


def open_league(seed: int, **kw) -> Tuple[object, random.Random]:
    """A new league on Founding Day: only rookies, and the record of how the clubs came together."""
    from league import new_league
    rng = random.Random(seed)
    lg = new_league(rng, rosters=True, founding="rookies", **kw)
    describe(lg)
    return lg, rng


def _spread(start: dt.date, end: dt.date, slot: int, n: int = 48) -> dt.date:
    span = (end - start).days
    return start + dt.timedelta(days=(span * (slot - 1)) // max(1, n - 1))


def _person(card) -> str:
    return f"{card.name} ({card.trait.lower()})" if getattr(card, "trait", "") else card.name


def describe(lg) -> dict:
    """Mark every player a founding rookie, give each a backstory, and write the dated record on `lg.founding`."""
    seed = lg.card_seed
    r = C._rng(seed, "founding-order")
    order = [t.id for t in lg.teams]
    r.shuffle(order)                                              # the lottery: the order in which the clubs were completed
    slot = {tid: i + 1 for i, tid in enumerate(order)}
    off = {e.name: e for e in K.offseason(YEAR)}
    draft = off["draft"]
    events, teams = [], {}
    import enrichment as EN
    for t in lg.teams:
        people = [p for p in list(t.roster) + list(t.practice_squad)]
        for p in people:
            o = PR.ensure_origin(seed, p, 0)
            o["founding"] = True
            if p.card is not None:
                p.card.career.append({"year": 0, "event": "founding class", "team": t.id}) if not any(e["event"] == "founding class" for e in p.card.career) else None
        for p in people:
            EN.ensure_bio(lg, p, 0)
        n = slot[t.id]
        d_ceo = K.fmt(dt.date(YEAR, 1, 1))
        d_gm = _spread(dt.date(YEAR, 1, 3), dt.date(YEAR, 1, 20), n)
        d_hc = _spread(dt.date(YEAR, 1, 21), dt.date(YEAR, 2, 5), n)
        d_co = _spread(dt.date(YEAR, 2, 6), dt.date(YEAR, 2, 14), n)
        d_ro = draft.start + dt.timedelta(days=(n - 1) // 16)
        d_ps = off["camp"].start
        d_cut = off["cutdown"].start
        own, gm, hc, oc, dc = t.owner, t.gm, t.coach, t.oc, t.dc
        top = max(t.roster, key=lambda p: (p.ovr, -p.id))
        colleges = {p.origin["college"] for p in t.roster}
        ev = [(dt.date(YEAR, 1, 1), "ceo", f"{t.name}: {own.name} takes the CEO's seat."),
              (d_gm, "gm", f"{t.name}: {gm.name} is named general manager."),
              (d_hc, "head_coach", f"{t.name}: {hc.name} is named head coach."),
              (d_co, "coordinators", f"{t.name}: {oc.name if oc else 'no one'} (offense) and {dc.name if dc else 'no one'} (defense) complete the staff."),
              (d_ro, "roster", f"{t.name}: {len(t.roster)} players assigned in the Founding Class."),
              (d_ps, "practice_squad", f"{t.name}: {len(t.practice_squad)} more arrive for the practice squad as camp opens."),
              (d_cut, "cutdown", f"{t.name}: the roster stands at {len(t.roster)} for the first season.")]
        events += [dict(date=d.isoformat(), team=t.id, kind=k, text=x) for d, k, x in ev]
        mean_age = sum(p.age for p in t.roster) / len(t.roster)
        story = (f"{t.name} was the {_ordinal(n)} club completed on Founding Day. {_person(own)} is its CEO; {_person(gm)} is general manager and {_person(hc)} head coach, "
                 f"with {oc.name if oc else 'no one'} calling the offense and {dc.name if dc else 'no one'} the defense. The {len(t.roster)} players on the first roster "
                 f"average {mean_age:.1f} years old and come from {len(colleges)} colleges; the best of them is {top.card.name}, a {top.pos} from {top.origin['college']}, "
                 f"rated {C.tier_label(top.ovr).lower()}.")
        teams[str(t.id)] = dict(slot=n, story=story, ceo=own.name, gm=gm.name, head_coach=hc.name, oc=oc.name if oc else None, dc=dc.name if dc else None,
                                roster=len(t.roster), practice_squad=len(t.practice_squad), best_player=top.card.name, colleges=len(colleges))
    events.sort(key=lambda e: (e["date"], e["team"], e["kind"]))
    lg.founding = dict(date=dt.date(YEAR, 1, 1).isoformat(), class_of="rookies", provenance=PROVENANCE, order=order, teams=teams, events=events,
                       first_game=K.opener(YEAR).isoformat(), pool=dict(free_agents=len(lg.free_agents), free_coaches=len(lg.free_coaches), free_gms=len(lg.free_gms)))
    return lg.founding


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def story(lg, team_id: int) -> str:
    return lg.founding["teams"][str(team_id)]["story"] if lg.founding else ""
