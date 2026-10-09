"""Step 6e to 6h: waivers, tags, trades, compensatory awards.

    python engine/check_transactions.py
"""
import os
import random
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contracts as CT  # noqa: E402
import decisions as D  # noqa: E402
import economy as EC  # noqa: E402
import movement as MV  # noqa: E402
import rosters  # noqa: E402
import store  # noqa: E402
import tables as TB  # noqa: E402
import rules as R  # noqa: E402
import transactions as T  # noqa: E402
from check_movement import scenario, everyone, expiring, state  # noqa: E402
from movement import MovementError  # noqa: E402
from positions import ROSTER_COUNTS, ROSTER_SIZE  # noqa: E402
from schedule import Game  # noqa: E402
from season import Options, run_season  # noqa: E402


def game(week, home, away, hp, ap, kind="division"):
    g = Game(week, home, away, kind)
    g.home_pts, g.away_pts = hp, ap
    return g


def make_short(lg, t, pos):
    """Take a club below its table count at `pos` and leave it a place on the 53."""
    gone = [p for p in t.roster if p.pos == pos][:1]
    t.roster.remove(gone[0])
    EC.release(t, gone[0])
    gone[0].team_id = None
    lg.free_agents.append(gone[0])
    for q in [q for q in t.practice_squad if q.pos == pos]:
        t.practice_squad.remove(q)
    return gone[0]


def star(lg, club, pos, salary=3.0, years=3, ovr=99.0):
    p = next(p for p in lg.by_id[club].roster if p.pos == pos)
    p.ovr = ovr
    EC.sign(p, salary, years)
    return p


