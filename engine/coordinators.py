"""Coordinator cards (Step B of the ring of accountability): the offensive and defensive coordinators.

The Commissioner's ring (2026-10-09): the head coach hires and fires the two coordinators; the coordinators call the plays and the
schemes, and the head coach has veto power. Everyone answers up the ring (players to coaches, coaches and GMs to the CEO, the CEO to the
fans), and everyone's first priority is the Diamond Coronation.

What this module adds
  * a light card for each coordinator (two ratings: playcalling and vision), who ages, grows, fades and retires, and who is hired, kept
    or fired by the head coach through Decision Points (`hire_coordinator`, `coord_review`);
  * a yearly scheme: before the season each coordinator proposes how her unit will play (offense: pass, run or balanced; defense:
    blitz, coverage or balanced) through the Decision Point `coord_scheme`; the head coach may approve it or veto it
    (`scheme_veto`), and a veto sends the unit back to balanced and costs the coordinator standing with her boss;
  * the lift a team gets from its coaches. Before this step the head coach's own offense and defense ratings lifted the units; now the
    coordinator who calls the plays carries most of it (COORD_WEIGHT) and the head coach keeps the rest, plus a small scheme-fit lift:
    a scheme that suits the roster adds a little, one that fights it takes a little away (SCHEME_CAP).

Safety, as everywhere else: every effect is small and capped; a coordinator's effect is measured against the league's average
coordinator, so the average one is worth exactly zero; the card's random draws come from generators private to the card or the event,
never from the engine's stream; and the whole thing is re-tested against the fair-competitiveness bands.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import card_pools as CP
import cards as C
import living as LV

# ---- dials (PLACEHOLDER, not league rules) -------------------------------------------------------
COORD_ATTRS = ("playcalling", "vision")
COORD_POINTS_AT_100 = C.COACH_POINTS_AT_100     # a 100-rated play-caller (against the league's average one) is worth this much margin, as for a head coach
COORD_WEIGHT = 0.6                               # the share of a unit's coaching lift that comes from the coordinator; the head coach's own rating keeps the rest
SCHEME_CAP = 0.4                                 # a scheme that fits the roster perfectly adds this many points (one that fights it takes the same away)
SCHEMES = {"offense": ("balanced", "pass", "run"), "defense": ("balanced", "blitz", "coverage")}
LEAN_NAME = {"offense": "pass_minus_run", "defense": "rush_minus_coverage"}
FIT_CLIP = 2.0                                   # a roster's lean is measured in spreads from the league's mean and clipped at this many
VISION_BASE, VISION_SPAN = 0.25, 0.70            # chance the coordinator proposes the best-fitting scheme = base + span * vision / 100
SEE_SD = 0.6                                     # how blurred a person's view of the fit is at the worst (vision 0 or gamecraft 0); it sharpens with the rating
VETO_BAR = -0.15                                 # the head coach's rule: veto a proposal she sees fitting worse than this
OVERRULED_HEAT = 0.05                            # a vetoed coordinator's heat rises this much
FIRE_HEAT = 0.30                                 # a coordinator is fired when her heat tops this (the head coach's rule; the CEO's rule for a head coach is a little tighter)
CLEAN_HOUSE = 0.60                               # chance a new head coach sweeps out each coordinator he inherits
COORD_RETIRE_FROM, COORD_MAX_AGE = 62, 70
FREE_MAX_YEARS = 3                               # a coordinator between jobs for longer than this leaves the business
HIRE_POOL = 3                                    # candidates a head coach sees
CAND_BASE = 30000                                # candidate cards that are not hired are numbered from here, clear of every real id
NAME_BASE = 1000                                 # coordinators draw their names from their own stretch of the name grid (no numeral until the grid is used up)
AGE_RANGE = (33, 58)

SIDES = ("offense", "defense")
SEAT = {"offense": "oc", "defense": "dc"}
TITLE = {"offense": "offensive coordinator", "defense": "defensive coordinator"}


@dataclass
class CoordCard:
    cid: int
    first: str
    last: str
    age: int
    side: str                                   # "offense" or "defense"
    hometown: str
    ratings: Dict[str, float]                   # playcalling and vision (1-100)
    team_id: Optional[int] = None
    seasons_with_team: int = 0
    heat: float = 0.0
    status: str = "coordinator"                 # coordinator, between jobs, retired
    idle_years: int = 0
    potential: float = 0.0
    ref: Optional[Dict[str, float]] = None      # the league's average coordinator on her side (refresh_refs)
    trait: str = ""
    soul_pos: str = ""
    soul_neg: str = ""
    esteem: float = 0.0
    standing: str = ""
    wants: str = ""
    fears: str = ""
    pressure: Dict[str, int] = field(default_factory=dict)
    honors: List[dict] = field(default_factory=list)
    history: List[dict] = field(default_factory=list)
    notes: List[dict] = field(default_factory=list)
    relationships: Dict[str, int] = field(default_factory=dict)
    career: List[dict] = field(default_factory=list)
    decision_log: List[dict] = field(default_factory=list)

    @property
    def name(self) -> str:
        return f"{self.first} {self.last}"

    @property
    def points(self) -> float:
        """Her lift to her unit, in points of margin: her playcalling against the league's average coordinator on her side, capped."""
        m = COORD_POINTS_AT_100
        return max(-m, min(m, LV.rel(self, "playcalling") / 50.0 * m))


