"""Checks for the save: the cards are the save, a league rebuilt from them resumes exactly, and one card can change leagues.

    python engine/check_store.py
"""
import json
import os
import random
import sqlite3
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agents as AG  # noqa: E402
import decisions as D  # noqa: E402
import fingerprint as FP  # noqa: E402
import movement as MV  # noqa: E402
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


def everything(lg):
    """The whole league as text with keys in their stored order: so a rebuilt league that differs in anything, including the order
    of a card's ratings, is a different text."""
    reg = store._registry(lg)
    cards = [(k, store._dump(store._plain(c))) for k, c in sorted(reg.items(), key=lambda kv: kv[0])]
    players = [(p.id, store._dump(store._body(p)), store._dump(store._plain(p.card)), p.ovr) for p in sorted(store._players(lg), key=lambda p: p.id)]
    teams = [(t.id, t.name, t.conf, t.div, t.status, t.tier, t.strength, t.bank, [p.id for p in t.roster or ()],
              t.coach and t.coach.cid, t.gm and t.gm.gid, t.owner and t.owner.oid) for t in lg.teams]
    lists = [[c.cid if hasattr(c, "cid") else c.gid for c in lg.passed_over], [c.cid for c in lg.coaches], [g.gid for g in lg.gms], [o.oid for o in lg.owners],
             [c.cid for c in lg.free_coaches], [g.gid for g in lg.free_gms], [p.id for p in lg.free_agents], [p.id for p in lg.retired_players]]
    return store._dump([cards, players, teams, lists, lg.archive, lg.choice_log, lg.hall, lg.refs, lg.prev_pct, lg.new_id.next,
                        [getattr(lg, k) for k in store.PLAIN], MV.dump(lg.movement)])


def play(lg, rng, a, b, driver=None):
    lg.driver = driver
    return [run_season(lg, y, rng, opt()) for y in range(a, b + 1)]


tmp = tempfile.mkdtemp()
db = os.path.join(tmp, "dfl.db")

# ---- the cards are the save ---------------------------------------------------------------------------------------------
r1 = random.Random(21)
A = new_league(r1, rosters=True)
resA = play(A, r1, 1, 20)
t0 = time.time()
size = store.save(db, A, r1, 20)
t_save = time.time() - t0
t0 = time.time()
B, r2, yB = store.load(db)
t_load = time.time() - t0
conn = sqlite3.connect(db)
check("a plain save holds no snapshot of the league: the cards and a small league record are all there is", conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0] == 0 and yB == 20)
rec_len = len(conn.execute("SELECT json FROM league").fetchone()[0])
check("the league record is small: it lists who sits where and the counters, and the people themselves stay on their cards",
      rec_len < 200_000, f"{rec_len / 1e3:.0f} kB of league record against {os.path.getsize(db) / 1e6:.1f} MB of cards, Archive and choices")
check("the league rebuilt from the cards is the saved league in every card, list and counter, down to the order of each card's ratings", everything(A) == everything(B))
check("and the random-number stream is in step", r1.getstate() == r2.getstate())
resB = play(B, r2, 21, 40)
resA2 = play(A, r1, 21, 40)
fa, fb = FP.fingerprint_of(A, resA + resA2), FP.fingerprint_of(B, resA + resB)
check("saved at season 20, rebuilt from the cards and played to 40 gives exactly the uninterrupted league", fa == fb and everything(A) == everything(B), f"{fa} vs {fb}")
check(f"saving 40 seasons' league takes {t_save:.1f}s and opening it {t_load:.1f}s", t_load < 10)

# a person's card is self-contained
coach = next(t.coach for t in A.teams if t.coach.history)
rec = json.loads(store.export_card(A, "coach", coach.cid))
need = {"soul_pos", "soul_neg", "ratings", "history", "honors", "career", "decision_log", "notes", "esteem", "standing", "trait", "pressure"}
check("an exported coach card carries her soul, ratings, trajectory, honors, career, decisions and notes", need <= set(rec["card"]) and rec["kind"] == "coach")
pl = next(t.roster[0] for t in A.teams)
prec = json.loads(store.export_card(A, "player", pl.id))
check("an exported player record carries her card and her body, so it is the whole person", "body" in prec and prec["body"]["ratings"] == pl.ratings and prec["card"]["pid"] == pl.id)

# ---- a card changes leagues -----------------------------------------------------------------------------------------------
r3 = random.Random(8)
C = new_league(r3, rosters=True)
play(C, r3, 1, 6)
text = store.export_card(A, "coach", coach.cid)
before = (len(C.coaches), len(C.free_coaches), C._coach_ids)
got = store.import_card(C, text)
check("an imported coach joins the pool of people between jobs under a fresh id and keeps everything that made her who she is",
      got in C.free_coaches and got in C.coaches and got.cid == before[2] + 1 and got.team_id is None and got.soul_pos == coach.soul_pos
      and got.ratings == coach.ratings and got.history == coach.history and got.honors == coach.honors and got.notes == coach.notes)
