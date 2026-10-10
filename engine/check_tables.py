"""Checks for negotiation tables, starting with the job interview.

    python engine/check_tables.py
"""
import collections
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adversaries as ADV  # noqa: E402
import agents as AG  # noqa: E402
import decisions as D  # noqa: E402
import fingerprint as FP  # noqa: E402
import interviews as IV  # noqa: E402
import staff_cards as S  # noqa: E402
import store  # noqa: E402
import tables as TB  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def play(seed, years, driver=None, start=1, lg=None, rng=None):
    if lg is None:
        rng = random.Random(seed)
        lg = new_league(rng, rosters=True)
    lg.driver = driver
    res = [run_season(lg, y, rng, Options(engine="fast", keep_boxes=False)) for y in range(start, start + years)]
    return lg, res, rng


def interviews_of(lg):
    return [e for e in lg.archive if e["event"] == "interview"]


def covered(lg):
    return all(t.coach is not None and t.gm is not None and t.owner is not None for t in lg.teams)


# ---- the autopilot's tables are the old rule -------------------------------------------------------------------------------------
GOLD = {33: "95ef2a988c0048ca", 21: "86af5a5f9971a94f"}
for seed, want in GOLD.items():
    lg, res, _ = play(seed, 40)
    got = FP.fingerprint_of(lg, res)
    check(f"with the autopilot every interview is the old rule (offer nothing, accept at once): seed {seed}, 40 seasons equals the golden league", got == want, got)
check("and nothing about the autopilot's interviews is written up in the Archive (nothing out of the ordinary happened)", not interviews_of(lg))
iv_kinds = collections.Counter(e["kind"] for e in lg.choice_log if e["kind"].startswith("interview"))
check("but every interview turn is in the choice log (offer and answer for every hire)", iv_kinds["interview_offer"] == iv_kinds["interview_reply"] > 100, str(dict(iv_kinds)))
check("every coach and GM the autopilot hired has a guarantee that has already lapsed", all(c.protected_until <= max(e["year"] for e in c.career if e["event"] == "hired") for c in lg.coaches if any(e["event"] == "hired" for e in c.career)))

# ---- a guarantee protects her ---------------------------------------------------------------------------------------------------------
class Guarantee3:
    """Every CEO offers three guaranteed seasons and every candidate accepts; and every CEO fires everyone she is allowed to, every year."""
    name = "guarantee-3"

    def choose(self, dp):
        if dp.kind == "interview_offer":
            return "offer_3", "max"
        if dp.kind == "staff_review":
            return max(dp.options, key=lambda o: o["tags"].get("fires", 0))["id"], "fire everyone I can"
        return dp.default, "default"


lg3, res3, _ = play(7, 14, Guarantee3())
fired = [(e["year"], e["team"], e.get("coach") or e.get("gm")) for e in lg3.archive if e["event"] in ("coach_fired", "gm_fired")]
viol = []
for c in list(lg3.coaches) + list(lg3.gms):
    for h in [e for e in c.career if e["event"] == "hired" and e.get("guaranteed")]:
        for e in c.career:
            if e["event"] == "fired" and h["year"] < e["year"] <= h["year"] + h["guaranteed"]:
                viol.append((c.name, h["year"], e["year"]))
check("a guaranteed coach or GM is never fired in the reviews her guarantee covers, even by a CEO who fires everyone she can", not viol and len(fired) > 20 and sum(1 for c in lg3.coaches if c.protected_until > 0) > 40,
      f"{len(fired)} firings in 14 seasons, none inside a guarantee")
check("nobody is ever guaranteed more than three reviews", all(c.protected_until - max(e["year"] for e in c.career if e["event"] == "hired") <= IV.MAX_GUARANTEE for c in list(lg3.coaches) + list(lg3.gms) if any(e["event"] == "hired" for e in c.career)))
rev = [e for e in lg3.choice_log if e["kind"] == "staff_review"]
check("while a guarantee lasts the CEO is not even offered the choice to fire her", any("fire_coach" not in e["options"] for e in rev) and any("fire_gm" not in e["options"] for e in rev))
check("the guarantee is on her card (and so in the save)", any(c.protected_until > 0 for c in lg3.coaches) and "protected_until" in store._plain(lg3.coaches[0]))

