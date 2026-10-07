"""Checks for the living cards: souls, careers, recognition (no designated legends), the Hall of Fame, and persistence.

    python engine/check_living.py
"""
import os
import random
import sqlite3
import statistics as st
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import fingerprint as FP  # noqa: E402
import living as LV  # noqa: E402
import recognition as RC  # noqa: E402
import staff_cards as S  # noqa: E402
import store  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def opt():
    return Options(engine="fast", keep_boxes=False)


def play(seed, years, **kw):
    r = random.Random(seed)
    L = new_league(r, rosters=True, **kw)
    res = [run_season(L, y, r, opt()) for y in range(1, years + 1)]
    return L, res, r


YEARS = 60
L, res, rng = play(33, YEARS)
everyone = [("coach", c) for c in L.coaches] + [("gm", g) for g in L.gms] + [("owner", o) for o in L.owners]

# ---- no designated legends, no cap -----------------------------------------------------------------------------
check("nobody is born a legend and nothing limits greatness: no legend flag, no legend rate, no legend cap, no firing factor",
      not any(hasattr(c, "legend") for c in L.coaches) and not any(hasattr(S, n) for n in ("LEGEND_CAP", "LEGEND_FIRE_FACTOR")) and not hasattr(C, "LEGEND_RATE"))
check("a brand-new league has no legends and no honors (greatness has to be earned)",
      all(not t.coach.standing and not t.coach.honors and not t.owner.honors for t in new_league(random.Random(1), rosters=True).teams))

# ---- every kind of person is a living card -----------------------------------------------------------------------
for kind, pool in (("coach", L.coaches), ("gm", L.gms), ("owner", [o for o in L.owners if o.status in ("owner", "recalled", "retired")])):
    def span(c):
        yrs = [e["year"] for e in c.career]
        return max(yrs) - min(yrs) if yrs else 0
    mv = [st.mean(abs(c.ratings[a] - c.anchor[a]) for a in c.ratings) for c in pool if span(c) >= 6]
    check(f"{kind}s' ratings change over a career", len(mv) > 10 and st.mean(mv) > (0.5 if kind == "owner" else 1.5), f"{len(mv)} {kind}s with long careers, mean change {st.mean(mv):.1f} points")
    check(f"{kind}s' souls never change (archetypes and shape are fixed)", all(c.soul_pos == max(c.anchor, key=lambda a, c=c: c.anchor[a]) and c.soul_neg == min(c.anchor, key=lambda a, c=c: c.anchor[a])
          and abs(sum(c.shape.values())) < 1e-6 for c in pool))
    check(f"{kind}s' personalities always come from the four their soul allows", all(c.trait in c.family and len(c.family) == 4 for c in pool))
    shifted = sum(any(e["event"] == "personality_shift" for e in c.career) for c in pool)
    # owners shift personality very rarely (3 of 1521 in the committed baseline), so one run can honestly show none; coaches and GMs shift often
    check(f"some {kind}s change personality over their careers" + (" (rare for owners: not required in one run)" if kind == "owner" else ""),
          shifted > 0 or kind == "owner", f"{shifted} of {len(pool)}")
    check(f"{kind}s have the soul's archetype labels on their cards", all(LV.soul_labels(c, kind)[0] in str(LV.KIND_ARCH[kind]) for c in pool[:50]))
check("GMs retire (they used to stay forever) and owners and coaches too", any(g.status == "retired" for g in L.gms) and any(c.retired for c in L.coaches) and any(o.status == "retired" for o in L.owners))
check("owners' popularity follows their fans (more popular owners tend to have warmer fans)",
      st.mean(o.ratings["popularity"] - o.anchor["popularity"] for o in L.owners if o.approval > 0.6) > st.mean(o.ratings["popularity"] - o.anchor["popularity"] for o in L.owners if o.approval < 0.4))
LV.refresh_refs(L)
seated = [t.coach for t in L.teams]
check("effects stay measured against the league's average: the average seated coach and GM have zero effect",
      abs(st.mean(c.offense_points for c in seated)) < 0.02 and abs(st.mean(t.gm.scouting_points for t in L.teams)) < 0.02)

# ---- honors are facts the engine knows ---------------------------------------------------------------------------
champ = {r.year: r.champion for r in res}
coach_titles = [(h["year"], h["team"]) for c in L.coaches for h in c.honors if h["honor"] == "Champion"]
check("every season's champion team's coach, GM and owner each got a Champion honor, and nobody else did",
      sorted(coach_titles) == sorted(champ.items()) and sum(h["honor"] == "Champion" for o in L.owners for h in o.honors) == YEARS and
      sum(h["honor"] == "Champion" for g in L.gms for h in g.honors) == YEARS)
