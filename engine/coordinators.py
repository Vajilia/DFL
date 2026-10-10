"""The coaching pool and the coaching staff (Step B of the ring of accountability, with the Commissioner's one-pool rule of 2026-10-09).

The Commissioner's ring: the head coach hires and fires the two coordinators; the coordinators call the plays and the schemes, and the head
coach has veto power. Everyone answers up the ring (players to coaches, coaches and GMs to the CEO, the CEO to the fans), and everyone's
first priority is the Diamond Coronation.

ONE POOL. A coach is a coach: head coaches and coordinators are the same kind of card (cards.CoachCard), and the character creator keeps one
coaching pool populated. The CEO hires her head coach from it; the head coach hires his coordinators from the same pool, so a head coach can
hire a former head coach as a coordinator. A coordinator who has proved herself (at least PROMOTE_MIN_YEARS on the job) can also be hired away as
a head coach by another club: the NFL does not let a club block an assistant from a head-coaching interview, so there is no permission step, and
the club she leaves refills her seat in the same offseason. (A coordinator cannot be hired away for another coordinator's job: only people between
jobs are on that market.) The creator adds fresh people only when the pool falls under its target (POOL_MIN, or enough for every open seat to
have its own slate of SLATE people), so the pool is always populated at the start of every hiring round and never flooded.

What a coordinator is. An offensive coordinator's playcalling is her offense rating and a defensive coordinator's is her defense rating; her
vision is her gamecraft. Her lift to her unit is measured against the league's average coordinator on that side, so the average one is worth
exactly zero.

Schemes. Before the season each coordinator proposes how her unit will play (offense: pass, run or balanced; defense: blitz, coverage or balanced)
through the Decision Point `coord_scheme`; the head coach may approve or veto it (`scheme_veto`), and a veto sends the unit back to balanced and
costs the coordinator standing with her boss. A scheme that suits the roster adds a little to the unit, one that fights it takes a little away
(SCHEME_CAP). A unit's coaching lift is mostly the coordinator's (COORD_WEIGHT); the head coach's own rating keeps the rest.

Safety, as everywhere else: every effect is small and capped; the card's random draws come from generators private to the card or the event,
never from the engine's stream; and the whole thing is re-tested against the fair-competitiveness bands.
"""
from __future__ import annotations

from typing import Dict

import cards as C
import living as LV

# ---- dials (PLACEHOLDER, not league rules) -------------------------------------------------------
COORD_POINTS_AT_100 = C.COACH_POINTS_AT_100     # a 100-rated play-caller (against the league's average one) is worth this much margin, as for a head coach
COORD_WEIGHT = 0.6                               # the share of a unit's coaching lift that comes from the coordinator; the head coach's own rating keeps the rest
SCHEME_CAP = 0.4                                 # a scheme that fits the roster perfectly adds this many points (one that fights it takes the same away)
SCHEMES = {"offense": ("balanced", "pass", "run"), "defense": ("balanced", "blitz", "coverage")}
FIT_CLIP = 2.0                                   # a roster's lean is measured in spreads from the league's mean and clipped at this many
VISION_BASE, VISION_SPAN = 0.25, 0.70            # chance the coordinator proposes the best-fitting scheme = base + span * vision / 100
SEE_SD = 0.6                                     # how blurred a person's view of the fit is at the worst (vision 0 or gamecraft 0); it sharpens with the rating
VETO_BAR = -0.15                                 # the head coach's rule: veto a proposal she sees fitting worse than this
OVERRULED_HEAT = 0.05                            # a vetoed coordinator's heat rises this much
FIRE_HEAT = 0.30                                 # a coordinator is fired when her heat tops this
CLEAN_HOUSE = 0.60                               # chance a new head coach sweeps out each coordinator he inherits
SLATE = 3                                        # candidates a head coach (or a CEO) sees
POOL_MIN = 40                                    # the coaching pool is brought back up to this many people between jobs at the start of every hiring round (the creator tops it up)
PROMOTE_MIN_YEARS = 2                            # a coordinator is on the head-coach market after this many seasons in her seat
POOL_AGE = (33, 58)                              # the creator's new coaches are position coaches and coordinators in the making

SIDES = ("offense", "defense")
SEAT = {"offense": "oc", "defense": "dc"}
TITLE = {"offense": "offensive coordinator", "defense": "defensive coordinator"}


# ---- the pool and the seats ----------------------------------------------------------------------
def _fresh(lg, year: int, event: str = "entered_coaching"):
    """A new person from the character creator, already a member of the league's coaching world."""
    cid = lg.new_coach_id()
    age = C._rng(lg.card_seed, "poolage", cid).randint(*POOL_AGE)
    c = C.make_coach_card(lg.card_seed, cid, None, age=age)
    c.career.append({"year": year, "event": event})
    lg.coaches.append(c)
    return c