play(C, r3, 7, 16)
check("the league with her in the pool plays on without trouble (10 seasons)", len(C.choice_log) > 0 and all(t.coach for t in C.teams if t.status == "active"))
gm = next(t.gm for t in A.teams)
g = store.import_card(C, store.export_card(A, "gm", gm.gid))
check("a GM can change leagues the same way", g in C.free_gms and g.soul_pos == gm.soul_pos)
try:
    store.import_card(C, store.export_card(A, "player", pl.id))
    check("a player card cannot be imported as a coach or GM", False)
except ValueError:
    check("a player card cannot be imported as a coach or GM", True)

# ---- snapshots are optional -------------------------------------------------------------------------------------------------
db2 = os.path.join(tmp, "snap.db")
r4 = random.Random(5)
D5 = new_league(r4, rosters=True)
play(D5, r4, 1, 8)
store.save(db2, D5, r4, 8, snapshot=True)
play(D5, r4, 9, 12)
store.save(db2, D5, r4, 12)
check("a snapshot keeps an earlier year reopenable beside the latest card save", store.years(db2) == [8, 12] and store.load(db2, 8)[2] == 8 and store.load(db2)[2] == 12)
try:
    store.load(db2, 10)
    check("a year without a snapshot is refused rather than guessed", False)
except KeyError:
    check("a year without a snapshot is refused rather than guessed", True)

# ---- the guards ----------------------------------------------------------------------------------------------------------------
D5.mystery = 1
try:
    store.save(os.path.join(tmp, "x.db"), D5, r4, 12)
    check("a league with state the save does not know about is refused, so nothing is silently lost", False)
except ValueError as e:
    check("a league with state the save does not know about is refused, so nothing is silently lost", "mystery" in str(e))
del D5.mystery
twin = D5.coaches[3]
dup = type(twin)(**{**store._plain(twin)})
D5.coaches.append(dup)
try:
    store.save(os.path.join(tmp, "y.db"), D5, r4, 12)
    check("two different cards with the same id are refused", False)
except ValueError:
    check("two different cards with the same id are refused", True)
D5.coaches.pop()
old = os.path.join(tmp, "old.db")
c = sqlite3.connect(old)
c.executescript(store.SCHEMA)
c.execute("INSERT INTO meta VALUES('format','1')")
c.commit()
c.close()
try:
    store.load(old)
    check("a save in a different layout is refused", False)
except ValueError:
    check("a save in a different layout is refused", True)
store.save(db2, D5, r4, 12)
n1 = sqlite3.connect(db2).execute("SELECT COUNT(*) FROM cards").fetchone()[0]
store.save(db2, D5, r4, 12)
check("saving twice leaves one copy of everything", sqlite3.connect(db2).execute("SELECT COUNT(*) FROM cards").fetchone()[0] == n1)

# ---- agents and the save ----------------------------------------------------------------------------------------------------------
ra = random.Random(11)
X = new_league(ra, rosters=True)
AGENT = AG.StandIn()
resX1 = play(X, ra, 1, 6, D.AgentDriver(AGENT, workers=12))
dbx = os.path.join(tmp, "agents.db")
store.save(dbx, X, ra, 6)
Y, ry, yy = store.load(dbx)
check("an owner's notes and decision log are on her card in the save and come back", all(o.notes == p.notes and o.decision_log == p.decision_log for o, p in zip(X.owners, Y.owners)) and sum(len(o.notes) for o in Y.owners) > 0)
resX2 = play(X, ra, 7, 12, D.AgentDriver(AGENT, workers=12))
resY = play(Y, ry, 7, 12, D.AgentDriver(AG.StandIn(), workers=12))
check("a league with agents, saved at season 6 and loaded with agents seated again, plays on exactly as if it had never stopped (12 seasons)",
      FP.fingerprint_of(X, resX1 + resX2) == FP.fingerprint_of(Y, resX1 + resY) and everything(X) == everything(Y))
dbz = os.path.join(tmp, "autopilot.db")
store.save(dbz, X, ra, 12)
Z, rz, _ = store.load(dbz)
resZ = play(Z, rz, 13, 18, None)
resX3 = play(X, ra, 13, 18, None)
check("and the same league can go back to the autopilot after loading, just as the original can", FP.fingerprint_of(X, resX1 + resX2 + resX3) == FP.fingerprint_of(Z, resX1 + resX2 + resZ))
check("every person has one row of cards and a row in the readable table", sqlite3.connect(dbz).execute("SELECT COUNT(*) FROM people").fetchone()[0] <=
      sqlite3.connect(dbz).execute("SELECT COUNT(*) FROM cards").fetchone()[0])

print()
if failures:
    print(f"{len(failures)} store check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All store checks passed.")
