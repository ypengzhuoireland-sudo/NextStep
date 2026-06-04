from pathlib import Path
import json

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import User

USERS_PATH = Path(__file__).resolve().parents[2] / "data" / "users.json"


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    seed_users()


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
