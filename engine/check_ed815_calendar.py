"""Edition 8.15 calendar and rotation property checks (pure, no legacy runner)."""
from __future__ import annotations

import ed815_calendar as C


def check_known_2000():
    assert str(C.coronation(1)) == "2000-12-31"
    r = C.season_calendar(1)
    assert len(r) == 27
    assert (str(r[0].saturday), str(r[0].sunday), str(r[0].monday)) == (
        "2000-07-01", "2000-07-02", "2000-07-03")
    assert (r[4].phase, r[10].phase, r[16].phase) == ("break",) * 3
    assert [r.calendar_week for r in r if r.numbered_week is not None] == [
        *range(1,5), *range(6,11), *range(12,17), *range(18,23)]
    assert C.fixture_weekend(1,19)[2].isoformat() == "2000-11-27"
    assert C.postseason_dates(1)["ambassador_bowl"].isoformat() == "2000-12-24"


def check_three_centuries():
    for season in range(1,301):
        cal = C.season_calendar(season)
        dates = C.postseason_dates(season)
        assert dates["coronation"].weekday() == 6
        assert dates["coronation"].month == 12
        assert (C.coronation(season).replace(day=31) - C.coronation(season)).days <= 6
        assert cal[21].monday == dates["last_regular_monday"]
        assert cal[22].sunday == dates["wild_card"]
        assert cal[23].sunday == dates["divisional"]
        assert cal[24].sunday == dates["conference"]
        assert cal[25].sunday == dates["ambassador_bowl"]
        assert cal[26].sunday == dates["coronation"]
        assert len([row for row in cal if row.phase == "break"]) == 3
        assert len([row for row in cal if row.phase == "regular"]) == 19
        rounds = C.tour_round_dates(season)
        assert len(rounds) == 7
        assert all((b[0]-a[0]).days in (21,28) for a,b in zip(rounds,rounds[1:]))
        assert (dates["ambassador_bowl"] - rounds[-1][0]).days >= 14
        assert C.calendar_week_for_fixture(15) == 18


def check_eight_year_rotation():
    initial = C.bed_assignment(1)
    assert list(initial.values()) == list(range(1,9))
    assert C.bed_assignment(9) == initial
    assert C.bed_assignment(5)[("Western","Northwest")] == 5
    assert C.bed_assignment(5)[("Eastern","Midwest")] == 1
    for season in range(1,401):
        current = C.bed_assignment(season)
        following = C.bed_assignment(season+1)
        assert sorted(current.values()) == list(range(1,9))
        assert C.bed_assignment(season+8) == current
        for div,bed in current.items():
            if season % 4 != 0:
                base = 1 if bed <= 4 else 5
                assert following[div] == base + (bed-base+1)%4
            else:
                assert abs(following[div]-bed) == 4


def check_assignments():
    seeded = {div:[f"{i}:{rank}" for rank in range(1,6)]
              for i,div in enumerate(C.DIVISION_ORDER)}
    a = C.assign_bed_ids(1,seeded)
    assert len(a) == len(set(a.values())) == 40
    assert a["0:1"] == "1-1"
    assert C.assign_bed_ids(9,seeded) == a
    assert C.assign_bed_ids(5,seeded)["0:1"] == "5-1"
    try:
        C.assign_bed_ids(1,{**seeded, C.DIVISION_ORDER[0]:["repeat"]*5})
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate club permitted")


if __name__ == "__main__":
    check_known_2000()
    check_three_centuries()
    check_eight_year_rotation()
    check_assignments()
    print("Edition 8.15 calendar: 300 years; rotation: 400 seasons; passed")
