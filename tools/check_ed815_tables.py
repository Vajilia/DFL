"""Validate Edition 8.15's stable, source-anchored tabular rule identities.

These rows are normative reference DATA, not proof that the running DFL engine
complies. One ID per team, fixture, and international venue; pinned source
anchors cannot silently drift or lose identities.
"""
from __future__ import annotations
import csv
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BIBLE=ROOT/"docs"/"DFL_Design_Document_Ed8.15.md"
MANIFEST=ROOT/"docs"/"ed815_table_row_register.json"
COUNTS={5:48,6:360,8:50}
LABELS={5:"TEAM",6:"GAME",8:"VENUE"}

def source_tables(raw):
    section=0
    fenced=False
    content={5:[],6:[],8:[]}
    for lineno,line in enumerate(raw.splitlines(),1):
        m=re.match(r"^## §(\d+)\s+",line)
        if m:
            section=int(m.group(1))
        if line.startswith("```"):
            fenced=not fenced
            continue
        if fenced and section in content and line:
            content[section].append((lineno,line))
    return content

def main():
    raw=BIBLE.read_text(encoding="utf-8")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema")!="dfl-ed815-table-row-register-v1":
        raise AssertionError("unknown Edition 8.15 table registry schema")
    source=source_tables(raw)
    observed=manifest["rows"]
    if len(observed)!=sum(COUNTS.values()):
        raise AssertionError("not all normative table rows registered")
    if len(set(x["id"] for x in observed))!=len(observed):
        raise AssertionError("duplicate stable rule identifier")
    expected=[]
    for section,count in COUNTS.items():
        lines=source[section]
        if len(lines)!=count+1:
            raise AssertionError(f"§{section}: source table should contain {count} data rows")
        header=lines[0][1]
        if manifest["headers"][str(section)]!=header:
            raise AssertionError(f"§{section}: header changed")
        parsed_header=next(csv.reader([header]))
        records=[dict(zip(parsed_header,next(csv.reader([row])))) for _,row in lines[1:]]
        if any(len(next(csv.reader([row])))!=len(parsed_header) for _,row in lines[1:]):
            raise AssertionError(f"§{section}: CSV column mismatch")
        if section==5:
            keys=[row["team_id"] for row in records]
        elif section==6:
            keys=[(row["week"],row["game"]) for row in records]
        else:
            keys=[row["venue_id"] for row in records]
        if len(keys)!=len(set(keys)):
            raise AssertionError(f"§{section}: duplicate canonical source-row identity")
        for i,(line_no,anchor) in enumerate(lines[1:],1):
            expected.append(dict(id=f"DFL-{section:02d}-{LABELS[section]}-{i:03d}",
                                 section=section,source_line=line_no,anchor=anchor))
    if manifest["counts"]!={str(k):v for k,v in COUNTS.items()}:
        raise AssertionError("registered table row counts changed")
    if observed!=expected:
        raise AssertionError("table row IDs or source anchors do not match Edition 8.15")
    print("OK: 458 source-anchored Edition 8.15 table row IDs (48 clubs, 360 games, 50 venues)")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
