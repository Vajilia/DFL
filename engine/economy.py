"""Pay and the salary cap.

The Commissioner's rules (2026-10-05): the Diamond States have no inflation, so the DFL salary cap is $100 million and never changes. Unused cap
room is carried over and banked, but $125 million is the most a team may go into a season with; anything above that is forfeited to
the league for redistribution (the pool funds the exiled teams' cap relief, the 50% absorption in the rules). A payroll floor of about
90% of the cap keeps teams from hoarding. Money is a currency that forces decisions: it limits who a team can keep and who it can sign.

What is mine (PLACEHOLDER, every number a named dial below): the pay scale (what a player of a given rating and position is worth, with
a minimum and a ceiling at 20% of the cap), contract lengths, the rookie scale by draft pick, and the order in which a team spends.
Everything here is the autopilot's formula, "the road": a player's asking price is her market price and a team signs her if it can
afford her. Negotiation tables for the important deals (contract and trade tables, with the players' representative) come next and
will move a price inside a band around this one.

Rules in force with the autopilot:
  * a team's payroll is the sum of its players' salaries; it can never sign or re-sign anyone if that leaves it unable to fill the rest of
    its roster at the minimum salary within this season's limit (so the cap is a hard limit, never a suggestion);
  * this season's limit = min(125, 100 + the room it banked last season);
  * at the end of a season a team's unused room is banked up to $25 million; the excess goes to the pool; a team below the floor pays the
    shortfall to the pool and banks as if it had spent the floor;
  * an exiled team's payroll counts at half for the exile season (the 50% absorption), the league absorbing the other half;
  * a contract is a cap number a year (the base salary plus the year's share of the signing bonus, which is spread evenly over the contract,
    at most 5 years); some of the base is guaranteed (round-1 rookies in full, veterans for their first year); a released player's unspent
    bonus and guaranteed pay become dead money on the team's cap, all in the year she is let go, or split across this season and next for the
    two post-draft designations a team has each year;
  * in the offseason, until the cutdown, only the 51 highest cap numbers count (plus dead money); once the season starts everyone counts;
  * the payroll floor is measured over rolling windows of four seasons (an exile season is skipped, it has no floor); a team whose four-season
    total falls short pays the difference to its own players;
  * the pool is the Equalization Fund, a cash account: forfeited room goes in as dollars, the league's half of exiled teams' payrolls comes out,
    a deficit is covered equally by all 48 teams, and what stands above a reserve is paid out equally to the 40 playing teams.
"""
from __future__ import annotations

import math

import cards as C
import rules as _rules
from positions import ROSTER_SIZE

CAP = 100.0                  # $ millions, never inflates
BANK_LIMIT = 125.0           # the most a team may go into a season with
FLOOR_FRAC = 0.90            # payroll floor, as a share of the cap (about; the Commissioner agreed)
ABSORPTION = 0.5             # share of an exiled team's payroll the league absorbs for the exile season (rules text)

