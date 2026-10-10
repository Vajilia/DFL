"""Writes reports/draft_board_sample.md: one draft class as the table it is, and a few player pages rendered from their cards.

    python engine/prospect_report.py [--seed 33] [--seasons 3]
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enrichment as EN  # noqa: E402
import prospects as PR  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=33)
    ap.add_argument("--seasons", type=int, default=3)
    a = ap.parse_args()
    seen = {}
    build = PR.build_class

    def spy(lg, rm, rng, year, n):
        rows = build(lg, rm, rng, year, n)
        seen["rows"], seen["year"] = list(rows), year
        return rows

    PR.build_class = spy
    r = random.Random(a.seed)
    lg = new_league(r, rosters=True)
    for y in range(1, a.seasons + 1):
        run_season(lg, y, r, Options(engine="fast", keep_boxes=False))
    PR.build_class = build
    rows, year = seen["rows"], seen["year"]
    taken = {p.id: p for t in lg.teams for p in list(t.roster) + list(t.practice_squad) + list(t.ir)}
    taken.update({p.id: p for p in lg.free_agents})
    import cards as C
    out = [f"# A draft class, as the table it is\n",
           f"Seed {a.seed}, the class of year {year}: {len(rows)} prospects, one row per pick. Names come from the placeholder word lists; the colleges are real programs the NFL draws from. "
           "The *grade* is what the stat lines say (true rating plus scouting noise); the true rating is not shown to a GM. The first 40 rows and a sample of later ones follow.\n",
           "| Rank | Name | Pos | Age | Born | College | Hometown | Grade | Senior year | Taken |", "|---|---|---|---|---|---|---|---|---|---|"]
    show = rows[:40] + rows[120::20]
    for p in show:
        o = p.origin
        name = C.make_name(lg.card_seed, p.id)
        who = taken.get(p.id)
        pick = f"pick {p.draft_pick}, {lg.by_id[p.team_id].name}" if p.draft_pick and p.team_id in lg.by_id else (f"pick {p.draft_pick}" if p.draft_pick else "")
        out.append(f"| {o['class_rank']} | {name[0]} {name[1]} | {p.pos} | {p.age} | {o['dob']} | {o['college']} | {o['hometown']} | {o['grade']:.0f} | {PR.stat_line(p.pos, o['stats'][-1])} | {pick} |")
    out.append("\n## Player pages rendered from the card\n")
    firsts = [taken[p.id] for p in rows[:3] if p.id in taken and taken[p.id].card is not None]
    for p in firsts:
        EN.ensure_bio(lg, p, year)
        out.append(EN.profile(lg, p, year) + "\n")
    path = os.path.join(ROOT, "reports", "draft_board_sample.md")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
