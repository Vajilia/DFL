"""Living cards (Phase 4c): the same bones for every coach, general manager and CEO, as players already have.

The Commissioner's rule (2026-10-04): the cards are living, persistent people. Each starts with ratings, an archetype (her soul) and a
personality, and these change over time. There are no designated legends and no limit on greatness: a legend is something the
media notices and the Hall of Fame confers (recognition.py), never a flag a person is born with.

What is fixed and what moves (the same split as on a player card):

  fixed   name, hometown, path, SOUL (the best and the worst of her ratings at birth, so her archetypes), the SHAPE of her
          ratings (each one relative to her own average), ego, temperament, pressure thresholds
  moves   age, ratings (they grow toward a hidden potential, plateau, then fade; the shape stays), how she rates herself
          (perceived ratings lag the truth), her core personality (only inside the traits her soul allows), team, honors,
          esteem and standing (recognition.py)
  grows   career, relationships, decision log

Effect sizes are unchanged and still capped (small lifts, re-tested against the fair-competitiveness bands). The only change to
the effects is that they are measured against the league's current average for that role (a "reference"), so a league whose
coaches grow better or worse together does not drift in talent: the lift of an average coach is always zero.

Every random draw here comes from a generator private to the card and the year, never the engine's stream.

All numbers are PLACEHOLDER dials, not league rules.
"""
from __future__ import annotations

import random
from typing import Dict, List, Tuple

import card_pools as CP

# ---- dials ------------------------------------------------------------------------------------
SOUL_PULL = 0.35                 # each year her ratings move this far back toward the shape her soul gives them
EGO_SD, EGO_CLIP = 4.0, 10.0
PERCEPTION_LAG, PERCEPTION_NOISE = 0.35, 1.0
CONFIDENCE_WEIGHT, CONFIDENCE_SCALE = 0.9, 8.0
TRAIT_SWITCH_MARGIN = 0.15
TEMPER_SD = 0.12
BASE_WEIGHTS = (0.60, 0.40, 0.25, 0.15)
RATING_SD = 14.0                 # new people are drawn around 50 with this spread

# coaches and general managers: a career curve
GROW_RATE = 0.15                 # share of the gap to her hidden potential that she closes each year while young
POTENTIAL_MEAN, POTENTIAL_SD = 5.0, 6.0   # how far above her starting level her ceiling sits (never below)
PEAK_FROM, DECLINE_FROM = 52, 62          # growth stops at 52; from 62 she loses DECLINE points a year, more each year after
DECLINE = 0.5
LEVEL_NOISE, ATTR_NOISE = 0.8, 0.6
COACH_RETIRE_FROM, GM_RETIRE_FROM = 60, 62
COACH_MAX_AGE, GM_MAX_AGE = 74, 76
# CEOs: ratings stay near where they began (an anchor), and her popularity follows her fans
OWNER_ANCHOR_PULL = 0.25
OWNER_NOISE = 0.8
OWNER_POPULARITY_FOLLOW = 2.0    # rating points a year per unit of approval above or below one half
# the people no team employs keep living for a while
FREE_AGENT_MAX_YEARS = 4         # an unemployed coach or GM who is still unhired after this many years drifts out of the business
FREE_AGENT_MAX_AGE = 66

KIND_ATTRS = {"coach": ("offense", "defense", "development", "gamecraft", "discipline", "motivation"),
              "gm": ("scouting", "negotiation", "evaluation", "trades", "cap_sense"),
              "owner": ("patience", "ambition", "involvement", "popularity", "business")}
KIND_ARCH = {"coach": CP.COACH_ARCHETYPES, "gm": CP.GM_ARCHETYPES, "owner": CP.OWNER_ARCHETYPES}
KIND_TRAITS = {"coach": CP.COACH_TRAITS, "gm": CP.GM_TRAITS, "owner": CP.OWNER_TRAITS}

# The personalities each strength allows, most natural first. A person's core trait is always one of the four her soul allows.
FAMILIES = {
    "coach": {"offense": ["Tactician", "Innovator", "Gambler", "Steady Hand"],
              "defense": ["Disciplinarian", "Tactician", "Steady Hand", "Survivor"],
              "development": ["Developer", "Players' Coach", "Steady Hand", "Innovator"],
              "gamecraft": ["Tactician", "Gambler", "Survivor", "Steady Hand"],
              "discipline": ["Disciplinarian", "Steady Hand", "Survivor", "Tactician"],
              "motivation": ["Players' Coach", "Developer", "Innovator", "Survivor"]},
    "gm": {"scouting": ["Talent Hawk", "Gambler", "Planner", "Loyal Lieutenant"],
           "negotiation": ["Dealmaker", "Cold Realist", "Loyal Lieutenant", "Planner"],
           "evaluation": ["Cold Realist", "Talent Hawk", "Planner", "Dealmaker"],
           "trades": ["Dealmaker", "Gambler", "Cold Realist", "Talent Hawk"],
           "cap_sense": ["Planner", "Cold Realist", "Dealmaker", "Loyal Lieutenant"]},
    "owner": {"patience": ["Patient Steward", "Legacy Builder", "Local Hero", "Penny-Pincher"],
              "ambition": ["Glory Hunter", "Legacy Builder", "Showwoman", "Opportunist"],
              "involvement": ["Meddler", "Legacy Builder", "Glory Hunter", "Patient Steward"],
              "popularity": ["Local Hero", "Showwoman", "Glory Hunter", "Patient Steward"],
              "business": ["Penny-Pincher", "Opportunist", "Legacy Builder", "Patient Steward"]},
}
for _k, _fam in FAMILIES.items():
    assert set(_fam) == set(KIND_ATTRS[_k]), _k
    assert set(t for f in _fam.values() for t in f) == set(KIND_TRAITS[_k]), _k
