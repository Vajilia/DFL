"""Step 6e to 6h: the movements that happen between games and between clubs: waivers, tags, trades, compensatory awards.

Waivers (this slice, 6e). NFL: a player released with fewer than four accrued seasons goes on waivers for 24 hours; the other clubs may claim her in
priority order. A vested veteran (four or more accrued seasons) is a free agent at once until the trade deadline and goes on waivers after it. The claimer takes
the contract as it stands (salary, bonus, guarantees) and needs the cap room; if she is claimed the releasing club has no dead money. Priority: through Week 3 the
order of the last draft (earliest pick first); afterwards the lower win percentage first, ties by the last draft order. An exiled club ranks by its Ambassador
record, which stops changing when its round robin ends. The sim resolves each week's waivers inside the week, before rosters are filled.

MODEL (not a rule): a club claims only when the waived player is better than whoever it would otherwise sign at a position where it is below its table count, and it has a place
and the money. `CLAIM_MARGIN` is the distance she must clear.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import economy as EC
import rules as R
from positions import ROSTER_COUNTS, ROSTER_SIZE, POSITIONS

CLAIM_MARGIN = 1.0           # MODEL: a claim must beat the club's alternative by this many rating points


# ---- records and priority ----------------------------------------------------------------------------------------------------------------------
def note_result(record: Dict[int, List[int]], game):
    """Win-loss-tie tally for waiver priority. Only games that count (regular season and the Ambassador round robin) are tallied."""
    if not game.counts_ties or game.home_pts is None:
        return
    for tid, mine, theirs in ((game.home, game.home_pts, game.away_pts), (game.away, game.away_pts, game.home_pts)):
        r = record.setdefault(tid, [0, 0, 0])
        r[0 if mine > theirs else 1 if mine < theirs else 2] += 1


def win_pct(record: Dict[int, List[int]], tid: int) -> float:
    w, l, t = record.get(tid, (0, 0, 0))
    n = w + l + t
    return 0.5 if n == 0 else (w + t / 2.0) / n


def last_draft_slots(lg, year: int) -> Dict[int, int]:
    """Each club's slot in the last draft (round 1, by original club). A league with no earlier draft ranks the weakest club first."""
    mv = lg.movement
    slots = {k[2]: pk.slot for k, pk in mv.picks.items() if k[0] == year - 1 and k[1] == 1 and pk.slot is not None}
    missing = sorted((t for t in lg.teams if t.id not in slots), key=lambda t: (t.strength, t.id))
    base = len(slots)
    for i, t in enumerate(missing, start=1):
        slots[t.id] = base + i
    return slots


def priority_order(lg, year: int, week: int, record: Dict[int, List[int]]) -> List[int]:
    """Waiver priority, first claim first."""
    slots = last_draft_slots(lg, year)
    if week <= R.WAIVER_DRAFT_ORDER_WEEKS:
        return sorted((t.id for t in lg.teams), key=lambda i: (slots[i], i))
    return sorted((t.id for t in lg.teams), key=lambda i: (win_pct(record, i), slots[i], i))


def subject_to_waivers(p, week: int) -> bool:
    return p.accrued_seasons < R.UFA_SEASONS or week > R.TRADE_DEADLINE_WEEK


# ---- the wire ----------------------------------------------------------------------------------------------------------------------------------
@dataclass
class Wire:
    """One week's waiver wire. `held` are players removed from their club but still carrying their contract."""
    year: int
    week: int
    order: List[int]
    held: List[tuple] = field(default_factory=list)          # (player, releasing club id)
    waived: int = 0
    claimed: int = 0
    cleared: int = 0


def new_wire(lg, year: int, week: int, record: Dict[int, List[int]]) -> Wire:
    return Wire(year, week, priority_order(lg, year, week, record))


def waive(lg, t, p, wire: Wire):
    """Take a rostered player off the 53 and onto the wire. Her contract stays on her until the claim is settled."""
    t.roster.remove(p)
    p.team_id = None
    wire.held.append((p, t.id))
    wire.waived += 1


def _alternative(lg, t, pos: str) -> float:
    """The rating of whoever the club would otherwise bring in at this position (its best practice-squad player or free agent there)."""
    best = 0.0
    for q in t.practice_squad:
        if q.pos == pos:
            best = max(best, q.ovr)
    for q in lg.free_agents:
        if not q.retired and q.pos == pos:
            best = max(best, q.ovr)
    return best


