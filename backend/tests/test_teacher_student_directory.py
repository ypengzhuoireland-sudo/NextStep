import unittest
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from fastapi import HTTPException
from app.api.dashboard import require_teacher_class_access
from app.db.base import Base
from app.db.init_db import seed_default_class_enrollments
from app.models import (
    ClassEnrollment,
    Exercise,
    KnowledgeComponent,
    StudentMastery,
    Submission,
    User,
)
from app.services.dashboard_service import (
    get_class_student_detail,
    list_class_students,
)
from app.schemas.sessions import UserProfile


class TeacherStudentDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def tearDown(self):
        self.engine.dispose()

    def test_search_returns_only_matching_students_in_the_requested_class(self):
        with self.SessionLocal() as db:
            self.seed_students(db)

            result = list_class_students(
                db,
                class_id="python-101",
                query="alice",
            )

        self.assertEqual(result.total, 1)
        self.assertEqual(result.items[0].student_id, "s1")
        self.assertEqual(result.items[0].display_name, "Alice")
        self.assertEqual(result.items[0].weakest_kc, "Variables")

    def test_detail_returns_activity_and_mastery_for_a_class_member(self):
        with self.SessionLocal() as db:
            self.seed_students(db)

            detail = get_class_student_detail(
                db,
                class_id="python-101",
                student_id="s1",
            )

        self.assertIsNotNone(detail)
        assert detail is not None
        self.assertEqual(detail.student.student_id, "s1")
        self.assertEqual(detail.student.average_mastery, 0.3)
        self.assertEqual(detail.weak_kcs[0].code, "KC001")
        self.assertEqual(detail.activity.submissions_7d, 1)
        self.assertEqual(detail.activity.failed_attempts_7d, 1)
        self.assertEqual(detail.activity.recent_submissions[0].exercise_title, "Variables Practice")

    def test_detail_returns_none_for_a_student_outside_the_class(self):
        with self.SessionLocal() as db:
            self.seed_students(db)

            detail = get_class_student_detail(
                db,
                class_id="python-101",
                student_id="s2",
            )

        self.assertIsNone(detail)

    def test_teacher_without_class_membership_is_forbidden(self):
        with self.SessionLocal() as db:
            db.add(
                User(
                    student_id="t2",
                    username="teacher@example.test",
                    name="Teacher Two",
                    role="teacher",
                    password_salt="salt",
                    password_hash="hash",
                )
            )
            db.commit()

            with self.assertRaises(HTTPException) as context:
                require_teacher_class_access(
                    db,
                    UserProfile(
                        student_id="t2",
                        username="teacher@example.test",
                        name="Teacher Two",
                        role="teacher",
                    ),
                    "python-101",
                )

        self.assertEqual(context.exception.status_code, 403)

    def test_default_class_enrollment_seed_is_idempotent(self):
        with self.SessionLocal() as db:
            db.add_all(
                [
                    User(
                        student_id="s1",
                        username="student@example.test",
                        name="Student One",
                        role="student",
                        password_salt="salt",
                        password_hash="hash",
                    ),
                    User(
                        student_id="t1",
                        username="teacher@example.test",
                        name="Teacher One",
                        role="teacher",
                        password_salt="salt",
                        password_hash="hash",
                    ),
                ]
            )

            seed_default_class_enrollments(db)
            seed_default_class_enrollments(db)
            db.commit()

            enrollments = db.scalars(
                select(ClassEnrollment).order_by(ClassEnrollment.user_id)
            ).all()

        self.assertEqual(
            [(item.class_id, item.user_id) for item in enrollments],
            [("demo-python-101", "s1"), ("demo-python-101", "t1")],
        )

    def seed_students(self, db):
        db.add_all(
            [
                User(
                    student_id="s1",
                    username="alice@example.test",
                    name="Alice",
                    role="student",
                    password_salt="salt",
                    password_hash="hash",
                ),
                User(
                    student_id="s2",
                    username="alice-outside@example.test",
                    name="Alice Outside",
                    role="student",
                    password_salt="salt",
                    password_hash="hash",
                ),
            ]
        )
        db.add_all(
            [
                ClassEnrollment(class_id="python-101", user_id="s1"),
                ClassEnrollment(class_id="python-102", user_id="s2"),
                KnowledgeComponent(id="KC001", name="Variables"),
                KnowledgeComponent(id="KC002", name="Loops"),
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
                ),
                StudentMastery(student_id="s1", kc_id="KC001", mastery=0.2),
                StudentMastery(student_id="s1", kc_id="KC002", mastery=0.4),
                StudentMastery(student_id="s2", kc_id="KC001", mastery=0.9),
                Submission(
                    student_id="s1",
                    exercise_id="EX001",
                    code="def answer():\n    return 1\n",
                    language="python",
                    status="failed",
                    passed=False,
                    score=0.0,
                    test_results=[{"passed": False}],
                    created_at=datetime.now(timezone.utc),
                ),
            ]
        )
        db.commit()


if __name__ == "__main__":
    unittest.main()