# the pay scale (PLACEHOLDER)
MIN_SALARY_SCALE = (0.29, 0.33, 0.36, 0.38, 0.40, 0.43)   # NFL 2026 minimums x 0.332, by credited seasons 0, 1, 2, 3, 4-6, 7+
MIN_SALARY = MIN_SALARY_SCALE[0]       # the lowest rung (a rookie): the least anyone can be paid
PRACTICE_SQUAD_SALARY = 0.10 # NFL 2025 weekly scale about $13-20k x 18 weeks x 0.332; counts against the cap like any contract
SQUAD_SIZE = ROSTER_SIZE + _rules.PRACTICE_SQUAD_SIZE     # everyone under contract to a team in a normal year
MAX_SALARY = 0.25 * CAP      # table limit (rulebook): no contract's yearly cap value above a quarter of the cap
PAY_SCALE = 12.5             # $ millions for a 90-rated player at a position with factor 1
PAY_POWER = 2.5              # how fast pay rises with rating (stars cost much more than starters)
POS_PAY = {"QB": 1.8, "RB": 0.8, "WR": 1.0, "TE": 0.8, "OL": 1.0, "DL": 1.2, "LB": 0.9, "CB": 1.1, "S": 0.9, "K": 0.35, "P": 0.3}
# The rookie scale by overall pick (NFL slot scale x 0.332, rulebook): pick 1 about $4.4M, $1.2M at the end of round 1, $0.65M at the end of round 2,
# $0.5M down to $0.3M through rounds 3 to 7; straight lines in the logarithm between the anchors
ROOKIE_SCALE = ((1, 4.4), (48, 1.2), (96, 0.65), (97, 0.50), (336, 0.30))
ROOKIE_YEARS, UNDRAFTED_YEARS = 4, 3
CONTRACT_YEARS_MAX = 5
BONUS_PRORATION_MAX_YEARS = 5   # a signing bonus is spread evenly over the contract, at most this many years
POST_DRAFT_DESIGNATIONS = 2     # releases a team a year whose dead money is split across this season and the next (NFL post-June-1)
OFFSEASON_COUNT = 51            # until the season begins, only the 51 highest cap numbers count
FLOOR_WINDOW_SEASONS = 4        # the floor is measured over rolling windows of this many seasons (exile seasons skipped)
EQUALIZATION_SURPLUS_TEAMS = 40 # the Fund's surplus is paid equally to the teams that play (not the 8 in exile)
# model dials (not league rules): how contracts are split into bonus and base, and the Fund's cash reserve
VETERAN_BONUS_SHARE = 0.25      # share of a veteran contract's yearly cap number that is signing bonus (contracts of 2+ years)
BONUS_MIN_SALARY = 1.0          # veterans below this cap number sign no bonus and have nothing guaranteed
ROOKIE_BONUS_SHARE = (0.50, 0.30, 0.10, 0.10, 0.10, 0.10, 0.10)   # by draft round
FUND_RESERVE = 100.0            # $ millions the Equalization Fund keeps before it pays a surplus
RESIGN_BASE = 0.45           # chance an expiring player reaches the market (stars half, a good negotiator GM lower): about 1 in 3 expire a year, so about 15% reach the market, as before
INIT_PAYROLL = (92.0, 99.5)  # where a founding team's payroll is put (contracts are scaled to it)


def min_salary(seasons: int) -> float:
    """The minimum salary by credited seasons (rungs for 0, 1, 2, 3, 4-6 and 7 or more)."""
    i = 0 if seasons <= 0 else seasons if seasons <= 3 else 4 if seasons <= 6 else 5
    return MIN_SALARY_SCALE[i]


def market_salary(pos: str, ovr: float, seasons: int = 0) -> float:
    x = max(0.0, (ovr - 40.0) / 50.0)
    return round(min(MAX_SALARY, min_salary(seasons) + PAY_SCALE * POS_PAY[pos] * x ** PAY_POWER), 2)


def rookie_salary(pick: int) -> float:
    """The scale salary for an overall pick, 1 to 336 (later picks are paid the last rung)."""
    pick = max(1, min(pick, ROOKIE_SCALE[-1][0]))
    for (p0, s0), (p1, s1) in zip(ROOKIE_SCALE, ROOKIE_SCALE[1:]):
        if p0 <= pick <= p1:
            if p1 == p0:
                return round(s0, 2)
            f = (pick - p0) / (p1 - p0)
            return round(math.exp(math.log(s0) + f * (math.log(s1) - math.log(s0))), 2)
    return round(ROOKIE_SCALE[-1][1], 2)


def contract_years(p) -> int:
    """How long a new contract runs: younger players and stars sign longer (a formula, no dice)."""
    base = 4 if p.age <= 25 else 3 if p.age <= 28 else 2 if p.age <= 31 else 1
    return base + (1 if p.ovr >= 70 else 0)


def payroll(t) -> float:
    """What counts against the cap this season: everyone under contract (the roster, the practice squad and injured reserve) plus dead money."""
    return round(sum(p.salary for p in t.roster) + sum(p.salary for p in t.practice_squad) + sum(p.salary for p in t.ir) + t.dead_now, 2)


OFFSEASON_RESERVE = (ROSTER_SIZE - OFFSEASON_COUNT) * MIN_SALARY + PRACTICE_SQUAD_SALARY * _rules.PRACTICE_SQUAD_SIZE
# what the 51 rule does not count but the season will: the 52nd and 53rd roster places and the practice squad, held back in every offseason test


def counted_51(salaries, dead: float = 0.0) -> float:
    """The offseason count of a list of cap numbers: the 51 highest, plus dead money."""
    return round(sum(sorted(salaries, reverse=True)[:OFFSEASON_COUNT]) + dead, 4)