def pool(lg) -> list:
    """The coaching pool: everyone between jobs who is still in the business."""
    return [c for c in lg.free_coaches if not c.retired]


def top_up(lg, year: int, vacancies: int = 0) -> int:
    """The creator keeps the pool populated: only when it is under its target (POOL_MIN, or a slate for every open seat) are new people added."""
    want = max(POOL_MIN, SLATE * vacancies)
    made = 0
    while len(pool(lg)) < want:
        c = _fresh(lg, year)
        c.team_id, c.idle_years = None, 0
        lg.free_coaches.append(c)
        made += 1
    return made


def _seat(lg, t, side: str, year: int):
    c = _fresh(lg, year, "hired")
    c.team_id, c.job = t.id, TITLE[side]
    c.career[-1].update(team=t.id, job=TITLE[side])
    c.ref = lg.refs.get(SEAT[side])
    setattr(t, SEAT[side], c)
    return c


def init(lg, year: int = 0):
    """A coordinator on each side for every team that has none (a new league, or an old save that never had them), and a full pool."""
    for t in lg.teams:
        for side in SIDES:
            if getattr(t, SEAT[side], None) is None:
                _seat(lg, t, side, year)
    top_up(lg, year, 0)


def seated(lg, side: str) -> list:
    return [c for c in (getattr(t, SEAT[side]) for t in lg.teams) if c is not None]


def refresh_refs(lg):
    """The mean rating of the coordinators on the job right now, per side. A coordinator's effect is her rating against this."""
    for side in SIDES:
        cs = seated(lg, side)
        if not cs:
            continue
        ref = {a: sum(c.ratings[a] for c in cs) / len(cs) for a in LV.KIND_ATTRS["coach"]}
        lg.refs[SEAT[side]] = ref
        for c in cs:
            c.ref = ref


def points(card, side: str) -> float:
    """A coordinator's lift to her unit, in points of margin: her side's rating against the league's average coordinator, capped."""
    return card.offense_points if side == "offense" else card.defense_points


def was_head_coach(card) -> bool:
    return any(e.get("event") == "hired" and "job" not in e for e in card.career)


def take(lg, card, year: int):
    """A person leaves where she was to take a head-coaching job: the pool, or her coordinator seat (the club she leaves refills it)."""
    if any(c is card for c in lg.free_coaches):
        lg.free_coaches = [c for c in lg.free_coaches if c is not card]
        return
    for t in lg.teams:
        for side in SIDES:
            if getattr(t, SEAT[side]) is card:
                setattr(t, SEAT[side], None)
                card.career.append({"year": year, "event": "promoted", "from": TITLE[side], "team": t.id})
                if t.coach is not None:
                    t.coach.decision_log.append({"year": year, "action": f"lost {card.name} as {TITLE[side]} to a head-coaching job"})
                return


def slate(lg, t, year: int, taken: set, head: bool, r) -> list:
    """The people a hiring boss sees: up to SLATE, drawn from the coaching pool (and, for a head-coach job, from the coordinators on other clubs who
    have been in their seat long enough). Nobody is offered to two clubs in the same round (`taken`)."""
    import staff_cards as S
    avail = [c for c in pool(lg) if id(c) not in taken and not S._recently_fired_here(c, t.id, year)]
    if head:
        for o in lg.teams:
            if o.id == t.id:
                continue
            for side in SIDES:
                c = getattr(o, SEAT[side])
                if c is not None and c.seasons_with_team >= PROMOTE_MIN_YEARS and id(c) not in taken:
                    avail.append(c)
    avail.sort(key=lambda c: c.cid)
    got = r.sample(avail, min(SLATE, len(avail)))
    while len(got) < SLATE:                                   # the creator never lets a boss run short
        c = _fresh(lg, year)
        c.team_id, c.idle_years = None, 0
        lg.free_coaches.append(c)
        got.append(c)
    return got


# ---- the lift a team gets from its coaches (called by lineup.build_lineup) -------------------------------
def lifts(coach, team):
    """(offense lift, defense lift) in points: the head coach's own, blended with the coordinator who calls the plays, plus the scheme's fit."""
    o = coach.offense_points if coach is not None else 0.0
    d = coach.defense_points if coach is not None else 0.0
    oc, dc = getattr(team, "oc", None), getattr(team, "dc", None)
    fit, scheme = getattr(team, "scheme_fit", None) or {}, getattr(team, "scheme", None) or {}
    if oc is not None:
        o = (1.0 - COORD_WEIGHT) * o + COORD_WEIGHT * points(oc, "offense") + SCHEME_CAP * fit.get(scheme.get("offense", "balanced"), 0.0)
    if dc is not None:
        d = (1.0 - COORD_WEIGHT) * d + COORD_WEIGHT * points(dc, "defense") + SCHEME_CAP * fit.get(scheme.get("defense", "balanced"), 0.0)
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


