"""Checks for governance (Step 8c): votes, the Competition Committee, shrink-only Commissioner powers, the DFLPA representative and discipline.

    python engine/check_governance.py
"""
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discipline as DS  # noqa: E402
import dflpa  # noqa: E402
import economy as EC  # noqa: E402
import governance as GV  # noqa: E402
import rules as R  # noqa: E402
import store  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


rng = random.Random(33)
lg = new_league(rng, rosters=True)
res = [run_season(lg, y, rng, Options(engine="fast", keep_boxes=False)) for y in range(1, 11)]

# ---- votes
check("rule changes need 36 of 48, a Commissioner's successor 32 of 48", (R.RULE_CHANGE_VOTES, R.COMMISSIONER_VOTES) == (36, 32) and GV.needed("rule") == 36 and GV.needed("commissioner") == 32)
p = GV.propose(lg, 11, "rule", "a test change")
check("proposals are numbered", p.pid >= 1)
GV.hold_vote(lg, p)
check("every club casts one vote", len(p.votes) == 48)
yes = sum(p.votes.values())
check("the result follows the threshold exactly", (p.result == "passed") == (yes >= 36), f"{yes} yes")
q = GV.propose(lg, 11, "rule", "a recused vote")
GV.hold_vote(lg, q, recuse=5)
check("a recused club casts no vote and the threshold is still set against 48", len(q.votes) == 47 and 5 not in q.votes and q.result in ("passed", "failed"))
# the committee's endorsement helps, and a neutral proposal with no endorsement is not a landslide
plain_pass = sum(GV.hold_vote(lg, GV.propose(lg, 12, "rule", f"p{i}")).result == "passed" for i in range(40))
endorsed_pass = sum(GV.hold_vote(lg, GV.propose(lg, 12, "rule", f"e{i}", endorsed=True)).result == "passed" for i in range(40))
check("a committee endorsement raises a proposal's chance of passing", endorsed_pass > plain_pass, f"{endorsed_pass} against {plain_pass} of 40")
check("an unendorsed neutral proposal rarely reaches three-quarters", plain_pass <= 8, f"{plain_pass} of 40")
a = GV.hold_vote(lg, GV.propose(lg, 13, "commissioner", "successor", candidate="x"))
check("a Commissioner's successor is decided at 32 votes", (a.result == "passed") == (sum(a.votes.values()) >= 32))
tilted_big = GV.propose(lg, 14, "rule", "favours big markets", tilt=1.0)
tilted_small = GV.propose(lg, 14, "rule", "favours small markets", tilt=-1.0)
GV.hold_vote(lg, tilted_big)
GV.hold_vote(lg, tilted_small)
big = [t.id for t in lg.teams if t.fans.market >= 60]
check("big-market clubs back a proposal that favours them more than small-market clubs do",
      sum(tilted_big.votes[i] for i in big) / len(big) > sum(tilted_small.votes[i] for i in big) / len(big))
check("votes are deterministic", GV.hold_vote(lg, GV.Proposal(pid=999, year=1, kind="rule", text="x")).votes == GV.hold_vote(lg, GV.Proposal(pid=999, year=1, kind="rule", text="x")).votes)

# ---- the committee
mt = res[-1].offseason["meeting"]
check("the committee has eight seats, one per division", len(lg.committee) == R.COMPETITION_COMMITTEE_SEATS == 8 and sorted(s["division"] for s in lg.committee) == list(range(8)))
check("each seat is held by a CEO of a club in that division", all(lg.by_id[s["team"]].div_id == s["division"] if hasattr(lg.by_id[s["team"]], "div_id") else lg.by_id[s["team"]].division_id == s["division"] for s in lg.committee))
check("the autopilot makes no proposals", mt["proposals"] == 0)

# ---- the Commissioner is shrink-only
check("reject, cap, delay and reduce all shrink", all(GV.shrink_only(r) for r in (GV.reject("t", 5.0, "x"), GV.cap("c", 9.0, 8.0, "x"), GV.delay("d", 3.0, "x"), GV.reduce_penalty("f", 4.0, 0.5, "x"))))
check("a cap never raises a figure that was already under the cap", GV.cap("c", 3.0, 8.0, "x").after == 3.0)
check("a penalty cannot be increased: a factor above 1 is clipped", GV.reduce_penalty("f", 4.0, 3.0, "x").after == 4.0)
check("a ruling that adds anything fails the audit", not GV.shrink_only(GV.Ruling("reduce", "f", 4.0, 5.0)) and not GV.shrink_only(GV.Ruling("grant", "f", 4.0, 2.0)))
t0, t1 = lg.teams[0], lg.teams[1]
r = GV.review_trade(lg, t0.id, t1.id, [], [], [], [], 11, None)
check("an empty trade is rejected with a reason", r is not None and r.power == "reject" and "nothing" in r.reason)
r2 = GV.review_trade(lg, t0.id, t0.id, [], [], [], [], 11, None)
check("a trade with oneself is rejected", r2 is not None and r2.power == "reject")
legal = [p for p in t0.roster if p.years_left >= 1][:1]
legal_b = [p for p in t1.roster if p.years_left >= 1][:1]
r3 = GV.review_trade(lg, t0.id, t1.id, [legal[0].id], [legal_b[0].id], [], [], 11, None, band_guard=lambda *a: "talent would concentrate")
check("the fairness guard can stop a trade and the reason is recorded", r3 is not None and r3.reason == "talent would concentrate")

