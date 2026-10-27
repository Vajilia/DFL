"""Fail-closed, read-only Phase 1 release readiness gate.

The audit branch remains a research/reference implementation. Use --require-complete
at any eventual candidate promotion; report mode is intentionally nonblocking for CI.
Passing tests must never be confused with compliance of legacy production routes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "ed815_phase1_gates.json"
GATE_IDS = (
    "source_checksum", "founding_tables", "structural_rotation",
    "economic_reference", "viewer_projection", "atomic_rule_manifest",
    "normative_open_items", "nfl_reference_snapshot", "legacy_route_isolation",
    "character_and_game_integration", "website_integration",
    "full_slow_suite", "year_zero_release_rehearsal",
)

def validate(manifest, *, root=ROOT):
    """Return (ready, blockers); raise on malformed or dishonest gate metadata."""
    if manifest.get("schema") != "dfl-ed815-phase1-gates-v1":
        raise ValueError("unrecognized gate schema")
    gates = manifest.get("gates")
    if not isinstance(gates, list):
        raise ValueError("gates must be a list")
    ids = [g.get("id") for g in gates]
    if len(ids) != len(set(ids)) or set(ids) != set(GATE_IDS):
        raise ValueError("duplicate, missing or unrecognized gate")
    for gate in gates:
        if gate.get("state") not in ("verified", "blocked"):
            raise ValueError("unrecognized verification state")
        if not gate.get("meaning") or not gate.get("artifact"):
            raise ValueError("gate requires a rationale and source artifact")
        artifact = root / gate["artifact"]
        if not artifact.is_file() or not artifact.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"missing or untrusted gate artifact: {gate['id']}")
    ci = manifest.get("verified_ci", {})
    if ci.get("fast_passed") != ci.get("fast_total") or not isinstance(ci.get("fast_total"), int):
        raise ValueError("FAST test evidence incomplete")
    blockers = [g["id"] for g in gates if g["state"] != "verified"]
    if not ci.get("slow_tested"):
        if "full_slow_suite" not in blockers:
            raise ValueError("cannot verify slow suite without execution evidence")
    if "normative_open_items" not in blockers:
        open_items = json.loads((root / "docs" / "ed815_open_items.json").read_text(encoding="utf-8"))
        if any(x["freeze_impact"] == "blocking" for x in open_items["items"]):
            raise ValueError("normative items cannot be verified while freeze decisions are open")
    if "atomic_rule_manifest" not in blockers:
        rule_register = json.loads((root / "docs" / "ed815_rule_register.json").read_text(encoding="utf-8"))
        if not rule_register.get("frozen", False):
            raise ValueError("atomic manifest cannot be verified while coarse register unfrozen")
    ready = not blockers and ci.get("slow_tested") is True
    if manifest.get("status") != ("ready" if ready else "blocked"):
        raise ValueError("manifest status contradicts evidence")
    return ready, blockers

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--require-complete", action="store_true")
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ready, blockers = validate(manifest)
    print("ED815 Phase 1:", "READY" if ready else "BLOCKED")
    print("Verified:", len(manifest["gates"]) - len(blockers), "/", len(manifest["gates"]))
    if blockers:
        print("Unresolved:", ", ".join(blockers))
    return 1 if args.require_complete and not ready else 0

if __name__ == "__main__":
    raise SystemExit(main())
