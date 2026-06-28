import unittest

from app.services.ai.schemas import (
    CurrentExercise,
    ExerciseContext,
    HintRequest,
    LearningAdviceRequest,
    ProgressTrend,
    RecommendationExplanationRequest,
    RecommendedExercise,
)
from app.services.ai.llm_client import (
    create_fallback_advice,
    create_fallback_explanation,
    create_fallback_hint,
)


class AIServiceFallbackTest(unittest.TestCase):
    def test_hint_fallback_preserves_requested_level(self):
        request = HintRequest(
            exercise=ExerciseContext(
                id="ex1",
                title="Celsius to Fahrenheit",
                prompt="Convert Celsius to Fahrenheit.",
                kc_tags=["variables"],
            ),
            requested_hint_level=2,
        )

        hint = create_fallback_hint(request)

        self.assertEqual(hint.level, 2)
        self.assertTrue(hint.avoid_full_solution)
        self.assertTrue(hint.hint_text)

    def test_recommendation_fallback_preserves_confidence(self):
        request = RecommendationExplanationRequest(
            student_id="s1",
            current_exercise=CurrentExercise(id="ex1", title="Current"),
            recommended_exercise=RecommendedExercise(
                id="ex2",
                title="Next",
                kc_tags=["loops"],
            ),
            strategy="lowest_mastery_with_difficulty_match",
            confidence=0.82,
        )

        explanation = create_fallback_explanation(request)

        self.assertEqual(explanation.confidence, 0.82)
        self.assertTrue(explanation.student_friendly_reason)

    def test_learning_advice_fallback_has_next_steps(self):
        request = LearningAdviceRequest(
            student_id="s1",
            progress_trend=ProgressTrend(overall_mastery=0.0, overall_delta=0.0),
        )

        advice = create_fallback_advice(request)

        self.assertGreaterEqual(len(advice.next_steps), 1)
        self.assertTrue(advice.summary)


if __name__ == "__main__":
    unittest.main()
