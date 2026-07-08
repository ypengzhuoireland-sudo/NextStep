import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import (
    Exercise,
    ExerciseKnowledgeComponent,
    KnowledgeComponent,
    MasteryEvent,
    StudentMastery,
    Submission,
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

    def test_answer_request_without_submission_returns_pseudocode_only(self):
        with self.SessionLocal() as db:
            self.seed_data(db)

            response = build_assistant_recommendation(
                db,
                student_id="s1",
                request=AssistantChatRequest(
                    message="Give me the full answer",
                    currentExerciseId="EX006",
                ),
                intent_result=self.intent("KC001"),
            )

            self.assertIsNone(response.recommendedExercise)
            self.assertIn("pseudocode", response.message.lower())
            self.assertIn("```text", response.message)
            self.assertIn("FUNCTION add_tax(price, rate)", response.message)
            self.assertIn("END FUNCTION", response.message)
            self.assertIn("submit", response.message.lower())
            self.assertNotIn("return price * (1 + rate)", response.message)

    def test_answer_request_after_submission_returns_review_mode_solution(self):
        with self.SessionLocal() as db:
            self.seed_data(db)
            db.add(
                Submission(
                    student_id="s1",
                    exercise_id="EX006",
                    code="def add_tax(price, rate):\n    return price\n",
                    language="python",
                    status="failed_tests",
                    passed=False,
                    score=0.0,
                    stdout="",
                    stderr="",
                    test_results=[],
                )
            )
            db.commit()

            response = build_assistant_recommendation(
                db,
                student_id="s1",
                request=AssistantChatRequest(
                    message="Show me the code",
                    currentExerciseId="EX006",
                ),
                intent_result=self.intent("KC001"),
            )

            self.assertIsNone(response.recommendedExercise)
            self.assertIn("Review Mode", response.message)
            self.assertIn("return price * (1 + rate)", response.message)

    def test_learning_summary_request_returns_student_progress(self):
        with self.SessionLocal() as db:
            self.seed_data(db)
            self.seed_learning_activity(db)

            response = build_assistant_recommendation(
                db,
                student_id="s1",
                request=AssistantChatRequest(message="How am I doing?"),
                intent_result=self.intent(None),
            )

            self.assertIsNone(response.recommendedExercise)
            self.assertTrue(response.exactMatch)
            self.assertIn("Learning Summary", response.message)
            self.assertIn("Strong areas", response.message)
            self.assertIn("Weak areas", response.message)
            self.assertIn("Recent progress", response.message)
            self.assertIn("2/3 recent submissions passed", response.message)
            self.assertIn("Lists", response.message)

    def test_chinese_learning_summary_request_is_supported(self):
        with self.SessionLocal() as db:
            self.seed_data(db)
            self.seed_learning_activity(db)

            response = build_assistant_recommendation(
                db,
                student_id="s1",
                request=AssistantChatRequest(message="我的学习情况怎么样"),
                intent_result=self.intent(None),
            )

            self.assertIsNone(response.recommendedExercise)
            self.assertTrue(response.exactMatch)
            self.assertIn("Learning Summary", response.message)
            self.assertIn("Next focus", response.message)

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

    def seed_learning_activity(self, db):
        db.add_all(
            [
                Submission(
                    student_id="s1",
                    exercise_id="EX001",
                    code="def answer():\n    return 1\n",
                    language="python",
                    status="accepted",
                    passed=True,
                    score=1.0,
                    stdout="",
                    stderr="",
                    test_results=[],
                ),
                Submission(
                    student_id="s1",
                    exercise_id="EX003",
                    code="def answer():\n    return 2\n",
                    language="python",
                    status="accepted",
                    passed=True,
                    score=1.0,
                    stdout="",
                    stderr="",
                    test_results=[],
                ),
                Submission(
                    student_id="s1",
                    exercise_id="EX004",
                    code="def answer():\n    return None\n",
                    language="python",
                    status="failed_tests",
                    passed=False,
                    score=0.0,
                    stdout="",
                    stderr="",
                    test_results=[],
                ),
                MasteryEvent(
                    student_id="s1",
                    exercise_id="EX003",
                    kc_id="KC003",
                    old_mastery=0.3,
                    new_mastery=0.4,
                    correct=True,
                    attempt_no=1,
                    bkt_prior=0.3,
                    bkt_learn=0.1,
                    bkt_guess=0.2,
                    bkt_slip=0.1,
                ),
            ]
        )
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
                starter_code=(
                    "def add_tax(price, rate):\n    pass\n"
                    if exercise_id == "EX006"
                    else "def answer():\n    pass\n"
                ),
                test_cases=[],
                hidden_tests=False,
                hints=[],
                solution=(
                    "def add_tax(price, rate):\n"
                    "    return price * (1 + rate)\n"
                    if exercise_id == "EX006"
                    else None
                ),
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
