"""Game engine: plays one football game and returns a box score.

What it stores is DRIVE-LEVEL (option 2): every drive, team totals and player stats.
Inside, it plays the game play by play to get yardage, clock and turnovers right. A later
"option 3" only has to keep those plays: call simulate_game(..., record_plays=True).

Every number in EngineParams is a PLACEHOLDER dial calibrated to look like football
(see calibrate_engine.py), not a league rule.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import rules as R
from lineup import Lineup


def _logit(p: float) -> float:
    return math.log(p / (1.0 - p))


def _sig(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


@dataclass
class EngineParams:
    ref: float = 64.0                  # rating that counts as "average"
    home_edge: float = 1.0             # rating points added to every home unit (about 2 points of margin)
    # passing
    pass_rate_first: float = 0.46
    sack_base: float = 0.065
    sack_slope: float = 0.40           # per 10 rating points of pass rush over pass block
    comp_base: float = 0.66
    comp_slope: float = 0.30           # per 10 points of passing skill over coverage
    comp_press: float = 0.10           # pressure lowers completions
    comp_yds_base: float = 11.6
    comp_yds_slope: float = 0.07
    comp_yds_shape: float = 2.2
    int_base: float = 0.02
    int_slope: float = 0.30
    int_press: float = 0.06
    # running
    run_yds_base: float = 4.4
    run_yds_slope: float = 0.16
    run_shape: float = 1.8
    # turnovers on other plays
    fumble_run: float = 0.011
    fumble_pass: float = 0.004
    fumble_sack: float = 0.03
    # defensive scores on turnovers
    pick_six: float = 0.045
    fumble_td: float = 0.03
    # clock (seconds per play)
    t_run: float = 38.0
    t_complete: float = 30.0
    t_incomplete: float = 7.0
    t_sack: float = 31.0
    t_jitter: float = 6.0
    hurry_factor: float = 0.55
    # kicking
    fg_c: float = 5.94
    fg_slope: float = 0.10
    fg_acc: float = 0.025
    fg_pow: float = 0.012
    xp_c: float = 2.9
    punt_gross: float = 46.0
    punt_sd: float = 6.0
    punt_pow: float = 0.12
    punt_return: float = 6.0
    touchback_start: float = 31.0
    p_touchback: float = 0.60
    kick_return_start: float = 26.0
    # fourth down
    go_short_prob: float = 0.35


Q_SECS = 900
OT_SECS = R.OVERTIME_MINUTES_REGULAR * 60       # regular season: one overtime period, a tie if still level
OT_SECS_POST = R.OVERTIME_MINUTES_POST * 60     # postseason: periods of this length until someone wins
MAX_OT = 4

FIELDS_OFF = ("pass_att", "pass_cmp", "pass_yds", "pass_td", "pass_int", "sacked", "sack_yds", "rush_att",
              "rush_yds", "rush_td", "targets", "rec", "rec_yds", "rec_td", "fumbles_lost")


class _Side:
    """Everything one team needs during a game, precomputed."""
    __slots__ = ("lu", "feats", "p_sack", "p_comp", "p_int", "mean_cy", "mean_run", "name")


class GameResult:
    __slots__ = ("score", "ot_periods", "drives", "team", "players", "injured", "plays", "coin_flip_tiebreak")

    def __init__(self):
        self.score = [0, 0]
        self.ot_periods = 0
        self.drives: List[dict] = []
        self.team = [dict(plays=0, yards=0, pass_yds=0, rush_yds=0, first_downs=0, turnovers=0, sacks=0,
                          punts=0, third_att=0, third_conv=0, fourth_att=0, fourth_conv=0, top_secs=0,
                          drives=0, fga=0, fgm=0, pass_att=0, pass_cmp=0, rush_att=0, sack_yds=0)
                     for _ in range(2)]
        self.players: Dict[int, dict] = {}
        self.injured = []
        self.plays: Optional[list] = None
        self.coin_flip_tiebreak = False

    @property
    def winner_index(self):
        """0 or 1; None for a tie (regular season only)."""
        return None if self.score[0] == self.score[1] else (0 if self.score[0] > self.score[1] else 1)


class _Game:
    def __init__(self, home: Lineup, away: Lineup, rng: random.Random, P: EngineParams, neutral: bool,
                 record_plays: bool):
        self.rng = rng
        self.P = P
        self.res = GameResult()
        if record_plays:
            self.res.plays = []
        self.rec = record_plays
        h = 0.0 if neutral else P.home_edge
        self.sides = [self._side(home, h), self._side(away, 0.0)]
        for i in (0, 1):
            self._matchup(i)
        self.score = self.res.score
        self.quarter = 1
        self.t = Q_SECS
        self.ended = False

    # -- setup ----------------------------------------------------------------
    def _side(self, lu: Lineup, bonus: float) -> _Side:
        s = _Side()
        s.lu = lu
        s.feats = {f: getattr(lu, f) + bonus for f in lu.FEATURES}
        s.name = lu.team_id
        return s

    def _matchup(self, i: int):
        """Probabilities for side i on offense against the other side's defense."""
        P = self.P
        o, d = self.sides[i].feats, self.sides[1 - i].feats
        ref = P.ref
        blk = (d["pass_rush"] - o["pass_block"]) / 10.0
        skill = 0.45 * o["qb_acc"] + 0.55 * o["rec"]
        cov = (skill - d["coverage"]) / 10.0
        s = self.sides[i]
        s.p_sack = _sig(_logit(P.sack_base) + P.sack_slope * blk)
        s.p_comp = _sig(_logit(P.comp_base) + P.comp_slope * cov - P.comp_press * blk)
        s.p_int = _sig(_logit(P.int_base) - P.int_slope * (o["qb_aware"] - d["ball_skills"]) / 10.0 + P.int_press * blk)
        air = (0.5 * o["qb_arm"] + 0.5 * o["rec"] - d["coverage"]) / 10.0
        s.mean_cy = P.comp_yds_base * math.exp(P.comp_yds_slope * air)
        run = (0.5 * o["rb_run"] + 0.5 * o["run_block"] - d["run_stop"]) / 10.0
        s.mean_run = P.run_yds_base * math.exp(P.run_yds_slope * run)

    # -- stat helpers ---------------------------------------------------------
    def _p(self, player) -> dict:
        d = self.res.players.get(player.id)
        if d is None:
            d = {"pos": player.pos, "team": 0}
            self.res.players[player.id] = d
        return d

    @staticmethod
    def _bump(d: dict, key: str, n=1):
        d[key] = d.get(key, 0) + n

    def _pick(self, players, cum):
        x = self.rng.random() * cum[-1]
        for p, c in zip(players, cum):
            if x < c:
                return p
        return players[-1]

    # -- clock ----------------------------------------------------------------
    def _tick(self, secs: float, off: int):
        if self.in_ot or self.quarter in (2, 4):
            secs = min(secs, max(self.t, 0.0))      # the half or period cannot run past zero
        self.res.team[off]["top_secs"] += secs
        self.t -= secs
        if self.t <= 0:
            if self.in_ot:
                self.period_over = True
            elif self.quarter in (1, 3):
                self.quarter += 1
                self.t += Q_SECS
            else:
                self.period_over = True

    in_ot = False
    period_over = False

    def _hurry(self, off: int) -> bool:
        if self.in_ot:
            return False
        behind = self.score[off] < self.score[1 - off]
        if not behind:
            return False
        return (self.quarter == 4 and self.t < 300) or (self.quarter == 2 and self.t < 120)

    # -- kicks ----------------------------------------------------------------
    def _kick_start(self) -> int:
        P, rng = self.P, self.rng
        if rng.random() < P.p_touchback:
            return int(P.touchback_start)
        return int(min(45, max(12, rng.gauss(P.kick_return_start, 5.0))))

    def _fg_make(self, off: int, dist: float) -> bool:
        P = self.P
        f = self.sides[off].feats
        z = P.fg_c - P.fg_slope * dist + P.fg_acc * (f["k_acc"] - P.ref) + P.fg_pow * (f["k_pow"] - P.ref) * dist / 45.0
        return self.rng.random() < _sig(z)

    def _xp(self, off: int) -> int:
        f = self.sides[off].feats
        z = self.P.xp_c + 0.02 * (f["k_acc"] - self.P.ref)
        return 1 if self.rng.random() < _sig(z) else 0

    # -- one drive --------------------------------------------------------------
    def drive(self, off: int, start: int) -> dict:
        """Play one drive. Returns the drive record; updates score, clock and next start spot."""
        P, rng = self.P, self.rng
        res = self.res
        me, you = self.sides[off], self.sides[1 - off]
        lu_o, lu_d = me.lu, you.lu
        tm = res.team[off]
        opp = res.team[1 - off]
        pos, down, to_go = start, 1, 10
        plays = yards = 0
        t0 = self.t
        q0 = self.quarter
        secs_used = 0.0
        result = None
        pts = 0
        def_pts = 0
        next_start = None
        next_off = 1 - off
        start_secs_total = tm["top_secs"]
        tm["drives"] += 1

        while True:
            dist_goal = 100 - pos
            # ---- fourth down decision
            if down == 4:
                late_trail = (not self.in_ot and self.quarter == 4 and self.t < 420 and self.score[off] < self.score[1 - off])
                ot_trail = self.in_ot and self.score[off] < self.score[1 - off]
                fg_dist = dist_goal + 17
                fg_max = 56 + (me.feats["k_pow"] - P.ref) * 0.12
                kick_ok = fg_dist <= fg_max
                trailing_by = self.score[1 - off] - self.score[off]
                go = False
                if kick_ok:
                    if to_go <= 1 and dist_goal <= 8 and rng.random() < 0.35:
                        go = True
                    if late_trail and trailing_by > 3 and self.t < 240:
                        go = True
                    if ot_trail and trailing_by > 3:
                        go = True                       # in overtime a field goal does not catch a team more than 3 down
                else:
                    if pos >= 40 and to_go <= 2 and rng.random() < P.go_short_prob:
                        go = True
                    if ot_trail and pos >= 25 and to_go <= 8:
                        go = True                       # a trailing team in overtime has no use for a punt
                    if late_trail and pos >= 30:
                        go = True
                if not go:
                    if kick_ok:
                        tm["fga"] += 1
                        k = lu_o.k
                        kd = self._p(k)
                        self._bump(kd, "fga")
                        made = self._fg_make(off, fg_dist)
                        self._tick(5 + 0, off)
                        if made:
                            tm["fgm"] += 1
                            self._bump(kd, "fgm")
                            kd["fg_long"] = max(kd.get("fg_long", 0), fg_dist)
                            pts = 3
                            self.score[off] += 3
                            result = "FG"
                            next_start = self._kick_start()
                        else:
                            result = "MISSED_FG"
                            next_start = int(max(20, min(80, 107 - pos)))     # opponent takes over at the kick spot, at least their 20
                        break
                    # punt
                    tm["punts"] += 1
                    pd = self._p(lu_o.p)
                    self._bump(pd, "punts")
                    gross = rng.gauss(P.punt_gross, P.punt_sd) + P.punt_pow * (me.feats["p_pow"] - P.ref)
                    self._tick(8, off)
                    if pos + gross >= 100:
                        net_spot = 20
                        self._bump(pd, "punt_yds", int(100 - pos))
                    else:
                        ret = max(0.0, rng.gauss(P.punt_return, 4.0))
                        net_spot = int(min(60, max(1, 100 - (pos + gross) + ret)))
                        self._bump(pd, "punt_yds", int(gross))
                    result = "PUNT"
                    next_start = net_spot
                    break
                tm["fourth_att"] += 1

            if down == 3:
                tm["third_att"] += 1

            # ---- choose run or pass
            if down == 1:
                pr = P.pass_rate_first
            elif down == 2:
                pr = min(0.72, max(0.38, 0.35 + 0.04 * to_go))
            else:
                pr = min(0.88, max(0.30, 0.30 + 0.065 * to_go))
            if not self.in_ot and self.quarter == 4:
                lead = self.score[off] - self.score[1 - off]
                if lead >= 8 and self.t < 420:
                    pr *= 0.65
                elif lead <= -8:
                    pr = min(0.92, pr + 0.20)
            hurry = self._hurry(off)
            hf = P.hurry_factor if hurry else 1.0
            jit = rng.gauss(0.0, P.t_jitter)

            turnover = False
            play_yards = 0
            if rng.random() < pr:
                # ---------------- pass play ----------------
                qb = lu_o.qb
                qd = self._p(qb)
                if rng.random() < me.p_sack:
                    sy = -int(max(1, min(15, rng.gauss(6.5, 2.5))))
                    play_yards = sy
                    tm["sack_yds"] += -sy
                    opp["sacks"] += 1
                    self._bump(qd, "sacked")
                    self._bump(qd, "sack_yds", -sy)
                    sacker = self._pick(lu_d.rushers, lu_d.rush_cum)
                    self._bump(self._p(sacker), "sacks")
                    self._tick(max(5.0, (P.t_sack + jit) * hf), off)
                    secs_used += 0
                    if rng.random() < P.fumble_sack:
                        turnover = "FUMBLE"
                        self._bump(qd, "fumbles_lost")
                else:
                    tm["pass_att"] += 1
                    self._bump(qd, "pass_att")
                    target = self._pick(lu_o.targets, lu_o.target_cum)
                    td_ = self._p(target)
                    self._bump(td_, "targets")
                    u = rng.random()
                    if u < me.p_int:
                        turnover = "INT"
                        self._bump(qd, "pass_int")
                        air = int(max(0, min(dist_goal, rng.gauss(10, 7))))
                        play_yards = air
                        picker = self._pick(lu_d.pickers, lu_d.pick_cum)
                        self._bump(self._p(picker), "ints")
                        self._tick(max(4.0, 8 * hf), off)
                    elif u < me.p_int + me.p_comp:
                        y = int(rng.gammavariate(P.comp_yds_shape, me.mean_cy / P.comp_yds_shape))
                        y = min(y, dist_goal)
                        play_yards = y
                        tm["pass_cmp"] += 1
                        tm["pass_yds"] += y
                        self._bump(qd, "pass_cmp")
                        self._bump(qd, "pass_yds", y)
                        self._bump(td_, "rec")
                        self._bump(td_, "rec_yds", y)
                        tk = self._pick(lu_d.tacklers, lu_d.tackle_cum)
                        self._bump(self._p(tk), "tackles")
                        self._tick(max(4.0, (P.t_complete + jit) * hf), off)
                        if y >= dist_goal:
                            self._bump(qd, "pass_td")
                            self._bump(td_, "rec_td")
                        elif rng.random() < P.fumble_pass:
                            turnover = "FUMBLE"
                            self._bump(td_, "fumbles_lost")
                    else:
                        self._tick(max(3.0, (P.t_incomplete + jit * 0.3) * (0.8 if hurry else 1.0)), off)
            else:
                # ---------------- run play ----------------
                carrier = self._pick(lu_o.carriers, lu_o.carry_cum)
                cd = self._p(carrier)
                mean = me.mean_run
                y = int(round(rng.gammavariate(P.run_shape, (mean + 2.0) / P.run_shape) - 2.0))
                y = min(y, dist_goal)
                play_yards = y
                tm["rush_yds"] += y
                tm["rush_att"] += 1
                self._bump(cd, "rush_att")
                self._bump(cd, "rush_yds", y)
                tk = self._pick(lu_d.tacklers, lu_d.tackle_cum)
                self._bump(self._p(tk), "tackles")
                self._tick(max(5.0, (P.t_run + jit) * hf), off)
                if y >= dist_goal:
                    self._bump(cd, "rush_td")
                elif rng.random() < P.fumble_run:
                    turnover = "FUMBLE"
                    self._bump(cd, "fumbles_lost")

            plays += 1
            tm["plays"] += 1
            if turnover == "INT":
                pass
            else:
                yards += play_yards
                tm["yards"] += play_yards
            pos_after = pos + play_yards
            if pos_after <= 0 and not turnover:
                # tackled in the end zone: safety, and the scoring team gets the ball after a free kick
                self.score[1 - off] += 2
                def_pts = 2
                result = "SAFETY"
                next_start = int(min(45, max(25, rng.gauss(35, 5))))
                break

            if self.rec:
                res.plays.append((off, q0, down, to_go, pos, play_yards, turnover))

            # ---------------- what happened ----------------
            if turnover:
                tm["turnovers"] += 1
                result = turnover
                if turnover == "INT":
                    spot = pos_after
                    ret = int(max(0, rng.gauss(9, 8)))
                    dstart = 20 if spot >= 99 else 100 - spot + ret
                    if rng.random() < P.pick_six:
                        result = "INT_TD"
                        self.score[1 - off] += 6
                        def_pts = 6 + self._xp(1 - off)
                        self.score[1 - off] += def_pts - 6
                        next_start = self._kick_start()
                        next_off = off
                    else:
                        next_start = int(min(99, max(1, dstart)))
                else:
                    if rng.random() < P.fumble_td:
                        result = "FUMBLE_TD"
                        self.score[1 - off] += 6
                        def_pts = 6 + self._xp(1 - off)
                        self.score[1 - off] += def_pts - 6
                        next_start = self._kick_start()
                        next_off = off
                    else:
                        next_start = int(min(99, max(1, 100 - pos_after)))
                break

            if pos_after >= 100:
                tm["first_downs"] += 1
                if down == 3:
                    tm["third_conv"] += 1
                if down == 4:
                    tm["fourth_conv"] += 1
                result = "TD"
                pts = 6
                self.score[off] += 6
                xp = self._xp(off)
                self.score[off] += xp
                pts += xp
                # credit the touchdown to the QB/receiver/runner already counted in play stats
                next_start = self._kick_start()
                break

            if play_yards >= to_go and play_yards > 0:
                tm["first_downs"] += 1
                if down == 3:
                    tm["third_conv"] += 1
                if down == 4:
                    tm["fourth_conv"] += 1
                down, to_go = 1, min(10, 100 - pos_after)
            else:
                to_go -= play_yards
                down += 1
                if down == 5:
                    result = "DOWNS"
                    next_start = int(min(99, max(1, 100 - pos_after)))
                    pos = pos_after
                    break
            pos = pos_after
            if self.period_over:
                result = "END_PERIOD"
                break

        rec = dict(team=me.name, side=off, quarter=q0, start=start, plays=plays, yards=yards,
                   secs=int(tm["top_secs"] - start_secs_total), result=result, pts=pts, def_pts=def_pts)
        res.drives.append(rec)
        self.next_start = next_start
        self.next_off = next_off
        return rec