# How a trait leans with confidence: + grows when she overrates herself, - grows when she doubts herself.
CONFIDENCE_LOAD = {"Gambler": 1.0, "Showwoman": 1.0, "Glory Hunter": 0.8, "Innovator": 0.7, "Talent Hawk": 0.5, "Meddler": 0.5,
                   "Opportunist": 0.4, "Dealmaker": 0.4, "Tactician": 0.4, "Legacy Builder": 0.3, "Disciplinarian": 0.2,
                   "Cold Realist": 0.2, "Players' Coach": -0.1, "Local Hero": -0.2, "Developer": -0.2, "Steady Hand": -0.4,
                   "Loyal Lieutenant": -0.4, "Patient Steward": -0.5, "Penny-Pincher": -0.6, "Planner": -0.7, "Survivor": -0.8}
assert all(t in CONFIDENCE_LOAD for k in KIND_TRAITS for t in KIND_TRAITS[k])


def rng(seed: int, *key) -> random.Random:
    return random.Random("-".join(str(k) for k in (seed,) + key))


def ident(card) -> int:
    for f in ("cid", "gid", "oid"):
        if hasattr(card, f):
            return getattr(card, f)
    raise TypeError(card)


def level(card) -> float:
    return sum(card.ratings.values()) / len(card.ratings)


def clip(x: float) -> float:
    return max(1.0, min(100.0, x))


# ---- birth: the soul -------------------------------------------------------------------------
def give_soul(card, kind: str, r: random.Random, age: int):
    """Read the soul off the ratings she is born with, and set the fixed parts of her mind. Her first personality is an
    expression of that soul."""
    attrs = KIND_ATTRS[kind]
    lv = level(card)
    card.soul_pos = max(attrs, key=lambda a: card.ratings[a])
    card.soul_neg = min(attrs, key=lambda a: card.ratings[a])
    card.family = list(FAMILIES[kind][card.soul_pos])
    card.shape = {a: card.ratings[a] - lv for a in attrs}
    card.anchor = dict(card.ratings)
    card.ego = max(-EGO_CLIP, min(EGO_CLIP, r.gauss(0.0, EGO_SD)))
    card.temper = {t: r.gauss(0.0, TEMPER_SD) for t in card.family}
    card.perceived = {a: card.ratings[a] + card.ego + r.gauss(0.0, 1.5) for a in attrs}
    card.potential = lv + (max(0.0, r.gauss(POTENTIAL_MEAN, POTENTIAL_SD)) if (kind != "owner" and age < PEAK_FROM) else 0.0)
    card.trait = express(card)
    card.wants, card.fears = KIND_TRAITS[kind][card.trait]


def soul_labels(card, kind: str) -> Tuple[str, str]:
    arch = KIND_ARCH[kind]
    return arch[card.soul_pos][0], arch[card.soul_neg][1]


# ---- the mind ----------------------------------------------------------------------------------
def confidence_gap(card) -> float:
    return sum(card.perceived[a] - card.ratings[a] for a in card.ratings) / len(card.ratings)


def confidence(card) -> float:
    return max(-1.0, min(1.0, confidence_gap(card) / CONFIDENCE_SCALE))


def trait_scores(card) -> Dict[str, float]:
    conf = confidence(card)
    return {t: BASE_WEIGHTS[i] + CONFIDENCE_WEIGHT * CONFIDENCE_LOAD[t] * conf + card.temper[t] for i, t in enumerate(card.family)}


def express(card) -> str:
    sc = trait_scores(card)
    return max(sc, key=sc.get)


