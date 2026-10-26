"""Independent DFLv2 reference validation of six Edition 8.15 source tables.

Copies the CSV blocks verbatim from pinned edition text into an isolated
temporary directory and runs the separately authored DFLv2 validator with its
original checks. The edition hash is validated independently by that tool.
"""
from __future__ import annotations
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOCUMENT=ROOT/"docs"/"DFL_Design_Document_Ed8.15.md"
VALIDATOR=ROOT/"tools"/"ed815_independent_validator.py"
TABLES={2:"CALENDAR",5:"TEAMS",6:"SCHEDULE",
        7:"TOUR",8:"INTL_VENUES",9:"COLOR_REGISTRY"}
EXPECTED={2:27,5:48,6:360,7:28,8:50,9:12}

def extracted_tables(document):
    section=0
    fenced=False
    tables={section:[] for section in TABLES}
    for line in document.splitlines():
        match=re.match(r"^## §(\d+)\s+",line)
        if match:
            section=int(match.group(1))
        if line.startswith("```"):
            fenced=not fenced
            continue
        if fenced and section in TABLES and line:
            tables[section].append(line)
    for section,lines in tables.items():
        if len(lines)!=EXPECTED[section]+1:
            raise AssertionError(
                f"§{section}: expected {EXPECTED[section]} records plus CSV header")
    return tables

def main():
    content=DOCUMENT.read_text(encoding="utf-8")
    tables=extracted_tables(content)
    with tempfile.TemporaryDirectory(prefix="dfl-ed815-validator-") as working:
        folder=Path(working)
        for section,name in TABLES.items():
            (folder/f"{name}.csv").write_text(
                 "\n".join(tables[section])+"\n",encoding="utf-8",newline="\n")
        command=[sys.executable,str(VALIDATOR),str(folder),
                 "--season","1","--doc",str(DOCUMENT),"--tour-rule","relaxed"]
        result=subprocess.run(command,capture_output=True,text=True,timeout=90)
        print(result.stdout,end="")
        if result.stderr:
            print(result.stderr,file=sys.stderr,end="")
        if result.returncode:
            print(f"Independent DFLv2 validator failed with exit {result.returncode}")
            return 1
        print("OK: independently validated all six exact Edition 8.15 founding CSV blocks")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
