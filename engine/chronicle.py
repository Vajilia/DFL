"""The Chronicle (2026-10-17): the league's story, told once after each week is played.

A separate, read-only consumer of the live feed (engine/live.py). It never touches the runner or the simulation, so no result can change.

    feed  --> facts (what happened, from the box scores and the standings)
          --> selector (newsworthiness: upsets, thrillers, streaks, star injuries, big nights; 1-10 stories under a word cap)
          --> fact sheet per story (the ONLY things a writer may say)
          --> writer (templates, free; or an LLM when a key and a price are configured)
          --> checker (every name and number in the text must be on the fact sheet, else retry once, else templates)
          --> chronicle/<year>_<unit>.json, written ONCE and never regenerated

The league replays its past seasons from the seed when the runner restarts, so the words cannot be re-derived: a written unit is kept as it was.
A unit is one regular-season week, one playoff round, or a season's review. Everything is keyed by year and unit.

    python engine/chronicle.py --feed /var/www/dfl/live --out /var/www/dfl/live/chronicle          scan once, write any finished unit not yet written
    python engine/chronicle.py --feed ... --out ... --every 60                                      keep scanning
    python engine/chronicle.py --feed ... --estimate                                                 size (and cost, with prices set) of one week's LLM prompts; writes nothing

LLM writing is OFF unless ANTHROPIC_API_KEY, DFL_CHRONICLE_MODEL, DFL_PRICE_IN and DFL_PRICE_OUT (dollars per million tokens) are all set in the environment.
A monthly budget (DFL_CHRONICLE_BUDGET, default 18 dollars) is kept in <out>/spend.json; at the limit, or on any failure, the template writer is used.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import random
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import injuries as INJ

VERSION = 1
WORD_CAP = 950                      # a week's entries together stay under about this many words
MAX_STORIES, MIN_SCORE = 10, 30
PARA_WORDS = 55                     # an estimate of a template paragraph, for the cap
OUTLET = "The Diamond Chronicle"
PO_ORDER = ["playoff_wc", "playoff_div", "playoff_conf", "playoff_final"]
PO_LABEL = {"playoff_wc": "Wild Card round", "playoff_div": "Divisional round", "playoff_conf": "Conference championships", "playoff_final": "The Coronation"}


# ------------------------------------------------------------------------------------------------ feed access

def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_teams():
    out = {}
    with open(os.path.join(HERE, "..", "data", "teams.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[int(r["club_id"])] = dict(id=int(r["club_id"]), abbr=r["abbr"], city=r["city"], nick=r["nickname"], name=f"{r['city']} {r['nickname']}")
    return out


def short_name(name):
    parts = name.split()
    return name if len(parts) < 2 else f"{parts[0][0]}. {' '.join(parts[1:])}"


class Feed:
    """The files the runner wrote. Nothing here is ever written."""

    def __init__(self, root):
        self.root = root
        self.teams = load_teams()
        self.meta = jload(os.path.join(root, "meta.json")) if os.path.exists(os.path.join(root, "meta.json")) else {}
        self._season, self._game = {}, {}

    def p(self, *a):
        return os.path.join(self.root, *a)

    def years(self):
        ys = []
        for fn in os.listdir(self.root):
            m = re.fullmatch(r"results_(\d+)\.json", fn)
            if m:
                ys.append(int(m.group(1)))
        return sorted(ys)

    def season(self, y):
        if y not in self._season:
            self._season[y] = jload(self.p(f"season_{y}.json"))
        return self._season[y]

    def results(self, y):
        return jload(self.p(f"results_{y}.json"))

    def game(self, y, gid):
        k = (y, gid)
        if k not in self._game:
            f = self.p("g", f"{y}_{gid}.json")
            g = jload(f) if os.path.exists(f) else None
            self._game[k] = g if g and not g.get("live") else None
        return self._game[k]

    def roster_names(self, y):
        """{(club id, short name, position): full name}, where the short name and position pick one player."""
        out = {}
        for tid, t in self.season(y)["teams"].items():
            for r in t["r"]:
                out.setdefault((int(tid), short_name(r[1]), r[2]), []).append((r[1], r[4]))
        return {k: v[0] for k, v in out.items() if len(v) == 1}

    def roster_rank(self, y):
        """{(club id, full name): rank by rating within the club (1 = best)}, and the rating."""
        out = {}
        for tid, t in self.season(y)["teams"].items():
            for i, r in enumerate(sorted(t["r"], key=lambda r: -r[4])):
                out[(int(tid), r[1])] = (i + 1, r[4])
        return out


# ------------------------------------------------------------------------------------------------ facts about a game

def player_lines(g, names, rank, clubs):
    """Each player's night from the play log alone: passing, rushing, receiving, sacks, interceptions, and who was hurt."""
    pl = g["pl"]                                    # [name, position, side (0 home, 1 away), id]; clubs is (home club id, away club id)
    st = {}

    def bump(i, k, n=1):
        if i is None or i < 0 or i >= len(pl):
            return
        d = st.setdefault(i, {})
        d[k] = d.get(k, 0) + n
    hurt = []
    for r in g["p"]:
        kind, pos, yds, a, b, c = r[6], r[3], r[4], r[7], r[8], r[9]
        if kind == "PC":
            bump(a, "cmp"); bump(a, "att"); bump(a, "pyds", yds); bump(b, "rec"); bump(b, "ryds", yds)
            if pos + yds >= 100:
                bump(a, "ptd"); bump(b, "rtd")
        elif kind == "PI":
            bump(a, "att")
        elif kind == "IN":
            bump(a, "att"); bump(a, "int"); bump(c, "ints")
        elif kind == "SK":
            bump(b, "sacks")
        elif kind == "RU":
            bump(a, "car"); bump(a, "uyds", yds)
            if pos + yds >= 100:
                bump(a, "utd")
        elif kind == "IJ" and 0 <= a < len(pl):
            hurt.append((a, c))
    out = {}
    for i, d in st.items():
        nm, ps, side, _pid = pl[i]
        tid = clubs[side]
        full = names.get((tid, nm, ps), (nm, 0))
        d["name"], d["pos"], d["team"] = full[0], ps, tid
        d["ovr"] = full[1]
        out[i] = d
    inj = []
    for i, c in hurt:
        nm, ps, side, _pid = pl[i]
        tid = clubs[side]
        full = names.get((tid, nm, ps), (nm, 0))
        rk = rank.get((tid, full[0]), (99, 0))
        inj.append(dict(name=full[0], pos=ps, team=tid, kind=INJ.KIND_NAMES[c] if 0 <= c < len(INJ.KIND_NAMES) else "injury", rank=rk[0], ovr=rk[1]))
    return out, inj


