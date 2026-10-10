"""The general manager builds the roster (Step C of the ring of accountability).

The GM scouts and assembles the team. Step B gave her the offseason plan (gm_plan.py). Here the four things she does with it are hers too,
each a Decision Point whose default is exactly what the engine's own rule did, so a league on the autopilot is unchanged:

  * `gm_draft_pick`: the prospect a first-round pick takes. The rule's pick (the best player on the consensus board, tilted toward the club's needs) is
    the default; she is shown that prospect and the one among the top of the board who would add the most role utility (roles.py) to her club, as
    the scouts' stat lines and her eye for talent give them to her, and may take the other instead. Later rounds stay with the scouts, as in the NFL,
    where the GM's board matters most at the top.
  * `gm_resign`: whether to keep an important player (rated at the contract-table line or better) whose deal is up, or to extend one mid-contract.
    Only asked when the cap would allow the deal. A cornerstone (role utility far above the club's keep line) cannot be let go (the franchise tag
    exists to keep one), and a GM lets at most one important player walk against the rule in an offseason.
  * `gm_free_agent`: which free agent the club signs when its turn comes and the best fit would start for it (role utility of a starter or better): the two the rule likes best.
  * `gm_trade_sell` / `gm_trade_buy`: whether the GM who starts a trade the market has put together (autotrade.py) agrees to it: the seller of a veteran for
    picks, or the club moving up the board in a swap. The legality checks and the Commissioner's review come after, as before.

What she sees. She sees her own roster exactly. She sees other clubs' players through her eye for talent: each veteran's rating is blurred by her
`evaluation` rating (about one rating point for the best eye, about six for the worst), and a trade's value in draft-chart points by her `trades`
rating. The blur comes from the GM's own card seed, never from the engine's random stream. Role utility (roles.py) is computed from what she sees.

Everything here is bounded by the engine: the cap, the roster limits, tenders and the trade rules still decide what can happen, and the fairness bands
are re-tested with agents choosing at random.
"""
from __future__ import annotations

import cards as C
import roles

ASK_ROUNDS = 1                       # draft rounds in which the GM chooses the prospect (0-based rounds below this): the first round, where her board matters most
ALTERNATES = 1                       # prospects offered besides the rule's: the one among the top of the board who would add the most role utility
BOARD_WINDOW = 12                    # how far down the consensus board the GM looks for an alternate
CORNERSTONE_MARGIN = 45.0             # a player whose role utility is this far above the club's keep line is a cornerstone: the GM cannot let her walk (the franchise tag exists to keep one)
LET_GO_MAX = 1                       # most important players one GM can let walk in an offseason when the rule would keep them (the franchise tag and the cap bound a real GM the same way)
FA_SHOWN = 2                         # free agents offered: the rule's pick and the next best fit
FA_ASK_MIN_GAIN = 5.0                # she is asked when the best fit would start for the club (role utility above this: a starter's floor is 5)
EYE_BASE, EYE_SPAN = 1.0, 20.0       # blur sd on a rating = EYE_BASE + (100 - rating)/EYE_SPAN
TRADE_BLUR_BASE, TRADE_BLUR_SPAN = 0.03, 700.0     # blur on a chart value = TRADE_BLUR_BASE + (100 - rating)/TRADE_BLUR_SPAN


def _eye(lg, g, kind: str, year: int, key, ovr: float) -> float:
    r = C._rng(lg.card_seed, "gmview", g.gid, year, kind, key)
    return round(ovr + r.gauss(0.0, EYE_BASE + (100.0 - g.ratings["evaluation"]) / EYE_SPAN), 1)


def _chart(lg, g, kind: str, year: int, key, points: float) -> float:
    r = C._rng(lg.card_seed, "gmview", g.gid, year, kind, key)
    return round(points * max(0.2, 1.0 + r.gauss(0.0, TRADE_BLUR_BASE + (100.0 - g.ratings["trades"]) / TRADE_BLUR_SPAN)), 0)