# ---- walking away -------------------------------------------------------------------------------------------------------------------------
lgw, resw, _ = play(33, 40, ADV.EveryoneWalks())
iv = interviews_of(lgw)
check("when every candidate refuses every job, the league office fills every seat by the old rule and the league is exactly the old league (40 seasons)",
      FP.fingerprint_of(lgw, resw) == GOLD[33] and iv and all(e["assigned"] for e in iv) and covered(lgw), f"{len(iv)} seats filled by the league office")
check("each of those jobs went to three interviews, one candidate after another", all(len(e["attempts"]) == 3 and len({a["candidate"] for a in e["attempts"]}) == 3 for e in iv))
check("and a candidate who walked has it on her card", any(x["event"] == "turned_down" for c in lgw.coaches + lgw.passed_over for x in c.career))
lgh, resh, _ = play(33, 25, ADV.HardBargain())
ivh = interviews_of(lgh)
check("when candidates ask for the most and CEOs hold the line, some jobs are filled by the league office and no seat is ever left empty", covered(lgh) and any(e["assigned"] for e in ivh) and all(len(e["attempts"]) <= 3 for e in ivh), f"{sum(e['assigned'] for e in ivh)} of {len(ivh)} written-up interviews")
check("a seat a candidate refused goes to one of the others (the CEO chooses again among those left)", any(len(e["attempts"]) > 1 and not e["assigned"] for e in ivh) or any(len(e["attempts"]) > 1 for e in iv))

# ---- what each side sees ------------------------------------------------------------------------------------------------------------------
seen = {"owner": [], "candidate": []}


class Spy:
    name = "spy"

    def choose(self, dp):
        p = dp.public()
        if dp.kind == "interview_offer":
            seen["owner"].append((p, dp.internal["owner"]))
        if dp.kind == "interview_reply":
            seen["candidate"].append((p, dp.internal["owner"], dp.internal["candidate"]))
        return dp.default, "spy"


play(8, 3, Spy())
p, o = seen["owner"][0]
check("the CEO is shown the candidate as she perceives her, and nothing of how the candidate reads the CEO", "patience_as_you_read_her" not in str(p["context"]) and "perceived" in str(p["context"]))
bad = 0
for p, o, cand in seen["candidate"]:
    c = p["context"]
    if "ratings" in c or "notes" in str(c["owner"]):
        bad += 1
check("the candidate is shown public facts and her own read of the CEO, never the CEO's card, ratings or notes", bad == 0 and all("patience_as_you_read_her" in p["context"]["owner"] for p, _, _ in seen["candidate"]))
off = [abs(p["context"]["owner"]["patience_as_you_read_her"] - o.ratings["patience"]) for p, o, _ in seen["candidate"]]
check("her read of the CEO is a read, not the truth (it is off by a few points, differently for each candidate)", sum(1 for x in off if x > 0.5) > 0.7 * len(off), f"mean error {sum(off) / len(off):.1f} points")
check("the candidate is deciding with her own card (a different person from the CEO)", all(p["decider"]["role"] in ("coach", "gm") and p["decider"]["name"] == cand.name for p, _, cand in seen["candidate"]))

# ---- agents at the tables ---------------------------------------------------------------------------------------------------------------------
agent = AG.StandIn()


class OneAtATime:
    name = "agent"

    def choose(self, dp):
        return agent(dp.public())


Lp, rp, _ = play(8, 8, D.AgentDriver(AG.StandIn(), workers=12))
Ls, rs, _ = play(8, 8, OneAtATime())
check("a dozen agents at the tables in parallel give exactly the history one agent asked one turn at a time gives (8 seasons)",
      FP.fingerprint_of(Lp, rp) == FP.fingerprint_of(Ls, rs) and Lp.choice_log == Ls.choice_log and [e["driver"] for e in Lp.choice_log if e["kind"].startswith("interview")] == ["agent"] * sum(e["kind"].startswith("interview") for e in Lp.choice_log))
check("no turn at any table was refused or timed out", all(e["status"] == "ok" for e in Lp.choice_log), f"{len(Lp.choice_log)} decisions")
La, ra, _ = play(11, 30, D.AgentDriver(AG.StandIn(), workers=12))
ia = interviews_of(La)
class Recording:
    """The stand-in agent, remembering what it was shown and what it did."""
    name = "agent"

    def __init__(self):
        self.agent, self.rows = AG.StandIn(), []

    def choose(self, dp):
        p = dp.public()
        res = self.agent(p)
        if dp.kind == "interview_offer":
            famous = p["context"]["candidate"].get("reputation") in ("legend", "Hall of Famer", "star")
            self.rows.append((p["decider"]["trait"], "no one else" in p["context"]["if_she_walks"], famous, int(res["choice"].split("_")[1])))
        return res


