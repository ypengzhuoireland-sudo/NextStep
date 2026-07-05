import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import (
    Exercise,
    ExerciseKnowledgeComponent,
    KnowledgeComponent,
    StudentMastery,
    User,
)
from app.schemas.recommendations import NextRecommendationRequest
from app.services.recommendation_api_service import build_next_recommendation


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    @patch(
        "app.services.recommendation_api_service.build_ai_recommendation_reason",
        side_effect=lambda db, student_id, exercise, strategy, confidence, fallback_reason, **kwargs: fallback_reason,
    )
    def test_next_recommendation_excludes_current_exercise(self, _mock_reason):
        with self.SessionLocal() as db:
            self.seed_data(db)

            response = build_next_recommendation(
                db,
                NextRecommendationRequest(
                    student_id="s1",
                    current_exercise_id="EX001",
                ),
            )

            self.assertIsNotNone(response.exercise)
            self.assertEqual(response.exercise.id, "EX002")

    def seed_data(self, db):
        db.add(
            User(
                student_id="s1",
                username="student@example.test",
                name="Student",
                role="student",
                password_salt="salt",
                password_hash="hash",
            )
        )
        db.add(KnowledgeComponent(id="KC001", name="Variables"))
        db.add(StudentMastery(student_id="s1", kc_id="KC001", mastery=0.1))

        for exercise_id in ("EX001", "EX002"):
            db.add(
                Exercise(
                    id=exercise_id,
                    type="coding",
                    title=exercise_id,
                    kc_id="KC001",
                    difficulty="easy",
                    estimated_minutes=5,
                    status="ready",
                    description="Practice variables.",
                    function_name="answer",
                    starter_code="def answer():\n    pass\n",
                    test_cases=[],
                    hidden_tests=False,
                    hints=[],
                    solution=None,
                )
            )
            db.add(
                ExerciseKnowledgeComponent(
                    exercise_id=exercise_id,
                    kc_id="KC001",
                )
            )

        db.commit()


if __name__ == "__main__":
    unittest.main()
