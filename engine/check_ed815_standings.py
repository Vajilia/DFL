"""Focused checks of the isolated Edition 8.15 standings model."""
from __future__ import annotations
import ed815_standings as S


def check_tied_game():
    clubs = {"a":{"conference":"W","division":"N"},"b":{"conference":"W","division":"N"}}
    r = S.build_records(clubs, [{"id":1,"home":"a","away":"b","home_score":10,"away_score":10}])
    assert r["a"].games_played == r["b"].games_played == 1
    assert r["a"].points_for == r["b"].points_for == 10
    assert (r["a"].wins,r["a"].losses,r["a"].win_pct,r["a"].opponents) == (0,0,0.0,[])
    assert S.opponent_pct(r["a"].opponents,r) == 0
    try:
        S.build_records(clubs,[{"id":1,"home":"a","away":"b","home_score":1,"away_score":0},{"id":1,"home":"b","away":"a","home_score":1,"away_score":0}])
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate game accepted")


def check_group_scope():
    clubs = {x:{"conference":("W" if x != "c" else "E"),"division":("N" if x != "b" else "S")} for x in "abc"}
    r = {c:S.Record() for c in clubs}
    r["a"].wins,r["a"].losses = 1,1
    r["b"].wins,r["b"].losses = 1,1
    r["c"].wins,r["c"].losses = 1,1
    r["a"].div_wins = 5
    r["b"].differential = 5
    r["c"].differential = 3
    # Different divisions/conferences: division win difference must be ignored.
    assert S.ranking(["a","b","c"],clubs,r,77,"test")[0] == "b"
    assert S.ranking(["c","a","b"],clubs,r,77,"test") == S.ranking(["a","b","c"],clubs,r,77,"test")


def check_wins_before_percentage():
    clubs={c:{"conference":"W","division":"N"} for c in "ab"}
    r={"a":S.Record(wins=2,losses=10),"b":S.Record(wins=1,losses=0)}
    assert S.ranking("ab",clubs,r,1,"test")[0] == "a"


def check_exile_and_playoffs():
    clubs={}
    ambassadors={}
    for conf in "WE":
        for div in range(4):
            ambassadors[(conf,div)] = f"{conf}{div}-amb"
            for slot in range(5):
                clubs[f"{conf}{div}-{slot}"]={"conference":conf,"division":div}
    records={c:S.Record(wins=18-int(c.rsplit("-",1)[1]),losses=int(c.rsplit("-",1)[1])) for c in clubs}
    ex=S.next_season_division_seeds(clubs,records,ambassadors,5)
    for div,entry in ex.items():
        assert entry["next_seeds"][-1] == ambassadors[div]
        assert entry["next_ambassador"].endswith("-4")
    seeds=S.playoff_seeds(clubs,records,5)
    for conf in "WE":
        assert len(seeds[conf]) == 7 and len(set(seeds[conf])) == 7
        assert all(not c.endswith("-4") for c in seeds[conf])
        assert all(c.endswith("-0") for c in seeds[conf][:4])


if __name__ == "__main__":
    check_tied_game()
    check_group_scope()
    check_wins_before_percentage()
    check_exile_and_playoffs()
    print("Edition 8.15 standings unit checks passed")
