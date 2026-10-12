"""The play log (2026-10-12): recording plays changes nothing, and replaying the log gives back the box score the engine kept.

    python engine/check_playlog.py
"""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_engine import simulate_game
from league import new_league
from lineup import build_lineup
from season import Options, run_season

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def replay(res):
    """Rebuild every player's stat line and each team's yards from the play log alone."""
    st, tm = {}, [dict(plays=0, yards=0, pass_yds=0, rush_yds=0, turnovers=0), dict(plays=0, yards=0, pass_yds=0, rush_yds=0, turnovers=0)]
    def bump(pid, k, n=1):
        d = st.setdefault(pid, {}); d[k] = d.get(k, 0) + n
    for (off, q, down, to_go, pos, yds, to, kind, a, b, c, q2, t2, ot, di) in res.plays:
        if kind in ("PC", "PI", "IN"):
            bump(a, "pass_att"); bump(b, "targets")
        if kind == "PC":
            bump(a, "pass_cmp"); bump(a, "pass_yds", yds); bump(b, "rec"); bump(b, "rec_yds", yds); bump(c, "tackles")
            tm[off]["pass_yds"] += yds
            if pos + yds >= 100: bump(a, "pass_td"); bump(b, "rec_td")
        elif kind == "IN":
            bump(a, "pass_int"); bump(c, "ints")
        elif kind == "SK":
            bump(a, "sacked"); bump(a, "sack_yds", -yds); bump(b, "sacks")
        elif kind == "RU":
            bump(a, "rush_att"); bump(a, "rush_yds", yds); bump(b, "tackles")
            tm[off]["rush_yds"] += yds
            if pos + yds >= 100: bump(a, "rush_td")
        elif kind == "FG":
            bump(a, "fga"); bump(a, "fgm", b)
        elif kind == "PU":
            bump(a, "punts")
        if kind in ("PC", "PI", "IN", "SK", "RU"):
            tm[off]["plays"] += 1
            if to != "INT": tm[off]["yards"] += yds
            if to: tm[off]["turnovers"] += 1
    return st, tm


rng = random.Random(5)
lg = new_league(rng, rosters=True)
teams = [t for t in lg.teams if t.status == "active"]
lus = [build_lineup(t.id, t.roster) for t in teams[:12]]
N = bad_same = bad_stats = bad_team = bad_clock = bad_drive = 0
kinds = set()
for i in range(len(lus)):
    for j in range(len(lus)):
        if i == j or (i + j) % 3:
            continue
        N += 1
        a, b = simulate_game(lus[i], lus[j], random.Random(N)), simulate_game(lus[i], lus[j], random.Random(N), record_plays=True)
        if a.score != b.score or a.drives != b.drives or a.players != b.players or a.team != b.team:
            bad_same += 1
        st, tm = replay(b)
        for pid, d in b.players.items():
            for k, v in st.get(pid, {}).items():
                if k in ("tackles",) and v != d.get(k, 0):
                    bad_stats += 1
                elif k != "tackles" and v != d.get(k, 0):
                    bad_stats += 1
            for k in ("pass_att", "pass_cmp", "pass_yds", "rush_att", "rush_yds", "rec", "rec_yds", "sacks", "ints", "fga", "fgm", "punts"):
                if d.get(k, 0) != st.get(pid, {}).get(k, 0):
                    bad_stats += 1
        for s in (0, 1):
            for k in ("plays", "yards", "pass_yds", "rush_yds", "turnovers"):
                if tm[s][k] != b.team[s][k]:
                    bad_team += 1
        ts = [(p[11], p[12], p[13]) for p in b.plays]
        for x, y in zip(ts, ts[1:]):
            if x[2] == y[2] and (y[0], -y[1]) < (x[0], -x[1]):
                bad_clock += 1
        if b.plays and (b.plays[-1][14] + 1 < len(b.drives) - 2 or max(p[14] for p in b.plays) >= len(b.drives)):
            bad_drive += 1
        kinds |= {p[7] for p in b.plays}
check("recording the plays changes nothing: same score, drives, player lines and team totals", bad_same == 0, f"{bad_same} of {N}")
check("replaying the play log gives every player's stat line back (passing, rushing, receiving, tackles, sacks, picks, kicks)", bad_stats == 0, f"{bad_stats} mismatches in {N} games")
check("replaying the play log gives each team's plays, yards and turnovers back", bad_team == 0, f"{bad_team}")
check("the clock never runs backward inside a stretch of play", bad_clock == 0, f"{bad_clock}")
check("every play points at a real drive of its game", bad_drive == 0, f"{bad_drive}")
check("all seven kinds of play appear", kinds == {"PC", "PI", "IN", "SK", "RU", "FG", "PU"}, str(sorted(kinds)))
print("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}")
sys.exit(1 if failures else 0)
