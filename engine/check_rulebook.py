"""Checks that the code and the DFL Rulebook (rulebook.py) say the same thing, and writes reports/rulebook_status.md.

    python engine/check_rulebook.py

A row's status must be true: "built" rows match the code, "differs" rows really differ, "missing" rows name constants the code does not
have yet. Every rule constant in rules.py and economy.py must be in some row (or be exempt with a reason). When a build step changes a
constant, this check fails until the row is updated, so the rulebook and the code cannot drift apart without anyone noticing.
"""
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import economy  # noqa: E402
import finance  # noqa: E402
import rulebook as RB  # noqa: E402
import rules  # noqa: E402

MODULES = {"rules": rules, "economy": economy, "finance": finance}
failures = []
ABSENT = object()


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def actual(name):
    mod, attr = name.split(".", 1)
    return getattr(MODULES[mod], attr, ABSENT)


def same(a, b):
    return a == b


ids = [r["id"] for r in RB.ROWS]
check("row ids are unique", len(ids) == len(set(ids)))
check("every row has a valid basis and status",
      all(r["basis"] in RB.BASES and r["status"] in ("built", "differs", "missing") for r in RB.ROWS))
check("every row says what it decides", all(r.get("rule") for r in RB.ROWS))

for r in RB.ROWS:
    exp = r.get("expect", {})
    vals = {k: actual(k) for k in exp}
    present = {k for k, v in vals.items() if v is not ABSENT}
    mismatch = {k for k in present if not same(vals[k], exp[k])}
    if r["status"] == "built":
        ok = not mismatch and len(present) == len(exp)
        bad = sorted(mismatch | (set(exp) - present))
        check(f"built: {r['id']}", ok, "code differs on " + ", ".join(bad) if not ok else "")
    elif r["status"] == "differs":
        ok = bool(mismatch) if exp else True
        check(f"differs: {r['id']}", ok, "the code now matches the rulebook; mark it built" if not ok else "")
    else:
        ok = not present
        check(f"missing: {r['id']}", ok, "the code now has " + ", ".join(sorted(present)) + "; update the row" if not ok else "")

covered = set(RB.EXEMPT)
for r in RB.ROWS:
    covered |= set(r.get("expect", {})) | set(r.get("covers", []))
for name in covered:
    if name in RB.EXEMPT or name in {k for r in RB.ROWS for k in r.get("covers", [])}:
        check(f"named constant exists: {name}", actual(name) is not ABSENT)
for mod_name, mod in MODULES.items():
    consts = [f"{mod_name}.{n}" for n in dir(mod) if n.isupper() and not n.startswith("_")]
    loose = [c for c in consts if c not in covered]
    check(f"every constant in {mod_name}.py is in a rulebook row", not loose, ", ".join(loose))
check("every exemption has a reason", all(RB.EXEMPT.values()))

# ---- the status report
by_area = defaultdict(Counter)
for r in RB.ROWS:
    by_area[r["area"]][r["status"]] += 1
lines = ["# Rulebook status: code against the DFL Rulebook\n",
         "Written by `engine/check_rulebook.py`. The prose rulebook is the living doc \"DFL Rulebook: The Synthesis\"; `engine/rulebook.py` is its "
         "machine-readable form, one row per rule. **built** = the code matches the rulebook value; **differs** = the code has it with "
         "another value or another mechanism and must change; **missing** = the rulebook sets it and the code has nothing yet.\n",
         "| Area | built | differs | missing |", "| --- | --- | --- | --- |"]
for area, c in by_area.items():
    lines.append(f"| {area} | {c['built']} | {c['differs']} | {c['missing']} |")
tot = Counter(r["status"] for r in RB.ROWS)
lines.append(f"| **All** | {tot['built']} | {tot['differs']} | {tot['missing']} |\n")
for status, title in (("differs", "The code differs from the rulebook"), ("missing", "The rulebook sets it and the code has nothing yet")):
    lines += [f"## {title}\n", "| Rule | Basis | What the rulebook says |", "| --- | --- | --- |"]
    for r in RB.ROWS:
        if r["status"] == status:
            lines.append(f"| `{r['id']}` | {r['basis']} | {r['rule']} |")
    lines.append("")
lines += ["## The code matches the rulebook\n", "| Rule | Basis | What the rulebook says |", "| --- | --- | --- |"]
for r in RB.ROWS:
    if r["status"] == "built":
        lines.append(f"| `{r['id']}` | {r['basis']} | {r['rule']} |")
lines.append("")
part = [r for r in RB.ROWS if r["status"] == "built" and r.get("mechanism") in ("partial", "not built")]
lines += ["## Constants match but the behaviour is not all there (hand-kept note)\n", "| Rule | Mechanism | What the rulebook says |", "| --- | --- | --- |"]
for r in part:
    lines.append(f"| `{r['id']}` | {r['mechanism']} | {r['rule']} |")
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "rulebook_status.md")
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f:
    f.write("\n".join(lines) + "\n")

print()
if failures:
    print(f"{len(failures)} rulebook check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print(f"All rulebook checks passed ({tot['built']} built, {tot['differs']} differ, {tot['missing']} missing). Report: reports/rulebook_status.md")