def _log(g, year: int, text: str):
    g.decision_log.append({"year": year, "action": text})


def _rank(lg, t) -> int:
    return 1 + sum(1 for x in lg.teams if x.strength > t.strength)


# ---- the draft -------------------------------------------------------------------------------------------------------------------------
def draft_pick(lg, t, year: int, overall: int, rnd: int, drawn, board, rm, focus: str):
    """The prospect the club takes at this pick: the rule's (`drawn`, a player on the board) unless the GM chooses another in the first round.
    She is shown the rule's prospect and the best alternate among the top of the board, each as she sees them: college, the production grade the
    scouts read off the stat lines (blurred by her eye), and the role utility a player of that grade would add to her roster."""
    g = t.gm
    if g is None or rnd >= ASK_ROUNDS:
        return drawn
    import decisions as D
    import prospects as PR
    import staff_cards as SC
    from positions import POSITIONS, ROSTER_COUNTS
    bonus = SC.gm_scouting_bonus(t)
    counts = {p: 0 for p in POSITIONS}
    for q in t.roster:
        counts[q.pos] += 1
    seen = {}

    def see(p):
        if p.id not in seen:
            seen[p.id] = _eye(lg, g, "draft", year, p.id, p.origin["grade"]) + bonus
        return seen[p.id]

    scored = []
    for p in board[:BOARD_WINDOW]:
        if p is drawn:
            continue
        if p.pos in ("K", "P") and (overall <= 100 or counts[p.pos] >= ROSTER_COUNTS[p.pos]):
            continue                                       # no one spends a first- or second-round pick on a kicker or punter
        scored.append((roles.utility(t.roster, p.pos, see(p)), p))
    scored.sort(key=lambda x: (-x[0], x[1].origin["class_rank"]))
    pick_list = [drawn] + [p for _, p in scored[:ALTERNATES]]

    def opt(p):
        u = roles.utility(t.roster, p.pos, see(p))
        o = p.origin
        return dict(id=str(p.id), label=f"Take {p.pos} from {o['college']} (board rank {o['class_rank']})",
                    tags=dict(position=p.pos, college=o["college"], board_rank=o["class_rank"], age=p.age, grade_as_you_see_her=round(see(p), 1),
                              role_utility=round(u, 1), would_be=roles.role_if_signed(t.roster, p.pos, see(p)),
                              senior_year=PR.stat_line(p.pos, o["stats"][-1]), on_roster=counts[p.pos], roster_wants=ROSTER_COUNTS[p.pos]))
    ctx = dict(draft="the draft", round=rnd + 1, overall_pick=overall,
               your_plan="draft for need" if focus == "needs" else "draft the best player", your_team_strength_rank=_rank(lg, t),
               note="You see your own roster exactly. A prospect's grade is what the scouts read off her college production, blurred by your eye for talent; "
                    "her true rating is not known until she plays. Role utility is what a player of that grade adds in the role she would play.")
    dp = D.DecisionPoint("gm_draft_pick", year, t.id, "gm", g, ctx, [opt(p) for p in pick_list], str(drawn.id),
                         dict(team=t, strength_rank=ctx["your_team_strength_rank"], true={str(p.id): (p.pos, p.ovr) for p in pick_list}))
    chosen = D.decide(lg, dp)
    if chosen != str(drawn.id):
        took = next(p for p in pick_list if str(p.id) == chosen)
        _log(g, year, f"took a {took.pos} from {took.origin['college']} at pick {overall} (the board said a {drawn.pos} from {drawn.origin['college']})")
        return took
    return drawn


