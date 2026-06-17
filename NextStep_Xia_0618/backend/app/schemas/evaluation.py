from typing import Any

from pydantic import BaseModel


class EvaluationExportResponse(BaseModel):
    format: str
    generated_at: str
    records: list[dict[str, Any]]