def simulate_game(home: Lineup, away: Lineup, rng: random.Random, params: EngineParams = None,
                  neutral: bool = False, record_plays: bool = False, allow_tie: bool = False) -> GameResult:
    """Play a whole game. Index 0 is the home team, 1 the away team. allow_tie=True is a regular-season game, which can end level
    after overtime; the default plays on until someone wins (postseason)."""
    P = params or EngineParams()
    g = _Game(home, away, rng, P, neutral, record_plays)
    res = g.res
    off = rng.randrange(2)                  # who receives the opening kickoff
    receive_first = off
    start = g._kick_start()
    half_done = False
    while True:
        g.period_over = False
        d = g.drive(off, start)
        off, start = g.next_off, g.next_start
        if g.period_over:
            if g.quarter == 2 and not half_done:
                half_done = True
                g.quarter = 3
                g.t = Q_SECS
                g.period_over = False
                off = 1 - receive_first
                start = g._kick_start()
                continue
            break

    # ---- overtime (NFL rule: both teams get a possession; regular season ends in a tie if still level)
    if g.score[0] == g.score[1]:
        _overtime(g, rng, allow_tie)

    # attach team labels to player stat blocks
    side_of = {}
    for i in (0, 1):
        lu = g.sides[i].lu
        for grp in (lu.rbs, lu.wrs, [lu.te, lu.qb, lu.k, lu.p], lu.ol, lu.dl, lu.lb, lu.cb, lu.s):
            for p in grp:
                side_of[p.id] = i
    for pid, d in res.players.items():
        d["team"] = side_of.get(pid, 0)
    return res