def evolve_mind(card, kind: str, seed: int, year: int):
    r = rng(seed, "mind", kind, ident(card), year)
    for a in card.ratings:
        card.perceived[a] += PERCEPTION_LAG * ((card.ratings[a] + card.ego) - card.perceived[a]) + r.gauss(0.0, PERCEPTION_NOISE)
    sc = trait_scores(card)
    best = max(sc, key=sc.get)
    if best != card.trait and sc[best] - sc[card.trait] >= TRAIT_SWITCH_MARGIN:
        card.career.append({"year": year, "event": "personality_shift", "from": card.trait, "to": best,
                            "confidence": round(confidence(card), 2)})
        card.trait = best
        card.wants, card.fears = KIND_TRAITS[kind][best]


# ---- growth ------------------------------------------------------------------------------------
def age_step(age: int, lv: float, potential: float) -> float:
    """How much her overall level changes this year."""
    if age <= PEAK_FROM:
        return GROW_RATE * max(0.0, potential - lv)
    if age <= DECLINE_FROM:
        return 0.0
    return -DECLINE * (age - DECLINE_FROM)


def grow(card, kind: str, seed: int, year: int, approval: float = None):
    """One year of her career. Coaches and GMs follow the career curve; CEOs stay near their anchor, and a CEO's popularity
    follows her fans. In both cases the ratings are pulled back to the shape the soul gave them. Then her mind moves."""
    r = rng(seed, "grow", kind, ident(card), year)
    attrs = KIND_ATTRS[kind]
    if kind == "owner":
        for a in attrs:
            card.ratings[a] = clip(card.ratings[a] + OWNER_ANCHOR_PULL * (card.anchor[a] - card.ratings[a]) + r.gauss(0.0, OWNER_NOISE))
        if approval is not None:
            card.ratings["popularity"] = clip(card.ratings["popularity"] + OWNER_POPULARITY_FOLLOW * (approval - 0.5))
    else:
        lv0 = level(card)
        dl = age_step(card.age, lv0, card.potential) + r.gauss(0.0, LEVEL_NOISE)
        for a in attrs:
            target = lv0 + dl + card.shape[a]
            moved = card.ratings[a] + dl
            card.ratings[a] = clip(moved + SOUL_PULL * (target - moved) + r.gauss(0.0, ATTR_NOISE))
        card.potential = max(card.potential, level(card)) if card.age <= PEAK_FROM else level(card)
    card.ratings = {a: round(v, 1) for a, v in card.ratings.items()}
    card.history.append({"year": year, "age": card.age, "level": round(level(card), 1)})
    evolve_mind(card, kind, seed, year)


# ---- the league's reference: effects are measured against the current average -------------------
def refresh_refs(lg):
    """The mean rating of the head coaches and GMs on the job right now. A person's effect is her rating against this, so the
    effect of the average person on the job is exactly zero whatever careers do to the ratings."""
    refs = {}
    for kind, getter in (("coach", lambda t: t.coach), ("gm", lambda t: t.gm)):
        seated = [getter(t) for t in lg.teams if getter(t) is not None]
        if seated:
            refs[kind] = {a: sum(c.ratings[a] for c in seated) / len(seated) for a in KIND_ATTRS[kind]}
    lg.refs = refs
    for t in lg.teams:
        for kind, c in (("coach", t.coach), ("gm", t.gm)):
            if c is not None:
                c.ref = refs.get(kind)


def seat_ref(lg, kind: str, card):
    card.ref = getattr(lg, "refs", {}).get(kind)


def rel(card, attr: str) -> float:
    """A rating against the reference (50 until a league has set one)."""
    ref = getattr(card, "ref", None)
    return card.ratings[attr] - (ref[attr] if ref else 50.0)


# ---- retirement --------------------------------------------------------------------------------
def retire_chance(kind: str, age: int) -> float:
    start = COACH_RETIRE_FROM if kind == "coach" else GM_RETIRE_FROM
    return 0.03 if age < start else min(1.0, 0.03 + 0.07 * (age - start + 1))


def retires(card, kind: str, seed: int, year: int) -> bool:
    mx = COACH_MAX_AGE if kind == "coach" else GM_MAX_AGE
    r = rng(seed, f"{kind}ret", ident(card), year)
    return card.age >= mx or r.random() < retire_chance(kind, card.age)


def free_pool_season(lg, year: int):
    """People between jobs live on: they age, change, may retire, and after a few idle years drift out of the business."""
    for kind, pool_name in (("coach", "free_coaches"), ("gm", "free_gms")):
        pool = getattr(lg, pool_name)
        keep = []
        for c in pool:
            c.age += 1
            c.idle_years += 1
            grow(c, kind, lg.card_seed, year)
            if retires(c, kind, lg.card_seed, year) or c.idle_years > FREE_AGENT_MAX_YEARS or c.age > FREE_AGENT_MAX_AGE:
                c.career.append({"year": year, "event": "retired", "age": c.age})
                _mark_retired(c, kind)
            else:
                keep.append(c)
        setattr(lg, pool_name, keep)


def _mark_retired(c, kind: str):
    if kind == "coach":
        c.retired = True
    else:
        c.status = "retired"
    c.team_id = None
