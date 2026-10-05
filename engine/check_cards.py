"""Checks for the character cards: players, coaches, and the rule that cards never change a game result
except through the capped coach effect.

    python engine/check_cards.py
"""
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import card_pools as CP  # noqa: E402
import power_rating as PR  # noqa: E402
from league import new_league  # noqa: E402
from lineup import build_lineup  # noqa: E402
from positions import ATTRS  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---- pools and names ---------------------------------------------------------------------------
check("name pools have no repeats", len(set(CP.FIRST_NAMES)) == len(CP.FIRST_NAMES) and len(set(CP.LAST_NAMES)) == len(CP.LAST_NAMES))
size = len(CP.FIRST_NAMES) * len(CP.LAST_NAMES)
names = {C.make_name(123, n) for n in range(1, size + 1)}
check("every id up to the size of the name grid gets a different name", len(names) == size, f"{size} names")
check("past the grid a numeral keeps names different", C.make_name(123, 1) != C.make_name(123, 1 + size))

# ---- a fresh league ----------------------------------------------------------------------------
lg = new_league(random.Random(5), rosters=True)
ps = [p for t in lg.teams for p in t.roster]
check("every player has a card and a real name", all(p.card is not None and not p.name.startswith("P0") for p in ps), f"{len(ps)} players")
check("names are unique across the league", len({p.name for p in ps}) == len(ps))
check("every team has a head coach", all(t.coach is not None and t.coach.team_id == t.id for t in lg.teams))
labels = ({lab for pos in C.ARCHETYPES.values() for pair in pos.values() for lab in pair}
          | {C.WELL_ROUNDED, C.NO_WEAKNESS})
check("every soul comes from the position's list", all(p.card.archetype_pos in labels and p.card.archetype_neg in labels for p in ps))
check("every archetype belongs to a temperament family", all(p.card.archetype_pos in C.ARCHETYPE_FAMILY for p in ps))
for pos in ATTRS:
    if len(ATTRS[pos]) > 1:
        probe = {a: (95 if i == 0 else 40) for i, a in enumerate(ATTRS[pos])}
        good, gattr, bad, battr = C.birth_archetypes(pos, probe)
        check(f"{pos}: the soul follows the birth profile", good == C.ARCHETYPES[pos][ATTRS[pos][0]][0] and gattr == ATTRS[pos][0] and battr == ATTRS[pos][1])
check("a card prints in the reference template format", all(k in C.render_player(ps[0], lg) for k in ("IDENTITY", "SOUL", "PERSONALITY", "RATINGS", "RELATIONSHIPS", "DECISION_LOG")))

# ---- determinism ---------------------------------------------------------------------------------
lg2 = new_league(random.Random(5), rosters=True)
check("same seed gives the same people", [p.name for t in lg.teams for p in t.roster] == [p.name for t in lg2.teams for p in t.roster]
      and [t.coach.name for t in lg.teams] == [t.coach.name for t in lg2.teams])
lg3 = new_league(random.Random(6), rosters=True)
check("a different seed gives different people", [p.name for p in lg3.teams[0].roster] != [p.name for p in lg.teams[0].roster])

# ---- coach effect is small, capped and exact -------------------------------------------------------
pts = [c.offense_points for c in lg.coaches] + [c.defense_points for c in lg.coaches]
check("coach effects are inside the cap", all(abs(x) <= C.COACH_POINTS_AT_100 + 1e-9 for x in pts), f"largest {max(abs(x) for x in pts):.2f}")
big = C.make_coach_card(1, 1)
big.ratings.update(offense=100.0, defense=1.0)
check("the cap holds at the extremes of the rating scale", abs(big.offense_points) <= C.COACH_POINTS_AT_100 + 1e-9 and abs(big.defense_points) <= C.COACH_POINTS_AT_100 + 1e-9)
t = max(lg.teams, key=lambda x: abs(x.coach.offense_points) + abs(x.coach.defense_points))
with_c = build_lineup(t.id, t.roster, t.coach)
without = build_lineup(t.id, t.roster, None)
check("a coach lifts the offensive units by exactly her offense points",
      abs((with_c.qb_acc - without.qb_acc) - t.coach.offense_points) < 1e-9 and abs((with_c.rec - without.rec) - t.coach.offense_points) < 1e-9)
check("a coach lifts the defensive units by exactly her defense points",
      abs((with_c.coverage - without.coverage) - t.coach.defense_points) < 1e-9)
shift = PR.rating(with_c) - PR.rating(without)
expect = t.coach.offense_points + t.coach.defense_points
check("in margin terms the effect is about the sum of her two points", abs(shift - expect) < 0.05, f"{shift:+.2f} vs {expect:+.2f}")
spread = st.pstdev([PR.rating(build_lineup(x.id, x.roster, x.coach)) - PR.rating(build_lineup(x.id, x.roster, None)) for x in lg.teams])
check("coach effect is small next to team talent (sd under 1.0 point)", spread < 1.0, f"sd {spread:.2f}")

