"""Contract tests for pinned §20 decision and calibration backlog."""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_ed815_open_items as O

document = O.BIBLE.read_text(encoding="utf-8")
register = json.loads(O.REGISTER.read_text(encoding="utf-8"))
blockers = O.validate(document, register)
assert len(blockers) == 6
assert len([x for x in register["items"] if x["freeze_impact"] == "nonblocking"]) == 11
assert len([x for x in register["items"] if x["freeze_impact"] == "closed"]) == 1
assert "DFL-20-004" in blockers
assert "DFL-20-008" in blockers
assert "DFL-20-014" in blockers

def fails(mutated_document, mutated_register):
    try:
        O.validate(mutated_document, mutated_register)
    except ValueError:
        return
    raise AssertionError("a false §20 register passed")

m = copy.deepcopy(register)
m["items"][7]["anchor"] = "8. silently changed"
fails(document, m)
m = copy.deepcopy(register)
m["items"][7]["freeze_impact"] = "closed"
m["items"][7]["disposition"] = "fixed_default"
m["items"][7]["blocker_reason"] = None
fails(document, m)
m = copy.deepcopy(register)
m["items"][11]["disposition"] = "requires_explicit_freeze"
fails(document, m)
fails(document.replace("1. Definitions for the analytics terms", "1. Renamed analytics terms"), register)
print("OK: 18 §20 stable anchors; six normative freeze blockers cannot be silently waived")
