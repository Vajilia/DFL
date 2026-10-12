"""Checks for the DFL calendar (calendar_dfl.py): the Commissioner's 2000 schedule reproduced date for date, and the rules that carry it to every other year.

    python engine/check_calendar.py
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calendar_dfl as K  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


D = dt.date
# the Commissioner's 2000 schedule: the Saturday of each of the 19 weeks, the playoffs and the Coronation
SAT = {1: D(2000, 7, 1), 2: D(2000, 7, 8), 3: D(2000, 7, 15), 4: D(2000, 7, 22), 5: D(2000, 8, 5), 6: D(2000, 8, 12), 7: D(2000, 8, 19), 8: D(2000, 8, 26),
       9: D(2000, 9, 2), 10: D(2000, 9, 16), 11: D(2000, 9, 23), 12: D(2000, 9, 30), 13: D(2000, 10, 7), 14: D(2000, 10, 14), 15: D(2000, 10, 28),
       16: D(2000, 11, 4), 17: D(2000, 11, 11), 18: D(2000, 11, 18), 19: D(2000, 11, 25)}
check("league year 1 is 2000", K.calendar_year(1) == 2000 and K.league_year(2000) == 1)
check("the 2000 Coronation is Sunday 31 December", K.coronation(2000) == D(2000, 12, 31) and K.coronation(2000).weekday() == 6)
check("the 2000 opener is Saturday 1 July", K.opener(2000) == D(2000, 7, 1))
check("every one of the 19 weeks of 2000 begins on the Commissioner's date", all(K.week_saturday(2000, w) == d for w, d in SAT.items()),
      [w for w, d in SAT.items() if K.week_saturday(2000, w) != d])
check("the last game of 2000 is Monday 27 November", K.game_days(2000, 19)[2] == D(2000, 11, 27))
p = K.playoffs(2000)
check("the 2000 playoffs are 3, 10 and 17 December and the Coronation 31 December",
      (p["wild_card"], p["divisional"], p["conference"], p["coronation"]) == (D(2000, 12, 3), D(2000, 12, 10), D(2000, 12, 17), D(2000, 12, 31)))
check("the 2000 offseason is 1 January to 30 June: 182 days", K.offseason_days(2000) == 182)

# every other year
bad = {k: [] for k in ("sun", "dec", "sat", "jun", "len", "week", "gap", "bye", "deadline", "order", "inside", "day")}
for cy in range(2000, 2300):
    c, o = K.coronation(cy), K.opener(cy)
    if c.weekday() != 6: bad["sun"].append(cy)
    if not (D(cy, 12, 25) <= c <= D(cy, 12, 31)): bad["dec"].append(cy)
    if o.weekday() != 5: bad["sat"].append(cy)
    if not (D(cy, 6, 25) <= o <= D(cy, 7, 1)): bad["jun"].append(cy)
    if not 175 <= K.offseason_days(cy) <= 182: bad["len"].append(cy)
    sats = [K.week_saturday(cy, w) for w in range(1, 20)]
    if any((b - a).days not in (7, 14) for a, b in zip(sats, sats[1:])) or sats[0] != o: bad["week"].append(cy)
    if [w for w in range(1, 19) if (sats[w] - sats[w - 1]).days == 14] != list(K.BYES_AFTER): bad["bye"].append(cy)
    pp = K.playoffs(cy)
    if not (K.game_days(cy, 19)[2] < pp["wild_card"] and (pp["divisional"] - pp["wild_card"]).days == 7 and (pp["conference"] - pp["divisional"]).days == 7
            and (pp["coronation"] - pp["conference"]).days == 14): bad["gap"].append(cy)
    td = K.trade_deadline(cy)
    if not (td.weekday() == 1 and K.game_days(cy, 9)[2] < td < K.week_saturday(cy, 10) and K.phase_on(td) == "bye"): bad["deadline"].append(cy)
    ev = K.offseason(cy)
    if any(a.start > b.start for a, b in zip(ev, ev[1:])): bad["order"].append(cy)
    if not all(D(cy, 1, 1) <= e.start <= e.end < o for e in ev): bad["inside"].append(cy)
    byname = {e.name: e for e in ev}
    if not (byname["draft"].start.weekday() == 3 and byname["draft"].start.month == 4 and byname["cutdown"].start.weekday() == 1 and byname["camp"].start.weekday() == 5):
        bad["day"].append(cy)
for label, key in (("the Coronation is always a Sunday", "sun"), ("and always the last Sunday of December", "dec"), ("the opener is always a Saturday", "sat"),
                   ("and falls between 25 June and 1 July", "jun"), ("the offseason is always 175 to 182 days", "len"),
                   ("weeks run from the opener a week apart, a fortnight across each league-wide bye", "week"), ("the byes come after weeks 4, 9 and 14", "bye"),
                   ("the playoffs follow the last game, a week apart, and the Coronation two weeks after the conference championships", "gap"),
                   ("the trade deadline is a Tuesday inside the Week 9 bye", "deadline"), ("offseason events are in order", "order"),
                   ("and all inside 1 January to the day before the first game", "inside"), ("the draft is a Thursday in April, the cutdown a Tuesday", "day")):
    check(label + " (300 years)", not bad[key], bad[key][:5])
check("the 2000 trade deadline is Tuesday 5 September", K.trade_deadline(2000) == D(2000, 9, 5))
check("the 2000 draft begins Thursday 27 April", K.event_date(2000, "draft") == D(2000, 4, 27))
check("the opener is the day after the offseason ends", K.phase_on(D(2000, 6, 30)) == "offseason" and K.phase_on(D(2000, 7, 1)) == "season"
      and K.phase_on(D(2000, 7, 25)) == "bye" and K.phase_on(D(2000, 8, 5)) == "season")
check("dates print the way the Commissioner's schedule does", K.fmt(D(2000, 7, 1)) == "7/1/00")
openers = {K.opener(cy).day for cy in range(2000, 2300) if K.opener(cy).month == 6}
check("most years open in the last week of June", len([cy for cy in range(2000, 2300) if K.opener(cy).month == 6]) > 240, f"June days seen: {sorted(openers)}")

print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
