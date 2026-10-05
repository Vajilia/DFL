"""Write reports/card_samples.md: sample player and coach cards from a simulated league, plus how the cards
spread across the league.

    python engine/card_report.py [--seed 1] [--seasons 6]
"""
import argparse
import collections
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import fan_media_cards as FM  # noqa: E402
import decisions as DEC  # noqa: E402
import interactions as IX  # noqa: E402
import json  # noqa: E402
import staff_cards as S  # noqa: E402
from league import new_league  # noqa: E402
from positions import POSITIONS  # noqa: E402
from season import Options, run_season  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seasons", type=int, default=14)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    lg = new_league(rng, rosters=True)
    for y in range(1, a.seasons + 1):
        res = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False))
    out = ["# Character cards: samples\n",
           f"Seed {a.seed}, after {a.seasons} seasons. Names, hometowns and backgrounds come from placeholder word lists "
           "(engine/card_pools.py) that you can replace. Ratings, archetypes and the coach effect are real: they come from "
           "the engine. Relationships and the decision log start empty and fill as the Interaction system plays scenes (firings, recall votes and exile determinations so far).\n",
           "## How to read a card\n",
           "- **Soul (archetypes)** is fixed for life. It is read from the rating profile she is born with: her best attribute names the positive archetype and her weakest the negative one. Her development is bent to stay true to it.",
           "- **Personality** is how her soul shows up. Her archetype allows four personalities; which one she shows depends on her temperament and on how she rates herself. Her self-image lags the truth, so a declining veteran overrates herself and a rising rookie undersells herself. When her confidence moves enough, her personality can shift, but only inside the four her soul allows.",
           "- **Pressure thresholds** (exile, contract, spotlight, loyalty) are how much each kind of pressure rattles her, 1 to 100. They do nothing yet; the Interaction system will use them.",
           "- **Fanbases and outlets**: a fanbase has a culture (its personality), five ratings and two stores: approval of the owner and Fan Capital (goodwill built by sustained success, which only ever buffers a recall). Its expectations drift with what the team delivers, inside a bound set at birth. An outlet has a voice, five ratings and Credibility, which rises when its forecasts come true and falls when they miss; one that stays irrelevant folds and is replaced. The press can move an owner's approval by at most 3 points a year.",
           "- **Coach ratings**: offense and defense lift the team (up to +/- 1.0 point of margin each); development adds up to 0.4 rating points a year to each young player. The other three are stored for later. Legends are the rare all-time greats.\n"]
    out.append("## A franchise player at each position group\n")
    active = [p for t in lg.teams for p in t.roster]
    for pos in ("QB", "WR", "OL", "DL", "CB", "K"):
        best = max((p for p in active if p.pos == pos), key=lambda p: p.ovr)
        out.append(render := C.render_player(best, lg))
    out.append("\n## A young rookie and a veteran\n")
    rookies = [p for p in active if p.draft_year == a.seasons]
    if rookies:
        out.append(C.render_player(min(rookies, key=lambda p: p.draft_pick), lg))
    vet = max((p for p in active if p.years_in_league > 8), key=lambda p: p.ovr, default=None)
    if vet:
        out.append(C.render_player(vet, lg))
    changed = [p for p in active if any(e["event"] == "personality_shift" for e in p.card.career) and p.ovr >= 60]
    out.append("\n## A player whose personality changed (her soul stayed the same)\n")
    if changed:
        out.append(C.render_player(max(changed, key=lambda p: sum(e["event"] == "personality_shift" for e in p.card.career)), lg))
    out.append("\n## A retired player (cards are kept for the Archive)\n")
    ret = max(lg.retired_players, key=lambda p: p.ovr)
    out.append(C.render_player(ret, lg))
    out.append("\n## Head coaches: a legend, a typical coach and a weak one\n")
    legends = [t for t in lg.teams if t.coach.legend]
    ranked = sorted(lg.teams, key=lambda t: t.coach.offense_points + t.coach.defense_points + t.coach.development_points)
    if legends:
        out.append(C.render_coach(legends[0].coach, lg))
    out.append(C.render_coach(ranked[len(ranked) // 2].coach, lg))
    out.append(C.render_coach(ranked[0].coach, lg))
    out.append("\n## An owner, a GM, and the Archive's first entries\n")
    top = max(lg.teams, key=lambda t: t.owner.seasons_owned)
    out.append(S.render_owner(top.owner, lg))
    recalled = [o for o in lg.owners if o.status == "recalled"]
    if recalled:
        out.append(S.render_owner(recalled[-1], lg))
    out.append(S.render_gm(max(lg.teams, key=lambda t: abs(t.gm.scouting_points) + abs(1 - t.gm.retention_factor)).gm, lg))
    votes = [e for e in lg.archive if e["event"] == "recall_vote"]
    out.append("**A recall vote as the Archive logs it:**\n")
    ex = next((e for e in reversed(votes) if e["result"] == "recalled"), None)
    if ex:
        out.append("```\n" + "\n".join(f"{k}: {v}" for k, v in ex.items()) + "\n```\n")
    out.append("\n## A fanbase and the press that covers it\n")
    drift = lambda t: t.fans.ratings["expectations"] - t.fans.birth_expectations
    out.append(FM.render_fanbase(max(lg.teams, key=drift).fans, lg))
    out.append(FM.render_fanbase(min(lg.teams, key=drift).fans, lg))
    out.append(FM.render_fanbase(max(lg.teams, key=lambda t: t.fans.capital).fans, lg))
    live = [m for m in lg.media if m.status == "active"]
    out.append(FM.render_outlet(max((m for m in live if m.kind == "national"), key=lambda m: m.credibility), lg))
    out.append(FM.render_outlet(min((m for m in live if m.kind == "national"), key=lambda m: m.credibility), lg))
    out.append(FM.render_outlet(max((m for m in live if m.kind == "local"), key=lambda m: m.credibility), lg))
    gone = [m for m in lg.media if m.status == "folded"]
    if gone:
        out.append("**An outlet that folded (the Archive keeps the card):**\n")
        out.append(FM.render_outlet(min(gone, key=lambda m: m.credibility), lg))
        ev = next((e for e in lg.archive if e["event"] == "outlet_folded"), None)
        if ev:
            out.append("```\n" + "\n".join(f"{k}: {v}" for k, v in ev.items()) + "\n```\n")
    out.append("\n## Scenes as the Archive records them\n")
    out.append("Each firing, recall vote and exile determination is a scene: every party gives its own claim, and the evidence section says, from the engine's own numbers, which claims hold. "
               "The scenes never change an outcome (the check script proves a league plays out identically with them on or off); they explain it, and they move relationships and decision logs.\n")
    sc = [e for e in lg.archive if e["event"] == "interaction"]
    def pick(pred, label):
        e = next((x for x in reversed(sc) if pred(x)), None)
        if e:
            out.append(f"**{label}**\n")
            out.append("```\n" + IX.render_scene(e, lg) + "\n```\n")
    pick(lambda x: x["kind"] == "exile_determination", "An exile determination")
    pick(lambda x: x["kind"] == "firing" and x["evidence"].get("ruling") == "fair", "A firing the record backs")
    pick(lambda x: x["kind"] == "firing" and x["evidence"].get("ruling") == "harsh", "A harsh firing (the roster explains the record)")
    pick(lambda x: x["kind"] == "firing" and x["evidence"].get("ruling") == "sweep", "A new owner's sweep")
    pick(lambda x: x["kind"] == "recall_vote" and "recalled;" in x["outcome"], "A recall vote that removes an owner")
    pick(lambda x: x["kind"] == "recall_vote" and x["outcome"].endswith("survives"), "A recall vote the owner survives")
    out.append("\n## What an agent is shown, and what the log keeps\n")
    out.append("Choices go through Decision Points. An agent is shown its own card, what it perceives (candidates' ratings as the owner sees them, with blind spots) and the legal options, and answers with one option id. "
               "The guard applies the choice (or the autopilot's choice if the answer is invalid or late) and logs it. Below: the two decisions an owner faces, as an agent receives them, and the log line.\n")
    seen = []

    def spy(payload):
        seen.append(payload)
        pick = max(payload["options"], key=lambda o: o.get("tags", {}).get("fires", 0))["id"] if payload["kind"] == "staff_review" else payload["options"][0]["id"]
        return {"choice": pick, "reason": "Illustrative answer from a stand-in agent."}
    rng2 = random.Random(a.seed + 1)
    lg2 = new_league(rng2, rosters=True)
    lg2.driver = DEC.AgentDriver(spy, timeout=10.0)
    for y in range(1, 4):
        run_season(lg2, y, rng2, Options(engine="fast", keep_boxes=False))
    rev = next(p for p in seen if p["kind"] == "staff_review")
    hire = next(p for p in seen if p["kind"] == "hire_coach")
    out.append("**An owner's staff review, as an agent receives it:**\n")
    out.append("```json\n" + json.dumps(rev, indent=1) + "\n```\n")
    out.append("**A coaching hire, as an agent receives it:**\n")
    out.append("```json\n" + json.dumps(hire, indent=1) + "\n```\n")
    out.append("**The choice log keeps:**\n")
    out.append("```\n" + "\n".join(json.dumps(e) for e in lg2.choice_log if e["kind"] == "hire_coach")[:1200] + "\n```\n")
    out.append("\n## How the cards spread across the league\n")
    tc = collections.Counter(p.card.trait for p in active)
    out.append("**Core personalities (all rostered players):** " + ", ".join(f"{k} {v}" for k, v in tc.most_common()) + "\n")
    ac = collections.Counter(p.card.archetype_pos for p in active)
    out.append("**Most common positive archetypes:** " + ", ".join(f"{k} {v}" for k, v in ac.most_common(8)) + "\n")
    eff = [t.coach.offense_points + t.coach.defense_points for t in lg.teams]
    out.append(f"**Coach effect across the 48 teams:** average {st.mean(eff):+.2f}, spread (sd) {st.pstdev(eff):.2f}, "
               f"best {max(eff):+.2f}, worst {min(eff):+.2f} points of expected margin. For scale, team talent has a spread of about 3 to 4 points.\n")
    shifts = sum(any(e["event"] == "personality_shift" for e in p.card.career) for p in active + list(lg.retired_players))
    out.append(f"**Personality shifts:** {shifts} of {len(active) + len(lg.retired_players)} players have changed personality at least once in {a.seasons} seasons.\n")
    out.append(f"**Legends:** {sum(c.legend for c in lg.coaches)} of {len(lg.coaches)} coaches hired so far are legends; {len(legends)} on the field now.\n")
    cc = collections.Counter(t.fans.culture for t in lg.teams)
    out.append("**Fan cultures:** " + ", ".join(f"{k} {v}" for k, v in cc.most_common()) + "\n")
    cap = [t.fans.capital for t in lg.teams]
    out.append(f"**Fan Capital:** average {st.mean(cap):.2f}, from {min(cap):.2f} to {max(cap):.2f}; "
               f"the most it can buffer a recall vote is {100 * FM.CAPITAL_RECALL_WEIGHT * (1 - FM.CAPITAL_FLOOR):.0f} points.\n")
    sway = [abs(t.fans.last_sway) for t in lg.teams]
    out.append(f"**The press on approval, last season:** average {100 * st.mean(sway):.1f} points either way, largest {100 * max(sway):.1f} (the cap is {100 * FM.MEDIA_SWAY:.0f} before market size and trust).\n")
    cr = [m.credibility for m in live]
    out.append(f"**Outlets:** {len(live)} active ({FM.N_NATIONAL} national, one local beat per team); credibility averages {st.mean(cr):.0f}, "
               f"from {min(cr):.0f} to {max(cr):.0f}; {len(gone)} have folded and been replaced in {a.seasons} seasons.\n")
    rul = collections.Counter(e["evidence"]["ruling"] for e in sc if e["kind"] == "firing")
    out.append(f"**Scenes:** {len(sc)} in {a.seasons} seasons ({collections.Counter(e['kind'] for e in sc).most_common()}). "
               f"Firings by ruling: {', '.join(f'{k} {v}' for k, v in rul.most_common())}.\n")
    yrs = a.seasons
    nv = len(votes)
    nr = sum(e["result"] == "recalled" for e in votes)
    out.append(f"**Recall votes:** {nv} in {yrs} seasons ({nv / yrs:.1f} a year); {nr} owners recalled ({nr / yrs:.1f} a year), "
               f"{100 * nr / max(1, nv):.0f}% of votes. Owners retire on their own too: {sum(o.status == 'retired' for o in lg.owners)} so far.\n")
    out.append(f"**Firings:** {sum(e['event'] == 'coach_fired' for e in lg.archive)} coaches and {sum(e['event'] == 'gm_fired' for e in lg.archive)} GMs fired in {yrs} seasons.\n")
    out.append(f"**Coaches so far:** {len(lg.coaches)} hired and {sum(c.retired for c in lg.coaches)} retired in {a.seasons} seasons.\n")
    out.append(f"**Players with cards:** {len(active) + len(lg.free_agents)} active or unsigned, {len(lg.retired_players)} retired.\n")
    path = os.path.join(ROOT, "reports", "card_samples.md")
    open(path, "w").write("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    main()
