"""Fast entrypoint for Edition 8.15 source-table integrity."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from check_ed815_tables import main
if __name__=="__main__":
    raise SystemExit(main())
