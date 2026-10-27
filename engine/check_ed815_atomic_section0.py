"""Fail-closed checker for *partial* Edition 8.15 atomic §0 rule work.

This is a source-anchoring test. It does NOT mean the implementation of any
unmapped rule has been verified, or that the whole register is complete.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check():
    source = (ROOT / "docs/DFL_Design_Document_Ed8.15.md").read_text(
        encoding="utf-8").splitlines()
    coarse = json.loads((ROOT / "docs/ed815_rule_register.json").read_text(
        encoding="utf-8"))
    partial = json.loads((ROOT / "docs/ed815_atomic_rules_section0.json").read_text(
        encoding="utf-8"))
    if partial["schema"] != "dfl-ed815-atomic-rule-register-v0":
        raise ValueError("wrong atomic draft schema")
    if partial["reference_sha256"] != coarse["reference_sha256"]:
        raise ValueError("atomic source checksum differs from coarse reference")
    if partial["status"] != "partial_unverified":
        raise ValueError("unreviewed section 0 is not frozen")
    clauses = {c["id"]: c for c in coarse["clauses"] if c["section"] == 0}
    if len(clauses) != 21:
        raise ValueError("canonical value row count changed")
    coverage = partial["coverage"]
    if coverage["sections"] != [0] or coverage["coarse_clauses_covered"] != len(clauses):
        raise ValueError("incorrect partial coverage")
    if coverage["coarse_clauses_total"] != len(coarse["clauses"]):
        raise ValueError("coarse source scope changed")
    atoms = partial["atoms"]
    ids, covered = set(), set()
    if coverage["atomic_entries"] != len(atoms):
        raise ValueError("atomic entry count differs")
    for atom in atoms:
        aid, parent = atom["id"], atom["clause_id"]
        if (aid in ids or parent not in clauses
                or re.fullmatch(r"DFL-00-\d{3}-\d{2}", aid) is None
                or not aid.startswith(parent + "-")):
            raise ValueError("duplicate or invalid atomic identity")
        ids.add(aid)
        covered.add(parent)
        row = clauses[parent]
        if (atom["source_line"] != row["source_line"]
                or source[row["source_line"] - 1] != row["anchor"]
                or atom["source_fragment"] not in row["anchor"]):
            raise ValueError("atomic source text/line drifted")
        if not atom["requirement"] or not isinstance(atom["requirement"], str):
            raise ValueError("missing atomic requirement")
        if atom["verification"] != "pending":
            raise ValueError("unmapped draft may not claim implementation verification")
        if atom["implementation"] != "unmapped" or atom["test"] != "unmapped":
            raise ValueError("evidence must be intentionally registered")
    if covered != set(clauses):
        raise ValueError("section 0 has missing canonical clauses")
    for parent in covered:
        suffixes = sorted(int(a["id"].split("-")[-1]) for a in atoms
                          if a["clause_id"] == parent)
        if suffixes != list(range(1, len(suffixes) + 1)):
            raise ValueError("atomic suffixes must be stable and contiguous")
    return len(atoms)


if __name__ == "__main__":
    print("OK: 21/21 Section 0 clauses source-anchored into",
          check(), "draft atoms; all implementation evidence pending")
