from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from app.models.diagnostic_attempt import DiagnosticAttempt
from app.schemas.diagnostic import DiagnosticAnswer
from app.services.diagnostic_service import (
    DiagnosticValidationError,
    load_question_bank,
    submit_diagnostic,
)


class FakeSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.commits = 0

    def get(self, _model: object, _key: object) -> None:
        return None

    def add(self, value: object) -> None:
        self.added.append(value)

    def commit(self) -> None:
        self.commits += 1


def make_user() -> SimpleNamespace:
    return SimpleNamespace(
        student_id="diagnostic_test_student",
        diagnostic_completed=False,
        diagnostic_completed_at=None,
    )


class DiagnosticServiceTests(TestCase):
    @patch("app.services.diagnostic_service.build_recommendations", return_value=[])
    def test_missing_answers_are_scored_as_skipped_and_incorrect(
        self,
        _build_recommendations: object,
    ) -> None:
        questions = load_question_bank()
        first_question = questions[0]
        db = FakeSession()
        user = make_user()

        result = submit_diagnostic(
            db,
            user,
            [
                DiagnosticAnswer(
                    questionId=first_question["id"],
                    selectedOptionId=first_question["correct_option_id"],
                )
            ],
        )

        self.assertEqual(result.correctAnswers, 1)
        self.assertEqual(result.totalQuestions, len(questions))
        self.assertTrue(result.questionResults[0].isCorrect)
        self.assertFalse(result.questionResults[0].skipped)
        self.assertTrue(result.questionResults[1].skipped)
        self.assertFalse(result.questionResults[1].isCorrect)
        self.assertEqual(db.commits, 1)
        self.assertTrue(user.diagnostic_completed)

        attempt = next(item for item in db.added if isinstance(item, DiagnosticAttempt))
        self.assertEqual(len(attempt.answers), len(questions))
        self.assertIsNone(attempt.answers[1]["selectedOptionId"])

    @patch("app.services.diagnostic_service.build_recommendations", return_value=[])
    def test_empty_submission_skips_the_entire_diagnostic(
        self,
        _build_recommendations: object,
    ) -> None:
        db = FakeSession()
        user = make_user()

        result = submit_diagnostic(db, user, [])

        self.assertEqual(result.correctAnswers, 0)
        self.assertEqual(result.overallScore, 0)
        self.assertTrue(all(item.skipped for item in result.questionResults))
        self.assertTrue(all(not item.isCorrect for item in result.questionResults))
        self.assertTrue(user.diagnostic_completed)

    def test_unknown_question_is_rejected(self) -> None:
        db = FakeSession()
        user = make_user()

        with self.assertRaisesRegex(
            DiagnosticValidationError,
            "Unknown diagnostic question",
        ):
            submit_diagnostic(
                db,
                user,
                [DiagnosticAnswer(questionId="not-a-question", selectedOptionId="a")],
            )

        self.assertEqual(db.commits, 0)
        self.assertFalse(user.diagnostic_completed)
