"""Recognition (Phase 4c): honors, esteem, what the media calls people, and the league Hall of Fame.

The Commissioner's rule (2026-10-04): no designated legends, and no limit on greatness. Legend is an emergent property the media notices,
and the Hall of Fame (the media plus the CEOs) confers.

How it works, and what it is allowed to touch:

  * HONORS are facts the engine knows: All-League, Player of the Year, titles, Coach of the Year, Executive of the Year. Each
    season's honors are written into the person's ledger.
  * ESTEEM is a single number for a person's career standing. Each season adds points for results and honors, and it fades a
    little each year while she is active (a career is judged by what she keeps doing). It stops fading when she retires.
  * STANDING is what the media calls her: known, respected, star, and then LEGEND. Each outlet reads her esteem with its own
    noise (a local outlet reads its own team's people kindly); the credibility-weighted share of outlets calling her a legend
    decides. When they split she is CONTESTED. Once she is a legend she keeps the title with a little extra room (sticky), so
    a legend does not flicker.
  * THE HALL OF FAME votes on retired people who waited a few years: every active outlet (weighted by credibility) and every
    CEO votes, and she goes in with three quarters of the vote. There is no cap and no quota; a class can be empty.
  * Reputation touches nothing (the Commissioner, 2026-10-10: organic outcomes). The dials for rope (more patience with a famous coach) and halo
    (a CEO sees a famous candidate's ratings a little higher) exist in staff_cards.py but are zero. The on-field effects of coaches, GMs and players stay
    capped exactly as before, so greatness is mostly reputation and story.

Every random draw comes from a generator private to the person, the outlet and the year.

All numbers are PLACEHOLDER dials, not league rules.
"""
from __future__ import annotations

from typing import Dict, List

import living as LV

# ---- dials: what earns esteem ---------------------------------------------------------------------
ESTEEM_DECAY = 0.06              # an active career's esteem fades this share each year
COACH_PTS = dict(record=6.0, playoff=1.0, title=7.0, award=3.0)    # record: points per unit of win% above .500
GM_PTS = dict(record=4.0, playoff=0.7, title=5.0, award=2.5)
OWNER_PTS = dict(record=4.0, playoff=0.8, title=6.0, approval=2.0)
PLAYER_PTS = dict(all_league=2.5, poy=4.0, title=1.2)
EXPECT_SPREAD = 0.25             # a team's expected win% runs from 0.5 + this (strongest) to 0.5 - this (weakest)
AWARD_MIN_GAP = 0.15             # a Coach (or Executive) of the Year must beat expectations by at least this
TITLE_MIN_OVR = 60               # a player counts as part of a title team above this overall
ALL_LEAGUE_SLOTS = {"QB": 1, "RB": 1, "WR": 2, "TE": 1, "OL": 3, "DL": 2, "LB": 2, "CB": 2, "S": 1, "K": 1, "P": 1}
POY_MIN_OVR = 78                 # a Player of the Year needs at least this overall
# ---- dials: the bar for "legend" (esteem), per kind of person, and the rungs below it as shares of the bar ----
LEGEND_BAR = {"coach": 23.0, "gm": 18.0, "owner": 21.0, "player": 26.0}
RUNGS = ((0.15, "known"), (0.35, "respected"), (0.60, "star"))
OUTLET_NOISE = 0.10              # how far one outlet's reading of a person's esteem strays
HOMER = 1.15                     # a local outlet reads its own team's people this much higher
LOCAL_WEIGHT = 0.5
LEGEND_SHARE = 0.60              # the credibility-weighted share of outlets that makes a legend
CONTESTED_SHARE = 0.30
LEGEND_STICK = 0.85              # a person who is already a legend is judged against this share of the bar
# ---- dials: the Hall of Fame -----------------------------------------------------------------------------
HOF_WAIT = 3                     # years after retiring before the first ballot
HOF_BALLOTS = 6                  # years on the ballot
HOF_FLOOR = 0.55                 # share of the legend bar below which nobody is on the ballot
HOF_BAR = 0.80                   # a voter votes yes if her reading of the person's esteem is above this share of the legend bar
HOF_SHARE = 0.75                 # share of the vote needed
HOF_NOISE = 0.15
# ---- dials: what reputation buys from CEOs ---------------------------------------------------------------
RATIO_CAP = 1.5

