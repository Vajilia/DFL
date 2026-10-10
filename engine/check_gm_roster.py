"""Checks for the GM building the roster (gm_roster.py) and role utility (roles.py): the draft position, re-signing and extensions, marquee free agents
and trades are the GM's Decision Points; the old rule is each one's default, so a league on the autopilot is unchanged.

    python engine/check_gm_roster.py
"""
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agents as AG  # noqa: E402
import decisions as D  # noqa: E402
import economy as EC  # noqa: E402
import gm_roster as GMR  # noqa: E402
import roles  # noqa: E402
import offseason as OFF  # noqa: E402
from league import new_league  # noqa: E402
from players import make_player  # noqa: E402
from positions import ROSTER_SIZE, STARTERS  # noqa: E402
from season import Options, run_season  # noqa: E402
import rules as R  # noqa: E402

failures = []
KINDS = ("gm_draft_pick", "gm_resign", "gm_free_agent", "gm_trade_sell", "gm_trade_buy")


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def play(seed, years, driver=None):
    r = random.Random(seed)
    L = new_league(r, rosters=True)
    L.driver = driver
    res = [run_season(L, y, r, Options(engine="fast", keep_boxes=False)) for y in range(1, years + 1)]
    return L, r, res


class Rule:
    """A driver that answers some kinds with a rule (a function of the decision) and everything else with the autopilot."""
    name = "rule"

    def __init__(self, rules):
        self.rules, self.seen = rules, {}

    def choose(self, dp):
        self.seen.setdefault(dp.kind, dp.public())
        f = self.rules.get(dp.kind)
        return (f(dp), "test") if f else (dp.default, "autopilot")


def trades(L):
    return sum(1 for e in L.movement.events if e["kind"] == "trade")


# ---- role utility -------------------------------------------------------------------------------------------------
L0, _, _ = play(33, 2)
t = L0.teams[0]
rng0 = random.Random(1)
ok_formula = True
for pos in STARTERS:
    for ovr in (35.0, 55.0, 62.0, 75.0, 90.0):
        c = make_player(rng0, 99999, pos, ovr, 25)
        floor = sorted((p.ovr for p in t.roster if p.pos == pos), reverse=True)
        floor = floor[STARTERS[pos] - 1] if len(floor) >= STARTERS[pos] else 45.0
        old = (c.ovr - floor) * (1.0 + 0.4 * STARTERS[pos]) + 5.0 if c.ovr > floor else c.ovr - 60.0
        ok_formula &= abs(OFF._gain(t.roster, c) - old) < 1e-9 and abs(roles.utility(t.roster, pos, c.ovr) - old) < 1e-9
check("role utility is exactly the number the free-agency rule always used (so the autopilot is unchanged)", ok_formula)
roles_seen = {roles.role_of(t.roster, p) for p in t.roster}
starters = [p for p in t.roster if roles.role_of(t.roster, p) == "starter"]
check("every player on a club has a role; the starters are the best at each position and there are the right number of them",
      roles_seen <= set(roles.ROLES) and len(starters) == sum(STARTERS.values()) and all(p.ovr >= max((q.ovr for q in t.roster if q.pos == p.pos), default=0) - 60 for p in starters))
best_wr = max((p for p in t.roster if p.pos == "WR"), key=lambda p: p.ovr)
worst_wr = min((p for p in t.roster if p.pos == "WR"), key=lambda p: p.ovr)
check("a newcomer better than the weakest starter would start; one worse than every player would be depth",
      roles.role_if_signed(t.roster, "WR", best_wr.ovr + 1) == "starter" and roles.role_if_signed(t.roster, "WR", worst_wr.ovr - 30) == "depth")
check("each seat has a plain-words yardstick; the Coronation tops every decision and the yardstick comes with it",
      all(roles.judged_on(k) for k in ("owner", "gm", "coach", "coordinator", "player", "fans")) and "Coronation" in roles.judged_on("gm") + D.coronation(L0, t.id)["goal"])

# ---- the autopilot: everything is asked, everything is the rule's answer -----------------------------------------------
L1, _, res1 = play(33, 6)
by = {k: [e for e in L1.choice_log if e["kind"] == k] for k in KINDS}
check("the GM is asked about draft positions (round 1), re-signings, free agents who would start and trades",
      all(len(v) > 0 for v in by.values()), {k: len(v) for k, v in by.items()})