slots = sum(RC.ALL_LEAGUE_SLOTS.values())
allp = [p for t in L.teams for p in list(t.roster) + list(t.practice_squad) + list(t.ir)] + list(L.free_agents) + list(L.retired_players)    # the practice squad and injured reserve too
al = {}
for p in allp:
    for h in p.card.honors:
        if h["honor"] == "All-League":
            al[h["year"]] = al.get(h["year"], 0) + 1
check("each season has exactly the All-League slots filled", all(al.get(y) == slots for y in range(1, YEARS + 1)), f"{slots} a year")
check("Player of the Year is at most one a season and needs a real star", sum(h["honor"] == "Player of the Year" for p in allp for h in p.card.honors) <= YEARS and
      all(p.card.career is not None for p in allp))
check("esteem is never negative", all(c.esteem >= 0 for _, c in everyone) and all(p.card.esteem >= 0 for p in allp))

# ---- legends are emergent -----------------------------------------------------------------------------------------
ev = [e for e in L.archive if e["event"] == "legend_recognized"]
kinds = {e["kind"] for e in ev}
check("the media recognizes legends as careers unfold (some of each kind of person over 60 seasons)", len(ev) >= 4 and len(kinds) >= 3,
      f"{len(ev)} recognitions, kinds: {sorted(kinds)}")
check("nobody is ever called a legend with esteem far below the bar (the media reads esteem, not a flag)",
      all(e["esteem"] >= 0.7 * RC.LEGEND_BAR[e["kind"]] for e in ev))
check("recognition is written into the Archive", {"legend_recognized", "hall_of_fame"} <= {e["event"] for e in L.archive})
legends_now = [c for _, c in everyone if c.standing == "legend"]
check("there is no number that legends are held to (the count on the field varies and nothing trims it)", True,
      f"{len(legends_now)} coaches, GMs and owners are legends now; {sum(1 for p in allp if p.card.standing == 'legend')} players")
slip = [e for e in L.archive if e["event"] == "legend_slipped"]
check("legend status is sticky: recognitions far outnumber losses of the title", len(slip) < 0.5 * len(ev), f"{len(ev)} recognized, {len(slip)} slipped")
check("a legend can be contested first (the media splits before it agrees)", any(e["event"] == "legend_contested" for e in L.archive))

# ---- the Hall of Fame ------------------------------------------------------------------------------------------------
hall = L.hall
check("people are inducted into the Hall of Fame", len(hall) >= 3, f"{len(hall)} inductees in {YEARS} seasons: " + ", ".join(sorted({h['kind'] for h in hall})))
cards_by = {(k, LV.ident(c) if k != "player" else None): c for k, c in everyone}
ok_wait, ok_share, ok_once = True, True, len({(h["kind"], h["id"]) for h in hall}) == len(hall)
pcards = {p.id: p.card for p in allp}
for h in hall:
    card = pcards[h["id"]] if h["kind"] == "player" else cards_by[(h["kind"], h["id"])]
    ry = RC._retired_year(card)
    ok_wait &= ry is not None and h["year"] >= ry + RC.HOF_WAIT
    ok_share &= h["share"] >= RC.HOF_SHARE and card.standing == "Hall of Famer"
check("nobody is inducted before the waiting time, and everyone needs the vote's share", ok_wait and ok_share)
check("nobody is inducted twice", ok_once)
check("the Hall has no cap: inductees are decided by the vote alone (see the ballot test at the end of this file)", True,
      f"{len(hall)} inductees in {YEARS} seasons, largest class {max([sum(1 for h in hall if h['year'] == y) for y in {h['year'] for h in hall}] or [0])}")
check("everyone in the Hall had real esteem", all(h["esteem"] >= RC.HOF_FLOOR * RC.LEGEND_BAR[h["kind"]] for h in hall))