KINDS = ("coach", "gm", "owner", "player")


def kind_of(card) -> str:
    if hasattr(card, "cid"):
        return "coach"
    if hasattr(card, "gid"):
        return "gm"
    if hasattr(card, "oid"):
        return "owner"
    return "player"


def cid_of(card) -> int:
    return card.pid if hasattr(card, "pid") else LV.ident(card)


def esteem_ratio(card) -> float:
    """Esteem as a share of the legend bar, capped. What CEOs react to."""
    return max(0.0, min(RATIO_CAP, card.esteem / LEGEND_BAR[kind_of(card)]))


# ---- honors and esteem ----------------------------------------------------------------------------------
def _honor(card, year: int, honor: str, **kw):
    card.honors.append(dict(year=year, honor=honor, **kw))


def _expected(lg, pct: Dict[int, float]):
    """Each active team's expected win%, from its strength rank at kickoff."""
    act = [t for t in lg.teams if t.id in pct and t.status == "active"]
    order = sorted(act, key=lambda t: -t.strength)
    n = len(order)
    return {t.id: 0.5 + EXPECT_SPREAD * (1.0 - 2.0 * (i + 0.5) / n) for i, t in enumerate(order)}


def season_honors(lg, year: int, pct: Dict[int, float], champion: int, playoff_teams):
    """Called once a season, after the playoffs and before anyone changes teams: honors and esteem for everyone who played,
    coached, managed or owned a team this year, then the media's reading of who is a legend. Never touches a game."""
    exp = _expected(lg, pct)
    # --- awards that go to one person a year
    gaps = {tid: pct[tid] - exp[tid] for tid in exp}
    coty = max(gaps, key=lambda i: (gaps[i], -i)) if gaps else None
    for t in lg.teams:
        tid = t.id
        if tid not in pct:
            continue
        won = tid == champion
        made = tid in playoff_teams
        rec = pct[tid] - 0.5
        for card, pts, kind in ((t.coach, COACH_PTS, "coach"), (t.gm, GM_PTS, "gm")):
            if card is None:
                continue
            gain = pts["record"] * rec + pts["playoff"] * made + pts["title"] * won
            if won:
                _honor(card, year, "Champion", team=tid)
            if tid == coty and gaps[tid] >= AWARD_MIN_GAP:
                _honor(card, year, "Coach of the Year" if kind == "coach" else "Executive of the Year", team=tid)
                gain += pts["award"]
            _bank(card, gain)
        o = t.owner
        if o is not None:
            gain = OWNER_PTS["record"] * rec + OWNER_PTS["playoff"] * made + OWNER_PTS["title"] * won + OWNER_PTS["approval"] * (o.approval - 0.5)
            if won:
                _honor(o, year, "Champion", team=tid)
            _bank(o, gain)
    _player_honors(lg, year, champion)
    # --- what the media makes of it
    media_notice(lg, year)


def _bank(card, gain: float):
    card.esteem = max(0.0, (card.esteem if _retired(card) else card.esteem * (1.0 - ESTEEM_DECAY)) + gain)


def _retired(card) -> bool:
    if hasattr(card, "pid"):
        return False                      # a player's retired flag lives on the Player; the card is decayed only while she is in the loop
    if hasattr(card, "cid"):
        return card.retired
    return getattr(card, "status", "") in ("retired",)


