"""Checks for the enrichment agent and the profile page (enrichment.py): a bio is flavour from the card's own facts, an agent may write it but never has
to, and nothing about a league's results depends on it.

    python engine/check_enrichment.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enrichment as EN  # noqa: E402
import cards as C  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def play(seed, years, enricher=None):
    r = random.Random(seed)
    L = new_league(r, rosters=True)
    L.enricher = enricher
    seen = []
    for y in range(1, years + 1):
        res = run_season(L, y, r, Options(engine="fast", keep_boxes=False))
        seen.append(res.get("offseason", {}).get("enrichment") if isinstance(res, dict) else None)
    return L, r, seen


calls = []


def good_agent(payload):
    calls.append(payload)
    f = payload["facts"]
    return f"{f['name']} came out of {f['college']} with a reputation for hard work, and {f['hometown']} still claims her as its own."


L0, r0, _ = play(33, 4)
players0 = [p for t in L0.teams for p in list(t.roster) + list(t.practice_squad) + list(t.ir)] + list(L0.free_agents)
rook = [p for p in players0 if p.draft_year == 3 and p.draft_pick and p.draft_pick <= EN.ENRICH_MAX_PICK and p.card is not None]
check("with no agent every draftee of the first two rounds gets the code writer's paragraph, and her card says so", rook and all(p.card.enriched == "code" and EN.valid(p.card.bio, EN.facts(L0, p)) for p in rook))
p = rook[0]
check("the code writer's paragraph is the same every time for the same card and is about her", EN.code_bio(L0, p) == EN.code_bio(L0, p) and p.card.name in p.card.bio and p.origin["college"] in p.card.bio)
state = r0.getstate()
vet = next(q for q in players0 if q.card is not None and not q.card.enriched)
check("later-round players and veterans are not written up until someone asks", vet.card.bio == "" and vet.card.enriched == "")
EN.ensure_bio(L0, vet)
check("writing a bio never touches the engine's random stream, and anyone who is shown gets one", r0.getstate() == state and vet.card.enriched == "code" and vet.card.bio)

L1, _, seen = play(33, 4, good_agent)
agent_rows = [p for t in L1.teams for p in t.roster if p.card is not None and p.card.enriched == "agent"]
check("with an agent the first two rounds are written by it, up to the yearly budget, in pick order",
      agent_rows and all(p.draft_pick <= EN.ENRICH_MAX_PICK for p in agent_rows) and len(calls) <= EN.AGENT_CALLS_PER_YEAR * 4
      and all(s is None or s["agent_calls"] <= EN.AGENT_CALLS_PER_YEAR for s in seen), (len(calls), len(agent_rows)))
keys = set(calls[0]["facts"])
check("the agent is given the player's facts but never her ratings", not ({"ratings", "ovr", "perceived"} & keys) and "level" in keys and all(isinstance(x, (str, int, dict, list, type(None))) for x in calls[0]["facts"].values()))

for label, bad in (("an agent that raises", lambda pl: 1 / 0), ("an agent that answers nonsense", lambda pl: "ok"), ("an agent that answers a novel",
                   lambda pl: pl["facts"]["name"] + " " + "x" * 3000), ("an agent that answers nothing", lambda pl: None)):
    Lb, _, _ = play(33, 3, bad)
    rb = [p for t in Lb.teams for p in list(t.roster) + list(t.practice_squad) + list(t.ir) if p.card is not None and p.draft_year == 2 and p.draft_pick and p.draft_pick <= EN.ENRICH_MAX_PICK]
    check(f"{label}: the code writer's paragraph stands and the league plays on", rb and all(p.card.enriched == "code" and p.card.bio for p in rb))

# the league's results do not depend on whether anyone writes about it
def sig(L):
    return [(p.id, round(p.ovr, 3), p.team_id) for t in L.teams for p in sorted(t.roster, key=lambda q: q.id)]


La, _, _ = play(33, 4, None)
Lb, _, _ = play(33, 4, good_agent)
check("the same league with and without an agent has exactly the same players on exactly the same teams", sig(La) == sig(Lb))

# the profile page
page = EN.profile(L1, agent_rows[0], 4)
c = agent_rows[0].card
check("a profile page is rendered from the card: name, birth, hometown, college, bio, four college seasons and a pro career, and kept on the card",
      c.profile == page and all(x in page for x in (c.name, c.dob, c.hometown, agent_rows[0].origin["college"], c.bio, "## College career", "## Pro career", "drafted"))
      and page.count("| FR |") + page.count("| SO |") + page.count("| JR |") + page.count("| SR |") == 4)
check("the card printout carries her origin and her bio", "ORIGIN:" in C.render_player(agent_rows[0], L1) and "BIO (agent):" in C.render_player(agent_rows[0], L1))

if failures:
    print(f"\n{len(failures)} FAILED")
    sys.exit(1)
print("\nAll enrichment checks passed.")