def offseason_payroll(t) -> float:
    """What counts from the start of the league year until the season begins: only the 51 highest cap numbers, plus dead money."""
    top = sorted((p.salary for p in list(t.roster) + list(t.practice_squad) + list(t.ir)), reverse=True)[:OFFSEASON_COUNT]
    return round(sum(top) + t.dead_now, 2)


# ---- contracts: bonus, guarantees, dead money ----------------------------------------------------------------------------------------------------
def clear_contract(p):
    """A player with no contract (released, expired, on the market)."""
    p.salary, p.years_left, p.bonus, p.bonus_years, p.guaranteed = 0.0, 0, 0.0, 0, 0.0


def sign(p, salary: float, years: int, share=None, guarantee_years: int = 1, rookie: bool = False):
    """Put a contract on a player. `salary` is the yearly cap number. The signing bonus (a share of it, spread over the whole contract, at most
    5 years) and the base are its two parts; `guarantee_years` of the base are guaranteed (veterans one year, round-1 rookies all four).
    Contracts that are small or a single year carry no bonus and, for veterans, no guarantee."""
    years = max(1, min(CONTRACT_YEARS_MAX, int(years)))
    salary = round(min(MAX_SALARY, max(min_salary(p.credited_seasons), salary)), 2)
    big = salary >= BONUS_MIN_SALARY
    if share is None:
        share = VETERAN_BONUS_SHARE if (big and years >= 2) else 0.0
    if not 0.0 <= share <= 1.0:
        raise ValueError("bonus share must be between zero and one")
    p.salary, p.years_left = salary, years
    # The rookie scale is a cap number; bonus cannot consume the base minimum.
    p.bonus = round(min(salary * share, max(0.0, salary - min_salary(p.credited_seasons))), 4)
    p.bonus_years = min(years, BONUS_PRORATION_MAX_YEARS) if p.bonus > 0 else 0
    base = salary - p.bonus
    p.guaranteed = round(base * min(guarantee_years, years), 4) if (big or rookie) else 0.0


def enforce_minimum(p):
    """Raise next year's base pay to the earned credited-service floor.

    Applies to continuing roster contracts, never practice-squad wages. Existing
    bonus proration and guaranteed dollars remain unchanged. This changes cap
    cost, so the caller must run the usual cap/cutdown checks afterwards.
    """
    if p.years_left <= 0:
        return
    p.salary = round(max(p.salary, min_salary(p.credited_seasons) + p.bonus), 4)


def run_down(p):
    """One season of the contract is paid: a year of the bonus is spread out, the base for the year comes off what is guaranteed."""
    p.guaranteed = round(max(0.0, p.guaranteed - (p.salary - p.bonus)), 4)
    if p.bonus_years > 0:
        p.bonus_years -= 1
        if p.bonus_years == 0:
            p.bonus = 0.0
    p.years_left -= 1


def dead_charge(p) -> float:
    """What a team still owes if it lets this player go: the bonus not yet spread out and the pay still guaranteed."""
    return round(p.bonus * p.bonus_years + p.guaranteed, 4)


def release(t, p, designate: bool = False) -> float:
    """The team lets a player go: her salary leaves the payroll and her dead money lands on it, all this season, or (a post-draft designation) only
    this year's share of the bonus now and the rest next season. Returns what lands on this season's cap. The caller moves the player."""
    dead = dead_charge(p)
    now = min(dead, p.bonus) if designate else dead
    t.dead_now = round(t.dead_now + now, 4)
    t.dead_next = round(t.dead_next + (dead - now), 4)
    if designate:
        t.designations += 1
    clear_contract(p)
    return now


def can_designate(t) -> bool:
    return t.designations < POST_DRAFT_DESIGNATIONS


def new_year(t):
    """A new league year: last season's dead money is gone, what was pushed to this year is now due, and the designations are fresh."""
    t.dead_now, t.dead_next, t.designations = t.dead_next, 0.0, 0


def limit(t) -> float:
    """What this team may spend this season."""
    return min(BANK_LIMIT, CAP + t.bank)


def floor() -> float:
    return FLOOR_FRAC * CAP