def wants(lg, t, p) -> bool:
    """A club with an open place claims her when she is better than its alternative, at a position where it is below its table count."""
    import rosters
    if len(t.roster) >= ROSTER_SIZE:
        return False
    c = rosters.counts(t.roster)
    if c[p.pos] >= ROSTER_COUNTS[p.pos]:                # only a position where the club is below its table count
        return False
    if p.retired:
        return False
    # the cap: her contract plus the rest of the open places at the minimum
    need = max(0, ROSTER_SIZE - len(t.roster) - 1) * EC.MIN_SALARY
    if EC.payroll(t) + p.salary + need > EC.limit(t) + 1e-9:
        return False
    return p.ovr >= _alternative(lg, t, p.pos) + CLAIM_MARGIN


def resolve(lg, wire: Wire) -> None:
    """The 24 hours end. Each waived player goes, best first, to the first club in priority that wants her; the rest are released (dead money lands on
    the releasing club) and join the free agents."""
    mv = lg.movement
    for p, club in sorted(wire.held, key=lambda x: (-x[0].ovr, x[0].id)):
        taker = None
        for tid in wire.order:
            if tid == club:
                continue
            t = lg.by_id[tid]
            if wants(lg, t, p):
                taker = t
                break
        if taker is not None:
            p.team_id = taker.id
            taker.roster.append(p)                      # the contract goes as it stands; nobody owes dead money
            wire.claimed += 1
            mv._event("waiver_claim", year=wire.year, week=wire.week, player=p.id, from_club=club, to_club=taker.id)
        else:
            EC.release(lg.by_id[club], p)
            p.fa_years = 0
            lg.free_agents.append(p)
            wire.cleared += 1
    wire.held.clear()


# ---- trades (6g) ---------------------------------------------------------------------------------------------------------------------------------
# NFL: players and picks may be traded from the start of the league year to the Tuesday after Week 9; both clubs must be under the cap once the trade is
# done; the club receiving a player takes her salary and her guarantees, the club sending her keeps what is left of her signing bonus (it accelerates onto
# its cap: all of it at once before the post-draft date, this season's share now and the rest next season after it); a player whose tender is still unsigned
# cannot be traded (in the DFL a tag or tender is signed when it is made, so the open ones are the rights still taking offers); picks are tradable for the
# coming draft and three drafts ahead. The Commissioner's review is shrink-only: he stops an illegal trade and changes nothing else, so the engine's
# job is to say exactly why a trade is illegal and to change nothing when it is.
# What is not modelled: conditional picks, cash, players on injured reserve or the practice squad, no-trade clauses, and trades made by the autopilot (it makes none).

class TradeError(ValueError):
    """An illegal trade. Nothing has changed when this is raised."""


def drafted(lg, year: int) -> bool:
    """Has the draft of this league year been held? (The post-draft date of the bonus rule.)"""
    return any(pk.year == year and pk.selected is not None for pk in lg.movement.picks.values())


def _lookup(t, pid: int):
    for p in t.roster:
        if p.id == pid:
            return p
    return None


def _cap_after(lg, t, out_players, in_players, dead_add: float, in_season: bool) -> float:
    """What the club's cap count would be after the trade, in the same measure the season uses (the 51 highest numbers plus the rest at the minimum in the
    offseason; everyone under contract in the season), less nothing for open offers: those holds count against it."""
    mv = lg.movement
    gone = {p.id for p in out_players}
    salaries = [p.salary for p in t.roster if p.id not in gone] + [p.salary - p.bonus for p in in_players]
    dead = t.dead_now + dead_add
    held = mv.reserved_cap(t.id)
    if in_season:
        return round(sum(salaries) + sum(p.salary for p in t.practice_squad) + sum(p.salary for p in t.ir) + dead + held, 4)
    count = EC.counted_51(salaries, dead)
    return round(count + max(0, EC.OFFSEASON_COUNT - len(salaries)) * EC.MIN_SALARY + EC.OFFSEASON_RESERVE + held, 4)


def acceleration(lg, p, year: int, week: Optional[int]):
    """(this season's, next season's) dead money the sending club takes for a traded player's unspent signing bonus."""
    total = round(p.bonus * p.bonus_years, 4)
    if week is None and not drafted(lg, year):
        return total, 0.0
    now = min(total, p.bonus)
    return now, round(total - now, 4)