def leaders(lines, tid):
    """The standout lines for a club: its best passer, rusher, receiver, and the sack and interception leaders. Only lines worth a sentence."""
    mine = [d for d in lines.values() if d["team"] == tid]
    out = []
    p = max((d for d in mine if d.get("att", 0) >= 10), key=lambda d: d.get("pyds", 0), default=None)
    if p:
        out.append(dict(kind="pass", name=p["name"], cmp=p.get("cmp", 0), att=p["att"], yds=p.get("pyds", 0), td=p.get("ptd", 0), int=p.get("int", 0)))
    r = max((d for d in mine if d.get("car", 0) >= 5), key=lambda d: d.get("uyds", 0), default=None)
    if r:
        out.append(dict(kind="rush", name=r["name"], car=r["car"], yds=r.get("uyds", 0), td=r.get("utd", 0)))
    c = max((d for d in mine if d.get("rec", 0) >= 2), key=lambda d: d.get("ryds", 0), default=None)
    if c:
        out.append(dict(kind="rec", name=c["name"], rec=c["rec"], yds=c.get("ryds", 0), td=c.get("rtd", 0)))
    s = max((d for d in mine if d.get("sacks", 0) >= 2), key=lambda d: d["sacks"], default=None)
    if s:
        out.append(dict(kind="sack", name=s["name"], n=s["sacks"]))
    i = max((d for d in mine if d.get("ints", 0) >= 2), key=lambda d: d["ints"], default=None)
    if i:
        out.append(dict(kind="ints", name=i["name"], n=i["ints"]))
    return out


# ------------------------------------------------------------------------------------------------ standings

class Table:
    """Records and streaks for the regular season, built from the finals of the weeks before (and including) a week."""

    def __init__(self):
        self.w = {}
        self.l = {}
        self.t = {}
        self.pf = {}
        self.pa = {}
        self.run = {}                      # club -> (+n win streak, -n losing streak, 0 after a tie)

    def add(self, home, away, hp, ap):
        for tid, f, a in ((home, hp, ap), (away, ap, hp)):
            self.pf[tid] = self.pf.get(tid, 0) + f
            self.pa[tid] = self.pa.get(tid, 0) + a
            r = self.run.get(tid, 0)
            if f > a:
                self.w[tid] = self.w.get(tid, 0) + 1
                self.run[tid] = r + 1 if r > 0 else 1
            elif f < a:
                self.l[tid] = self.l.get(tid, 0) + 1
                self.run[tid] = r - 1 if r < 0 else -1
            else:
                self.t[tid] = self.t.get(tid, 0) + 1
                self.run[tid] = 0

    def rec(self, tid):
        return (self.w.get(tid, 0), self.l.get(tid, 0), self.t.get(tid, 0))

    def pct(self, tid):
        w, l, t = self.rec(tid)
        n = w + l + t
        return None if n == 0 else (w + t / 2) / n

    def games(self, tid):
        return sum(self.rec(tid))


def rec_str(r):
    return f"{r[0]}-{r[1]}" + (f"-{r[2]}" if r[2] else "")


def weeks_of(season):
    """{week: [game rows]} for the regular season."""
    out = {}
    for row in season["games"]:
        out.setdefault(row[1], []).append(row)
    return out


# ------------------------------------------------------------------------------------------------ the unit: what happened, scored

def build_unit(feed, y, unit):
    """Everything a writer may know about one unit, or None when the unit is not finished. unit is 'w<N>', a playoff kind, or 'review'."""
    res = feed.results(y)
    fin = res["final"]
    season = feed.season(y)
    teams = feed.teams
    names, rank = feed.roster_names(y), feed.roster_rank(y)
    wk = weeks_of(season)
    po = {r[0]: r for r in season["po"]}
    if unit.startswith("w"):
        w = int(unit[1:])
        rows = wk.get(w)
        if not rows or any(r[0] not in fin for r in rows):
            return None
        amb = [r for r in season["amb"] if r[1] == w]
        if any(r[0] not in fin for r in amb):
            return None
        label = f"Week {w}"
        before = Table()
        for ww in sorted(wk):
            if ww >= w:
                break
            for r in sorted(wk[ww]):
                before.add(r[2], r[3], fin[r[0]][0], fin[r[0]][1])
        after = Table()
        for ww in sorted(wk):
            if ww > w:
                break
            for r in sorted(wk[ww]):
                after.add(r[2], r[3], fin[r[0]][0], fin[r[0]][1])
        games = [(r[0], r[2], r[3], r[5]) for r in sorted(rows)]
        exile_games = [(r[0], r[2], r[3], "ambassador") for r in sorted(amb)]
    elif unit in PO_ORDER:
        ids = [r[0] for r in season["po"] if r[1] == unit]
        if not ids or any(i not in fin for i in ids) or any(i not in res["po"] for i in ids):
            return None
        label = PO_LABEL[unit]
        after = Table()
        for ww in sorted(wk):
            for r in sorted(wk[ww]):
                after.add(r[2], r[3], fin[r[0]][0], fin[r[0]][1])
        before = after
        games = [(i, res["po"][i][0], res["po"][i][1], unit) for i in ids]
        exile_games = []
    else:
        return None

    stories, quiet = [], []
    for gid, h, a, kind in games:
        hp, ap, ot = fin[gid]
        g = feed.game(y, gid)
        if g is None:
            return None                                    # the game's file is not final yet: wait
        lines, inj = player_lines(g, names, rank, (h, a))
        st = dict(id=gid, kind=kind, home=h, away=a, hp=hp, ap=ap, ot=ot, lines=lines, inj=inj, tm=g.get("tm"))
        stories.append(st)
    facts = dict(v=VERSION, year=y, unit=unit, label=label, games=[], exile=[])
    po_unit = unit in PO_ORDER
    for st in stories:
        h, a, hp, ap = st["home"], st["away"], st["hp"], st["ap"]
        win, lose = (h, a) if hp > ap else (a, h) if ap > hp else (None, None)
        gs = dict(id=st["id"], kind=st["kind"], home=h, away=a, hp=hp, ap=ap, ot=st["ot"], margin=abs(hp - ap),
                  winner=win, loser=lose, angles=[], leaders={str(h): leaders(st["lines"], h), str(a): leaders(st["lines"], a)}, injuries=[])
        if not po_unit:
            gs["rec_before"] = {str(t): list(before.rec(t)) for t in (h, a)}
            gs["rec_after"] = {str(t): list(after.rec(t)) for t in (h, a)}
            gs["run_after"] = {str(t): after.run.get(t, 0) for t in (h, a)}
            gs["run_before"] = {str(t): before.run.get(t, 0) for t in (h, a)}
        else:
            gs["rec_after"] = {str(t): list(after.rec(t)) for t in (h, a)}
        gs["injuries"] = [i for i in st["inj"] if i["rank"] <= 3 or i["ovr"] >= 80]
        gs["angles"] = angles(gs, before, po_unit)
        gs["score"] = story_score(gs, po_unit)
        facts["games"].append(gs)
    for gid, h, a, _k in exile_games:
        hp, ap, ot = fin[gid]
        facts["exile"].append(dict(id=gid, home=h, away=a, hp=hp, ap=ap, ot=ot))
    facts["standings"] = standings_brief(after, teams)
    return facts


