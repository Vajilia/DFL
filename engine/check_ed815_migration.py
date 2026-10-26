"""Edition 8.15 legacy migration consistency check."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / "tools" / "check_ed815_migration.py")]))
