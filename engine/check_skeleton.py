"""The Commissioner's schedule skeleton (2026-10-12): a fixed slot template, filled every season by whoever holds each seed, which is set from the previous
season's final division rankings. Year 1 must be his own schedule; every re-seeding must stay legal; the template must save and load."""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R
import identity as ID
import founding as F
from league import new_league
from schedule import Game, build_schedule, check_schedule
from season import run_season, Options
import store, tempfile

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


lg, _ = F.open_league(7)
tmpl = lg.schedule_template
check("the league carries the Commissioner's template: 360 slot games, each slot (conference, division, seed)", len(tmpl) == 360 and all(len(h) == 3 and len(a) == 3 for _, h, a, _ in tmpl))
g1 = build_schedule(lg, random.Random(1))
want = sorted((w, h, a, k) for w, h, a, k in ID.first_season_games(lg.teams))
check("year 1 filled from the template is exactly his schedule (same games, same weeks, same grounds)", sorted((g.week, g.home, g.away, g.kind) for g in g1) == want)
check("building the schedule draws no chance: any generator gives the same games", [(g.week, g.home, g.away) for g in build_schedule(lg, random.Random(2))] == [(g.week, g.home, g.away) for g in g1])

# every re-seeding stays legal: shuffle the seeds inside each division, including returns of exiles into any seed
act = lg.active()
ex = lg.exiled()
bad = 0
for i in range(60):
    r = random.Random(1000 + i)
    for d in range(R.TOTAL_DIVISIONS):
        members = lg.division(d)
        pool = list(members)
        r.shuffle(pool)
        for status, tier, t in zip(["active"] * 5 + ["exiled"], [1, 2, 3, 4, 5, None], pool):
            t.status, t.tier = status, tier
    errs = check_schedule(lg, build_schedule(lg, r))
    if errs:
        bad += 1
        print(errs[:2])
check("60 random re-seedings (any five of a division's six clubs in any seeds) all give a legal schedule", bad == 0, f"{bad} illegal")

# the slot layout is the same every year; the clubs in the slots change
lg2, rr = F.open_league(11)
opt = Options(engine="fast", keep_boxes=False)
opt.validate_schedule = True
tm0 = [tuple(map(tuple, (r[1], r[2]))) + (r[0], r[3]) for r in lg2.schedule_template]
seen = []
for y in range(1, 6):
    run_season(lg2, y, rr, opt)                       # raises if any year's schedule is illegal
    seen.append(tuple(t.tier for t in lg2.teams))
check("five seasons in a row under the template are all legal (checked each year) and the template never changes", [tuple(map(tuple, (r[1], r[2]))) + (r[0], r[3]) for r in lg2.schedule_template] == tm0)
check("the seeds move with the standings: the clubs in the slots are not the same five seasons on", len(set(seen)) > 1)

# save / load
path = os.path.join(tempfile.mkdtemp(), "x.db")
store.save(path, lg2, random.Random(1), 5)
L, _, _ = store.load(path)
check("the template survives saving and loading and fills the same schedule", [(g.week, g.home, g.away) for g in build_schedule(L, random.Random(5))] == [(g.week, g.home, g.away) for g in build_schedule(lg2, random.Random(5))])

# the divisions rotate through the slot divisions each year; the conferences swap every fifth year (the Commissioner, 2026-10-12)
from schedule import rotation
lg3, _ = F.open_league(7)
D = R.DIVISIONS_PER_CONFERENCE
sm = lg3.slot_map()
def team_in_slot(year, c, d, t):
    flip, shift = rotation(year)
    return sm[(c ^ flip, (d - shift) % D, t)]
check("year 1 is the identity: slot division A is the first division of the first conference", rotation(1) == (0, 0))
check("year 2: slot A is used by the fourth division, slot B by the first, C by the second", [team_in_slot(2, 0, d, 1).div for d in range(D)] == [3, 0, 1, 2])
check("years 2 to 4 only rotate inside the conference, never across it", all(team_in_slot(y, c, d, 1).conf == c for y in (1, 2, 3, 4) for c in (0, 1) for d in range(D)))
check("year 5: the divisions have made a full turn and the conferences swap: slot A is the fifth division (the second conference's first), B the sixth ... E the first",
      [(team_in_slot(5, c, d, 1).conf, team_in_slot(5, c, d, 1).div) for c in (0, 1) for d in range(D)] == [(1, d) for d in range(D)] + [(0, d) for d in range(D)])