def _scheme_point(lg, t, side: str, c, year: int, rank: int, lean_z: float):
    import decisions as D
    fit = {"balanced": 0.0, "pass": lean_z, "run": -lean_z} if side == "offense" else {"balanced": 0.0, "blitz": lean_z, "coverage": -lean_z}
    vision = c.ratings["gamecraft"]
    seen = {s: round(_see(lg, t, side, year, f"coord{c.cid}", vision, f), 2) if s != "balanced" else 0.0 for s, f in fit.items()}
    opts = [dict(id=s, label=f"Call it {s}", tags={"perceived_fit": seen[s]}) for s in SCHEMES[side]]
    order = sorted(fit, key=lambda s: (-fit[s], s))                          # the truly best-fitting first
    r = C._rng(lg.card_seed, "scheme", t.id, year, side)
    p_best = VISION_BASE + VISION_SPAN * vision / 100.0
    default = order[0] if r.random() < p_best else r.choice(order[1:])
    ctx = dict(role=TITLE[side], your_team_strength_rank=rank, your_roster_leans=round(seen["pass"] if side == "offense" else seen["blitz"], 2),
               leaning_means=("positive: the passing units are stronger than the running ones" if side == "offense"
                              else "positive: the pass rush is stronger than the coverage"),
               your_boss=t.coach.name if t.coach else None)
    return D.DecisionPoint("coord_scheme", year, t.id, "coordinator", c, ctx, opts, default, dict(team=t, fit=fit, strength_rank=rank))


def _veto_point(lg, t, side: str, c, scheme: str, year: int, rank: int):
    import decisions as D
    true = t.scheme_fit[scheme]
    sees = round(_see(lg, t, side, year, f"coach{t.coach.cid}", t.coach.ratings["gamecraft"], true), 2)
    opts = [dict(id="approve", label=f"Let {c.name} run the {scheme} scheme", tags={"your_view_of_fit": sees}),
            dict(id="veto", label=f"Veto it: the {side} plays balanced", tags={"your_view_of_fit": sees})]
    default = "veto" if sees < VETO_BAR else "approve"
    ctx = dict(coordinator=c.name, unit=side, proposed_scheme=scheme, your_view_of_fit=sees, your_team_strength_rank=rank,
               coordinator_view=dict(playcalling=c.ratings[side], vision=c.ratings["gamecraft"]))
    return D.DecisionPoint("scheme_veto", year, t.id, "coach", t.coach, ctx, opts, default, dict(team=t, fit=true, strength_rank=rank))


# ---- the yearly review, firings and hires (called by staff_cards.season_end) --------------------------------
def _perceived(lg, t, c, side: str, year: int) -> dict:
    """A head coach sees a candidate's ratings blurred by her own gamecraft: her playcalling for this side and her vision (gamecraft)."""
    g = t.coach.ratings["gamecraft"] if t.coach is not None else 50.0
    r = C._rng(lg.card_seed, "seecoord", t.id, c.cid, year, side)
    sd = 8.0 * (1.0 - g / 100.0)
    return {"playcalling": round(max(1.0, min(100.0, c.ratings[side] + r.gauss(0.0, sd))), 1),
            "vision": round(max(1.0, min(100.0, c.ratings["gamecraft"] + r.gauss(0.0, sd))), 1)}


def _release(lg, c, year: int):
    c.team_id, c.idle_years, c.heat, c.job = None, 0, 0.0, ""
    lg.free_coaches.append(c)


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
               coordinators={s: dict(name=c.name, unit=c.job, heat=round(c.heat, 2), years_here=c.seasons_with_team,
                                     seen=_perceived(lg, t, c, c_side(s), year)) for s, c in cands.items()})
    return D.DecisionPoint("coord_review", year, t.id, "coach", t.coach, ctx, opts, default, dict(team=t, strength_rank=rank))


def c_side(key: str) -> str:
    return "offense" if key == "oc" else "defense"


