import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.api.assistant import chat_with_study_assistant
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


class AssistantApiTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.seed_data()

    def tearDown(self):
        self.engine.dispose()

    @patch("app.api.assistant.parse_assistant_intent")
    @patch("app.api.assistant.get_user_model_from_token")
    def test_authenticated_request_returns_database_exercise(
        self,
        mock_get_user,
        mock_parse_intent,
    ):
        with self.SessionLocal() as db:
            mock_get_user.return_value = db.scalar(
                select(User).where(User.student_id == "s1")
            )
            mock_parse_intent.return_value = AssistantIntentResult(
                intent=AssistantIntent(
                    kc_code="KC003",
                    difficulty="easy",
                    use_weakest_kc=False,
                ),
                source="openai",
            )

            response = chat_with_study_assistant(
                request=AssistantChatRequest(
                    message="I want an easy loops exercise",
                    currentExerciseId="EX001",
                ),
                auth_credentials=HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials="valid-token",
                ),
                db=db,
            )

        self.assertEqual(response.recommendedExercise.id, "EX003")
        self.assertEqual(response.intent.source, "openai")

    def test_missing_token_returns_401(self):
        with self.SessionLocal() as db:
            with self.assertRaises(HTTPException) as context:
                chat_with_study_assistant(
                    request=AssistantChatRequest(message="Recommend something"),
                    auth_credentials=None,
                    db=db,
                )

        self.assertEqual(context.exception.status_code, 401)

    @patch("app.api.assistant.get_user_model_from_token", return_value=None)
    def test_invalid_token_returns_401(self, _mock_get_user):
        with self.SessionLocal() as db:
            with self.assertRaises(HTTPException) as context:
                chat_with_study_assistant(
                    request=AssistantChatRequest(message="Recommend something"),
                    auth_credentials=HTTPAuthorizationCredentials(
                        scheme="Bearer",
                        credentials="invalid-token",
                    ),
                    db=db,
                )

        self.assertEqual(context.exception.status_code, 401)

    def seed_data(self):
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
            db.add(StudentMastery(student_id="s1", kc_id="KC003", mastery=0.2))
            for exercise_id in ("EX001", "EX003"):
                db.add(
                    Exercise(
                        id=exercise_id,
                        type="coding",
                        title=exercise_id,
                        kc_id="KC003",
                        difficulty="easy",
                        estimated_minutes=5,
                        status="published",
                        description="Practise loops.",
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
                        kc_id="KC003",
                    )
                )
            db.commit()


if __name__ == "__main__":
    unittest.main()