check("year 9 is year 1 again: the whole pattern repeats every eight years", all(rotation(y) == rotation(y + 8) for y in range(1, 30)) and len({rotation(y) for y in range(1, 9)}) == 8)
g_by_year = {y: sorted((g.week, g.home, g.away) for g in build_schedule(lg3, random.Random(0), y)) for y in range(1, 17)}
check("eight different schedules in eight years, then the same eight again", len({tuple(v) for y, v in g_by_year.items() if y <= 8}) == 8 and all(g_by_year[y] == g_by_year[y + 8] for y in range(1, 9)))
check("every one of the eight years is legal (also after re-seeding the clubs)", all(check_schedule(lg3, build_schedule(lg3, random.Random(0), y)) == [] for y in range(1, 17)))
bad = 0
for i in range(24):
    r = random.Random(5000 + i)
    for d in range(R.TOTAL_DIVISIONS):
        pool = list(lg3.division(d)); r.shuffle(pool)
        for status, tier, t in zip(["active"] * 5 + ["exiled"], [1, 2, 3, 4, 5, None], pool):
            t.status, t.tier = status, tier
    for y in range(1, 9):
        if check_schedule(lg3, build_schedule(lg3, r, y)):
            bad += 1
check("24 random re-seedings in each of the eight years (192 schedules) are all legal", bad == 0, f"{bad} illegal")
lg3, _ = F.open_league(7)
sm = lg3.slot_map()
# division games still stay inside the real division, whatever the year
ok = True
for y in range(1, 9):
    for g in build_schedule(lg3, random.Random(0), y):
        if g.kind == "division":
            ok &= next(t for t in lg3.teams if t.id == g.home).division_id == next(t for t in lg3.teams if t.id == g.away).division_id
check("division games are always between clubs of the same real division", ok)
# primetime points (MNF 5, Saturday night 4, Sunday evening 3, Sunday afternoon 2, Sunday morning 1)
pts = {}
for (w, h, a), (gn, day, ko) in ID.slot_times(lg3.teams).items():
    p = {(0, "17:30"): 4, (1, "10:00"): 1, (1, "13:00"): 2, (1, "17:30"): 3, (2, "17:30"): 5}[(day, ko)]
    for sl in (h, a):
        pts[sl] = pts.get(sl, 0) + p
check("his time-slot points: every slot gets between 33 and 38 in a season", min(pts.values()) == 33 and max(pts.values()) == 38, (min(pts.values()), max(pts.values())))
def total(c, d, t, years):
    return sum(pts[(c ^ rotation(y)[0], (d + rotation(y)[1]) % D, t)] for y in range(1, years + 1))
spread4 = max(max(total(c, d, t, 4) for c in (0, 1) for d in range(D)) - min(total(c, d, t, 4) for c in (0, 1) for d in range(D)) for t in range(1, 6))
spread8 = max(max(total(c, d, t, 8) for c in (0, 1) for d in range(D)) - min(total(c, d, t, 8) for c in (0, 1) for d in range(D)) for t in range(1, 6))
check("with the rotation a club of any one seed ends four years within 1 point of any other division's, and eight years exactly level (no rotation: up to 5 points in one year)", spread4 <= 1 and spread8 == 0, (spread4, spread8))

# the ordinary league keeps a random template each season
plain = new_league(random.Random(4), rosters=True)
check("an ordinary league has no template and builds a fresh one each season", plain.schedule_template is None
      and [(g.week, g.home) for g in build_schedule(plain, random.Random(1))] != [(g.week, g.home) for g in build_schedule(plain, random.Random(2))])

# timing travels with the slot
T = ID.slot_times(F.open_league(7)[0].teams)
check("each slot game has its workbook game number, day and kickoff (the opener is Saturday 5:30pm, game 1)", len(T) == 360 and T[(1, tmpl[0][1], tmpl[0][2])][0] >= 1
      and any(v == (1, 0, "17:30") for v in T.values()))

print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
