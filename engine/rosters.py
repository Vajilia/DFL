"""The roster lists: the 90-man camp, the 53-man roster, the 48 active on game day, the practice squad and injured reserve.

Rulebook (rosters section, NFL, kept for exiled teams too): 90 in camp, cut to 53; only 48 of the 53 may be active on game day; a practice
squad of 16; up to 8 players a team a season may be designated to return from injured reserve, after at least 4 games; the practice squad
takes rookies and second-year players, plus at most 6 players with more seasons.

Everything here is the autopilot's "road": the lists, the limits and the weekly bookkeeping are code, and the choices inside them (who is
inactive, who goes on injured reserve, who is promoted) follow plain formulas by rating and need. When agents choose, they choose among
what these functions allow.

Known simplifications (the rulebook rows say so): practice-squad
players are not elevated to game day for single games; an exiled team's injured reserve works on the same calendar as everyone's.
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional

import economy as EC
import rules as R
from players import Player, clamp, make_player
from positions import ACTIVE_MINIMUMS, POSITIONS, ROSTER_COUNTS, ROSTER_SIZE


# ---- who is on which list --------------------------------------------------------------------------------------------------
def squad(t) -> List[Player]:
    """Everyone under contract to the team: the 53, the practice squad and injured reserve."""
    return list(t.roster or ()) + list(t.practice_squad) + list(t.ir)


def counts(players) -> Dict[str, int]:
    c = {pos: 0 for pos in POSITIONS}
    for p in players:
        c[p.pos] += 1
    return c


def active_list(t) -> List[Player]:
    """Game day: at most 48 healthy players from the 53. Healthy players beyond 48 are inactive: the weakest ones, but never below the
    position minimums (ACTIVE_MINIMUMS), so a team never leaves out the only kicker or a third of its line."""
    healthy = [p for p in t.roster if p.weeks_out == 0]
    surplus = len(healthy) - R.ACTIVE_LIMIT
    if surplus <= 0:
        return healthy
    droppable = []
    for pos in POSITIONS:
        at = sorted((p for p in healthy if p.pos == pos), key=lambda p: -p.ovr)
        droppable.extend(at[ACTIVE_MINIMUMS[pos]:])
    droppable.sort(key=lambda p: (p.ovr, p.id))
    out = {p.id for p in droppable[:surplus]}
    return [p for p in healthy if p.id not in out]


def game_roster(t) -> List[Player]:
    """What the depth chart is built from: the active players, then the injured (who fill in only if too few are healthy)."""
    return active_list(t) + [p for p in t.roster if p.weeks_out > 0]


# ---- the practice squad -----------------------------------------------------------------------------------------------------
def seasons_of(p: Player) -> int:
    """Earned accrued seasons, with the one-time legacy estimate on old saves."""
    return p.accrued_seasons


def ps_rookie_slot(p: Player) -> bool:
    return seasons_of(p) <= R.PRACTICE_SQUAD_SEASONS


def veterans_on_squad(players) -> int:
    return sum(1 for p in players if not ps_rookie_slot(p))


def choose_practice_squad(cands: List[Player], have: Optional[List[Player]] = None, size: int = None) -> List[Player]:
    """The best candidates (by rating, younger first on a tie) that the rule allows: rookies and second-year players freely, at most
    PRACTICE_SQUAD_VETERANS_MAX with more seasons. Returns the players to add to `have` to fill the squad."""
    have = list(have or ())
    size = R.PRACTICE_SQUAD_SIZE if size is None else size
    vets = veterans_on_squad(have)
    out = []
    for p in sorted(cands, key=lambda p: (-(p.ovr + 0.3 * (26 - p.age)), p.id)):
        if len(have) + len(out) >= size:
            break
        if ps_rookie_slot(p):
            out.append(p)
        elif vets < R.PRACTICE_SQUAD_VETERANS_MAX:
            vets += 1
            out.append(p)
    return out


def to_practice_squad(p: Player):
    """A player signed to (or kept on) the practice squad is on the practice-squad contract for the season."""
    EC.clear_contract(p)
    p.salary, p.years_left = EC.PRACTICE_SQUAD_SALARY, 1


def street_player(lg, rng: random.Random, pos: str, young: bool = False) -> Player:
    """No one on the market at that position: a street free agent, as the offseason has always signed (a minimum-salary body)."""
    age = rng.choice((22, 23, 24)) if young else rng.choice((23, 24, 25, 26))
    p = make_player(rng, lg.new_id(), pos, clamp(rng.gauss(46.0, 5.0), 28, 70), age, None)
    p.years_in_league = max(0, age - 22)
    # A generated street player has no documented prior qualifying games.
    p.accrued_seasons = p.credited_seasons = 0
    return p


def best_free_agent(lg, pos: Optional[str] = None, eligible=None) -> Optional[Player]:
    best = None
    for q in lg.free_agents:
        if q.retired or (pos is not None and q.pos != pos) or (eligible is not None and not eligible(q)):
            continue
        if best is None or q.ovr > best.ovr:
            best = q
    return best


# ---- the weekly bookkeeping: injured reserve, promotions, returns ----------------------------------------------------------
def _release(lg, t, p: Player):
    t.roster.remove(p)
    EC.release(t, p)
    p.team_id, p.fa_years = None, 0
    lg.free_agents.append(p)


def _weakest_surplus(t) -> Player:
    """Who is released to make room: the weakest healthy player at a position that has more than its table count, else the weakest
    healthy player who is not the last kicker, punter or quarterback."""
    c = counts(t.roster)
    pool = [p for p in t.roster if p.weeks_out == 0 and c[p.pos] > ROSTER_COUNTS[p.pos]]
    if not pool:
        pool = [p for p in t.roster if p.weeks_out == 0 and c[p.pos] > ACTIVE_MINIMUMS[p.pos]]
    if not pool:
        pool = [p for p in t.roster if p.weeks_out == 0] or list(t.roster)
    return min(pool, key=lambda p: (p.ovr, -p.id))


def fill_roster(lg, t, rng: random.Random, log: Optional[dict] = None):
    """Back to 53 after someone went on injured reserve: promote the best practice-squad player at the position that is short, else sign the
    best free agent at that position, else a street player, at the minimum. Then refill the practice squad."""
    while len(t.roster) < ROSTER_SIZE:
        c = counts(t.roster)
        short = sorted(POSITIONS, key=lambda pos: c[pos] - ROSTER_COUNTS[pos])
        pos = short[0]
        at = [p for p in t.practice_squad if p.pos == pos]
        if at:                                              # the best on the practice squad at that position
            pick = max(at, key=lambda p: (p.ovr, -p.id))
            t.practice_squad.remove(pick)
        else:                                               # else the best free agent at that position, else a street player: never someone from another position
            pick = best_free_agent(lg, pos)
            if pick is not None:
                lg.free_agents.remove(pick)
                if log is not None:
                    log["signed"] = log.get("signed", 0) + 1
            else:
                pick = street_player(lg, rng, pos)
        pick.team_id = t.id
        t.roster.append(pick)
        EC.sign(pick, EC.min_salary(pick.credited_seasons), 1)
        if log is not None and at:
            log["promoted"] = log.get("promoted", 0) + 1
    refill_practice_squad(lg, t, rng)


def refill_practice_squad(lg, t, rng: random.Random):
    while len(t.practice_squad) < R.PRACTICE_SQUAD_SIZE:
        cands = [q for q in lg.free_agents if not q.retired and (ps_rookie_slot(q) or veterans_on_squad(t.practice_squad) < R.PRACTICE_SQUAD_VETERANS_MAX)]
        add = choose_practice_squad(cands, t.practice_squad, len(t.practice_squad) + 1)
        if add:
            p = add[0]
            lg.free_agents.remove(p)
        else:
            p = street_player(lg, rng, rng.choices(POSITIONS, [ROSTER_COUNTS[x] for x in POSITIONS])[0], young=True)
        p.team_id = t.id
        to_practice_squad(p)
        t.practice_squad.append(p)


def manage_week(lg, rng: random.Random, weeks_left: int, wire=None) -> dict:
    """Called at the end of each regular-season week, after the injuries have ticked. For every team: players who have healed and are
    allowed back return from injured reserve (the weakest surplus player is released to make room), players newly out for 4 or more
    games go on injured reserve (designated to return if they could come back this season and the team still has a return left;
    otherwise only if the season is over for them), and the roster is filled back to 53.

    With a waiver `wire` (transactions.Wire), a released player who is subject to waivers goes on the wire instead of straight to free agency; the wire is
    settled once every club's injured reserve is done and before any club fills its open places, so a claim can take the place of a signing."""
    import transactions as T
    log = {"ir_placed": 0, "ir_returned": 0, "promoted": 0, "signed": 0}
    for t in lg.teams:
        for p in t.ir:
            p.ir_games += 1
        back = sorted((p for p in t.ir if p.ir_designated and p.weeks_out == 0 and p.ir_games >= R.IR_MIN_GAMES), key=lambda p: -p.ovr)
        for p in back:
            t.ir.remove(p)
            t.roster.append(p)                              # she is back first; then the weakest surplus player at a position over its table count goes
            p.ir_games, p.ir_designated = 0, False
            log["ir_returned"] += 1
            if len(t.roster) > ROSTER_SIZE:
                out = _weakest_surplus(t)
                if wire is not None and T.subject_to_waivers(out, wire.week):
                    T.waive(lg, t, out, wire)
                else:
                    _release(lg, t, out)
        hurt = sorted((p for p in t.roster if p.weeks_out >= R.IR_MIN_GAMES), key=lambda p: -p.ovr)
        for p in hurt:
            season_ending = p.weeks_out >= weeks_left
            if season_ending or t.ir_returns < R.IR_RETURNS_MAX:
                t.roster.remove(p)
                t.ir.append(p)
                p.ir_games = 0
                p.ir_designated = not season_ending
                if p.ir_designated:
                    t.ir_returns += 1
                log["ir_placed"] += 1
    if wire is not None:
        T.resolve(lg, wire)
        log["waived"], log["claimed"] = wire.waived, wire.claimed
    # a player who is out for the season and can never return this year does not need a designation; one who has been on injured
    # reserve and is healed but was not designated stays there until the offseason
    for t in lg.teams:
        if len(t.roster) < ROSTER_SIZE:
            fill_roster(lg, t, rng, log)
    return log
