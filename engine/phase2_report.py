"""Write reports/phase2_report.md: sample box score, league stats against football-like targets,
leaders, parity, injuries and the exile target on the roster model.

    python engine/phase2_report.py [--seed 1] [--seasons 10]
"""
import argparse
import collections
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R  # noqa: E402
from boxscore import format_box  # noqa: E402
from calibrate_engine import TARGETS  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def exile_finish(engine, seeds, n, burn=8):
    fin = []
    for sd in seeds:
        rng = random.Random(sd)
        lg = new_league(rng, rosters=True)
        prev = []
        for y in range(1, n + 1):
            r = run_season(lg, y, rng, Options(engine=engine, keep_boxes=False))
            if y > burn:
                for ranks in r.division_ranks.values():
                    fin += [ranks.index(t) + 1 for t in prev if t in ranks]
            prev = r.returners
    c = collections.Counter(fin)
    return st.mean(fin), st.pstdev(fin) / len(fin) ** 0.5, len(fin), {k: c[k] / len(fin) for k in sorted(c)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seasons", type=int, default=10)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    lg = new_league(rng, rosters=True)
    out = []
    out.append("# Phase 2 report: rosters and the drive-by-drive game engine\n")
    out.append(f"Seed {a.seed}, {a.seasons} seasons, drive engine. Player names are placeholders (P00123) until the character "
               "cards exist. Every number here comes from placeholder dials, not from league rules.\n")

    tot = collections.defaultdict(float)
    ngames_team = 0
    pl = collections.defaultdict(lambda: collections.defaultdict(float))
    inj = []
    win_pcts, offlog = [], collections.defaultdict(list)
    margins, home_wins, n_reg, ots = [], 0, 0, 0
    sample_final = None
    sds = []
    for y in range(1, a.seasons + 1):
        res = run_season(lg, y, rng, Options(engine="drives", keep_boxes=(y == 1)))
        rn = res.runner
        if y == 1:
            sample_final = res.playoff_games[-1]
        for tid, tt in rn.team_totals.items():
            for k, v in tt.items():
                tot[k] += v
        for pid, d in rn.player_totals.items():
            for k, v in d.items():
                if k != "pos":
                    pl[pid][k] += v
            pl[pid]["pos"] = d["pos"]
        inj.append(len(rn.injury_log))
        for s in res.stats.values():
            win_pcts.append(s.pct)
        for g in res.games:
            margins.append(g.home_pts - g.away_pts)
            home_wins += g.home_pts > g.away_pts
            n_reg += 1
        for k, v in res.offseason.items():
            offlog[k].append(v)
        sds.append(st.pstdev([t.strength for t in lg.teams]))

    # --- sample box scores (season 1)
    out.append("## Sample box score: the season-1 championship game\n")
    out.append(format_box(sample_final, lg))      # team names never change, so the later league object is fine
    out.append("")

    # --- league stats
    g = tot["games"]
    pg = lambda k: tot[k] / g
    stats = {
        "points": tot["pf"] / g,
        "plays": pg("plays"),
        "pass_att": pg("pass_att"),
        "completion_pct": 100 * tot["pass_cmp"] / tot["pass_att"],
        "yards_per_attempt": tot["pass_yds"] / tot["pass_att"],
        "rush_att": pg("rush_att"),
        "yards_per_carry": tot["rush_yds"] / tot["rush_att"],
        "total_yards": pg("yards"),
        "sacks_taken": pg("sacks"),
        "punts": pg("punts"),
        "first_downs": pg("first_downs"),
        "third_down_pct": 100 * tot["third_conv"] / tot["third_att"],
        "fg_attempts": pg("fga"),
        "fg_pct": 100 * tot["fgm"] / max(1, tot["fga"]),
        "drives": pg("drives"),
        "time_of_possession_min": pg("top_secs") / 60,
        "game_margin_sd": st.pstdev(margins),
        "home_win_pct": 100 * home_wins / n_reg,
    }
    out.append(f"## League stats over {a.seasons} seasons ({int(g)} team-games, regular season, Ambassador and playoffs)\n")
    out.append("| Measure (per team per game unless noted) | This league | Football-like target | Within range? |")
    out.append("| --- | --- | --- | --- |")
    for k, v in stats.items():
        t, tol = TARGETS[k]
        out.append(f"| {k.replace('_', ' ')} | {v:.2f} | {t:.2f} (+/- {tol}) | {'yes' if abs(v - t) <= tol else 'NO'} |")
    out.append("")
    out.append("Targets are rough NFL-style figures chosen by the AI as a stand-in for \"looks like football\". They are not "
               "rules and not your decisions.\n")

    # --- leaders
    def leaders(title, key, pos, n=5, minimum=0, fmt=lambda d: ""):
        rows = [(pid, d) for pid, d in pl.items() if d["pos"] == pos and d.get(key, 0) > minimum]
        rows.sort(key=lambda x: -x[1][key])
        out.append(f"**{title}** (all {a.seasons} seasons combined, per player id)")
        out.append("")
        for pid, d in rows[:n]:
            out.append(f"- P{pid:05d} ({pos}): {int(d[key])}  {fmt(d)}")
        out.append("")

    out.append("## Career leaders in the simulated seasons\n")
    leaders("Passing yards", "pass_yds", "QB", fmt=lambda d: f"({int(d['pass_td'])} TD, {int(d['pass_int'])} INT, {int(d['games'])} games)")
    leaders("Rushing yards", "rush_yds", "RB", fmt=lambda d: f"({int(d['rush_att'])} carries, {d['rush_yds'] / d['rush_att']:.1f} avg)")
    leaders("Receiving yards", "rec_yds", "WR", fmt=lambda d: f"({int(d['rec'])} catches, {int(d['rec_td'])} TD)")
    leaders("Sacks", "sacks", "DL")
    leaders("Interceptions", "ints", "CB")

    # --- parity and injuries
    wp = sorted(win_pcts)
    out.append("## Parity\n")
    out.append(f"- Team strength spread (standard deviation of team power ratings, points): {st.mean(sds):.1f} on average "
               f"(range {min(sds):.1f} to {max(sds):.1f}).")
    out.append(f"- Regular-season win percentage of the 40 active teams: sd {st.pstdev(win_pcts):.3f}; "
               f"best 5% about {wp[int(.95 * len(wp))]:.3f}, worst 5% about {wp[int(.05 * len(wp))]:.3f}.")
    out.append("")
    out.append("## Injuries\n")
    out.append(f"- About {st.mean(inj):.0f} injuries per season league-wide, roughly {st.mean(inj) / 48:.1f} per team. "
               "Rates and lengths are placeholder dials in injuries.py.\n")
    out.append("## Roster offseason (per year, whole league)\n")
    out.append("| Retirements | Contracts ended | Free-agent signings | Premium (exile relief) signings | Rookies drafted | Street free agents needed |")
    out.append("| --- | --- | --- | --- | --- | --- |")
    out.append("| " + " | ".join(f"{st.mean(offlog[k]):.0f}" if k != "premium" else f"{st.mean(offlog[k]):.1f}"
                                 for k in ("retired", "expired", "signed", "premium", "rookies", "street")) + " |")
    out.append("")

    # --- exile target
    out.append("## Exile target on the roster model\n")
    out.append("Where a team that has just come back from exile finishes in its division. Your target: it should have the "
               "potential to compete for about 3rd, sometimes succeeding and sometimes not. A league-average team finishes "
               "3.0 on average, so about 3.0 to 3.3 hits the target.\n")
    out.append("| Engine | Leagues x seasons | Average finish | 1st | 2nd | 3rd | 4th | 5th (exiled again) |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for eng, seeds, n in (("fast", range(10, 18), 40), ("drives", range(20, 24), 40)):
        m, se, cnt, dist = exile_finish(eng, seeds, n)
        out.append(f"| {eng} | {len(seeds)} x {n} | {m:.2f} (+/- {1.96 * se:.2f}) | "
                   + " | ".join(f"{100 * dist.get(k, 0):.0f}%" for k in range(1, 6)) + " |")
    out.append("")
    out.append("`fast` decides a game from the two teams' power ratings; `drives` plays the whole game. They agree, which is "
               "the point of the fast mode: long studies can use it.\n")

    path = os.path.join(ROOT, "reports", "phase2_report.md")
    with open(path, "w") as f:
        f.write("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    main()
