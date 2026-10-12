"""The DFL's calendar (the Commissioner, 2026-10-11 and 12).

Founding Day is 1 January 2000. Every season begins on 1 January: league year n is calendar year 1999 + n, so league year 1 is 2000. The offseason runs from
1 January to the day before the first game. The season is worked out BACKWARDS from the Diamond Coronation, which is played on the last Sunday of the
calendar year (25 to 31 December):

    first game   a Saturday, 183 days before the Coronation (so 25 June to 1 July: the offseason is 175 to 182 days)
    weeks        Saturday night, Sunday, Monday night; 19 weeks, and a league-wide bye after weeks 4, 9 and 14 (one skipped week each)
    playoffs     wild card, divisional, conference championships on the three Sundays after the final Monday; then a two-week gap, then the Coronation

Checked against the Commissioner's 2000 schedule (every date in it). Everything else here is dated by analogy with the NFL and labelled so: the rule basis is
NFL where the NFL has a date, Adapted where the DFL's own shape forces a change, Model where it is only a placeholder. The Director (the alarm clock) reads
this module; no engine rule does yet, so the league on the autopilot is unchanged.

Known differences from the NFL, recorded rather than hidden:
  * staff reviews are on 2 January (the Commissioner's rule: every offseason task falls between 1 January and the day before the first game); the NFL
    fires coaches the day after the regular season, which here would be late November;
  * the engine settles free agency after the draft; the NFL opens it in March, before the draft. The dates below are the NFL's; the order of processing
    is the engine's (rulebook row `calendar`).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import List, Optional

BASE = 1999                          # league year n is calendar year BASE + n
REGULAR_WEEKS = 19                   # 18 games and a bye for each club
BYES_AFTER = (4, 9, 14)              # a league-wide bye after these weeks
OPENER_BEFORE_CORONATION = 183       # days
CAMP_BEFORE_OPENER = 42              # training camp opens this many days before the first game (NFL: about six weeks)
CUTDOWN_BEFORE_OPENER = 11           # the Tuesday cutdown to 53 (NFL: the Tuesday about nine days before the opener)
TRADE_DEADLINE_AFTER_WEEK = 9        # the Tuesday after this week's last game (NFL 2024 and 2025: the Tuesday after Week 9 of 18)


def calendar_year(league_year: int) -> int:
    return BASE + league_year


def league_year(cal_year: int) -> int:
    return cal_year - BASE


def coronation(cal_year: int) -> dt.date:
    """The last Sunday of December."""
    d = dt.date(cal_year, 12, 31)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)          # Monday is 0, Sunday is 6


def opener(cal_year: int) -> dt.date:
    """The first game: the Saturday 183 days before the Coronation."""
    return coronation(cal_year) - dt.timedelta(days=OPENER_BEFORE_CORONATION)


def week_saturday(cal_year: int, week: int) -> dt.date:
    """The Saturday on which a regular-season week begins (its Saturday-night game); league-wide byes skip a week."""
    skipped = sum(1 for b in BYES_AFTER if week > b)
    return opener(cal_year) + dt.timedelta(days=7 * (week - 1 + skipped))


def game_days(cal_year: int, week: int) -> tuple:
    s = week_saturday(cal_year, week)
    return s, s + dt.timedelta(days=1), s + dt.timedelta(days=2)       # Saturday night, Sunday, Monday night


def playoffs(cal_year: int) -> dict:
    last = week_saturday(cal_year, REGULAR_WEEKS) + dt.timedelta(days=8)      # the Sunday after the final Monday
    return dict(wild_card=last, divisional=last + dt.timedelta(days=7), conference=last + dt.timedelta(days=14), coronation=coronation(cal_year))


def season_end(cal_year: int) -> dt.date:
    return coronation(cal_year)


def trade_deadline(cal_year: int) -> dt.date:
    """The Tuesday after the last game of Week 9: inside the league-wide bye that follows it."""
    return week_saturday(cal_year, TRADE_DEADLINE_AFTER_WEEK) + dt.timedelta(days=3)


def _nth_weekday(cal_year: int, month: int, weekday: int, n: int) -> dt.date:
    d = dt.date(cal_year, month, 1)
    d += dt.timedelta(days=(weekday - d.weekday()) % 7)
    return d + dt.timedelta(days=7 * (n - 1))


@dataclass(frozen=True)
class Event:
    name: str
    start: dt.date
    end: dt.date
    basis: str            # NFL | Adapted | Model
    note: str = ""

    def on(self, d: dt.date) -> bool:
        return self.start <= d <= self.end


def offseason(cal_year: int) -> List[Event]:
    """Every dated offseason event of the calendar year, in order. The offseason is 1 January to the day before the first game."""
    y = cal_year
    o = opener(y)
    D = dt.date
    draft = _nth_weekday(y, 4, 3, 4)                                      # the fourth Thursday of April
    ev = [
        Event("rollover", D(y, 1, 1), D(y, 1, 1), "Adapted", "the year turns; contracts and ages run on; retirements"),
        Event("staff_reviews", D(y, 1, 2), D(y, 1, 2), "Adapted", "each CEO decides whether to keep her head coach and GM"),
        Event("hiring_window", D(y, 1, 3), D(y, 2, 14), "NFL", "interviews (two interviews before an offer), head coach and GM searches, coordinator hires"),
        Event("tag_window", D(y, 2, 25), D(y, 3, 4), "NFL", "franchise and transition tags"),
        Event("negotiating_window", D(y, 3, 10), D(y, 3, 11), "NFL", "clubs may talk to other clubs' free agents (the NFL's legal tampering window)"),
        Event("free_agency", D(y, 3, 12), o - dt.timedelta(days=1), "NFL", "the new league year: free agency opens, trades take effect"),
        Event("restricted_market", D(y, 3, 12), D(y, 4, 22), "NFL", "offer sheets, five days to match"),
        Event("draft", draft, draft + dt.timedelta(days=2), "NFL", "round 1 Thursday, rounds 2 and 3 Friday, rounds 4 to 7 Saturday"),
        Event("undrafted_signings", draft + dt.timedelta(days=2), draft + dt.timedelta(days=3), "NFL", "undrafted rookies sign"),
        Event("camp", o - dt.timedelta(days=CAMP_BEFORE_OPENER), o - dt.timedelta(days=CUTDOWN_BEFORE_OPENER + 1), "NFL", "training camp"),
        Event("cutdown", o - dt.timedelta(days=CUTDOWN_BEFORE_OPENER), o - dt.timedelta(days=CUTDOWN_BEFORE_OPENER), "NFL", "rosters cut to 53"),
        Event("practice_squad", o - dt.timedelta(days=CUTDOWN_BEFORE_OPENER - 1), o - dt.timedelta(days=CUTDOWN_BEFORE_OPENER - 2), "NFL", "waivers, then practice squads"),
    ]
    return sorted(ev, key=lambda e: (e.start, e.end))


def in_season(cal_year: int) -> List[Event]:
    """The dated events from the first game to the Coronation."""
    y = cal_year
    ev = [Event("trade_deadline", trade_deadline(y), trade_deadline(y), "NFL", "the Tuesday after Week 9, in the league-wide bye; no trades until the new league year")]
    for b in BYES_AFTER:
        s = week_saturday(y, b) + dt.timedelta(days=3)
        ev.append(Event(f"bye_after_week_{b}", s, s + dt.timedelta(days=10), "Adapted", "league-wide bye"))
    p = playoffs(y)
    ev += [Event("wild_card", p["wild_card"], p["wild_card"], "NFL"), Event("divisional", p["divisional"], p["divisional"], "NFL"),
           Event("conference_championships", p["conference"], p["conference"], "NFL"), Event("coronation", p["coronation"], p["coronation"], "Adapted", "the Diamond Coronation")]
    return sorted(ev, key=lambda e: (e.start, e.end))


def offseason_days(cal_year: int) -> int:
    return (opener(cal_year) - dt.date(cal_year, 1, 1)).days


def phase_on(d: dt.date) -> str:
    """"offseason", "season" or "bye" for a date."""
    y = d.year
    if d < opener(y):
        return "offseason"
    for b in BYES_AFTER:
        s = week_saturday(y, b) + dt.timedelta(days=3)
        if s <= d <= s + dt.timedelta(days=10):
            return "bye"
    return "season"


def fmt(d: dt.date) -> str:
    return f"{d.month}/{d.day}/{d.year % 100:02d}"


def event_date(cal_year: int, name: str) -> Optional[dt.date]:
    for e in offseason(cal_year) + in_season(cal_year):
        if e.name == name:
            return e.start
    return None
