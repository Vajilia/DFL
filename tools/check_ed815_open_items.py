"""Validate Edition 8.15 §20's open-item register against the source text.

This checks classification completeness, not whether the owner has resolved an item.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIBLE = ROOT / "docs" / "DFL_Design_Document_Ed8.15.md"
REGISTER = ROOT / "docs" / "ed815_open_items.json"
VALID_IMPACT = {"blocking", "nonblocking", "closed"}
VALID_DISPOSITION = {
    "requires_explicit_freeze",
    "future_implementation_or_calibration",
    "explicitly_deferred",
    "fixed_default",
}

def validate(document: str, record: dict):
    if record.get("schema") != "dfl-ed815-open-item-register-v1":
        raise ValueError("wrong open-item schema")
    if "## §20 Open items\n" not in document:
        raise ValueError("Edition 8.15 §20 absent")
    section = document.split("## §20 Open items\n", 1)[1]
    originals = re.findall(r"^(\d+)\.\s+(.+)$", section, flags=re.M)
    if [int(n) for n, _ in originals] != list(range(1, 19)):
        raise ValueError("the Bible no longer has precisely eighteen consecutively numbered items")
    items = record.get("items", [])
    if not isinstance(items, list) or len(items) != 18:
        raise ValueError("open-item register must contain eighteen entries")
    blockers = []
    for i, (item, source) in enumerate(zip(items, originals), start=1):
        number, text = source
        if item.get("number") != i or item.get("id") != f"DFL-20-{i:03d}":
            raise ValueError(f"item {i} has an unstable identifier")
        if item.get("anchor") != f"{number}. {text}":
            raise ValueError(f"item {i} lost its exact constitutional source anchor")
        impact, disposition = item.get("freeze_impact"), item.get("disposition")
        if impact not in VALID_IMPACT or disposition not in VALID_DISPOSITION:
            raise ValueError(f"item {i} has invalid classification")
        if not item.get("next_action"):
            raise ValueError(f"item {i} has no disposition plan")
        if impact == "blocking":
            if disposition != "requires_explicit_freeze" or not item.get("blocker_reason"):
                raise ValueError(f"item {i} was silently waived")
            blockers.append(item["id"])
        elif item.get("blocker_reason"):
            raise ValueError(f"item {i} has contradictory block status")
    if len(blockers) != 6:
        raise ValueError("unexpected number of unresolved freeze decisions")
    if items[17]["freeze_impact"] != "closed" or items[17]["disposition"] != "fixed_default":
        raise ValueError("jersey-number defaults were reopened without approval")
    if items[11]["disposition"] != "explicitly_deferred":
        raise ValueError("emergency cap borrowing must remain deferred")
    return blockers

def main():
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    blockers = validate(BIBLE.read_text(encoding="utf-8"), data)
    print(f"OK: 18 pinned §20 items; {len(blockers)} require pre-founding freeze choices")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