def _player_honors(lg, year: int, champion: int):
    pool: Dict[str, list] = {}
    for t in lg.teams:
        if t.roster is None:
            continue
        for p in t.roster:
            if p.card is None:
                continue
            p.card.esteem *= (1.0 - ESTEEM_DECAY)
            pool.setdefault(p.pos, []).append(p)
    # titles
    champ = lg.by_id.get(champion)
    if champ is not None and champ.roster is not None:
        for p in champ.roster:
            if p.card is not None and p.ovr >= TITLE_MIN_OVR:
                _honor(p.card, year, "Champion", team=champion)
                p.card.esteem += PLAYER_PTS["title"]
    # All-League: the best at each position, and the best player of all
    top = None
    for pos, k in ALL_LEAGUE_SLOTS.items():
        ranked = sorted(pool.get(pos, []), key=lambda p: (-p.ovr, p.id))[:k]
        for p in ranked:
            _honor(p.card, year, "All-League", pos=pos, team=p.team_id)
            p.card.esteem += PLAYER_PTS["all_league"]
            if pos not in ("K", "P") and (top is None or p.ovr > top.ovr):
                top = p
    if top is not None and top.ovr >= POY_MIN_OVR:
        _honor(top.card, year, "Player of the Year", pos=top.pos, team=top.team_id)
        top.card.esteem += PLAYER_PTS["poy"]


# ---- the media ---------------------------------------------------------------------------------------------
def _rung(share_of_bar: float) -> str:
    out = ""
    for cut, label in RUNGS:
        if share_of_bar >= cut:
            out = label
    return out


def media_notice(lg, year: int):
    """Every active outlet reads the esteem of everyone above the lowest rung; the credibility-weighted share that calls a person
    a legend decides it. Writes the Archive entries when a legend is recognized, contested, or lost."""
    outlets = [m for m in lg.media if m.status == "active"]
    for card, team_id in _with_teams(lg):
        kind = kind_of(card)
        bar = LEGEND_BAR[kind]
        if card.standing == "Hall of Famer":
            continue
        if card.esteem < RUNGS[0][0] * bar and card.standing not in ("legend", "contested"):
            card.standing = ""
            continue
        was = card.standing
        if outlets:
            share = _legend_share(lg, card, kind, team_id, outlets, bar, year, sticky=(was == "legend"))
        else:
            share = 1.0 if card.esteem >= bar else 0.0
        if share >= LEGEND_SHARE:
            now = "legend"
        elif share >= CONTESTED_SHARE:
            now = "contested"
        else:
            now = _rung(card.esteem / bar)
        if was == "legend" and now == "contested":
            now = "contested"
        card.standing = now
        if now != was and (now in ("legend", "contested") or was == "legend"):
            ev = ("legend_recognized" if now == "legend" else "legend_contested" if now == "contested" else "legend_slipped")
            lg.archive.append(dict(year=year, event=ev, kind=kind, id=cid_of(card), name=card.name, esteem=round(card.esteem, 1),
                                   outlets_calling_it=round(share, 2)))


def _with_teams(lg):
    """Everyone who might be noticed: the people on the job and those between jobs, plus retired people with enough esteem to
    still matter (they can still be named a legend)."""
    for t in lg.teams:
        for c in (t.coach, t.gm, t.owner):
            if c is not None:
                yield c, t.id
        for p in (t.roster or ()):
            if p.card is not None and p.card.esteem >= RUNGS[0][0] * LEGEND_BAR["player"] or (p.card is not None and p.card.standing):
                yield p.card, t.id
    for pool in (lg.free_coaches, lg.free_gms):
        for c in pool:
            yield c, None
    for p in lg.free_agents:
        if p.card is not None and (p.card.esteem >= RUNGS[0][0] * LEGEND_BAR["player"] or p.card.standing):
            yield p.card, None
    for c in lg.coaches:
        if c.retired and c.esteem >= RUNGS[0][0] * LEGEND_BAR["coach"] and c.standing != "Hall of Famer":
            yield c, None
    for g in lg.gms:
        if g.status == "retired" and g.esteem >= RUNGS[0][0] * LEGEND_BAR["gm"] and g.standing != "Hall of Famer":
            yield g, None
    for o in lg.owners:
        if o.status in ("retired", "recalled", "sold") and o.esteem >= RUNGS[0][0] * LEGEND_BAR["owner"] and o.standing != "Hall of Famer":
            yield o, None
    for p in lg.retired_players:
        if p.card is not None and p.card.esteem >= RUNGS[0][0] * LEGEND_BAR["player"] and p.card.standing != "Hall of Famer":
            yield p.card, None


