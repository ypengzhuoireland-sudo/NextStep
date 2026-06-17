import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models import Exercise, ExerciseKnowledgeComponent, KnowledgeComponent, StudentMastery, User
from app.models.bkt_parameters import KnowledgeComponentBKTParameters
from app.models.mastery_event import MasteryEvent
from app.services.submission_service import update_mastery_for_submission


class BKTMasteryIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def test_submission_update_uses_bkt_and_logs_event(self):
        with self.SessionLocal() as db:
            self.seed_exercise(db)

            deltas = update_mastery_for_submission(
                db=db,
                student_id="s1",
                exercise_id="ex1",
                passed=True,
            )
            db.commit()

            mastery = db.get(StudentMastery, ("s1", "KC001"))
            event = db.scalar(select(MasteryEvent))

            self.assertEqual(len(deltas), 1)
            self.assertAlmostEqual(deltas[0].before, 0.5, places=4)
            self.assertAlmostEqual(deltas[0].after, 0.8455, places=4)
            self.assertIsNotNone(mastery)
            self.assertAlmostEqual(mastery.mastery, 0.8455, places=4)
            self.assertIsNotNone(event)
            self.assertEqual(event.student_id, "s1")
            self.assertEqual(event.exercise_id, "ex1")
            self.assertEqual(event.kc_id, "KC001")
            self.assertTrue(event.correct)
            self.assertEqual(event.attempt_no, 1)
            self.assertAlmostEqual(event.old_mastery, 0.5, places=4)
            self.assertAlmostEqual(event.new_mastery, 0.8455, places=4)
            self.assertAlmostEqual(event.bkt_learn, 0.15, places=4)
            self.assertAlmostEqual(event.bkt_guess, 0.2, places=4)
            self.assertAlmostEqual(event.bkt_slip, 0.1, places=4)

    def test_submission_update_uses_kc_specific_bkt_parameters(self):
        with self.SessionLocal() as db:
            self.seed_exercise(db)
            db.add(
                KnowledgeComponentBKTParameters(
                    kc_id="KC001",
                    prior=0.2,
                    learn=0.05,
                    guess=0.25,
                    slip=0.2,
                )
            )
            db.commit()

            deltas = update_mastery_for_submission(
                db=db,
                student_id="s1",
                exercise_id="ex1",
                passed=True,
            )
            db.commit()

            event = db.scalar(select(MasteryEvent))

            self.assertAlmostEqual(deltas[0].after, 0.7738, places=4)
            self.assertIsNotNone(event)
            self.assertAlmostEqual(event.bkt_learn, 0.05, places=4)
            self.assertAlmostEqual(event.bkt_guess, 0.25, places=4)
            self.assertAlmostEqual(event.bkt_slip, 0.2, places=4)

    def test_failed_submission_does_not_raise_zero_mastery(self):
        with self.SessionLocal() as db:
            self.seed_exercise(db, initial_mastery=0.0)

            deltas = update_mastery_for_submission(
                db=db,
                student_id="s1",
                exercise_id="ex1",
                passed=False,
            )
            db.commit()

            mastery = db.get(StudentMastery, ("s1", "KC001"))
            event = db.scalar(select(MasteryEvent))

            self.assertEqual(deltas[0].before, 0.0)
            self.assertEqual(deltas[0].after, 0.0)
            self.assertIsNotNone(mastery)
            self.assertEqual(mastery.mastery, 0.0)
            self.assertIsNotNone(event)
            self.assertFalse(event.correct)
            self.assertEqual(event.new_mastery, 0.0)

    def seed_exercise(self, db: Session, initial_mastery: float = 0.5) -> None:
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
        db.add(
            Exercise(
                id="ex1",
                type="coding",
                title="Variables Practice",
                kc_id="KC001",
                difficulty="easy",
                estimated_minutes=6,
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
        db.add(ExerciseKnowledgeComponent(exercise_id="ex1", kc_id="KC001"))
        db.add(StudentMastery(student_id="s1", kc_id="KC001", mastery=initial_mastery))
        db.commit()


if __name__ == "__main__":
    unittest.main()