check("the draft asks about the first round each year: 48 picks, the GMs' own, wherever they were traded", len(by["gm_draft_pick"]) == 6 * R.TOTAL_TEAMS, len(by["gm_draft_pick"]))
check("on the autopilot every answer is the rule's own answer", all(e["chosen"] == e["default"] and e["status"] == "ok" for k in KINDS for e in by[k]))
check("a draft pick offers the rule's position and one other (the one with the most role utility)", all(e["default"] in e["options"] and len(e["options"]) == 2 for e in by["gm_draft_pick"]))
check("the GM who starts a trade is asked (the seller of a veteran, or the club moving up in a pick swap), once per trade, and trades happen",
      len(by["gm_trade_sell"]) > 0 and len(by["gm_trade_buy"]) > 0 and len(by["gm_trade_sell"]) + len(by["gm_trade_buy"]) >= trades(L1) > 0, f"{trades(L1)} trades")

# ---- what the GM sees ----------------------------------------------------------------------------------------------------
rule = Rule({})
play(33, 3, rule)
pick, res_dp, fa, sell = (rule.seen.get(k) for k in ("gm_draft_pick", "gm_resign", "gm_free_agent", "gm_trade_sell"))
check("a draft decision shows the Coronation and what the seat is judged on first, the expected rookie, and each position's role utility",
      pick is not None and "Coronation" in pick["top_priority"]["goal"] and pick["top_priority"]["you_are_judged_on"].startswith("Judged by the CEO")
      and all("role_utility" in o["tags"] and o["tags"]["would_be"] in roles.ROLES for o in pick["options"]) and "rookie_rating_expected_at_this_slot" in pick["context"])
check("a re-signing shows her role utility to the club, her price and the role she would have, but not her true rating",
      res_dp is not None and {"role_utility_to_you", "her_price_per_year_m", "her_role_if_kept"} <= set(res_dp["context"]) and "rating_as_you_see_her" in res_dp["context"]["player"]
      and "ovr" not in str(res_dp["context"]).replace("rating", ""))
check("a free-agent decision lists the candidates with price, role and utility as she sees them", fa is not None and 2 <= len(fa["options"]) <= GMR.FA_SHOWN and all("price_m" in o["tags"] for o in fa["options"]))
check("a trade decision shows what she gives and gets, the chart points and the role utility she gains and loses",
      sell is not None and {"you_give", "you_get", "chart_points_you_give", "chart_points_you_get", "role_utility_you_lose", "role_utility_you_gain"} <= set(sell["context"]))

# a better eye blurs less, and the blur is the GM's own (not the engine's random stream)
g = L1.teams[0].gm
sd = {}
for rating in (10.0, 50.0, 95.0):
    g.ratings["evaluation"] = rating
    sd[rating] = st.pstdev([GMR._eye(L1, g, "t", y, i, 70.0) - 70.0 for y in range(1, 6) for i in range(200)])
check("a GM with a better eye sees ratings more clearly (about 1 point for the best, 6 for the worst)", sd[95.0] < sd[50.0] < sd[10.0] and sd[95.0] < 1.7 and 4.0 < sd[10.0] < 8.0,
      {k: round(v, 2) for k, v in sd.items()})
check("the same GM sees the same player the same way (the blur is private to her card)", GMR._eye(L1, g, "t", 3, 7, 70.0) == GMR._eye(L1, g, "t", 3, 7, 70.0))

# ---- choices change things, always inside the rules --------------------------------------------------------------------
def flip(dp):
    others = [o for o in dp.option_ids if o != dp.default]
    return others[0] if others else dp.default


counts = {}


def other(dp):
    counts[dp.kind] = counts.get(dp.kind, 0) + 1
    return flip(dp)


La, ra, _ = play(33, 4, Rule({k: other for k in KINDS}))
check("a GM who always overrules the rule changes the league (but the rosters are always full and legal)",
      all(len(t.roster) == ROSTER_SIZE and len(t.practice_squad) == R.PRACTICE_SQUAD_SIZE for t in La.teams) and [t.strength for t in La.teams] != [t.strength for t in L1.teams],
      {k: counts.get(k, 0) for k in KINDS})
check("her overrides are on her card and in the choice log", any("took a" in d["action"] or "signed a" in d["action"] or "declined" in d["action"] or "re-signed" in d["action"] or "let go" in d["action"] for t in La.teams for d in t.gm.decision_log)
      and any(e["chosen"] != e["default"] for e in La.choice_log if e["kind"] in KINDS))
check("the cap still rules: no club is over the hard cap after any of it", all(EC.payroll(t) <= EC.limit(t) + 1e-6 for t in La.teams))

Ld, _, _ = play(33, 3, Rule({"gm_trade_sell": lambda dp: "decline"}))
def pick_swaps(L):
    return sum(1 for e in L.movement.events if e["kind"] == "trade" and not e["players"][0] and not e["players"][1])


check("a seller who declines stops the sale of her veteran (and a swap-up GM who declines stops the swap)",
      trades(Ld) - pick_swaps(Ld) == 0 and pick_swaps(Ld) > 0, f"{trades(Ld)} trades, {pick_swaps(Ld)} swaps")