rec = Recording()
play(12, 25, rec)
by = collections.defaultdict(list)
for trait, last, famous, g in rec.rows:
    if not last and not famous:
        by[trait].append(g)
rates = {k: sum(v) / len(v) for k, v in by.items() if len(v) >= 25}
check("CEOs with different personalities open with different offers when the candidate is an ordinary one and has alternatives (the card decides)",
      len(rates) >= 4 and max(rates.values()) - min(rates.values()) > 0.4, ", ".join(f"{k} {v:.2f}" for k, v in sorted(rates.items(), key=lambda kv: kv[1])))
mv = collections.Counter(e["chosen"].split("_")[0] for e in La.choice_log if e["kind"] == "interview_reply")
check("candidates accept, ask for more, and sometimes walk (not all one thing)", all(mv[k] > 20 for k in ("accept", "counter", "walk")), str(dict(mv)))
check("a real bargain happens: asks are sometimes met, sometimes held, sometimes refused", all(any(e["kind"] == "interview_counter" and e["chosen"] == k for e in La.choice_log) for k in ("accept", "hold", "walk")))
check("candidates keep notes to themselves on their own cards", sum(1 for c in La.coaches if any(n["kind"].startswith("interview") for n in c.notes)) > 20)
ids = [e["id"] for e in La.choice_log]
check("every table turn has its own id", len(ids) == len(set(ids)))
check("every seat is filled after every season, whoever sat at the tables", covered(La))
rel = [(c, [k for k in c.relationships if k.startswith("owner:")]) for c in La.coaches if c.team_id is not None]
check("a signed deal leaves goodwill between the CEO and the person she hired", sum(1 for c, ks in rel if ks and any(c.relationships[k] > 0 for k in ks)) > 20)

# ---- replay, saving and speed ----------------------------------------------------------------------------------------------------------------------
Lr, rr, _ = play(21, 10, D.RandomLegalDriver(5))
Ly, ry, _ = play(21, 10, D.ReplayDriver(Lr.choice_log))
check("a random-legal league with its tables replays exactly from its choice log", FP.fingerprint_of(Lr, rr) == FP.fingerprint_of(Ly, ry) and [(e["id"], e["chosen"]) for e in Lr.choice_log] == [(e["id"], e["chosen"]) for e in Ly.choice_log] and interviews_of(Lr) == interviews_of(Ly))
import tempfile  # noqa: E402
db = os.path.join(tempfile.mkdtemp(), "t.db")
A, ra2, rng_a = play(5, 5, D.AgentDriver(AG.StandIn(), workers=12))
store.save(db, A, rng_a, 5)
B, rng_b, y = store.load(db)
resA = play(None, 6, D.AgentDriver(AG.StandIn(), workers=12), start=6, lg=A, rng=rng_a)
resB = play(None, 6, D.AgentDriver(AG.StandIn(), workers=12), start=6, lg=B, rng=rng_b)
check("a league saved mid-way with guarantees on its cards, loaded and played on, equals the one that never stopped", FP.fingerprint_of(A, ra2 + resA[1]) == FP.fingerprint_of(B, ra2 + resB[1])
      and [(c.name, c.protected_until) for c in A.coaches] == [(c.name, c.protected_until) for c in B.coaches] and A.choice_log == B.choice_log)
t0 = time.time()
Lt, rt, _ = play(5, 1, D.AgentDriver(AG.StandIn(delay=0.05), workers=12))
dt = time.time() - t0
t0 = time.time()
play(5, 1, None)
base = time.time() - t0
nd = len(Lt.choice_log)
check(f"one season of {nd} decisions with a 50 ms agent costs {dt - base:.1f}s over the engine's {base:.1f}s (one at a time: {0.05 * nd:.1f}s): the tables of all 48 CEOs run side by side", dt - base < 0.05 * nd / 3)
try:
    class Forever(TB.Table):
        def next_point(self):
            return D.DecisionPoint("x", 1, 1, "owner", Lp.owners[0], {}, [dict(id="a", label="a", tags={})], "a")

        def apply(self, pick):
            pass
    f = Forever()
    f.points = []
    TB.run_tables(Lp, [f])
    check("a table that never ends is stopped rather than hanging the league", False)
except RuntimeError:
    check("a table that never ends is stopped rather than hanging the league", True)

print()
if failures:
    print(f"{len(failures)} table check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All table checks passed.")
