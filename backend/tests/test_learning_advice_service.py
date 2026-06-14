import unittest

from app.services.ai.schemas import LearningAdviceRequest, ProgressTrend
from app.services.learning_advice_service import build_learning_advice_from_ai_request


class LearningAdviceServiceTest(unittest.TestCase):
    def test_empty_context_returns_valid_next_steps(self):
        request = LearningAdviceRequest(
            student_id="s1",
            progress_trend=ProgressTrend(overall_mastery=0.0, overall_delta=0.0),
        )

        response = build_learning_advice_from_ai_request(request)

        self.assertTrue(response.summary)
        self.assertGreaterEqual(len(response.next_steps), 1)
        self.assertEqual(response.warning, "")


if __name__ == "__main__":
    unittest.main()
