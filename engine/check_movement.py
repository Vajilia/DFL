"""Step 6c/6d: pick ownership, tenders, funded offers, the five-day match, compensation, and saving all of it.

    python engine/check_movement.py
"""
import copy
import os
import random
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import economy as EC  # noqa: E402
import movement as MV  # noqa: E402
import rules as R  # noqa: E402
import store  # noqa: E402
from league import new_league  # noqa: E402
from movement import MovementError  # noqa: E402
from roster_model import RosterModel  # noqa: E402
from season import Options, run_season  # noqa: E402


def scenario(seed=7, year=1):
    """A founding league in the offseason after `year`: the ledger is open, the order is team id order, every club has room for offers."""
    rng = random.Random(seed)
    lg = new_league(rng, rosters=True)
    pick_of = {t.id: i + 1 for i, t in enumerate(lg.teams)}
    lg.movement.begin_year(lg, year, pick_of)
    for t in lg.teams:
        t.bank = 25.0
    return lg, rng, pick_of


def expiring(lg, club, accrued, draft_pick=None, pos=None, nth=0):
    """A player on `club`'s roster whose contract has just run out, with the given service."""
    t = lg.by_id[club]
    cands = sorted((p for p in t.roster if pos is None or p.pos == pos), key=lambda p: (-p.ovr, p.id))
    p = cands[nth]
    p.years_left, p.accrued_seasons, p.draft_pick = 0, accrued, draft_pick
    return p


def everyone(lg):
    out = {}
    for t in lg.teams:
        for p in list(t.roster) + list(t.practice_squad) + list(t.ir):
            out[p.id] = p
    for p in list(lg.free_agents) + list(lg.retired_players):
        out[p.id] = p
    return out


def state(lg):
    """Everything an offer can touch, as text: the ledger, every roster, every contract and every club's cap numbers."""
    teams = [(t.id, [p.id for p in t.roster], round(sum(p.salary for p in t.roster), 4), t.dead_now) for t in lg.teams]
    players = [(p.id, p.team_id, p.salary, p.years_left, p.bonus, p.guaranteed) for p in sorted((p for t in lg.teams for p in t.roster), key=lambda p: p.id)]
    return MV.dump(lg.movement) + repr((teams, players))


