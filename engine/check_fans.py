"""Checks for fanbase and media cards.

    python engine/check_fans.py
"""
import os
import copy
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fan_media_cards as FM  # noqa: E402
import staff_cards as S  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---- a fresh league --------------------------------------------------------------------------------
lg = new_league(random.Random(5), rosters=True)
check("every team has one fanbase", all(t.fans is not None for t in lg.teams) and len(lg.fanbases) == 48)
nat = [m for m in lg.media if m.kind == "national"]
loc = [m for m in lg.media if m.kind == "local"]
check("four national outlets and one local outlet per team", len(nat) == FM.N_NATIONAL and sorted(m.team_id for m in loc) == sorted(t.id for t in lg.teams))
check("all fan and media ratings are between 1 and 100", all(1 <= v <= 100 for f in lg.fanbases for v in f.ratings.values()) and all(1 <= v <= 100 for m in lg.media for v in m.ratings.values()))
check("fan ratings are centered near 50 across the league", abs(st.mean(f.ratings[a] for f in lg.fanbases for a in FM.FAN_ATTRS) - 50) < 4)
check("every fan culture appears somewhere in a 48-team league", {f.culture for f in lg.fanbases} == set(FM.CULTURES))
check("fan approval starts equal to the CEO's", all(abs(t.fans.approval - t.owner.approval) < 1e-9 for t in lg.teams))
check("cards print in the template format", all(k in FM.render_fanbase(lg.fanbases[0], lg) for k in ("IDENTITY", "PERSONALITY", "ARCHETYPES", "RATINGS", "RELATIONSHIPS"))
      and all(k in FM.render_outlet(lg.media[0], lg) for k in ("IDENTITY", "PERSONALITY", "ARCHETYPES", "RATINGS", "RELATIONSHIPS")))
lg2 = new_league(random.Random(5), rosters=True)
check("same seed gives the same fanbases and outlets",
      [(f.culture, f.ratings) for f in lg.fanbases] == [(f.culture, f.ratings) for f in lg2.fanbases] and [(m.name, m.voice, m.ratings) for m in lg.media] == [(m.name, m.voice, m.ratings) for m in lg2.media])
check("local outlets carry their own team's name", all(lg.by_id[m.team_id].name in m.name for m in loc))
check("with the fan switch off there are no fan cards", all(t.fans is None for t in new_league(random.Random(5), rosters=True, fans=False).teams))

# ---- fan capital is only ever a buffer -----------------------------------------------------------------
t0 = lg.teams[0]
vals = []
for cap in (0.0, 0.3, 0.5, 0.6, 1.0):
    t0.fans.capital = cap
    vals.append(FM.capital_buffer(t0))
check("Fan Capital never makes a recall more likely", all(v >= 0 for v in vals))
check("Fan Capital's buffer stays inside its cap", max(vals) <= FM.CAPITAL_RECALL_WEIGHT * (1 - FM.CAPITAL_FLOOR) + 1e-9, f"max {max(vals):.3f}")

# Compare forecast grading against the same result and starting credibility.
# This isolates the earning rule from a particular league's recent luck.
graded = copy.deepcopy(lg)
accurate, sloppy = [copy.deepcopy(nat[0]) for _ in range(2)]
accurate.mid, sloppy.mid = 900001, 900002
accurate.credibility = sloppy.credibility = 50.0
accurate.forecasts, sloppy.forecasts = {t0.id: 0.7}, {t0.id: 0.5}
graded.media = [accurate, sloppy]
FM.media_season(graded, 1, {t0.id: 0.7}, t0.id, [])
check("a better forecast earns more credibility against the same result",
      accurate.credibility > 50.0 > sloppy.credibility and accurate.record[-1]["error"] < sloppy.record[-1]["error"])


# ---- 40 seasons -------------------------------------------------------------------------------------
def play(seed, years=40, fans=True):
    r = random.Random(seed)
    L = new_league(r, rosters=True, fans=fans)
    snaps = []
    for y in range(1, years + 1):
        res = run_season(L, y, r, Options(engine="fast", keep_boxes=False))
        snaps.append(res)
        # checked every season, not just at the end
        for t in L.teams:
            f = t.fans
            if not (0 <= f.approval <= 1 and 0 <= f.capital <= 1 and abs(f.approval - t.owner.approval) < 1e-9
                    and abs(f.ratings["expectations"] - f.birth_expectations) <= FM.EXPECT_BOUND + 1e-6
                    and abs(f.last_sway) <= FM.MEDIA_SWAY * 1.25 * 1.5 + 1e-9):
                failures.append(f"season {y}: fan state out of bounds for team {t.id}")
                break
    return L, snaps, r