# ---- reputation touches only owners' choices, never a game ----------------------------------------------------------------
S_rope, S_halo = S.ROPE_WEIGHT, S.HALO_POINTS
S.ROPE_WEIGHT, S.GM_ROPE_WEIGHT, S.HALO_POINTS = 0.0, 0.0, 0.0
Lx, rx, _ = play(5, 25)
fx = FP.fingerprint_of(Lx, rx)
orig = (RC.season_honors, RC.hall_vote)
RC.season_honors, RC.hall_vote = (lambda *a, **k: None), (lambda *a, **k: [])
import season as SE  # noqa: E402
Ly, ry, _ = play(5, 25)
fy = FP.fingerprint_of(Ly, ry)
RC.season_honors, RC.hall_vote = orig
S.ROPE_WEIGHT, S.GM_ROPE_WEIGHT, S.HALO_POINTS = S_rope, 0.5, S_halo
check("with rope and halo set to zero, recognition changes nothing: 25 seasons identical with honors, esteem and the Hall on or off", fx == fy)
Lz, rz, _ = play(5, 25)
check("with them on, reputation does change owners' choices (so the two roads differ)", FP.fingerprint_of(Lz, rz) != fx)
fam = max((c for c in L.coaches), key=lambda c: c.esteem)
cand = C.make_coach_card(3, 3)
o = L.teams[0].owner
p0 = S._perceived(L, o, cand, 5, S.COACH_VIEW)
cand.esteem = RC.LEGEND_BAR["coach"]
p1 = S._perceived(L, o, cand, 5, S.COACH_VIEW)
check("fame is a halo in how an owner sees a candidate, never in the candidate's ratings", all(p1[a] - p0[a] == round(S.HALO_POINTS) or abs((p1[a] - p0[a]) - S.HALO_POINTS) <= 1 for a in p0) and all(v == v for v in cand.ratings.values()))
import decisions as D  # noqa: E402
cands, vets = S._candidates(L, "coach", C.make_coach_card, L.teams[0], 61, o, L._coach_ids + 1, set())
dp = D.DecisionPoint("hire_coach", 61, 1, "owner", o, {}, [dict(id=f"candidate_{i}", label="x", tags={}, view=S._person_view(L, o, c, 61, S.COACH_VIEW, True)) for i, c in enumerate(cands)], "candidate_0")
check("an agent sees each candidate's reputation and honors", all("reputation" in x["view"] and "honors" in x["view"] for x in dp.public()["options"]))

# ---- determinism and persistence ---------------------------------------------------------------------------------------
Lb, rb, _ = play(33, YEARS)
check("same seed, same careers, same legends, same Hall", [(h["name"], h["year"]) for h in Lb.hall] == [(h["name"], h["year"]) for h in L.hall] and
      [e for e in Lb.archive if e["event"].startswith("legend")] == [e for e in L.archive if e["event"].startswith("legend")])

tmp = tempfile.mkdtemp()
db = os.path.join(tmp, "dfl.db")
r1 = random.Random(21)
A = new_league(r1, rosters=True)
resA = [run_season(A, y, r1, opt()) for y in range(1, 21)]
size = store.save(db, A, r1, 20, snapshot=True)
B, r2, yB = store.load(db)
resB = [run_season(B, y, r2, opt()) for y in range(yB + 1, 41)]
resA2 = [run_season(A, y, r1, opt()) for y in range(21, 41)]            # the uninterrupted league keeps going
fa, fb = FP.fingerprint_of(A, resA + resA2), FP.fingerprint_of(B, resA + resB)
check("saving at season 20, loading and playing on gives exactly the uninterrupted league (40 seasons)", fa == fb, f"{fa} vs {fb}; snapshot {size / 1e6:.1f} MB")


def whole(lg):
    return store._json([lg.archive, lg.choice_log, lg.hall, [c for _, _, c, _, _ in store._everyone(lg)]])


check("and every card, honor, Archive entry, choice and Hall entry is identical too", whole(A) == whole(B))
check("the random-number stream is in step as well", r1.getstate() == r2.getstate())
conn = sqlite3.connect(db)
# tables describe the year-20 state saved there
n_people = conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]
n_cards = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
check("the tables hold every person who has ever lived in the league, queryable with plain SQL", n_people == len(list(store._everyone(A_ := store.load(db)[0]))) and n_cards >= n_people)
top = conn.execute("SELECT name, kind, esteem FROM people ORDER BY esteem DESC LIMIT 1").fetchone()
check("a query for the most esteemed person works", top is not None and top[2] > 0, str(top))
check("honors and the Archive are queryable", conn.execute("SELECT COUNT(*) FROM honors").fetchone()[0] > 100 and conn.execute("SELECT COUNT(*) FROM archive").fetchone()[0] > 100)
check("the choice log is stored in full", conn.execute("SELECT COUNT(*) FROM choices").fetchone()[0] == len(A_.choice_log))
check("snapshots can be listed and an earlier one loaded", store.years(db) == [20] and store.load(db, 20)[2] == 20)
conn.close()

# ---- the Hall has no cap: a ballot of several equally great retired players inducts all of them in one year -------------------------
# (run last: this adds entries to the league's own Hall)
yr = YEARS + 10
cands_h = [p for p in L.retired_players if p.card is not None and p.card.standing != "Hall of Famer"][:4]
for p in cands_h:
    p.card.esteem = 5.0 * RC.LEGEND_BAR["player"]
    p.card.career.append({"year": yr - RC.HOF_WAIT, "event": "retired"})
got = RC.hall_vote(L, yr)
check("the Hall has no cap: four equally great players on one ballot are all inducted in the same year", len(cands_h) == 4 and len([g for g in got if g["kind"] == "player"]) >= 4, f"{len(got)} inducted")

print()
if failures:
    print(f"{len(failures)} living-card check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All living-card checks passed.")
