"""The roster offseason: aging, retirement, contracts ending, the draft and free agency.

The lists, limits and draft here are the rulebook's (rosters.py has the lists); the numbers that make players are MODEL structure (a stand-in, not a league rule) with PLACEHOLDER numbers (see roster_model.py). The one
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
import rosters
import economy as EC
import contracts as CT
import movement as MV
import tables as TB
import staff_cards as SC
import transactions as T
import injuries as IJ

CUT_CLAIMS_MAX = 3            # MODEL: most waiver claims one club makes at the cutdown
CUT_CLAIM_MARGIN = 4.0        # MODEL: a cut player must beat the club's weakest player at her position by this many rating points to be claimed

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
    if p.wear:
        base += IJ.wear_retire_bonus(p)                                   # lasting damage shortens a career
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
    """Rating of the player taken at overall pick `pick` (1-336): steep over the first round, then a slow slide toward an undrafted player's."""
    base = rm.rookie_base - rm.rookie_late_drop * min(1.0, (pick - 1) / (R.DRAFT_ROUNDS * R.TOTAL_TEAMS - 1))
    return clamp(base + rm.rookie_span * math.exp(-(pick - 1) / rm.rookie_decay)
                 + rng.gauss(0.0, rm.rookie_sd), 30, 95)


def _team_counts(roster: List[Player]) -> Dict[str, int]:
    c = {p: 0 for p in POSITIONS}
    for pl in roster:
        c[pl.pos] += 1
    return c


def _pick_rookie_position(roster: List[Player], overall: int, rng: random.Random) -> str:
    counts = _team_counts(roster)
    w = []
    for pos in POSITIONS:
        need = ROSTER_COUNTS[pos] - counts[pos]
        if pos in ("K", "P"):
            x = 1.0 if need > 0 else 0.02
            if overall <= 100:                       # no one spends a first- or second-round pick on a kicker or punter
                x *= 0.05
            w.append(x)
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
    """This year's undrafted rookies: the market for camp invitations. They have never been on a roster, so they have no card
    until one makes a team's practice squad or roster or lands in the free-agent pool."""
    out = []
    for _ in range(rm.undrafted_per_year):
        pos = rng.choices(POSITIONS, [ROSTER_COUNTS[p] for p in POSITIONS])[0]
        ovr = clamp(rng.gauss(rm.undrafted_mean, rm.undrafted_sd), 28, 80)
        p = make_player(rng, lg.new_id(), pos, ovr, rng.choice((22, 22, 23, 24)), None)
        p.years_in_league = 0
        p.accrued_seasons = p.credited_seasons = 0
        out.append(p)
    return out


def _pick_cut(t, players, emergency: bool = False):
    """The player a team in cap trouble lets go: of the players whose release saves more than her replacement (at the highest minimum rung) would cost,
    the most overpaid. A post-draft designation is used when one is left and the dead money is large. When nothing helps and the designations are
    gone, the league lets the team defer the dead money to next season (emergency); this is the only way a team's cap can be put right, and the
    study counts how often it happens. Returns (player, designate) or None."""
    repl = EC.MIN_SALARY_SCALE[-1]
    options = []
    for p in players:
        des = EC.can_designate(t) and EC.dead_charge(p) > 0.5 * p.salary
        if emergency and not EC.can_designate(t):
            des = True
        now = min(EC.dead_charge(p), p.bonus) if des else EC.dead_charge(p)
        if p.salary - now - repl > 0.005:
            options.append((p.salary - EC.market_salary(p.pos, p.ovr, p.credited_seasons) - 0.5 * now, p.id, p, des))
    if not options:
        return None
    _, _, w, des = max(options, key=lambda o: (o[0], o[1]))
    return w, des


def _offseason_over(t, extra_slots: int = 0) -> float:
    """The offseason cap count with room held back for the places still to fill (economy.offseason_over)."""
    return EC.offseason_over(t, extra_slots)