def standings_brief(t, teams):
    """The league's best and worst records after the unit (clubs with a game played)."""
    ids = [i for i in teams if t.games(i)]
    ids.sort(key=lambda i: (-(t.pct(i) or 0), -(t.pf.get(i, 0) - t.pa.get(i, 0)), i))
    return dict(best=[[i, list(t.rec(i))] for i in ids[:3]], worst=[[i, list(t.rec(i))] for i in ids[-3:]],
                unbeaten=[i for i in ids if t.rec(i)[1] == 0 and t.rec(i)[2] == 0 and t.rec(i)[0] >= 4],
                winless=[i for i in ids if t.rec(i)[0] == 0 and t.rec(i)[2] == 0 and t.rec(i)[1] >= 4])


def angles(gs, before, po_unit):
    """The reasons a game might be a story, each with a strength 0-100. Machine-readable, so the writer and the checker know exactly what is claimed."""
    out = []
    h, a, win, lose, m = gs["home"], gs["away"], gs["winner"], gs["loser"], gs["margin"]
    if gs["ot"]:
        out.append(dict(t="overtime", s=45 + 10 * min(gs["ot"], 2), n=gs["ot"]))
    if m <= 3 and win is not None:
        out.append(dict(t="thriller", s=40 + (4 - m) * 3, margin=m))
    if m >= 28:
        out.append(dict(t="blowout", s=30 + min(m - 28, 14), margin=m))
    if win is not None and min(gs["hp"], gs["ap"]) == 0:
        out.append(dict(t="shutout", s=38, by=win))
    if not po_unit and win is not None and before.games(win) >= 3 and before.games(lose) >= 3:
        d = before.pct(lose) - before.pct(win)
        if d >= 0.3:
            out.append(dict(t="upset", s=int(40 + 60 * min(d, 0.7) / 0.7 * 0.6), diff=round(d, 2)))
    if not po_unit:
        for t in (h, a):
            b, r = gs["run_before"][str(t)], gs["run_after"][str(t)]
            if r >= 5:
                out.append(dict(t="win_streak", s=30 + 4 * min(r, 10), club=t, n=r))
            if r <= -5:
                out.append(dict(t="losing_streak", s=30 + 3 * min(-r, 10), club=t, n=-r))
            if b <= -4 and r == 1:
                out.append(dict(t="streak_snapped_loss", s=45 + min(-b, 8), club=t, n=-b))
            if b >= 4 and r == -1:
                out.append(dict(t="streak_snapped_win", s=45 + min(b, 8), club=t, n=b))
            rec = gs["rec_after"][str(t)]
            if rec[1] == 0 and rec[2] == 0 and rec[0] >= 4:
                out.append(dict(t="unbeaten", s=32 + 2 * min(rec[0], 8), club=t, n=rec[0]))
            if rec[0] == 0 and rec[2] == 0 and rec[1] >= 4:
                out.append(dict(t="winless", s=32 + 2 * min(rec[1], 8), club=t, n=rec[1]))
    for side in (h, a):
        for ln in gs["leaders"][str(side)]:
            if ln["kind"] == "pass" and (ln["yds"] >= 350 or ln["td"] >= 4):
                out.append(dict(t="big_night", s=40 + min((ln["yds"] - 300) // 10, 15) + 3 * ln["td"], club=side, line=ln))
            if ln["kind"] == "rush" and (ln["yds"] >= 160 or ln["td"] >= 3):
                out.append(dict(t="big_night", s=40 + min((ln["yds"] - 140) // 8, 15) + 3 * ln["td"], club=side, line=ln))
            if ln["kind"] == "rec" and (ln["yds"] >= 160 or ln["td"] >= 3):
                out.append(dict(t="big_night", s=40 + min((ln["yds"] - 140) // 8, 15) + 3 * ln["td"], club=side, line=ln))
    for inj in gs["injuries"]:
        out.append(dict(t="star_injury", s=36 + (10 if inj["rank"] == 1 else 0), club=inj["team"], who=inj["name"], pos=inj["pos"], inj=inj["kind"]))
    if po_unit:
        out.append(dict(t="playoff", s=60 + (30 if gs["kind"] == "playoff_final" else 8 * PO_ORDER.index(gs["kind"])), round=gs["kind"]))
    return out


def story_score(gs, po_unit):
    ss = sorted((a["s"] for a in gs["angles"]), reverse=True)
    if not ss:
        return 0
    return int(min(100, ss[0] + 0.25 * sum(ss[1:3])))


def paragraph_count(score, po_unit):
    n = 1 + (score >= 50) + (score >= 65) + (score >= 80) + (score >= 95)
    return min(n + (1 if po_unit and n < 5 else 0), 5)


def select(facts):
    """Choose 1-10 stories under the word cap. Quiet weeks get few; a roundup of the rest is always added (short). Order: biggest first."""
    po_unit = facts["unit"] in PO_ORDER
    ranked = sorted(facts["games"], key=lambda g: (-g["score"], g["id"]))
    chosen, words = [], 0
    roundup_words = 90
    for g in ranked:
        if len(chosen) >= MAX_STORIES - 1:
            break
        if g["score"] < MIN_SCORE and (chosen or po_unit is False and g["score"] == 0 and len(ranked) > 0 and chosen):
            break
        if g["score"] < MIN_SCORE and chosen:
            break
        n = paragraph_count(g["score"], po_unit)
        if chosen and words + n * PARA_WORDS + roundup_words > WORD_CAP:
            continue
        chosen.append(dict(game=g["id"], paras=n, score=g["score"]))
        words += n * PARA_WORDS
    if not chosen and ranked:
        g = ranked[0]
        chosen.append(dict(game=g["id"], paras=1, score=g["score"]))
    return chosen


# ------------------------------------------------------------------------------------------------ fact sheets

def club_block(feed, tid):
    t = feed.teams[tid]
    return dict(id=tid, name=t["name"], city=t["city"], nick=t["nick"], abbr=t["abbr"])


def fact_sheet(feed, facts, pick, recent=()):
    """The closed set of things a writer may say about one story. Names and numbers are collected so the checker can hold the text to them."""
    g = next(x for x in facts["games"] if x["id"] == pick["game"])
    sheet = dict(
        outlet=OUTLET, year=facts["year"], unit=facts["unit"], label=facts["label"], game=g["id"], kind=g["kind"], paragraphs=pick["paras"],
        home=club_block(feed, g["home"]), away=club_block(feed, g["away"]), hp=g["hp"], ap=g["ap"], overtime_periods=g["ot"], margin=g["margin"],
        winner=club_block(feed, g["winner"]) if g["winner"] is not None else None, loser=club_block(feed, g["loser"]) if g["loser"] is not None else None,
        records_before={k: rec_str(v) for k, v in g.get("rec_before", {}).items()}, records_after={k: rec_str(v) for k, v in g["rec_after"].items()},
        angles=sorted(g["angles"], key=lambda a: -a["s"])[:4], leaders=g["leaders"], injuries=g["injuries"], recent=list(recent))
    return finish_sheet(sheet)


def collect(obj, nums, words):
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, int):
        nums.add(abs(obj))
    elif isinstance(obj, float):
        nums.add(round(obj, 2))
    elif isinstance(obj, str):
        for m in re.findall(r"\d+", obj):
            nums.add(int(m))
        for w in re.findall(r"[A-Za-z][A-Za-z'’\.\-]*", obj):
            words.add(w.strip(".-").lower())
    elif isinstance(obj, dict):
        for v in obj.values():
            collect(v, nums, words)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            collect(v, nums, words)


def finish_sheet(sheet):
    """Add the allowed numbers and words. Derived numbers a writer may reasonably state (a combined score, differences) are included."""
    nums, words = set(), set()
    body = {k: v for k, v in sheet.items() if k not in ("allowed_numbers", "allowed_pairs", "allowed_words")}
    collect(body, nums, words)
    nums |= {sheet["hp"] + sheet["ap"], sheet["hp"], sheet["ap"], sheet["margin"], 0, 1, 2, 3, 4, 5}
    for rec in list(sheet["records_after"].values()) + list(sheet["records_before"].values()):
        for m in re.findall(r"\d+", rec):
            nums.add(int(m))
    pairs = {f"{sheet['hp']}-{sheet['ap']}", f"{sheet['ap']}-{sheet['hp']}"}
    for g in sheet.get("games", []):
        if isinstance(g, dict) and "hp" in g:
            pairs |= {f"{g['hp']}-{g['ap']}", f"{g['ap']}-{g['hp']}"}
            for rc in list(g.get("rec_after", {}).values()) + list(g.get("rec_before", {}).values()):
                pairs.add(f"{rc[0]}-{rc[1]}")
    for e in sheet.get("exile", []):
        pairs |= {f"{e['hp']}-{e['ap']}", f"{e['ap']}-{e['hp']}"}
    for rec in list(sheet["records_after"].values()) + list(sheet["records_before"].values()):
        pairs.add(re.match(r"\d+-\d+", rec).group(0))
    for rr in sheet.get("allowed_records", []):
        pairs.add(rr)
    sheet["allowed_pairs"] = sorted(pairs)
    sheet["allowed_numbers"] = sorted(nums)
    sheet["allowed_words"] = sorted(words)
    return sheet


# ------------------------------------------------------------------------------------------------ the checker

NUMWORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
            "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}
UNIT_AFTER = r"(?:-point|-yard|\s+points?|\s+yards?|\s+touchdowns?|\s+games?|\s+sacks?|\s+interceptions?|\s+turnovers?|\s+straight|\s+consecutive|\s+weeks?|\s+losses|\s+wins)"
OPENERS = set("""the a an in on at with after for as but and while when once still yet by from to of it its this that these those their her his she they there then so now here
meanwhile elsewhere however instead overall afterward later earlier today tonight saturday sunday monday friday thursday wednesday tuesday week round both each neither either one two
three four five six seven eight nine ten no not only even just also after before until since because despite behind against over under into through between among without within
across during along around if than too very more most less least much many few several some any all another other such what which who whom whose how why where whether""".split())
STOPCAPS = {"diamond", "football", "league", "chronicle", "dfl", "week", "wild", "card", "divisional", "conference", "coronation", "round", "overtime", "sunday", "saturday", "monday",
            "friday", "thursday", "wednesday", "tuesday", "ot", "qb", "rb", "wr", "te", "ol", "dl", "lb", "cb", "s", "k", "p", "championship", "championships", "final", "finals", "playoff",
            "playoffs", "division", "ambassador", "season", "year", "the", "a", "an"}


def check_text(text, sheet):
    """Problems found in a piece of text against its fact sheet: numbers and proper names that are not on it. Empty list: the text may be published."""
    problems = []
    nums = set(sheet["allowed_numbers"])
    words = set(sheet["allowed_words"]) | STOPCAPS
    for m in re.finditer(r"(?<![A-Za-z])\d[\d,]*", text):
        s = m.group(0).rstrip(",").replace(",", "")
        if s and int(s) not in nums:
            problems.append(f"number {s}")
    pairs = set(sheet.get("allowed_pairs", []))
    for m in re.finditer(r"(?<![\d-])(\d+)-(\d+)(?![\d-])", text):
        if m.group(0) not in pairs and not (m.group(2) == "0" and int(m.group(1)) in nums) and not (m.group(1) == "0" and int(m.group(2)) in nums):
            problems.append(f"score {m.group(0)}")
    for m in re.finditer(r"\b(" + "|".join(NUMWORDS) + r")\b" + UNIT_AFTER, text, flags=re.I):
        v = NUMWORDS[m.group(1).lower()]
        if v not in nums:
            problems.append(f"number {m.group(1)}")
    for sent in re.split(r"(?<=[.!?])\s+|\n+", text):
        toks = list(re.finditer(r"[A-Za-z][A-Za-z'’\-\.]*", sent))
        i = 0
        while i < len(toks):
            tk = toks[i].group(0)
            if not (tk[0].isupper()):
                i += 1
                continue
            j = i
            run = []
            while j < len(toks) and toks[j].group(0)[0].isupper() and (not run or toks[j].start() - toks[j - 1].end() <= 1):
                run.append(toks[j].group(0))
                j += 1
            first = i == 0
            while run and first and run[0].lower() in OPENERS:
                run.pop(0)
                first = False
            if first and len(run) == 1 and (run[0].lower().endswith(("ly", "ing")) or run[0].lower() in words):
                run = []
            for t in run:
                w = t.strip(".-").lower()
                for suf in ("'s", "’s", "'", "’"):
                    if w.endswith(suf):
                        w = w[:-len(suf)]
                        break
                if w and w not in words and w not in OPENERS and len(w) > 1:
                    problems.append(f"name {t}")
            i = j
    return problems


# ------------------------------------------------------------------------------------------------ the template writer

def _rng(sheet):
    return random.Random(int(hashlib.sha256(f"{sheet['year']}|{sheet['unit']}|{sheet['game']}".encode()).hexdigest()[:12], 16))


def _line_text(ln):
    if ln["kind"] == "pass":
        s = f"{ln['name']} threw for {ln['yds']} yards on {ln['cmp']} of {ln['att']}"
        if ln["td"]:
            s += f" with {ln['td']} touchdown{'s' if ln['td'] != 1 else ''}"
        if ln["int"]:
            s += f" and {ln['int']} interception{'s' if ln['int'] != 1 else ''}"
        return s
    if ln["kind"] == "rush":
        s = f"{ln['name']} ran {ln['car']} times for {ln['yds']} yards"
        if ln["td"]:
            s += f" and {ln['td']} touchdown{'s' if ln['td'] != 1 else ''}"
        return s
    if ln["kind"] == "rec":
        s = f"{ln['name']} caught {ln['rec']} passes for {ln['yds']} yards"
        if ln["td"]:
            s += f" and {ln['td']} touchdown{'s' if ln['td'] != 1 else ''}"
        return s
    if ln["kind"] == "sack":
        return f"{ln['name']} sacked the quarterback {ln['n']} times"
    return f"{ln['name']} came away with {ln['n']} interceptions"


def _decision(sheet, r):
    h, a = sheet["home"], sheet["away"]
    w, l = sheet["winner"], sheet["loser"]
    hp, ap = sheet["hp"], sheet["ap"]
    if w is None:
        return f"{h['name']} and {a['name']} played to a {hp}-{ap} tie."
    wp, lp = max(hp, ap), min(hp, ap)
    verb = r.choice(["beat", "defeated", "got past", "handled"] if sheet["margin"] > 3 else ["edged", "outlasted", "held off", "survived"])
    s = f"{w['name']} {verb} {l['name']} {wp}-{lp}"
    if sheet["overtime_periods"]:
        s += " in overtime" if sheet["overtime_periods"] == 1 else f" in {sheet['overtime_periods']} overtime periods"
    return s + (f" at {h['city']}." if w["id"] == a["id"] else ".")


def _headline(sheet, r):
    w, l = sheet["winner"], sheet["loser"]
    top = sheet["angles"][0]["t"] if sheet["angles"] else "result"
    if w is None:
        return f"{sheet['home']['nick']} and {sheet['away']['nick']} end level at {sheet['hp']}-{sheet['ap']}"
    score = f"{max(sheet['hp'], sheet['ap'])}-{min(sheet['hp'], sheet['ap'])}"
    opts = {
        "overtime": [f"{w['nick']} win it in overtime, {score}", f"{w['nick']} outlast {l['nick']} in overtime"],
        "thriller": [f"{w['nick']} survive {l['nick']}, {score}", f"{w['nick']} take a close one over {l['nick']}"],
        "upset": [f"{w['nick']} stun {l['nick']}, {score}", f"Upset: {w['nick']} topple {l['nick']}"],
        "blowout": [f"{w['nick']} run away from {l['nick']}, {score}", f"{w['nick']} romp past {l['nick']}"],
        "shutout": [f"{w['nick']} blank {l['nick']}, {score}"],
        "win_streak": [f"{w['nick']} keep rolling, {score} over {l['nick']}"],
        "losing_streak": [f"{l['nick']} slide on against {w['nick']}"],
        "streak_snapped_loss": [f"{w['nick']} finally win again, {score}"],
        "streak_snapped_win": [f"{w['nick']} end the {l['nick']} winning streak, {score}"],
        "unbeaten": [f"{w['nick']} stay unbeaten, {score}"],
        "winless": [f"{l['nick']} still looking for a first win"],
        "big_night": [f"{w['nick']} top {l['nick']}, {score}"],
        "star_injury": [f"{w['nick']} beat {l['nick']}, {score}, but injuries sting"],
        "playoff": [f"{w['nick']} advance, {score} over {l['nick']}", f"{l['nick']} are out: {w['nick']} win {score}"],
    }.get(top, [f"{w['nick']} {score} over {l['nick']}"])
    if sheet["kind"] == "playoff_final":
        return f"{w['nick']} are the champions: {score} over {l['nick']}"
    return r.choice(opts)


def write_template(sheet):
    """Free, deterministic prose from the fact sheet. Returns {headline, paragraphs}. Same sheet, same words."""
    r = _rng(sheet)
    h, a = sheet["home"], sheet["away"]
    w, l = sheet["winner"], sheet["loser"]
    ra, rb = sheet["records_after"], sheet["records_before"]
    league = sheet["kind"] in ("division", "tier", "nonconf")

    def T(c):
        return "the " + c["nick"]

    def Tc(c):
        return "The " + c["nick"]

    def nm_of(cid):
        return T(h) if cid == h["id"] else T(a)
    p1 = _decision(sheet, r)
    if ra and league:
        if w is not None:
            p1 += r.choice([f" The win moves {T(w)} to {ra[str(w['id'])]}; {T(l)} fall to {ra[str(l['id'])]}.", f" {Tc(w)} are {ra[str(w['id'])]} now, and {T(l)} are {ra[str(l['id'])]}."])
        else:
            p1 += f" {Tc(h)} are {ra[str(h['id'])]}, {T(a)} {ra[str(a['id'])]}."
    if ra and not league and w is not None:
        p1 += f" {Tc(w)} finished the regular season {ra[str(w['id'])]}; {T(l)} finished {ra[str(l['id'])]}."
    by_t = {x["t"]: x for x in sheet["angles"]}
    ctx = []
    if "upset" in by_t and w is not None and rb:
        ctx.append(f"It was a surprise. Coming in, {T(w)} were {rb[str(w['id'])]} and {T(l)} were {rb[str(l['id'])]}.")
    for t in ("streak_snapped_loss", "streak_snapped_win", "win_streak", "losing_streak", "unbeaten", "winless"):
        x = by_t.get(t)
        if not x:
            continue
        nm = nm_of(x["club"])
        ctx.append({"streak_snapped_loss": f"The win ends a run of {x['n']} straight losses for {nm}.",
                    "streak_snapped_win": f"The loss ends a run of {x['n']} straight wins for {nm}.",
                    "win_streak": f"That is {x['n']} straight wins for {nm}.",
                    "losing_streak": f"That is {x['n']} straight losses for {nm}.",
                    "unbeaten": f"{nm[0].upper() + nm[1:]} are still unbeaten at {x['n']}-0.",
                    "winless": f"{nm[0].upper() + nm[1:]} are still without a win after {x['n']} games."}[t])
        break
    if "shutout" in by_t and w is not None:
        ctx.append(f"{T(w)[0].upper() + T(w)[1:]} did not allow a point.")
    if "thriller" in by_t and "overtime" not in by_t and w is not None and not ctx:
        ctx.append(f"The final margin was {sheet['margin']} point{'s' if sheet['margin'] != 1 else ''}.")
    sides = (w, l) if w is not None else (h, a)
    lead = {}
    for sd in sides:
        lead[sd["id"]] = [_line_text(ln) for ln in sheet["leaders"].get(str(sd["id"]), [])[:3]]

    def sentence(sd, lines):
        return f"For {T(sd)}: " + "; ".join(lines) + "."
    paras = [p1]
    if ctx:
        paras.append(" ".join(ctx))
    n = sheet["paragraphs"]
    if n >= 4 or (n == 3 and not ctx):
        for sd in sides:
            if lead[sd["id"]]:
                paras.append(sentence(sd, lead[sd["id"]]))
    else:
        bits = [f"For {T(sd)}, {lead[sd['id']][0]}." for sd in sides if lead[sd["id"]]]
        if bits:
            paras.append(" ".join(bits))
    for ang in sheet["angles"]:
        if ang["t"] == "star_injury":
            paras.append(f"The bigger worry for {nm_of(ang['club'])} is {ang['who']}, the {ang['pos']}, who left the game with a {ang['inj']} injury.")
            break
    if sheet["kind"] == "playoff_final" and w is not None:
        paras.append(f"{w['name']} are the league's champions.")
    if len(paras) > n:                                    # keep the lead and the closing line (champion, injury) over middle detail
        paras = paras[:n - 1] + [paras[-1]] if sheet["kind"] == "playoff_final" else paras[:n]
    return dict(headline=_headline(sheet, r), paragraphs=paras)


def write_roundup(feed, facts, featured):
    """The short 'around the league' piece: scores of the games not given a story, and the unbeaten and winless clubs."""
    rest = [g for g in facts["games"] if g["id"] not in featured]
    if not rest and not facts["exile"]:
        return None
    teams = feed.teams
    bits = []
    for g in rest:
        h, a = teams[g["home"]]["nick"], teams[g["away"]]["nick"]
        if g["winner"] is None:
            bits.append(f"{h} and {a} tied {g['hp']}-{g['ap']}")
        elif g["winner"] == g["home"]:
            bits.append(f"{h} beat {a} {g['hp']}-{g['ap']}")
        else:
            bits.append(f"{a} won at {teams[g['home']]['city']}, {g['ap']}-{g['hp']}")
    paras = []
    if bits:
        paras.append("Elsewhere: " + "; ".join(bits) + ".")
    if facts["exile"]:
        ex = []
        for e in facts["exile"]:
            ex.append(f"{teams[e['home']]['nick']} {e['hp']}, {teams[e['away']]['nick']} {e['ap']}")
        paras.append("In the Ambassador Season: " + "; ".join(ex) + ".")
    st = facts["standings"]
    if st["unbeaten"] or st["winless"]:
        s = []
        if st["unbeaten"]:
            s.append("Still unbeaten: " + ", ".join(teams[i]["nick"] for i in st["unbeaten"]) + ".")
        if st["winless"]:
            s.append("Still winless: " + ", ".join(teams[i]["nick"] for i in st["winless"]) + ".")
        paras.append(" ".join(s))
    return dict(id="roundup", headline="Around the league", paragraphs=paras)


def roundup_sheet(feed, facts, featured, entry):
    """A fact sheet for the roundup (for the checker): every club and number in it."""
    sheet = dict(outlet=OUTLET, year=facts["year"], unit=facts["unit"], label=facts["label"], game="roundup", hp=0, ap=0, margin=0,
                 clubs=[club_block(feed, i) for i in feed.teams], games=[g for g in facts["games"] if g["id"] not in featured], exile=facts["exile"], standings=facts["standings"],
                 records_after={}, records_before={}, paragraphs=len(entry["paragraphs"]))
    return finish_sheet(sheet)


# ------------------------------------------------------------------------------------------------ the LLM writer (off unless configured)

class Budget:
    def __init__(self, path, limit):
        self.path, self.limit = path, limit

    def _month(self):
        return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m")

    def spent(self):
        try:
            d = jload(self.path)
        except (OSError, ValueError):
            return 0.0
        return float(d.get(self._month(), 0.0))

    def allows(self, estimate):
        return self.spent() + estimate <= self.limit

    def add(self, amount):
        try:
            d = jload(self.path)
        except (OSError, ValueError):
            d = {}
        d[self._month()] = round(float(d.get(self._month(), 0.0)) + amount, 6)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f)
        os.replace(tmp, self.path)


SYSTEM = ("You are a sports columnist for a national football paper covering the Diamond Football League, a fictional 48-club women's league. You will be given a FACT SHEET in JSON "
          "for one game. Write only from it. Every name and every number you use must appear in the fact sheet. Do not invent quotes, plays, weather, crowds, future results, "
          "coaches' words, or injuries beyond those listed. No quotation marks. Plain, vivid, grounded prose in the voice of a national outlet that reports each club's year as it was.")


def build_prompt(sheet, memory):
    keep = {k: v for k, v in sheet.items() if k not in ("allowed_numbers", "allowed_words", "allowed_pairs")}
    return (f"FACT SHEET:\n{json.dumps(keep, separators=(',', ':'))}\n\nRecent headlines for continuity (do not repeat them): {json.dumps(list(memory))}\n\n"
            f"Write exactly {sheet['paragraphs']} paragraph(s) and a headline. Reply with JSON only: {{\"headline\": \"...\", \"paragraphs\": [\"...\"]}}")


class LLMWriter:
    def __init__(self, env=None, transport=None):
        env = os.environ if env is None else env
        self.key, self.model = env.get("ANTHROPIC_API_KEY"), env.get("DFL_CHRONICLE_MODEL")
        try:
            self.p_in, self.p_out = float(env.get("DFL_PRICE_IN", "")), float(env.get("DFL_PRICE_OUT", ""))
        except ValueError:
            self.p_in = self.p_out = None
        self.transport = transport or self._http
        self.spent = 0.0

    def enabled(self):
        return bool(self.key and self.model and self.p_in is not None and self.p_out is not None)

    def estimate(self, prompt):
        return ((len(SYSTEM) + len(prompt)) / 4 * self.p_in + 450 * self.p_out) / 1e6

    def _http(self, body):
        import urllib.request
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
                                     headers={"x-api-key": self.key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())

    def write(self, sheet, memory):
        """(entry or None, dollars spent). None on any failure; the caller falls back to templates."""
        prompt = build_prompt(sheet, memory)
        body = dict(model=self.model, max_tokens=900, system=SYSTEM, messages=[dict(role="user", content=prompt)])
        resp = self.transport(body)
        u = resp.get("usage", {})
        cost = (u.get("input_tokens", 0) * self.p_in + u.get("output_tokens", 0) * self.p_out) / 1e6
        text = "".join(b.get("text", "") for b in resp.get("content", []))
        m = re.search(r"\{.*\}", text, flags=re.S)
        if not m:
            return None, cost
        try:
            d = json.loads(m.group(0))
            paras = [str(x) for x in d["paragraphs"]]
            return dict(headline=str(d["headline"]), paragraphs=paras), cost
        except (ValueError, KeyError, TypeError):
            return None, cost


# ------------------------------------------------------------------------------------------------ writing a unit

def entry_ok(entry, sheet):
    if not entry or not entry.get("paragraphs") or not entry.get("headline"):
        return ["empty"]
    if not 1 <= len(entry["paragraphs"]) <= 5:
        return ["paragraph count"]
    return check_text(entry["headline"] + "\n" + "\n".join(entry["paragraphs"]), sheet)


def compose(feed, facts, llm=None, budget=None, memory=()):
    """The unit's entries: the selected stories (LLM when allowed and it passes the checker, else templates) and the roundup."""
    picks = select(facts)
    entries, featured, log = [], set(), dict(llm_used=0, llm_rejected=0, cost=0.0)
    for pick in picks:
        sheet = fact_sheet(feed, facts, pick, memory)
        entry, how = None, "template"
        if llm is not None and llm.enabled():
            est = llm.estimate(build_prompt(sheet, memory))
            for _try in range(2):
                if budget is not None and not budget.allows(est):
                    break
                try:
                    cand, cost = llm.write(sheet, memory)
                except Exception:                                  # a network or API failure: templates carry on
                    break
                log["cost"] += cost
                if budget is not None:
                    budget.add(cost)
                if cand and not entry_ok(cand, sheet):
                    entry, how = cand, "llm"
                    log["llm_used"] += 1
                    break
                log["llm_rejected"] += 1
        if entry is None:
            entry = write_template(sheet)
            bad = entry_ok(entry, sheet)
            if bad:
                raise AssertionError(f"template text fails its own fact sheet ({facts['year']} {facts['unit']} {pick['game']}): {bad}")
        g = next(x for x in facts["games"] if x["id"] == pick["game"])
        entries.append(dict(id=pick["game"], headline=entry["headline"], paragraphs=entry["paragraphs"], score=pick["score"], how=how,
                            clubs=[g["home"], g["away"]], angles=[a["t"] for a in sorted(g["angles"], key=lambda a: -a["s"])[:3]]))
        featured.add(pick["game"])
    ru = write_roundup(feed, facts, featured)
    if ru:
        bad = check_text(ru["headline"] + "\n" + "\n".join(ru["paragraphs"]), roundup_sheet(feed, facts, featured, ru))
        if bad:
            raise AssertionError(f"roundup fails its own fact sheet: {bad}")
        entries.append(dict(id="roundup", headline=ru["headline"], paragraphs=ru["paragraphs"], score=0, how="template", clubs=[], angles=[]))
    return entries, log


def unit_names(feed, y):
    """The units of a year in order, that are complete in the feed."""
    season = feed.season(y)
    res = feed.results(y)
    out = [f"w{w}" for w in sorted(weeks_of(season))]
    out += [k for k in PO_ORDER if any(r[1] == k for r in season["po"])]
    return out


def write_once(path, obj):
    """Create the file only if it does not exist. Returns True if written. The words are never regenerated."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    return True


def league_id(feed):
    return f"{feed.meta.get('seed')}:{feed.meta.get('epoch_ms')}"


def scan(feed, out, llm=None, budget=None, now=None):
    """Write every finished unit not written yet. Returns the list of (year, unit) written."""
    os.makedirs(out, exist_ok=True)
    ident = league_id(feed)
    idp = os.path.join(out, "league.json")
    if os.path.exists(idp):
        if jload(idp).get("league") != ident:
            raise SystemExit("this chronicle belongs to another league (seed or start differs); refusing to mix them")
    else:
        with open(idp, "w") as f:
            json.dump(dict(league=ident), f)
    wrote = []
    for y in feed.years():
        memory = []
        for unit in unit_names(feed, y):
            fp = os.path.join(out, f"{y}_{unit}.json")
            if os.path.exists(fp):
                memory = [e["headline"] for e in jload(fp)["entries"][:3]]
                continue
            facts = build_unit(feed, y, unit)
            if facts is None:
                break                                              # later units cannot be finished before this one
            entries, log = compose(feed, facts, llm, budget, memory[-6:])
            doc = dict(v=VERSION, league=ident, year=y, season=feed.season(y)["season"], unit=unit, label=facts["label"], outlet=OUTLET, written=(now or dt.datetime.now(dt.timezone.utc)).isoformat(timespec="seconds"),
                       entries=entries, llm=log)
            if write_once(fp, doc):
                wrote.append((y, unit))
            memory = [e["headline"] for e in entries[:3]]
    write_index(out)
    return wrote


def write_index(out):
    items = []
    for fn in os.listdir(out):
        m = re.fullmatch(r"(\d+)_(\w+)\.json", fn)
        if m:
            d = jload(os.path.join(out, fn))
            items.append(dict(year=d["year"], season=d.get("season", d["year"]), unit=d["unit"], label=d["label"], file=fn, n=len(d["entries"]), top=d["entries"][0]["headline"] if d["entries"] else "", written=d["written"]))

    def key(i):
        u = i["unit"]
        return (i["year"], int(u[1:]) if u.startswith("w") else 100 + (PO_ORDER.index(u) if u in PO_ORDER else 9))
    items.sort(key=key)
    tmp = os.path.join(out, "index.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dict(v=VERSION, units=items), f, ensure_ascii=False)
    os.replace(tmp, os.path.join(out, "index.json"))


def estimate(feed):
    """How big one week's LLM prompts are, from the latest finished regular-season week (nothing written)."""
    for y in reversed(feed.years()):
        for unit in sorted(unit_names(feed, y), key=lambda u: u.startswith("w"))[::-1] if False else sorted(unit_names(feed, y), key=lambda u: (u.startswith("w"), unit_names(feed, y).index(u)), reverse=True):
            facts = build_unit(feed, y, unit)
            if facts:
                picks = select(facts)
                tot_in = 0
                for p in picks:
                    s = fact_sheet(feed, facts, p, ["x" * 60] * 3)
                    tot_in += (len(SYSTEM) + len(build_prompt(s, ["x" * 60] * 3))) // 4
                out_tok = sum(p["paras"] * 90 + 30 for p in picks)
                return dict(year=y, unit=unit, stories=len(picks), input_tokens=tot_in, output_tokens=out_tok)
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", required=True)
    ap.add_argument("--out")
    ap.add_argument("--every", type=float, default=0, help="keep scanning every N seconds (0: scan once)")
    ap.add_argument("--estimate", action="store_true")
    a = ap.parse_args(argv)
    feed = Feed(a.feed)
    if a.estimate:
        print(json.dumps(estimate(feed)))
        return 0
    if not a.out:
        ap.error("--out is required")
    llm = LLMWriter()
    budget = Budget(os.path.join(a.out, "spend.json"), float(os.environ.get("DFL_CHRONICLE_BUDGET", "18")))
    while True:
        try:
            feed = Feed(a.feed)
            for y, u in scan(feed, a.out, llm if llm.enabled() else None, budget):
                print(f"wrote {y} {u}", flush=True)
        except (OSError, ValueError, KeyError) as err:         # the feed was caught mid-write or the runner is replaying: try again next time round
            if not a.every:
                raise
            print(f"waiting: {err!r}", flush=True)
        if not a.every:
            return 0
        time.sleep(a.every)


if __name__ == "__main__":
    sys.exit(main())
