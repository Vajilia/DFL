"""The live runner (the Commissioner, 2026-10-12): the league's seasons revealed on the real clock, for the website to watch.

    python engine/live.py --out /var/www/dfl/live --opener-at 2026-10-13T09:00      # first run: choose when the first kickoff happens (local time)
    python engine/live.py --out /var/www/dfl/live                                     # after that: carry on from the saved meta.json

The engine stays wherever it runs and the page is the viewing glass: this program plays no football of its own. It plays each league year with the real drive
engine and the play log on (engine/site_export.play_season), and then REVEALS the year on the real clock: a game's plays appear in the feed as they "happen", the
standings are whatever the revealed finals add up to, the playoff matchups are announced shortly before they are played. Because every season is a pure function
of the seed, a restart loses nothing: the runner replays the years already gone (about two seconds each) and carries on from the clock.

Time. One league year is YEAR_HOURS real hours (168: a normal season is a real week). A league date maps to real time by its share of its calendar year (the last
WRAP_UP hours of the real week stay clear so a late-December Coronation can finish before the next year begins), so a game
kicks off at the real moment that corresponds to its league date and kickoff time. A game itself takes REAL_PER_GAME real seconds per game second plus a halftime
(the page's replay uses the same two numbers), about 36 minutes.

Feed (all under --out, written atomically; nothing in it is ahead of the clock):
    meta.json      {seed, epoch_ms, year_hours}        fixed for the life of the league
    season.json    the current year's schedule: no scores, no matchups for playoff games not yet announced
    results.json   revealed finals, games in progress, announced playoff games, and, once they are decided, seeds, division ranks, exits, champion; plus the clock
    season_<year>.json, results_<year>.json    each year's schedule and results, kept after the year ends
    g/<year>_<id>.json    a game's players, completed drives and the plays so far (all of them once final)
    history.json   the champions of the years already over
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calendar_dfl as K
import founding as F
import identity as ID
import rules as R
import parity
import site_export as SE
from schedule import rotation

YEAR_HOURS = 168.0
WRAP_UP = 1.5                       # the last real hours of a year are kept clear (the 31 December Coronation can take until midnight): league dates map onto the rest
SPAN_HOURS = YEAR_HOURS - WRAP_UP
REAL_PER_GAME = 0.6                 # real seconds per game second (the page uses the same numbers)
HALFTIME_PAUSE = 20.0               # real seconds
TAIL = 15.0                         # real seconds after the last play before a game counts as final
SLOT_GAP_MS = 38 * 60 * 1000        # kickoff windows are at least this far apart in real time: a game (about 36 minutes) is over before the next window opens
ANNOUNCE = 20 * 60 * 1000           # a playoff game's matchup is announced this long (real ms) before its kickoff
PO_KICK = {"playoff_wc": ["13:00", "13:00", "16:30", "16:30", "20:00", "20:00"], "playoff_div": ["13:00", "13:00", "16:30", "16:30"],
           "playoff_conf": ["15:00", "18:30"], "playoff_final": ["17:30"]}
PO_DATE = {"playoff_wc": "wild_card", "playoff_div": "divisional", "playoff_conf": "conference", "playoff_final": "coronation"}
HOUR_MS = 3600 * 1000

# "Blocks" pacing (the Commissioner, 2026-10-13): the league runs almost continually instead of spreading a year over the calendar. A league day's kickoff windows are the blocks
# b1 Saturday night, b2 Sunday morning, b3 Sunday afternoon, b4 Sunday evening, b5 Monday evening, one after another in real time: a block starts when the longest game of the
# one before it has ended plus a short gap. Playoff rounds run the same way. A league year is then as long as its games take (about 56 real hours at 30-minute games).
BLOCK_REAL_PER_GAME = 0.48          # real seconds per game second: a game's 60 minutes play out in about 30 real minutes (halftime and the tail on top)
BLOCK_GAP_MS = 2 * 60 * 1000        # between two blocks of the same week (or the same playoff round)
WEEK_GAP_MS = 5 * 60 * 1000         # between the last block of a week (or round) and the first block of the next
OFFSEASON_MS = 60 * 60 * 1000       # from the end of the Coronation to the next league year's first kickoff
WRAP_UP_MS = 20 * 60 * 1000         # the page moves on to the next league year this long after the Coronation ends (the champion stays on show until then)
PACINGS = ("blocks", "legacy")


def year_start_ms(epoch_ms: int, n: int) -> float:
    return epoch_ms + (n - 1) * YEAR_HOURS * HOUR_MS


def real_ms(epoch_ms: int, n: int, when: dt.datetime) -> int:
    """The real moment (ms) that league year n's moment `when` corresponds to."""
    y = K.calendar_year(n)
    jan1 = dt.datetime(y, 1, 1)
    days = 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365
    return int(year_start_ms(epoch_ms, n) + (when - jan1).total_seconds() / (days * 86400) * SPAN_HOURS * HOUR_MS)


