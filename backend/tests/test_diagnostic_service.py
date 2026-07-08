import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import (
    DiagnosticAttempt,
    Exercise,
    ExerciseKnowledgeComponent,
    KnowledgeComponent,
    StudentMastery,
    User,
)
from app.schemas.diagnostic import DiagnosticAnswer
from app.services.diagnostic_service import (
    DiagnosticAlreadyCompletedError,
    get_diagnostic_questions,
    load_question_bank,
    submit_diagnostic,
)


class DiagnosticServiceTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.seed_data()

    def tearDown(self):
        self.engine.dispose()

    def test_question_response_does_not_expose_answers(self):
        response = get_diagnostic_questions()

        self.assertEqual(response.totalQuestions, 24)
        self.assertEqual(len(response.questions), 24)
        self.assertFalse(hasattr(response.questions[0], "correct_option_id"))

    def test_submission_sets_mastery_and_recommends_weakest_kcs(self):
        questions = load_question_bank()
        answers = []
        for index, question in enumerate(questions):
            selected = question["correct_option_id"]
            if question["kc_id"] != "KC001" and question["id"] != "DQ005":
                selected = next(
                    option["id"]
                    for option in question["options"]
                    if option["id"] != question["correct_option_id"]
                )
            answers.append(
                DiagnosticAnswer(
                    questionId=question["id"],
                    selectedOptionId=selected,
                )
            )

        with self.SessionLocal() as db:
            user = db.scalar(select(User).where(User.student_id == "s1"))
            result = submit_diagnostic(db, user, answers)

            mastery_rows = db.scalars(
                select(StudentMastery).where(StudentMastery.student_id == "s1")
            ).all()
            attempt = db.scalar(select(DiagnosticAttempt))

            self.assertEqual(result.correctAnswers, 3)
            self.assertEqual(result.strengths, ["Variables and Expressions"])
            self.assertIn("Conditionals", result.weaknesses)
            self.assertEqual(len(mastery_rows), 12)
            self.assertEqual(
                next(row.mastery for row in mastery_rows if row.kc_id == "KC001"),
                0.6,
            )
            self.assertEqual(
                next(row.mastery for row in mastery_rows if row.kc_id == "KC002"),
                0.0,
            )
            self.assertEqual(
                next(row.mastery for row in mastery_rows if row.kc_id == "KC003"),
                0.3,
            )
            self.assertEqual(
                next(item.level for item in result.kcResults if item.kcId == "KC003"),
                "developing",
            )
            self.assertEqual(len(result.recommendations), 3)
            self.assertEqual(result.recommendations[0].kcId, "KC002")
            self.assertIsNotNone(attempt)
            self.assertTrue(user.diagnostic_completed)

            with self.assertRaises(DiagnosticAlreadyCompletedError):
                submit_diagnostic(db, user, answers)

    def seed_data(self):
        with self.SessionLocal() as db:
            db.add(
                User(
                    student_id="s1",
                    username="new@example.test",
                    name="New Student",
                    role="student",
                    password_salt="salt",
                    password_hash="hash",
                    diagnostic_completed=False,
                )
            )
            for index in range(1, 13):
                kc_id = f"KC{index:03d}"
                db.add(KnowledgeComponent(id=kc_id, name=f"KC {index}"))
                db.add(StudentMastery(student_id="s1", kc_id=kc_id, mastery=0.2))
                exercise_id = f"EX{index:03d}"
                db.add(
                    Exercise(
                        id=exercise_id,
                        type="coding",
                        title=f"Exercise {index}",
                        kc_id=kc_id,
                        difficulty="easy",
                        estimated_minutes=5,
                        status="ready",
                        description="Practice exercise",
                        function_name="answer",
                        starter_code="def answer():\n    pass\n",
                        test_cases=[],
                        hidden_tests=False,
                        hints=[],
                        solution=None,
                    )
                )
                db.add(ExerciseKnowledgeComponent(exercise_id=exercise_id, kc_id=kc_id))
            db.commit()


if __name__ == "__main__":
    unittest.main()
