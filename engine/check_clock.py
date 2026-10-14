"""Clock management (rules version 3, 2026-10-14): near the end of a half the offense kicks or spikes instead of running a play it cannot finish, and a team that leads late kneels.
Rules 1 and 2 must come out exactly as before (the fingerprint test in docs/decisions.md).

    python engine/check_clock.py
"""
import collections
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_export

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def stats(d):
    box, games = d["box"], {g["id"]: g for g in d["games"] + d["playoffs"] + d["ambassador"]}
    c = collections.Counter()
    for gid, b in box.items():
        g = games[gid]; ps = b["p"]
        for i, p in enumerate(ps):
            k = p[6]
            c[k] += 1
            if k == "SP":
                c["sp"] += 1
                prev = ps[i - 1] if i else None
                # a spike stops a running clock: it follows a snap that left it running, in the same drive, in the 2nd or 4th quarter, with a down left
                if not (prev and prev[13] == p[13] and prev[6] in ("RU", "PC", "SK") and p[10] in (2, 4) and p[1] <= 4 and p[12] == 0):
                    c["sp_bad"] += 1
            if k == "KN":
                c["kn"] += 1
                lead = (g["hp"] - g["ap"]) * (1 if p[0] == 0 else -1)
                if p[10] != 4 or p[12] or lead <= 0 or p[4] != -1:
                    c["kn_bad"] += 1
        for k, dr in enumerate(b["dr"]):
            if dr[1] == 2 and dr[6] == "END_PERIOD":
                pl = [x for x in ps if x[13] == k and x[6] in ("RU", "PC", "SK", "PI", "IN", "FG", "PU", "SP", "KN")]
                if pl and pl[-1][3] >= 61 and pl[-1][6] in ("RU", "PC", "SK", "PI", "SP"):
                    c["stuck"] += 1
    c["games"] = len(box)
    return c


c2, c3 = stats(site_export.export(7, 2)), stats(site_export.export(7, 3))
check("rules 2 has no spikes and no kneels", c2["SP"] == 0 and c2["KN"] == 0, str(c2))
check("rules 3: a half that ends with the offense inside the opponent's 40 is rare (rules 2 leaves it dozens of times)", c2["stuck"] > 40 and c3["stuck"] * 4 < c2["stuck"], f"{c2['stuck']} -> {c3['stuck']}")
check("rules 3: spikes happen, and every one stops a running clock in the 2nd or 4th quarter", c3["sp"] > 100 and c3["sp_bad"] == 0, f"{c3['sp']} spikes, {c3['sp_bad']} bad")
check("rules 3: kneels happen, and only a leading team in the 4th quarter kneels, for a yard lost", c3["kn"] > 300 and c3["kn_bad"] == 0, f"{c3['kn']} kneels, {c3['kn_bad']} bad")
check("rules 3: turnovers and penalties stay in their usual range", abs(c3["TO"] / c3["games"] - c2["TO"] / c2["games"]) < 1.5 and abs(c3["PN"] / c3["games"] - c2["PN"] / c2["games"]) < 1.5, f"{c2['TO']/c2['games']:.2f} {c3['TO']/c3['games']:.2f}")

# the first two versions are byte for byte what they were
def fp(r):
    box = site_export.export(7, r)["box"]
    return hashlib.sha256(json.dumps(box, sort_keys=True).encode()).hexdigest()[:16]
check("rules 1 is unchanged", fp(1) == "8f192eab685ccf5a", fp(1))
check("rules 2 is unchanged", fp(2) == "304532285addcee2", fp(2))
check("rules 3 is unchanged", fp(3) == "ece72a2698c8a433", fp(3))
check("rules 4 is unchanged", fp(4) == "2259b2b7e5af2ce0", fp(4))

print("\n%d failed" % len(failures) if failures else "\nall passed")
sys.exit(1 if failures else 0)