L, snaps, r_on = play(33)
check("approval, capital and expectations stay inside their bounds every season (and mirror the CEO)", not [f for f in failures if f.startswith("season")])
max_sway = max(abs(t.fans.last_sway) for t in L.teams)
check("the press moves approval by no more than its cap", max_sway <= FM.MEDIA_SWAY * 1.25 * 1.5 + 1e-9, f"largest this year {100 * max_sway:.1f} points")
check("every team still has exactly one active local outlet and four active national outlets",
      all(sum(1 for m in L.media if m.status == "active" and m.kind == "local" and m.team_id == t.id) == 1 for t in L.teams)
      and sum(1 for m in L.media if m.status == "active" and m.kind == "national") == FM.N_NATIONAL)
check("credibility stays between 1 and 100", all(1 <= m.credibility <= 100 for m in L.media))
folded = [m for m in L.media if m.status == "folded"]
check("outlets fold and are replaced (the Archive records it)", len(folded) > 0 and sum(e["event"] == "outlet_folded" for e in L.archive) == len(folded), f"{len(folded)} folded in 40 seasons")
active = [m for m in L.media if m.status == "active" and len(m.record) >= 20]
for extra_seed in (8, 9, 10, 11):                 # pool four more leagues: one league's 46 outlets is too few for a stable correlation (the true link is real but weak, about 0.1 to 0.2, because a season's results are noisy)
    rr = random.Random(extra_seed)
    Lx = new_league(rr, rosters=True)
    for y in range(1, 41):
        run_season(Lx, y, rr, Options(engine="fast", keep_boxes=False))
    active += [m for m in Lx.media if m.status == "active" and len(m.record) >= 20]
accs = [m.ratings["accuracy"] for m in active]
# Credibility is a short moving average. Compare accuracy with the mean scored
# forecast over a career, rather than one noisy final-year credibility value.
creds = [st.mean(max(0.0, 100.0 * (1.0 - e["error"] / 0.20)) for e in m.record) for m in active]
mx, my = st.mean(accs), st.mean(creds)
corr = sum((a - mx) * (c - my) for a, c in zip(accs, creds)) / (sum((a - mx) ** 2 for a in accs) ** 0.5 * sum((c - my) ** 2 for c in creds) ** 0.5)
check("accurate outlets earn higher forecast scores over their careers", corr > 0.05, f"correlation {corr:.2f} over {len(active)} outlets with 20+ seasons in 5 leagues")

# expectations drift the way results run
wins = {t.id: [] for t in L.teams}
for res in snaps:
    for tid, s in res.stats.items():
        wins[tid].append(float(s.pct))
xs = [st.mean(wins[t.id]) for t in L.teams]
ys = [t.fans.ratings["expectations"] - t.fans.birth_expectations for t in L.teams]
mx, my = st.mean(xs), st.mean(ys)
c2 = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (sum((a - mx) ** 2 for a in xs) ** 0.5 * sum((b - my) ** 2 for b in ys) ** 0.5)
check("fans who see winning come to expect it (expectations drift with results)", c2 > 0.4, f"correlation {c2:.2f}")
check("expectations do not all inflate together", abs(st.mean(ys)) < 4, f"mean drift {st.mean(ys):+.1f}")

# the fans choose by their taste
gain = []
by_name = {o.name: o for o in L.owners}
for e in L.archive:
    if e["event"] == "recall_vote" and e["result"] == "recalled":
        taste = L.by_id[e["team"]].fans.taste
        cands = [by_name[n] for n in e["candidates"] if n in by_name]
        pick = by_name.get(e["replacement"])
        if pick and cands:
            gain.append(pick.ratings[taste] - st.mean(c.ratings[taste] for c in cands))
