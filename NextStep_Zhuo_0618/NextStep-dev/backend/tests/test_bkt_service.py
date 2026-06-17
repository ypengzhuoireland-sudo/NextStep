import unittest

from app.services.bkt_service import BKTParameters, update_knowledge_state


class BKTServiceTest(unittest.TestCase):
    def test_correct_answer_uses_bayesian_knowledge_tracing_formula(self):
        params = BKTParameters(prior=0.2, learn=0.15, guess=0.2, slip=0.1)

        updated = update_knowledge_state(0.5, correct=True, params=params)

        self.assertAlmostEqual(updated, 0.8455, places=4)

    def test_incorrect_answer_uses_slip_and_guess_in_bkt_formula(self):
        params = BKTParameters(prior=0.2, learn=0.15, guess=0.2, slip=0.1)

        updated = update_knowledge_state(0.5, correct=False, params=params)

        self.assertAlmostEqual(updated, 0.2444, places=4)

    def test_update_is_clamped_between_zero_and_one(self):
        params = BKTParameters(prior=0.2, learn=0.95, guess=0.01, slip=0.01)

        updated = update_knowledge_state(1.0, correct=True, params=params)

        self.assertEqual(updated, 1.0)

    def test_incorrect_answer_does_not_increase_mastery_from_zero(self):
        params = BKTParameters(prior=0.2, learn=0.15, guess=0.2, slip=0.1)

        updated = update_knowledge_state(0.0, correct=False, params=params)

        self.assertEqual(updated, 0.0)


if __name__ == "__main__":
    unittest.main()
