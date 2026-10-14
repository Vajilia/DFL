"""Kickoffs and conversions (rules version 5, 2026-10-14): a kickoff is a play of its own (touchback, return, return touchdown, fumble, foul, onside kick), and the point
after a touchdown is an extra-point kick or a two-point try in the log. Rules 1 to 4 must come out exactly as before (check_clock.py holds their fingerprints).

    python engine/check_kickoffs.py
"""
import collections
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_export

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


d5, d4 = site_export.export(7, 5), site_export.export(7, 4)
games = {g["id"]: g for g in d5["games"] + d5["playoffs"] + d5["ambassador"]}
c = collections.Counter()
for gid, b in d5["box"].items():
    ps, dr, g = b["p"], b["dr"], games[gid]
    firsts = {}
    for i, p in enumerate(ps):
        firsts.setdefault(p[13], i)
    sc = [0, 0]
    for k, d in enumerate(dr):
        side, q, start, plays, yds, secs, res, pts, dpts = d
        sc[side] += pts
        sc[1 - side] += dpts
        first = ps[firsts[k]] if k in firsts else None
        rows = [p for p in ps if p[13] == k]
        if res == "KICK_TD":
            c["ktd"] += 1
            if not (rows and rows[0][6] == "KO" and rows[0][5] == 2 and plays == 0):
                c["ktd_bad"] += 1
        # the drive after a score, the opening drive of each half and of overtime begin with a kickoff; no other drive does
        prev = dr[k - 1] if k else None
        after_score = prev is None or prev[6] in ("TD", "FG", "SAFETY", "INT_TD", "FUMBLE_TD", "KICK_TD")
        starts_ko = bool(first) and first[6] == "KO"
        if starts_ko:
            c["ko_drives"] += 1
        if after_score and not starts_ko and res != "KICK_TD":
            c["missing_ko"] += 1
        if starts_ko and not after_score and not (first[10] == 3 or first[12]):
            c["stray_ko"] += 1
        # a touchdown is followed by one try, whose result is in the drive's points (no try in sudden death or when it cannot matter)
        tries = [p for p in rows if p[6] in ("XP", "2P")]
        if res in ("TD", "INT_TD", "FUMBLE_TD", "KICK_TD"):
            c["td"] += 1
            if len(tries) > 1:
                c["many_tries"] += 1
            if tries:
                t = tries[0]
                got = (t[8] if t[6] == "XP" else 2 * t[9])
                if (pts if res in ("TD", "KICK_TD") else dpts) != 6 + got:
                    c["pts_bad"] += 1
            else:
                c["no_try"] += 1
        elif tries:
            c["try_without_td"] += 1
    if sc != [g["hp"], g["ap"]]:
        c["score_bad"] += 1
    for p in ps:
        k = p[6]
        if k == "KO":
            c["ko"] += 1
            c[f"code{p[5]}"] += 1
            if p[5] not in range(7):
                c["code_bad"] += 1
            if p[5] == 0 and p[3] != 31:
                c["tb_bad"] += 1
            if p[5] in (1, 4) and p[3] < 1:
                c["ret_bad"] += 1
        if k == "XP":
            c["xp"] += 1
            c["xp_good"] += p[8]
        if k == "2P":
            c["tp"] += 1
            c["tp_good"] += p[9]
n = len(d5["box"])
check("every score is followed by a kickoff (the opening kick, the second half, overtime, after every touchdown, field goal and safety)", c["missing_ko"] == 0, str(c["missing_ko"]))
check("no drive begins with a kickoff that does not belong there", c["stray_ko"] == 0, str(c["stray_ko"]))
check("the kickoff outcomes are the seven the page knows, and a touchback is spotted on the 31", c["code_bad"] == 0 and c["tb_bad"] == 0 and c["ret_bad"] == 0, str(c))
check("about 8 to 13 kickoffs a game, and about 55% to 65% are touchbacks", 8 <= c["ko"] / n <= 13 and 0.5 <= c["code0"] / c["ko"] <= 0.7, f"{c['ko'] / n:.1f} a game, {c['code0'] / c['ko']:.2f} touchbacks")
check("a kickoff is returned for a touchdown now and then (0.1% to 1% of kickoffs), and the touchdown is a drive of its own", 0.001 <= c["ktd"] / c["ko"] <= 0.01 and c["ktd_bad"] == 0, f"{c['ktd']} of {c['ko']}, {c['ktd_bad']} bad")
att = c["code5"] + c["code6"]
check("onside kicks are tried (a few hundred a thousand games) and are recovered 15% to 40% of the time", 20 <= att and 0.1 <= c["code5"] / att <= 0.45, f"{att} tried, {c['code5']} recovered")
check("every touchdown has one try, worth what the drive says, and no try follows anything else", c["many_tries"] == 0 and c["pts_bad"] == 0 and c["try_without_td"] == 0 and c["no_try"] <= 0.02 * c["td"], str(c))
check("extra points are good 90% to 97% of the time", 0.9 <= c["xp_good"] / c["xp"] <= 0.97, f"{c['xp_good'] / c['xp']:.3f}")
check("two-point tries happen (1% to 8% of touchdowns) and are good 35% to 62% of the time", 0.01 <= c["tp"] / c["td"] <= 0.08 and 0.35 <= c["tp_good"] / c["tp"] <= 0.62, f"{c['tp']} tries, {c['tp_good']} good")
check("the drives' points add up to every game's final score", c["score_bad"] == 0, str(c["score_bad"]))
pts = lambda d: st.mean(g["hp"] + g["ap"] for g in d["games"])
check("scoring per game stays within two points of rules 4", abs(pts(d5) - pts(d4)) < 2.0, f"{pts(d4):.1f} {pts(d5):.1f}")
check("rules 4 has no kickoffs in the log", all(p[6] not in ("KO", "XP", "2P") for b in d4["box"].values() for p in b["p"]))
print("\n%d failed" % len(failures) if failures else "\nall passed")
sys.exit(1 if failures else 0)