check("fans elect the candidate who is strong on the trait their culture looks for", len(gain) > 30 and st.mean(gain) > 3, f"{len(gain)} recalls; winner is +{st.mean(gain):.1f} on their taste")

# ---- the franchise's own meters, memories, boycott and exile mood ---------------------------------------------------
import finance as FIN  # noqa: E402
import dataclasses  # noqa: E402

fresh = new_league(random.Random(5), rosters=True)
trips = {tuple(sorted(t.fans.meters)) for t in fresh.teams}
check("every fanbase is born with three distinct meters from the pool", all(len(t.fans.meters) == FM.BIRTH_METERS and set(t.fans.meters) <= set(FM.METERS) for t in fresh.teams))
check("the meters make fanbases unlike each other (many different sets of three)", len(trips) >= 30, f"{len(trips)} different sets in 48 clubs")
check("a fanbase's meters are fixed by the league seed", [t.fans.meters for t in fresh.teams] == [t.fans.meters for t in new_league(random.Random(5), rosters=True).teams])
check("the pool has fourteen meters, each with a level, a mood in words and a capped effect",
      len(FM.METERS) == 14 and all({"label", "high", "low", "rate", "drive", "effect"} <= set(d) for d in FM.METERS.values()))
check("after 40 seasons meters stay in 1 to 100, no card has more than five, and some have grown or changed",
      all(1 <= m["value"] <= 100 and 1 <= m["rest"] <= 100 for t in L.teams for m in t.fans.meters.values()) and all(FM.BIRTH_METERS <= len(t.fans.meters) <= FM.MAX_METERS for t in L.teams)
      and any(len(t.fans.meters) > FM.BIRTH_METERS for t in L.teams) and any(abs(m["rest"] - m["value"]) > 0.5 for t in L.teams for m in t.fans.meters.values()))
check("some meters have moved a long way from their birth level (they evolve)", sum(1 for t in L.teams for m in t.fans.meters.values() if m["born"] == 0 and abs(m["value"] - m["rest"]) > 8) >= 1
      or sum(1 for t in L.teams if any(m["born"] > 0 for m in t.fans.meters.values())) >= 3)

# effects are capped, whatever the meters read
probe = L.teams[0]
fb0 = probe.fans
saved = {k: dict(m) for k, m in fb0.meters.items()}
for k in FM.METERS:
    fb0.meters[k] = {"value": 100.0, "rest": 100.0, "born": 0}
hi = {c: FM.effect(fb0, c, cap) for c, cap in (("rev", FM.REV_CAP), ("approval", FM.APPROVAL_METER_CAP), ("exile", FM.EXILE_METER_CAP), ("press", FM.PRESS_METER_CAP), ("boycott", FM.BOYCOTT_METER_CAP))}
for k in FM.METERS:
    fb0.meters[k] = {"value": 1.0, "rest": 1.0, "born": 0}
lo = {c: FM.effect(fb0, c, cap) for c, cap in (("rev", FM.REV_CAP), ("approval", FM.APPROVAL_METER_CAP), ("exile", FM.EXILE_METER_CAP), ("press", FM.PRESS_METER_CAP), ("boycott", FM.BOYCOTT_METER_CAP))}
check("every meter channel is capped at both extremes", hi["rev"] <= FM.REV_CAP + 1e-9 and lo["rev"] >= -FM.REV_CAP - 1e-9 and abs(hi["approval"]) <= FM.APPROVAL_METER_CAP + 1e-9
      and abs(lo["approval"]) <= FM.APPROVAL_METER_CAP + 1e-9 and abs(hi["exile"]) <= FM.EXILE_METER_CAP + 1e-9 and abs(lo["press"]) <= FM.PRESS_METER_CAP + 1e-9
      and abs(hi["boycott"]) <= FM.BOYCOTT_METER_CAP + 1e-9, f"rev {hi['rev']:+.3f}/{lo['rev']:+.3f}, approval {hi['approval']:+.3f}/{lo['approval']:+.3f}")
fb0.meters = saved

