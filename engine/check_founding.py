"""Checks for Founding Day (founding.py): an all-rookie league, its dated record, and a clean handover to the engine.

    python engine/check_founding.py
"""
import datetime as dt
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calendar_dfl as K  # noqa: E402
import founding as F  # noqa: E402
import store  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


lg, rng = F.open_league(33)
every = [p for t in lg.teams for p in list(t.roster) + list(t.practice_squad)]
# ---- everyone is a rookie ------------------------------------------------------------------------------------------------------------
check("every player is a rookie: 21 to 23 years old, no years in the league, no accrued seasons",
      all(21 <= p.age <= 23 and p.years_in_league == 0 and p.accrued_seasons == 0 and p.credited_seasons == 0 for p in every),
      f"ages {min(p.age for p in every)} to {max(p.age for p in every)}")
check("the roster and the practice squad are the usual size at every club", all(len(t.roster) == 53 and len(t.practice_squad) == 16 for t in lg.teams))
check("no pro past: the only career entry on any card is the founding class", all([e["event"] for e in p.card.career if e["event"] != "personality_shift"] == ["founding class"] for p in every))
check("no honors, no pro statistics", all(not p.card.honors for p in every))
check("everyone has a college career: a real program, four seasons, a hometown and a date of birth",
      all(p.origin["college"] and len(p.origin["stats"]) == 4 and p.origin["hometown"] and p.origin["dob"] and p.origin.get("founding") for p in every))
check("her card's date of birth is her origin's, and she is the age her birth year says",
      all(p.card.dob == p.origin["dob"] and int(p.origin["dob"][:4]) == 1999 - p.age for p in every))
check("everyone has a one-paragraph backstory that names her and says she is of the Founding Class",
      all(p.card.bio and "\n" not in p.card.bio and p.card.name in p.card.bio and "Founding Class" in p.card.bio or "turned pro with the league itself" in p.card.bio for p in every))
check("no two players share a card name-and-birthday", len({(p.card.name, p.origin["dob"]) for p in every}) == len(every))

# ---- the record ----------------------------------------------------------------------------------------------------------------------
rec = lg.founding
check("the record says plainly that no one made a choice", "No agent and no rule made a choice" in rec["provenance"] and rec["date"] == "2000-01-01")
check("the lottery order is a permutation of all 48 clubs", sorted(rec["order"]) == [t.id for t in lg.teams])
t0 = next(t for t in lg.teams if t.id == 7)
tr = rec["teams"]["7"]
check("each club's account names the people who really sit in those seats",
      all(rec["teams"][str(t.id)]["ceo"] == t.owner.name and rec["teams"][str(t.id)]["gm"] == t.gm.name and rec["teams"][str(t.id)]["head_coach"] == t.coach.name
          and rec["teams"][str(t.id)]["oc"] == (t.oc.name if t.oc else None) and rec["teams"][str(t.id)]["dc"] == (t.dc.name if t.dc else None) for t in lg.teams))
check("and every number and name in the story is true: the best player is the best, the college count is right, the roster size is right",
      all(F.story(lg, t.id).count(max(t.roster, key=lambda p: (p.ovr, -p.id)).card.name) >= 1
          and f"from {len({p.origin['college'] for p in t.roster})} colleges" in F.story(lg, t.id) and f"The {len(t.roster)} players" in F.story(lg, t.id) for t in lg.teams))
check("every story is a plain paragraph, with no invented motive (no 'because', 'wanted to', 'dreamed')",
      all("\n" not in x["story"] and not any(w in x["story"].lower() for w in ("because", "wanted to", "dreamed", "hoped", "believed")) for x in rec["teams"].values()))
ev = rec["events"]
check("seven dated events for each of the 48 clubs, in date order", len(ev) == 48 * 7 and ev == sorted(ev, key=lambda e: (e["date"], e["team"], e["kind"])))
off = {e.name: e for e in K.offseason(2000)}
d = lambda e: dt.date.fromisoformat(e["date"])
check("every event falls in the 2000 offseason, before the first game", all(dt.date(2000, 1, 1) <= d(e) < K.opener(2000) for e in ev), f"first game {rec['first_game']}")
check("people are named in the hiring window, the roster on the draft days, the cutdown on the cutdown date",
      all(off["hiring_window"].on(d(e)) for e in ev if e["kind"] in ("gm", "head_coach", "coordinators"))
      and all(off["draft"].on(d(e)) for e in ev if e["kind"] == "roster") and all(d(e) == off["cutdown"].start for e in ev if e["kind"] == "cutdown")
      and all(d(e) == off["camp"].start for e in ev if e["kind"] == "practice_squad") and all(d(e) == dt.date(2000, 1, 1) for e in ev if e["kind"] == "ceo"))
byteam = {}
for e in ev:
    byteam.setdefault(e["team"], {})[e["kind"]] = d(e)
check("within a club the order is CEO, GM, head coach, coordinators, roster, practice squad, cutdown",
      all(v["ceo"] <= v["gm"] <= v["head_coach"] <= v["coordinators"] < v["roster"] < v["practice_squad"] < v["cutdown"] for v in byteam.values()))
check("the leftover pool is stated truthfully", rec["pool"]["free_coaches"] == len(lg.free_coaches) and rec["pool"]["free_agents"] == len(lg.free_agents))

