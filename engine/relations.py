"""The GM and the head coach: equals with separate spheres, and a relationship that is theirs to grow or sour (the Commissioner, 2026-10-11).

Neither is obliged to cooperate with the other. Most pairs get on, some become a great team, a few turn into bitter lifelong enemies; that is a road each
side travels, for good or bad or indifferent. Each side keeps her own meter for the other on her card (`relationships`, -100 to +100, keys `coach:<id>` and
`gm:<id>`), so the two can disagree about how it is going. The meters move once a season, from:

  * how the club did (shared success warms, shared failure sours),
  * how well the roster the GM built suits the schemes the head coach runs (a roster that fits is a gift; one that fights the schemes is an insult),
  * their temperaments (some pairings click, some grate),
  * momentum (warm pairs tend to get warmer and cold pairs colder), against time, which slowly settles feeling back toward the ordinary, and
  * chance, drawn separately for each side.

The meters inform; they do not decide. No engine rule reads them, so the autopilot is unchanged. They are shown to each seat at its own decisions (the GM's
and the head coach's), to the CEO at her staff review, and they are what the Director will use to schedule a confrontation or a reconciliation scene.
Every draw comes from a private stream (the league's card seed, the pair and the year), never the engine's.
"""
from __future__ import annotations

import cards as C

START_MEAN, START_SD = 25.0, 22.0        # most pairs begin on good terms; some do not
SUCCESS_SWING = 24.0                      # a club that wins every game warms each side by half this a season, one that loses every game cools by it
FIT_SWING = 10.0                          # the average fit of the schemes in play, -1 to 1, times this
MOMENTUM = 0.08                           # each season a side moves this fraction of her current score further the way she already leans
SETTLE = 0.20                             # ...while time pulls this fraction of the way back toward where most pairs start (feelings fade; no one stays at +100 for ever)
NOISE_SD = 5.0                            # how much each side's season varies by chance
AFFINITY = 8.0                            # how much a clicking (or grating) temperament pair moves a side at the start; a fifth of it every season

CLICK = {("Players' Coach", "Loyal Lieutenant"), ("Developer", "Planner"), ("Steady Hand", "Planner"), ("Tactician", "Talent Hawk"),
         ("Gambler", "Gambler"), ("Innovator", "Dealmaker")}
GRATE = {("Disciplinarian", "Dealmaker"), ("Innovator", "Cold Realist"), ("Gambler", "Planner"), ("Survivor", "Cold Realist"),
         ("Players' Coach", "Cold Realist"), ("Disciplinarian", "Gambler")}

LABELS = ((60, "a great partnership"), (30, "they get on well"), (10, "friendly"), (-10, "indifferent"), (-40, "strained"), (-101, "bitter enemies"))


def label(score: float) -> str:
    return next(name for cut, name in LABELS if score >= cut)


def _affinity(coach, gm) -> float:
    pair = (coach.trait, gm.trait)
    return AFFINITY if pair in CLICK else -AFFINITY if pair in GRATE else 0.0


def _start(lg, coach, gm, side: str) -> int:
    r = C._rng(lg.card_seed, "gmhc-start", gm.gid, coach.cid, side)
    return int(max(-100, min(100, round(r.gauss(START_MEAN, START_SD) + _affinity(coach, gm)))))


def season(lg, year: int, pct: dict) -> dict:
    """One season of every club's GM-and-head-coach relationship. Returns counts for the log."""
    out = dict(pairs=0, started=0)
    if not getattr(lg, "interactions_on", True):          # a league with the relationship layer switched off keeps no meters
        return out
    for t in lg.teams:
        c, g = t.coach, t.gm
        if c is None or g is None or t.status != "active":
            continue
        out["pairs"] += 1
        kc, kg = f"coach:{c.cid}", f"gm:{g.gid}"
        fit = [v for k, v in (t.scheme_fit or {}).items() if k in set((t.scheme or {}).values())]
        fit_avg = sum(fit) / len(fit) if fit else 0.0
        win = (pct.get(t.id, 0.5) - 0.5) * SUCCESS_SWING
        for card, other, side in ((g, kc, "gm"), (c, kg, "coach")):
            if other not in card.relationships:
                card.relationships[other] = _start(lg, c, g, side)
                out["started"] += 1
            cur = card.relationships[other]
            r = C._rng(lg.card_seed, "gmhc", g.gid, c.cid, side, year)
            move = win + FIT_SWING * fit_avg + MOMENTUM * cur - SETTLE * (cur - START_MEAN) + _affinity(c, g) / 5.0 + r.gauss(0.0, NOISE_SD)
            card.relationships[other] = int(max(-100, min(100, round(cur + move))))
    return out


def view(t, seat: str) -> dict:
    """How one of the pair sees the other: `seat` is "gm" (her view of the head coach) or "coach" (his view of the GM)."""
    c, g = t.coach, t.gm
    if c is None or g is None:
        return {}
    mine, other_key = (g, f"coach:{c.cid}") if seat == "gm" else (c, f"gm:{g.gid}")
    score = mine.relationships.get(other_key)
    if score is None:
        return dict(how_you_get_on="new to each other; no history yet")      # a new pairing starts its meter at the next season's turn
    return dict(how_you_get_on=label(score), score=score)


def gm_note(t) -> dict:
    """What the head coach is shown about the general manager at her own decisions. The GM has no say in coaching; neither is obliged to the other."""
    g = t.gm
    if g is None:
        return dict(your_gm="none at present")
    return dict(your_gm=dict(name=g.name, personality=g.trait, **view(t, "coach"),
                             note="She runs player personnel and you run coaching. You have no say in hers and she has no say in yours, and neither of you is "
                                  "obliged to cooperate. How that goes is a road you each travel."))


def pair_view(t) -> dict:
    """What the CEO is shown: how the two of them seem to get on, from the club's side (her read of each, not the scores)."""
    c, g = t.coach, t.gm
    if c is None or g is None:
        return {}
    a, b = g.relationships.get(f"coach:{c.cid}"), c.relationships.get(f"gm:{g.gid}")
    if a is None or b is None:
        return dict(gm_on_coach="new to each other", coach_on_gm="new to each other")
    return dict(gm_on_coach=label(a), coach_on_gm=label(b))