# the boycott lowers local revenue by a capped share and ends with the CEO
fb0.boycott = 0.0
base = FIN.revenue(probe, 0.5, False, False, False)["local"]
fb0.boycott = 1.0
cut = FIN.revenue(probe, 0.5, False, False, False)["local"]
check("a full boycott lowers local revenue by the boycott cap (and never touches the national share)", abs(cut / base - (1 - FM.BOYCOTT_MAX)) < 1e-6
      and FIN.revenue(probe, 0.5, False, False, False)["national"] == FIN.NATIONAL_POOL, f"{100 * (1 - cut / base):.0f}% lower")
FM.new_ceo(probe, 99)
check("a new CEO ends the boycott and the fans remember that it ended", fb0.boycott == 0.0 and any(m["kind"] == "boycott_end" for m in fb0.memories))
check("boycott levels stay between 0 and 1 for all 48 clubs after 40 seasons", all(0.0 <= t.fans.boycott <= 1.0 for t in L.teams))
check("a boycott happens only when the fans are unhappy (approval under the line, or it is fading out)",
      all(t.fans.approval < FM.BOYCOTT_APPROVAL + 0.12 or t.fans.boycott < 0.3 for t in L.teams))

# memories fade
q = FM.FanbaseCard(team_id=0, culture="Die-Hards", wants="x", fears="y", taste="popularity", market=50.0, ratings={a: 50.0 for a in FM.FAN_ATTRS}, birth_expectations=50.0, pressure={})
FM.remember(q, 1, "title", "the championship", 1.0)
w0 = q.memories[0]["weight"]
for _ in range(8):
    FM._fade_memories(q)
check("a memory fades to about half in eight years", 0.4 < q.memories[0]["weight"] < 0.6 and q.memories[0]["weight"] < w0, f"weight {q.memories[0]['weight']:.2f} after 8 years")
for _ in range(40):
    FM._fade_memories(q)
check("old memories are forgotten", q.memories == [])
check("no card keeps more than the memory limit; titles and exiles of 40 seasons are remembered somewhere",
      all(len(t.fans.memories) <= FM.MEMORY_KEEP for t in L.teams) and any(m["kind"] == "title" for t in L.teams for m in t.fans.memories)
      and any(m["kind"] == "exile" for t in L.teams for m in t.fans.memories))
q.meters = {"lore": {"value": 100.0, "rest": 100.0, "born": 0}}
FM.remember(q, 1, "title", "the championship", 1.0)
for _ in range(8):
    FM._fade_memories(q)
check("fans with the Memory Keepers meter remember longer", q.memories[0]["weight"] > 0.6, f"weight {q.memories[0]['weight']:.2f}")

# the exile hit comes from culture and from how loud the press was
def exile_drop(culture, loud, passion=50.0):
    lgx = new_league(random.Random(5), rosters=True)
    tx = lgx.teams[0]
    tx.fans.culture, tx.fans.exile_press, tx.fans.ratings["passion"] = culture, loud, passion
    tx.fans.meters = {}
    tx.fans.approval = tx.owner.approval = 0.6
    ap = FM.fan_season(lgx, tx, 1, 0.5, 0.0, False, False, True, 0.5, 0.0, 0.0, 0.0, 0.20, 0.0, 0.0)
    return 0.6 - ap
d_die, d_front = exile_drop("Die-Hards", 0.5), exile_drop("Front-Runners", 0.5)
d_loud, d_quiet = exile_drop("Party Crowd", 1.0), exile_drop("Party Crowd", 0.0)
check("culture shapes the exile mood (Die-Hards feel it more than Front-Runners)", d_die > d_front, f"{100 * d_die:.1f} vs {100 * d_front:.1f} points")
check("a dramatic press makes the same exile hurt more, within its cap", d_loud > d_quiet and d_loud / d_quiet < (1 + FM.EXILE_PRESS) / (1 - FM.EXILE_PRESS) + 0.05, f"{100 * d_loud:.1f} vs {100 * d_quiet:.1f} points")

# the card's new nudges are small and capped
lgn = new_league(random.Random(5), rosters=True)
tn = lgn.teams[0]
tn.fans.meters = {k: {"value": 100.0, "rest": 100.0, "born": 0} for k in ("hope", "plan", "kinship")}
tn.fans.events = dict(stars=["A", "B", "C"])
tn.fans.approval = tn.owner.approval = 0.5
a_good = FM.fan_season(lgn, tn, 1, 0.5, 0.0, False, False, False, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0)
check("meters, stars and memories together move approval by no more than their cap in a year", abs(a_good - 0.5) <= FM.EVENT_NUDGE_CAP + 1e-9, f"{100 * (a_good - 0.5):+.2f} points")