# ---- cards never change results; coaches switched off must match a league with no card code at all -------
def run(seed, coaches, patch):
    saved = (C.offseason_cards, C.init_league_cards, C.SOUL_PULL)
    C.SOUL_PULL = 0.0                       # the soul pull is a deliberate design effect; switch it off for this comparison
    if patch:
        C.offseason_cards = lambda *a, **k: None
        C.init_league_cards = lambda *a, **k: None
    try:
        r = random.Random(seed)
        L = new_league(r, rosters=True, coaches=coaches)
        out = []
        for y in range(1, 5):
            s = run_season(L, y, r, Options(engine="fast", keep_boxes=False))
            out.append((s.champion, tuple(sorted(s.new_exiles)), round(sum(x.strength for x in L.teams), 6)))
        return out
    finally:
        C.offseason_cards, C.init_league_cards, C.SOUL_PULL = saved


import league as LG  # noqa: E402
check("with coaches off, cards change no result (they never draw from the engine's random stream)",
      run(11, False, False) == run(11, False, True))
check("with coaches on, results differ (the coach effect is real)", run(11, True, False) != run(11, False, False))

# ---- many seasons: cards persist, retire and archive --------------------------------------------------
rng = random.Random(33)
L = new_league(rng, rosters=True)
first = {p.id: (p.name, p.card.hometown) for t in L.teams for p in t.roster}
coach_names = {t.id: t.coach.cid for t in L.teams}
for y in range(1, 26):
    run_season(L, y, rng, Options(engine="fast", keep_boxes=False))
alive = [p for t in L.teams for p in t.roster] + list(L.free_agents)
everyone = alive + L.retired_players
check("everyone who ever played has a card", all(p.card is not None for p in everyone), f"{len(everyone)} players over 25 seasons")
check("no two players ever share a name", len({p.name for p in everyone}) == len(everyone))
same = all((p.name, p.card.hometown) == first[p.id] for p in everyone if p.id in first)
check("a player keeps her name and hometown for life", same)
check("retired players keep their cards and a 'retired' career entry",
      len(L.retired_players) > 1000 and all(any(e["event"] == "retired" for e in p.card.career) for p in L.retired_players))
rookies = [p for t in L.teams for p in t.roster if p.draft_year is not None]
check("drafted players record the draft on their card", rookies and all(any(e["event"] == "drafted" for e in p.card.career) for p in rookies))
check("every team still has a coach and none is over the age limit",
      all(t.coach is not None and t.coach.age <= C.COACH_MAX_AGE and not t.coach.retired for t in L.teams))
check("coaches retire and are replaced over 25 seasons", len(L.coaches) > 48 and sum(c.retired for c in L.coaches) > 10,
      f"{len(L.coaches)} coaches hired, {sum(c.retired for c in L.coaches)} retired")
ages = [t.coach.age for t in L.teams]
check("coach ages look sensible", 38 <= min(ages) and max(ages) <= C.COACH_MAX_AGE, f"{min(ages)}-{max(ages)}")
check("the league's coach effects stay centered near zero", abs(st.mean([t.coach.offense_points + t.coach.defense_points for t in L.teams])) < 0.4)


# ---- souls, perception and personality over 25 seasons --------------------------------------------------
souls_before = {p.id: (p.card.archetype_pos, p.card.archetype_neg, p.card.family) for t in L.teams for p in t.roster}
check("every player has a card and the soul never changed",
      all((p.card.archetype_pos, p.card.archetype_neg, p.card.family) == souls_before[p.id] for p in everyone if p.id in souls_before))
check("her personality is always one her soul allows", all(p.card.trait in C.FAMILY_TRAITS[p.card.family] for p in everyone))
shifts = [e for p in everyone for e in p.card.career if e["event"] == "personality_shift"]
long_careers = [p for p in everyone if p.years_in_league >= 6]
shifted = sum(any(e["event"] == "personality_shift" for e in p.card.career) for p in long_careers)
check("personalities do shift over a long career (but not for everyone)", 0.08 < shifted / len(long_careers) < 0.60,
      f"{shifted / len(long_careers):.0%} of {len(long_careers)} players with 6+ years shifted at least once")
check("personalities are still varied", len({p.card.trait for p in alive}) == 10)
vets = [p for p in alive if p.age >= 32]
rooks = [p for p in alive if p.age <= 24 and p.years_in_league <= 2]
vg = st.mean(p.card.confidence_gap(p.ratings) for p in vets)
rg = st.mean(p.card.confidence_gap(p.ratings) for p in rooks)
check("declining veterans overrate themselves, rising youngsters undersell themselves", vg > rg + 1.0, f"veterans {vg:+.1f}, youngsters {rg:+.1f} rating points")
kept = []
for p in alive:
    ga, _, _, _ = None, None, None, None
    # her signature attribute (the one her soul is named for) should still be among her best
    good = p.card.archetype_pos
    for att, (g, b) in C.ARCHETYPES[p.pos].items():
        if g == good:
            top = max(p.ratings, key=p.ratings.get)
            kept.append(p.ratings[att] >= p.ratings[top] - 4.0)
