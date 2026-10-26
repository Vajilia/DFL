"""Independent DFLv2 cross-check of Edition 8.15 eight-year bed assignment.

Reference formula: Vajilia/DFLv2 commit
9c9254f3d11967e7d520db92ee98398f590f405b,
src/dfl/schedule_bed_rotation.py. This check intentionally derives expected
bed order without calling the tested Edition 8.15 implementation.
"""
from __future__ import annotations
import ed815_calendar as C

def independent_beds(year, divisions=tuple(range(1,9))):
    if type(year) is not int or year<1:
        raise ValueError("positive season required")
    offset=(year-1)%4
    swapped=((year-1)//4)%2
    return tuple(divisions[((bed//4)^swapped)*4+
                   (bed%4-offset)%4] for bed in range(8))

def main():
    for year in range(1,401):
        expected={club:i+1 for i,club in enumerate(independent_beds(year))}
        observed=C.bed_assignment(year)
        for i,division in enumerate(C.DIVISION_ORDER,1):
            if observed[division]!=expected[i]:
                raise AssertionError(f"year {year}, {division} bed mismatch")
    print("OK: 400 seasons × 8 divisions agree with independent DFLv2 rotation")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
