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
import injuries as IJ
import lineup as LU
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
    # rules version 2 (new leagues only; version 1 draws no extra random number, so it plays exactly as before)
    rules: int = 1
    pen_rate: float = 0.085            # chance a scrimmage down is wiped out by an accepted penalty (NFL: about 11 a game between the two teams)
    timeout_prob: float = 0.75         # a trailing team with a timeout left, late in a half, calls one after a play that kept the clock running
    timeout_refund: float = 12.0       # the most seconds of clock a timeout saves
    # rules version 3 (new leagues only): the clock at the end of a half
    late_secs: float = 22.0            # a team in field-goal range that needs the points kicks, or spikes the ball to stop the clock, when this little time is left in a half
    spike_secs: float = 3.0
    half_timeout_prob: float = 0.5     # the chance the team with the ball calls a timeout after a play that kept the clock running, at the end of the first half
    kneel_clock: float = 40.0          # a kneel-down lets about this much clock run (the play clock)
    kneel_left: float = 3.0            # a timeout called after a kneel saves all but this much of it
    # rules version 4 (new leagues only): players are hurt during the game
    inj_play: float = 0.034            # the chance that a player on the field is hurt on a scrimmage play (fitted so a club has about as many injuries a season, near 33, as the old after-the-game roll gave); she leaves and a healthy player from the bench takes her place
    # rules version 5 (new leagues only): kickoffs and conversions are plays of their own
    ko_return_mean: float = 21.0       # yards a returned kickoff is run back from where it is caught
    ko_return_sd: float = 8.0
    ko_td: float = 0.007               # a returned kickoff goes all the way
    ko_fumble: float = 0.006           # the returner fumbles and the kicking team falls on it
    ko_penalty: float = 0.05           # a foul on the return: ten yards back for the receivers (70%), five forward for them if the kicking team is flagged
    onside_rec: float = 0.13           # the kicking team gets an expected onside kick back
    onside_surprise: float = 0.004     # a surprise onside kick tried at any other time
    onside_surprise_rec: float = 0.35
    two_make: float = 0.48             # a two-point try is good (NFL since 2015: about 48%); the units move it a little
    two_rand: float = 0.01             # a coach goes for two with no reason in the chart


Q_SECS = 900
OT_SECS = R.OVERTIME_MINUTES_REGULAR * 60       # regular season: one overtime period, a tie if still level
OT_SECS_POST = R.OVERTIME_MINUTES_POST * 60     # postseason: periods of this length until someone wins
MAX_OT = 4


# The penalty list (rules version 2): (name, who is fouled: 0 offense / 1 defense, yards (0 = spot foul), automatic first down, when: "pre" snap or "live", plays: "any"/"pass"/"run", weight, who commits it).
# Weights follow how often the NFL calls each one. Only accepted penalties are modelled: the down is wiped out (no play), the yardage is enforced, and the down is replayed unless the
# yards or the automatic first down earn a new one. Declined and offsetting penalties, and penalties on kicks, are not modelled.
PENALTIES = (
    ("Offensive holding", 0, 10, False, "live", "any", 14, "ol"),
    ("False start", 0, 5, False, "pre", "any", 14, "ol"),
    ("Offside", 1, 5, False, "pre", "any", 7, "dl"),
    ("Defensive pass interference", 1, 0, True, "live", "pass", 6, "cb"),
    ("Defensive holding", 1, 5, True, "live", "any", 6, "cb"),
    ("Illegal formation", 0, 5, False, "pre", "any", 3, "ol"),
    ("Delay of game", 0, 5, False, "pre", "any", 5, "qb"),
    ("Unnecessary roughness", 1, 15, True, "live", "any", 4, "lb"),
    ("Roughing the passer", 1, 15, True, "live", "pass", 3, "dl"),
    ("Neutral zone infraction", 1, 5, False, "pre", "any", 4, "dl"),
    ("Encroachment", 1, 5, False, "pre", "any", 3, "dl"),
    ("Illegal block in the back", 0, 10, False, "live", "any", 3, "rb"),
    ("Ineligible receiver downfield", 0, 5, False, "live", "pass", 2, "ol"),
    ("Illegal motion", 0, 5, False, "pre", "any", 2, "wr"),
    ("Face mask", 1, 15, True, "live", "any", 3, "lb"),
    ("Illegal use of hands", 1, 5, True, "live", "any", 3, "s"),
    ("Offensive pass interference", 0, 10, False, "live", "pass", 2, "wr"),
    ("Illegal contact", 1, 5, True, "live", "pass", 2, "cb"),
    ("Tripping", 0, 10, False, "live", "run", 1, "ol"),
    ("Too many men on the field", 1, 5, False, "pre", "any", 1, None),
)
PENALTY_NAMES = tuple(p[0] for p in PENALTIES)