class Waivers(unittest.TestCase):
    def setUp(self):
        self.lg, self.rng, self.pick_of = scenario(seed=11, year=1)
        for t in self.lg.teams:
            t.dead_now = t.dead_next = 0.0

    # 1 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_record_counts_only_games_that_count(self):
        rec = {}
        T.note_result(rec, game(1, 1, 2, 24, 17))
        T.note_result(rec, game(2, 1, 3, 20, 20))
        T.note_result(rec, game(3, 2, 3, 3, 10, "ambassador"))
        T.note_result(rec, game(4, 1, 2, 30, 0, "playoff_wild"))
        T.note_result(rec, game(5, 1, 2, 30, 0, "ambassador_bowl"))
        self.assertEqual(rec, {1: [1, 0, 1], 2: [0, 2, 0], 3: [1, 0, 1]})
        self.assertAlmostEqual(T.win_pct(rec, 1), 0.75)
        self.assertAlmostEqual(T.win_pct(rec, 2), 0.0)
        self.assertEqual(T.win_pct(rec, 99), 0.5)                    # no games yet: level

    # 2 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_priority_follows_last_draft_early_then_record(self):
        lg = self.lg
        lg.movement.begin_year(lg, 2, {t.id: 49 - (i + 1) for i, t in enumerate(lg.teams)})      # the draft of year 2: reverse id order
        year = 3
        slots = T.last_draft_slots(lg, year)
        self.assertEqual(sorted(slots.values()), list(range(1, 49)))
        early = T.priority_order(lg, year, R.WAIVER_DRAFT_ORDER_WEEKS, {})
        self.assertEqual(early, sorted(slots, key=slots.get))                                   # earliest pick first
        rec = {tid: [9, 9, 0] for tid in slots}
        rec[7], rec[8] = [1, 8, 0], [0, 9, 0]
        rec[20] = [17, 1, 0]
        late = T.priority_order(lg, year, R.WAIVER_DRAFT_ORDER_WEEKS + 1, rec)
        self.assertEqual(late[:2], [8, 7])                                                      # the worst record claims first
        self.assertEqual(late[-1], 20)
        tie = {tid: [9, 9, 0] for tid in slots}
        order = T.priority_order(lg, year, 5, tie)
        self.assertEqual(order, sorted(slots, key=slots.get))                                   # equal records: last draft order breaks it

    def test_priority_without_an_earlier_draft_ranks_weakest_first(self):
        lg = self.lg                                                                            # the ledger holds only draft 1
        order = T.priority_order(lg, 1, 1, {})
        self.assertEqual(sorted(order), sorted(t.id for t in lg.teams))
        strengths = [lg.by_id[i].strength for i in order]
        self.assertEqual(strengths, sorted(strengths))

    def test_exiled_club_keeps_its_ambassador_record(self):
        lg = self.lg
        lg.movement.begin_year(lg, 2, self.pick_of)
        rec = {t.id: [9, 9, 0] for t in lg.teams}
        ex = [t.id for t in lg.teams][:2]
        rec[ex[0]], rec[ex[1]] = [0, 7, 0], [6, 1, 0]                                           # the round robin is over; nothing changes them in weeks 8 to 19
        order = T.priority_order(lg, 3, 12, rec)
        self.assertEqual(order[0], ex[0])
        self.assertEqual(order[-1], ex[1])

    # 3 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_who_is_subject_to_waivers(self):
        p = next(iter(self.lg.teams[0].roster))
        for accrued, week, expect in ((0, 3, True), (3, 12, True), (4, 3, False), (6, R.TRADE_DEADLINE_WEEK, False),
                                      (4, R.TRADE_DEADLINE_WEEK + 1, True), (9, 15, True)):
            p.accrued_seasons = accrued
            self.assertEqual(T.subject_to_waivers(p, week), expect, (accrued, week))

    # 4 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_claimed_player_keeps_her_contract_and_the_releaser_owes_nothing(self):
        lg = self.lg
        a, b = 1, 2
        make_short(lg, lg.by_id[b], "WR")
        p = star(lg, a, "WR")
        before_a = EC.payroll(lg.by_id[a])
        before_b = EC.payroll(lg.by_id[b])
        terms = (p.salary, p.years_left, p.bonus, p.bonus_years, p.guaranteed)
        wire = T.new_wire(lg, 1, 5, {})
        wire.order = [3, b, a]                                                                  # club 3 is first but has no need: skipped
        T.waive(lg, lg.by_id[a], p, wire)
        self.assertNotIn(p, lg.by_id[a].roster)
        self.assertIsNone(p.team_id)
        T.resolve(lg, wire)
        self.assertIn(p, lg.by_id[b].roster)
        self.assertEqual(p.team_id, b)
        self.assertEqual(terms, (p.salary, p.years_left, p.bonus, p.bonus_years, p.guaranteed))
        self.assertEqual(lg.by_id[a].dead_now, 0.0)
        self.assertAlmostEqual(EC.payroll(lg.by_id[a]), before_a - terms[0], 3)
        self.assertGreater(EC.payroll(lg.by_id[b]), before_b)
        self.assertNotIn(p, lg.free_agents)
        self.assertEqual((wire.claimed, wire.cleared, wire.held), (1, 0, []))
        ev = [e for e in lg.movement.events if e["kind"] == "waiver_claim"]
        self.assertEqual((ev[-1]["from_club"], ev[-1]["to_club"], ev[-1]["player"]), (a, b, p.id))

    def test_unclaimed_player_becomes_a_free_agent_and_the_releaser_pays_dead_money(self):
        lg = self.lg
        a = 1
        p = star(lg, a, "WR", salary=4.0, years=3, ovr=20.0)                                    # nobody wants her
        owed = EC.dead_charge(p)
        self.assertGreater(owed, 0)
        wire = T.new_wire(lg, 1, 5, {})
        T.waive(lg, lg.by_id[a], p, wire)
        T.resolve(lg, wire)
        self.assertIn(p, lg.free_agents)
        self.assertEqual((p.salary, p.years_left), (0.0, 0))
        self.assertAlmostEqual(lg.by_id[a].dead_now, owed, 4)
        self.assertEqual((wire.claimed, wire.cleared), (0, 1))

    def test_first_club_in_priority_that_wants_her_gets_her(self):
        lg = self.lg
        for i in (2, 3, 4):
            make_short(lg, lg.by_id[i], "WR")
        p = star(lg, 1, "WR")
        wire = T.new_wire(lg, 1, 5, {})
        wire.order = [4, 2, 3, 1]
        T.waive(lg, lg.by_id[1], p, wire)
        T.resolve(lg, wire)
        self.assertEqual(p.team_id, 4)

    def test_no_claim_without_a_place_the_cap_or_a_need(self):
        lg = self.lg
        for label in ("full roster", "cap", "better alternative"):
            lg2, _, _ = scenario(seed=11, year=1)
            p2 = star(lg2, 1, "WR", salary=2.0, ovr=60.0 if label == "better alternative" else 99.0)
            t2 = lg2.by_id[2]
            if label == "cap":
                make_short(lg2, t2, "WR")
                t2.bank = 0.0
                t2.roster[0].salary += 100.0
            elif label == "better alternative":
                make_short(lg2, t2, "WR")
                for q in lg2.free_agents:
                    if q.pos == "WR":
                        q.ovr = 95.0
            wire = T.new_wire(lg2, 1, 5, {})
            wire.order = [2, 1]
            T.waive(lg2, lg2.by_id[1], p2, wire)
            T.resolve(lg2, wire)
            self.assertEqual((wire.claimed, wire.cleared), (0, 1), label)

    def test_releasing_club_cannot_claim_its_own_player(self):
        lg = self.lg
        make_short(lg, lg.by_id[1], "WR")
        p = star(lg, 1, "WR")
        wire = T.new_wire(lg, 1, 5, {})
        wire.order = [1]
        T.waive(lg, lg.by_id[1], p, wire)
        T.resolve(lg, wire)
        self.assertEqual(wire.claimed, 0)

    # 5 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_manage_week_routes_waivable_releases_and_keeps_everyone_somewhere(self):
        lg = self.lg
        t = lg.by_id[1]
        # a returner from injured reserve pushes the roster to 54 and the weakest surplus player goes
        back = t.practice_squad.pop()
        back.team_id = t.id
        t.ir.append(back)
        back.ir_designated, back.ir_games, back.weeks_out = True, R.IR_MIN_GAMES, 0
        EC.sign(back, 1.0, 1)
        n_before = len(everyone(lg))
        for week, subject in ((5, True),):
            for q in t.roster:
                q.accrued_seasons = 0
            wire = T.new_wire(lg, 1, week, {})
            log = rosters.manage_week(lg, self.rng, 10, wire)
            self.assertEqual(log["waived"], 1)
            self.assertEqual(wire.held, [])
            self.assertEqual(len(t.roster), ROSTER_SIZE)
        self.assertEqual(len(everyone(lg)), n_before)

    def test_vested_veteran_is_released_at_once_before_the_deadline(self):
        lg = self.lg
        t = lg.by_id[1]
        back = t.practice_squad.pop()
        back.team_id = t.id
        t.ir.append(back)
        back.ir_designated, back.ir_games, back.weeks_out = True, R.IR_MIN_GAMES, 0
        EC.sign(back, 1.0, 1)
        for q in list(t.roster):
            q.accrued_seasons = 6
        back.accrued_seasons = 6
        wire = T.new_wire(lg, 1, 5, {})
        log = rosters.manage_week(lg, self.rng, 10, wire)
        self.assertEqual(log["waived"], 0)
        self.assertEqual(len(t.roster), ROSTER_SIZE)

    def test_whole_seasons_with_waivers_keep_every_player_on_one_list(self):
        rng = random.Random(21)
        from league import new_league
        lg = new_league(rng, rosters=True)
        for y in range(1, 4):
            res = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False))
            self.assertTrue(res.runner.record)
            self.assertTrue(any(l.get("waived", 0) for l in res.runner.ir_log))
            seen = {}
            for t in lg.teams:
                self.assertLessEqual(len(t.roster), ROSTER_SIZE + 0)
                for p in rosters.squad(t):
                    self.assertNotIn(p.id, seen)
                    seen[p.id] = t.id
                    self.assertEqual(p.team_id, t.id)
            for p in lg.free_agents:
                self.assertNotIn(p.id, seen)
                self.assertIsNone(p.team_id)
            for t in lg.teams:
                self.assertGreaterEqual(t.dead_now, 0.0)