def init_contracts(lg):
    """Contracts for a founding league: market prices, how long each has left drawn privately, then each team's payroll scaled into the
    legal range so every team begins inside the cap and above the floor."""
    lo, hi = INIT_PAYROLL
    for t in lg.teams:
        for p in t.roster:
            r = C._rng(lg.card_seed, "contract", p.id)
            p.salary = market_salary(p.pos, p.ovr, p.credited_seasons)
            p.years_left = r.randint(1, contract_years(p))
        raw = [p.salary for p in t.roster]
        minimums = [min_salary(p.credited_seasons) for p in t.roster]
        for p in t.practice_squad:
            clear_contract(p)
            p.salary, p.years_left = PRACTICE_SQUAD_SALARY, 1
        target = max(lo, min(hi, sum(raw))) - PRACTICE_SQUAD_SALARY * len(t.practice_squad)
        a, b = 0.0, 10.0                                  # scale so the payroll lands on target even after the minimum wage is applied
        for _ in range(60):
            k = (a + b) / 2
            if sum(max(floor, x * k) for x, floor in zip(raw, minimums)) < target:
                a = k
            else:
                b = k
        for p, x in zip(t.roster, raw):
            sal = max(min_salary(p.credited_seasons), round(x * a, 2))
            sign(p, sal, p.years_left)                        # the founding contracts have their bonus and guarantee like any other
            p.years_left = max(1, min(p.years_left, CONTRACT_YEARS_MAX))
        t.bank = 0.0
        t.dead_now = t.dead_next = 0.0
        t.designations = 0
        t.cash, t.topup, t.fund_cash = [], [], 0.0
    lg.pool = 0.0


def close_season(lg, returners, year: int) -> dict:
    """The season's accounts, before anything changes. Each team's unused room is banked (up to $25M) or forfeited. The floor is tested over the last
    four seasons the team played (an exile season is skipped): a team whose payrolls add up to less than four floors pays the difference to its own
    players. The league absorbs half of an exiled team's payroll. Forfeited room goes into the Equalization Fund as dollars and the absorption comes
    out of it; a deficit is covered equally by all 48 teams, and what stands above the reserve is paid equally to the teams that played."""
    ret = set(returners)
    forfeited = shortfall = absorbed = 0.0
    for t in lg.teams:
        pay = payroll(t)
        if t.id in ret:                                       # the exile season: the league absorbs half, and the floor does not apply (a 7-game season)
            eff = pay * (1.0 - ABSORPTION)
            absorbed += pay - eff
        else:
            eff = pay
            t.cash = (list(t.cash) + [pay])[-FLOOR_WINDOW_SEASONS:]
            t.topup = (list(t.topup) + [0.0])[-FLOOR_WINDOW_SEASONS:]
            if len(t.cash) >= FLOOR_WINDOW_SEASONS:
                short = FLOOR_WINDOW_SEASONS * floor() - sum(t.cash) - sum(t.topup)
                if short > 1e-9:
                    t.topup[-1] = round(t.topup[-1] + short, 4)
                    shortfall += short
        unused = max(0.0, limit(t) - eff)
        t.bank = min(BANK_LIMIT - CAP, unused)
        forfeited += max(0.0, unused - (BANK_LIMIT - CAP))
    lg.pool += forfeited - absorbed
    levy = payout = 0.0
    if lg.pool < 0.0:                                         # the Fund is short: all 48 teams cover it equally
        levy = -lg.pool
        for t in lg.teams:
            t.fund_cash -= levy / len(lg.teams)
        lg.pool = 0.0
    elif lg.pool > FUND_RESERVE:                              # above the reserve is a surplus: the teams that played split it equally
        playing = [t for t in lg.teams if t.id not in ret]
        payout = lg.pool - FUND_RESERVE
        for t in playing:
            t.fund_cash += payout / len(playing)
        lg.pool = FUND_RESERVE
    rec = dict(year=year, forfeited=round(forfeited, 2), shortfall=round(shortfall, 2), absorbed=round(absorbed, 2), levy=round(levy, 2),
               payout=round(payout, 2), pool=round(lg.pool, 2),
               payroll_mean=round(sum(payroll(t) for t in lg.teams) / len(lg.teams), 2),
               dead_mean=round(sum(t.dead_now for t in lg.teams) / len(lg.teams), 2),
               banked=round(sum(t.bank for t in lg.teams), 2))
    return rec