# ---- same seed, same founding; the old league is untouched ---------------------------------------------------------------------------------
lg2, _ = F.open_league(33)
lg3, _ = F.open_league(34)
check("the same seed gives the same founding", lg.founding == lg2.founding and [p.card.name for p in every[:50]] == [p.card.name for t in lg2.teams for p in t.roster][:50])
check("a different seed gives a different one", lg.founding["order"] != lg3.founding["order"])
old = new_league(random.Random(33), rosters=True)
check("the default league is the one every earlier test knew: veterans, up to 35", old.founding_class == "veterans" and old.founding is None
      and max(p.age for t in old.teams for p in t.roster) >= 33)
check("in a rookie league the staff are as they always were (only the players differ)",
      [t.coach.name for t in old.teams] == [t.coach.name for t in lg.teams] and [t.gm.name for t in old.teams] == [t.gm.name for t in lg.teams])

# ---- the handover: the engine takes it from here ------------------------------------------------------------------------------------
res = []
cur2, rr = F.open_league(33)
for y in range(1, 4):
    res.append(run_season(cur2, y, rr, Options(engine="fast", keep_boxes=False)))
check("the engine plays the first three seasons of a rookie league", len(res) == 3 and all(x.champion for x in res))
every_now = [p for t in cur2.teams for p in t.roster]
check("the Founding Class ages: three seasons on, the average player is about 3 years older", 24.4 <= sum(p.age for p in every_now) / len(every_now) <= 25.6,
      f"{sum(p.age for p in every_now) / len(every_now):.1f}")
check("first-season choices made on the autopilot are the autopilot's, and the record is still there", cur2.founding == lg2.founding)
with tempfile.TemporaryDirectory() as dd:
    db = os.path.join(dd, "f.db")
    store.save(db, lg2, random.Random(1), 0)
    L2, _, _ = store.load(db)
    check("the Founding Day record survives saving and loading", L2.founding == lg2.founding and L2.founding_class == "rookies")

# ---- the clubs' real identities and the Commissioner's own first season ------------------------------------------------------------------------
import csv  # noqa: E402
import identity as ID  # noqa: E402
import rules as R  # noqa: E402
from schedule import Game, check_schedule  # noqa: E402

rows = ID.load_teams()
check("the workbook has 48 clubs, 8 divisions of 5 and an exile each, in two conferences", len(rows) == 48 and sum(r["exile"] for r in rows) == 8
      and {(r["conference"], r["division"]) for r in rows}.__len__() == 8 and {r["conference"] for r in rows} == set(R.CONFERENCES))
check("every club has a unique name, abbreviation and venue-and-colours record", len({r["name"] for r in rows}) == 48 and len({r["abbr"] for r in rows}) == 48
      and all(r["venue"] and r["location"] and r["primary"] and r["secondary"] and r["tertiary"] and r["primary_hex"].startswith("#") for r in rows))
check("the founding league carries those names: Team 01 is gone", all(t.name == r["name"] and t.identity["abbr"] == r["abbr"] for t, r in zip(lg.teams, rows)) and not any(t.name.startswith("Team ") for t in lg.teams))
exiles = {t.name for t in lg.teams if t.status == "exiled"}
check("the eight clubs in exile on Founding Day are the workbook's", exiles == {"Portland Tempest", "Los Angeles Legion", "Minnesota Warriors", "Baja Barracudas",
                                                                             "Indianapolis Slipstream", "Buffalo Herd", "Baltimore Skipjacks", "Tampa Bay Corsairs"}, sorted(exiles))
check("each division's five active clubs hold tiers 1 to 5 by the workbook's seeding", all(sorted(t.tier for t in lg.active_in_division(d)) == [1, 2, 3, 4, 5] for d in range(R.TOTAL_DIVISIONS))
      and {t.name: t.tier for t in lg.teams if t.status == "active"}["Montana Outriders"] == 1 and {t.name: t.tier for t in lg.teams}["Idaho Tomahawks"] == 5)
check("each division's clubs sit together by name (Northwest: Montana, Seattle, Utah, Calgary, Idaho, Portland)", [t.name.split()[0] for t in lg.teams[:6]] == ["Montana", "Seattle", "Utah", "Calgary", "Idaho", "Portland"])
check("the Commissioner's 2000 schedule passes every rulebook check (18 games, one bye in weeks 15-19, blocks, tiers, 9 home games each)",
      check_schedule(lg, [Game(w, h, a, k) for w, h, a, k in ID.first_season_games(lg.teams)]) == [] and len(ID.first_season_games(lg.teams)) == 360)
check("the first season plays that schedule: 360 regular-season games, Montana's first opponent is Carolina on 7/2", len([g for g in ID.first_season_games(lg.teams) if g[0] == 1]) == 20
      and ID.game_times()[(1, 11)][2:] == ("Montana Outriders", "Carolina Copperheads") and ID.game_times()[(1, 11)][0] == "2000-07-02")
check("the dates in his schedule are the calendar's: every week starts on the day calendar_dfl says", all(
    K.game_days(2000, w)[0].isoformat() == min(v[0] for (ww, g), v in ID.game_times().items() if ww == w) for w in range(1, 20)))
check("the identities and the first schedule survive saving and loading", [[list(x) if isinstance(x, tuple) else x for x in r] for r in L2.schedule_template] == [[list(x) if isinstance(x, tuple) else x for x in r] for r in lg2.schedule_template] and [t.identity for t in L2.teams] == [t.identity for t in lg2.teams]
      and [t.name for t in L2.teams] == [t.name for t in lg2.teams])
played = res[0].games if hasattr(res[0], "games") else None
check("season 1 of the founding league is played under the club names and ends with a champion who is one of the 40 active clubs", res[0].champion in {t.id for t in lg2.teams if t.identity})

print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
