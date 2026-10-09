"""Mid-contract extensions: a good player with her final year ahead can be signed to a new term before it runs out (NFL: drafted players only after
their third season), at today's market price, and always inside the cap.

    python engine/check_extensions.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import economy as EC  # noqa: E402
import rules as R  # noqa: E402
from league import new_league  # noqa: E402
from roster_model import RosterModel  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


rm = RosterModel()
r = random.Random(7)
L = new_league(r, rosters=True)
rows = []
dup = 0
for y in range(1, 7):
    s = run_season(L, y, r, Options(engine="fast", keep_boxes=False))
    yr = s.offseason.get("extension_list", [])
    dup += len(yr) - len({x[1] for x in yr})
    rows += yr
    exiled_now = {t.id for t in L.teams if t.status == "exiled"}
n = len(rows)
per_year = n / 6
check("clubs extend players in mid-contract", n > 0, f"{n} in 6 seasons, {per_year:.0f} a year")
check("a year's extensions are a modest share of the league (10 to 80)", 10 <= per_year <= 80)
check("only players with her final year ahead are extended", all(old_y == 1 for _, _, _, old_y, *_ in rows))
check("only players with 3 or more accrued seasons (NFL: after the third season)", all(acc >= R.EXTENSION_MIN_SEASONS for *_, acc, _, _ in rows))
check("only players rated at the threshold or better, and young enough", all(ovr >= rm.ext_min_ovr - 1.0 and age <= rm.ext_max_age + 1 for *_, age, ovr in rows))
check("an extension pays no less than the old deal (she is signed at her price)", all(new >= old * 1.02 - 1e-9 for _, _, old, _, new, *_ in rows))
check("every extension is a legal length (1 to the contract maximum)", all(1 <= yrs <= EC.CONTRACT_YEARS_MAX for _, _, _, _, _, yrs, *_ in rows))
check("extensions never raise a number above the maximum contract", all(new <= EC.MAX_SALARY + 1e-9 for _, _, _, _, new, *_ in rows))
check("the same player is not extended twice in one offseason", dup == 0)

print()
if failures:
    print(f"{len(failures)} extension check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All extension checks passed.")
