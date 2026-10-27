"""Validate the pinned Edition 8.15 document against the source-anchor register.

This does NOT assert implementation compliance. It fails closed on document drift
or an incomplete coarse clause register. Atomic implementation coverage is separate.
Run: python tools/check_ed815_register.py
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs" / "DFL_Design_Document_Ed8.15.md"
MANIFEST = ROOT / "docs" / "ed815_rule_register.json"

def main() -> int:
    raw = DOCUMENT.read_bytes()
    if b"\r" in raw:
        print("FAIL: design document must be UTF-8 with LF endings")
        return 1
    text = raw.decode("utf-8")
    lines = text.splitlines()
    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reference = expected["reference_sha256"]
    filtered = "".join(
        line + "\n" for line in text.splitlines()
        if not line.startswith("**Content hash (SHA-256 of this file with this line removed):**")
    )
    digest = hashlib.sha256(filtered.encode("utf-8")).hexdigest()
    errors = []
    if digest != reference:
        errors.append(f"authority SHA-256 mismatch: {digest} != {reference}")
    if expected.get("frozen") is True:
        errors.append("manifest incorrectly claims a frozen implementation")
    ids = [r["id"] for r in expected["clauses"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate clause ID")
    selected = {}
    section = 0
    fenced = False
    for number, line in enumerate(lines, 1):
        head = re.match(r"^## §(\d+)\s+", line)
        if head:
            section = int(head.group(1))
            fenced = False
            continue
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        is_value = (section == 0 and line.startswith("|")
                    and not re.match(r"^\|\s*(?:Item\s*\||[-: ]+\|)", line))
        is_clause = 1 <= section <= 19 and line.startswith("- ")
        is_gate = section == 18 and bool(re.match(r"^\*\*[A-Z][A-Z-]+\*\*\s+—", line))
        if is_value or is_clause or is_gate:
            selected[number] = line
    registered = {}
    for r in expected["clauses"]:
        line_no = r["source_line"]
        if not isinstance(line_no, int) or line_no < 1 or line_no > len(lines):
            errors.append(f"{r['id']}: source line out of bounds")
        elif lines[line_no - 1] != r["anchor"]:
            errors.append(f"{r['id']}: source anchor mismatch")
        if line_no in registered:
            errors.append(f"two rules point to source line {line_no}")
        registered[line_no] = r["anchor"]
    if selected != registered:
        missing = sorted(set(selected) - set(registered))
        extra = sorted(set(registered) - set(selected))
        errors.append(f"register coverage changed: missing={missing}, extra={extra}")
    if errors:
        print("FAIL: Edition 8.15 register")
        for e in errors:
            print(" -", e)
        return 1
    print(f"OK: {len(ids)} coarse clauses anchored; SHA-256 verified; implementation UNVERIFIED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