class Tags(unittest.TestCase):
    def setUp(self):
        self.lg, self.rng, self.pick_of = scenario(seed=13, year=1)
        self.mv = self.lg.movement

    def vet(self, club, pos=None, nth=0, accrued=6):
        return expiring(self.lg, club, accrued, pos=pos, nth=nth)

    # 1 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_prices_come_from_the_position_table_and_the_players_last_cap_number(self):
        lg, mv = self.lg, self.mv
        p = self.vet(1, "OL")
        table = mv.tag_table(lg)
        sal = sorted((q.salary for t in lg.teams for q in t.roster if q.pos == "OL" and q.years_left > 0), reverse=True)
        self.assertEqual(table["OL"], sal)
        top7, top15 = sum(sal[:7]) / 7, sum(sal[:15]) / 15
        p.salary = 0.5                                                   # her last cap number is small: the table decides
        self.assertAlmostEqual(mv.tag_price(p, "franchise", 1, 1, table), round(top7, 2), 2)
        self.assertAlmostEqual(mv.tag_price(p, "exclusive", 1, 1, table), round(top7, 2), 2)
        self.assertAlmostEqual(mv.tag_price(p, "transition", 1, 1, table), round(top15, 2), 2)
        self.assertLess(top15, top7)
        p.salary = 25.0                                                  # a large last cap number: 120% of it is above the maximum, which caps it
        self.assertEqual(mv.tag_price(p, "franchise", 1, 1, table), EC.MAX_SALARY)
        p.salary = round(top7 / 1.2 + 1.0, 2)                            # 120% of her last cap number is just above the table
        self.assertGreater(1.2 * p.salary, top7)
        self.assertAlmostEqual(mv.tag_price(p, "franchise", 1, 1, table), round(max(top7, 1.2 * p.salary), 2), 2)
        with self.assertRaises(MovementError):
            mv.tag_price(p, "bogus", 1, 1, table)

    def test_consecutive_franchise_tags_escalate_and_the_fourth_is_refused(self):
        lg, mv = self.lg, self.mv
        p = self.vet(1, "WR")
        table = {"WR": [4.0] * 20, "QB": [9.0] * 20}
        p.salary = 1.0
        base = mv.tag_price(p, "franchise", 3, 1, table)
        self.assertEqual(base, 4.0)
        mv.rights[(2, p.id)] = MV.Right(2, p.id, 1, "franchise", "franchise", 5.0, 1, "kept")
        self.assertEqual(mv.tag_streak(3, 1, p.id), 1)
        self.assertEqual(mv.tag_price(p, "franchise", 3, 1, table), 6.0)                       # 120% of last year's 5.0
        self.assertEqual(mv.tag_price(p, "transition", 3, 1, table), 4.0)                      # the transition tag does not escalate
        mv.rights[(1, p.id)] = MV.Right(1, p.id, 1, "franchise_x", "exclusive", 4.0, None, "kept")
        self.assertEqual(mv.tag_streak(3, 1, p.id), 2)
        self.assertEqual(mv.tag_price(p, "franchise", 3, 1, table), round(max(1.44 * 5.0, 9.0, 1.2 * 4.0), 2))   # the QB number is the floor of the third
        mv.rights[(0, p.id)] = MV.Right(0, p.id, 1, "franchise", "franchise", 4.0, 1, "kept")
        with self.assertRaises(MovementError):
            mv.tag_price(p, "franchise", 3, 1, table)
        mv.rights[(2, p.id)].club = 9                                                          # another club's tag does not count toward the streak
        self.assertEqual(mv.tag_streak(3, 1, p.id), 0)

    def test_a_fourth_tag_in_a_row_is_refused_even_after_the_ledger_rolls_over(self):
        lg, mv = self.lg, self.mv
        p = self.vet(1, "WR")
        for y in (10, 11, 12):
            mv.rights[(y, p.id)] = MV.Right(y, p.id, 1, "franchise", "franchise", 5.0, 1, "kept")
        mv.begin_year(lg, 13, self.pick_of)
        self.assertEqual(mv.tag_streak(13, 1, p.id), 3)
        with self.assertRaises(MovementError):
            mv.tag_price(p, "franchise", 13, 1, {"WR": [4.0] * 20})

    def test_trade_accepts_list_shaped_pick_keys(self):
        lg = self.lg
        T.check_trade(lg, 1, 2, [], [], [[1, 1, 1], [1, 1, 1]], [], 1)

    def test_rights_for_a_streak_are_kept_two_years_back(self):
        lg, mv = self.lg, self.mv
        mv.rights[(1, 77)] = MV.Right(1, 77, 1, "franchise", "franchise", 5.0, 1, "kept")
        mv.rights[(1, 78)] = MV.Right(1, 78, 1, "restricted", "first", 2.7, 1, "kept")
        mv.begin_year(lg, 3, self.pick_of)
        self.assertIn((1, 77), mv.rights)                               # a franchise tag two years old stays: a third tag needs it
        self.assertNotIn((1, 78), mv.rights)
        mv.begin_year(lg, 4, self.pick_of)
        self.assertIn((1, 77), mv.rights)                               # kept long enough to count a fourth tag against the streak
        mv.begin_year(lg, 5, self.pick_of)
        self.assertNotIn((1, 77), mv.rights)

    # 2 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_tag_is_a_one_year_guaranteed_contract_and_the_club_has_one_a_year(self):
        lg, mv = self.lg, self.mv
        p, q = self.vet(1, "DL"), self.vet(1, "CB")
        r = mv.tag(lg, p, "franchise", 1)
        self.assertEqual((p.years_left, p.bonus), (1, 0.0))
        self.assertAlmostEqual(p.guaranteed, p.salary, 3)
        self.assertEqual((r.kind, r.status, r.comp_round, r.price), ("franchise", "tendered", 1, p.salary))
        self.assertIs(mv.tag_of(1, 1), r)
        with self.assertRaises(MovementError):
            mv.tag(lg, q, "transition", 1)                              # one tag a club a year
        with self.assertRaises(MovementError):
            mv.tag(lg, p, "franchise", 1)
        x = mv.tag(lg, self.vet(2, "QB"), "exclusive", 1)
        self.assertEqual((x.kind, x.status, x.comp_round), ("franchise_x", "kept", None))
        tr = mv.tag(lg, self.vet(3, "TE"), "transition", 1)
        self.assertEqual((tr.kind, tr.status, tr.comp_round), ("transition", "tendered", None))

    def test_only_unrestricted_expiring_players_on_the_53_can_be_tagged(self):
        lg, mv = self.lg, self.mv
        for accrued in (0, 3):
            with self.assertRaises(MovementError):
                mv.tag(lg, self.vet(4, "RB", accrued=accrued), "franchise", 1)
        live = lg.by_id[5].roster[0]
        live.years_left = 2
        with self.assertRaises(MovementError):
            mv.tag(lg, live, "franchise", 1)
        ps = lg.by_id[6].practice_squad[0]
        ps.years_left, ps.accrued_seasons = 0, 6
        with self.assertRaises(MovementError):
            mv.tag(lg, ps, "franchise", 1)
        self.assertEqual([k for k in mv.rights], [])                    # nothing was created by the refusals

    def test_an_exiled_club_may_tag(self):
        lg, mv = self.lg, self.mv
        lg.by_id[7].status = "exiled"
        r = mv.tag(lg, self.vet(7, "LB"), "franchise", 1)
        self.assertEqual(r.club, 7)

    # 3 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_exclusive_tag_takes_no_offer(self):
        lg, mv = self.lg, self.mv
        p = self.vet(1, "WR")
        mv.tag(lg, p, "exclusive", 1)
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 2, p.id, 20.0, 3, 1)

    def test_franchise_offer_carries_two_firsts_held_together_and_released_by_a_match(self):
        lg, mv = self.lg, self.mv
        p = self.vet(1, "WR")
        r = mv.tag(lg, p, "franchise", 1)
        before = [(k, pk.owner) for k, pk in mv.picks.items()]
        salary = round(r.price + 0.5, 2)
        o = mv.make_offer(lg, 2, p.id, salary, 4, 1)
        self.assertEqual(len(o.keys), 2)
        self.assertEqual([k[1] for k in o.keys], [1, 1])
        self.assertEqual(sorted(k[0] for k in o.keys), [1, 2])             # this draft's first and next draft's first
        self.assertTrue(all(mv.picks[k].reserved_by == o.id and mv.picks[k].owner == 2 for k in o.keys))
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 3, p.id, salary + 1, 4, 1)                   # one offer at a time
        mv.advance(lg, 3)
        mv.match(lg, o.id)
        self.assertTrue(all(mv.picks[k].reserved_by is None and mv.picks[k].owner == 2 for k in o.keys))
        self.assertEqual(before, [(k, pk.owner) for k, pk in mv.picks.items()])
        self.assertEqual((p.team_id, p.salary), (1, salary))

    def test_franchise_offer_not_matched_sends_player_and_both_firsts_together(self):
        lg, mv = self.lg, self.mv
        p = self.vet(1, "WR")
        r = mv.tag(lg, p, "franchise", 1)
        o = mv.make_offer(lg, 2, p.id, round(r.price + 0.5, 2), 4, 1)
        mv.advance(lg, R.RFA_MATCH_DAYS + 1)
        self.assertEqual(o.status, "transferred")
        self.assertEqual(p.team_id, 2)
        self.assertTrue(all(mv.picks[k].owner == 1 and mv.picks[k].reserved_by is None for k in o.keys))
        self.assertEqual(sum(1 for pk in mv.owned(1, 1) if pk.rnd == 1), 2)

    def test_franchise_offer_needs_two_firsts_and_nothing_is_reserved_otherwise(self):
        lg, mv = self.lg, self.mv
        for y in range(1, 5):                                              # club 2 owns none of its firsts
            mv.transfer_pick(lg, (y, 1, 2), 30)
        p = self.vet(1, "WR")
        r = mv.tag(lg, p, "franchise", 1)
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 2, p.id, round(r.price + 1, 2), 3, 1)
        self.assertTrue(all(pk.reserved_by is None for pk in mv.picks.values()))
        self.assertEqual(mv.reserved_cap(2), 0.0)
        mv.transfer_pick(lg, (2, 1, 31), 2)                                # one first is not two; two are enough
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 2, p.id, round(r.price + 1, 2), 3, 1)
        mv.transfer_pick(lg, (3, 1, 32), 2)
        o = mv.make_offer(lg, 2, p.id, round(r.price + 1, 2), 3, 1)
        self.assertEqual(sorted(o.keys), [(2, 1, 31), (3, 1, 32)])

    def test_transition_offer_has_no_compensation_and_a_five_day_match(self):
        lg, mv = self.lg, self.mv
        p = self.vet(1, "TE")
        r = mv.tag(lg, p, "transition", 1)
        o = mv.make_offer(lg, 2, p.id, round(r.price + 0.3, 2), 3, 1)
        self.assertEqual(o.keys, [])
        self.assertEqual(o.deadline, o.day + R.RFA_MATCH_DAYS)
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 3, p.id, round(r.price + 0.3, 2), 3, 1)
        mv.advance(lg, R.RFA_MATCH_DAYS)
        mv.match(lg, o.id)                                                 # still in time on the last day
        self.assertEqual(p.team_id, 1)

    def test_franchise_offer_survives_save_and_load(self):
        lg, mv = self.lg, self.mv
        p = self.vet(1, "WR")
        r = mv.tag(lg, p, "franchise", 1)
        o = mv.make_offer(lg, 2, p.id, round(r.price + 0.5, 2), 4, 1)
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "dfl.db")
            store.save(db, lg, self.rng, 1)
            con = sqlite3.connect(db)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM movement_offer_extra").fetchone()[0], 1)
            con.close()
            back, _, _ = store.load(db)
        self.assertEqual(MV.dump(mv), MV.dump(back.movement))
        self.assertEqual(back.movement.offers[o.id].keys, o.keys)
        back.movement.advance(back, R.RFA_MATCH_DAYS + 1)
        mv.advance(lg, R.RFA_MATCH_DAYS + 1)
        self.assertEqual(MV.dump(mv), MV.dump(back.movement))

    # 4 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_autopilot_tags_a_sensible_number_each_year(self):
        rng = random.Random(33)
        from league import new_league
        lg = new_league(rng, rosters=True)
        counts = []
        for y in range(1, 5):
            res = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False))
            counts.append(res.offseason.get("tagged", 0))
            mv = lg.movement
            mine = [r for r in mv.rights.values() if r.year == y and r.kind in MV.FRANCHISE_KINDS + ("transition",)]
            self.assertEqual(len(mine), counts[-1])
            self.assertEqual(len({r.club for r in mine}), len(mine))                       # at most one a club
            by_id = {p.id: p for t in lg.teams for p in rosters.squad(t)}
            for r in mine:
                p = by_id.get(r.player_id)
                if p is not None and r.status in ("kept", "matched"):
                    self.assertGreaterEqual(p.ovr, 60.0)
                self.assertLessEqual(r.price, EC.MAX_SALARY)
        self.assertTrue(all(3 <= c <= 30 for c in counts), counts)