def sim_date(epoch_ms: int, n: int, now_ms: float) -> dt.datetime:
    y = K.calendar_year(n)
    days = 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365
    frac = min(1.0, (now_ms - year_start_ms(epoch_ms, n)) / (SPAN_HOURS * HOUR_MS))
    return dt.datetime(y, 1, 1) + dt.timedelta(seconds=frac * days * 86400)


def year_at(epoch_ms: int, now_ms: float) -> int:
    return 0 if now_ms < epoch_ms else int((now_ms - epoch_ms) // (YEAR_HOURS * HOUR_MS)) + 1


def play_offset_ms(pl, rpg=None, half=None) -> float:
    """Real ms after kickoff at which a play (as logged: ... quarter, seconds left, overtime flag, drive, game seconds) has happened.
    rpg and half are the league's real seconds per game second and its halftime pause (the module's numbers when not given)."""
    rpg = REAL_PER_GAME if rpg is None else rpg
    half = HALFTIME_PAUSE if half is None else half
    return (pl[14] * rpg + (half if (pl[10] >= 3 or pl[12]) else 0.0)) * 1000.0


def opener_epoch(opener_at: dt.datetime) -> int:
    """The epoch (real ms) that puts league year 1's first kickoff at `opener_at` (local time of the machine)."""
    o = K.opener(K.calendar_year(1))
    f = (dt.datetime(o.year, o.month, o.day, 17, 30) - dt.datetime(K.calendar_year(1), 1, 1)).total_seconds() / (366 * 86400)
    return int(opener_at.timestamp() * 1000 - f * SPAN_HOURS * HOUR_MS)


class Season:
    """One league year, played in full and ready to be revealed."""

    def __init__(self, world, n: int, start_ms=None, begin_ms=None, prev_when=None):
        self.n, self.epoch = n, world.epoch_ms
        self.pacing, self.rpg, self.half = world.pacing, world.rpg, world.half
        self.start_ms, self.begin_ms, self.prev_when = start_ms, begin_ms, prev_when    # blocks pacing: first kickoff, when the page moves to this year, the last Coronation's league date
        lg = world.lg
        res, names = SE.play_season(lg, world.rng, n, world.rules)
        self.res = res
        cal = K.calendar_year(n)
        flip, shift = rotation(n)
        D = R.DIVISIONS_PER_CONFERENCE
        slot = {t.id: (t.conf ^ flip, (t.div + shift) % D, res.start[t.id][1]) for t in lg.teams if res.start[t.id][0] == "active"}
        times = world.times
        short = {pid: SE._short(nm) for pid, nm in names.items()}
        self.games = []                                   # every game, in id order within its group
        for g in sorted(res.games, key=lambda g: (g.week, g.home)):
            num, day, kick = times[(g.week, slot[g.home], slot[g.away])]
            when = dt.datetime.combine(K.week_saturday(cal, g.week) + dt.timedelta(days=day), dt.time(*map(int, kick.split(":"))))
            self.games.append(self._game(f"r{g.week}_{g.home}", "reg", g, when, short))
        for g in sorted(res.ambassador_games, key=lambda g: (g.week, g.home)):
            when = dt.datetime.combine(K.week_saturday(cal, g.week) + dt.timedelta(days=1), dt.time(12, 0))
            self.games.append(self._game(f"a{g.week}_{g.home}", "amb", g, when, short))
        po, seen = K.playoffs(cal), {}
        for i, g in enumerate(res.playoff_games):
            k = seen[g.kind] = seen.get(g.kind, -1) + 1
            when = dt.datetime.combine(po[PO_DATE[g.kind]], dt.time(*map(int, PO_KICK[g.kind][k].split(":"))))
            self.games.append(self._game(f"p{i}", "po", g, when, short))
        if self.pacing == "blocks":
            self._place_blocks(start_ms)
        else:
            self._space_windows()
        self.by_id = {g["id"]: g for g in self.games}
        self.reg_end = max(g["end"] for g in self.games if g["group"] == "reg")
        self.final_end = max(g["end"] for g in self.games if g["group"] == "po")
        self.opener_ms = min(g["start"] for g in self.games if g["group"] == "reg")

    def _game(self, gid, group, g, when, short):
        b = SE._box(g.result, short)
        plays = b["p"]
        offs = [play_offset_ms(p, self.rpg, self.half) for p in plays]
        last_of = {}
        for i, p in enumerate(plays):
            last_of[p[13]] = i                            # index of the last play of each drive
        start = 0.0 if self.pacing == "blocks" else real_ms(self.epoch, self.n, when)      # blocks pacing places every game afterwards, block by block
        return dict(id=gid, group=group, week=g.week, home=g.home, away=g.away, kind=g.kind, hp=g.home_pts, ap=g.away_pts, ot=g.result.ot_periods, box=b, offs=offs,
                    last_of=last_of, start=start, end=start + (offs[-1] if offs else 0) + TAIL * 1000, when=when.isoformat(timespec="minutes"), written=-1)

    def _space_windows(self):
        """Kickoff windows (all the games with the same league date and kickoff time) keep the league's order, but at least SLOT_GAP_MS apart in real time. A league day is only
        about 27 real minutes, so left on the straight-line clock the Sunday windows (10:00, 13:00, 17:30) would start 3 to 5 minutes apart and overlap into one block. The
        Ambassador games, which have a time of their own, play in the latest window at or before it. The window starts are a pure function of the schedule (a restart changes nothing)."""
        slots = sorted({g["when"] for g in self.games if g["group"] != "amb"})
        lin = {}
        for g in self.games:
            lin.setdefault(g["when"], g["start"])
        start, prev = {}, None
        for w in slots:
            start[w] = lin[w] if prev is None else max(lin[w], prev + SLOT_GAP_MS)
            prev = start[w]
        self.window_start = start
        for g in self.games:
            w = g["when"] if g["group"] != "amb" else (max([x for x in slots if x <= g["when"]], default=slots[0]))
            dur = g["end"] - g["start"]
            g["start"] = start[w]
            g["end"] = g["start"] + dur

    def _place_blocks(self, start_ms):
        """Blocks pacing. Every kickoff window (the games with one league date and kickoff time) is a block. The blocks keep the league's order and follow one another in real
        time: a block starts when the longest game of the block before it has ended, plus BLOCK_GAP_MS (WEEK_GAP_MS when it opens a new week or playoff round). The Ambassador
        games, which have a time of their own, play in the latest block at or before it. A year's blocks depend only on the schedule and the games' lengths, so a restart changes nothing."""
        slots = sorted({g["when"] for g in self.games if g["group"] != "amb"})
        blocks = {}
        for g in self.games:
            w = g["when"] if g["group"] != "amb" else max([x for x in slots if x <= g["when"]], default=slots[0])
            blocks.setdefault(w, []).append(g)
        t, prev, self.window_start = float(start_ms), None, {}
        for w in slots:
            gs = blocks[w]
            plain = [g for g in gs if g["group"] != "amb"]
            label = ("po", plain[0]["kind"]) if plain[0]["group"] == "po" else ("reg", min(g["week"] for g in plain))
            if prev is not None:
                t += WEEK_GAP_MS if label != prev else BLOCK_GAP_MS
            dur = max(g["end"] - g["start"] for g in gs)             # every game was built starting at 0, so its end is its length
            for g in gs:
                length = g["end"] - g["start"]
                g["start"], g["end"] = t, t + length
            self.window_start[w] = t
            t += dur
            prev = label

    # -- what the clock allows -------------------------------------------------
    def revealed(self, g, now_ms):
        k = 0
        rel = now_ms - g["start"]
        offs = g["offs"]
        while k < len(offs) and offs[k] <= rel:
            k += 1
        return k

    def game_file(self, g, now_ms, k):
        b = g["box"]
        final = now_ms >= g["end"]
        out = dict(id=g["id"], year=self.n, pl=b["pl"], dr=[d for i, d in enumerate(b["dr"]) if i in g["last_of"] and g["last_of"][i] < k] if not final else b["dr"],
                   p=b["p"][:k] if not final else b["p"], live=not final, start=g["start"])
        if final:
            out.update(tm=b["tm"], n=b["n"], tb=b["tb"], hp=g["hp"], ap=g["ap"])
        return out

    def schedule_file(self, now_ms):
        regs = [[g["id"], g["week"], g["home"], g["away"], g["start"], g["kind"], g["when"]] for g in self.games if g["group"] == "reg"]
        ambs = [[g["id"], g["week"], g["home"], g["away"], g["start"], "ambassador", g["when"]] for g in self.games if g["group"] == "amb"]
        pos = [[g["id"], g["kind"], g["start"], g["when"]] for g in self.games if g["group"] == "po"]
        cal = K.calendar_year(self.n)
        yh = YEAR_HOURS if self.pacing != "blocks" else round((self.final_end - self.opener_ms) / HOUR_MS, 1)      # blocks pacing: the length of this year's games, first kickoff to the Coronation's end
        return dict(year=self.n, season=cal, calendar=SE.calendar_for(cal), games=regs, amb=ambs, po=pos, epoch=self.epoch, year_hours=yh, pacing=self.pacing,
                    real_per_game=self.rpg, halftime=self.half,
                    exiled=sorted(t for t, v in self.res.start.items() if v[0] == "exiled"), tiers={str(t): v[1] for t, v in self.res.start.items() if v[1] is not None})

    def score_now(self, g, now_ms):
        """[home, away, quarter, seconds left, overtime] for a game in progress: the points of the drives the clock has finished, and the clock of the last play."""
        b, k = g["box"], self.revealed(g, now_ms)
        sc = [0, 0]
        for i, (side, q, st, pl, yd, sec, res_, pts, dpts) in enumerate(b["dr"]):
            if i in g["last_of"] and g["last_of"][i] < k:
                sc[side] += pts; sc[1 - side] += dpts
        last = b["p"][k - 1] if k else None
        return [sc[0], sc[1], last[10] if last else 1, last[11] if last else 900, last[12] if last else 0]

    def sim_now(self, now_ms):
        """The league date shown on the page. In season it is the date and time of the latest kickoff window to have opened (the windows are spaced out in real time, so the straight-line
        clock would run ahead of them during a week); outside the season it is the straight-line clock, never behind the last game played."""
        opened = [w for w, st in self.window_start.items() if st <= now_ms]
        if self.pacing == "blocks":
            if opened:
                return dt.datetime.fromisoformat(max(opened))        # the league date of the latest block to have opened (the Coronation's, once the year is over)
            first = dt.datetime.fromisoformat(min(self.window_start))
            if self.prev_when is None or self.begin_ms is None or self.start_ms <= self.begin_ms:
                return first
            f = min(1.0, max(0.0, (now_ms - self.begin_ms) / (self.start_ms - self.begin_ms)))
            return self.prev_when + (first - self.prev_when) * f      # the offseason: the league date runs from the last Coronation to this year's opener
        lin = sim_date(self.epoch, self.n, now_ms)
        if not opened:
            return lin
        last = dt.datetime.fromisoformat(max(opened))
        return last if now_ms <= self.final_end else max(lin, last)

    def results_file(self, now_ms, history):
        res = self.res
        final, live, po_teams = {}, [], {}
        for g in self.games:
            if now_ms >= g["end"]:
                final[g["id"]] = [g["hp"], g["ap"], g["ot"]]
            elif now_ms >= g["start"]:
                live.append(g["id"])
            if g["group"] == "po" and now_ms >= g["start"] - ANNOUNCE:
                po_teams[g["id"]] = [g["home"], g["away"]]
        out = dict(t=int(now_ms), year=self.n, sim=self.sim_now(now_ms).isoformat(timespec="minutes"), final=final, live=live, po=po_teams, history=history,
                   now={i: self.score_now(self.by_id[i], now_ms) for i in live})
        if now_ms >= self.reg_end:                         # the regular season is over: the seeds and final division order are known
            out["seeds"] = {str(k): v for k, v in res.seeds.items()}
            out["division_ranks"] = {str(k): v for k, v in res.division_ranks.items()}
        if now_ms >= self.final_end:
            out["champion"] = res.champion
            out["exits"] = {str(k): v for k, v in res.exits.items()}
        return out


class World:
    def __init__(self, seed: int, epoch_ms: int, pacing: str = "legacy", rpg=None, half=None, profile: str = "tight", rules: int = 1):
        """pacing "legacy": the epoch is Founding Day and a league year is YEAR_HOURS real hours (the first live league). "blocks": the epoch is the first kickoff and
        the league runs block after block (see BLOCK_REAL_PER_GAME); rpg and half are the league's real seconds per game second and halftime pause."""
        assert pacing in PACINGS, pacing
        self.seed, self.epoch_ms, self.pacing = seed, epoch_ms, pacing
        self.rpg = (BLOCK_REAL_PER_GAME if pacing == "blocks" else REAL_PER_GAME) if rpg is None else float(rpg)
        self.half = HALFTIME_PAUSE if half is None else float(half)
        self.rules = int(rules)                              # rules version 1: as first played; 2: penalties and timeouts; 3: clock management, spikes and kneels (new leagues only)
        self.profile = parity.apply(profile)                 # the parity profile's dials are set before the league is opened
        self.lg, self.rng = F.open_league(seed)
        self.times = ID.slot_times(self.lg.teams)         # taken now, while the tiers are the founding seeds
        self.year = 0
        self.season = None
        self.history = []                                 # [{year, champion}] for the years already played out

    def advance_to(self, n: int):
        """Legacy pacing: play every year up to n (a restart replays the years gone by: the seed decides them all)."""
        while self.year < n:
            if self.season is not None:
                self.history.append(dict(year=K.calendar_year(self.year), champion=self.season.res.champion))
            self.year += 1
            self.season = Season(self, self.year)
        return self.season

    def season_at(self, now_ms: float):
        """Blocks pacing: the league year the page shows at now_ms (None before the first kickoff). The year after one begins WRAP_UP_MS after its Coronation ends and has its first
        kickoff OFFSEASON_MS after it; every year is played in full as soon as the clock needs it, and a restart replays the years gone by (the seed decides them all)."""
        while True:
            begin = self.epoch_ms if self.season is None else self.season.final_end + WRAP_UP_MS
            if now_ms < begin:
                return self.season
            if self.season is None:
                start, prev_when = self.epoch_ms, None
            else:
                self.history.append(dict(year=K.calendar_year(self.year), champion=self.season.res.champion))
                start = self.season.final_end + OFFSEASON_MS
                prev_when = dt.datetime.fromisoformat(max(self.season.window_start))
            self.year += 1
            self.season = Season(self, self.year, start_ms=start, begin_ms=begin, prev_when=prev_when)


def write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f, separators=(",", ":"))
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def engine_commit() -> str:
    """The short commit of the engine code that is running (for the league's meta.json), or "unknown"."""
    try:
        import subprocess
        r = subprocess.run(["git", "-c", "safe.directory=*", "-C", os.path.dirname(os.path.abspath(__file__)), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


class Runner:
    def __init__(self, out: str, seed: int, epoch_ms: int, meta=None):
        """meta: the league's meta.json as it was fixed when the league was made (a restart passes it back unchanged); without it, the first live league's legacy meta."""
        m = meta or dict(seed=seed, epoch_ms=epoch_ms, year_hours=YEAR_HOURS, real_per_game=REAL_PER_GAME, halftime=HALFTIME_PAUSE)
        self.out, self.world = out, World(seed, epoch_ms, m.get("pacing", "legacy"), m.get("real_per_game"), m.get("halftime"), m.get("parity", "tight"), m.get("rules", 1))
        self.meta = m
        self.pauses = [list(p) for p in m.get("pauses", [])]    # [[real ms the league was paused, real ms it was resumed or None while it is paused]]: part of the league's history
        write_json(os.path.join(out, "meta.json"), m)
        self.sched_year = None
        self.last_season = None

    # -- pausing: the league's own clock stops and carries on from the same moment (the person's league, paused after a late night and resumed after breakfast) -------
    def paused(self) -> bool:
        return bool(self.pauses) and self.pauses[-1][1] is None

    def _control(self, real_ms: float) -> None:
        """control.json in the feed folder says whether the league should be paused: {"paused": true}. Whatever writes it (a script, later a button) never touches the engine."""
        want = False
        try:
            want = bool(json.load(open(os.path.join(self.out, "control.json"))).get("paused"))
        except (OSError, ValueError, AttributeError):
            pass
        if want and not self.paused():
            self.pauses.append([int(real_ms), None])
        elif not want and self.paused():
            self.pauses[-1][1] = int(real_ms)
        else:
            return
        self.meta["pauses"] = self.pauses
        write_json(os.path.join(self.out, "meta.json"), self.meta)       # saved at once, so a restart in the middle of a pause (or after one) keeps the same clock

    def effective(self, real_ms: float):
        """(the league's own clock, the real time lost to pauses so far). Every time in the feed is on the league's clock; the page adds the lost time to show real times."""
        lost = sum((real_ms if b is None else b) - a for a, b in self.pauses)
        return real_ms - lost, lost

    def write_games(self, s, now_ms: float) -> None:
        """Each started game's file, rewritten only when it has grown (the final write holds every play)."""
        for g in s.games:
            if now_ms < g["start"]:
                continue
            k = s.revealed(g, now_ms)
            final = now_ms >= g["end"]
            stamp = len(g["offs"]) + 1 if final else k
            if g["written"] != stamp:
                write_json(os.path.join(self.out, "g", f"{s.n}_{g['id']}.json"), s.game_file(g, now_ms, k))
                g["written"] = stamp

    def finalize(self, s, history) -> None:
        """A year that has just ended: every game file and the year's results are written as they stood when its Coronation ended, so a finished season is complete on disk even if no tick fell in its last moments."""
        end = s.final_end
        self.write_games(s, end)
        write_json(os.path.join(self.out, f"results_{s.n}.json"), s.results_file(end, history))

    def tick(self, real_now: float) -> dict:
        """Write the feed as it stands at the real moment `real_now`. Returns the results written (None before the league begins)."""
        self._control(real_now)
        now_ms, shift = self.effective(real_now)
        w = self.world
        if w.pacing == "blocks":
            s = w.season_at(now_ms)
            n = w.year if s is not None else 0
        else:
            n = year_at(w.epoch_ms, now_ms)
            s = w.advance_to(n) if n else None
        if n == 0:
            write_json(os.path.join(self.out, "results.json"), dict(t=int(now_ms), year=0, final={}, live=[], po={}, history=[], epoch=w.epoch_ms, shift=int(shift), paused=self.paused()))
            return None
        if self.sched_year != n:
            sf = s.schedule_file(now_ms)
            write_json(os.path.join(self.out, "season.json"), sf)
            write_json(os.path.join(self.out, f"season_{n}.json"), sf)      # kept for good: a finished season's schedule, so its games can be listed later
            write_json(os.path.join(self.out, "history.json"), w.history)
            self.sched_year = n
        prev = self.last_season
        if prev is not None and prev is not s:              # the year has turned over: close the books on the one that ended, whatever the ticks did near its end
            self.finalize(prev, w.history[:prev.n - 1])
        self.last_season = s
        self.write_games(s, now_ms)
        out = s.results_file(now_ms, w.history)
        out["shift"], out["paused"] = int(shift), self.paused()          # the real time lost to pauses (the page adds it to the league's clock to show real times), and whether the league is paused now
        write_json(os.path.join(self.out, "results.json"), out)
        write_json(os.path.join(self.out, f"results_{n}.json"), out)    # the same, kept per year (the last write of a year is its final results)
        return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--opener-at", help="local time of the first kickoff, e.g. 2026-10-13T09:00 (only when the league is first started)")
    ap.add_argument("--every", type=float, default=3.0, help="seconds between writes")
    ap.add_argument("--init", action="store_true", help="only write meta.json (fixing the opener) and stop; the service then carries on from it")
    ap.add_argument("--parity", choices=parity.NAMES, default="tight", help="how much the league regulates salaries and protects weak clubs (a NEW league only): tight (the rules as written) or none")
    ap.add_argument("--rules", type=int, choices=(1, 2, 3), default=3, help="game rules of a NEW league: 3 = clock management on top of 2 (default); 2 = penalties and timeouts; 1 = the first version, without them")
    ap.add_argument("--pacing", choices=PACINGS, default="blocks", help="how a NEW league runs: blocks (continuous, about 30-minute games) or legacy (a league year spread over a real week)")
    a = ap.parse_args(argv)
    meta = os.path.join(a.out, "meta.json")
    if os.path.exists(meta) and not a.opener_at:
        m = json.load(open(meta))
        seed, epoch = m["seed"], m["epoch_ms"]
        now_code = engine_commit()
        if m.get("engine_commit") and now_code != "unknown" and m["engine_commit"] != now_code:
            print(f"WARNING: this league was made with engine code {m['engine_commit']} and the code now is {now_code}. Years already revealed are replayed from the seed, "
                  f"so any change to how games are played can change what they were. Reset the league, or return to {m['engine_commit']}.", flush=True)
    elif a.opener_at:
        seed = a.seed
        if a.pacing == "blocks":
            epoch = int(dt.datetime.fromisoformat(a.opener_at).timestamp() * 1000)       # the first kickoff itself
            m = dict(seed=seed, epoch_ms=epoch, pacing="blocks", real_per_game=BLOCK_REAL_PER_GAME, halftime=HALFTIME_PAUSE, engine_commit=engine_commit(), parity=a.parity, rules=a.rules)
        else:
            epoch = opener_epoch(dt.datetime.fromisoformat(a.opener_at))
            m = dict(seed=seed, epoch_ms=epoch, year_hours=YEAR_HOURS, real_per_game=REAL_PER_GAME, halftime=HALFTIME_PAUSE)
    else:
        sys.exit("First start: give --opener-at (local time of the first kickoff).")
    if a.init:
        write_json(meta, m)
        print(f"league fixed: seed {seed}; first kickoff {a.opener_at}; pacing {m.get('pacing', 'legacy')}; epoch {epoch}", flush=True)
        return
    r = Runner(a.out, seed, epoch, m)
    print(f"league seed {seed}; Founding Day (1 Jan 2000) is {dt.datetime.fromtimestamp(epoch / 1000):%Y-%m-%d %H:%M}; the feed is in {a.out}", flush=True)
    while True:
        r.tick(time.time() * 1000)
        time.sleep(a.every)


if __name__ == "__main__":
    main()
