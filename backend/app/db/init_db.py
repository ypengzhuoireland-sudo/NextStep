from pathlib import Path
import json
from typing import Any

from sqlalchemy import delete, or_, select, text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.bkt_parameters import KnowledgeComponentBKTParameters
from app.models.exercise import Exercise, ExerciseKnowledgeComponent
from app.models.knowledge_component import KnowledgeComponent
from app.models.mastery_event import MasteryEvent
from app.models.student_mastery import StudentMastery
from app.models.submission import Submission
from app.models.user import User
from app.services.bkt_service import DEFAULT_BKT_PARAMETERS

USERS_PATH = Path(__file__).resolve().parents[2] / "seeds" / "users_seed.json"
EXERCISE_BANK_PATH = Path(__file__).resolve().parents[2] / "seeds" / "p09_python_exercise_bank.json"


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_exercise_schema()
    seed_users()
    seed_exercise_bank()


def ensure_exercise_schema() -> None:
    statements = [
        "ALTER TABLE knowledge_components ADD COLUMN IF NOT EXISTS short_name VARCHAR(80)",
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS type VARCHAR(50) NOT NULL DEFAULT 'coding'",
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS estimated_minutes INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS function_name VARCHAR(200) NOT NULL DEFAULT ''",
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS hidden_tests BOOLEAN NOT NULL DEFAULT false",
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS hints JSON NOT NULL DEFAULT '[]'::json",
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS solution TEXT",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def seed_users() -> None:
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        seed_data = json.load(f)

    db = SessionLocal()

    try:
        for user_data in seed_data:
            user = db.query(User).filter(User.username == user_data["username"]).one_or_none()

            if user is None:
                db.add(
                    User(
                        student_id=user_data["student_id"],
                        username=user_data["username"],
                        name=user_data["name"],
                        role=user_data["role"],
                        password_salt=user_data["password_salt"],
                        password_hash=user_data["password_hash"],
                    )
                )
                continue

            user.student_id = user_data["student_id"]
            user.name = user_data["name"]
            user.role = user_data["role"]
            user.password_salt = user_data["password_salt"]
            user.password_hash = user_data["password_hash"]
            user.is_active = True

        db.commit()
    finally:
        db.close()


def seed_exercise_bank() -> None:
    with open(EXERCISE_BANK_PATH, "r", encoding="utf-8") as file:
        exercise_bank = json.load(file)

    kc_items = exercise_bank["kc_map"]
    exercise_items = exercise_bank["exercises"]
    kc_ids = {item["kc_id"] for item in kc_items}
    exercise_ids = {item["exercise_id"] for item in exercise_items}

    validate_exercise_bank(kc_ids, exercise_items)

    db = SessionLocal()

    try:
        delete_stale_exercise_seed_rows(db, exercise_ids, kc_ids)
        upsert_knowledge_components(db, kc_items)
        db.flush()
        seed_default_bkt_parameters(db, kc_ids)
        db.flush()
        upsert_exercises(db, exercise_items)
        db.flush()
        seed_default_mastery(db, kc_ids)
        db.commit()
    finally:
        db.close()


def validate_exercise_bank(kc_ids: set[str], exercise_items: list[dict[str, Any]]) -> None:
    missing_kc_refs = sorted(
        {
            kc_id
            for exercise in exercise_items
            for kc_id in exercise["kc_tags"]
            if kc_id not in kc_ids
        }
    )

    if missing_kc_refs:
        raise ValueError(f"Exercise bank references unknown KC ids: {missing_kc_refs}")


def delete_stale_exercise_seed_rows(
    db: Session,
    exercise_ids: set[str],
    kc_ids: set[str],
) -> None:
    db.execute(
        delete(MasteryEvent).where(
            or_(
                MasteryEvent.exercise_id.not_in(exercise_ids),
                MasteryEvent.kc_id.not_in(kc_ids),
            )
        )
    )
    db.execute(
        delete(ExerciseKnowledgeComponent).where(
            ExerciseKnowledgeComponent.exercise_id.not_in(exercise_ids)
        )
    )
    db.execute(delete(Exercise).where(Exercise.id.not_in(exercise_ids)))
    db.execute(delete(StudentMastery).where(StudentMastery.kc_id.not_in(kc_ids)))
    db.execute(
        delete(KnowledgeComponentBKTParameters).where(
            KnowledgeComponentBKTParameters.kc_id.not_in(kc_ids)
        )
    )
    db.execute(delete(KnowledgeComponent).where(KnowledgeComponent.id.not_in(kc_ids)))


def upsert_knowledge_components(db: Session, kc_items: list[dict[str, Any]]) -> None:
    for kc_data in kc_items:
        kc = db.get(KnowledgeComponent, kc_data["kc_id"])

        if kc is None:
            kc = KnowledgeComponent(id=kc_data["kc_id"], name=kc_data["kc_name"])
            db.add(kc)

        kc.name = kc_data["kc_name"]
        kc.short_name = kc_data.get("short_name")
        kc.description = kc_data.get("description")


def seed_default_bkt_parameters(db: Session, kc_ids: set[str]) -> None:
    for kc_id in sorted(kc_ids):
        params = db.get(KnowledgeComponentBKTParameters, kc_id)

        if params is None:
            db.add(
                KnowledgeComponentBKTParameters(
                    kc_id=kc_id,
                    prior=DEFAULT_BKT_PARAMETERS.prior,
                    learn=DEFAULT_BKT_PARAMETERS.learn,
                    guess=DEFAULT_BKT_PARAMETERS.guess,
                    slip=DEFAULT_BKT_PARAMETERS.slip,
                )
            )


def upsert_exercises(db: Session, exercise_items: list[dict[str, Any]]) -> None:
    for exercise_data in exercise_items:
        kc_tags = exercise_data["kc_tags"]
        primary_kc = kc_tags[0]
        exercise = db.get(Exercise, exercise_data["exercise_id"])

        if exercise is None:
            exercise = Exercise(id=exercise_data["exercise_id"], kc_id=primary_kc)
            db.add(exercise)

        exercise.type = exercise_data["type"]
        exercise.title = exercise_data["title"]
        exercise.kc_id = primary_kc
        exercise.difficulty = exercise_data["difficulty"]
        exercise.estimated_minutes = exercise_data["estimated_minutes"]
        exercise.status = "ready"
        exercise.description = exercise_data["prompt"]
        exercise.function_name = exercise_data["function_name"]
        exercise.starter_code = exercise_data["starter_code"]
        exercise.test_cases = exercise_data["test_cases"]
        exercise.hidden_tests = exercise_data["hidden_tests"]
        exercise.hints = exercise_data["hints"]
        exercise.solution = exercise_data.get("solution")

        db.execute(
            delete(ExerciseKnowledgeComponent).where(
                ExerciseKnowledgeComponent.exercise_id == exercise_data["exercise_id"]
            )
        )

        for kc_id in kc_tags:
            db.add(
                ExerciseKnowledgeComponent(
                    exercise_id=exercise_data["exercise_id"],
                    kc_id=kc_id,
                )
            )


def seed_default_mastery(db: Session, kc_ids: set[str]) -> None:
    student_ids = db.scalars(
        select(User.student_id).where(User.is_active.is_(True)).order_by(User.student_id)
    ).all()

    for student_id in student_ids:
        for kc_id in sorted(kc_ids):
            mastery = db.get(StudentMastery, (student_id, kc_id))

            if mastery is None:
                db.add(
                    StudentMastery(
                        student_id=student_id,
                        kc_id=kc_id,
                        mastery=DEFAULT_BKT_PARAMETERS.prior,
                    )
                )