def check_trade(lg, a: int, b: int, players_a, players_b, picks_a, picks_b, year: int, week: Optional[int] = None) -> List[str]:
    """Every reason a trade is illegal (empty when it is legal). `players_a` are the ids club `a` sends to `b`; `picks_a` are the keys it sends. `week` is the
    number of regular-season weeks finished, or None in the offseason."""
    mv = lg.movement
    picks_a, picks_b = [tuple(k) for k in picks_a], [tuple(k) for k in picks_b]
    why: List[str] = []
    if a == b:
        why.append("a club cannot trade with itself")
    if a not in lg.by_id or b not in lg.by_id:
        return why + ["no such club"]
    if week is not None and week > R.TRADE_DEADLINE_WEEK:
        why.append(f"the trade deadline has passed (week {R.TRADE_DEADLINE_WEEK})")
    if not (players_a or players_b or picks_a or picks_b):
        why.append("nothing is traded")
    if len(set(players_a)) != len(players_a) or len(set(players_b)) != len(players_b) or len(set(picks_a)) != len(picks_a) or len(set(picks_b)) != len(picks_b):
        why.append("an asset is listed twice")
    sending = {a: [], b: []}
    for club, pids in ((a, players_a), (b, players_b)):
        t = lg.by_id[club]
        for pid in pids:
            p = _lookup(t, pid)
            if p is None:
                why.append(f"player {pid} is not on club {club}'s 53")
                continue
            if p.years_left < 1:
                why.append(f"player {pid} has no contract past this season")
            right = mv.rights.get((year, pid))
            if right is not None and right.status == "tendered":
                why.append(f"player {pid} is on an open tender: it must be signed or matched first")
            if any(o.status == "pending" and o.player_id == pid for o in mv.offers.values()):
                why.append(f"player {pid} has an offer pending")
            sending[club].append(p)
    for club, keys in ((a, picks_a), (b, picks_b)):
        for key in keys:
            pk = mv.picks.get(tuple(key))
            if pk is None:
                why.append(f"no such pick {tuple(key)}")
            elif pk.owner != club:
                why.append(f"pick {tuple(key)} is not club {club}'s")
            elif pk.selected is not None:
                why.append(f"pick {tuple(key)} has been used")
            elif pk.reserved_by is not None:
                why.append(f"pick {tuple(key)} is held for offer {pk.reserved_by}")
    if why:
        return why
    limit = R.ROSTER_LIMIT if week is not None else R.CAMP_LIMIT
    for club, other in ((a, b), (b, a)):
        t = lg.by_id[club]
        n = len(t.roster) - len(sending[club]) + len(sending[other])
        if n > limit:
            why.append(f"club {club} would carry {n} players (limit {limit})")
        now = next_ = 0.0
        for p in sending[club]:
            x, y = acceleration(lg, p, year, week)
            now, next_ = now + x, next_ + y
        cap = _cap_after(lg, t, sending[club], sending[other], now, week is not None)
        if cap > EC.limit(t) + 1e-9:
            why.append(f"club {club} would be over the cap ({cap:.2f} against {EC.limit(t):.2f})")
    return why


def trade(lg, a: int, b: int, players_a, players_b, picks_a, picks_b, year: int, week: Optional[int] = None) -> dict:
    """Make the trade. Everything is checked first: an illegal trade raises TradeError and nothing has changed. A player keeps her base salary and her
    guarantees with the new club; the sending club keeps her signing bonus as dead money (acceleration)."""
    why = check_trade(lg, a, b, players_a, players_b, picks_a, picks_b, year, week)
    if why:
        raise TradeError("; ".join(why))
    mv = lg.movement
    ta, tb = lg.by_id[a], lg.by_id[b]
    for src, dst, pids in ((ta, tb, players_a), (tb, ta, players_b)):
        for pid in pids:
            p = _lookup(src, pid)
            now, later = acceleration(lg, p, year, week)
            src.dead_now = round(src.dead_now + now, 4)
            src.dead_next = round(src.dead_next + later, 4)
            src.roster.remove(p)
            p.salary = round(p.salary - p.bonus, 4)                   # the receiver takes the base and the guarantees; the bonus stays behind
            p.bonus, p.bonus_years = 0.0, 0
            p.team_id, p.fa_years = dst.id, 0
            dst.roster.append(p)
    for owner_to, keys in ((b, picks_a), (a, picks_b)):
        for key in keys:
            mv.transfer_pick(lg, tuple(key), owner_to, reason="trade")
    mv._event("trade", year=year, week=week, clubs=[a, b], players=[list(players_a), list(players_b)],
              picks=[[list(k) for k in picks_a], [list(k) for k in picks_b]])
    return {"clubs": (a, b), "players": (list(players_a), list(players_b)), "picks": (list(picks_a), list(picks_b))}


