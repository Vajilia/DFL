"""The fairness report's verdicts: inside, edge (outside by no more than two error bars, so not yet distinguishable from chance) and outside."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fairness, rules as R

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def leagues(vals):
    base = {k: (lo + hi) / 2 for k, (lo, hi, _) in R.FAIR_COMPETITION_BANDS.items()}
    return [dict(base, win_pct_sd=v, exile_effect=0.0, _xy=([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0], [0.0, 1.0, 0.0, 1.0])) for v in vals]


def verdict(vals):
    per = leagues(vals)
    rows = fairness.evaluate(per)
    return fairness.verdicts(per, rows)["win_pct_sd"], rows, per


v, rows, per = verdict([0.16, 0.17] * 4)
check("a value inside its band is inside", v[0] == "inside", v)
v, rows, per = verdict([0.17, 0.23] * 4)          # mean 0.20, band 0.13 to 0.19, wide scatter between leagues
check("a value just outside a band that the leagues' scatter cannot rule out is on the edge", v[0] == "edge", v)
check("an edge value is not reported as clearly outside", "win_pct_sd" not in fairness.clearly_outside(per, rows))
v, rows, per = verdict([0.20] * 8)                 # same mean, no scatter at all
check("the same miss with no scatter between leagues is clearly outside", v[0] == "outside", v)
check("clearly_outside names it", fairness.clearly_outside(per, rows) == ["win_pct_sd"])
v, rows, per = verdict([0.40] * 8)
check("a value far outside is outside", v[0] == "outside", v)
check("the table gains a verdict column when the leagues are supplied and not otherwise", "Verdict" in fairness.table(rows, per) and "Verdict" not in fairness.table(rows))
print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