FIELDS_OFF = ("pass_att", "pass_cmp", "pass_yds", "pass_td", "pass_int", "sacked", "sack_yds", "rush_att",
              "rush_yds", "rush_td", "targets", "rec", "rec_yds", "rec_td", "fumbles_lost")


class _Side:
    """Everything one team needs during a game, precomputed."""
    __slots__ = ("lu", "feats", "p_sack", "p_comp", "p_int", "mean_cy", "mean_run", "name", "bonus")


class GameResult:
    __slots__ = ("score", "ot_periods", "drives", "team", "players", "injured", "plays", "coin_flip_tiebreak")

    def __init__(self):
        self.score = [0, 0]
        self.ot_periods = 0
        self.drives: List[dict] = []
        self.team = [dict(plays=0, yards=0, pass_yds=0, rush_yds=0, first_downs=0, turnovers=0, sacks=0,
                          punts=0, third_att=0, third_conv=0, fourth_att=0, fourth_conv=0, top_secs=0,
                          drives=0, fga=0, fgm=0, pass_att=0, pass_cmp=0, rush_att=0, sack_yds=0, pen=0, pen_yds=0)
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
                 record_plays: bool, injuries: bool = False):
        self.rng = rng
        self.inj_on = injuries and P.rules >= 4          # players can be hurt during the game (rules version 4); the lineups are then copies that lose players
        self.scrim = False                               # the last thing that happened was a scrimmage play: the next look at the game rolls for an injury
        self.ko_next = False                             # (rules version 5) the drive ended in a score, so a kickoff comes next
        self.free = False                                # ... and it is a free kick after a safety
        self.over = False                                # a kickoff returned for a touchdown in overtime ends the game
        self.ot_poss = 0                                 # overtime possessions played so far (a touchdown in sudden death needs no conversion)
        self.side_of = {}
        if P.rules >= 4:
            home, away = LU.clone(home), LU.clone(away)
            for i, lu in enumerate((home, away)):
                for pl in LU.on_field(lu) + [lu.k, lu.p]:
                    self.side_of[pl.id] = i
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
        self.to = [3, 3]                    # timeouts left, home and away (rules version 2): three a half, two in overtime

    # -- setup ----------------------------------------------------------------
    def _side(self, lu: Lineup, bonus: float) -> _Side:
        s = _Side()
        s.lu = lu
        s.feats = {f: getattr(lu, f) + bonus for f in lu.FEATURES}
        s.bonus = bonus
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

    def _log(self, off, down, to_go, pos, yards, turnover, kind, a=None, b=None, c=None):
        """Record one play (only when play recording is on; it reads the game and never draws a random number). Kinds: PC completion
        (passer, target, tackler), PI incomplete (passer, target), SK sack (passer, sacker), IN interception (passer, target, picker),
        RU run (carrier, tackler), FG kick (kicker, 1 if good, distance), PU punt (punter), and in rules version 2 PN penalty (penalty number, 0 if the offense
        was fouled and 1 if the defense, the offender) and TO timeout (the team that called it, timeouts it has left). After the usual seven fields come the kind,
        the three players, the quarter and seconds left once the play is over, whether it is overtime, and which drive of the game it belongs to."""
        rec = (off, self.quarter, down, to_go, pos, yards, turnover, kind, a, b, c, self.quarter, int(max(self.t, 0)), bool(self.in_ot), len(self.res.drives))
        self.res.plays.append(rec + ((self.to[0], self.to[1]) if self.P.rules >= 2 else ()))     # version 2 adds each side's timeouts left

    # -- injuries during the game (rules version 4) -------------------------------------------------------------
    def _injury_check(self, off: int, down: int, to_go: int, pos: int):
        """Called as the next play is about to be chosen: if the last thing was a scrimmage play, a player on the field may have been hurt in it. She leaves, the best healthy player
        at her position comes on (the unit ratings are worked out again), and the play log says so. With no one on the bench she plays on and nothing is recorded."""
        if not self.scrim:
            return
        self.scrim = False
        P, rng = self.P, self.rng
        if rng.random() >= P.inj_play:
            return
        cands = [(i, p) for i in (0, 1) for p in LU.on_field(self.sides[i].lu) if p.weeks_out == 0]
        i, hurt = rng.choices(cands, [IJ.POS_RISK.get(p.pos, 1.0) for _, p in cands])[0]
        kind, games = IJ.draw_kind(rng)
        sub = LU.substitute(self.sides[i].lu, hurt)
        if sub is None:
            return
        self.res.injured.append((hurt, kind, games, i))
        self._p(hurt)
        self._p(sub)
        self.side_of[sub.id] = i
        s = self.sides[i]
        s.feats = {f: getattr(s.lu, f) + s.bonus for f in s.lu.FEATURES}
        self._matchup(0)
        self._matchup(1)
        if self.rec:
            self._log(off, down, to_go, pos, 0, False, "IJ", hurt.id, sub.id, IJ.KIND_NAMES.index(kind))

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
            return True                         # overtime is played at the two-minute pace (NFL: no-huddle, clock managed for a last kick)
        behind = self.score[off] < self.score[1 - off]
        if self.P.rules >= 3:
            if self.quarter == 2 and self.t < 120:
                return True                     # the end of the first half is played at the two-minute pace by any offense: the points are there to be had
            if self.quarter == 4 and self.t < 120 and self.score[off] == self.score[1 - off]:
                return True
        if not behind:
            return False
        return (self.quarter == 4 and self.t < 300) or (self.quarter == 2 and self.t < 120)

    # -- penalties and timeouts (rules version 2) -------------------------------
    def _penalty(self, off: int, is_pass: bool, down: int, to_go: int, pos: int, hurry: bool):
        """Draw an accepted penalty for this scrimmage down, or None. Returns (number, fouled side, signed yards for the offense, first down, culprit id or -1)."""
        P, rng = self.P, self.rng
        if rng.random() >= P.pen_rate:
            return None
        kinds = [(i, p) for i, p in enumerate(PENALTIES) if p[5] == "any" or p[5] == ("pass" if is_pass else "run")]
        x = rng.random() * sum(p[6] for _, p in kinds)
        pick = kinds[-1]
        for i, p in kinds:
            x -= p[6]
            if x < 0:
                pick = (i, p)
                break
        i, (name, side, yds, afd, when, _plays, _w, who) = pick
        lu = self.sides[off if side == 0 else 1 - off].lu
        group = {"ol": lu.ol, "dl": lu.dl, "lb": lu.lb, "cb": lu.cb, "s": lu.s, "rb": lu.rbs, "wr": lu.wrs, "qb": [lu.qb]}.get(who)
        who_ = rng.choice(group) if group else None
        if who_ is not None:
            self._p(who_)                                   # the offender is named in the box even with no other stat (a lookup, no random number)
        return i, side, yds, afd, who_.id if who_ is not None else -1

    def _timeout_check(self, off: int, down: int, to_go: int, pos: int, spent: float) -> bool:
        """After a play that kept the clock running: late in a half, the trailing team (within two scores) with a timeout left may call one and save some of the clock.
        Rules version 3: at the end of the first half the team with the ball calls it, whatever the score. Returns True if a timeout was called."""
        P = self.P
        q = self.quarter
        if self.in_ot or self.period_over or not ((q == 2 and self.t <= 120) or (q == 4 and self.t <= 300)):
            return False
        a, b = self.score[0], self.score[1]
        if P.rules >= 3 and q == 2 and self.to[off] > 0:
            trail = off
        else:
            if a == b or abs(a - b) > 16:
                return False
            trail = 0 if a < b else 1
        if self.to[trail] <= 0 or self.rng.random() >= (P.half_timeout_prob if P.rules >= 3 and q == 2 and trail == off else P.timeout_prob):
            return False
        self.to[trail] -= 1
        back = min(P.timeout_refund, max(0.0, spent))
        self.t += back
        self.res.team[off]["top_secs"] -= back
        if self.rec:
            self._log(off, down, to_go, pos, 0, False, "TO", trail, self.to[trail])
        return True

    # -- kicks ----------------------------------------------------------------
    def _kick_start(self) -> int:
        P, rng = self.P, self.rng
        if rng.random() < P.p_touchback:
            return int(P.touchback_start)
        return int(min(45, max(12, rng.gauss(P.kick_return_start, 5.0))))

    # -- kickoffs and conversions (rules version 5) --------------------------------------------------------
    def _kickoff(self, rcv: int, free: bool = False):
        """The kickoff (or the free kick after a safety) to side rcv: a play of its own in the log (kind KO). Returns (side with the ball, its start spot).
        Outcomes (the code in the log): 0 touchback, 1 returned, 2 returned for a touchdown, 3 fumbled on the return and recovered by the kicking team,
        4 a foul on the return (the start spot moves), 5 an onside kick the kicking team recovers, 6 an onside kick the receivers recover."""
        P, rng = self.P, self.rng
        while True:
            kick = 1 - rcv
            klu, rlu = self.sides[kick].lu, self.sides[rcv].lu
            kicker = klu.k
            lead = self.score[kick] - self.score[rcv]
            onside = surprise = False
            if not free and not self.in_ot:
                if self.quarter == 4 and -16 <= lead < 0:
                    pr = 0.9 if self.t <= 180 else 0.35 if self.t <= 300 else 0.0
                    onside = pr > 0 and rng.random() < pr
                if not onside and rng.random() < P.onside_surprise:
                    onside = surprise = True
            tackler = None
            rets = [rlu.wrs[-1], rlu.rbs[-1], rlu.cb[-1]]
            who = rets[0 if rng.random() < 0.4 else 1 if rng.random() < 0.6 else 2]
            off, start, landing, code = rcv, 0, 0, 1
            if onside:
                spot = int(min(55, max(40, rng.gauss(47, 3))))          # where the ball is picked up, in the kicking team's frame
                if rng.random() < (P.onside_surprise_rec if surprise else P.onside_rec):
                    off, start, code = kick, spot, 5
                    who = rng.choice(klu.wrs + klu.cb)
                else:
                    start, code = 100 - spot, 6
                    tackler = klu.tacklers[rng.randrange(len(klu.tacklers))]
                landing = 100 - spot
            elif rng.random() < P.p_touchback:
                start, code = int(P.touchback_start), 0
                landing = -min(9, int(abs(rng.gauss(3, 2))))
            else:
                start = int(min(45, max(12, rng.gauss(P.kick_return_start, 5.0))))
                landing = max(1, start - int(max(0.0, rng.gauss(P.ko_return_mean, P.ko_return_sd))))
                x = rng.random()
                if x < P.ko_td:
                    code, start = 2, 100
                elif x < P.ko_td + P.ko_fumble:
                    off, start, code = kick, 100 - start, 3
                elif x < P.ko_td + P.ko_fumble + P.ko_penalty:
                    code = 4
                    start = max(1, start - 10) if rng.random() < 0.7 else min(60, start + 5)
                if code in (1, 3, 4):
                    tackler = klu.tacklers[rng.randrange(len(klu.tacklers))]      # (on a fumble, the kicking team's man who fell on the ball)
            if self.rec:
                self._p(kicker), self._p(who)
                if tackler is not None:
                    self._p(tackler)
                self._log(off, 2 if free else 1, 10, min(start, 99) if code != 2 else min(landing, 99), landing, code, "KO", kicker.id, who.id, tackler.id if tackler is not None else -1)
            if code != 2:
                return off, start
            # returned for a touchdown: the receivers score, a conversion is tried, and the kick comes back the other way
            self.score[rcv] += 6
            conv = self._try(rcv)
            self.res.drives.append(dict(team=self.sides[rcv].name, side=rcv, quarter=self.quarter, start=max(1, landing), plays=0, yards=0, secs=0,
                                        result="KICK_TD", pts=6 + conv, def_pts=0))
            if self.in_ot:
                self.over = True
                return rcv, 25
            rcv, free = kick, False

    def _try(self, scorer: int) -> int:
        """The conversion after a touchdown by side scorer, called with the six points already on the board; returns the points it adds (0, 1 or 2) and logs it
        as an extra-point kick (XP) or a two-point try (2P). A late chart for the trailing team, plus the odd gambler, decides when to go for two."""
        P, rng = self.P, self.rng
        d = self.score[scorer] - self.score[1 - scorer]
        if self.in_ot and self.ot_poss >= 2:
            return 0                                                    # sudden death: the touchdown ends the game
        if not self.in_ot and self.quarter == 4 and self.t <= 0 and (d >= 1 or d <= -3):
            return 0                                                    # time has run out and no conversion could change who wins
        lu = self.sides[scorer].lu
        late = not self.in_ot and self.quarter == 4 and self.t <= 600
        go = (late and d in (-2, -5, -9) and rng.random() < 0.9) or (not (late and d in (-2, -5, -9)) and rng.random() < P.two_rand)
        if not go:
            good = self._xp(scorer)
            if self.rec:
                self._p(lu.k)
                self._log(scorer, 1, 10, 85, 33, False, "XP", lu.k.id, good, 33)
            self.score[scorer] += good
            return good
        of, df = self.sides[scorer].feats, self.sides[1 - scorer].feats
        edge = (of["rec"] + of["run_block"] + of["qb_acc"]) / 3.0 - (df["coverage"] + df["run_stop"] + df["pass_rush"]) / 3.0
        good = 1 if rng.random() < min(0.7, max(0.25, P.two_make + 0.004 * edge)) else 0
        if rng.random() < 0.6:
            a, b = lu.qb, self._pick(lu.targets, lu.target_cum)
        else:
            a, b = self._pick(lu.carriers, lu.carry_cum), None
        if self.rec:
            self._p(a)
            if b is not None:
                self._p(b)
            self._log(scorer, 1, 2, 98, 2, False, "2P", a.id, b.id if b is not None else -1, good)
        self.score[scorer] += 2 * good
        return 2 * good

    def _after_score(self):
        """The spot the next drive starts from after a score: drawn at once before rules version 5; from version 5 the kickoff is a play of its own, played when the drive is over."""
        if self.P.rules < 5:
            return self._kick_start()
        self.ko_next = True
        return None

    def _conv(self, scorer: int) -> int:
        """The conversion after a touchdown, added to the score; returns its points."""
        if self.P.rules >= 5:
            return self._try(scorer)
        x = self._xp(scorer)
        self.score[scorer] += x
        return x

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
        self.ko_next = self.free = False
        tm["drives"] += 1
        stopped = True                                  # is the clock stopped? (rules version 3: a spike is only worth it when it is running)

        while True:
            if self.inj_on:
                self._injury_check(off, down, to_go, pos)
                lu_o, lu_d = me.lu, you.lu                  # (the lineups are the same objects; kept for clarity)
            dist_goal = 100 - pos
            force_kick = False
            if P.rules >= 3 and not self.in_ot and self.quarter in (2, 4):
                # ---- the end of a half (rules version 3): run the clock out, kick for the points, or stop the clock to be able to
                lead = self.score[off] - self.score[1 - off]
                in_range = dist_goal + 17 <= 56 + (me.feats["k_pow"] - P.ref) * 0.12
                if self.quarter == 4 and lead > 0 and pos >= 3 and self.t > 0:
                    kneels, theirs = 5 - down, self.to[1 - off]
                    if max(0, kneels - theirs) * P.kneel_clock + min(kneels, theirs) * P.kneel_left >= self.t + 2:
                        qb = lu_o.qb
                        qd = self._p(qb)
                        tm["rush_att"] += 1
                        tm["rush_yds"] -= 1
                        tm["plays"] += 1
                        tm["yards"] -= 1
                        self._bump(qd, "rush_att")
                        self._bump(qd, "rush_yds", -1)
                        t_before = self.t
                        self._tick(P.kneel_clock, off)
                        if self.rec:
                            self._log(off, down, to_go, pos, -1, False, "KN", qb.id)
                        plays += 1
                        yards -= 1
                        pos, down, to_go = pos - 1, down + 1, to_go + 1
                        if self.period_over:
                            result = "END_PERIOD"
                            break
                        if down == 5:
                            result = "DOWNS"
                            next_start = int(min(99, max(1, 100 - pos)))
                            break
                        stopped = False
                        if self.to[1 - off] > 0 and rng.random() < P.timeout_prob:      # the trailing team stops the clock after the kneel
                            back = max(0.0, (t_before - self.t) - P.kneel_left)
                            self.to[1 - off] -= 1
                            self.t += back
                            tm["top_secs"] -= back
                            stopped = True
                            if self.rec:
                                self._log(off, down, to_go, pos, 0, False, "TO", 1 - off, self.to[1 - off])
                        continue
                need_pts = self.quarter == 2 or lead <= 0
                want_fg = in_range and (self.quarter == 2 or -3 <= lead <= 0)
                spike = False
                if want_fg and self.t <= P.late_secs:
                    if not stopped and self.t > 10 and down <= 3:
                        spike = True
                    else:
                        force_kick = True
                elif need_pts and not stopped and self.t <= 28 and down <= 2 and pos >= 45:
                    spike = True
                if spike:
                    qb = lu_o.qb
                    qd = self._p(qb)
                    tm["pass_att"] += 1
                    tm["plays"] += 1
                    self._bump(qd, "pass_att")
                    self._tick(P.spike_secs, off)
                    if self.rec:
                        self._log(off, down, to_go, pos, 0, False, "SP", qb.id)
                    plays += 1
                    down += 1
                    stopped = True
                    if self.period_over:
                        result = "END_PERIOD"
                        break
                    continue
            # ---- fourth down decision
            if down == 4 or force_kick:
                late_trail = (not self.in_ot and self.quarter == 4 and self.t < 420 and self.score[off] < self.score[1 - off])
                ot_trail = self.in_ot and self.score[off] < self.score[1 - off]
                fg_dist = dist_goal + 17
                fg_max = 56 + (me.feats["k_pow"] - P.ref) * 0.12
                kick_ok = fg_dist <= fg_max
                trailing_by = self.score[1 - off] - self.score[off]
                go = False
                if force_kick:
                    pass
                elif kick_ok:
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
                    if self.in_ot and self.score[off] == self.score[1 - off] and self.t < 180 and pos >= 45 and to_go <= 3:
                        go = True                       # level in the last minutes of overtime: a team goes for it rather than settle for a tie
                if not go:
                    if kick_ok:
                        tm["fga"] += 1
                        k = lu_o.k
                        kd = self._p(k)
                        self._bump(kd, "fga")
                        made = self._fg_make(off, fg_dist)
                        self._tick(5 + 0, off)
                        if self.rec:
                            self._log(off, down, to_go, pos, fg_dist, False, "FG", k.id, 1 if made else 0, int(fg_dist))
                        if made:
                            tm["fgm"] += 1
                            self._bump(kd, "fgm")
                            kd["fg_long"] = max(kd.get("fg_long", 0), fg_dist)
                            pts = 3
                            self.score[off] += 3
                            result = "FG"
                            next_start = self._after_score()
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
                    if self.rec:
                        self._log(off, 4, to_go, pos, int(min(gross, 100 - pos)), False, "PU", lu_o.p.id)
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
            is_pass = rng.random() < pr                      # the one draw that decides run or pass (it used to sit in the branch below)

            if P.rules >= 2:                                 # an accepted penalty wipes the down out: no play, the yardage is enforced, the down is replayed or a new one earned
                pen = self._penalty(off, is_pass, down, to_go, pos, hurry)
                if pen is not None:
                    pi, side, pyds, afd, culprit = pen
                    if down == 3:
                        tm["third_att"] -= 1
                    if down == 4:
                        tm["fourth_att"] -= 1
                    spot_foul = pyds == 0
                    if side == 0:                            # the offense is fouled against: it goes back, half the distance to its own goal at most
                        gain = -min(pyds, pos // 2)
                        new_pos, new_down, new_togo = pos + gain, down, to_go - gain
                        first = False
                        pen_team = off
                    else:                                    # the defense is fouled against: the offense goes forward, half the distance to the goal at most
                        if spot_foul:
                            gain = int(max(5, min(40, rng.gauss(17, 9))))
                            gain = min(gain, max(0, dist_goal - 1))
                        else:
                            gain = min(pyds, dist_goal // 2)
                        new_pos = pos + gain
                        first = afd or gain >= to_go
                        new_down, new_togo = (1, min(10, 100 - new_pos)) if first else (down, to_go - gain)
                        pen_team = 1 - off
                    tm_pen = res.team[pen_team]
                    tm_pen["pen"] += 1
                    tm_pen["pen_yds"] += abs(gain)
                    live = PENALTIES[pi][4] == "live"
                    self._tick(max(3.0, (9.0 if live else 4.0) * hf), off)
                    if self.rec:
                        self._log(off, down, to_go, pos, gain, False, "PN", pi, side, culprit)
                    pos, down, to_go = new_pos, new_down, new_togo
                    stopped = True
                    if self.period_over:
                        result = "END_PERIOD"
                        break
                    continue
                t_before, q_before = self.t, self.quarter

            turnover = False
            play_yards = 0
            kind = a_ = b_ = c_ = None
            if is_pass:
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
                    kind, a_, b_ = "SK", qb.id, sacker.id
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
                        kind, a_, b_, c_ = "IN", qb.id, target.id, picker.id
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
                        kind, a_, b_, c_ = "PC", qb.id, target.id, tk.id
                        self._tick(max(4.0, (P.t_complete + jit) * hf), off)
                        if y >= dist_goal:
                            self._bump(qd, "pass_td")
                            self._bump(td_, "rec_td")
                        elif rng.random() < P.fumble_pass:
                            turnover = "FUMBLE"
                            self._bump(td_, "fumbles_lost")
                    else:
                        kind, a_, b_ = "PI", qb.id, target.id
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
                kind, a_, b_ = "RU", carrier.id, tk.id
                self._tick(max(5.0, (P.t_run + jit) * hf), off)
                if y >= dist_goal:
                    self._bump(cd, "rush_td")
                elif rng.random() < P.fumble_run:
                    turnover = "FUMBLE"
                    self._bump(cd, "fumbles_lost")

            plays += 1
            tm["plays"] += 1
            self.scrim = True
            if turnover == "INT":
                pass
            else:
                yards += play_yards
                tm["yards"] += play_yards
            pos_after = pos + play_yards
            if self.rec:
                self._log(off, down, to_go, pos, play_yards, turnover, kind, a_, b_, c_)
            if pos_after <= 0 and not turnover:
                # tackled in the end zone: safety, and the scoring team gets the ball after a free kick
                self.score[1 - off] += 2
                def_pts = 2
                result = "SAFETY"
                if P.rules >= 5:
                    next_start, self.ko_next, self.free = None, True, True      # a free kick from the 20 follows
                else:
                    next_start = int(min(45, max(25, rng.gauss(35, 5))))
                break

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
                        def_pts = 6 + self._conv(1 - off)
                        next_start = self._after_score()
                        next_off = off
                    else:
                        next_start = int(min(99, max(1, dstart)))
                else:
                    if rng.random() < P.fumble_td:
                        result = "FUMBLE_TD"
                        self.score[1 - off] += 6
                        def_pts = 6 + self._conv(1 - off)
                        next_start = self._after_score()
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
                pts += self._conv(off)
                # credit the touchdown to the QB/receiver/runner already counted in play stats
                next_start = self._after_score()
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
            stopped = kind == "PI"
            if P.rules >= 2 and kind in ("RU", "PC", "SK") and self.quarter == q_before:
                if self._timeout_check(off, down, to_go, pos, t_before - self.t):
                    stopped = True

        rec = dict(team=me.name, side=off, quarter=q0, start=start, plays=plays, yards=yards,
                   secs=int(tm["top_secs"] - start_secs_total), result=result, pts=pts, def_pts=def_pts)
        res.drives.append(rec)
        self.next_start = next_start
        self.next_off = next_off
        return rec


def simulate_game(home: Lineup, away: Lineup, rng: random.Random, params: EngineParams = None,
                  neutral: bool = False, record_plays: bool = False, allow_tie: bool = False, injuries: bool = False) -> GameResult:
    """Play a whole game. Index 0 is the home team, 1 the away team. allow_tie=True is a regular-season game, which can end level
    after overtime; the default plays on until someone wins (postseason)."""
    P = params or EngineParams()
    g = _Game(home, away, rng, P, neutral, record_plays, injuries)
    res = g.res
    off = rng.randrange(2)                  # who receives the opening kickoff
    receive_first = off
    if P.rules < 5:
        start = g._kick_start()
    else:
        off, start = g._kickoff(off)
    half_done = False
    while True:
        g.period_over = False
        d = g.drive(off, start)
        off, start = g.next_off, g.next_start
        if g.ko_next and not g.period_over:                 # (rules version 5) a score: the kickoff is a play
            off, start = g._kickoff(off, g.free)
        if g.period_over:
            if g.quarter == 2 and not half_done:
                half_done = True
                g.quarter = 3
                g.t = Q_SECS
                g.to = [3, 3]
                g.period_over = False
                off = 1 - receive_first
                if P.rules >= 5:
                    off, start = g._kickoff(off)
                else:
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
    side_of.update(g.side_of)                       # (rules version 4) players who came on, and those who left
    for pid, d in res.players.items():
        d["team"] = side_of.get(pid, 0)
    return res


def _overtime(g: _Game, rng: random.Random, allow_tie: bool = False):
    """NFL overtime. Each team gets a possession even if the first scores a touchdown (a defensive touchdown on the first possession
    ends it); once both have had one, the next score wins. Regular season: one 10-minute period, a tie if still level. Postseason:
    15-minute periods until someone leads when a period ends (a seeded kick-off decides after MAX_OT periods, recorded as such)."""
    res = g.res
    g.in_ot = True
    kicks = getattr(getattr(g, "P", None), "rules", 1) >= 5          # rules version 5: the kickoff is a play, played at the top of the loop below
    off = rng.randrange(2)
    start = None if kicks else g._kick_start()            # (rules version 5: the kickoff is played at the top of the loop below)
    possessions = 0
    periods = 1 if allow_tie else MAX_OT
    secs = OT_SECS if allow_tie else OT_SECS_POST
    for period in range(1, periods + 1):
        res.ot_periods = period
        g.t = secs
        g.to = [2, 2]
        g.period_over = False
        if start is None and not kicks:
            start = g._kick_start()
        while True:
            g.ot_poss = possessions
            if start is None:                                # (rules version 5) the kickoff, or the free kick after a safety
                off, start = g._kickoff(off, g.free)
                if g.over:
                    return
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