class Movement(unittest.TestCase):
    # 1 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_ledger_separates_original_owner_slot_reservation_and_selection(self):
        lg, rng, pick_of = scenario()
        mv = lg.movement
        self.assertEqual(len(mv.picks), (MV.HORIZON + 1) * R.DRAFT_ROUNDS * R.TOTAL_TEAMS)
        self.assertTrue(all(p.owner == p.original for p in mv.picks.values()))
        pk = mv.picks[(1, 2, 5)]
        self.assertEqual(pk.slot, R.DRAFT_PICKS_PER_ROUND + pick_of[5])
        self.assertTrue(all(p.slot is None for p in mv.picks.values() if p.year > 1))      # only the coming draft has an order
        mv.transfer_pick(lg, (1, 2, 5), 9)
        self.assertEqual((pk.original, pk.owner, pk.slot), (5, 9, R.DRAFT_PICKS_PER_ROUND + pick_of[5]))
        self.assertEqual(sorted(p.rnd for p in mv.owned(1, 9)), [1, 2, 2, 3, 4, 5, 6, 7])
        self.assertIn(R.DRAFT_PICKS_PER_ROUND + pick_of[5], mv.slots_owned(1, 9))
        for bad in ((1, 2, 5), (3, 3, 3)):                          # already his / not his to give to himself
            with self.assertRaises(MovementError):
                mv.transfer_pick(lg, bad, 9 if bad[2] == 5 else bad[2])
        with self.assertRaises(MovementError):
            mv.transfer_pick(lg, (1, 1, 1), 999)
        with self.assertRaises(MovementError):
            mv.transfer_pick(lg, (9, 1, 1), 2)
        pk.reserved_by = 77
        with self.assertRaises(MovementError):
            mv.transfer_pick(lg, (1, 2, 5), 3)
        with self.assertRaises(MovementError):
            mv.select((1, 2, 5), 1)
        pk.reserved_by, pk.selected = None, 12345
        with self.assertRaises(MovementError):
            mv.transfer_pick(lg, (1, 2, 5), 3)
        # the ledger moves forward a year: the finished draft is kept one year, then dropped
        mv.begin_year(lg, 2, pick_of)
        self.assertIn((1, 1, 1), mv.picks)
        mv.begin_year(lg, 3, pick_of)
        self.assertNotIn((1, 1, 1), mv.picks)
        self.assertIn((6, 7, 48), mv.picks)

    # 2 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_the_draft_follows_current_ownership_and_keeps_slot_and_price(self):
        lg, rng, pick_of = scenario(seed=11)
        mv = lg.movement
        a, b = 3, 40
        mv.ensure_picks(lg, 1)
        mv.transfer_pick(lg, (1, 1, a), b)                           # b holds a's first-round pick as well as its own
        mv.transfer_pick(lg, (1, 5, a), b)
        from offseason import run_roster_offseason
        from roster_model import RosterModel
        log = run_roster_offseason(lg, rng, RosterModel(), 1, pick_of, returners=[t.id for t in lg.exiled()])
        self.assertEqual(log["rookies"], R.DRAFT_ROUNDS * R.TOTAL_TEAMS)
        people = everyone(lg)
        first = people[mv.picks[(1, 1, a)].selected]
        own = people[mv.picks[(1, 1, b)].selected]
        self.assertEqual(first.draft_pick, pick_of[a])               # the slot is a's
        self.assertEqual(own.draft_pick, pick_of[b])
        self.assertEqual(first.team_id, b)                           # the player went to the owner (round-1 contracts are guaranteed, so she stays)
        self.assertEqual(first.draft_year, 1)
        self.assertAlmostEqual(first.salary, EC.rookie_salary(pick_of[a]))        # the price is the slot's
        self.assertTrue(all(pk.selected is not None for pk in mv.picks.values() if pk.year == 1))
        drafted = [people[pk.selected] for pk in mv.picks.values() if pk.year == 1]
        self.assertEqual(sorted(p.draft_pick for p in drafted), list(range(1, 337)))
        moved = sum(1 for o in mv.offers.values() if o.year == 1 and o.status == "transferred" and o.pick)
        self.assertEqual(log.get("traded_picks_used"), 2 + moved)        # the two moved here, and the compensation picks the market moved

    # 3 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_who_can_be_tendered_and_the_price(self):
        lg, rng, _ = scenario()
        mv = lg.movement
        # exclusive rights below three accrued seasons: only the exclusive tender, the minimum rung or 110% of her base
        p = expiring(lg, 1, accrued=2)
        with self.assertRaises(MovementError):
            mv.tender(lg, p, "first", 1)
        base = p.salary - p.bonus
        r = mv.tender(lg, p, "exclusive", 1)
        self.assertEqual((r.kind, r.status, r.comp_round), ("exclusive", "kept", None))
        self.assertAlmostEqual(r.price, max(EC.min_salary(p.credited_seasons), round(1.1 * base, 2)), places=2)
        self.assertEqual((p.salary, p.years_left, p.bonus, p.guaranteed), (r.price, 1, 0.0, 0.0))
        with self.assertRaises(MovementError):
            mv.tender(lg, p, "exclusive", 1)                          # once a year
        # restricted at exactly three: four levels, rounds of compensation
        for level, comp, floor in (("first", 1, EC.RFA_TENDERS[0]), ("second", 2, EC.RFA_TENDERS[1]), ("refusal", None, EC.RFA_TENDERS[3])):
            q = expiring(lg, 2, accrued=3, nth=("first", "second", "refusal").index(level))
            q.salary, q.bonus = 0.5, 0.0
            r = mv.tender(lg, q, level, 1)
            self.assertEqual((r.kind, r.status, r.comp_round), ("restricted", "tendered", comp))
            self.assertAlmostEqual(r.price, floor)
        # the 110% rule lifts every level, and nothing goes above the maximum contract
        q = expiring(lg, 3, accrued=3)
        q.salary, q.bonus = 4.0, 0.0
        self.assertAlmostEqual(mv.tender(lg, q, "second", 1).price, 4.4)
        q = expiring(lg, 3, accrued=3, nth=1)
        q.salary, q.bonus = 40.0, 0.0
        self.assertAlmostEqual(mv.tender(lg, q, "refusal", 1).price, EC.MAX_SALARY)
        # original round needs a drafted player; her round is the compensation
        q = expiring(lg, 4, accrued=3, draft_pick=None)
        with self.assertRaises(MovementError):
            mv.tender(lg, q, "original", 1)
        q = expiring(lg, 4, accrued=3, draft_pick=2 * R.DRAFT_PICKS_PER_ROUND + 5, nth=1)
        self.assertEqual(mv.tender(lg, q, "original", 1).comp_round, 3)
        # four accrued seasons: unrestricted, no rights, unless her club is exiled
        q = expiring(lg, 5, accrued=4)
        with self.assertRaises(MovementError):
            mv.tender(lg, q, "refusal", 1)
        self.assertEqual(mv.tender(lg, q, "refusal", 1, exiled=True).kind, "restricted")
        # a player who is not on a squad, or whose contract has not run out, is not tendered
        with self.assertRaises(MovementError):
            mv.tender(lg, lg.by_id[6].roster[0], "exclusive", 1)
        z = lg.free_agents[0] if lg.free_agents else lg.by_id[6].practice_squad[0]
        z.team_id = None
        with self.assertRaises(MovementError):
            mv.tender(lg, z, "exclusive", 1)

    # 4 ---------------------------------------------------------------------------------------------------------------------------------------
    def rfa(self, lg, level="second", club=1, nth=0, draft_pick=None):
        p = expiring(lg, club, accrued=3, draft_pick=draft_pick, nth=nth)
        p.salary, p.bonus = 0.5, 0.0
        lg.movement.tender(lg, p, level, 1)
        return p

    def test_an_offer_must_be_funded_binding_and_carry_compensation(self):
        lg, rng, _ = scenario()
        mv = lg.movement
        p = self.rfa(lg, "second")
        price = mv.rights[(1, p.id)].price
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 1, p.id, 3.0, 3, 1)                      # its own player
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 2, p.id, price - 0.01, 3, 1)             # below the tender
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 2, p.id, EC.MAX_SALARY + 1, 3, 1)
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 2, p.id, 3.0, 9, 1)                       # a nine-year contract
        for gy in (-1, 4):
            with self.assertRaises(MovementError):
                mv.make_offer(lg, 2, p.id, 3.0, 3, 1, guarantee_years=gy)
        lg.by_id[2].bank = 0.0
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 2, p.id, 20.0, 3, 1)                      # not funded
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 2, 12345, 3.0, 3, 1)                      # no such rights
        self.assertEqual((mv.reserved_cap(2), len(mv.offers)), (0.0, 0))
        # no pick, no offer: a second-round tender needs a pick in round 2 or earlier
        for pk in mv.owned(1, 3):
            if pk.rnd <= 2:
                mv.transfer_pick(lg, pk.key, 4)
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 3, p.id, 3.0, 3, 1)
        # a right of first refusal carries no compensation, so a club with no early picks may still offer
        q = self.rfa(lg, "refusal", club=1, nth=1)
        o = mv.make_offer(lg, 3, q.id, 2.0, 2, 1)
        self.assertIsNone(o.pick)
        # a good offer holds the cap room and the pick; a second offer for the same player is refused
        o = mv.make_offer(lg, 5, p.id, 3.0, 3, 1)
        pk = mv.picks[o.pick]
        self.assertEqual((pk.rnd, pk.owner, pk.reserved_by), (2, 5, o.id))
        self.assertAlmostEqual(mv.reserved_cap(5), 3.0)
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 6, p.id, 4.0, 3, 1)
        # the held pick cannot be traded or used while the offer is open
        with self.assertRaises(MovementError):
            mv.transfer_pick(lg, pk.key, 7)
        with self.assertRaises(MovementError):
            mv.check_ready_for_draft(1)
        # an exclusive-rights player draws no offers
        e = expiring(lg, 8, accrued=1)
        mv.tender(lg, e, "exclusive", 1)
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 9, e.id, 3.0, 3, 1)

    # 5 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_own_or_better_compensation(self):
        lg, rng, _ = scenario()
        mv = lg.movement
        p = self.rfa(lg, "second")
        # club 2 keeps only a round-1 and a round-3 pick: the round-1 pick (better) answers a second-round tender
        for pk in mv.owned(1, 2):
            if pk.rnd not in (1, 3):
                mv.transfer_pick(lg, pk.key, 40)
        o = mv.make_offer(lg, 2, p.id, 2.5, 2, 1)
        self.assertEqual(o.pick[1], 1)
        # the exact round is preferred when the club has it
        q = self.rfa(lg, "second", club=1, nth=1)
        o2 = mv.make_offer(lg, 40, q.id, 2.5, 2, 1)
        self.assertEqual(o2.pick[1], 2)
        # only a worse pick than the tender asks for: refused
        r = self.rfa(lg, "first", club=1, nth=2)
        for pk in mv.owned(1, 41):
            if pk.rnd == 1:
                mv.transfer_pick(lg, pk.key, 42)
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 41, r.id, 3.5, 2, 1)

    # 6 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_matching_inside_five_days_releases_the_holds(self):
        lg, rng, _ = scenario()
        mv = lg.movement
        p = self.rfa(lg, "first")
        o = mv.make_offer(lg, 2, p.id, 4.0, 3, 1, share=0.2, guarantee_years=2)
        self.assertEqual(o.deadline, o.day + R.RFA_MATCH_DAYS)
        mv.advance(lg, R.RFA_MATCH_DAYS)                                # day 5: the last day to match
        self.assertEqual(o.status, "pending")
        mv.match(lg, o.id)
        self.assertEqual(o.status, "matched")
        self.assertEqual((p.team_id, p.salary, p.years_left), (1, 4.0, 3))                 # every represented term, with her old club
        self.assertAlmostEqual(p.bonus, 0.8)
        self.assertAlmostEqual(p.guaranteed, (4.0 - 0.8) * 2)
        self.assertEqual((mv.reserved_cap(2), mv.picks[o.pick].reserved_by, mv.picks[o.pick].owner), (0.0, None, 2))
        self.assertEqual(mv.rights[(1, p.id)].status, "matched")
        with self.assertRaises(MovementError):
            mv.match(lg, o.id)                                          # nothing left to match
        mv.advance(lg, 10)
        self.assertEqual((p.team_id, mv.picks[o.pick].owner), (1, 2))
        mv.close_window(1)
        self.assertEqual(mv.rights[(1, p.id)].status, "matched")

    # 7 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_no_match_moves_the_player_and_the_pick_together(self):
        lg, rng, _ = scenario()
        mv = lg.movement
        p = self.rfa(lg, "first")
        o = mv.make_offer(lg, 2, p.id, 4.0, 3, 1)
        pay1, pay2 = EC.payroll(lg.by_id[1]), EC.payroll(lg.by_id[2])
        mv.advance(lg, R.RFA_MATCH_DAYS)
        self.assertEqual((o.status, p.team_id), ("pending", 1))
        mv.advance(lg, 1)                                              # day 6: the period is over
        self.assertEqual(o.status, "transferred")
        self.assertEqual((p.team_id, p.salary, p.years_left), (2, 4.0, 3))
        self.assertIn(p, lg.by_id[2].roster)
        self.assertNotIn(p, lg.by_id[1].roster)
        pk = mv.picks[o.pick]
        self.assertEqual((pk.original, pk.owner, pk.reserved_by), (2, 1, None))                # the compensation went to her old club
        self.assertEqual(mv.rights[(1, p.id)].status, "transferred")
        self.assertAlmostEqual(EC.payroll(lg.by_id[2]), pay2 + 4.0)
        self.assertAlmostEqual(EC.payroll(lg.by_id[1]), pay1 - EC.tender_price("first", 0.5))
        self.assertEqual(mv.reserved_cap(2), 0.0)
        kinds = [e["kind"] for e in mv.events]
        self.assertEqual(kinds[-2:], ["offer", "transfer"])

    # 8 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_boundaries_in_money_and_days(self):
        lg, rng, _ = scenario()
        mv = lg.movement
        p = self.rfa(lg, "refusal")
        price = mv.rights[(1, p.id)].price
        t = lg.by_id[2]
        t.bank -= mv.room(lg, 2) - 6.0                                                      # exactly $6.00M of room
        self.assertAlmostEqual(mv.room(lg, 2), 6.0)
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 2, p.id, 6.02, 2, 1)                                          # two cents over the room
        o = mv.make_offer(lg, 2, p.id, 6.0, 2, 1)                                           # exactly the room is funded
        self.assertAlmostEqual(o.salary, 6.0)
        self.assertAlmostEqual(mv.room(lg, 2), 0.0)
        r2 = self.rfa(lg, "refusal", club=1, nth=1)
        with self.assertRaises(MovementError):
            mv.make_offer(lg, 2, r2.id, price, 2, 1)                                        # the held money cannot be spent twice
        o_eq = mv.make_offer(lg, 3, r2.id, mv.rights[(1, r2.id)].price, 2, 1)               # an offer equal to the tender is allowed
        self.assertAlmostEqual(o_eq.salary, mv.rights[(1, r2.id)].price)
        # a match needs the room for the difference, exactly
        lg2, _, _ = scenario()
        mv2 = lg2.movement
        q = self.rfa(lg2, "refusal")
        o2 = mv2.make_offer(lg2, 2, q.id, 6.0, 2, 1)
        t1 = lg2.by_id[1]
        spare = EC.limit(t1) - EC.offseason_over(t1) - mv2.reserved_cap(1)
        t1.bank = t1.bank - (spare - (6.0 - q.salary) + 0.05)                     # leave 5 cents too little
        before = state(lg2)
        with self.assertRaises(MovementError):
            mv2.match(lg2, o2.id)
        self.assertEqual(before, state(lg2))
        t1.bank += 0.10
        mv2.match(lg2, o2.id)
        self.assertEqual(o2.status, "matched")
        # the day after the last day is too late to match: the offer was committed by the passing day
        lg3, _, _ = scenario()
        r = self.rfa(lg3, "refusal")
        o3 = lg3.movement.make_offer(lg3, 2, r.id, 3.0, 2, 1)
        lg3.movement.day = o3.deadline + 1
        with self.assertRaises(MovementError):
            lg3.movement.match(lg3, o3.id)
        lg3.movement.advance(lg3, 0)
        self.assertEqual(o3.status, "transferred")
        with self.assertRaises(MovementError):
            lg3.movement.advance(lg3, -1)

    # 9 ---------------------------------------------------------------------------------------------------------------------------------------
    def test_a_failed_commit_or_match_changes_nothing(self):
        lg, rng, _ = scenario()
        mv = lg.movement
        p = self.rfa(lg, "first")
        o = mv.make_offer(lg, 2, p.id, 4.0, 3, 1)
        before = state(lg)
        pk = mv.picks[o.pick]
        pk.reserved_by = None                                           # the hold is lost
        with self.assertRaises(MovementError):
            mv.commit(lg, o.id)
        pk.reserved_by = o.id
        self.assertEqual(before, state(lg))
        off = lg.by_id[2]
        off.bank = 0.0
        off.roster[0].salary += 30.0                                    # the offering club's payroll balloons: the offer is no longer funded
        before = state(lg)
        with self.assertRaises(MovementError):
            mv.commit(lg, o.id)
        self.assertEqual(before, state(lg))                              # nothing moved: not the player, the pick, the money or the ledger
        mv.advance(lg, 10)                                               # the passing day tries the same commit; it cannot complete, so the offer lapses
        self.assertEqual(o.status, "void")
        self.assertEqual((mv.reserved_cap(2), mv.picks[o.pick].reserved_by, mv.picks[o.pick].owner), (0.0, None, 2))      # both holds released
        self.assertEqual(mv.events[-1]["kind"], "void")
        self.assertEqual(mv.rights[(1, p.id)].status, "tendered")        # she stays on her tender
        mv.close_window(1)
        self.assertEqual(mv.rights[(1, p.id)].status, "kept")
        self.assertEqual(p.team_id, 1)
        self.assertEqual(mv.picks[o.pick].owner, 2)
        self.assertIn(p, lg.by_id[1].roster)

    # 10 --------------------------------------------------------------------------------------------------------------------------------------
    def test_save_and_resume_with_pending_offer_and_future_pick(self):
        def build():
            lg, rng, _ = scenario(seed=5)
            mv = lg.movement
            mv.transfer_pick(lg, (3, 1, 7), 20)                         # a pick two drafts ahead has a new owner
            mv.transfer_pick(lg, (1, 4, 9), 21)
            p = self.rfa(lg, "first", club=1)
            mv.make_offer(lg, 2, p.id, 4.5, 3, 1)
            mv.advance(lg, 2)
            return lg, rng, p
        a, rng_a, pa = build()
        b, rng_b, pb = build()
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "dfl.db")
            store.save(db, b, rng_b, 1)
            con = sqlite3.connect(db)
            self.assertEqual(con.execute("SELECT value FROM meta WHERE key='format'").fetchone()[0], "3")
            self.assertEqual(con.execute("SELECT COUNT(*) FROM movement_offers WHERE status='pending'").fetchone()[0], 1)
            self.assertEqual(con.execute("SELECT owner FROM movement_picks WHERE year=3 AND rnd=1 AND original=7").fetchone()[0], 20)
            con.close()
            b2, _, year = store.load(db)
        self.assertEqual(MV.dump(a.movement), MV.dump(b2.movement))
        self.assertEqual(b2.movement.picks[(3, 1, 7)].owner, 20)
        self.assertEqual(sum(1 for o in b2.movement.offers.values() if o.status == "pending"), 1)
        # play the rest of the window on both: they stay the same
        a.movement.advance(a, 6)
        b2.movement.advance(b2, 6)
        self.assertEqual(MV.dump(a.movement), MV.dump(b2.movement))
        self.assertEqual(store._dump(store._body(pa)), store._dump(store._body(everyone(b2)[pa.id])))
        self.assertEqual([p.id for p in a.by_id[2].roster], [p.id for p in b2.by_id[2].roster])
        self.assertEqual(everyone(b2)[pa.id].team_id, 2)

    # 11 --------------------------------------------------------------------------------------------------------------------------------------
    def test_a_version_2_save_opens_and_is_upgraded_and_other_versions_are_refused(self):
        lg, rng, _ = scenario(seed=6)
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "dfl.db")
            store.save(db, lg, rng, 1)
            con = sqlite3.connect(db)                                    # make it a version-2 file: no movement tables
            for tbl in ("movement_state", "movement_picks", "movement_rights", "movement_offers", "movement_events"):
                con.execute(f"DROP TABLE {tbl}")
            con.execute("UPDATE meta SET value='2' WHERE key='format'")
            con.commit()
            con.close()
            old, orng, year = store.load(db)
            self.assertEqual((year, len(old.movement.picks), len(old.movement.offers)), (1, 0, 0))      # every pick is at its original club
            old.movement.ensure_picks(old, 1)
            self.assertTrue(all(p.owner == p.original for p in old.movement.picks.values()))
            old.movement.transfer_pick(old, (1, 1, 1), 2)
            store.save(db, old, orng, 1)                                  # the first save upgrades it
            con = sqlite3.connect(db)
            self.assertEqual(con.execute("SELECT value FROM meta WHERE key='format'").fetchone()[0], "3")
            self.assertEqual(con.execute("SELECT owner FROM movement_picks WHERE year=1 AND rnd=1 AND original=1").fetchone()[0], 2)
            con.execute("UPDATE meta SET value='4' WHERE key='format'")
            con.commit()
            con.close()
            with self.assertRaises(ValueError):
                store.load(db)
            with self.assertRaises(ValueError):
                store.save(db, old, orng, 1)
            # a snapshot written before the ledger existed gets an empty one
            con = sqlite3.connect(db)
            con.execute("UPDATE meta SET value='3' WHERE key='format'")
            con.commit()
            con.close()
            import pickle
            legacy = copy.copy(old)
            del legacy.__dict__["movement"]
            legacy.driver = None
            con = sqlite3.connect(db)
            con.execute("INSERT OR REPLACE INTO snapshots VALUES(?,?,?,?)", (9, "x", "legacy", pickle.dumps({"league": legacy, "rng_state": orng.getstate(), "year": 9})))
            con.commit()
            con.close()
            snap, _, y = store.load(db, year=9)
            self.assertEqual((y, len(snap.movement.picks)), (9, 0))

    # 12 --------------------------------------------------------------------------------------------------------------------------------------
    def test_whole_seasons_leave_a_clean_ledger(self):
        rng = random.Random(21)
        lg = new_league(rng, rosters=True)
        picks_to_use = None
        transfers = 0
        for y in range(1, 5):
            if y == 2:                                                   # a pick of the coming draft and one a draft ahead change owners mid-career
                lg.movement.ensure_picks(lg, y)
                lg.movement.transfer_pick(lg, (2, 1, 10), 11)
                lg.movement.transfer_pick(lg, (3, 2, 10), 11)
                picks_to_use = (2, 1, 10)
            res = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False, roster_model=RosterModel(rfa_offer_prob=1.0)))
            mv = lg.movement
            if y == 2:
                used = mv.picks[picks_to_use]
                self.assertEqual((used.owner, used.original), (11, 10))
                taken = everyone(lg)[used.selected]
                self.assertEqual((taken.draft_year, taken.draft_pick), (2, used.slot))
            self.assertFalse([o for o in mv.offers.values() if o.status == "pending"])
            self.assertEqual(mv.reserved_cap(1), 0.0)
            self.assertFalse([pk for pk in mv.picks.values() if pk.reserved_by is not None])
            self.assertFalse([r for r in mv.rights.values() if r.status == "tendered"])
            self.assertTrue(all(pk.selected is not None for pk in mv.picks.values() if pk.year == y))
            people = everyone(lg)
            for pk in mv.picks.values():
                if pk.year == y:
                    self.assertEqual(people[pk.selected].draft_pick, pk.slot)
                    self.assertEqual(people[pk.selected].draft_year, y)
            transfers += sum(1 for o in mv.offers.values() if o.status == "transferred" and o.year == y)
            for t in lg.teams:
                self.assertEqual(len(t.roster), 53)
                self.assertEqual(len(t.practice_squad), 16)
                self.assertLessEqual(EC.payroll(t), EC.limit(t) + 1e-6)
            # every offer that moved a player moved the compensation with her
            for o in mv.offers.values():
                if o.status == "transferred" and o.pick and o.year == y:
                    self.assertEqual(mv.picks[o.pick].owner, o.original)
        self.assertGreater(transfers, 0)                                 # with every eligible offer made, players did change clubs
        pk = lg.movement.picks[(3, 2, 10)]                               # the pick a draft ahead was used in year 3 by its new owner
        self.assertEqual((pk.owner, pk.original), (11, 10))
        self.assertEqual(everyone(lg)[pk.selected].draft_year, 3)
        self.assertGreater(len(lg.movement.rights), 0)
        # and it all survives a save
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "dfl.db")
            store.save(db, lg, rng, 4)
            back, _, _ = store.load(db)
            self.assertEqual(MV.dump(lg.movement), MV.dump(back.movement))

    # 13 --------------------------------------------------------------------------------------------------------------------------------------
    def test_a_lapsed_offer_does_not_block_the_others_and_a_half_upgraded_file_loads(self):
        lg, rng, _ = scenario()
        mv = lg.movement
        p1 = self.rfa(lg, "refusal", club=1, nth=0)
        p2 = self.rfa(lg, "refusal", club=3, nth=0)
        o1 = mv.make_offer(lg, 2, p1.id, 2.0, 2, 1)
        o2 = mv.make_offer(lg, 4, p2.id, 2.0, 2, 1)
        lg.by_id[1].roster.remove(p1)                                    # something outside the offer flow takes her away
        mv.advance(lg, 6)
        self.assertEqual((o1.status, o2.status), ("void", "transferred"))
        self.assertEqual((mv.reserved_cap(2), mv.reserved_cap(4)), (0.0, 0.0))
        self.assertEqual(p2.team_id, 4)
        with self.assertRaises(MovementError):
            mv.void(o1.id)                                               # already over
        mv.void(mv.make_offer(lg, 5, self.rfa(lg, "refusal", club=6).id, 2.0, 2, 1).id, "changed mind")
        self.assertEqual(mv.reserved_cap(5), 0.0)
        mv.close_window(1)
        # a version-2 file whose upgrade failed half way (empty movement tables, format still 2) still loads
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "dfl.db")
            store.save(db, lg, rng, 1)
            con = sqlite3.connect(db)
            for tbl in ("movement_state", "movement_picks", "movement_rights", "movement_offers", "movement_events"):
                con.execute(f"DELETE FROM {tbl}")
            con.execute("UPDATE meta SET value='2' WHERE key='format'")
            con.commit()
            con.close()
            back, _, _ = store.load(db)
            self.assertEqual(len(back.movement.picks), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
