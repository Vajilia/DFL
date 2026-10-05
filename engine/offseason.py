"""The roster offseason: aging, retirement, contracts ending, the draft and free agency.

Everything here is ASSUMED structure with PLACEHOLDER numbers (see roster_model.py). The one
confirmed design intent it serves: a team coming back from exile gets modest help (priority in
free agency plus a few top-of-market signings, standing in for the 50% cap relief) so it has the
potential to compete for about 3rd in its division.
"""
from __future__ import annotations

import math
import random
from typing import Dict, List

import rules as R
from league import League, refresh_strengths
from players import Player, clamp, make_player, random_age
from positions import POSITIONS, ROSTER_COUNTS, ROSTER_SIZE, STARTERS
from roster_model import RosterModel
import economy as EC
import staff_cards as SC

# Years of aging offset by position: quarterbacks, kickers and punters last longer.
AGE_SHIFT = {"QB": 2, "K": 5, "P": 5, "RB": -1}
# mean yearly change in overall rating by (shifted) age
def _age_drift(age: int) -> float:
    if age <= 23:
        return 3.0
    if age <= 25:
        return 1.8
    if age <= 27:
        return 0.6
    if age <= 29:
        return -0.6
    if age <= 31:
        return -1.8
    if age <= 33:
        return -3.2
    return -4.5


def _retire_prob(p: Player) -> float:
    a = p.age - AGE_SHIFT.get(p.pos, 0)
    base = {31: 0.05, 32: 0.10, 33: 0.20, 34: 0.35}.get(a, 0.60 if a >= 35 else 0.0)
    if a >= 28 and p.ovr < 45:
        base += 0.15
    return min(base, 0.95)


def progress(players: List[Player], rm: RosterModel, rng: random.Random, coach_of: Dict[int, object] = None):
    """Everyone ages and changes. `coach_of` maps a player id to the head coach she developed under this year
    (cards.development_bonus). Afterwards each player's ratings are pulled back toward the shape her soul gives her
    (cards.apply_soul). Neither step draws random numbers, so the random stream is the same with or without cards."""
    import cards
    for p in players:
        p.age += 1
        p.years_in_league += 1
        shift = _age_drift(p.age - AGE_SHIFT.get(p.pos, 0)) + rng.gauss(0.0, rm.prog_noise)
        if coach_of:
            shift += cards.development_bonus(coach_of.get(p.id), p.age)
        for a in p.ratings:
            p.ratings[a] = clamp(p.ratings[a] + shift + rng.gauss(0.0, rm.prog_attr_noise))
        p.recompute()
        cards.apply_soul(p)


def rookie_ovr(pick: int, rm: RosterModel, rng: random.Random) -> float:
    return clamp(rm.rookie_base + rm.rookie_span * math.exp(-(pick - 1) / rm.rookie_decay)
                 + rng.gauss(0.0, rm.rookie_sd), 30, 95)


def _team_counts(roster: List[Player]) -> Dict[str, int]:
    c = {p: 0 for p in POSITIONS}
    for pl in roster:
        c[pl.pos] += 1
    return c


def _pick_rookie_position(roster: List[Player], rng: random.Random) -> str:
    counts = _team_counts(roster)
    w = []
    for pos in POSITIONS:
        need = ROSTER_COUNTS[pos] - counts[pos]
        if pos in ("K", "P"):
            w.append(1.0 if need > 0 else 0.02)
        else:
            w.append(max(0.15, need + 0.4) * ROSTER_COUNTS[pos])
    return rng.choices(POSITIONS, w)[0]


def _slot_floor(roster: List[Player], pos: str) -> float:
    """Overall of the weakest starter at a position (what a newcomer has to beat to start)."""
    at = sorted((p.ovr for p in roster if p.pos == pos), reverse=True)
    n = STARTERS[pos]
    return at[n - 1] if len(at) >= n else 45.0


def _quick_strength(roster: List[Player]) -> float:
    """Average overall of the starters (a missing starter counts as 40). Used only to order free agency,
    when rosters have holes and the full power rating cannot be built yet."""
    tot, n = 0.0, 0
    for pos in POSITIONS:
        at = sorted((p.ovr for p in roster if p.pos == pos), reverse=True)[:STARTERS[pos]]
        at += [40.0] * (STARTERS[pos] - len(at))
        tot += sum(at)
        n += STARTERS[pos]
    return tot / n


def _gain(roster: List[Player], cand: Player) -> float:
    n = STARTERS[cand.pos]
    floor = _slot_floor(roster, cand.pos)
    if cand.ovr > floor:                                  # would start
        return (cand.ovr - floor) * (1.0 + 0.4 * n) + 5.0
    return cand.ovr - 60.0                                # depth only: small and negative