check("her ratings stay true to her soul (signature attribute still near her best)", st.mean(kept) > 0.75, f"{st.mean(kept):.0%} of {len(kept)} players")

# ---- coaches: development and legends ---------------------------------------------------------------------
import copy  # noqa: E402
import offseason as OFF  # noqa: E402
from roster_model import RosterModel  # noqa: E402
rm = RosterModel()
pool = [p for p in new_league(random.Random(9), rosters=True, coaches=False).teams[3].roster]
for p in pool:
    p.card = None
base = copy.deepcopy(pool)
boost = copy.deepcopy(pool)
good_coach = C.make_coach_card(1, 1)
good_coach.ratings["development"] = 100.0
OFF.progress(base, rm, random.Random(4))
OFF.progress(boost, rm, random.Random(4), {p.id: good_coach for p in boost})
diff = st.mean(b.ovr - a.ovr for a, b in zip(base, boost))
young = [(a, b) for a, b in zip(base, boost) if a.age <= 27]
dy = st.mean(b.ovr - a.ovr for a, b in young)
check("a 100-rated development coach adds her bonus to young players", abs(dy - C.DEV_POINTS_AT_100) < 0.06 * C.DEV_POINTS_AT_100 + 0.02,
      f"{dy:+.3f} vs {C.DEV_POINTS_AT_100:+.3f}")
poor = C.make_coach_card(1, 2)
poor.ratings["development"] = 1.0
check("a poor development coach holds players back", C.development_bonus(poor, 24) < 0 and abs(C.development_bonus(poor, 24)) <= C.DEV_POINTS_AT_100 + 1e-9)
check("development bonus is capped", all(abs(C.development_bonus(c, 24)) <= C.DEV_POINTS_AT_100 + 1e-9 for c in L.coaches))
check("older players respond half as much", abs(C.development_bonus(good_coach, 30) - 0.5 * C.development_bonus(good_coach, 24)) < 1e-9)
# ---- coaches are living people: no designated legends -----------------------------------------------------------
import living as LV  # noqa: E402
check("no coach is born a legend (there is no such flag)", not any(hasattr(c, "legend") for c in L.coaches) and not hasattr(C, "LEGEND_RATE"))
many = [C.make_coach_card(7, i) for i in range(1, 4001)]
check("new coaches are drawn around 50, with no special tail", abs(st.mean(c.ratings["offense"] for c in many) - 50.0) < 1.0 and
      sum(c.ratings["offense"] >= 90 for c in many) / len(many) < 0.01, f"mean {st.mean(c.ratings['offense'] for c in many):.1f}, "
      f"{sum(c.ratings['offense'] >= 90 for c in many)} of {len(many)} at 90+")
old = [c for c in L.coaches if len([e for e in c.career if e["event"] == "hired"]) and c.seasons_with_team >= 8]
check("a career changes a coach's ratings (they grow, plateau and fade)", len(old) > 10 and st.mean(abs(c.ratings["offense"] - c.anchor["offense"]) for c in old) > 3.0,
      f"{len(old)} coaches with 8+ seasons; mean change {st.mean(abs(c.ratings['offense'] - c.anchor['offense']) for c in old):.1f}")
check("but her soul is fixed: the best and worst of her birth ratings are still her archetypes and her shape never moved",
      all(c.soul_pos == max(c.anchor, key=lambda a, c=c: c.anchor[a]) and c.soul_neg == min(c.anchor, key=lambda a, c=c: c.anchor[a]) and
          abs(sum(c.shape.values())) < 1e-6 for c in L.coaches))
check("her soul keeps her ratings in shape (her birth strength is still, on average, her best)", st.mean(c.ratings[c.soul_pos] >= LV.level(c) for c in old) > 0.8)
check("her personality is always one her soul allows", all(c.trait in c.family for c in L.coaches))
check("some coaches changed personality over their careers", sum(any(e["event"] == "personality_shift" for e in c.career) for c in L.coaches) > 5)
check("a coach's self-image lags the truth (the average gap is real but small)", all(abs(LV.confidence_gap(c)) < 20 for c in L.coaches))
seated = [t.coach for t in L.teams]
check("the average coach on the job has zero effect (effects are measured against the league's current average)",
      abs(st.mean(c.offense_points for c in seated)) < 0.05 and abs(st.mean(c.development_points for c in seated)) < 0.02,
      f"{st.mean(c.offense_points for c in seated):+.3f} and {st.mean(c.development_points for c in seated):+.3f}")
check("effects are capped at the stated sizes whatever the ratings", all(abs(c.offense_points) <= C.COACH_POINTS_AT_100 + 1e-9 and abs(c.defense_points) <= C.COACH_POINTS_AT_100 + 1e-9
      and abs(c.development_points) <= C.DEV_POINTS_AT_100 + 1e-9 for c in L.coaches))
check("every rating stays between 1 and 100", all(1 <= v <= 100 for c in L.coaches for v in c.ratings.values()))

print()
if failures:
    print(f"{len(failures)} card check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All card checks passed.")
