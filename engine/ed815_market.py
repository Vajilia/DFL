"""Edition 8.15 transactional calendar gates, isolated from legacy transactions.

§2 and §12. All datetimes must be timezone-aware UTC (the fixed league civil
clock). This module authorizes *when* finalization may occur, never a trade's
financial or roster legality.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
import ed815_calendar as CAL

UTC = timezone.utc


def _require_utc(moment: datetime) -> None:
    if moment.tzinfo is None or moment.utcoffset() != timedelta(0):
        raise ValueError("DFL transactions require explicit UTC datetimes")


def trade_open(season: int) -> datetime:
    return datetime(CAL.civil_year(season), 2, 1, 0, 0, tzinfo=UTC)


def first_kickoff(season: int) -> datetime:
    sat = CAL.fixture_weekend(season, 1)[0]
    return datetime(sat.year,sat.month,sat.day,17,30,tzinfo=UTC)


def trade_deadline(season: int) -> datetime:
    # The Friday immediately before the first game of numbered fixture week 9.
    sat = CAL.fixture_weekend(season, 9)[0]
    friday = sat - timedelta(days=1)
    return datetime(friday.year,friday.month,friday.day,23,59,tzinfo=UTC)


def may_finalize_trade(season: int, moment: datetime) -> bool:
    _require_utc(moment)
    if moment < trade_open(season) or moment >= trade_deadline(season) + timedelta(minutes=1):
        return False
    if moment < first_kickoff(season):
        return True  # Offseason: trading remains open continuously.
    # In competition: Tuesday 00:01 through Friday 23:59, inclusive.
    weekday = moment.weekday()  # Monday=0
    if weekday == 1:
        return moment.time() >= datetime.min.time().replace(minute=1)
    if weekday in (2,3):
        return True
    if weekday == 4:
        return True
    return False
