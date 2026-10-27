"""Ensure Edition 8.15 Phase 1 cannot be falsely marked complete."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_ed815_phase1_gate as G

data = json.loads(G.MANIFEST.read_text(encoding="utf-8"))
ready, blockers = G.validate(data)
assert not ready
assert len(data["gates"]) == 13
assert len(blockers) == 8
assert data["verified_ci"]["fast_passed"] == data["verified_ci"]["fast_total"] == 55
assert "legacy_route_isolation" in blockers
assert "atomic_rule_manifest" in blockers
assert "year_zero_release_rehearsal" in blockers

def must_fail(mutant):
    try:
        G.validate(mutant)
    except ValueError:
        return
    raise AssertionError("malformed or dishonest readiness report passed")

m = copy.deepcopy(data)
m["status"] = "ready"
must_fail(m)
m = copy.deepcopy(data)
m["gates"][0]["id"] = "legacy_route_isolation"
must_fail(m)
m = copy.deepcopy(data)
m["gates"][0]["state"] = "passed"
must_fail(m)
m = copy.deepcopy(data)
m["verified_ci"]["fast_passed"] = 54
must_fail(m)
m = copy.deepcopy(data)
m["gates"][0]["artifact"] = "docs/missing-source.txt"
must_fail(m)
m = copy.deepcopy(data)
for g in m["gates"]:
    g["state"] = "verified"
m["status"] = "ready"
must_fail(m)

runner = [sys.executable, str(ROOT / "tools" / "check_ed815_phase1_gate.py")]
report = subprocess.run(runner, capture_output=True, text=True)
assert report.returncode == 0 and "BLOCKED" in report.stdout
promotion = subprocess.run(runner + ["--require-complete"], capture_output=True, text=True)
assert promotion.returncode == 1 and "BLOCKED" in promotion.stdout
print("OK: 13 Phase 1 gates, 8 explicit blockers; premature promotion fails closed")