def make_coord_card(seed: int, cid: int, side: str, team_id: Optional[int] = None, age: Optional[int] = None) -> CoordCard:
    r = C._rng(seed, "coord", cid)
    first, last = C.make_name(seed + 51111, NAME_BASE + cid)
    ratings = {a: max(1.0, min(100.0, round(r.gauss(C.COACH_RATING_MEAN, C.COACH_RATING_SD), 1))) for a in COORD_ATTRS}
    if age is None:
        age = r.randint(*AGE_RANGE)
    lv = sum(ratings.values()) / len(ratings)
    card = CoordCard(cid=cid, first=first, last=last, age=age, side=side, hometown=r.choice(CP.HOMETOWNS), ratings=ratings, team_id=team_id,
                     potential=lv + (max(0.0, r.gauss(LV.POTENTIAL_MEAN, LV.POTENTIAL_SD)) if age < LV.PEAK_FROM else 0.0))
    card.history.append({"year": 0, "age": age, "level": round(lv, 1)})
    return card


# ---- seating --------------------------------------------------------------------------------------
def _seat(lg, t, side: str, year: int):
    c = make_coord_card(lg.card_seed, lg.new_coord_id(), side, t.id)
    c.career.append({"year": year, "event": "hired", "team": t.id})
    setattr(t, SEAT[side], c)
    lg.coords.append(c)
    return c


def init(lg, year: int = 0):
    """A coordinator on each side for every team that has none (a new league, or an old save that never had them)."""
    for t in lg.teams:
        for side in SIDES:
            if getattr(t, SEAT[side], None) is None:
                _seat(lg, t, side, year)


def seated(lg, side: str) -> list:
    return [c for c in (getattr(t, SEAT[side]) for t in lg.teams) if c is not None]


def refresh_refs(lg):
    """The mean rating of the coordinators on the job right now, per side. A coordinator's effect is her rating against this."""
    for side in SIDES:
        cs = seated(lg, side)
        if not cs:
            continue
        ref = {a: sum(c.ratings[a] for c in cs) / len(cs) for a in COORD_ATTRS}
        lg.refs[SEAT[side]] = ref
        for c in cs:
            c.ref = ref


# ---- the lift a team gets from its coaches (called by lineup.build_lineup) -------------------------------
def lifts(coach, team):
    """(offense lift, defense lift) in points: the head coach's own, blended with the coordinator who calls the plays, plus the scheme's fit."""
    o = coach.offense_points if coach is not None else 0.0
    d = coach.defense_points if coach is not None else 0.0
    oc, dc = getattr(team, "oc", None), getattr(team, "dc", None)
    fit, scheme = getattr(team, "scheme_fit", None) or {}, getattr(team, "scheme", None) or {}
    if oc is not None:
        o = (1.0 - COORD_WEIGHT) * o + COORD_WEIGHT * oc.points + SCHEME_CAP * fit.get(scheme.get("offense", "balanced"), 0.0)
    if dc is not None:
        d = (1.0 - COORD_WEIGHT) * d + COORD_WEIGHT * dc.points + SCHEME_CAP * fit.get(scheme.get("defense", "balanced"), 0.0)
    return o, d


