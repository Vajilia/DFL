"""Verify the source-anchored §1 identity/scope decomposition (draft only)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "docs/DFL_Design_Document_Ed8.15.md").read_text(
    encoding="utf-8").splitlines()
coarse = json.loads((ROOT / "docs/ed815_rule_register.json").read_text(
    encoding="utf-8"))
s0 = json.loads((ROOT / "docs/ed815_atomic_rules_section0.json").read_text(
    encoding="utf-8"))
s1 = json.loads((ROOT / "docs/ed815_atomic_rules_section1.json").read_text(
    encoding="utf-8"))
assert s1["schema"] == "dfl-ed815-atomic-rule-register-v0"
assert s1["status"] == "partial_unverified"
assert s1["reference_sha256"] == s0["reference_sha256"] == coarse["reference_sha256"]
assert s1["coverage"]["sections"] == [1]
assert s1["coverage"]["coarse_clauses_covered"] == 5
assert s1["coverage"]["coarse_clauses_total"] == len(coarse["clauses"])
assert s1["coverage"]["atomic_entries"] == len(s1["atoms"]) == 13
clauses = {c["id"]: c for c in coarse["clauses"] if c["section"] == 1}
assert len(clauses) == 5
assert {a["clause_id"] for a in s1["atoms"]} == set(clauses)
ids = {a["id"] for a in s0["atoms"]}
assert len(ids) == len(s0["atoms"])
for atom in s1["atoms"]:
    aid = atom["id"]
    c = clauses[atom["clause_id"]]
    assert aid not in ids and re.fullmatch(r"DFL-01-\d{3}-\d{2}", aid)
    ids.add(aid)
    assert atom["source_line"] == c["source_line"]
    assert source[c["source_line"] - 1] == c["anchor"]
    assert atom["source_fragment"] in c["anchor"]
    assert atom["requirement"] and atom["verification"] == "pending"
    assert atom["implementation"] == atom["test"] == "unmapped"
for parent in clauses:
    suffixes = sorted(int(a["id"].split("-")[-1])
                      for a in s1["atoms"] if a["clause_id"] == parent)
    assert suffixes == list(range(1, len(suffixes) + 1))
print("OK: 5/5 §1 clauses decomposed, 13 anchored draft atoms; 83 across §0+§1")
