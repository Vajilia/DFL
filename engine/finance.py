"""Club finance (Step 7): revenue, surplus, the CEO's draw, subsidies and what the fans think of the spending.

The Commissioner's skeleton: an owner is a CEO with a 10 to 20 year tenure; her personal draw is capped at $100 million a year and anything
above the cap goes to the Equalization Fund; subsidies to weaker clubs come out of CEOs' draws; each fanbase card stands for 1,000,000 fans
and has a say in how the club spends. Everything else here is MODEL (a named dial below), in the same dollars as the cap ($100M, no inflation).

Two rules keep money off the field:
  * the cap does not change. Nothing here moves a player's pay, a club's limit, its bank or its floor (economy.py owns those), and a club's reserve
    can only cover its own losses;
  * nothing here draws from the game's random stream (no random numbers at all), and the only thing finance moves in the league's people is a
    small, capped nudge to an owner's approval, applied after the season's votes.

One year, in order (`close_books`, called after the season's cap accounts close and before the owners' review):
  1. revenue: an equal share of the league's national money, plus local money that grows with the market, the fans' passion and the team's
     success (a title and a playoff run pay extra); an exiled club earns a fraction of the local money (its Ambassador Season is short) and
     half the national share;
  2. expenses: the payroll the club carried (the league absorbs half of an exiled club's) plus fixed operating costs;
  3. the Fund: a club pays its share of a levy and receives its share of a payout (the Fund's cash is real, economy.close_season);
  4. surplus = revenue - expenses + Fund payout - levy. The CEO reinvests a share of any profit in the club (spent), sets a little aside in the
     reserve, and takes the rest as her draw, up to the cap; the excess above the cap goes to the Fund. A loss comes out of the reserve first, then from subsidies, then from her pocket;
  5. subsidy: CEOs with a taste for it (the owner card's subsidy pressure) pay part of their draw into a pool that covers the losses of clubs
     the reserve cannot, pro rata to what each CEO is willing to give;
  6. the fans: they compare what the club invested (the reserve share plus any subsidy given) with what a million fans expect, and a maximum draw
     from a club that is losing annoys them. The result is one capped number added to approval next year.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import economy as EC
import cards as C
import rules as R

# ---- the Commissioner's rules (SKELETON) ------------------------------------------------------------------------------------
DRAW_CAP = 100.0                  # a CEO's personal draw never exceeds this in a year ($ millions); the excess goes to the Equalization Fund
TENURE_MIN, TENURE_MAX = 10, 20   # a CEO's tenure in years, drawn when she is seated
FANS_PER_CARD = 1_000_000         # one fanbase card is a million fans

# ---- model dials (MODEL: every number is mine, to be tuned) -------------------------------------------------------------------
NATIONAL_POOL = 130.0             # each club's equal share of the league's national money
LOCAL_BASE = 85.0                 # local money of a market-50 club with average fans and a .500 team
LOCAL_MARKET = (0.40, 1.20)       # local money scales from LOCAL_MARKET[0] + LOCAL_MARKET[1] x market / 100 (market 5 pays 0.46, market 95 pays 1.54 of base)
LOCAL_PASSION = 0.30              # a 100-passion fanbase pays this much more local money than a 50 (a 1: this much less)
LOCAL_SUCCESS = 0.45              # local money rises by this x (win% - .5) x 2 (a perfect year +45%, a winless one -45%)
PLAYOFF_BONUS, TITLE_BONUS = 4.0, 8.0     # extra revenue for a playoff team and for the champion ($ millions)
OPERATING_COST = 45.0             # non-player costs (staff, stadium, travel)
EXILE_LOCAL_SHARE = 0.35          # an exiled club earns this share of its local money (short Ambassador Season) ...
EXILE_NATIONAL_SHARE = 0.50       # ... and this share of the national pool
REINVEST_BASE, REINVEST_AMBITION = 0.05, 0.25   # share of a profit the CEO puts back into the club: 5% plus up to 25% for a 100-ambition CEO
RESERVE_SHARE = 0.10              # share of a profit the CEO sets aside in the club's reserve (a rainy-day fund; reinvested money, by contrast, is spent)
RESERVE_MAX = 40.0                # a club's reserve stops growing here (the rest of the profit is drawn)
SUBSIDY_SHARE = 0.20              # a 100-subsidy-pressure CEO is willing to give up to this share of her draw (a 1: about none)
FAN_WANT = (4.0, 0.06, 0.04)     # what a million fans expect the club to invest each year: 10 + 0.15 x passion + 0.10 x expectations ($ millions)
FAN_NORM = 0.80                   # fans are content when the club invests this share of what they want
FAN_SPEND_WEIGHT = 0.02           # the most the investment can move approval in a year (before the draw-while-losing hit)
FAN_GREED_HIT = 0.01              # approval lost when a CEO takes (nearly) the maximum draw from a club that wins under 40%
GREED_DRAW_SHARE, GREED_WIN_PCT = 0.80, 0.40
TICKET_SHARE_OF_LOCAL = 0.50     # share of a club's local money that is ticket revenue (the rest: concessions, sponsors, merchandise)
SALE_YES_BASE = 0.40              # chance another CEO votes to force a sale ...
SALE_YES_PAYER = 0.25             # ... plus this if she paid subsidy this year ...
SALE_YES_PRESSURE = 0.30          # ... minus this x (her subsidy pressure / 100 - 0.5): a CEO who likes subsidising is slower to cast a club out
BOOKS_YEARS = 4                   # years of accounts a club keeps (the floor looks back four seasons too)


def draw_tenure(rng_card) -> int:
    """A CEO's tenure, drawn from her card's private generator."""
    return rng_card.randint(TENURE_MIN, TENURE_MAX)


def revenue(team, pct: float, playoffs: bool, champion: bool, exiled: bool) -> Dict[str, float]:
    fb = team.fans
    market = fb.market if fb is not None else 50.0
    passion = fb.ratings["passion"] if fb is not None else 50.0
    scale = LOCAL_MARKET[0] + LOCAL_MARKET[1] * market / 100.0
    scale *= 1.0 + LOCAL_PASSION * (passion - 50.0) / 50.0
    scale *= 1.0 + LOCAL_SUCCESS * (pct - 0.5) * 2.0
    local = LOCAL_BASE * scale + (PLAYOFF_BONUS if playoffs else 0.0) + (TITLE_BONUS if champion else 0.0)
    national = NATIONAL_POOL
    if exiled:
        local *= EXILE_LOCAL_SHARE
        national *= EXILE_NATIONAL_SHARE
    return dict(national=national, local=local)


def fan_want(team) -> float:
    fb = team.fans
    passion = fb.ratings["passion"] if fb is not None else 50.0
    expect = fb.ratings["expectations"] if fb is not None else 50.0
    return FAN_WANT[0] + FAN_WANT[1] * passion + FAN_WANT[2] * expect


def reinvest_share(owner) -> float:
    ambition = owner.ratings["ambition"] if owner is not None else 50.0
    return REINVEST_BASE + REINVEST_AMBITION * ambition / 100.0


def subsidy_willing(owner, draw: float) -> float:
    pressure = owner.pressure.get("subsidy", 50) if owner is not None else 50
    return max(0.0, draw) * SUBSIDY_SHARE * pressure / 100.0


def close_books(lg, year: int, pct: Dict[int, float], playoff_teams, champion: int, returners, cap_rec: dict) -> dict:
    """Close every club's books for the season. `cap_rec` is economy.close_season's record (its levy and payout are real cash). Returns the league
    record (totals, the Fund's inflow from draws, subsidies, and each club's line) and sets `lg.pool`, each team's reserve and books, and
    `lg.finance_nudge` (team id -> (owner id, approval nudge)) for the caller to apply after the votes."""
    ret = set(returners)
    teams = lg.teams
    playing = [t for t in teams if t.id not in ret]
    levy_each = cap_rec.get("levy", 0.0) / len(teams)
    payout_each = cap_rec.get("payout", 0.0) / max(1, len(playing))
    lines: Dict[int, dict] = {}
    revs = {t.id: revenue(t, pct.get(t.id, 0.5), t.id in playoff_teams, t.id == champion, t.id in ret) for t in teams}
    ticket_pool = R.TICKET_POOL_SHARE * sum(TICKET_SHARE_OF_LOCAL * r["local"] for r in revs.values())      # 34% of every club's tickets, shared equally
    pool_share = ticket_pool / len(teams)
    for t in teams:
        exiled = t.id in ret
        rev = dict(revs[t.id])
        out_t = R.TICKET_POOL_SHARE * TICKET_SHARE_OF_LOCAL * rev["local"]
        rev["local"] = rev["local"] - out_t + pool_share
        pay = EC.payroll(t) * ((1.0 - EC.ABSORPTION) if exiled else 1.0)
        fund = (0.0 if exiled else payout_each) - levy_each
        surplus = rev["national"] + rev["local"] - pay - OPERATING_COST + fund
        lines[t.id] = dict(team=t.id, year=year, exiled=exiled, national=round(rev["national"], 2), local=round(rev["local"], 2),
                           ticket_pool_in=round(pool_share, 2), ticket_pool_out=round(out_t, 2), payroll=round(pay, 2),
                           operating=OPERATING_COST, fund=round(fund, 2), surplus=round(surplus, 2))
    # profits: the reserve share, then the draw, capped; losses: the reserve first
    need: Dict[int, float] = {}
    willing: Dict[int, float] = {}
    to_fund = 0.0
    for t in teams:
        ln = lines[t.id]
        o = t.owner
        s = ln["surplus"]
        reserve = t.reserve
        if s >= 0.0:
            spent = s * reinvest_share(o)                                  # reinvested: stadium, community, staff; gone, but the fans see it
            saved = min(s * RESERVE_SHARE, max(0.0, RESERVE_MAX - reserve))
            reserve += saved
            keep = spent
            avail = s - spent - saved
            draw = min(DRAW_CAP, avail)
            excess = avail - draw
            to_fund += excess
            ln.update(reinvested=round(keep, 2), draw=round(draw, 2), to_fund=round(excess, 2), loss=0.0)
            willing[t.id] = subsidy_willing(o, draw)
        else:
            loss = -s
            covered = min(reserve, loss)
            reserve -= covered
            ln.update(reinvested=0.0, draw=0.0, to_fund=0.0, loss=round(loss, 2), covered_by_reserve=round(covered, 2))
            if loss - covered > 1e-9:
                need[t.id] = loss - covered
        t.reserve = reserve
    # subsidies: willing CEOs pay pro rata to what they offered, up to the losses the reserves could not cover
    total_need = sum(need.values())
    total_willing = sum(willing.values())
    paid = min(total_need, total_willing)
    given: Dict[int, float] = {}
    if paid > 1e-9:
        for tid, w in willing.items():
            amt = paid * w / total_willing
            if amt > 1e-9:
                given[tid] = amt
                lines[tid]["subsidy_paid"] = round(amt, 2)
                lines[tid]["draw"] = round(lines[tid]["draw"] - amt, 2)
        for tid, n in need.items():
            got = paid * n / total_need
            lines[tid]["subsidy_received"] = round(got, 2)
    for t in teams:
        lines[t.id]["sub_quarters"] = 0
    for tid, n in need.items():
        got = paid * n / total_need if total_need > 1e-9 else 0.0
        loss = lines[tid]["loss"]
        lines[tid]["sub_quarters"] = min(R.FISCAL_QUARTERS, int(-(-R.FISCAL_QUARTERS * got // loss))) if got > 1e-9 and loss > 0 else 0
        lines[tid]["own_pocket"] = round(n - got, 2)
        lines[tid]["draw"] = round(-(n - got), 2)       # a negative draw: the CEO puts her own money in
    lg.pool += to_fund
    # the fans: investment against what a million fans want, and the greed hit
    nudge: Dict[int, tuple] = {}
    for t in teams:
        ln = lines[t.id]
        want = fan_want(t)
        invested = ln["reinvested"] + given.get(t.id, 0.0)
        ratio = invested / want if want > 0 else FAN_NORM
        n = FAN_SPEND_WEIGHT * max(-1.0, min(1.0, ratio / FAN_NORM - 1.0))
        if ln["draw"] >= GREED_DRAW_SHARE * DRAW_CAP and pct.get(t.id, 0.5) < GREED_WIN_PCT:
            n -= FAN_GREED_HIT
        ln.update(want=round(want, 2), invested=round(invested, 2), nudge=round(n, 4))
        if t.owner is not None:
            nudge[t.id] = (t.owner.oid, n)
            t.owner.draws = round(getattr(t.owner, "draws", 0.0) + max(0.0, ln["draw"]), 2)
        t.books = (list(t.books) + [ln])[-BOOKS_YEARS:]
    lg.finance_nudge = nudge
    import staff_cards as SC
    SC.log(lg, year, "finance_close", to_fund=round(to_fund, 4), subsidy=round(paid, 4), draw_total=round(sum(max(0.0, l["draw"]) for l in lines.values()), 2))
    rec = dict(year=year, revenue_mean=round(sum(l["national"] + l["local"] for l in lines.values()) / len(teams), 2),
               surplus_mean=round(sum(l["surplus"] for l in lines.values()) / len(teams), 2),
               draw_total=round(sum(max(0.0, l["draw"]) for l in lines.values()), 2),
               draws_at_cap=sum(1 for l in lines.values() if l["draw"] >= DRAW_CAP - 1e-9),
               to_fund=round(to_fund, 2), subsidy=round(paid, 2), clubs_in_loss=sum(1 for l in lines.values() if l["loss"] > 0),
               own_pocket=round(sum(l.get("own_pocket", 0.0) for l in lines.values()), 2), pool=round(lg.pool, 2), lines=lines)
    return rec


def forced_sales(lg, year: int, rec: dict) -> List[int]:
    """Rulebook (Skeleton): a club subsidised in R.FORCED_SALE_SUBSIDY_QUARTERS or more quarters of a rolling four has its owner forced to sell if
    R.FORCED_SALE_VOTES_NEEDED of the 48 owners vote for it (the owner concerned is recused, so 47 vote). A year's loss is spread over four equal
    quarters and the subsidy covers the later ones, so a club's subsidised quarters are the share of its loss that other CEOs paid (rounded up).
    Gap: the window is the one season, not a true rolling four quarters. Returns the teams whose owner was forced out."""
    import staff_cards as SC
    sold = []
    lines = rec["lines"]
    for tid in sorted(lines):
        ln = lines[tid]
        if ln.get("sub_quarters", 0) < R.FORCED_SALE_SUBSIDY_QUARTERS:
            continue
        t = lg.by_id[tid]
        o = t.owner
        if o is None:
            continue
        yes = 0
        for v in lg.teams:
            if v.id == tid or v.owner is None:
                continue
            payer = lines[v.id].get("subsidy_paid", 0.0) > 0
            p = SALE_YES_BASE + (SALE_YES_PAYER if payer else 0.0) - SALE_YES_PRESSURE * (v.owner.pressure.get("subsidy", 50) / 100.0 - 0.5)
            if C._rng(lg.card_seed, "forcedsale", o.oid, year, v.owner.oid).random() < max(0.0, min(1.0, p)):
                yes += 1
        passed = yes >= R.FORCED_SALE_VOTES_NEEDED
        SC.log(lg, year, "forced_sale_vote", team=tid, owner=o.name, subsidised_quarters=ln["sub_quarters"], yes=yes, result="sold" if passed else "kept")
        ln.update(sale_votes=yes, sale_result="sold" if passed else "kept")
        if passed:
            o.status = "sold"
            o.career.append({"year": year, "event": "forced_sale", "team": tid, "votes": yes})
            SC._seat_owner(lg, t, year, new_owner=True, age=None)
            if t.fans is not None:
                t.fans.approval = t.owner.approval
            sold.append(tid)
    return sold


def apply_nudges(lg) -> int:
    """After the owners' review: each club's approval nudge goes to the owner who earned it, if she is still the owner."""
    n = 0
    nudge = getattr(lg, "finance_nudge", None) or {}
    for tid, (oid, d) in nudge.items():
        t = lg.by_id[tid]
        o = t.owner
        if o is None or o.oid != oid:
            continue
        o.approval = max(0.0, min(1.0, o.approval + d))
        if t.fans is not None:
            t.fans.approval = o.approval
        n += 1
    lg.finance_nudge = {}
    return n
