from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.db.init_db import init_db


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
