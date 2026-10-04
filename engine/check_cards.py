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
labels = {lab for pos in C.ARCHETYPES.values() for pair in pos.values() for lab in pair} | {"Well-Rounded", "No Glaring Weakness", "No Standout Skill"}
ok = True
for p in ps:
    a, b = C.archetypes(p.pos, p.ratings)
    ok &= a in labels and b in labels
check("archetypes always come from the position's list", ok)
for pos in ATTRS:
    sample = next(p for p in ps if p.pos == pos)
    check(f"{pos}: archetype follows the ratings",
          C.archetypes(pos, {a: (95 if i == 0 else 40) for i, a in enumerate(ATTRS[pos])})[0] == C.ARCHETYPES[pos][ATTRS[pos][0]][0]
          if len(ATTRS[pos]) > 1 else True)
check("a card prints in the reference template format", all(k in C.render_player(ps[0], lg) for k in ("IDENTITY", "PERSONALITY", "ARCHETYPES", "RATINGS", "RELATIONSHIPS", "DECISION_LOG")))

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
check("the cap holds at the extremes of the rating scale", abs(big.offense_points) <= 1.0 and abs(big.defense_points) <= 1.0)
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
check("coach effect is small next to team talent (sd under 0.6 points)", spread < 0.6, f"sd {spread:.2f}")

# ---- cards never change results; coaches switched off must match a league with no card code at all -------
def run(seed, coaches, patch):
    saved = (C.offseason_cards, C.init_league_cards)
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
        C.offseason_cards, C.init_league_cards = saved


import league as LG  # noqa: E402
check("with coaches off, cards change no result (they never draw from the engine's random stream)",
      run(11, False, False) == run(11, False, True))
check("with coaches on, results differ (the coach effect is real)", run(11, True, False) != run(11, False, False))

# ---- many seasons: cards persist, retire and archive --------------------------------------------------
rng = random.Random(33)
L = new_league(rng, rosters=True)
first = {p.id: (p.name, p.card.trait, p.card.hometown) for t in L.teams for p in t.roster}
coach_names = {t.id: t.coach.cid for t in L.teams}
for y in range(1, 26):
    run_season(L, y, rng, Options(engine="fast", keep_boxes=False))
alive = [p for t in L.teams for p in t.roster] + list(L.free_agents)
everyone = alive + L.retired_players
check("everyone who ever played has a card", all(p.card is not None for p in everyone), f"{len(everyone)} players over 25 seasons")
check("no two players ever share a name", len({p.name for p in everyone}) == len(everyone))
same = all((p.name, p.card.trait, p.card.hometown) == first[p.id] for p in everyone if p.id in first)
check("a player keeps her name, personality and hometown for life", same)
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

print()
if failures:
    print(f"{len(failures)} card check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All card checks passed.")
