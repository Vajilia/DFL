"""Earned service: boundary cases, roster movement, game integration and save/resume."""
import random
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import service
import store
from league import new_league
from players import make_player
from schedule import Game
from roster_model import RosterModel
from season import Options, run_season


class ServiceChecks(unittest.TestCase):
    def setUp(self):
        self.p = make_player(random.Random(1), 1, "WR", 60, 22, 1)
        self.ps = make_player(random.Random(2), 2, "WR", 50, 22, 1)
        self.ir = make_player(random.Random(3), 3, "WR", 60, 22, 1)
        self.ir.weeks_out = 8
        self.t = SimpleNamespace(roster=[self.p], ir=[self.ir], practice_squad=[self.ps])
        self.other = SimpleNamespace(roster=[], ir=[], practice_squad=[])
        self.lg = SimpleNamespace(teams=[self.t, self.other], by_id={1: self.t, 2: self.other},
                                  has_rosters=True, free_agents=[], retired_players=[])

    def games(self, weeks, kind="division", year=1):
        for w in weeks:
            service.record_game(self.lg, Game(w, 1, 2, kind), year)

    def test_boundaries_and_paid_inactive_or_ir(self):
        self.games(range(1, 6))
        service.settle_season(self.lg, 1)
        self.assertEqual((self.p.accrued_seasons, self.p.credited_seasons), (0, 1))
        self.assertEqual((self.ir.accrued_seasons, self.ir.credited_seasons), (0, 0))
        self.assertEqual((self.ps.accrued_seasons, self.ps.credited_seasons), (0, 0))
        self.games(range(1, 7), year=2)
        service.settle_season(self.lg, 2)
        self.assertEqual((self.p.accrued_seasons, self.p.credited_seasons), (1, 2))
        service.settle_season(self.lg, 2)
        self.assertEqual(self.p.accrued_seasons, 1)
        self.assertEqual((self.ir.accrued_seasons, self.ir.credited_seasons), (1, 0))
        with self.assertRaises(ValueError):
            self.games([7], year=2)

    def test_salary_credit_tracks_roster_ir_moves_and_legacy_partial_year(self):
        self.games([1, 2])
        self.t.roster.remove(self.p)
        self.t.ir.append(self.p)
        self.games([3, 4, 5, 6])
        service.settle_season(self.lg, 1)
        self.assertEqual((self.p.accrued_seasons, self.p.credited_seasons), (1, 0))
        self.assertEqual(self.p.credited_service_weeks, [1, 2])
        self.t.ir.remove(self.p)
        self.t.roster.append(self.p)
        self.games([1, 2, 3], year=2)
        self.t.roster.remove(self.p)
        self.t.ir.append(self.p)
        self.games([4, 5, 6], year=2)
        service.settle_season(self.lg, 2)
        self.assertEqual((self.p.accrued_seasons, self.p.credited_seasons), (2, 1))
        # Old partial-year saves have no IR/roster distinction: retain a one-time estimate.
        from dataclasses import asdict
        from players import Player
        old = asdict(self.p)
        del old['credited_service_weeks']
        restored = Player(**old)
        self.assertEqual(restored.credited_service_weeks, self.p.service_weeks)

    def test_bowl_playoffs_and_byeless_calendar(self):
        self.games([1, 2], "ambassador")
        self.games([3], "ambassador_bowl")
        self.games([4], "playoff_final")
        service.settle_season(self.lg, 1)
        self.assertEqual((self.p.accrued_seasons, self.p.credited_seasons), (0, 0))
        self.games([1, 2, 3, 4, 5, 6, 7], "ambassador", year=2)
        service.settle_season(self.lg, 2)
        self.assertEqual((self.p.accrued_seasons, self.p.credited_seasons), (1, 1))

    def test_promotion_club_change_release_and_duplicate_game(self):
        self.games([1, 2, 3])
        self.t.practice_squad.remove(self.ps)
        self.t.roster.append(self.ps)
        self.games([4, 5])
        self.t.roster.remove(self.p)
        self.other.roster.append(self.p)
        self.games([5, 6])
        self.other.roster.remove(self.p)
        self.lg.free_agents.append(self.p)
        service.settle_season(self.lg, 1)
        self.assertEqual(self.p.accrued_seasons, 1)
        self.assertEqual((self.ps.accrued_seasons, self.ps.credited_seasons), (0, 1))

    def test_expiration_is_not_release_and_exile_override(self):
        self.p.years_left = 1
        with self.assertRaises(ValueError):
            service.expiry_class(self.p)
        self.p.years_left = 0
        for n, cls in ((0, "exclusive_rights"), (2, "exclusive_rights"),
                       (3, "restricted"), (4, "unrestricted"), (10, "unrestricted")):
            self.p.accrued_seasons = n
            self.assertEqual(service.expiry_class(self.p), cls)
            self.assertEqual(service.expiry_class(self.p, exiled=True), "restricted")

    def test_real_season_rookies_and_saves(self):
        rng = random.Random(3)
        lg = new_league(rng, rosters=True)
        # A partially earned season survives save and load before its award.
        a, b = lg.teams[:2]
        p = a.roster[0]
        old = p.accrued_seasons
        for w in range(1, 4):
            service.record_game(lg, Game(w, a.id, b.id, "division"), 1)
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "service.db")
            store.save(db, lg, rng, 0)
            resumed, _, _ = store.load(db)
            rp = next(x for x in resumed.by_id[a.id].roster if x.id == p.id)
            for w in range(4, 7):
                service.record_game(resumed, Game(w, a.id, b.id, "division"), 1)
            service.settle_season(resumed, 1)
            self.assertEqual(rp.accrued_seasons, old + 1)
            store.save(db, resumed, rng, 1)
            twice, _, _ = store.load(db)
            service.settle_season(twice, 1)
            pp = next(x for x in twice.by_id[a.id].roster if x.id == p.id)
            self.assertEqual(pp.accrued_seasons, old + 1)
        for engine in ("fast", "drives"):
            rr = random.Random(4)
            league = new_league(rr, rosters=True)
            starters = [(t.status, p, p.accrued_seasons) for t in league.teams for p in t.roster]
            run_season(league, 1, rr, Options(engine=engine, keep_boxes=False, injuries=False,
                                              roster_model=RosterModel(trade_sell_prob=0.0, trade_swap_prob=0.0, trade_week_prob=0.0)))   # a trade changes a player's club and her service weeks
            for status, p, before in starters:
                self.assertEqual(len(p.service_weeks), 7 if status == "exiled" else 18)
                self.assertEqual(p.accrued_seasons, before + 1)
            import rosters
            rookies = [p for t in league.teams for p in rosters.squad(t) if p.draft_year == 1]
            self.assertTrue(rookies)
            self.assertTrue(all(p.accrued_seasons == p.credited_seasons == 0 for p in rookies))


if __name__ == "__main__":
    unittest.main(verbosity=2)