Lb, _, _ = play(33, 3, Rule({"gm_trade_buy": lambda dp: "decline"}))
check("a swap-up GM who declines stops the swaps but not the sales", pick_swaps(Lb) == 0 and trades(Lb) > 0, f"{trades(Lb)} trades, {pick_swaps(Lb)} swaps")

Lw, _, _ = play(33, 5, Rule({"gm_resign": lambda dp: "let_walk"}))
Lk, _, _ = play(33, 5, Rule({"gm_resign": lambda dp: "re_sign"}))
check("the re-signing choice matters: GMs who let every important player walk and GMs who keep every one that fits end up with different clubs",
      [t.strength for t in Lw.teams] != [t.strength for t in Lk.teams])

# the limits on re-signing: a cornerstone is never let go, and a GM lets at most one important player walk against the rule in an offseason
seen_rs = []
from roster_model import RosterModel  # noqa: E402
import staff_cards as SC  # noqa: E402
rm0 = RosterModel()


def walk_all(dp):
    """Always lets her go; notes, at the moment of the decision, how far above the club's keep line she was."""
    p, rest, t_ = dp.internal["player"], dp.internal["rest"], dp.internal["team"]
    price = dp.options[0]["tags"]["price_m"]
    line = rm0.keep_g0 + rm0.keep_g1 * price + rm0.keep_gm_shift * (SC.gm_retention_factor(t_) - 1.0)
    seen_rs.append((dp, roles.utility(rest, p.pos, p.ovr) - line))
    return "let_walk"


Lc, _, _ = play(33, 5, Rule({"gm_resign": walk_all}))
rule_keeps = [(dp, m) for dp, m in seen_rs if dp.default == "re_sign" and "extension" not in dp.context["what"]]
margins = [m for _, m in rule_keeps]
check("a cornerstone (role utility far above the club's keep line) is never offered for letting go", len(rule_keeps) > 0 and max(margins) <= GMR.CORNERSTONE_MARGIN + 1e-6,
      f"{len(rule_keeps)} asked, largest margin {max(margins):.1f}" if margins else "none asked")
per_club = {}
for dp, _ in rule_keeps:
    per_club[(dp.year, dp.team_id)] = per_club.get((dp.year, dp.team_id), 0) + 1
check("a GM who always lets people go loses at most one important player a year against the rule's wishes (passing on an extension costs nothing)",
      len(per_club) > 0 and max(per_club.values()) <= GMR.LET_GO_MAX, f"most in one club-year: {max(per_club.values())}")

# ---- agents ------------------------------------------------------------------------------------------------------------------
ag = AG.StandIn()
Ls, rs, _ = play(33, 4, D.AgentDriver(ag, workers=4))
mine = [e for e in Ls.choice_log if e["kind"] in KINDS]
check("the stand-in agent answers every GM roster decision, none falls back to the autopilot", len(mine) > 0 and all(e["status"] == "ok" and e["driver"] == "agent" for e in mine), len(mine))
check("a stand-in GM chooses by role utility, so some answers differ from the rule and some match", any(e["chosen"] != e["default"] for e in mine) and any(e["chosen"] == e["default"] for e in mine))
check("a stand-in's notes to self land on the GM's card", any(n["kind"] in KINDS for t in Ls.teams for n in t.gm.notes))
Lf, _, _ = play(33, 4, D.AgentDriver(AG.Flaky(AG.StandIn(), every=3), workers=4))
check("lost or garbled answers fall back to the rule and the league plays on", any(e["status"] != "ok" for e in Lf.choice_log if e["kind"] in KINDS) and all(len(t.roster) == ROSTER_SIZE for t in Lf.teams))

# ---- a club with no GM, and random choices ------------------------------------------------------------------------------------
Ln = new_league(random.Random(5), rosters=True)
for tm in Ln.teams[:3]:
    tm.gm = None
check("a club without a GM keeps the rule: nothing is asked and the draw stands", GMR.draft_pick(Ln, Ln.teams[0], 1, 5, 0, "QB", None, "needs") == "QB"
      and GMR.resign(Ln, None, Ln.teams[0], 1, Ln.teams[0].roster[0], 1.0, True, Ln.teams[0].roster, False) is True
      and GMR.free_agent(Ln, Ln.teams[0], 1, [(1.0, Ln.teams[0].roster[0]), (0.5, Ln.teams[0].roster[1])], Ln.teams[0].roster[0], lambda c: 1.0) is Ln.teams[0].roster[0])
Lr, _, _ = play(5, 6, D.RandomLegalDriver(seed=3))
check("with every GM choosing at random the league plays on with full, legal rosters", all(len(t.roster) == ROSTER_SIZE for t in Lr.teams) and all(EC.payroll(t) <= EC.limit(t) + 1e-6 for t in Lr.teams))

print()
if failures:
    print(f"{len(failures)} GM roster check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All GM roster checks passed.")