class Trades(unittest.TestCase):
    def setUp(self):
        self.lg, self.rng, self.pick_of = scenario(seed=17, year=1)
        self.mv = self.lg.movement
        for t in self.lg.teams:
            t.dead_now = t.dead_next = 0.0

    def veteran(self, club, pos, salary=4.0, years=4, share=0.25, nth=0):
        p = [q for q in self.lg.by_id[club].roster if q.pos == pos][nth]
        EC.sign(p, salary, years, share=share, guarantee_years=2)
        return p

    # 1 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_receiver_takes_base_and_guarantees_sender_takes_the_whole_bonus_before_the_draft(self):
        lg = self.lg
        p = self.veteran(1, "WR", salary=5.0, years=4)
        q = self.veteran(2, "WR", salary=3.0, years=3, share=0.0)
        bonus_left, base, guar = p.bonus * p.bonus_years, p.salary - p.bonus, p.guaranteed
        self.assertGreater(bonus_left, 0)
        out = T.trade(lg, 1, 2, [p.id], [q.id], [], [], year=1)
        self.assertEqual((p.team_id, q.team_id), (2, 1))
        self.assertIn(p, lg.by_id[2].roster)
        self.assertIn(q, lg.by_id[1].roster)
        self.assertEqual((p.salary, p.bonus, p.bonus_years, p.guaranteed, p.years_left), (round(base, 4), 0.0, 0, guar, 4))
        self.assertAlmostEqual(lg.by_id[1].dead_now, bonus_left, 3)                  # before the draft: all of it, now
        self.assertEqual(lg.by_id[1].dead_next, 0.0)
        self.assertEqual(lg.by_id[2].dead_now, 0.0)                                  # q carried no bonus
        ev = [e for e in self.mv.events if e["kind"] == "trade"]
        self.assertEqual((len(ev), ev[0]["clubs"], ev[0]["players"]), (1, [1, 2], [[p.id], [q.id]]))
        self.assertEqual(out["players"], ([p.id], [q.id]))

    def test_after_the_draft_the_sender_takes_this_seasons_share_and_the_rest_next_season(self):
        lg, mv = self.lg, self.mv
        pk = mv.picks[(1, 7, 48)]
        pk.selected = 123456                                                         # the draft of this league year has been held
        self.assertTrue(T.drafted(lg, 1))
        p = self.veteran(1, "OL", salary=6.0, years=5)
        total = p.bonus * p.bonus_years
        this_year = p.bonus
        T.trade(lg, 1, 2, [p.id], [], [], [], year=1)
        self.assertAlmostEqual(lg.by_id[1].dead_now, this_year, 3)
        self.assertAlmostEqual(lg.by_id[1].dead_next, total - this_year, 3)

    def test_in_season_trade_deadline_roster_limit_and_acceleration(self):
        lg = self.lg
        p = self.veteran(1, "CB", salary=5.0, years=3)
        q = self.veteran(2, "CB", salary=2.0, years=3, share=0.0)
        with self.assertRaises(T.TradeError) as cm:
            T.trade(lg, 1, 2, [p.id], [q.id], [], [], year=1, week=R.TRADE_DEADLINE_WEEK + 1)
        self.assertIn("deadline", str(cm.exception))
        before = state(lg)
        with self.assertRaises(T.TradeError):                                          # 54 players on one side
            T.trade(lg, 1, 2, [p.id], [], [], [], year=1, week=4)
        self.assertEqual(before, state(lg))
        T.trade(lg, 1, 2, [p.id], [q.id], [], [], year=1, week=R.TRADE_DEADLINE_WEEK)   # the last week is open
        self.assertAlmostEqual(lg.by_id[1].dead_now, 5.0 * 0.25, 3)                   # this season's share now
        self.assertAlmostEqual(lg.by_id[1].dead_next, 5.0 * 0.25 * 2, 3)              # the rest next season

    # 2 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_picks_move_through_the_one_door_and_keep_their_original_club_and_slot(self):
        lg, mv = self.lg, self.mv
        slot = mv.picks[(1, 1, 3)].slot
        T.trade(lg, 3, 4, [], [], [(1, 1, 3), (4, 2, 3)], [(2, 3, 4)], year=1)             # a pick for the coming draft and one four drafts ahead
        self.assertEqual((mv.picks[(1, 1, 3)].owner, mv.picks[(1, 1, 3)].original, mv.picks[(1, 1, 3)].slot), (4, 3, slot))
        self.assertEqual(mv.picks[(4, 2, 3)].owner, 4)
        self.assertEqual(mv.picks[(2, 3, 4)].owner, 3)
        self.assertEqual(sum(1 for e in mv.events if e["kind"] == "pick_transfer"), 3)

    def test_illegal_picks_are_refused_and_nothing_changes(self):
        lg, mv = self.lg, self.mv
        mv.picks[(1, 2, 5)].selected = 99
        mv.picks[(1, 3, 6)].reserved_by = 5
        p = self.veteran(1, "TE")
        before = state(lg)
        for picks_a, picks_b in (([(1, 2, 5)], []), ([(1, 3, 6)], []), ([(1, 1, 9)], []), ([(9, 1, 1)], []), ([], [(1, 1, 1)]),
                                 ([(1, 1, 3), (1, 1, 3)], []), ([(1, 4, 3)], [(1, 4, 3)])):
            with self.assertRaises(T.TradeError, msg=(picks_a, picks_b)):
                T.trade(lg, 3, 4, [], [], picks_a, picks_b, year=1)
        with self.assertRaises(T.TradeError):                                           # a legal player with an illegal pick: neither moves
            T.trade(lg, 1, 4, [p.id], [], [(1, 1, 9)], [], year=1)
        with self.assertRaises(T.TradeError):
            T.trade(lg, 3, 3, [], [], [(1, 1, 3)], [], year=1)
        with self.assertRaises(T.TradeError):
            T.trade(lg, 3, 4, [], [], [], [], year=1)
        self.assertEqual(before, state(lg))

    # 3 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_both_clubs_must_be_under_the_cap_afterwards(self):
        lg = self.lg
        big = self.veteran(1, "QB", salary=24.0, years=4)
        t2 = lg.by_id[2]
        t2.bank = 0.0
        t2.dead_now = max(0.0, EC.limit(t2) - EC.offseason_over(t2) + 10.0 - 1.0)         # club 2 has less than the player's base to spare
        self.assertLess(EC.limit(t2) - EC.offseason_over(t2), 24.0 * 0.75)
        before = state(lg)
        with self.assertRaises(T.TradeError) as cm:
            T.trade(lg, 1, 2, [big.id], [], [], [], year=1)
        self.assertIn("club 2 would be over the cap", str(cm.exception))
        self.assertEqual(before, state(lg))

    def test_the_senders_acceleration_can_put_it_over_the_cap(self):
        lg = self.lg
        p = self.veteran(1, "QB", salary=24.0, years=5, share=0.5)                      # 12.0 a year of bonus, 60 of it still to spread
        t1 = lg.by_id[1]
        t1.bank = 0.0
        t1.dead_now = 0.0
        # make the club exactly at its limit before the trade: acceleration adds more than the salary it sheds
        gap = EC.limit(t1) - EC.offseason_over(t1)
        t1.dead_now = round(max(0.0, gap - 1.0), 4)
        before = state(lg)
        why = T.check_trade(lg, 1, 2, [p.id], [], [], [], 1)
        self.assertTrue(any("club 1 would be over the cap" in w for w in why), why)
        with self.assertRaises(T.TradeError):
            T.trade(lg, 1, 2, [p.id], [], [], [], year=1)
        self.assertEqual(before, state(lg))

    # 4 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_players_on_a_tender_or_with_an_offer_or_without_a_contract_cannot_be_traded(self):
        lg, mv = self.lg, self.mv
        rfa = expiring(lg, 1, 3, draft_pick=5, pos="WR")
        r = mv.tender(lg, rfa, "first", 1)
        self.assertEqual(r.status, "tendered")
        gone = expiring(lg, 1, 1, pos="OL")
        ok = self.veteran(1, "DL")
        for pid in (rfa.id, gone.id):
            with self.assertRaises(T.TradeError):
                T.trade(lg, 1, 2, [pid], [], [], [], year=1)
        o = mv.make_offer(lg, 2, rfa.id, round(r.price + 1.0, 2), 3, 1)
        why = T.check_trade(lg, 1, 2, [rfa.id], [], [], [], 1)
        self.assertTrue(any("offer pending" in w for w in why), why)
        mv.advance(lg, R.RFA_MATCH_DAYS + 1)                                           # she is now with club 2 and signed: tradable again
        self.assertEqual(rfa.team_id, 2)
        T.trade(lg, 2, 3, [rfa.id], [], [], [], year=1)
        self.assertEqual(rfa.team_id, 3)
        T.trade(lg, 1, 2, [ok.id], [], [], [], year=1)

    def test_a_tag_that_is_signed_and_closed_can_be_traded_but_an_open_one_cannot(self):
        lg, mv = self.lg, self.mv
        p = expiring(lg, 1, 6, pos="LB")
        mv.tag(lg, p, "exclusive", 1)                                                      # signed, no offers possible
        T.trade(lg, 1, 2, [p.id], [], [], [], year=1)
        self.assertEqual(p.team_id, 2)
        q = expiring(lg, 3, 6, pos="LB")
        mv.tag(lg, q, "franchise", 1)                                                      # still takes offers
        with self.assertRaises(T.TradeError):
            T.trade(lg, 3, 2, [q.id], [], [], [], year=1)
        mv.close_window(1)
        T.trade(lg, 3, 2, [q.id], [], [], [], year=1)

    # 5 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_trades_survive_save_and_load(self):
        lg, mv = self.lg, self.mv
        p = self.veteran(1, "WR")
        T.trade(lg, 1, 2, [p.id], [], [(3, 1, 1)], [(2, 2, 2)], year=1)
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "dfl.db")
            store.save(db, lg, self.rng, 1)
            back, _, _ = store.load(db)
        self.assertEqual(MV.dump(mv), MV.dump(back.movement))
        self.assertEqual(back.movement.picks[(3, 1, 1)].owner, 2)
        self.assertEqual(everyone(back)[p.id].team_id, 2)
        self.assertEqual(back.by_id[1].dead_now, lg.by_id[1].dead_now)
        self.assertEqual([e["kind"] for e in back.movement.events if e["kind"] == "trade"], ["trade"])


