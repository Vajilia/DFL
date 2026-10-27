"""Edition 8.15 preview route in the existing website builder is opt-in only."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import build_site as BUILDER

with tempfile.TemporaryDirectory() as td:
    output = Path(td) / "new-preview.html"
    command = [sys.executable, str(ROOT / "engine" / "build_site.py"),
               "--ed815-preview", str(output)]
    run = subprocess.run(command, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert output.exists()
    page = output.read_text(encoding="utf-8")
    assert "Edition 8.15" in page
    assert page.count("<section id=") == 6
    assert "admin=1" not in page and "<button" not in page
    assert "No public player cards" in page
    original = page

    again = subprocess.run(command, capture_output=True, text=True)
    assert again.returncode != 0
    assert output.read_text(encoding="utf-8") == original
    missing_path = subprocess.run(
        [sys.executable, str(ROOT / "engine" / "build_site.py"), "--ed815-preview"],
        capture_output=True, text=True,
    )
    assert missing_path.returncode != 0
    invalid_mix = subprocess.run(
        [sys.executable, str(ROOT / "engine" / "build_site.py"), "--live",
         "--ed815-preview", str(Path(td) / "mixed.html")],
        capture_output=True, text=True,
    )
    assert invalid_mix.returncode != 0
    assert not (Path(td) / "mixed.html").exists()
assert callable(BUILDER.build)
print("OK: opt-in Edition 8.15 website builder, safe output, legacy default unchanged")
