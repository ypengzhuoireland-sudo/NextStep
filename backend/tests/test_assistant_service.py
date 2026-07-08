import unittest

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
from app.schemas.assistant import AssistantChatRequest
from app.services.ai.schemas import AssistantIntent, AssistantIntentResult
from app.services.assistant_service import build_assistant_recommendation


class AssistantServiceTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def test_requested_kc_takes_priority_over_weakest_kc(self):
        with self.SessionLocal() as db:
            self.seed_data(db)

            response = build_assistant_recommendation(
                db,
                student_id="s1",
                request=AssistantChatRequest(
                    message="I want to practise loops",
                    currentExerciseId="EX001",
                ),
                intent_result=self.intent("KC003"),
            )

            self.assertIsNotNone(response.recommendedExercise)
            self.assertEqual(response.recommendedExercise.id, "EX003")
            self.assertTrue(response.exactMatch)

    def test_weakest_kc_is_used_for_general_request(self):
        with self.SessionLocal() as db:
            self.seed_data(db)

            response = build_assistant_recommendation(
                db,
                student_id="s1",
                request=AssistantChatRequest(message="Recommend something useful"),
                intent_result=self.intent(None, use_weakest=True),
            )

            self.assertIsNotNone(response.recommendedExercise)
            self.assertEqual(response.recommendedExercise.primaryKc, "KC006")

    def test_current_exercise_is_excluded_when_another_match_exists(self):
        with self.SessionLocal() as db:
            self.seed_data(db)

            response = build_assistant_recommendation(
                db,
                student_id="s1",
                request=AssistantChatRequest(
                    message="Give me a list exercise",
                    currentExerciseId="EX004",
                ),
                intent_result=self.intent("KC006"),
            )

            self.assertIsNotNone(response.recommendedExercise)
            self.assertEqual(response.recommendedExercise.id, "EX005")

    def test_named_exercise_request_takes_priority_over_kc_order(self):
        with self.SessionLocal() as db:
            self.seed_data(db)

            response = build_assistant_recommendation(
                db,
                student_id="s1",
                request=AssistantChatRequest(
                    message="give me the add_tax exercise from Variables and Expressions",
                    currentExerciseId="EX003",
                ),
                intent_result=self.intent("KC001"),
            )

            self.assertIsNotNone(response.recommendedExercise)
            self.assertEqual(response.recommendedExercise.id, "EX006")
            self.assertTrue(response.exactMatch)

    def test_closest_difficulty_is_returned_when_exact_match_is_unavailable(self):
        with self.SessionLocal() as db:
            self.seed_data(db)

            response = build_assistant_recommendation(
                db,
                student_id="s1",
                request=AssistantChatRequest(message="I want hard loops"),
                intent_result=self.intent("KC003", difficulty="hard"),
            )

            self.assertIsNotNone(response.recommendedExercise)
            self.assertEqual(response.recommendedExercise.id, "EX003")
            self.assertFalse(response.exactMatch)
            self.assertIn("closest", response.message.lower())

    def test_no_eligible_exercise_returns_null_recommendation(self):
        with self.SessionLocal() as db:
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
            db.add(KnowledgeComponent(id="KC003", name="Loops"))
            db.commit()

            response = build_assistant_recommendation(
                db,
                student_id="s1",
                request=AssistantChatRequest(message="loops"),
                intent_result=self.intent("KC003"),
            )

            self.assertIsNone(response.recommendedExercise)
            self.assertFalse(response.exactMatch)

    def intent(self, kc_code, difficulty=None, use_weakest=False):
        return AssistantIntentResult(
            intent=AssistantIntent(
                kc_code=kc_code,
                difficulty=difficulty,
                use_weakest_kc=use_weakest,
            ),
            source="openai",
        )

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
        for code, name, mastery in (
            ("KC001", "Variables", 0.5),
            ("KC003", "Loops", 0.4),
            ("KC006", "Lists", 0.1),
        ):
            db.add(KnowledgeComponent(id=code, name=name))
            db.add(StudentMastery(student_id="s1", kc_id=code, mastery=mastery))

        self.add_exercise(db, "EX001", "Variables One", "KC001", "easy")
        self.add_exercise(db, "EX002", "Variables Two", "KC001", "medium")
        self.add_exercise(db, "EX003", "Loop Practice", "KC003", "easy")
        self.add_exercise(db, "EX004", "List Practice One", "KC006", "easy")
        self.add_exercise(db, "EX005", "List Practice Two", "KC006", "easy")
        self.add_exercise(db, "EX006", "Add Tax Helper", "KC001", "easy", "add_tax")
        db.commit()

    def add_exercise(self, db, exercise_id, title, kc_id, difficulty, function_name="answer"):
        db.add(
            Exercise(
                id=exercise_id,
                type="coding",
                title=title,
                kc_id=kc_id,
                difficulty=difficulty,
                estimated_minutes=5,
                status="published",
                description=f"Practise {title}.",
                function_name=function_name,
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
                kc_id=kc_id,
            )
        )


if __name__ == "__main__":
    unittest.main()
