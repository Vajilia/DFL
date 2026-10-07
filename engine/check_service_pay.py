"""Earned-service salary and practice-squad integration (Step 6b)."""
import os
import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import economy as EC
import rosters as RS
import store
from league import new_league
from players import make_player
from season import Options, run_season


class ServicePayChecks(unittest.TestCase):
    def player(self, pid=900001, accrued=0, credited=0):
        p = make_player(random.Random(pid), pid, "WR", 30, 30)
        p.accrued_seasons, p.credited_seasons = accrued, credited
        return p

    def test_calendar_age_does_not_create_eligibility_or_pay(self):
        p = self.player(accrued=2, credited=1)
        p.years_in_league = 12
        self.assertTrue(RS.ps_rookie_slot(p))
        self.assertEqual(EC.market_salary(p.pos, 20, p.credited_seasons), 0.33)
        p.accrued_seasons = 3
        self.assertFalse(RS.ps_rookie_slot(p))
        cands = [self.player(i, accrued=3) for i in range(20)]
        self.assertEqual(len(RS.choose_practice_squad(cands)), 6)
        cands.extend(self.player(i, accrued=2) for i in range(20, 40))
        chosen = RS.choose_practice_squad(cands)
        self.assertEqual(len(chosen), 16)
        self.assertLessEqual(RS.veterans_on_squad(chosen), 6)

    def test_contract_base_floor_and_continuing_contract(self):
        p = self.player(credited=0)
        EC.sign(p, 0.30, 4, share=0.1, guarantee_years=0, rookie=True)
        self.assertAlmostEqual(p.salary, 0.30)
        self.assertAlmostEqual(p.bonus, 0.01)
        self.assertAlmostEqual(p.salary - p.bonus, 0.29)
        bonus, guarantee = p.bonus, p.guaranteed
        p.credited_seasons = 2
        EC.enforce_minimum(p)
        self.assertAlmostEqual(p.salary - p.bonus, 0.36)
        self.assertEqual((p.bonus, p.guaranteed), (bonus, guarantee))
        EC.enforce_minimum(p)
        self.assertAlmostEqual(p.salary, 0.37)
        veteran = self.player(credited=7)
        EC.sign(veteran, 0.29, 1)
        self.assertEqual(veteran.salary, 0.43)

    def test_street_initialization_and_practice_squad_promotion(self):
        rng = random.Random(77)
        lg = new_league(rng, rosters=True)
        street = RS.street_player(lg, rng, "OL")
        self.assertEqual((street.accrued_seasons, street.credited_seasons), (0, 0))
        t = lg.teams[0]
        promoted = max((p for p in t.practice_squad if p.pos == "OL"), key=lambda p: (p.ovr, -p.id))
        promoted.credited_seasons, promoted.years_in_league = 2, 12
        RS.to_practice_squad(promoted)
        self.assertEqual(promoted.salary, EC.PRACTICE_SQUAD_SALARY)
        removed = next(p for p in t.roster if p.pos == "OL")
        t.roster.remove(removed)
        removed.team_id = None
        removed.retired = True
        lg.retired_players.append(removed)
        RS.fill_roster(lg, t, rng)
        self.assertIn(promoted, t.roster)
        self.assertEqual(promoted.salary, 0.36)

    def test_full_seasons_and_saved_eligibility(self):
        for engine in ("fast", "drives"):
            rng = random.Random(17)
            lg = new_league(rng, rosters=True)
            for year in range(1, 5):
                run_season(lg, year, rng, Options(engine=engine, keep_boxes=False))
                for t in lg.teams:
                    self.assertLessEqual(EC.payroll(t), EC.limit(t) + 1e-6)
                    self.assertLessEqual(RS.veterans_on_squad(t.practice_squad), 6)
                    for p in t.roster + t.ir:
                        self.assertGreaterEqual(p.salary - p.bonus + 1e-8, EC.min_salary(p.credited_seasons))
                    for p in t.practice_squad:
                        self.assertEqual(p.salary, EC.PRACTICE_SQUAD_SALARY)
            with tempfile.TemporaryDirectory() as tmp:
                db = str(Path(tmp) / "pay.db")
                store.save(db, lg, rng, 4)
                resumed, rr, _ = store.load(db)
                run_season(lg, 5, rng, Options(engine=engine, keep_boxes=False))
                run_season(resumed, 5, rr, Options(engine=engine, keep_boxes=False))
                body = lambda league: [(t.id, [(p.id, p.salary, p.bonus, p.accrued_seasons, p.credited_seasons) for p in RS.squad(t)]) for t in league.teams]
                self.assertEqual(body(lg), body(resumed))
                self.assertEqual(rng.getstate(), rr.getstate())


if __name__ == "__main__":
    unittest.main(verbosity=2)
