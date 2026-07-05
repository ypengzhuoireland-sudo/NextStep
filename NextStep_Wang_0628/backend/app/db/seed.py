import json
from pathlib import Path
from typing import Any


BACKEND_DIR = Path(__file__).resolve().parents[2]
SEEDS_DIR = BACKEND_DIR / "seeds"


# Load a JSON seed file used to initialize or mock backend data during MVP development.
def load_seed_json(filename: str) -> list[dict[str, Any]]:
    path = SEEDS_DIR / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