def _legend_share(lg, card, kind: str, team_id, outlets, bar: float, year: int, sticky: bool) -> float:
    cutoff = bar * (LEGEND_STICK if sticky else 1.0)
    cid = cid_of(card)
    num = den = 0.0
    for m in outlets:
        if m.kind == "local" and m.team_id != team_id:
            continue
        w = (LOCAL_WEIGHT if m.kind == "local" else 1.0) * m.credibility / 100.0
        r = LV.rng(lg.card_seed, "notice", kind, cid, m.mid, year)
        seen = card.esteem * (HOMER if m.kind == "local" else 1.0) * (1.0 + r.gauss(0.0, OUTLET_NOISE))
        num += w * (seen >= cutoff)
        den += w
    return num / den if den else 0.0


# ---- the Hall of Fame ----------------------------------------------------------------------------------------
def _retired_year(card):
    for e in reversed(card.career):
        if e["event"] in ("retired", "recalled"):
            return e["year"]
    return None


def hall_vote(lg, year: int):
    """The yearly ballot. Returns the people inducted this year. No cap, no quota."""
    outlets = [m for m in lg.media if m.status == "active"]
    owners = [t.owner for t in lg.teams if t.owner is not None]
    if not outlets and not owners:
        return []
    ballot = []
    for lst, kind in ((lg.coaches, "coach"), (lg.gms, "gm"), (lg.owners, "owner"), (lg.retired_players, "player")):
        for c in lst:
            card = c.card if kind == "player" else c
            if card is None or card.standing == "Hall of Famer":
                continue
            if kind == "coach" and not c.retired or kind == "gm" and c.status != "retired" or kind == "owner" and c.status not in ("retired", "recalled", "sold"):
                continue
            ry = _retired_year(card)
            if ry is None or not (ry + HOF_WAIT <= year < ry + HOF_WAIT + HOF_BALLOTS):
                continue
            if card.esteem < HOF_FLOOR * LEGEND_BAR[kind]:
                continue
            ballot.append((kind, card))
    inducted = []
    for kind, card in sorted(ballot, key=lambda kc: (kc[0], cid_of(kc[1]))):
        bar = HOF_BAR * LEGEND_BAR[kind]
        cid = cid_of(card)
        yes = tot = 0.0
        for m in outlets:
            w = m.credibility / 100.0
            r = LV.rng(lg.card_seed, "hof", kind, cid, m.mid, year)
            yes += w * (card.esteem * (1.0 + r.gauss(0.0, HOF_NOISE)) >= bar)
            tot += w
        for o in owners:
            r = LV.rng(lg.card_seed, "hof", kind, cid, "o", o.oid, year)
            yes += card.esteem * (1.0 + r.gauss(0.0, HOF_NOISE)) >= bar
            tot += 1.0
        share = yes / tot if tot else 0.0
        card.career.append({"year": year, "event": "hof_ballot", "share": round(share, 2)})
        if share >= HOF_SHARE:
            card.standing = "Hall of Famer"
            _honor(card, year, "Hall of Fame", share=round(share, 2))
            entry = dict(year=year, kind=kind, id=cid, name=card.name, esteem=round(card.esteem, 1), share=round(share, 2),
                         honors=_honor_counts(card))
            lg.hall.append(entry)
            lg.archive.append(dict(year=year, event="hall_of_fame", **{k: v for k, v in entry.items() if k != "year"}))
            inducted.append(entry)
    return inducted


def _honor_counts(card) -> Dict[str, int]:
    h: Dict[str, int] = {}
    for e in card.honors:
        if e["honor"] != "Hall of Fame":
            h[e["honor"]] = h.get(e["honor"], 0) + 1
    return h