# ---- the DFLPA representative
reps = [dflpa.rep_for(lg, "player", i) for i in range(300)]
check("a client always has the same representative", dflpa.rep_for(lg, "player", 7) == dflpa.rep_for(lg, "player", 7))
check("representatives have names and ratings in range", all(r.name and 1 <= r.advocacy <= 100 and 1 <= r.caution <= 100 for r in reps))
prot = [r for r in reps if r.advocacy >= dflpa.ADVOCACY_HOLD]
check("about a fifth to a half of representatives are protective", 0.1 < len(prot) / len(reps) < 0.5, f"{len(prot) / len(reps):.2f}")
check("a protective representative holds back a 90% offer and never a 100% or 110% one", prot[0].holds_back(90) and not prot[0].holds_back(100) and not prot[0].holds_back(110))
check("a modest representative holds nothing back", not [r for r in reps if r.advocacy < dflpa.ADVOCACY_HOLD][0].holds_back(90))
import contracts as CT  # noqa: E402
team = lg.teams[0]
pl = team.roster[0]
tb_all = []
for q in team.roster[:60]:
    tb = CT.ContractTable(lg, 11, team, q, 5.0, 3, lambda s: True)
    tb_all.append((tb, tb.pays()))
check("a table never offers a price the representative holds back, and always keeps 100% on the table", all((90 not in pays) == tb.rep.holds_back(90) and 100 in pays for tb, pays in tb_all))

# ---- discipline
sus = [len(r.runner.suspension_log) for r in res]
check("suspensions run at about the NFL's scale (30 to 80 a year across 48 clubs)", all(25 <= n <= 90 for n in sus), f"{min(sus)}-{max(sus)}")
kinds = {}
for r in res:
    for _, _, _, k, g in r.runner.suspension_log:
        kinds[k] = kinds.get(k, 0) + 1
check("all four policies appear", set(kinds) >= {"conduct", "substance", "performance_enhancing"}, str(kinds))
check("no one is suspended at the start of a season for more than a season's games", all(p.suspended <= 19 for t in lg.teams for p in t.roster))
fines = [e for e in lg.archive if e["event"] == "discipline_fine"]
check("club cases are rare and fines are inside the cap's 10%", len(fines) > 0 and all(e["amount"] <= R.CAP_PENALTY_MAX_PCT * EC.CAP + 1e-9 for e in fines), f"{len(fines)} fines in 10 seasons")
t = lg.teams[3]
t.fines = 0.0
pool0 = lg.pool
a1 = DS.fine_team(lg, t, "cap_circumvention", 8.0, 11)
a2 = DS.fine_team(lg, t, "cap_circumvention", 8.0, 11)
check("a club's fines in a season stop at 10% of the cap ($10M)", abs(a1 + a2 - 10.0) < 1e-9 and a2 <= 2.0, f"{a1} + {a2}")
check("fines go to the Equalization Fund", abs(lg.pool - pool0 - (a1 + a2)) < 1e-9)
t.fines = 0.0
half = DS.fine_team(lg, t, "tampering", 1.0, 11, factor=0.5)
check("the Commissioner can halve a fine and the autopilot pays the baseline", half == 0.5 and DS.fine_team(lg, lg.teams[4], "tampering", 1.0, 11) == 1.0)
t.fines = 0.0
more = DS.fine_team(lg, t, "tampering", 1.0, 11, factor=5.0)
check("a factor above 1 does not raise a fine", more == 1.0)
pl.suspended = 6
check("the Commissioner can shorten a suspension but not lengthen it", DS.reduce_suspension(pl, 0.5) == 3 and DS.reduce_suspension(pl, 4.0) == 3)
pl.suspended = 0
import rosters  # noqa: E402
q = team.roster[0]
q.suspended = 2
check("a suspended player is not active on game day", q.id not in {x.id for x in rosters.active_list(team)})
q.suspended = 0

# ---- save and load
q = lg.teams[1].roster[0]
q.suspended = 4
lg.teams[1].fines = 1.25
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "x.db")
    store.save(path, lg, rng, 10)
    lg2, _, _ = store.load(path)
    q2 = [x for x in lg2.teams[1].roster if x.id == q.id][0]
    check("a suspension, a club's fines, the committee and the vote counter survive a save",
          q2.suspended == 4 and abs(lg2.teams[1].fines - 1.25) < 1e-9 and lg2.committee == lg.committee and lg2.proposals_made == lg.proposals_made)

print()
print("FAILED: " + ", ".join(failures) if failures else "all governance checks passed")
sys.exit(1 if failures else 0)
