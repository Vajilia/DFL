"""Turn a played game into a readable box score (markdown).

    from boxscore import format_box
    print(format_box(game, league))

Players are named by their character cards (P00123 only if a card is missing).
"""
from __future__ import annotations

import math


def _clock(secs: float) -> str:
    s = int(round(secs))
    return f"{s // 60}:{s % 60:02d}"


def _lines(res, side, pid_pos, names=None):
    rows = {"pass": [], "rush": [], "rec": [], "def": [], "kick": []}
    for pid, d in sorted(res.players.items()):
        if d["team"] != side:
            continue
        nm = (names or {}).get(pid) or f"P{pid:05d}"
        if d.get("pass_att"):
            rows["pass"].append(f"{nm} ({d['pos']}) {d.get('pass_cmp', 0)}/{d['pass_att']}, {d.get('pass_yds', 0)} yds, "
                                f"{d.get('pass_td', 0)} TD, {d.get('pass_int', 0)} INT, sacked {d.get('sacked', 0)}")
        if d.get("rush_att"):
            ypc = d.get("rush_yds", 0) / d["rush_att"]
            rows["rush"].append(f"{nm} ({d['pos']}) {d['rush_att']} car, {d.get('rush_yds', 0)} yds ({ypc:.1f}), "
                                f"{d.get('rush_td', 0)} TD")
        if d.get("targets"):
            rows["rec"].append(f"{nm} ({d['pos']}) {d.get('rec', 0)} rec on {d['targets']} tgt, {d.get('rec_yds', 0)} yds, "
                               f"{d.get('rec_td', 0)} TD")
        if d.get("tackles") or d.get("sacks") or d.get("ints"):
            rows["def"].append(f"{nm} ({d['pos']}) {d.get('tackles', 0)} tkl, {d.get('sacks', 0)} sack, {d.get('ints', 0)} INT")
        if d.get("fga"):
            rows["kick"].append(f"{nm} (K) FG {d.get('fgm', 0)}/{d['fga']}")
        if d.get("punts"):
            rows["kick"].append(f"{nm} (P) {d['punts']} punts, {d.get('punt_yds', 0) / d['punts']:.1f} avg")
    return rows


def format_box(game, league, drive_log: bool = True) -> str:
    res = game.result
    if res is None:
        return f"{game.home} {game.home_pts} - {game.away} {game.away_pts} (no box score kept)"
    pname = {p.id: p.name for p in [q for t in league.teams for q in t.roster] + list(league.free_agents)
             + list(getattr(league, "retired_players", ()))}
    h, a = league.by_id[game.home].name, league.by_id[game.away].name
    names = (h, a)
    L = []
    ot = f" (OT{res.ot_periods if res.ot_periods > 1 else ''})" if res.ot_periods else ""
    L.append(f"### {a} at {h}  -  week {game.week}, {game.kind.replace('_', ' ')}")
    L.append(f"**Final: {a} {res.score[1]}, {h} {res.score[0]}{ot}**")
    L.append("")
    L.append(f"| | {h} (home) | {a} (away) |")
    L.append("|---|---|---|")
    t0, t1 = res.team
    def row(label, f):
        L.append(f"| {label} | {f(t0)} | {f(t1)} |")
    row("Total yards", lambda t: t["yards"])
    row("Plays", lambda t: t["plays"])
    row("Passing", lambda t: f"{t['pass_cmp']}/{t['pass_att']}, {t['pass_yds']} yds")
    row("Rushing", lambda t: f"{t['rush_att']} car, {t['rush_yds']} yds")
    row("First downs", lambda t: t["first_downs"])
    row("3rd down", lambda t: f"{t['third_conv']}/{t['third_att']}")
    row("Turnovers", lambda t: t["turnovers"])
    row("Sacks by defense", lambda t: t["sacks"])
    row("Punts", lambda t: t["punts"])
    row("Time of possession", lambda t: _clock(t["top_secs"]))
    L.append("")
    for side in (0, 1):
        rows = _lines(res, side, None, pname)
        L.append(f"**{names[side]}**")
        for key, title in (("pass", "Passing"), ("rush", "Rushing"), ("rec", "Receiving"), ("kick", "Kicking"),
                           ("def", "Defense")):
            if rows[key]:
                L.append(f"- {title}: " + "; ".join(rows[key]))
        L.append("")
    if drive_log:
        L.append("**Drive log**")
        L.append("")
        L.append("| # | Team | Qtr | Start | Plays | Yds | Time | Result |")
        L.append("|---|---|---|---|---|---|---|---|")
        for i, d in enumerate(res.drives, 1):
            L.append(f"| {i} | {names[d['side']]} | {d['quarter']} | own {d['start']} | {d['plays']} | {d['yards']} | "
                     f"{_clock(d['secs'])} | {d['result']} |")
    return "\n".join(L)
