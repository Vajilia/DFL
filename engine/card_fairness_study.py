"""Does the head-coach effect keep the league inside the fair-competitiveness bands?

Runs the same leagues with coaches off and on, and then with the coach effect made 3x and 5x stronger
(a stress test: how much room is there before a band breaks?). Writes reports/coach_fairness_study.md.

    python engine/card_fairness_study.py [--leagues 8] [--seasons 48]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import fairness  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leagues", type=int, default=8)
    ap.add_argument("--seasons", type=int, default=48)
    ap.add_argument("--drive-leagues", type=int, default=5)
    a = ap.parse_args()
    out = ["# Head-coach effect and fair competitiveness\n",
           "Each coach card carries an offense and a defense rating. A 50 is average and has no effect; a 100 is worth "
           f"+{C.COACH_POINTS_AT_100:.1f} point of expected margin on that side of the ball (a 1 is worth -{C.COACH_POINTS_AT_100:.1f}). "
           "Coaches stay with a team until they retire, so a good coach is a lasting edge. This study asks whether that edge "
           "pushes any trend outside the fair-competitiveness bands. Same leagues, same seeds, 48 seasons each (first 8 thrown away).\n"]
    seeds = range(100, 100 + a.leagues)
    base = C.COACH_POINTS_AT_100
    for label, coaches, mult, eng, n in (("Coaches off (the league as it was before cards)", False, 1, "fast", a.leagues),
                                         ("Coaches on, as built (cap 1.0 point per side)", True, 1, "fast", a.leagues),
                                         ("Stress test: coach effect 3x (cap 3.0 points per side)", True, 3, "fast", a.leagues),
                                         ("Stress test: coach effect 5x (cap 5.0 points per side)", True, 5, "fast", a.leagues),
                                         ("Coaches on, as built, full drive engine", True, 1, "drives", a.drive_leagues)):
        C.COACH_POINTS_AT_100 = base * mult
        per, rows = fairness.run(eng, range(100, 100 + n), a.seasons, coaches=coaches)
        bad = [r[0] for r in rows if not r[4]]
        out.append(f"## {label}\n")
        out.append(f"{eng} engine, {n} leagues x {a.seasons} seasons.\n")
        out.append(fairness.table(rows))
        out.append("\n" + ("All trends inside the bands.\n" if not bad else f"Outside the bands: {', '.join(bad)}.\n"))
        print(label, "->", "ALL INSIDE" if not bad else "OUTSIDE: " + ", ".join(bad), flush=True)
    C.COACH_POINTS_AT_100 = base
    path = os.path.join(ROOT, "reports", "coach_fairness_study.md")
    open(path, "w").write("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    main()