# ---- re-signing and extensions ----------------------------------------------------------------------------------------------------------
def resign(lg, rm, t, year: int, p, price: float, wants: bool, keep, extension: bool, let_go=None) -> bool:
    """Does the club keep this important player at her price? `wants` is the engine's rule (the default). Only called when the cap allows it."""
    g = t.gm
    if g is None:
        return wants
    import decisions as D
    import staff_cards as SC
    rest = [k for k in keep if k is not p]
    if wants and not extension:
        line = rm.keep_g0 + rm.keep_g1 * price + rm.keep_gm_shift * (SC.gm_retention_factor(t) - 1.0)
        if roles.utility(rest, p.pos, p.ovr) - line > CORNERSTONE_MARGIN:
            return wants                                   # a cornerstone: the rule keeps her whatever the GM would like
        if let_go is not None and let_go.get(t.id, 0) >= LET_GO_MAX:
            return wants                                   # she has already let her one important player go this offseason: the rule keeps the rest
    seen = _eye(lg, g, "resign", year, p.id, p.ovr)
    u = roles.utility(rest, p.pos, seen)
    ctx = dict(player=dict(position=p.pos, age=p.age, rating_as_you_see_her=seen, seasons_in_league=p.years_in_league),
               what="an extension before her contract runs out" if extension else "her contract is up",
               her_price_per_year_m=round(price, 2), role_utility_to_you=round(u, 1),
               her_role_if_kept=roles.role_if_signed(rest, p.pos, seen), your_team_strength_rank=_rank(lg, t),
               note="The cap allows this deal. If you let her go she reaches the market, and you fill her place from the draft or free agency.")
    opts = [dict(id="re_sign", label="Extend her now" if extension else "Re-sign her", tags=dict(price_m=round(price, 2))),
            dict(id="let_walk", label="Pass on the extension" if extension else "Let her go", tags={})]
    default = "re_sign" if wants else "let_walk"
    chosen = D.decide(lg, D.DecisionPoint("gm_resign", year, t.id, "gm", g, ctx, opts, default, dict(team=t, player=p, rest=rest, strength_rank=ctx["your_team_strength_rank"])))
    if chosen != default:
        _log(g, year, f"{'re-signed' if chosen == 're_sign' else 'let go'} a {p.pos} the rule would have {'let go' if chosen == 're_sign' else 're-signed'}")
    if wants and not extension and chosen == "let_walk" and let_go is not None:
        let_go[t.id] = let_go.get(t.id, 0) + 1
    return chosen == "re_sign"


# ---- free agency ----------------------------------------------------------------------------------------------------------------------
def free_agent(lg, t, year: int, cands, best, price_of):
    """The free agent the club signs. `cands` = [(gain, player)] the club could sign and afford, in the engine's order; `best` is the rule's pick."""
    g = t.gm
    if g is None or len(cands) < 2:
        return best
    import decisions as D
    top = sorted(cands, key=lambda x: -x[0])[:FA_SHOWN]
    if best not in [c for _, c in top]:
        top = top[:FA_SHOWN - 1] + [next(x for x in cands if x[1] is best)]
    opts = []
    for _, c in top:
        seen = _eye(lg, g, "fa", year, c.id, c.ovr)
        opts.append(dict(id=f"p{c.id}", label=f"Sign a {c.pos}",
                         tags=dict(position=c.pos, age=c.age, rating_as_you_see_her=seen, price_m=round(price_of(c), 2),
                                   role_utility=round(roles.utility(t.roster, c.pos, seen), 1), would_be=roles.role_if_signed(t.roster, c.pos, seen))))
    ctx = dict(market="free agency", open_positions=sorted({c.pos for _, c in top}), your_team_strength_rank=_rank(lg, t),
               note="These are the best fits for the holes in your roster that you can afford. The rest of your open places are filled after.")
    chosen = D.decide(lg, D.DecisionPoint("gm_free_agent", year, t.id, "gm", g, ctx, opts, f"p{best.id}",
                                                  dict(team=t, candidates={f"p{c.id}": c for _, c in top}, strength_rank=ctx["your_team_strength_rank"])))
    pick = next((c for _, c in top if f"p{c.id}" == chosen), best)
    if pick is not best:
        _log(g, year, f"signed a {pick.pos} over the {best.pos} the rule preferred")
    return pick


