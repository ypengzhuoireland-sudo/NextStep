import unittest

from app.services.ai.schemas import HintResponse
from app.services.practice_service import build_hint_message_from_ai_response
from app.services.ai.schemas import RecommendationExplanationResponse
from app.services.recommendation_api_service import build_recommendation_reason_from_ai_response


class AIIntegrationTest(unittest.TestCase):
    def test_build_hint_message_from_ai_response_maps_existing_fields(self):
        ai_hint = HintResponse(
            level=2,
            title="Check the formula",
            hint_text="Make sure you multiply Celsius by 9/5 before adding 32.",
            next_step="Trace the sample input 100 by hand.",
            kc_code="variables",
            avoid_full_solution=True,
        )

        message = build_hint_message_from_ai_response(
            session_id="ses_demo",
            student_id="s1",
            exercise_id="ex1",
            hint=ai_hint,
        )

        self.assertEqual(message.id, "hint_ses_demo_s1_ex1_2")
        self.assertEqual(message.role, "assistant")
        self.assertEqual(message.level, 2)
        self.assertEqual(message.title, "Check the formula")
        self.assertEqual(message.text, ai_hint.hint_text)
        self.assertEqual(message.kcCode, "variables")
        self.assertTrue(message.avoid_full_solution)

    def test_build_recommendation_reason_from_ai_response_uses_student_text(self):
        explanation = RecommendationExplanationResponse(
            reason="Mastery for loops is below the target threshold.",
            student_friendly_reason="This one helps you practise loops while the task is still short.",
            focus_kc="loops",
            expected_benefit="You will strengthen loop tracing.",
            confidence=0.82,
        )

        reason = build_recommendation_reason_from_ai_response(explanation)

        self.assertEqual(
            reason,
            "This one helps you practise loops while the task is still short.",
        )


if __name__ == "__main__":
    unittest.main()