def season(lg, year: int, pct: Dict[int, float], coach_changed) -> dict:
    """The offseason for coordinators: they age and change, some retire; each head coach reviews hers (a new head coach often brings her
    own people); vacancies (including seats left by coordinators hired away as head coaches) are filled from the coaching pool."""
    import decisions as D
    out = dict(fired=[], retired=[], hired=[])
    init(lg, year)
    # 1. a year on: age, growth, heat, retirement (the people between jobs have already had theirs: living.free_pool_season)
    for t in lg.teams:
        for side in SIDES:
            c = getattr(t, SEAT[side])
            if c is None:
                continue
            c.age += 1
            c.seasons_with_team += 1
            LV.grow(c, "coach", lg.card_seed, year)
            c.heat = 0.6 * c.heat + (0.5 - pct.get(t.id, 0.5))
            if LV.retires(c, "coach", lg.card_seed, year):
                c.retired, c.team_id, c.job = True, None, ""
                c.career.append({"year": year, "event": "retired", "age": c.age})
                setattr(t, SEAT[side], None)
                out["retired"].append((t.id, side))
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
                c.career.append({"year": year, "event": "fired", "team": t.id, "job": TITLE[side]})
                t.coach.decision_log.append({"year": year, "action": f"fired {c.name} as {TITLE[side]}"})
                _release(lg, c, year)
                setattr(t, key, None)
                out["fired"].append((t.id, side))
    # 3. fill every vacancy: the head coach chooses among three from the coaching pool
    jobs = [(t, side) for t in lg.teams for side in SIDES if getattr(t, SEAT[side]) is None]
    if jobs:
        out["hired"] = _hire_round(lg, year, jobs)
    return out


def _hire_round(lg, year: int, jobs) -> list:
    import decisions as D
    top_up(lg, year, len(jobs))
    taken: set = set()
    seats = []
    for t, side in jobs:
        r = C._rng(lg.card_seed, "coordslate", t.id, year, side)
        cands = slate(lg, t, year, taken, False, r)
        taken |= {id(c) for c in cands}
        seats.append((t, side, cands))
    dps = []
    for t, side, cands in seats:
        if t.coach is None:
            dps.append(None)
            continue
        opts = [dict(id=f"candidate_{i}", label=f"Hire {c.name}", tags={"between_jobs": True, "former_head_coach": was_head_coach(c)},
                     view=dict(age=c.age, former_head_coach=was_head_coach(c), **_perceived(lg, t, c, side, year))) for i, c in enumerate(cands)]
        dps.append(D.DecisionPoint("hire_coordinator", year, t.id, "coach", t.coach, dict(team_needs=f"a {TITLE[side]}", unit=side), opts,
                                   "candidate_0", dict(team=t, strength_rank=1 + sum(1 for x in lg.teams if x.strength > t.strength),
                                                       candidates={f"candidate_{i}": c for i, c in enumerate(cands)})))
    live = [d for d in dps if d is not None]
    picks = iter(D.decide_many(lg, live) if live else [])
    hired = []
    for (t, side, cands), dp in zip(seats, dps):
        k = int(next(picks).split("_")[1]) if dp is not None else 0
        new = cands[k]
        lg.free_coaches = [c for c in lg.free_coaches if c is not new]
        new.team_id, new.idle_years, new.heat, new.seasons_with_team, new.job = t.id, 0, 0.0, 0, TITLE[side]
        new.ref = lg.refs.get(SEAT[side])
        new.career.append({"year": year, "event": "hired", "team": t.id, "job": TITLE[side]})
        if t.coach is not None:
            t.coach.decision_log.append({"year": year, "action": f"hired {new.name} as {TITLE[side]}" + (" (a former head coach)" if was_head_coach(new) else "")})
        setattr(t, SEAT[side], new)
        hired.append((t.id, side, new.name))
    return hired


# ---- the card as text -----------------------------------------------------------------------------------------
def render_coord(c, lg=None) -> str:
    side = "defense" if "defensive" in c.job else "offense"
    team = lg.by_id[c.team_id].name if (lg is not None and c.team_id is not None) else "between jobs"
    lines = [f"{c.name.upper()}  -  {c.job or 'coach'}, {team}  -  age {c.age}, from {c.hometown}",
             f"  PLAYCALLING {c.ratings[side]:.0f}   VISION (gamecraft) {c.ratings['gamecraft']:.0f}   heat {c.heat:+.2f}   years here {c.seasons_with_team}",
             f"  Her lift to her unit: {points(c, side):+.2f} points of margin (the average coordinator is zero)."]
    if c.career:
        lines.append("  Career: " + "; ".join(f"{e['year']} {e['event']}" + (f" ({e['job']})" if e.get("job") else "") for e in c.career[-6:]))
    if c.decision_log:
        lines.append("  Lately: " + "; ".join(f"{d['year']} {d['action']}" for d in c.decision_log[-3:]))
    return "\n".join(lines)
