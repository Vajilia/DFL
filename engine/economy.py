"""Pay and the salary cap.

Jeph's rules (2026-10-05): the Diamond States have no inflation, so the DFL salary cap is $100 million and never changes. Unused cap
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
  * released players take their salary with them (no dead money yet; a known simplification).
"""
from __future__ import annotations

import math

import cards as C
from positions import ROSTER_SIZE

CAP = 100.0                  # $ millions, never inflates
BANK_LIMIT = 125.0           # the most a team may go into a season with
FLOOR_FRAC = 0.90            # payroll floor, as a share of the cap (about; Jeph agreed)
ABSORPTION = 0.5             # share of an exiled team's payroll the league absorbs for the exile season (rules text)

# the pay scale (PLACEHOLDER)
MIN_SALARY = 0.75
MAX_SALARY = 0.20 * CAP      # no one costs more than a fifth of the cap
PAY_SCALE = 12.5             # $ millions for a 90-rated player at a position with factor 1
PAY_POWER = 2.5              # how fast pay rises with rating (stars cost much more than starters)
POS_PAY = {"QB": 1.8, "RB": 0.8, "WR": 1.0, "TE": 0.8, "OL": 1.0, "DL": 1.2, "LB": 0.9, "CB": 1.1, "S": 0.9, "K": 0.35, "P": 0.3}
ROOKIE_TOP, ROOKIE_BOTTOM, ROOKIE_DECAY = 4.0, 0.9, 10.0     # the rookie scale by draft pick, a fixed scale like a wage scale
ROOKIE_YEARS, UNDRAFTED_YEARS = 4, 2
RESIGN_BASE = 0.45           # chance an expiring player reaches the market (stars half, a good negotiator GM lower): about 1 in 3 expire a year, so about 15% reach the market, as before
INIT_PAYROLL = (92.0, 99.5)  # where a founding team's payroll is put (contracts are scaled to it)


def market_salary(pos: str, ovr: float) -> float:
    x = max(0.0, (ovr - 40.0) / 50.0)
    return round(min(MAX_SALARY, MIN_SALARY + PAY_SCALE * POS_PAY[pos] * x ** PAY_POWER), 2)


def rookie_salary(pick: int) -> float:
    return round(ROOKIE_BOTTOM + (ROOKIE_TOP - ROOKIE_BOTTOM) * math.exp(-(pick - 1) / ROOKIE_DECAY), 2)


def contract_years(p) -> int:
    """How long a new contract runs: younger players and stars sign longer (a formula, no dice)."""
    base = 4 if p.age <= 25 else 3 if p.age <= 28 else 2 if p.age <= 31 else 1
    return base + (1 if p.ovr >= 70 else 0)


def payroll(t) -> float:
    return round(sum(p.salary for p in t.roster), 2)


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
            p.salary = market_salary(p.pos, p.ovr)
            p.years_left = r.randint(1, contract_years(p))
        raw = [p.salary for p in t.roster]
        target = max(lo, min(hi, sum(raw)))
        a, b = 0.0, 10.0                                  # scale so the payroll lands on target even after the minimum wage is applied
        for _ in range(60):
            k = (a + b) / 2
            if sum(max(MIN_SALARY, x * k) for x in raw) < target:
                a = k
            else:
                b = k
        for p, x in zip(t.roster, raw):
            p.salary = max(MIN_SALARY, round(x * a, 2))
        t.bank = 0.0
    lg.pool = 0.0


def close_season(lg, returners, year: int) -> dict:
    """The season's accounts, before anything changes: each team's unused room is banked (up to $25M) or forfeited, a team below the floor pays
    the shortfall, and the league absorbs half of an exiled team's payroll. Everything forfeited or paid goes into the pool, which funds the
    absorption; the pool's balance is kept so the study can say how much of the relief it covers."""
    ret = set(returners)
    forfeited = shortfall = absorbed = 0.0
    for t in lg.teams:
        pay = payroll(t)
        if t.id in ret:                                       # the exile season: the league absorbs half, and the floor does not apply (a 7-game season)
            counted = pay * (1.0 - ABSORPTION)
            absorbed += pay - counted
            eff = counted
        else:
            counted = pay
            eff = max(counted, floor())
            shortfall += eff - counted
        unused = max(0.0, limit(t) - eff)
        t.bank = min(BANK_LIMIT - CAP, unused)
        forfeited += max(0.0, unused - (BANK_LIMIT - CAP))
    lg.pool += forfeited + shortfall - absorbed
    rec = dict(year=year, forfeited=round(forfeited, 2), shortfall=round(shortfall, 2), absorbed=round(absorbed, 2), pool=round(lg.pool, 2),
               payroll_mean=round(sum(payroll(t) for t in lg.teams) / len(lg.teams), 2),
               banked=round(sum(t.bank for t in lg.teams), 2))
    return rec
