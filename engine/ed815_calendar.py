"""Edition 8.15 calendar and seed-bed rotation.

Pure reference mechanics. Does not invoke the old game engine or rewrite live time.
Design authority: pinned Edition 8.15 §§0, 2–3, 7, 18.
All datetimes are naive dates on the fixed UTC civil calendar, not local zones.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

FIRST_YEAR = 2000
NUMBERED_WEEKS = 19
CALENDAR_WEEKS = 27
BREAK_AFTER = (4, 9, 14)
BYE_WEEKS = (15, 16, 17, 18, 19)
BYE_SEED_BY_WEEK = {15: 3, 16: 1, 17: 2, 18: 5, 19: 4}
TOUR_CALENDAR_WEEKS = (1, 4, 8, 11, 15, 18, 22)
SATURDAY_KICKOFF = "17:30"
SUNDAY_KICKOFFS = ("10:00", "13:00", "17:30")
MONDAY_KICKOFF = "17:30"
DIVISION_ORDER = (
    ("Western", "Northwest"), ("Western", "Southwest"),
    ("Western", "Central"), ("Western", "Southern"),
    ("Eastern", "Midwest"), ("Eastern", "Northeast"),
    ("Eastern", "East"), ("Eastern", "Southeast"),
)


def civil_year(season: int) -> int:
    if season < 1:
        raise ValueError("season must be positive")
    return FIRST_YEAR + season - 1


def coronation(season: int) -> date:
    dec31 = date(civil_year(season), 12, 31)
    return dec31 - timedelta(days=(dec31.weekday() + 1) % 7)


def calendar_week_for_fixture(week: int) -> int:
    if week not in range(1, NUMBERED_WEEKS + 1):
        raise ValueError("numbered fixture week must be 1..19")
    return week + sum(week > end for end in BREAK_AFTER)


def saturday_of_calendar_week(season: int, calendar_week: int) -> date:
    if calendar_week not in range(1, CALENDAR_WEEKS + 1):
        raise ValueError("calendar week must be 1..27")
    # Numbered week 19 is calendar week 22, whose Monday is C-34.
    first_saturday = coronation(season) - timedelta(days=183)
    return first_saturday + timedelta(weeks=calendar_week - 1)


def fixture_weekend(season: int, week: int) -> tuple[date, date, date]:
    saturday = saturday_of_calendar_week(season, calendar_week_for_fixture(week))
    return saturday, saturday + timedelta(days=1), saturday + timedelta(days=2)


def phase_for_calendar_week(week: int) -> str:
    if week not in range(1, CALENDAR_WEEKS + 1):
        raise ValueError("calendar week must be 1..27")
    if week in (5, 11, 17):
        return "break"
    if week <= 22:
        return "regular"
    return {23: "wild_card", 24: "divisional", 25: "conference",
            26: "ambassador_bowl", 27: "coronation"}[week]


def postseason_dates(season: int) -> dict[str, date]:
    c = coronation(season)
    return {"last_regular_monday": c - timedelta(days=34),
            "wild_card": c - timedelta(days=28),
            "divisional": c - timedelta(days=21),
            "conference": c - timedelta(days=14),
            "ambassador_bowl": c - timedelta(days=7),
            "coronation": c}


def tour_round_dates(season: int) -> list[tuple[date, date, date]]:
    return [(
        saturday_of_calendar_week(season, week),
        saturday_of_calendar_week(season, week) + timedelta(days=1),
        saturday_of_calendar_week(season, week) + timedelta(days=2),
    ) for week in TOUR_CALENDAR_WEEKS]


def bed_assignment(season: int) -> dict[tuple[str, str], int]:
    """Section 3 formula: rotate four beds yearly, flip blocks after four years."""
    if season < 1:
        raise ValueError("season must be positive")
    k = (season - 1) % 4
    p = ((season - 1) // 4) % 2
    result = {}
    for i, div in enumerate(DIVISION_ORDER):
        conf_offset = 4 * p if div[0] == "Western" else 4 * (1 - p)
        result[div] = 1 + conf_offset + (i % 4 + k) % 4
    return result


def assign_bed_ids(season: int, seeded_divisions: dict) -> dict:
    """Map 5 ordered active club IDs per division to this season's bed-rank IDs.

    Separate from the source schedule's immutable bed-pairing template.
    """
    assignments = bed_assignment(season)
    if set(seeded_divisions) != set(assignments):
        raise ValueError("expected exactly the eight canonical divisions")
    result = {}
    for division, bed in assignments.items():
        clubs = seeded_divisions[division]
        if len(clubs) != 5 or len(set(clubs)) != 5:
            raise ValueError("each division needs five unique active club IDs")
        for rank, club in enumerate(clubs, 1):
            if club in result:
                raise ValueError("club appears in multiple divisions")
            result[club] = f"{bed}-{rank}"
    if len(result) != 40:
        raise AssertionError("expected 40 active clubs")
    return result


@dataclass(frozen=True)
class CalendarRow:
    calendar_week: int
    phase: str
    numbered_week: int | None
    saturday: date
    sunday: date
    monday: date


def season_calendar(season: int) -> list[CalendarRow]:
    numbered = {calendar_week_for_fixture(w): w for w in range(1, 20)}
    rows = []
    for cweek in range(1, 28):
        sat = saturday_of_calendar_week(season, cweek)
        rows.append(CalendarRow(cweek, phase_for_calendar_week(cweek),
                                numbered.get(cweek), sat, sat + timedelta(days=1),
                                sat + timedelta(days=2)))
    return rows


def fixtures_for_season(season: int, seeded_divisions: dict,
                        template_path=None) -> list[dict]:
    """Fill Edition 8.15's immutable Season 1 bed pairings from current seeds.

    Returns 360 fixture dicts (week, game, ISO date, kickoff, away, home).
    The builder cannot independently modify opponents or home/away allocation.
    """
    import csv
    from pathlib import Path

    path = (Path(template_path) if template_path is not None
            else Path(__file__).resolve().parents[1] / "data" / "ed815_fixture_beds.csv")
    mapping = assign_bed_ids(season, seeded_divisions)
    by_bed = {bed: cid for cid, bed in mapping.items()}
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            week = int(raw["week"])
            game = int(raw["game"])
            offset = int(raw["day_offset"])
            if offset not in (0, 1, 2):
                raise ValueError("invalid fixture weekday offset")
            if raw["away_bed"] not in by_bed or raw["home_bed"] not in by_bed:
                raise ValueError("unknown seed bed in immutable fixture")
            if raw["away_bed"] == raw["home_bed"]:
                raise ValueError("self-fixture")
            saturday = fixture_weekend(season, week)[0]
            rows.append({"week": week, "game": game,
                         "date": (saturday + timedelta(days=offset)).isoformat(),
                         "kickoff": raw["kickoff"],
                         "away": by_bed[raw["away_bed"]],
                         "home": by_bed[raw["home_bed"]]})
    if len(rows) != 360 or len({(r["week"], r["game"]) for r in rows}) != 360:
        raise ValueError("fixture template must contain exactly 360 unique slots")
    rows.sort(key=lambda x: (x["week"], x["game"]))
    return rows


def validate_fixture_counts(fixtures: list[dict], seeded_divisions: dict) -> None:
    """Cheap independent structural gate; semantic opponent checks are next."""
    from collections import Counter

    active = {club for ids in seeded_divisions.values() for club in ids}
    games = Counter()
    home = Counter()
    away = Counter()
    by_week = Counter()
    for fixture in fixtures:
        h, a = fixture["home"], fixture["away"]
        if h == a or h not in active or a not in active:
            raise ValueError("invalid club pairing")
        games[h] += 1
        games[a] += 1
        home[h] += 1
        away[a] += 1
        by_week[fixture["week"]] += 1
    if len(fixtures) != 360 or len(active) != 40:
        raise ValueError("wrong league shape")
    if any(games[club] != 18 or home[club] != 9 or away[club] != 9 for club in active):
        raise ValueError("a club lacks 18 games or 9H/9A")
    if any(by_week[w] != (20 if w <= 14 else 16) for w in range(1, 20)):
        raise ValueError("fixture-week game count differs from Edition 8.15")
