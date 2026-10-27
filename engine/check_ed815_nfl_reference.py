"""Audit the candidate 2026 NFL gap-source inventory without freezing DFL."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
reference = json.loads((ROOT / "docs/ed815_nfl_2026_reference.json").read_text(
    encoding="utf-8"))
open_items = json.loads((ROOT / "docs/ed815_open_items.json").read_text(
    encoding="utf-8"))

assert reference["schema"] == "dfl-ed815-nfl-reference-inventory-v1"
assert reference["status"] == "candidate_not_frozen"
assert reference["dfl_authority"] == "docs/DFL_Design_Document_Ed8.15.md"
assert "Edition 8.15" in reference["precedence"][0]
assert "zero automatic effect" in reference["temporal_fence"]
sources = reference["sources"]
assert len(sources) == 3 and len({x["id"] for x in sources}) == 3
assert all(x["url"].startswith("https://") and x["year"] == 2026
           and x["archived_copy"] is False and x["sha256"] is None
           for x in sources)
assert sources[0]["url"].endswith(".pdf")
defaults = {x["id"]: x for x in reference["provisional_defaults"]}
assert {key: row["value"] for key, row in defaults.items()} == {
    "NFL-GD-48": 48, "NFL-GD-47": 47, "NFL-PS-GAME": 2,
    "NFL-PS-PLAYER": 3, "NFL-IR-MIN": 4,
}
assert all(x["source"] in {s["id"] for s in sources}
           and x["dfl_status"] == "requires_freeze"
           for x in defaults.values())
assert any(x["number"] == 8 and x["freeze_impact"] == "blocking"
           for x in open_items["items"])
assert len(reference["remaining_evidence"]) >= 3
print("OK: candidate 2026 NFL sources and five defaults recorded; freezing still blocked")
