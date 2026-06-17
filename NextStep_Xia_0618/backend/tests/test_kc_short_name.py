import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import KnowledgeComponent, StudentMastery, User
from app.services.mastery_service import get_student_mastery_profile


class KnowledgeComponentShortNameTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def test_mastery_profile_includes_short_name(self):
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
            db.add(
                KnowledgeComponent(
                    id="KC001",
                    name="Variables and Expressions",
                    short_name="Vars",
                    description="Assignment and expressions.",
                )
            )
            db.add(StudentMastery(student_id="s1", kc_id="KC001", mastery=0.4))
            db.commit()

            profile = get_student_mastery_profile(db, "s1")

            self.assertIsNotNone(profile)
            self.assertEqual(profile.items[0].shortName, "Vars")


if __name__ == "__main__":
    unittest.main()
