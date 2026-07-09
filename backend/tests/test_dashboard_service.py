import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Exercise, KnowledgeComponent, StudentMastery, Submission, User
from app.services.dashboard_service import build_class_dashboard_summary


class DashboardServiceTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def test_class_dashboard_includes_recent_submissions(self):
        with self.SessionLocal() as db:
            db.add(
                User(
                    student_id="s1",
                    username="student@example.test",
                    name="Student One",
                    role="student",
                    password_salt="salt",
                    password_hash="hash",
                )
            )
            db.add(KnowledgeComponent(id="KC001", name="Variables"))
            db.add(
                Exercise(
                    id="EX001",
                    type="coding",
                    title="Variables Practice",
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
            db.add(StudentMastery(student_id="s1", kc_id="KC001", mastery=0.4))
            db.add(
                Submission(
                    student_id="s1",
                    exercise_id="EX001",
                    code="def answer():\n    return 1\n",
                    language="python",
                    status="Accepted",
                    passed=True,
                    score=1.0,
                    test_results=[
                        {"passed": True},
                        {"passed": True},
                    ],
                )
            )
            db.commit()

            summary = build_class_dashboard_summary(db, "demo-python-101")

            self.assertEqual(summary.totals.submissions_7d, 1)
            self.assertEqual(len(summary.recent_submissions), 1)
            self.assertEqual(summary.recent_submissions[0].display_name, "Student One")
            self.assertEqual(summary.recent_submissions[0].exercise_title, "Variables Practice")
            self.assertEqual(summary.recent_submissions[0].status, "passed")
            self.assertEqual(summary.recent_submissions[0].passed_count, 2)
            self.assertEqual(summary.recent_submissions[0].total_count, 2)


if __name__ == "__main__":
    unittest.main()