# ---- how well a scheme suits a roster ---------------------------------------------------------------------
def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


def _leans(L) -> Dict[str, float]:
    """A lineup's raw lean on each side: how much stronger its passing units are than its running ones, and its pass rush than its coverage."""
    pass_u = _mean((L.qb_acc, L.qb_arm, L.qb_aware, L.rec, L.pass_block))
    run_u = _mean((L.run_block, L.rb_run))
    return {"offense": pass_u - run_u, "defense": L.pass_rush - L.coverage}


def preseason(lg, year: int):
    """Before the games: measure every roster's lean, let every coordinator propose a scheme, and let every head coach decide on it."""
    if not getattr(lg, "has_rosters", False):
        return
    import decisions as D
    import rosters
    from lineup import build_lineup
    init(lg, year)
    teams = [t for t in lg.teams if t.roster]
    raw = {t.id: _leans(build_lineup(t.id, rosters.game_roster(t), None)) for t in teams}
    z: Dict[str, Dict[int, float]] = {}
    for side in SIDES:
        xs = [raw[t.id][side] for t in teams]
        m = _mean(xs)
        sd = (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5 or 1.0
        z[side] = {t.id: max(-FIT_CLIP, min(FIT_CLIP, (raw[t.id][side] - m) / sd)) / FIT_CLIP for t in teams}
    for t in teams:
        fo, fd = z["offense"][t.id], z["defense"][t.id]
        t.scheme_fit = {"pass": fo, "run": -fo, "blitz": fd, "coverage": -fd}
    rank = {t.id: 1 + sum(1 for x in lg.teams if x.strength > t.strength) for t in teams}
    # 1. the proposals
    dps, meta = [], []
    for t in teams:
        for side in SIDES:
            c = getattr(t, SEAT[side])
            dps.append(_scheme_point(lg, t, side, c, year, rank[t.id], z[side][t.id]))
            meta.append((t, side, c))
    picks = D.decide_many(lg, dps)
    proposed = {}
    for (t, side, c), pick in zip(meta, picks):
        proposed[(t.id, side)] = pick
        c.decision_log.append({"year": year, "action": f"proposed the {pick} scheme"})
    # 2. the head coach's say (a balanced proposal needs none)
    vdps, vmeta = [], []
    for t in teams:
        for side in SIDES:
            s = proposed[(t.id, side)]
            if s != "balanced" and t.coach is not None:
                vdps.append(_veto_point(lg, t, side, getattr(t, SEAT[side]), s, year, rank[t.id]))
                vmeta.append((t, side, s))
    vpicks = D.decide_many(lg, vdps) if vdps else []
    vetoed = {(t.id, side) for (t, side, s), v in zip(vmeta, vpicks) if v == "veto"}
    for t in teams:
        t.scheme = {}
        for side in SIDES:
            c = getattr(t, SEAT[side])
            s = proposed[(t.id, side)]
            if (t.id, side) in vetoed:
                c.heat += OVERRULED_HEAT
                c.decision_log.append({"year": year, "action": f"was overruled by {t.coach.name} on the {s} scheme; the unit plays balanced"})
                t.coach.decision_log.append({"year": year, "action": f"vetoed {c.name}'s {s} scheme"})
                s = "balanced"
            t.scheme[side] = s


def _see(lg, t, side: str, year: int, who: str, rating: float, true: float) -> float:
    """What a person with this rating (1-100) sees of a fit that is really `true`: the truth blurred by a card-private draw."""
    r = C._rng(lg.card_seed, "seefit", who, t.id, side, year)
    return true + r.gauss(0.0, SEE_SD * (1.0 - rating / 100.0))


def _scheme_point(lg, t, side: str, c: CoordCard, year: int, rank: int, lean_z: float):
    import decisions as D
    fit = {"balanced": 0.0, "pass": lean_z, "run": -lean_z} if side == "offense" else {"balanced": 0.0, "blitz": lean_z, "coverage": -lean_z}
    seen = {s: round(_see(lg, t, side, year, f"coord{c.cid}", c.ratings["vision"], f), 2) if s != "balanced" else 0.0 for s, f in fit.items()}
    opts = [dict(id=s, label=f"Call it {s}", tags={"perceived_fit": seen[s]}) for s in SCHEMES[side]]
    order = sorted(fit, key=lambda s: (-fit[s], s))                          # the truly best-fitting first
    r = C._rng(lg.card_seed, "scheme", t.id, year, side)
    p_best = VISION_BASE + VISION_SPAN * c.ratings["vision"] / 100.0
    default = order[0] if r.random() < p_best else r.choice(order[1:])
    ctx = dict(role=TITLE[side], your_team_strength_rank=rank, your_roster_leans=round(seen["pass"] if side == "offense" else seen["blitz"], 2),
               leaning_means=("positive: the passing units are stronger than the running ones" if side == "offense"
                              else "positive: the pass rush is stronger than the coverage"),
               your_boss=t.coach.name if t.coach else None)
    return D.DecisionPoint("coord_scheme", year, t.id, "coordinator", c, ctx, opts, default, dict(team=t, fit=fit, strength_rank=rank))


def _veto_point(lg, t, side: str, c: CoordCard, scheme: str, year: int, rank: int):
    import decisions as D
    true = t.scheme_fit[scheme]
    sees = round(_see(lg, t, side, year, f"coach{t.coach.cid}", t.coach.ratings["gamecraft"], true), 2)
    opts = [dict(id="approve", label=f"Let {c.name} run the {scheme} scheme", tags={"your_view_of_fit": sees}),
            dict(id="veto", label=f"Veto it: the {side} plays balanced", tags={"your_view_of_fit": sees})]
    default = "veto" if sees < VETO_BAR else "approve"
    ctx = dict(coordinator=c.name, unit=side, proposed_scheme=scheme, your_view_of_fit=sees, your_team_strength_rank=rank,
               coordinator_view=dict(playcalling=c.ratings["playcalling"], vision=c.ratings["vision"]))
    return D.DecisionPoint("scheme_veto", year, t.id, "coach", t.coach, ctx, opts, default, dict(team=t, fit=true, strength_rank=rank))


# ---- the yearly review, firings and hires (called by staff_cards.season_end) --------------------------------
def _grow(lg, c: CoordCard, year: int):
    r = LV.rng(lg.card_seed, "coordgrow", c.cid, year)
    lv = LV.level(c)
    dl = LV.age_step(c.age, lv, c.potential) + r.gauss(0.0, LV.LEVEL_NOISE)
    for a in COORD_ATTRS:
        c.ratings[a] = round(LV.clip(c.ratings[a] + dl + r.gauss(0.0, LV.ATTR_NOISE)), 1)
    lv2 = LV.level(c)
    c.potential = max(c.potential, lv2) if c.age <= LV.PEAK_FROM else lv2
    c.history.append({"year": year, "age": c.age, "level": round(lv2, 1)})


def _retires(lg, c: CoordCard, year: int) -> bool:
    r = LV.rng(lg.card_seed, "coordret", c.cid, year)
    p = 0.03 if c.age < COORD_RETIRE_FROM else min(1.0, 0.03 + 0.07 * (c.age - COORD_RETIRE_FROM + 1))
    return c.age >= COORD_MAX_AGE or r.random() < p


def _free_pool_season(lg, year: int):
    keep = []
    for c in lg.free_coords:
        c.age += 1
        c.idle_years += 1
        _grow(lg, c, year)
        if _retires(lg, c, year) or c.idle_years > FREE_MAX_YEARS:
            c.status = "retired"
            c.career.append({"year": year, "event": "retired", "age": c.age})
        else:
            keep.append(c)
    lg.free_coords = keep


def _perceived(lg, t, c: CoordCard, year: int) -> dict:
    """A head coach sees a candidate's ratings blurred by her own gamecraft."""
    g = t.coach.ratings["gamecraft"] if t.coach is not None else 50.0
    r = C._rng(lg.card_seed, "seecoord", t.id, c.cid, year)
    sd = 8.0 * (1.0 - g / 100.0)
    return {a: round(max(1.0, min(100.0, c.ratings[a] + r.gauss(0.0, sd))), 1) for a in COORD_ATTRS}


def _release(lg, c: CoordCard, year: int):
    c.team_id, c.idle_years, c.status, c.heat = None, 0, "between jobs", 0.0
    lg.free_coords.append(c)


def _review_point(lg, t, year: int, new_hc: bool, defaults: dict):
    import decisions as D
    oc, dc = t.oc, t.dc
    cands = {s: c for s, c in (("oc", oc), ("dc", dc)) if c is not None}
    ids = ["keep_both"] + [f"fire_{s}" for s in cands] + (["fire_both"] if len(cands) == 2 else [])
    fo, fd = defaults.get("oc", False), defaults.get("dc", False)
    default = "fire_both" if fo and fd and len(cands) == 2 else "fire_oc" if fo else "fire_dc" if fd else "keep_both"
    opts = [dict(id=i, label=i.replace("_", " "), tags={"fires": {"keep_both": 0, "fire_both": 2}.get(i, 1)}) for i in ids]
    rank = 1 + sum(1 for x in lg.teams if x.strength > t.strength)
    ctx = dict(new_head_coach=new_hc, team_strength_rank=rank,
               coordinators={s: dict(name=c.name, unit=c.side, heat=round(c.heat, 2), years_here=c.seasons_with_team,
                                     seen=_perceived(lg, t, c, year)) for s, c in cands.items()})
    return D.DecisionPoint("coord_review", year, t.id, "coach", t.coach, ctx, opts, default, dict(team=t, strength_rank=rank))


def season(lg, year: int, pct: Dict[int, float], coach_changed) -> dict:
    """The offseason for coordinators: they age and change, some retire; each head coach reviews hers (a new head coach often brings her
    own people); vacancies are filled by the head coach from three candidates."""
    import decisions as D
    out = dict(fired=[], retired=[], hired=[])
    init(lg, year)
    # 1. a year on: age, growth, heat, retirement
    for t in lg.teams:
        for side in SIDES:
            c = getattr(t, SEAT[side])
            if c is None:
                continue
            c.age += 1
            c.seasons_with_team += 1
            _grow(lg, c, year)
            c.heat = 0.6 * c.heat + (0.5 - pct.get(t.id, 0.5))
            if _retires(lg, c, year):
                c.status, c.team_id = "retired", None
                c.career.append({"year": year, "event": "retired", "age": c.age})
                setattr(t, SEAT[side], None)
                out["retired"].append((t.id, side))
    _free_pool_season(lg, year)
    # 2. the head coach's review (only where there is a head coach and someone to review)
    reviews = []
    for t in lg.teams:
        if t.coach is None or (t.oc is None and t.dc is None):
            continue
        r = C._rng(lg.card_seed, "coordfire", t.id, year)
        new_hc = t.id in coach_changed
        defaults = {}
        for key in ("oc", "dc"):
            c = getattr(t, key)
            sweep = new_hc and r.random() < CLEAN_HOUSE
            defaults[key] = c is not None and (sweep or c.heat > FIRE_HEAT)
        reviews.append((t, _review_point(lg, t, year, new_hc, defaults)))
    picks = D.decide_many(lg, [dp for _, dp in reviews]) if reviews else []
    for (t, dp), pick in zip(reviews, picks):
        for key, side in (("oc", "offense"), ("dc", "defense")):
            if pick in (f"fire_{key}", "fire_both"):
                c = getattr(t, key)
                c.career.append({"year": year, "event": "fired", "team": t.id})
                t.coach.decision_log.append({"year": year, "action": f"fired {c.name} as {TITLE[side]}"})
                _release(lg, c, year)
                setattr(t, key, None)
                out["fired"].append((t.id, side))
    # 3. fill every vacancy: the head coach chooses among three
    jobs = [(t, side) for t in lg.teams for side in SIDES if getattr(t, SEAT[side]) is None]
    if jobs:
        out["hired"] = _hire_round(lg, year, jobs)
    return out


def _hire_round(lg, year: int, jobs) -> list:
    import decisions as D
    taken: set = set()
    seats = []
    for t, side in jobs:
        avail = [c for c in lg.free_coords if c.side == side and id(c) not in taken]
        r = C._rng(lg.card_seed, "coordvets", t.id, year, side)
        vets = r.sample(avail, min(len(avail), HIRE_POOL - 1)) if avail else []
        taken |= {id(v) for v in vets}
        cands = []
        lg._cand_ids += 1
        cands.append(make_coord_card(lg.card_seed, CAND_BASE + lg._cand_ids, side, t.id))        # the league's first candidate comes first (the autopilot takes her)
        cands += vets
        while len(cands) < HIRE_POOL:
            lg._cand_ids += 1
            cands.append(make_coord_card(lg.card_seed, CAND_BASE + lg._cand_ids, side, t.id))
        seats.append((t, side, cands, {id(v) for v in vets}))
    dps = []
    for t, side, cands, vets in seats:
        if t.coach is None:
            dps.append(None)
            continue
        opts = [dict(id=f"candidate_{i}", label=f"Hire {c.name}", tags={"between_jobs": id(c) in vets},
                     view=dict(age=c.age, **_perceived(lg, t, c, year))) for i, c in enumerate(cands)]
        dps.append(D.DecisionPoint("hire_coordinator", year, t.id, "coach", t.coach, dict(team_needs=f"a {TITLE[side]}", unit=side), opts,
                                   "candidate_0", dict(team=t, strength_rank=1 + sum(1 for x in lg.teams if x.strength > t.strength),
                                                                          candidates={f"candidate_{i}": c for i, c in enumerate(cands)})))
    live = [d for d in dps if d is not None]
    picks = iter(D.decide_many(lg, live) if live else [])
    hired = []
    for (t, side, cands, vets), dp in zip(seats, dps):
        k = int(next(picks).split("_")[1]) if dp is not None else 0
        new = cands[k]
        if id(new) in vets:
            lg.free_coords = [c for c in lg.free_coords if c is not new]
        else:
            new.cid = lg.new_coord_id()
            lg.coords.append(new)
        new.team_id, new.idle_years, new.heat, new.seasons_with_team, new.status = t.id, 0, 0.0, 0, "coordinator"
        new.career.append({"year": year, "event": "hired", "team": t.id})
        if t.coach is not None:
            t.coach.decision_log.append({"year": year, "action": f"hired {new.name} as {TITLE[side]}"})
        setattr(t, SEAT[side], new)
        hired.append((t.id, side, new.name))
    return hired


# ---- the card as text -----------------------------------------------------------------------------------------
def render_coord(c: CoordCard, lg=None) -> str:
    team = lg.by_id[c.team_id].name if (lg is not None and c.team_id is not None) else "between jobs"
    lines = [f"{c.name.upper()}  -  {TITLE[c.side]}, {team}  -  age {c.age}, from {c.hometown}",
             f"  PLAYCALLING {c.ratings['playcalling']:.0f}   VISION {c.ratings['vision']:.0f}   heat {c.heat:+.2f}   years here {c.seasons_with_team}",
             f"  Her lift to her unit: {c.points:+.2f} points of margin (the average coordinator is zero)."]
    if c.career:
        lines.append("  Career: " + "; ".join(f"{e['year']} {e['event']}" for e in c.career[-6:]))
    if c.decision_log:
        lines.append("  Lately: " + "; ".join(f"{d['year']} {d['action']}" for d in c.decision_log[-3:]))
    return "\n".join(lines)
