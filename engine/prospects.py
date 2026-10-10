"""The draft class and where every player came from (stage 1 of the character creator).

Before each draft the league builds this year's class as a table of rows, one per prospect, ranked on the consensus board. A row is a real
`Player` who is on no roster yet. She has a position, an age, her true ratings, and an `origin`: the college she played for (real programs of the
kind the NFL draws from), her date of birth, her hometown and four seasons of college statistics. The statistics are derived from her
*production grade*, which is her true rating plus the scouting noise every real prospect carries, so a scout reading the stat lines sees the
production, never the truth.

The board is the draft's source of players. The draft picks from it:

  * The rule (the autopilot's answer) takes the best player on the consensus board, tilted toward the positions the club needs (the same
    need weights the engine has always used, now applied to a walk down the board). Nothing about the league's talent changes: the class is built
    from the same rookie curve (`offseason.rookie_ovr`), sorted, so the rating of the n-th best prospect is what the n-th pick has always been.
  * A GM (gm_roster.draft_pick) is shown the rule's prospect and the best alternate on her board, as she sees them through her eye for talent.

Only the winners of a pick keep a row. Her origin travels with her (Player.origin) and her card (cards.py) takes her hometown and date of birth
from it. Players who never came through a draft (the founding rosters, street players, undrafted free agents) get an origin lazily the first time
anything needs one (`ensure_origin`), built from their rating the same way.

Nothing here draws from the engine's random stream except the class itself (ratings, positions, ages), which is the draft's own draw; the
origin comes from private streams seeded by the league's card seed and the player's id, so a league's results do not depend on whether anyone ever
looks at a prospect's college.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

import card_pools as CP
import cards as C
from players import clamp, make_player
from positions import POSITIONS, ROSTER_COUNTS

# ---- dials (placeholders, not rules) -----------------------------------------------------------------------------------------------------
GRADE_SD = 4.0                    # the scouting noise on a prospect: her production grade is her true rating plus this (sd)
PROD_FLOOR_RANK = 120             # kickers and punters appear in the class only below this consensus rank (as in the NFL, where they go late)
CALENDAR_BASE = 2025               # league year 1 is the 2026 season: a date of birth is a real calendar date
SEASONS = ("FR", "SO", "JR", "SR")
GAMES = (11, 12, 12, 13)

# (program, tier): tier 1 = a power-conference program, 2 = a mid-major, 3 = a small-college or FCS program the NFL still scouts
COLLEGES = [
    ("Alabama", 1), ("Georgia", 1), ("Ohio State", 1), ("Michigan", 1), ("Clemson", 1), ("LSU", 1), ("Oklahoma", 1), ("Texas", 1),
    ("Notre Dame", 1), ("Penn State", 1), ("Florida", 1), ("Florida State", 1), ("Oregon", 1), ("USC", 1), ("Washington", 1),
    ("Tennessee", 1), ("Auburn", 1), ("Texas A&M", 1), ("Wisconsin", 1), ("Iowa", 1), ("Miami (FL)", 1), ("Utah", 1), ("Ole Miss", 1),
    ("Arkansas", 1), ("Kentucky", 1), ("South Carolina", 1), ("Missouri", 1), ("Oklahoma State", 1), ("Baylor", 1), ("TCU", 1),
    ("Nebraska", 1), ("Michigan State", 1), ("Minnesota", 1), ("North Carolina", 1), ("NC State", 1), ("Virginia Tech", 1),
    ("Pittsburgh", 1), ("Louisville", 1), ("Stanford", 1), ("UCLA", 1), ("Arizona State", 1), ("Colorado", 1), ("West Virginia", 1),
    ("Kansas State", 1), ("Mississippi State", 1), ("Illinois", 1), ("Purdue", 1), ("Maryland", 1), ("Cal", 1), ("Duke", 1),
    ("Boise State", 2), ("Cincinnati", 2), ("UCF", 2), ("Houston", 2), ("Memphis", 2), ("SMU", 2), ("Tulane", 2), ("Appalachian State", 2),
    ("Coastal Carolina", 2), ("Fresno State", 2), ("San Diego State", 2), ("Toledo", 2), ("Western Michigan", 2), ("Liberty", 2),
    ("Marshall", 2), ("Troy", 2), ("Utah State", 2), ("Wyoming", 2), ("Air Force", 2), ("Navy", 2), ("UNLV", 2), ("Louisiana", 2),
    ("Georgia Southern", 2), ("Northern Illinois", 2), ("Ohio", 2), ("Buffalo", 2), ("Old Dominion", 2), ("James Madison", 2),
    ("North Dakota State", 3), ("Montana", 3), ("Eastern Washington", 3), ("Villanova", 3), ("Delaware", 3), ("Sam Houston", 3),
    ("Jackson State", 3), ("Grambling State", 3), ("Florida A&M", 3), ("South Dakota State", 3), ("Furman", 3), ("Princeton", 3),
    ("Harvard", 3), ("Youngstown State", 3), ("Weber State", 3), ("Southern Utah", 3), ("Hampton", 3), ("Morehouse", 3),
]
_BY_TIER = {t: [c for c, tt in COLLEGES if tt == t] for t in (1, 2, 3)}


def _tier_weights(grade: float):
    if grade >= 70:
        return (0.80, 0.17, 0.03)
    if grade >= 55:
        return (0.55, 0.33, 0.12)
    return (0.35, 0.40, 0.25)


# ---- college statistics, derived from the production grade ----------------------------------------------------------------------------------
def _n(r, mean: float) -> int:
    """A count around `mean` with a little more than Poisson spread."""
    return max(0, int(round(r.gauss(mean, math.sqrt(max(mean, 1.0)) * 0.7))))


def _scale(grade: float) -> float:
    """How much she produced relative to a standout: 0.05 (a bench player) to 1.3 (an all-conference season)."""
    return max(0.05, min(1.3, (grade - 35.0) / 45.0))


def _season(pos: str, m: float, g: int, r) -> Dict[str, float]:
    if pos == "QB":
        att = _n(r, g * (10 + 22 * m))
        pct = clamp(0.50 + 0.14 * m + r.gauss(0, 0.02), 0.40, 0.78)
        cmp_ = int(att * pct)
        return dict(att=att, cmp=cmp_, yds=int(cmp_ * (10.0 + 3.0 * m + r.gauss(0, 0.6))), td=_n(r, att * (0.018 + 0.04 * m)),
                    ints=_n(r, att * (0.036 - 0.015 * m)), rush_yds=_n(r, g * (3 + 9 * r.random())))
    if pos == "RB":
        att = _n(r, g * (4 + 16 * m))
        return dict(att=att, yds=int(att * (3.6 + 1.7 * m + r.gauss(0, 0.25))), td=_n(r, att * (0.025 + 0.02 * m)), rec=_n(r, g * (0.4 + 2.6 * m)))
    if pos in ("WR", "TE"):
        rec = _n(r, g * ((1.2 + 5.2 * m) if pos == "WR" else (0.6 + 3.4 * m)))
        return dict(rec=rec, yds=int(rec * ((10.5 + 5 * m) if pos == "WR" else (9.0 + 4 * m)) + r.gauss(0, 20)), td=_n(r, rec * (0.04 + 0.06 * m)))
    if pos == "OL":
        return dict(starts=g if m > 0.45 else _n(r, g * m), sacks_allowed=_n(r, g * max(0.05, 0.9 - 0.7 * min(m, 1.0))), pancakes=_n(r, g * (0.8 + 2.6 * m)))
    if pos == "DL":
        return dict(tkl=_n(r, g * (1.5 + 3.0 * m)), tfl=_n(r, g * (0.2 + 0.9 * m)), sacks=_n(r, g * (0.1 + 0.6 * m)))
    if pos == "LB":
        return dict(tkl=_n(r, g * (3.0 + 5.0 * m)), tfl=_n(r, g * (0.3 + 0.9 * m)), sacks=_n(r, g * (0.05 + 0.4 * m)), ints=_n(r, g * 0.05 * m * 2))
    if pos == "CB":
        return dict(tkl=_n(r, g * (1.5 + 2.0 * m)), ints=_n(r, g * (0.03 + 0.22 * m)), pd=_n(r, g * (0.2 + 0.8 * m)))
    if pos == "S":
        return dict(tkl=_n(r, g * (2.5 + 3.0 * m)), ints=_n(r, g * (0.03 + 0.2 * m)), pd=_n(r, g * (0.2 + 0.6 * m)))
    if pos == "K":
        att = _n(r, g * (1.0 + 1.2 * m))
        return dict(fg_att=att, fg_made=int(att * clamp(0.62 + 0.28 * m + r.gauss(0, 0.04), 0.4, 1.0)), long=int(38 + 16 * m + r.gauss(0, 2)))
    return dict(punts=_n(r, g * (4.0 + 1.0 * m)), avg=round(38.0 + 8.0 * m + r.gauss(0, 0.8), 1), inside20=_n(r, g * (1.2 + 1.6 * m)))   # P


def _college_stats(seed: int, p, grade: float) -> List[dict]:
    r = C._rng(seed, "college", p.id)
    out = []
    for k, (label, g) in enumerate(zip(SEASONS, GAMES)):
        m = _scale(grade) * (0.55, 0.8, 0.95, 1.0)[k] * (0.85 + 0.30 * r.random())
        row = dict(class_year=label, games=g)
        row.update(_season(p.pos, m, g, r))
        out.append(row)
    return out


def stat_line(pos: str, row: dict) -> str:
    """One season in plain words, for a decision screen or a profile."""
    if pos == "QB":
        return f"{row['cmp']}/{row['att']}, {row['yds']} yds, {row['td']} TD, {row['ints']} INT"
    if pos == "RB":
        return f"{row['att']} att, {row['yds']} yds, {row['td']} TD, {row['rec']} rec"
    if pos in ("WR", "TE"):
        return f"{row['rec']} rec, {row['yds']} yds, {row['td']} TD"
    if pos == "OL":
        return f"{row['starts']} starts, {row['sacks_allowed']} sacks allowed, {row['pancakes']} pancakes"
    if pos == "DL":
        return f"{row['tkl']} tkl, {row['tfl']} TFL, {row['sacks']} sacks"
    if pos == "LB":
        return f"{row['tkl']} tkl, {row['tfl']} TFL, {row['sacks']} sacks, {row['ints']} INT"
    if pos in ("CB", "S"):
        return f"{row['tkl']} tkl, {row['ints']} INT, {row['pd']} PD"
    if pos == "K":
        return f"{row['fg_made']}/{row['fg_att']} FG, long {row['long']}"
    return f"{row['punts']} punts, {row['avg']} avg, {row['inside20']} inside the 20"


# ---- one person's origin -------------------------------------------------------------------------------------------------------------------
def make_origin(seed: int, p, year: int, class_rank: Optional[int] = None, grade: Optional[float] = None) -> dict:
    """College, date of birth, hometown and four college seasons for player `p` in league year `year` (the year she turns pro, or the year her card
    is made for a player who never came through a draft here). All from private streams."""
    r = C._rng(seed, "origin", p.id)
    if grade is None:
        grade = round(p.ovr + r.gauss(0.0, GRADE_SD), 1)
    tier = r.choices((1, 2, 3), _tier_weights(grade))[0]
    college = r.choice(_BY_TIER[tier])
    hometown = r.choice(CP.HOMETOWNS)
    born = CALENDAR_BASE + year - p.age                  # her birth year: the calendar year of the season she turns pro (or has her card made) less her age then
    dob = f"{born:04d}-{r.randint(1, 12):02d}-{r.randint(1, 28):02d}"
    o = dict(college=college, tier=tier, hometown=hometown, dob=dob, grade=round(grade, 1), stats=_college_stats(seed, p, grade))
    if class_rank is not None:
        o["class_rank"] = class_rank
    return o


def ensure_origin(seed: int, p, year: int) -> dict:
    if not p.origin:
        p.origin = make_origin(seed, p, year)
    return p.origin


def career_line(p) -> str:
    st = p.origin.get("stats") or []
    if not st:
        return ""
    last = st[-1]
    return f"{p.origin['college']}, senior year: {stat_line(p.pos, last)}"


# ---- the class -----------------------------------------------------------------------------------------------------------------------------------
def build_class(lg, rm, rng, year: int, n: int) -> List:
    """This year's draft class: `n` prospects on the consensus board, best first. The prospect on the board at rank k is rated as the k-th pick always has
    been (`rookie_ovr`, curve and spread), so the autopilot's draft leaves the league's talent where it was. Her production grade (what the stat lines
    say) is her true rating plus scouting noise, so the board and the stat lines disagree a little, and a scout reading either can be wrong."""
    import offseason as OFF
    weights = [float(ROSTER_COUNTS[x]) for x in POSITIONS]
    rows = []
    for i in range(n):
        ovr = OFF.rookie_ovr(i + 1, rm, rng)
        w = [0.0 if (x in ("K", "P") and i < PROD_FLOOR_RANK) else wi for x, wi in zip(POSITIONS, weights)]
        pos = rng.choices(POSITIONS, w)[0]
        p = make_player(rng, lg.new_id(), pos, ovr, rng.choice((22, 22, 22, 23)), None, draft_year=year)
        p.years_in_league = 0
        p.accrued_seasons = p.credited_seasons = 0
        rows.append(p)
    for i, p in enumerate(rows):                           # the scouting noise on each one, from a private stream (so it never touches the engine's)
        p.origin = make_origin(lg.card_seed, p, year, class_rank=i + 1)
    return rows


def best_available(board: List, pick_weight, rng, reach: float) -> object:
    """The rule's pick: walk down the consensus board and take each prospect with probability pick_weight(prospect) / reach, so the best player at a
    position the club needs goes before a better one it does not."""
    for p in board:
        if rng.random() < min(1.0, pick_weight(p) / reach):
            return p
    return board[0]