class Compensatory(unittest.TestCase):
    def setUp(self):
        self.lg, self.rng, self.pick_of = scenario(seed=19, year=1)
        self.mv = self.lg.movement

    def test_value_is_pay_weighted_by_how_much_she_played(self):
        self.assertEqual(T.comp_value(8.0, R.REGULAR_SEASON_WEEKS - 1), 8.0)
        self.assertEqual(T.comp_value(8.0, 0), 4.0)
        self.assertEqual(T.comp_value(8.0, 99), 8.0)
        self.assertLess(T.comp_value(8.0, 6), T.comp_value(8.0, 12))

    def test_cancellation_is_best_against_best_and_leftovers_are_the_lowest(self):
        lost = [(1, 10, 9.0), (1, 11, 5.0), (1, 12, 2.0), (2, 13, 4.0), (3, 14, 6.0), (4, 15, 3.0)]
        signed = [(1, 20, 8.0), (2, 21, 7.0), (3, 22, 1.0), (4, 23, 1.0), (4, 24, 0.5)]
        got = {(club, pid): (v, kind) for v, club, pid, kind in T.comp_candidates(lost, signed)}
        # club 1 lost three and signed one: the best loss is cancelled, the other two are net losses
        self.assertEqual(sorted(k for k in got if k[0] == 1), [(1, 11), (1, 12)])
        self.assertNotIn((2, 13), got)                                      # signed more than it lost
        self.assertNotIn((3, 14), got)                                      # club 3 lost one and signed one: equal
        self.assertNotIn((4, 15), got)                                      # signed two for one
        # club 3 lost 1 and signed 1: the gap (5.0) earns a gap candidate with no player
        self.assertEqual(got[(3, None)], (5.0, "gap"))

    def test_equal_loss_gap_is_small_enough_to_earn_nothing(self):
        got = T.comp_candidates([(1, 10, 3.0)], [(1, 20, 3.0 - T.COMP_GAP_MIN / 2)])
        self.assertEqual(got, [])

    def test_a_club_gets_at_most_four_net_losses_considered(self):
        lost = [(1, 100 + i, 5.0 - i * 0.1) for i in range(7)]
        got = T.comp_candidates(lost, [])
        self.assertEqual(len(got), R.COMP_PICKS_PER_TEAM_MAX)
        self.assertEqual([c[2] for c in got], [100, 101, 102, 103])

    def test_award_puts_picks_at_the_end_of_rounds_three_to_seven_with_rounds_by_value(self):
        lg, mv = self.lg, self.mv
        lost = [(1, 1000, 6.0), (2, 1001, 2.0), (3, 1002, 1.2), (4, 1003, 0.8), (5, 1004, 0.5), (6, 1005, 0.1)]
        awards = T.award_compensatory(lg, 1, lost, [])
        self.assertEqual([(a["club"], a["round"]) for a in awards], [(1, 3), (2, 4), (3, 5), (4, 6), (5, 7)])    # 0.1 is worth nothing
        for a in awards:
            pk = mv.picks[(2, a["round"], MV.COMP_BASE)]
            self.assertEqual((pk.owner, pk.slot, pk.selected, pk.reserved_by), (a["club"], a["round"] * R.DRAFT_PICKS_PER_ROUND, None, None))
        self.assertEqual([p.original for p in mv.comp_picks(2, 3)], [MV.COMP_BASE])
        with self.assertRaises(MV.MovementError):
            T.award_compensatory(lg, 1, lost, [])                              # one award a year
        mv.begin_year(lg, 2, self.pick_of)                                       # beginning that year keeps the slot (the end of the round)
        self.assertEqual(mv.picks[(2, 3, MV.COMP_BASE)].slot, 3 * R.DRAFT_PICKS_PER_ROUND)

    def test_full_rounds_push_picks_down_and_the_totals_are_capped(self):
        lg, mv = self.lg, self.mv
        lost = [(i % 48, 2000 + i, 9.0 - i * 0.01) for i in range(120)]            # 120 high-value losses over 48 clubs (at most 4 each by cancellation rules)
        awards = T.award_compensatory(lg, 1, lost, [])
        self.assertLessEqual(len(awards), R.COMP_PICKS_MAX)
        by_round = {}
        for a in awards:
            by_round[a["round"]] = by_round.get(a["round"], 0) + 1
        for i, size in enumerate(T.COMP_ROUND_SIZES):
            self.assertLessEqual(by_round.get(3 + i, 0), size)
        self.assertEqual(by_round[3], T.COMP_ROUND_SIZES[0])                        # the best fill round 3, the rest are pushed down
        per_club = {}
        for a in awards:
            per_club[a["club"]] = per_club.get(a["club"], 0) + 1
        self.assertLessEqual(max(per_club.values()), R.COMP_PICKS_PER_TEAM_MAX)

    def test_a_compensatory_pick_can_be_traded_and_carries_its_slot(self):
        lg, mv = self.lg, self.mv
        T.award_compensatory(lg, 1, [(1, 1000, 6.0)], [])
        key = (2, 3, MV.COMP_BASE)
        T.trade(lg, 1, 2, [], [], [key], [], year=1)
        self.assertEqual(mv.picks[key].owner, 2)
        self.assertEqual(mv.picks[key].original, MV.COMP_BASE)

    def test_the_autopilot_awards_ufa_losses_only_and_the_draft_uses_the_picks(self):
        rng = random.Random(33)
        from league import new_league
        lg = new_league(rng, rosters=True)
        total = 0
        for y in range(1, 5):
            res = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False))
            mv = lg.movement
            awards = [e for e in mv.events if e["kind"] == "comp_award" and e["year"] == y + 1]
            self.assertLessEqual(len(awards), R.COMP_PICKS_MAX)
            per_club = {}
            for e in awards:
                per_club[e["club"]] = per_club.get(e["club"], 0) + 1
                self.assertTrue(3 <= e["round"] <= 7)
            self.assertTrue(all(c <= R.COMP_PICKS_PER_TEAM_MAX for c in per_club.values()))
            self.assertEqual(res.offseason["comp_picks"], len(awards))
            if y > 1:                                                               # last year's awards were drafted this year
                last = [e for e in mv.events if e["kind"] == "comp_award" and e["year"] == y]
                self.assertEqual(res.offseason.get("comp_rookies", 0), len(last))
                used = [pk for pk in mv.picks.values() if pk.year == y and pk.original >= MV.COMP_BASE]
                self.assertEqual(len(used), len(last))
                self.assertTrue(all(pk.selected is not None for pk in used))
            total += len(awards)
        self.assertGreater(total, 0)
        people = {p.id: p for t in lg.teams for p in rosters.squad(t)}
        people.update({p.id: p for p in lg.free_agents})
        people.update({p.id: p for p in lg.retired_players})
        for e in lg.movement.events:
            if e["kind"] == "comp_award" and e["basis"] == "net" and e["player"] in people:
                self.assertGreaterEqual(people[e["player"]].accrued_seasons, R.UFA_SEASONS)       # only unrestricted players count