def _overtime(g: _Game, rng: random.Random, allow_tie: bool = False):
    """NFL overtime. Each team gets a possession even if the first scores a touchdown (a defensive touchdown on the first possession
    ends it); once both have had one, the next score wins. Regular season: one 10-minute period, a tie if still level. Postseason:
    15-minute periods until someone leads when a period ends (a seeded kick-off decides after MAX_OT periods, recorded as such)."""
    res = g.res
    g.in_ot = True
    off = rng.randrange(2)
    start = g._kick_start()
    possessions = 0
    periods = 1 if allow_tie else MAX_OT
    secs = OT_SECS if allow_tie else OT_SECS_POST
    for period in range(1, periods + 1):
        res.ot_periods = period
        g.t = secs
        g.period_over = False
        if start is None:
            start = g._kick_start()
        while True:
            d = g.drive(off, start)
            possessions += 1
            off, start = g.next_off, g.next_start
            if possessions == 1:
                if d["result"] in ("INT_TD", "FUMBLE_TD"):
                    return
            elif g.score[0] != g.score[1]:
                return
            if g.period_over:
                break
        if g.score[0] != g.score[1]:
            return
    if allow_tie:
        return                                          # level after the period: a tie
    # still level after the extra periods: decided by a seeded kick-off, recorded as such
    res.coin_flip_tiebreak = True
    i = rng.randrange(2)
    g.score[i] += 3