# ---- trades ---------------------------------------------------------------------------------------------------------------------------
def _pick_text(lg, key) -> str:
    pk = lg.movement.picks.get(key)
    if pk is None:
        return str(key)
    return f"{pk.year} round {pk.rnd}" + (f" (slot {pk.slot})" if pk.slot is not None else "")


def trade_ok(lg, rm, a: int, b: int, pa, pb, ka, kb, pts: float, year: int, week) -> bool:
    """The GM of the club that starts a trade the market has put together agrees or declines. A club without a GM agrees (the rule). Default: agree.
    Club `a` starts it: in a sale it is the seller (it picked the player it can spare), in a pick swap it is the club moving up the board. The other
    club is the market's willing counterparty (autotrade finds a buyer that would start her and can afford her), so it is not asked: one GM's
    decision per trade, as in the NFL, where the club that wants to deal makes the call and the other side's price is the chart."""
    import decisions as D
    kind_a = "gm_trade_sell" if pa else "gm_trade_buy"
    sides = ((kind_a, a, b, pa, ka, pb, kb),)
    dps = []
    for kind, me, other, give_p, give_k, get_p, get_k in sides:
        t, o = lg.by_id[me], lg.by_id[other]
        if t.gm is None:
            continue
        g = t.gm
        gp = [q for q in t.roster if q.id in give_p]
        rp = [q for q in o.roster if q.id in get_p]
        rest = [q for q in t.roster if q.id not in give_p]
        lost = sum(roles.utility(rest, q.pos, _eye(lg, g, "trade", year, q.id, q.ovr)) for q in gp)
        gained = sum(roles.utility(rest, q.pos, _eye(lg, g, "trade", year, q.id, q.ovr)) for q in rp)

        def view(q):
            return dict(position=q.pos, age=q.age, rating_as_you_see_her=_eye(lg, g, "trade", year, q.id, q.ovr), years_left=q.years_left,
                        pay_m=round(q.salary, 2), your_role=roles.role_of(t.roster, q) if q in t.roster else roles.role_if_signed(rest, q.pos, q.ovr))
        ctx = dict(trade="a trade the market has put together", with_club=o.name, when="the offseason" if week is None else f"week {week}",
                   you_give=dict(players=[view(q) for q in gp], picks=[_pick_text(lg, k) for k in give_k]),
                   you_get=dict(players=[view(q) for q in rp], picks=[_pick_text(lg, k) for k in get_k]),
                   chart_points_you_give=_chart(lg, g, "tradeg", year, (me, other, tuple(give_p), tuple(give_k)), _side_points(lg, rm, give_p, give_k, t)),
                   chart_points_you_get=_chart(lg, g, "tradeg", year, (other, me, tuple(get_p), tuple(get_k)), _side_points(lg, rm, get_p, get_k, o)),
                   role_utility_you_lose=round(lost, 1), role_utility_you_gain=round(gained, 1), your_team_strength_rank=_rank(lg, t))
        dps.append(D.DecisionPoint(kind, year, me, "gm", g, ctx,
                                   [dict(id="accept", label="Agree to the trade", tags={}), dict(id="decline", label="Decline", tags={})], "accept",
                                   dict(team=t, strength_rank=_rank(lg, t), true_give=_side_points(lg, rm, give_p, give_k, t), true_get=_side_points(lg, rm, get_p, get_k, o))))
    if not dps:
        return True
    picks = D.decide_many(lg, dps)
    for dp, ch in zip(dps, picks):
        if ch != "accept":
            _log(dp.actor, year, "declined a trade the market had put together")
    return all(ch == "accept" for ch in picks)


def _side_points(lg, rm, players, keys, club) -> float:
    import autotrade
    tot = 0.0
    for k in keys:
        pk = lg.movement.picks.get(k)
        if pk is not None:
            tot += autotrade.pick_value(pk)
    for q in club.roster:
        if q.id in players:
            tot += autotrade.player_points(q, rm)
    return tot