def _undrafted(lg: League, rm: RosterModel, rng: random.Random) -> List[Player]:
    out = []
    tot = sum(ROSTER_COUNTS.values())
    for _ in range(rm.undrafted_per_year):
        pos = rng.choices(POSITIONS, [ROSTER_COUNTS[p] for p in POSITIONS])[0]
        ovr = clamp(rng.gauss(rm.undrafted_mean, rm.undrafted_sd), 28, 80)
        out.append(make_player(rng, lg.new_id(), pos, ovr, rng.choice((22, 22, 23, 24)), None))
    return out


def run_roster_offseason(lg: League, rng: random.Random, rm: RosterModel, year: int,
                         pick_of: Dict[int, int], returners: List[int]) -> dict:
    """Update every roster for next season. `pick_of` maps team id -> draft pick (1-48);
    `returners` are the teams coming back from exile. Returns a small log of what happened."""
    log = dict(retired=0, expired=0, signed=0, premium=0, released=0, rookies=0, street=0, resigned=0, cap_blocked=0, cap_cuts=0)
    log["cap"] = EC.close_season(lg, returners, year)       # this season's accounts, before anything changes
    SC.log(lg, year, "cap_close", **{k: v for k, v in log["cap"].items() if k != "year"})
    teams = lg.teams
    # injuries heal over the offseason
    for t in teams:
        for p in t.roster:
            p.weeks_out = 0
    for p in lg.free_agents:
        p.weeks_out = 0

    # 1. everybody ages and changes
    progress([p for t in teams for p in t.roster], rm, rng,
             {p.id: t.coach for t in teams if t.coach is not None for p in t.roster})
    progress(lg.free_agents, rm, rng)

    # 2. retirement (rostered players and the unsigned)
    for t in teams:
        keep = []
        for p in t.roster:
            if rng.random() < _retire_prob(p):
                p.retired, p.team_id = True, None
                log["retired"] += 1
            else:
                keep.append(p)
        t.roster = keep
    pool: List[Player] = []
    for p in lg.free_agents:
        p.fa_years += 1
        if rng.random() < _retire_prob(p) or p.fa_years > 2:
            p.retired = True
            log["retired"] += 1
        else:
            pool.append(p)

    # 3. contracts run down. Players whose contracts end are re-signed (at today's market price) or reach the market: stars are likelier to
    # be kept and a good negotiator GM keeps more, but a team can only keep who it can afford this season (the cap is a hard limit)
    for t in teams:
        for p in t.roster:
            p.years_left -= 1
        keep = [p for p in t.roster if p.years_left > 0]
        expiring = sorted((p for p in t.roster if p.years_left <= 0), key=lambda p: -p.ovr)
        lim, committed = EC.limit(t), sum(p.salary for p in keep)
        rookie = EC.rookie_salary(pick_of[t.id])
        for p in expiring:
            q = EC.RESIGN_BASE * (rm.fa_star_protect if p.ovr >= 70 else 1.0) * SC.gm_retention_factor(t)
            wants = rng.random() >= q
            cost = EC.market_salary(p.pos, p.ovr)
            slots_after = max(0, ROSTER_SIZE - (len(keep) + 1) - 1)          # the rest of the roster and the rookie still to come
            if wants and committed + cost + rookie + slots_after * EC.MIN_SALARY <= lim:
                p.salary, p.years_left = cost, EC.contract_years(p)
                keep.append(p)
                committed += cost
                log["resigned"] += 1
            else:
                if wants:
                    log["cap_blocked"] += 1
                p.team_id, p.fa_years = None, 0
                p.salary = p.years_left = 0
                pool.append(p)
                log["expired"] += 1
        t.roster = keep
    pool.extend(_undrafted(lg, rm, rng))

    # 4. the draft: one rookie per team, quality by pick
    for t in teams:
        pick = pick_of[t.id]
        pos = _pick_rookie_position(t.roster, rng)
        p = make_player(rng, lg.new_id(), pos, clamp(rookie_ovr(pick, rm, rng) + SC.gm_scouting_bonus(t), 30, 95), rng.choice((22, 22, 22, 23)), t.id,
                        draft_year=year, draft_pick=pick)
        p.years_in_league = 0
        p.salary, p.years_left = EC.rookie_salary(pick), EC.ROOKIE_YEARS
        t.roster.append(p)
        log["rookies"] += 1
    # trim positions that are over the limit (the weakest are released to the market)
    for t in teams:
        for pos in POSITIONS:
            at = sorted((p for p in t.roster if p.pos == pos), key=lambda p: -p.ovr)
            for p in at[ROSTER_COUNTS[pos]:]:
                t.roster.remove(p)
                p.team_id, p.fa_years = None, 0
                pool.append(p)
                log["released"] += 1

    # 4b. cap casualties. Banked room is a one-season allowance: a team that spent it on multi-year contracts comes back to the $100M cap and must
    # shed the players who cost the most beyond their market price until it can fill its roster at the minimum wage inside its limit
    for t in teams:
        while EC.payroll(t) + max(0, ROSTER_SIZE - len(t.roster)) * EC.MIN_SALARY > EC.limit(t) + 1e-9:
            w = max(t.roster, key=lambda p: (p.salary - EC.market_salary(p.pos, p.ovr), p.id))
            t.roster.remove(w)
            w.team_id, w.fa_years = None, 0
            pool.append(w)
            log["cap_cuts"] += 1

    # 5. free agency, worst team first. Returning teams go first and get premium signings.
    ret = set(returners)
    quick = {t.id: _quick_strength(t.roster) for t in teams}
    order = sorted(teams, key=lambda t: (0 if (t.id in ret and rm.exile_fa_priority) else 1, quick[t.id] + rng.gauss(0.0, rm.fa_priority_noise)))
    by_pos: Dict[str, List[Player]] = {pos: [] for pos in POSITIONS}
    for p in pool:
        by_pos[p.pos].append(p)
    for pos in POSITIONS:
        by_pos[pos].sort(key=lambda p: -p.ovr)

    def room_for(t) -> float:
        """What this team can pay the next signing: this season's limit less its payroll, keeping the minimum salary back for every other open slot."""
        return EC.limit(t) - EC.payroll(t) - max(0, ROSTER_SIZE - len(t.roster) - 1) * EC.MIN_SALARY

    def take(t, p, price=None):
        by_pos[p.pos].remove(p)
        p.team_id, p.fa_years = t.id, 0
        p.salary = EC.market_salary(p.pos, p.ovr) if price is None else price
        p.years_left = EC.contract_years(p)
        t.roster.append(p)
        log["signed"] += 1

    def affordable(t, pos):
        """The best player on the market at a position that this team can afford (an asking price is the market price)."""
        room = room_for(t)
        for c in by_pos[pos]:
            if EC.market_salary(c.pos, c.ovr) <= room:
                return c
        return None

    def release_worst(t, pos):
        at = sorted((p for p in t.roster if p.pos == pos), key=lambda p: p.ovr)
        w = at[0]
        t.roster.remove(w)
        w.team_id, w.fa_years = None, 0
        by_pos[pos].append(w)
        by_pos[pos].sort(key=lambda p: -p.ovr)
        log["released"] += 1

    # 5a. premium signings for returners (stand-in for the 50% cap relief)
    for t in order:
        if t.id not in ret:
            continue
        n = int(rm.exile_premium_signings) + (1 if rng.random() < rm.exile_premium_signings % 1 else 0)
        for _ in range(n):
            best, best_gain = None, 0.0
            for pos in POSITIONS:
                c = affordable(t, pos)
                if c is None:
                    continue
                g = _gain(t.roster, c)
                if g > best_gain:
                    best, best_gain = c, g
            if best is None:
                break
            take(t, best)
            log["premium"] += 1
            counts = _team_counts(t.roster)
            if counts[best.pos] > ROSTER_COUNTS[best.pos]:
                release_worst(t, best.pos)

    # 5b. fill every open slot, round by round
    while True:
        progressed = False
        for t in order:
            counts = _team_counts(t.roster)
            open_pos = [pos for pos in POSITIONS if counts[pos] < ROSTER_COUNTS[pos]]
            if not open_pos:
                continue
            best, best_gain = None, -1e9
            for pos in open_pos:
                c = affordable(t, pos)
                if c is None:
                    continue
                g = _gain(t.roster, c)
                if g > best_gain:
                    best, best_gain = c, g
            price = None
            if best is None:                                # no one on the market at an open position that the team can afford: a street free agent at the minimum
                pos = open_pos[0]
                best = make_player(rng, lg.new_id(), pos, clamp(rng.gauss(46.0, 5.0), 28, 70),
                                   rng.choice((22, 23, 24)), None)
                by_pos[pos].append(best)
                price = EC.MIN_SALARY
                log["street"] += 1
            take(t, best, price)
            progressed = True
        if not progressed:
            break

    lg.free_agents = [p for pos in POSITIONS for p in by_pos[pos]]
    for t in teams:
        assert len(t.roster) == sum(ROSTER_COUNTS.values()), (t.id, len(t.roster))
    refresh_strengths(lg)
    return log
