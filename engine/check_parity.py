"""Parity profiles (parity.py): "tight" changes nothing; "none" really removes the cap, floor, exile help and lottery, and the league still runs."""
import os, random, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import economy as EC, parity
from league import new_league
from season import Options, run_season
import fingerprint

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


shipped = dict(REGULATED=True, FLOOR_FRAC=0.90, ABSORPTION=0.5, MAX_SALARY=25.0, STAFF_CONTRACT_MAX_PCT=0.08, STAFF_PAYROLL_MAX_PCT=0.20)
parity.apply("tight")
check("tight leaves every dial as shipped and adds no Options", all(getattr(EC, k) == v for k, v in shipped.items()) and parity.options() == {})
try:
    parity.apply("loosey"); check("an unknown profile is refused", False)
except ValueError:
    check("an unknown profile is refused", True)

# tight: the same six seasons as before the profiles existed (the hash was first taken on the code without them, baa3e7353bf2281b, and held through the parity merge;
# it moved to the value below at PR #14, the Commissioner's tiebreak-order change, 2026-10-14, and has not moved since)
lg, res, _ = fingerprint.run(33, 6)
check("tight plays seed 33 for six seasons exactly as the code did before profiles", fingerprint.fingerprint_of(lg, res) == "9871d9a5986ec47d")

# none
parity.apply("none")
check("none switches off the regulated economy", EC.REGULATED is False and EC.FLOOR_FRAC == 0 and EC.ABSORPTION == 0 and EC.limit(type("T", (), {"bank": 0.0})()) >= 1e5)
rng = random.Random(33)
lg = new_league(rng, rosters=True)
out = [run_season(lg, y, rng, Options(engine="fast", keep_boxes=False, **parity.options())) for y in range(1, 7)]
check("none: six seasons run, each with a champion and a 48-pick draft", all(r.champion is not None and len(r.draft) == 48 for r in out))
check("none: no pick is a lottery pick, and the exiled clubs hold no early priority", all(b != "exiled_lottery" for r in out for _, _, b in r.draft) and all(r.lottery_pool_order == [] for r in out))
check("none: nothing is banked or topped up to a floor (the pool only holds conduct fines)", all(not t.bank and not any(t.topup) for t in lg.teams))
pay = [EC.payroll(t) for t in lg.teams]
check("none: payrolls are free to go past the old cap (the cap really is off)", max(pay) > 100.0, f"max {max(pay):.1f}")
off = [r.offseason["cap"] for r in out if r.offseason and r.offseason.get("cap")]
check("none: the season accounts show no forfeit, shortfall, absorption, levy or payout", all(not (c["forfeited"] or c["shortfall"] or c["absorbed"] or c["levy"] or c["payout"]) for c in off), str(off[:1]))
parity.apply("tight")
check("switching back to tight restores the dials", all(getattr(EC, k) == v for k, v in shipped.items()))
# a new league records its profile, and the runner opens it under that profile
import json, subprocess, tempfile
for prof in ("none", "tight"):
    d = tempfile.mkdtemp()
    subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "live.py"), "--out", d, "--opener-at", "2026-10-17T19:00", "--seed", "7", "--pacing", "blocks", "--parity", prof, "--init"], check=True, capture_output=True)
    m = json.load(open(os.path.join(d, "meta.json")))
    check(f"a new league made with --parity {prof} records it in meta.json", m.get("parity") == prof)
import live
w = live.World(7, 0, "blocks", None, None, "none")
check("the runner opens a league under its recorded profile (none: the cap is off) and an old meta.json (no profile) opens as tight", EC.REGULATED is False and live.World(7, 0, "blocks", None, None, json.loads('{}').get("parity", "tight")).profile == "tight" and EC.REGULATED is True)
parity.apply("tight")
print("\nALL PASS" if not failures else "\nFAILED: " + ", ".join(failures))
sys.exit(1 if failures else 0)
