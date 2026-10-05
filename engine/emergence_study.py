"""What greatness looks like when nothing designates it.

Plays several long leagues and reports how often the media recognizes a legend, how the Hall of Fame fills, what a legend's career
looks like, and whether teams led by recognized legends are any more successful than the rest (they should be a little, and
nowhere near enough to threaten the fair-competitiveness bands). Writes reports/emergence_study.md.

    python engine/emergence_study.py [--leagues 6] [--seasons 100]
"""
import argparse
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import recognition as RC  # noqa: E402
import staff_cards as S  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__)).rsplit(os.sep, 1)[0]


def one(seed, seasons):
    r = random.Random(seed)
    L = new_league(r, rosters=True)
    led = dict(n=0, wins=0.0, playoff=0, titles=0)
    per_year_legends = []
    for y in range(1, seasons + 1):
        legends = {t.id for t in L.teams if t.coach.standing in ("legend", "Hall of Famer") and t.status == "active"}
        res = run_season(L, y, r, Options(engine="fast", keep_boxes=False))
        pct = {tid: float(s.pct) for tid, s in res.stats.items()}
        po = {t for seeds in res.seeds.values() for t in seeds}
        for tid in legends:
            if tid in pct:
                led["n"] += 1
                led["wins"] += pct[tid]
                led["playoff"] += tid in po
                led["titles"] += tid == res.champion
        per_year_legends.append(sum(1 for t in L.teams if t.coach.standing == "legend") + sum(1 for t in L.teams if t.gm.standing == "legend")
                                + sum(1 for t in L.teams if t.owner.standing == "legend"))
    return L, led, per_year_legends


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leagues", type=int, default=6)
    ap.add_argument("--seasons", type=int, default=100)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    out = [f"# Emergent greatness: {a.leagues} leagues x {a.seasons} seasons\n",
           "Nobody is born a legend and nothing limits how many there can be. Each season the engine records honors and a career esteem; "
           "the 52 media outlets read each person's esteem with their own noise and a credibility-weighted share of them calling someone "
           "a legend makes it so; the Hall of Fame (the outlets and the 48 owners) votes on people who retired a few years ago. "
           "This study counts what comes out.\n"]
    tot = {k: [] for k in RC.KINDS}
    hall = {k: [] for k in RC.KINDS}
    led = dict(n=0, wins=0.0, playoff=0, titles=0)
    stats = []
    sample = None
    lens = []
    contested = slipped = 0
    per_year = []
    for i in range(a.leagues):
        L, ld, py = one(200 + i, a.seasons)
        per_year += py
        for k in led:
            led[k] += ld[k]
        rec = [e for e in L.archive if e["event"] == "legend_recognized"]
        for k in RC.KINDS:
            tot[k].append(sum(e["kind"] == k for e in rec))
            hall[k].append(sum(h["kind"] == k for h in L.hall))
        contested += sum(e["event"] == "legend_contested" for e in L.archive)
        slipped += sum(e["event"] == "legend_slipped" for e in L.archive)
        classes = {}
        for h in L.hall:
            classes[h["year"]] = classes.get(h["year"], 0) + 1
        stats.append((len(L.hall), max(classes.values()) if classes else 0, a.seasons - len(classes)))
        best = max(L.coaches, key=lambda c: c.esteem)
        if sample is None:
            sample = (L, best)
        for c in L.coaches:
            if c.standing in ("legend", "Hall of Famer"):
                yrs = [e["year"] for e in c.career if e["event"] in ("hired",)]
                lens.append(sum(1 for e in c.career if e["event"] == "hired"))
        print(f"league {i + 1}: {len(L.hall)} in the Hall; recognitions " + ", ".join(f"{k} {tot[k][-1]}" for k in RC.KINDS), flush=True)
    out.append("## How often the media names a legend\n")
    out.append("| Kind of person | Legends recognized per league (mean) | Per decade | Hall of Fame inductees per league |")
    out.append("|---|---|---|---|")
    for k in RC.KINDS:
        m = st.mean(tot[k])
        out.append(f"| {k} | {m:.1f} | {m / (a.seasons / 10):.1f} | {st.mean(hall[k]):.1f} |")
    out.append(f"\nAcross the {a.leagues} leagues: {contested} times the media split on someone before (or instead of) agreeing, and {slipped} times a "
               f"legend lost the title (a legend keeps it with a little extra room, so it rarely flickers).\n")
    out.append(f"Hall of Fame: {st.mean(s[0] for s in stats):.0f} inductees per {a.seasons}-season league on average; the biggest single class in any league was "
               f"{max(s[1] for s in stats)}; classes that year were empty in {st.mean(s[2] for s in stats):.0f} of {a.seasons} seasons. There is no cap or quota: "
               "these numbers are what the voters decide.\n")
    out.append(f"People the media called a legend at once, in all kinds, on the field (coach + GM + owner): mean {st.mean(per_year):.1f}, "
               f"most {max(per_year)}, fewest {min(per_year)}. Nothing holds this number anywhere; it rises and falls with careers.\n")
    out.append("## Do teams led by a recognized-legend coach win more?\n")
    if led["n"]:
        n = led["n"]
        out.append(f"Team-seasons led by a coach the media called a legend or who is in the Hall: {n} over {a.leagues} leagues. Those teams won "
                   f"{100 * led['wins'] / n:.1f}% of their games (league average 50%), made the playoffs {100 * led['playoff'] / n:.0f}% of the time "
                   f"(about 35% on average) and won the title in {100 * led['titles'] / n:.1f}% of seasons (about 2.5% on average). Part of that is "
                   "that these coaches earned their fame by winning (reputation follows results, so some of this is cause and some is effect); the "
                   "coach's own on-field lift is capped at the same small size as everyone else's.\n")
    L, best = sample
    out.append("## The most esteemed coach in the first league\n")
    out.append(C.render_coach(best, L))
    out.append("\n## Hall of Fame, first league\n")
    out.append("| Year | Kind | Name | Esteem | Vote | Honors |\n|---|---|---|---|---|---|")
    for h in L.hall:
        out.append(f"| {h['year']} | {h['kind']} | {h['name']} | {h['esteem']} | {h['share']:.0%} | " + ", ".join(f"{k} x{v}" for k, v in h["honors"].items()) + " |")
    path = a.out or os.path.join(ROOT, "reports", "emergence_study.md")
    open(path, "w").write("\n".join(out) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
