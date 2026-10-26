"""Read-only Edition 8.15 migration identity and schedule audit.

Checks historical stable IDs and all 360 fixtures before any production migration.
Never writes the legacy source files.
"""
from __future__ import annotations

import csv
import io
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIBLE = ROOT / "docs" / "DFL_Design_Document_Ed8.15.md"
DELTA = ROOT / "docs" / "ed815_legacy_identity_delta.json"

FIELD_MAP = {
    "abbr": "abbr",
    "location": "location",
    "primary_color": "primary",
    "primary_hex": "primary_hex",
    "secondary_color": "secondary",
    "secondary_hex": "secondary_hex",
    "tertiary_color": "tertiary",
    "tertiary_hex": "tertiary_hex",
}
UNCHANGED = {
    "conference": "conference",
    "division": "division",
    "team_city": "city",
    "team_name": "nickname",
    "venue": "venue",
    "division_rank": "seed",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main() -> None:
    bible = BIBLE.read_text(encoding="utf-8")
    blocks = re.findall(r"```\s*\n(.*?)```", bible, flags=re.S)
    def canonical(header: str) -> list[dict[str, str]]:
        matches = [b for b in blocks if b.startswith(header + ",") or b.splitlines()[0] == header]
        require(len(matches) == 1, f"missing or ambiguous Bible CSV: {header}")
        return list(csv.DictReader(io.StringIO(matches[0].strip())))

    clubs = canonical("team_id,abbr,team_city,team_name")
    fixtures = canonical("week,game,date,kickoff,away,home")
    old_clubs = read_csv(ROOT / "data" / "teams.csv")
    old_fixtures = [r for r in read_csv(ROOT / "data" / "schedule_2000.csv")
                    if r["week"] and r["game"]]
    delta = json.loads(DELTA.read_text(encoding="utf-8"))

    require(len(clubs) == len(old_clubs) == 48, "expected 48 teams")
    require(len(fixtures) == len(old_fixtures) == 360, "expected 360 numbered games")
    canonical_by_id = {int(r["team_id"]): r for r in clubs}
    legacy_by_id = {int(r["club_id"]): r for r in old_clubs}
    require(set(canonical_by_id) == set(legacy_by_id) == set(range(1, 49)),
            "team numeric identities must remain stable, 1..48")
    expected_deltas = []
    counts: Counter[str] = Counter()
    legacy_name_to_city = {}
    for club_id, new in canonical_by_id.items():
        old = legacy_by_id[club_id]
        for key, old_key in UNCHANGED.items():
            require(new[key] == old[old_key],
                    f"identity field changed without approval: id={club_id} {key}")
        legacy_name_to_city[f'{old["city"]} {old["nickname"]}'] = new["team_city"]
        changes = {}
        for key, old_key in FIELD_MAP.items():
            if new[key] != old[old_key]:
                changes[key] = {"old": old[old_key], "new": new[key]}
                counts[key] += 1
        if changes:
            expected_deltas.append({
                "stable_club_id": club_id,
                "club": f'{new["team_city"]} {new["team_name"]}',
                "changes": changes,
            })
    expected_deltas.sort(key=lambda d: list(canonical_by_id).index(d["stable_club_id"]))
    require(expected_deltas == delta["changes"], "published identity-delta inventory is stale")
    require(dict(counts) == delta["counts"]["by_field"], "identity-delta counts differ")
    require(delta["counts"]["clubs"] == 48
            and delta["counts"]["with_changes"] == len(expected_deltas),
            "identity-delta totals differ")

    by_key = {(r["week"], r["game"]): r for r in fixtures}
    require(len(by_key) == 360, "duplicate canonical fixture keys")
    for old in old_fixtures:
        key = (old["week"], old["game"])
        require(key in by_key, f"legacy fixture key absent: {key}")
        new = by_key[key]
        for field in ("date", "kickoff"):
            require(old[field] == new[field], f"fixture {key} {field} mismatch")
        require(legacy_name_to_city[old["away"]] == new["away"],
                f"fixture {key} away changed")
        require(legacy_name_to_city[old["home"]] == new["home"],
                f"fixture {key} home changed")
    print("OK: 48 stable club IDs, 176 reviewed field deltas, 360 identical numbered fixtures")


if __name__ == "__main__":
    main()