# ---- compensatory picks (6h) -----------------------------------------------------------------------------------------------------------------------
# NFL: a club that loses more (or better) compensatory free agents than it signs is awarded picks at the end of rounds 3 to 7 of the next draft. Only
# unrestricted free agents whose contracts ran out count (released players, restricted players and players cut loose by the exile rule do not). Each
# club's lost and signed players cancel in order of value, best against best; what is left over is ranked league-wide by value (the new contract's average
# yearly pay, weighted by how much of the season she played) and the picks go out from the top, at most four to a club and, in the NFL, 32 in all.
# DFL: 48 clubs, so at most 48 picks (rules.COMP_PICKS_MAX), four to a club (rules.COMP_PICKS_PER_TEAM_MAX), and a club whose losses and signings are equal
# in number can still earn a seventh-round pick if what it lost was worth clearly more than what it signed.
# MODEL (the value scale and the round sizes): the NFL's formula is not public beyond its inputs.
COMP_ROUND_SIZES = (6, 9, 10, 10, 13)            # picks in rounds 3 to 7; they add up to rules.COMP_PICKS_MAX
COMP_VALUE_FLOORS = (3.0, 1.8, 1.1, 0.7, 0.45)   # the least value that earns a pick in rounds 3 to 7 ($ millions of weighted yearly pay)
COMP_GAP_MIN = 0.5                               # value a club that lost and signed the same number must have lost on balance to earn a seventh
assert sum(COMP_ROUND_SIZES) == R.COMP_PICKS_MAX


def comp_value(apy: float, weeks_played: int) -> float:
    """What a lost or signed free agent counts for: her new contract's yearly pay, from half of it (a player who missed the year) to all of it."""
    frac = min(1.0, max(0, weeks_played) / float(R.REGULAR_SEASON_WEEKS - 1))
    return round(apy * (0.5 + 0.5 * frac), 4)


def comp_candidates(lost: List[tuple], signed: List[tuple]):
    """`lost` is (club, player id, value) for each qualifying player who left her club; `signed` is (club, player id, value) for each signing of one. Returns the
    candidates [(value, club, player id or None, kind)] after each club's cancellation, best first (kind "net" or "gap")."""
    by_lost, by_signed = {}, {}
    for club, pid, v in lost:
        by_lost.setdefault(club, []).append((v, pid))
    for club, pid, v in signed:
        by_signed.setdefault(club, []).append((v, pid))
    out = []
    for club, ls in by_lost.items():
        ls.sort(key=lambda x: (-x[0], x[1]))
        gs = sorted(by_signed.get(club, []), key=lambda x: (-x[0], x[1]))
        if len(ls) > len(gs):
            for v, pid in ls[len(gs):][:R.COMP_PICKS_PER_TEAM_MAX]:      # best against best: what is left over is the club's lowest-valued losses
                out.append((v, club, pid, "net"))
        elif len(ls) == len(gs):
            gap = sum(v for v, _ in ls) - sum(v for v, _ in gs)
            if gap >= COMP_GAP_MIN:
                out.append((round(gap, 4), club, None, "gap"))
    out.sort(key=lambda x: (x[3] == "gap", -x[0], x[1], x[2] if x[2] is not None else -1))
    return out


def award_compensatory(lg, year: int, lost: List[tuple], signed: List[tuple]) -> List[dict]:
    """Award the picks for the draft of `year` + 1 (the free agency just held is the one before that draft). Returns what was awarded."""
    import movement as MV
    mv = lg.movement
    draft = year + 1
    if any(p.year == draft and p.original >= MV.COMP_BASE for p in mv.picks.values()):
        raise MV.MovementError(f"compensatory picks for the {draft} draft are already awarded")
    room = list(COMP_ROUND_SIZES)
    per_club: Dict[int, int] = {}
    taken: Dict[int, int] = {}
    awards = []
    for value, club, pid, kind in comp_candidates(lost, signed):
        if sum(per_club.values()) >= R.COMP_PICKS_MAX or per_club.get(club, 0) >= R.COMP_PICKS_PER_TEAM_MAX:
            continue
        if kind == "gap":
            i = len(room) - 1                                            # only a seventh
            ok = value >= COMP_GAP_MIN and room[i] > 0
        else:
            i = next((i for i, f in enumerate(COMP_VALUE_FLOORS) if value >= f), None)
            while i is not None and i < len(room) and room[i] == 0:      # a full round pushes the pick down a round
                i += 1
            ok = i is not None and i < len(room)
        if not ok:
            continue
        rnd = 3 + i
        room[i] -= 1
        seq = taken.get(rnd, 0)
        taken[rnd] = seq + 1
        pk = MV.Pick(draft, rnd, MV.COMP_BASE + seq, club, rnd * R.DRAFT_PICKS_PER_ROUND)
        mv.picks[pk.key] = pk
        per_club[club] = per_club.get(club, 0) + 1
        mv._event("comp_award", year=draft, round=rnd, club=club, place=seq, value=value, basis=kind, player=pid)
        awards.append(dict(year=draft, round=rnd, club=club, value=value, basis=kind, player=pid))
    return awards