class Scripted:
    """A driver that plays the moves it is given, by decision kind; anything else is the autopilot's."""
    name = "scripted"

    def __init__(self, moves):
        self.moves = dict(moves)

    def choose(self, dp):
        return self.moves.get(dp.kind, dp.default), "scripted"


class ContractTables(unittest.TestCase):
    def setUp(self):
        self.lg, self.rng, _ = scenario(seed=23, year=1)
        self.lg.choice_log = []
        self.team = self.lg.by_id[1]
        self.p = next(q for q in self.team.roster if q.pos == "WR")
        self.p.ovr = 75.0
        self.market = EC.market_salary(self.p.pos, self.p.ovr, self.p.credited_seasons)

    def table(self, fits=None, years=3, market=None):
        return CT.ContractTable(self.lg, 1, self.team, self.p, self.market if market is None else market, years, fits or (lambda x: True))

    def play(self, tb, moves=None):
        self.lg.driver = Scripted(moves or {})
        TB.run_tables(self.lg, [tb])
        return tb

    # 1 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_autopilot_settles_at_the_market_price_for_the_standard_length_in_two_turns(self):
        tb = self.play(self.table(years=3))
        self.assertEqual(tb.outcome, ("deal", (100, 3)))
        self.assertEqual(tb.deal, (self.market, 3))
        self.assertTrue(tb.plain())
        self.assertEqual([e["kind"] for e in self.lg.choice_log], ["contract_offer", "contract_reply"])
        self.assertTrue(all(e["status"] == "ok" for e in self.lg.choice_log))

    def test_counter_paths(self):
        for moves, outcome in (
            ({"contract_offer": "offer_90_3", "contract_reply": "counter_100", "contract_counter": "accept"}, ("deal", (100, 3))),
            ({"contract_offer": "offer_90_4", "contract_reply": "counter_110", "contract_counter": "hold", "contract_final": "accept"}, ("deal", (90, 4))),
            ({"contract_offer": "offer_90_2", "contract_reply": "counter_100", "contract_counter": "hold", "contract_final": "walk"}, ("walk", "player")),
            ({"contract_offer": "offer_90_3", "contract_reply": "counter_100", "contract_counter": "walk"}, ("walk", "club")),
            ({"contract_offer": "offer_100_3", "contract_reply": "walk"}, ("walk", "player")),
            ({"contract_offer": "offer_110_2"}, ("deal", (110, 2))),
        ):
            self.lg.choice_log = []
            tb = self.play(self.table(), moves)
            self.assertEqual(tb.outcome, outcome, moves)
            self.assertEqual(tb.plain(), outcome == ("deal", (100, 3)) and len(tb.steps) == 2)
            if tb.outcome[0] == "deal":
                pct = tb.outcome[1][0]
                self.assertEqual(tb.deal[0], round(min(EC.MAX_SALARY, max(EC.min_salary(self.p.credited_seasons), self.market * pct / 100)), 2))
            else:
                self.assertIsNone(tb.deal)

    # 2 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_the_rep_removes_unaffordable_prices_from_both_sides(self):
        cap = self.market * 1.0 + 0.001                                       # the club can pay 100% but not 110%
        tb = self.table(fits=lambda x: x <= cap)
        dp = tb.next_point()
        self.assertEqual(sorted({o["tags"]["pct"] for o in dp.options}), [90, 100])
        self.assertIn("110%", " ".join(tb.held_back))
        self.assertIn("off the table", dp.context["rep_note"])
        tb.apply("offer_90_3")
        reply = tb.next_point()
        self.assertEqual([o["id"] for o in reply.options], ["accept", "counter_100", "walk"])
        self.assertEqual(reply.default, "counter_100")                         # she asks for her market price, the most the rep allows

    def test_length_stays_between_one_and_five_years(self):
        for std, expect in ((1, [1, 2]), (5, [4, 5]), (3, [2, 3, 4])):
            tb = self.table(years=std)
            self.assertEqual(tb.lengths(), expect)
            self.assertEqual(sorted({o["tags"]["years"] for o in tb.next_point().options}), expect)

    def test_prices_are_clamped_to_the_minimum_and_the_maximum_contract(self):
        top = self.table(market=EC.MAX_SALARY)
        self.assertEqual(top.salary(110), EC.MAX_SALARY)
        low = self.table(market=0.01)
        self.assertEqual(low.salary(90), EC.min_salary(self.p.credited_seasons))

    def test_nothing_affordable_leaves_an_empty_offer_list_not_an_illegal_one(self):
        tb = self.table(fits=lambda x: False)
        self.assertEqual(tb.pays(), [])

    # 3 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_no_driver_can_take_a_deal_the_rules_or_the_cap_forbid(self):
        cap = self.market * 1.0 + 0.001
        for seed in range(60):
            self.lg.choice_log = []
            tb = self.table(fits=lambda x: x <= cap, years=3 + seed % 3)
            self.lg.driver = D.RandomLegalDriver(seed)
            TB.run_tables(self.lg, [tb])
            self.assertTrue(tb.done)
            self.assertLessEqual(tb.turns, 4)
            if tb.deal:
                salary, years = tb.deal
                self.assertLessEqual(salary, cap)
                self.assertTrue(EC.min_salary(self.p.credited_seasons) <= salary <= EC.MAX_SALARY)
                self.assertTrue(1 <= years <= EC.CONTRACT_YEARS_MAX)

    def test_a_table_can_be_replayed_from_the_choice_log(self):
        self.lg.driver = D.RandomLegalDriver(5)
        a = self.table()
        TB.run_tables(self.lg, [a])
        log = list(self.lg.choice_log)
        self.lg.choice_log = []
        self.lg.driver = D.ReplayDriver(log)
        b = self.table()
        TB.run_tables(self.lg, [b])
        self.assertEqual(a.outcome, b.outcome)
        self.assertEqual([e["chosen"] for e in log], [e["chosen"] for e in self.lg.choice_log])

    def test_a_broken_driver_falls_back_to_the_autopilot(self):
        class Broken:
            name = "broken"

            def choose(self, dp):
                return "not an option"
        self.lg.driver = Broken()
        tb = self.table()
        TB.run_tables(self.lg, [tb])
        self.assertTrue(tb.plain())
        self.assertTrue(all(e["status"] == "invalid_choice" for e in self.lg.choice_log))

    # 4 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_value_rule_rises_with_gain_falls_with_price_and_favours_a_good_negotiator(self):
        self.assertTrue(CT.club_wants(30.0, 5.0))
        self.assertFalse(CT.club_wants(-30.0, 0.4))
        self.assertTrue(CT.club_wants(0.0, 0.4))
        gain = CT.KEEP_G0 + CT.KEEP_G1 * 10.0 + 0.5
        self.assertTrue(CT.club_wants(gain, 10.0))
        self.assertFalse(CT.club_wants(gain, 14.0))                         # the same player at a higher price
        self.assertFalse(CT.club_wants(gain - 1.0, 10.0, gm_factor=1.0))
        self.assertTrue(CT.club_wants(gain - 1.0, 10.0, gm_factor=0.95))    # a good negotiator keeps her

    def test_gain_measures_what_she_adds_over_the_rest_of_the_position(self):
        t = self.team
        wrs = sorted((q for q in t.roster if q.pos == "WR"), key=lambda q: -q.ovr)
        best = wrs[0]
        best.ovr = 95.0
        self.assertGreater(CT.club_gain(t.roster, best), CT.club_gain(t.roster, wrs[-1]))
        self.assertGreater(CT.club_gain(t.roster, best), 5.0)

    # 5 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_the_offseason_makes_important_deals_at_tables_and_with_the_flag_off_it_does_not(self):
        from league import new_league
        from roster_model import RosterModel
        counts = {}
        for flag in (True, False):
            rng = random.Random(41)
            lg = new_league(rng, rosters=True)
            seen = 0
            for y in range(1, 4):
                res = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False, roster_model=RosterModel(contract_tables=flag)))
                seen += res.offseason.get("tables", 0)
            counts[flag] = seen
            offers = sum(1 for e in lg.choice_log if e["kind"] == "contract_offer")
            self.assertEqual(offers, seen)
            if flag:
                replies = sum(1 for e in lg.choice_log if e["kind"] == "contract_reply")
                self.assertEqual(replies, seen)                              # the autopilot settles every table in two turns
        self.assertGreater(counts[True], 20)
        self.assertEqual(counts[False], 0)

    # 6 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_the_cutdown_has_waiver_claims_and_every_claim_leaves_a_legal_roster(self):
        from league import new_league
        rng = random.Random(41)
        lg = new_league(rng, rosters=True)
        total = 0
        for y in range(1, 4):
            res = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False))
            total += res.offseason.get("claims", 0)
            self.assertLessEqual(res.offseason.get("claims", 0), 3 * R.TOTAL_TEAMS)
            self.assertEqual(res.offseason["waived"], len([e for e in lg.movement.events if e.get("kind") == "waiver_claim" and e.get("week") is None and e.get("year") == y])
                             + res.offseason["waived"] - res.offseason.get("claims", 0))
            ids = [p.id for t in lg.teams for p in t.roster + t.practice_squad]
            self.assertEqual(len(ids), len(set(ids)))                                     # no player is on two clubs
            self.assertFalse({p.id for p in lg.free_agents} & set(ids))                  # and none is on a club and the market at once
            for t in lg.teams:
                self.assertEqual(len(t.roster), ROSTER_SIZE)
                self.assertTrue(all(p.team_id == t.id for p in t.roster))
                self.assertLessEqual(EC.payroll(t), EC.limit(t) + 1e-6)                   # the cap holds after claims
        self.assertGreater(total, 10)
        claims = [e for e in lg.movement.events if e.get("kind") == "waiver_claim" and e.get("week") is None]
        self.assertEqual(len(claims), total)
        self.assertTrue(all(e["from_club"] != e["to_club"] for e in claims))


if __name__ == "__main__":
    unittest.main(verbosity=1)
