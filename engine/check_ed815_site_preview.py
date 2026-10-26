"""Edition 8.15 founding website renders only canonical public data."""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import ed815_site_preview as SITE

document = SITE.SOURCE.read_text(encoding="utf-8")
teams, games = SITE.founding_tables(document)
assert len(teams) == 48
assert sum(x["is_active"] == "true" for x in teams) == 40
assert len(games) == 360
assert {x["club_status"] for x in teams} == {"active", "ambassador"}

secret_card = {
    "id": "P-X", "name": "<script>Player</script>", "role": "player",
    "position": "QB", "birth_year": 1978, "height": 69, "weight": 152,
    "look": {"hair_color": "red", "secret_memory": "DO NOT EXPOSE"},
    "attributes": {"throwing": 99}, "memories": ["DO NOT EXPOSE"],
}
events = [
    {"id": "e1", "sequence": 1, "simulated_time": "2000-01-01",
     "visibility": "public", "public_summary": "<script>Signed</script>",
     "private_details": "DO NOT EXPOSE"},
    {"id": "e2", "sequence": 2, "simulated_time": "2000-01-02",
     "visibility": "private", "public_summary": "DO NOT EXPOSE"},
]
h = SITE.render_html(document, cards=[secret_card], events=events, revealed_through_sequence=1)
assert h.startswith("<!doctype html>")
assert 'Content-Security-Policy' in h
assert h.count("<section id=") == 6
for tab in ("home", "teams", "players", "schedule", "standings", "statistics"):
    assert f'href="#{tab}"' in h
    assert f'<section id="{tab}">' in h
assert h.count("<tr>") == 410  # two headers, 48 clubs, 360 fixtures
assert "&lt;script&gt;Player&lt;/script&gt;" in h
assert "&lt;script&gt;Signed&lt;/script&gt;" in h
assert "<script>" not in h
assert "DO NOT EXPOSE" not in h\nassert "Final recorded" not in h
assert "pause-live" not in h
assert "admin=1" not in h
assert "<button" not in h and "<form" not in h
assert "public-event digest" in h.lower()
assert SITE.render_html(document, cards=[secret_card], events=events, revealed_through_sequence=1) == h

def must_fail(source):
    try:
        SITE.founding_tables(source)
    except ValueError:
        return
    raise AssertionError("invalid founding source was accepted")

must_fail(document.replace("30,MON,Montana", "99,MON,Montana", 1).replace("21,SEA,Seattle", "99,SEA,Seattle", 1))
must_fail(document.replace("2000-07-01,17:30,Oklahoma City,St. Louis",
                           "2000-07-01,17:30,Unknown City,St. Louis", 1))
with tempfile.TemporaryDirectory() as td:
    output = Path(td) / "preview.html"
    result = subprocess.run(
        [sys.executable, str(ROOT / "engine" / "ed815_site_preview.py"), "--out", str(output)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert output.is_file()
    assert output.read_text(encoding="utf-8").count("<section id=") == 6
print("OK: six-tab read-only founding preview, 48 clubs, 360 fixtures, zero hidden/control leaks")