def _keep_rule_factory(rm, rng):
    def keep_rule(t, keep, p, cost) -> bool:
        """Does the club want her back at her price? The value-to-price rule (contracts.club_wants); the old re-signing dice when tables are off."""
        if rm.contract_tables:
            return CT.club_wants(CT.club_gain(keep + [p], p), cost, SC.gm_retention_factor(t), rm.keep_g0, rm.keep_g1, rm.keep_gm_shift)
        q = EC.RESIGN_BASE * (rm.fa_star_protect if p.ovr >= 70 else 1.0) * SC.gm_retention_factor(t)
        return rng.random() >= q
    return keep_rule


def run_roster_offseason(lg: League, rng: random.Random, rm: RosterModel, year: int,
                         pick_of: Dict[int, int], returners: List[int]) -> dict:
    """Update every roster for next season. `pick_of` maps team id -> its place in every round of the draft (1-48);
    `returners` are the teams coming back from exile. Returns a small log of what happened.

    The order: the season's accounts close; everyone under contract (the 53, the practice squad and injured reserve) becomes one squad;
    everyone ages, some retire, contracts run down; the seven-round draft; cap casualties; free agency fills each position; every team
    invites undrafted rookies and others until the camp holds 90; the cutdown takes each team to 53 plus a practice squad of 16."""
    log = dict(retired=0, expired=0, signed=0, premium=0, released=0, rookies=0, street=0, resigned=0, cap_blocked=0, cap_cuts=0,
               udfa=0, camp=0, cut=0, dropped=0, practice_squad=0, expired_roster=0)
    log["cap"] = EC.close_season(lg, returners, year)       # this season's accounts, before anything changes
    SC.log(lg, year, "cap_close", **{k: v for k, v in log["cap"].items() if k != "year"})
    teams = lg.teams
    mv = lg.movement
    mv.begin_year(lg, year, pick_of)                         # the pick ledger: this draft and the next three, slots set from the draft order
    for t in teams:
        EC.new_year(t)                                       # a new league year: last season's dead money is gone, designations are fresh
    # injuries heal over the offseason, injured reserve is over, and the practice squad joins the squad
    ps_ids = {p.id for t in teams for p in t.practice_squad}
    for t in teams:
        t.roster = list(t.roster) + list(t.ir) + list(t.practice_squad)
        t.ir, t.practice_squad, t.ir_returns, t.elevated = [], [], 0, []
        for p in t.roster:
            p.weeks_out, p.ir_games, p.ir_designated, p.injury, p.elevations = 0, 0, False, "", 0
    for p in lg.free_agents:
        p.weeks_out, p.injury = 0, ""

    # 1. everybody ages and changes
    progress([p for t in teams for p in t.roster], rm, rng,
             {p.id: t.coach for t in teams if t.coach is not None for p in t.roster})
    progress(lg.free_agents, rm, rng)

    # 2. retirement (the squad and the unsigned)
    for t in teams:
        keep = []
        for p in t.roster:
            if rng.random() < _retire_prob(p):
                p.retired, p.team_id = True, None
                IJ.clear_on_exit(p)
                log["retired"] += 1
            else:
                keep.append(p)
        t.roster = keep
    pool: List[Player] = []
    for p in lg.free_agents:
        p.fa_years += 1
        if rng.random() < _retire_prob(p) or p.fa_years > 2:
            p.retired = True
            IJ.clear_on_exit(p)
            log["retired"] += 1
        else:
            pool.append(p)

    # 3. contracts run down. An expiring player is first classed by her earned service (service.expiry_class; every expiring player of an
    # exiled club counts as restricted). Exclusive-rights and restricted players are tendered or not by a value rule; a tender gives the club
    # rights (movement.py) and she plays on it. Unrestricted players are re-signed (at today's market price) or reach the market: stars are
    # likelier to be kept and a good negotiator GM keeps more, but a team can only keep who it can afford this season (the cap is a hard limit)
    import service
    per = R.TOTAL_TEAMS
    keep_rule = _keep_rule_factory(rm, rng)
    pending: List[tuple] = []                # important re-signings waiting for their contract table: (club, player, market price, standard years, class, rookie pays, limit)
    comp_lost: Dict[int, tuple] = {}         # player id -> (club she left, weeks she played): unrestricted players who reached the market
    signed_by: Dict[int, tuple] = {}         # player id -> (club that signed her, her new yearly pay) for each of them another club signed
    tag_tbl = mv.tag_table(lg, 2)          # tag prices are read off the contracts that run past this offseason, fixed before any club's contracts run down
    for t in teams:
        for p in t.roster:
            EC.run_down(p)
            if p.years_left > 0:
                EC.enforce_minimum(p)
        keep = [p for p in t.roster if p.years_left > 0]
        lim = EC.limit(t) - rm.cap_headroom          # a club keeps a little room back; the hard limit still applies at the cut-downs
        # mid-contract extensions (NFL: any time after a drafted player's third season): a player with her final year ahead who is good, still young
        # enough and wanted is signed at today's market price for a new term; the club must fit her new number under its limit
        exiled0 = t.status == "exiled"
        if not exiled0:
            for p in sorted((q for q in keep if q.years_left == 1 and q.id not in ps_ids and q.ovr >= rm.ext_min_ovr and q.age <= rm.ext_max_age
                             and (q.accrued_seasons or 0) >= R.EXTENSION_MIN_SEASONS), key=lambda q: -q.ovr):
                if rng.random() >= rm.ext_prob / max(0.5, SC.gm_retention_factor(t)):
                    continue
                cost = EC.market_salary(p.pos, p.ovr, p.credited_seasons)
                if cost <= p.salary * 1.02:
                    continue                                         # she is already paid at or above her price: nothing to agree
                rookie_pays0 = [EC.rookie_salary(x) for x in mv.slots_owned(year, t.id)]
                slots0 = max(0, EC.OFFSEASON_COUNT - len(keep) - len(rookie_pays0))
                new_sal = [k.salary for k in keep if k is not p] + [cost]
                if not (keep_rule(t, keep, p, cost)
                        and EC.counted_51(new_sal + rookie_pays0, t.dead_now) + slots0 * EC.MIN_SALARY + EC.OFFSEASON_RESERVE <= lim):
                    continue
                old = (p.salary, p.years_left)
                EC.sign(p, cost, EC.contract_years(p))
                log["extensions"] = log.get("extensions", 0) + 1
                log.setdefault("extension_list", []).append((t.id, p.id, old[0], old[1], p.salary, p.years_left, p.accrued_seasons or 0, p.age, round(p.ovr, 1)))
        expiring = sorted((p for p in t.roster if p.years_left <= 0), key=lambda p: -p.ovr)
        lim = EC.limit(t) - rm.cap_headroom          # a club keeps a little room back; the hard limit still applies at the cut-downs
        rookie_pays = [EC.rookie_salary(s) for s in mv.slots_owned(year, t.id)]
        exiled = t.status == "exiled"
        # the club's one tag: its best expiring unrestricted player, if she is good enough, the dice say so and the tag fits under the cap
        tag_cand = next((q for q in expiring if not exiled and q.id not in ps_ids and q.ovr >= rm.tag_min_ovr and service.expiry_class(q) == "unrestricted"), None)
        tag_roll = tag_cand is not None and rng.random() < rm.tag_prob
        for p in expiring:
            if tag_roll and p is tag_cand:
                ttype = "franchise" if p.ovr >= rm.tag_franchise_ovr else "transition"
                if ttype == "franchise" and mv.tag_streak(year, t.id, p.id) >= MV.TAG_MAX_STREAK:
                    ttype = "transition"                         # a club may franchise-tag the same player only three years running
                price = mv.tag_price(p, ttype, year, t.id, tag_tbl)
                slots_t = max(0, EC.OFFSEASON_COUNT - (len(keep) + 1) - len(rookie_pays))
                if EC.counted_51([k.salary for k in keep] + [price] + rookie_pays, t.dead_now) + slots_t * EC.MIN_SALARY + EC.OFFSEASON_RESERVE <= lim:
                    mv.tag(lg, p, ttype, year, table=tag_tbl)
                    keep.append(p)
                    log["tagged"] = log.get("tagged", 0) + 1
                    continue
                log["tag_cap_blocked"] = log.get("tag_cap_blocked", 0) + 1
            cls = service.expiry_class(p, exiled=exiled)
            cost = EC.market_salary(p.pos, p.ovr, p.credited_seasons)
            slots_after = max(0, EC.OFFSEASON_COUNT - (len(keep) + 1) - len(rookie_pays))      # the rest of the 51 and the rookies still to come
            level, wants = None, None
            if cls != "unrestricted" and p.id not in ps_ids:      # practice-squad wages are for the year: no rights, as in the NFL
                prior_base = max(0.0, p.salary - p.bonus)
                if rm.exile_veteran_dice and exiled and service.expiry_class(p) == "unrestricted":
                    # exile rights on a veteran who would otherwise be a free agent: the club still has to want her (the same dice as any re-signing);
                    # what the rights add is the tender's protection and price, not a guaranteed keep (MODEL: roster_model.exile_veteran_dice)
                    q = EC.RESIGN_BASE * (rm.fa_star_protect if p.ovr >= 70 else 1.0) * SC.gm_retention_factor(t)
                    dice = rng.random() >= q
                    wants = dice and (keep_rule(t, keep, p, cost) if rm.contract_tables else True)    # both the dice and the value rule must say yes
                level = mv.choose_level(p, cls, cost, prior_base, rm.tender_reach) if wants is not False else None
                if level != "extend":
                    if level is not None:
                        price = EC.tender_price(level, prior_base, p.credited_seasons)
                        if exiled and service.expiry_class(p) == "unrestricted":
                            price = max(price, min(EC.MAX_SALARY, cost))       # movement.tender prices a veteran held only by the exile rule at her market price
                        count = EC.counted_51([k.salary for k in keep] + [price] + rookie_pays, t.dead_now)
                        if count + slots_after * EC.MIN_SALARY + EC.OFFSEASON_RESERVE <= lim:
                            mv.tender(lg, p, level, year, exiled=exiled)
                            keep.append(p)
                            log["tendered"] = log.get("tendered", 0) + 1
                            continue
                        log["cap_blocked"] += 1
                    p.team_id, p.fa_years = None, 0
                    EC.clear_contract(p)
                    pool.append(p)
                    log["expired"] += 1
                    log["expired_roster"] += p.id not in ps_ids
                    continue
                log["extended"] = log.get("extended", 0) + 1             # no tender fits (worth less than the lowest, or far more than the top fit): negotiated at the market, like an unrestricted player
            if wants is None:
                wants = keep_rule(t, keep, p, cost)
            count = EC.counted_51([k.salary for k in keep] + [cost] + rookie_pays, t.dead_now)
            deal = None
            if wants and count + slots_after * EC.MIN_SALARY + EC.OFFSEASON_RESERVE <= lim:
                deal = (cost, EC.contract_years(p))
                if rm.contract_tables and p.ovr >= rm.table_min_ovr and p.id not in ps_ids:         # an important deal is made at a table (below), with the DFLPA representative present
                    pending.append((t, p, cost, deal[1], cls, rookie_pays, lim))
            if deal is not None:
                EC.sign(p, deal[0], deal[1])
                keep.append(p)
                log["resigned"] += 1
            else:
                if wants:
                    log["cap_blocked"] += 1
                if cls == "unrestricted" and p.id not in ps_ids:         # a compensatory free agent if another club signs her (exile-class and restricted players are not)
                    weeks = len(p.service_weeks) if p.service_year == year else 0
                    comp_lost[p.id] = (t.id, weeks)
                p.team_id, p.fa_years = None, 0
                EC.clear_contract(p)
                pool.append(p)
                log["expired"] += 1
                log["expired_roster"] += p.id not in ps_ids
        t.roster = keep
    # 3a. contract tables: every important re-signing (rated table_min_ovr or better) was provisionally signed at her market price above; the tables for all of
    # them now run together, each club's general manager against the player, the DFLPA representative holding back what the rules or the cap forbid
    if pending:
        def fits_for(t, p, rookie_pays, lim):
            def fits(x):
                sal = [k.salary for k in t.roster if k is not p] + [x]
                slots = max(0, EC.OFFSEASON_COUNT - len(t.roster) - len(rookie_pays))
                return EC.counted_51(sal + rookie_pays, t.dead_now) + slots * EC.MIN_SALARY + EC.OFFSEASON_RESERVE <= lim + 1e-9
            return fits
        tbs = [CT.ContractTable(lg, year, t, p, cost, yrs, fits_for(t, p, rp, lim)) for (t, p, cost, yrs, _, rp, lim) in pending]
        TB.run_tables(lg, tbs)
        for (t, p, cost, yrs, cls, rp, lim), tb in zip(pending, tbs):
            log["tables"] = log.get("tables", 0) + 1
            deal = tb.deal
            if deal is not None and not fits_for(t, p, rp, lim)(deal[0]):
                deal = (cost, yrs)                                  # an earlier deal at this club used the room: she signs at the market price the cap was reserved for
            if deal is None:                                         # she (or the club) walked: she reaches the market
                log["table_walks"] = log.get("table_walks", 0) + 1
                log["resigned"] -= 1
                log["expired"] += 1
                log["expired_roster"] += 1                               # only players on the 53 are tabled (a practice-squad wage is for the year)
                t.roster.remove(p)
                if cls == "unrestricted":
                    comp_lost[p.id] = (t.id, len(p.service_weeks) if p.service_year == year else 0)
                p.team_id, p.fa_years = None, 0
                EC.clear_contract(p)
                pool.append(p)
            else:
                if not tb.plain():
                    log["table_changes"] = log.get("table_changes", 0) + 1
                EC.sign(p, deal[0], deal[1])
    udfa = _undrafted(lg, rm, rng)

    # 3b. the restricted market: offer sheets, five days to match, compensation (movement.py), all settled before the draft
    mv.run_market(lg, rng, rm, year, log)
    mv.check_ready_for_draft(year)
    if rm.trade_sell_prob > 0:
        import autotrade
        log["trades"] = autotrade.window(lg, rng, rm, year, None, rm.trade_sell_prob, rm.trade_swap_prob, year, rounds=2)      # the trade market before the draft

    # 4. the draft: seven rounds of 48 picks in the same order each round, quality by overall pick, a rookie-scale contract by pick.
    # The club that owns a pick makes the selection (it may be another club's original pick); the slot and the rookie price are the pick's.
    def draft_pick_made(pk, overall, rnd):
        t = lg.by_id[pk.owner]
        mv.check_free(pk.key)                              # before anything is made for it: a used or held pick stops the draft cleanly
        pos = _pick_rookie_position(t.roster, overall, rng)
        p = make_player(rng, lg.new_id(), pos, clamp(rookie_ovr(overall, rm, rng) + SC.gm_scouting_bonus(t), 30, 95),
                        rng.choice((22, 22, 22, 23)), t.id, draft_year=year, draft_pick=overall)
        p.years_in_league = 0
        p.accrued_seasons = p.credited_seasons = 0
        EC.sign(p, EC.rookie_salary(overall), EC.ROOKIE_YEARS, share=EC.ROOKIE_BONUS_SHARE[rnd],
                guarantee_years=EC.ROOKIE_YEARS if rnd == 0 else 0, rookie=True)     # round-1 deals are fully guaranteed
        t.roster.append(p)
        mv.select(pk.key, p.id)
        log["rookies"] += 1
        if pk.original >= MV.COMP_BASE:
            log["comp_rookies"] = log.get("comp_rookies", 0) + 1
        elif pk.owner != pk.original:
            log["traded_picks_used"] = log.get("traded_picks_used", 0) + 1

    for rnd in range(R.DRAFT_ROUNDS):
        for orig in sorted(teams, key=lambda t: pick_of[t.id]):
            pk = mv.picks[(year, rnd + 1, orig.id)]
            overall = rnd * per + pick_of[orig.id]
            assert pk.slot == overall, (pk.key, pk.slot, overall)
            draft_pick_made(pk, overall, rnd)
        for pk in mv.comp_picks(year, rnd + 1):             # compensatory picks come at the end of rounds 3 to 7, best value first
            draft_pick_made(pk, pk.slot, rnd)

    # 4b. cap casualties. Banked room is a one-season allowance: a team that spent it on multi-year contracts comes back to the $100M cap and must
    # shed the players who cost the most beyond their market price until it can fill its squad at the minimum wage inside its limit
    for t in teams:
        while _offseason_over(t) > EC.limit(t) + 1e-9:
            top = sorted(t.roster, key=lambda p: (-p.salary, p.id))[:EC.OFFSEASON_COUNT]        # only the 51 highest cap numbers count, so only they can help
            pick = _pick_cut(t, top) or _pick_cut(t, top, emergency=True)
            if pick is None:
                break
            w, des = pick
            log["emergency"] = log.get("emergency", 0) + (des and not EC.can_designate(t))
            t.roster.remove(w)
            EC.release(t, w, des)
            w.team_id, w.fa_years = None, 0
            pool.append(w)
            log["cap_cuts"] += 1
            log["designated"] = log.get("designated", 0) + des

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
        return EC.limit(t) - rm.cap_headroom - _offseason_over(t, extra_slots=1)

    def take(t, p, price=None):
        by_pos[p.pos].remove(p)
        p.team_id, p.fa_years = t.id, 0
        EC.sign(p, EC.market_salary(p.pos, p.ovr, p.credited_seasons) if price is None else price, EC.contract_years(p))
        t.roster.append(p)
        log["signed"] += 1
        if p.id in comp_lost and comp_lost[p.id][0] != t.id:
            signed_by[p.id] = (t.id, p.salary)

    def affordable(t, pos):
        """The best player on the market at a position that this team can afford (an asking price is the market price)."""
        room = room_for(t)
        for c in by_pos[pos]:
            if EC.market_salary(c.pos, c.ovr, c.credited_seasons) <= room:
                return c
        return None

    def release_worst(t, pos):
        at = sorted((p for p in t.roster if p.pos == pos), key=lambda p: p.ovr)
        w = at[0]
        t.roster.remove(w)
        EC.release(t, w)
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

    # 5b. fill every open slot at every position, round by round
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
                best = rosters.street_player(lg, rng, pos)
                by_pos[pos].append(best)
                price = EC.min_salary(best.credited_seasons)
                log["street"] += 1
            take(t, best, price)
            progressed = True
        if not progressed:
            break

    # 5c. compensatory picks for the next draft: the club that lost more (or better) unrestricted players than it signed
    lost_list, signed_list = [], []
    for pid, (club, wk) in sorted(comp_lost.items()):
        who = signed_by.get(pid)
        if who is not None:
            v = T.comp_value(who[1], wk)
            lost_list.append((club, pid, v))
            signed_list.append((who[0], pid, v))
    awards = T.award_compensatory(lg, year, lost_list, signed_list)
    log["comp_picks"] = len(awards)

    # 6. the camp: every team invites undrafted rookies (three-year minimum contracts) and, when they run out at a position, unsigned veterans,
    # round by round in the same order, until it holds 90
    udfa_by_pos: Dict[str, List[Player]] = {pos: [] for pos in POSITIONS}
    for p in udfa:
        udfa_by_pos[p.pos].append(p)
    for pos in POSITIONS:
        udfa_by_pos[pos].sort(key=lambda p: -p.ovr)
    weights = [ROSTER_COUNTS[pos] for pos in POSITIONS]
    while True:
        progressed = False
        for t in order:
            if len(t.roster) >= R.CAMP_LIMIT:
                continue
            for _ in range(4):                               # a few tries at positions the market has run out of
                pos = rng.choices(POSITIONS, weights)[0]
                if udfa_by_pos[pos]:
                    p = udfa_by_pos[pos].pop(0)
                    p.team_id = t.id
                    EC.sign(p, EC.MIN_SALARY, EC.UNDRAFTED_YEARS)
                    t.roster.append(p)
                    log["udfa"] += 1
                    progressed = True
                    break
                vet = next((q for q in by_pos[pos] if q.ovr <= rm.camp_vet_max_ovr), None)
                if vet is not None:
                    by_pos[pos].remove(vet)
                    vet.team_id, vet.fa_years = t.id, 0
                    EC.sign(vet, EC.min_salary(vet.credited_seasons), 1)
                    t.roster.append(vet)
                    log["signed"] += 1
                    progressed = True
                    break
        if not progressed:
            break
    leftovers = [p for pos in POSITIONS for p in udfa_by_pos[pos]]       # unsigned undrafted rookies join the market

    # 7. the cutdown to 53, then each team's practice squad of 16 from the players it cut. A team keeps the best players at each position up to
    # the roster table and, if that costs more than its limit, sheds its most overpaid player and chooses again.
    cut: List[Player] = []
    held_ids: set = set()
    held: List[tuple] = []                                  # (player, club that cut her): on waivers until 7a
    for t in order:
        camp = sorted(t.roster, key=lambda p: (-p.ovr, p.id))
        log["camp"] += len(camp)
        while True:
            sel, rest = [], []
            taken = {pos: 0 for pos in POSITIONS}
            for p in camp:
                if taken[p.pos] < ROSTER_COUNTS[p.pos]:
                    taken[p.pos] += 1
                    sel.append(p)
                else:
                    rest.append(p)
            short = [pos for pos in POSITIONS if taken[pos] < ROSTER_COUNTS[pos]]
            if short:                                          # the camp ran out at a position: a street free agent at the minimum
                for pos in short:
                    for _ in range(ROSTER_COUNTS[pos] - taken[pos]):
                        s = rosters.street_player(lg, rng, pos)
                        s.team_id = t.id
                        EC.sign(s, EC.min_salary(s.credited_seasons), 1)
                        camp.append(s)
                        log["street"] += 1
                camp.sort(key=lambda p: (-p.ovr, p.id))
                continue
            ps = rosters.choose_practice_squad(rest, [], R.PRACTICE_SQUAD_SIZE)
            gone = [p for p in rest]                            # everyone not selected is released (the practice squad signs fresh one-year wages)
            pay = sum(p.salary for p in sel) + EC.PRACTICE_SQUAD_SALARY * R.PRACTICE_SQUAD_SIZE + t.dead_now + sum(EC.dead_charge(p) for p in gone)
            if pay <= EC.limit(t) + 1e-9:
                break
            pick = _pick_cut(t, sel) or _pick_cut(t, sel, emergency=True)
            if pick is None:
                break
            w, des = pick
            log["emergency"] = log.get("emergency", 0) + (des and not EC.can_designate(t))
            camp.remove(w)
            EC.release(t, w, des)
            w.team_id, w.fa_years = None, 0
            cut.append(w)
            log["cap_cuts"] += 1
            log["designated"] = log.get("designated", 0) + des
        ps_ids = {p.id for p in ps}
        for p in rest:
            if p.id not in ps_ids and T.subject_to_waivers(p, 0) and p.team_id == t.id and p.salary > 0:
                held.append((p, t.id))
                held_ids.add(p.id)                            # under 4 accrued seasons: on waivers until the claims are settled (no dead money if she is claimed)
            else:
                EC.release(t, p)                              # let go (the practice squad starts a new one-year contract)
        for p in ps:
            rosters.to_practice_squad(p)
        for p in rest:
            if p.id not in ps_ids and p.id not in held_ids:
                p.team_id, p.fa_years = None, 0
                cut.append(p)
                log["cut"] += 1
        t.roster, t.practice_squad = sel, ps
        log["practice_squad"] += len(ps)
    # 7a. waivers on the cutdown (NFL): the cut players with under 4 accrued seasons are claimed, best first, by the first club in waiver priority (the order of
    # this draft, worst first) that she would improve at her position by CUT_CLAIM_MARGIN and can afford; the club drops its weakest player at that position
    # (and owes the dead money on her). The claimer takes the contract as it stands; if no one claims her the club that cut her pays what a release costs.
    claimed_ids = set()
    prio = T.priority_order(lg, year + 1, 0, {})
    n_claims = {t.id: 0 for t in teams}
    pend = {t.id: 0.0 for t in teams}                       # dead money a club will owe for its own waived players if none is claimed
    for p, club in held:
        pend[club] += EC.dead_charge(p)
    for p, club in sorted(held, key=lambda x: (-x[0].ovr, x[0].id)):
        for tid in prio:
            t2 = lg.by_id[tid]
            if tid == club or n_claims[tid] >= CUT_CLAIMS_MAX:
                continue
            at = [q for q in t2.roster if q.pos == p.pos]
            if not at:
                continue
            weakest = min(at, key=lambda q: (q.ovr, -q.id))
            if p.ovr < weakest.ovr + CUT_CLAIM_MARGIN:
                continue
            if EC.payroll(t2) + pend[tid] + p.salary - weakest.salary + EC.dead_charge(weakest) > EC.limit(t2) + 1e-9:
                continue
            t2.roster.remove(weakest)
            EC.release(t2, weakest)
            weakest.team_id, weakest.fa_years = None, 0
            cut.append(weakest)
            p.team_id = t2.id
            t2.roster.append(p)
            n_claims[tid] += 1
            claimed_ids.add(p.id)
            pend[club] -= EC.dead_charge(p)
            log["claims"] = log.get("claims", 0) + 1
            mv._event("waiver_claim", year=year, week=None, player=p.id, from_club=club, to_club=tid)
            break
    for p, club in held:
        if p.id not in claimed_ids:
            EC.release(lg.by_id[club], p)
            p.team_id, p.fa_years = None, 0
            cut.append(p)
            log["cut"] += 1
    log["waived"] = len(held)

    # the market for next year: everyone not signed, the best of them kept (the rest leave football; players who were already part of the
    # league leave as retired, so their cards are kept, and camp invitees who never made a roster are simply gone)
    market = [p for pos in POSITIONS for p in by_pos[pos]] + leftovers + cut
    market.sort(key=lambda p: (-p.ovr, p.id))
    keep_market = market[:rm.market_size]
    for p in market[rm.market_size:]:
        if p.card is not None:                              # already part of the league: leaves as retired, her card kept
            p.retired = True
            IJ.clear_on_exit(p)
        elif p.draft_year is not None:                      # a draft pick who did not make it: she is on record, so she keeps a card
            p.retired, p.team_id = True, None
            lg.retired_players.append(p)
        log["dropped"] += 1
    lg.free_agents = keep_market
    for t in order:
        rosters.refill_practice_squad(lg, t, rng)
    for t in teams:
        assert len(t.roster) == ROSTER_SIZE, (t.id, len(t.roster))
        assert len(t.practice_squad) == R.PRACTICE_SQUAD_SIZE, (t.id, len(t.practice_squad))
    refresh_strengths(lg)
    return log
