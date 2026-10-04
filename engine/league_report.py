"""Plain-language report on a multi-season run.

    python engine/league_report.py --seed 1 --seasons 20
"""
import argparse
import os
import random
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R  # noqa: E402
import placeholder_model as PM  # noqa: E402
from draft import run_lottery  # noqa: E402
from season import Options  # noqa: E402
from run_sim import simulate  # noqa: E402

NAME = lambda tid: f"Team {tid:02d}"
CRITERION_WORDS = {
    "head_to_head": "head-to-head record",
    "division_record": "division record",
    "point_differential": "point differential",
    "seeded_coin_flip": "a coin flip",
}


def build_report(seed: int, seasons: int) -> str:
    league, results = simulate(seed, seasons)
    L = []
    w = L.append
    w(f"# DFL trial run: {seasons} seasons (seed {seed})\n")
    w("This is the league running by itself with **no characters and no AI**. Game scores come from placeholder ratings "
      "(see `engine/placeholder_model.py`), so team names are placeholders and results show how the *machinery* behaves, "
      "not what the real league will feel like. Every season's schedule passed the full rule check.\n")

    # champions
    w("## Champions\n")
    w("| Year | Champion | Record | Conference | Went into the year as |")
    w("| --- | --- | --- | --- | --- |")
    titles = Counter()
    for r in results:
        c = r.champion
        titles[c] += 1
        tier = r.start[c][1]
        w(f"| {r.year} | {NAME(c)} | {r.stats[c].record} | {R.CONFERENCES[(c - 1) // 24]} | Tier {tier} |")
    most = titles.most_common(3)
    w(f"\n{len(titles)} different teams won the title in {seasons} seasons. Most titles: "
      + ", ".join(f"{NAME(t)} ({n})" for t, n in most) + ".\n")
    repeat = sum(1 for a, b in zip(results, results[1:]) if a.champion == b.champion)
    w(f"Back-to-back champions: {repeat}.\n")

    # parity
    best = [max(s.wins for s in r.stats.values()) for r in results]
    worst = [min(s.wins for s in r.stats.values()) for r in results]
    spread = [statistics.pstdev([r.start[t][2] for t, (st, _, _) in r.start.items() if st == "active"]) for r in results]
    w("## How even is the league?\n")
    w(f"The best regular-season record each year averaged {statistics.mean(best):.1f}-{18 - statistics.mean(best):.1f} "
      f"(range {min(best)} to {max(best)} wins). The worst averaged {statistics.mean(worst):.1f}-{18 - statistics.mean(worst):.1f} "
      f"(range {min(worst)} to {max(worst)} wins).\n")
    w(f"The gap between strong and weak teams (standard deviation of the placeholder ratings) stayed between "
      f"{min(spread):.1f} and {max(spread):.1f} points, so the league neither collapsed into a few powers nor went completely flat.\n")

    # exile
    w("## Exile\n")
    ex_counts = Counter()
    for r in results:
        ex_counts.update(r.new_exiles)
    never = [t for t in range(1, 49) if ex_counts[t] == 0]
    w(f"Eight teams are exiled every year, one per division. Across {seasons} years that is {8 * seasons} exiles. "
      f"Most exiles for one team: {', '.join(f'{NAME(t)} ({n})' for t, n in ex_counts.most_common(3))}. "
      + (f"{len(never)} of the 48 teams were never exiled." if never else "Every one of the 48 teams was exiled at least once.") + "\n")
    again = 0
    returns = 0
    for i, r in enumerate(results[:-3]):
        for t in r.new_exiles:
            returns += 1
            if any(t in results[i + k].new_exiles for k in (2, 3)):
                again += 1
    if returns:
        w(f"After an exile, a team came back as Tier 5. {again} of {returns} ({100 * again / returns:.0f}%) were exiled again "
          f"within two seasons of coming back.\n")
    w("| Year | Exiled for the next season |")
    w("| --- | --- |")
    for r in results:
        w(f"| {r.year} | {', '.join(str(t) for t in sorted(r.new_exiles))} |")
    w("")

    # ties for 5th
    tied = 0
    deciders = Counter()
    divisions = 0
    for r in results:
        for d, ranks in r.division_ranks.items():
            divisions += 1
            five = ranks[4]
            recs = [x for x in r.tiebreak_log if x["context"] == "division" and five in x["teams"]]
            if recs:
                tied += 1
                deciders[recs[-1]["decided_by"]] += 1
    w("## Ties for 5th place (which now means exile)\n")
    w(f"The exile spot needed a tiebreaker in {tied} of {divisions} division-seasons ({100 * tied / divisions:.0f}%). "
      "What finally settled it: " + (", ".join(f"{CRITERION_WORDS[k]} ({v})" for k, v in deciders.most_common()) or "nothing needed") + ". "
      "The tiebreaker order is an assumption, so this tells you how often it will matter.\n")

    # lottery
    w("## The lottery\n")
    pool_names = {"just_finished_fifth": "the 8 teams that just finished 5th"}
    w(f"The lottery covers {pool_names.get(R.LOTTERY_POOL, R.LOTTERY_POOL)}, with weights "
      f"{' / '.join(str(x) for x in R.LOTTERY_WEIGHTS)} (placeholder). ")
    got_first = Counter()
    avg_pick = defaultdict(list)
    for r in results:
        pick_of = {t: p for p, t, _ in r.draft}
        for idx, t in enumerate(r.lottery_pool_order):
            avg_pick[idx].append(pick_of[t])
        got_first[r.lottery_pool_order.index(next(t for p, t, _ in r.draft if p == 1))] += 1
    exp = defaultdict(float)
    lot_rng = random.Random(0)
    N = 20000
    for _ in range(N):
        for pick, idx in enumerate(run_lottery(list(range(8)), R.LOTTERY_WEIGHTS, lot_rng), start=1):
            exp[idx] += pick / N
    w(f"The worst-record team won pick 1 in {got_first[0]} of {seasons} years; the best-record team of the eight won it "
      f"{got_first[7]} times. Average pick by record, worst to best: "
      + ", ".join(f"{statistics.mean(avg_pick[i]):.1f}" for i in range(8))
      + f" in this run, and {', '.join(f'{exp[i]:.1f}' for i in range(8))} expected over many lotteries. "
      "With these weights the worst team's edge over the best is only about two picks on average.\n")

    # recall
    votes = [len(r.recall_votes) for r in results]
    w("## Owner recall workload (for the AI budget)\n")
    same = min(votes) == max(votes)
    w(f"Each year one division's owners come up for a vote (6 teams), and each exiled team's owner also faces one. "
      f"That is {'exactly ' + str(votes[0]) if same else format(statistics.mean(votes), '.1f') + ' on average (range ' + str(min(votes)) + ' to ' + str(max(votes)) + ')'} owner votes a year. "
      f"At 5 replacement candidates per vote that is at most about {5 * round(statistics.mean(votes))} generated owner cards a year, "
      f"if every recall succeeds.\n")

    # does tier predict success? (bigger sample), with and without the exile benefits
    def tier_table(opt):
        rows = defaultdict(lambda: [0, 0, 0, 0])      # tier -> team-seasons, wins, playoffs, titles
        for sd in range(40):
            _, big = simulate(5000 + sd, 30, opt)
            for r in big[5:]:
                for t, st in r.stats.items():
                    row = rows[r.start[t][1]]
                    row[0] += 1
                    row[1] += st.wins
                    row[2] += t in r.exits
                    row[3] += r.champion == t
        return rows

    def write_tier_table(rows):
        w("| Tier | Average wins | Made the playoffs | Won the title |")
        w("| --- | --- | --- | --- |")
        for tier in sorted(rows):
            n, wi, po, ti = rows[tier]
            w(f"| {tier} | {wi / n:.1f} | {100 * po / n:.0f}% | {100 * ti / n:.1f}% |")

    w("## Does a team's tier predict how it does?\n")
    w("Over 40 separate leagues of 25 seasons each (1,000 seasons), by the tier a team started the year in. "
      "Tier 5 is where exiled teams return.\n")
    w("**With the placeholder exile benefits** (top-8 lottery pick plus cap relief):\n")
    write_tier_table(tier_table(Options(validate_schedule=False)))
    w("\n**With the exile benefits switched off** (no draft value for anyone, no cap relief). "
      "What remains is the easier Tier 5 schedule and the fact that the weakest teams get exiled:\n")
    off = PM.Model(draft_pick1_value=0.0, exile_return_bonus=0.0)
    write_tier_table(tier_table(Options(model=off, validate_schedule=False)))
    w("\nA league built as the rules text describes (\"the 1s battle the 1s, the 5s fight to avoid the bottom\") would show "
      "Tier 1 clearly ahead and Tier 5 clearly behind. Anything else means exile is working as a reward or a reset rather than "
      "a punishment. How steep the slope is depends on placeholder numbers, so treat it as a dial to tune later.\n")

    w("## What this run can and cannot tell you\n")
    w("It shows the rules interlock: the right 8 teams are exiled, return as Tier 5, draft in the right order and so on. "
      "It cannot say whether games feel right, because scores here are simple ratings plus noise. "
      "Nothing here involves characters, money or the Archive yet.\n")
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seasons", type=int, default=20)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    text = build_report(a.seed, a.seasons)
    path = os.path.join(a.out, f"league_summary_seed{a.seed}.md")
    with open(path, "w") as f:
        f.write(text + "\n")
    print("wrote", path)