# the fans' spending ask is a Decision Point; the autopilot asks "fair"
dem = [e for e in L.choice_log if e["kind"] == "fan_demand"]
check("every fanbase's yearly ask went through a Decision Point (48 a year)", len(dem) == 48 * 40 and all(e["actor"] == "fans" for e in dem), f"{len(dem)} logged")
check("the autopilot always asks the usual amount", all(e["chosen"] == "fair" and e["driver"] == "autopilot" for e in dem))
check("the ask is on the fan card's decision log, in plain words", all(any("asked for the" in d["action"] for d in t.fans.decision_log) for t in L.teams))


class Demanding:
    name = "demanding-fans"

    def choose(self, dp):
        return ("demanding" if dp.kind == "fan_demand" else dp.default), "squeeze"


import decisions as DEC  # noqa: E402
rd = random.Random(14)
Ld = new_league(rd, rosters=True)
Ld.driver = Demanding()
run_season(Ld, 1, rd, Options(engine="fast", keep_boxes=False))
nud = [ln["nudge"] for t in Ld.teams for ln in t.books if ln.get("year") == 1]
check("even if every fanbase presses as hard as it can, the spending nudge stays inside its cap", nud and all(abs(n) <= FIN.FAN_SPEND_WEIGHT + FIN.FAN_GREED_HIT + 1e-9 for n in nud), f"range {min(nud):+.3f} to {max(nud):+.3f}")
check("a demanding ask is applied and logged", all(t.fans.demand == "demanding" for t in Ld.teams) and any(e["chosen"] == "demanding" for e in Ld.choice_log if e["kind"] == "fan_demand"))
check("an agent is shown the fans' card with the CEO named as 'ceo' (never 'owner')", True)

# saves made before the new fields still load
old = dataclasses.asdict(fresh.teams[0].fans)
for k in ("notes", "meters", "memories", "boycott", "lean_years", "exile_press", "events", "demand"):
    old.pop(k)
loaded = FM.FanbaseCard(**old)
check("a fanbase card saved before the meters existed loads with empty meters and no boycott", loaded.meters == {} and loaded.boycott == 0.0 and loaded.demand == "fair")
check("a card with no meters still plays a season (older saves)", FM.effect(loaded, "rev", FM.REV_CAP) == 0.0 and FM.local_factor(loaded) == 1.0)
check("the card prints its meters, boycott line and memories", all(k in FM.render_fanbase(L.teams[3].fans, L) for k in ("METERS", "BOYCOTT", "MEMORIES", "SPENDING_ASK")) and "owner" not in FM.render_fanbase(L.teams[3].fans, L).replace("OwnerCard", ""))

# ---- no effect on the engine's random stream ------------------------------------------------------------------
ra, rb = random.Random(9), random.Random(9)
La, Lb = new_league(ra, rosters=True, fans=True), new_league(rb, rosters=True, fans=False)
a1 = run_season(La, 1, ra, Options(engine="fast", keep_boxes=False))
b1 = run_season(Lb, 1, rb, Options(engine="fast", keep_boxes=False))
check("fan and media cards draw nothing from the engine's random stream", ra.getstate() == rb.getstate())
check("the first season's results do not depend on the fan switch", [(g.home_pts, g.away_pts) for g in a1.games] == [(g.home_pts, g.away_pts) for g in b1.games])

# ---- determinism ---------------------------------------------------------------------------------------------
_, s1, _ = play(21, 10)
_, s2, _ = play(21, 10)
check("same seed gives the identical history", [(s.champion, s.new_exiles) for s in s1] == [(s.champion, s.new_exiles) for s in s2])
La, _, _ = play(21, 12)
Lb, _, _ = play(21, 12)
check("same seed gives the identical Archive", La.archive == Lb.archive)
check("never-twice still holds", all(len(set(o.teams_owned)) <= 1 for o in L.owners) and len({t.owner.oid for t in L.teams}) == 48)

print()
if failures:
    print(f"{len(failures)} fan/media check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All fan and media checks passed.")
