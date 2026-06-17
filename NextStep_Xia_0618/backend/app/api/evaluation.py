from datetime import datetime, timezone

from fastapi import APIRouter, Query

from app.schemas.evaluation import EvaluationExportResponse

router = APIRouter()


@router.get("/evaluation/export", response_model=EvaluationExportResponse)
def export_evaluation(
    format: str = Query(default="json"),
) -> EvaluationExportResponse:
    return EvaluationExportResponse(
        format=format,
        generated_at=datetime.now(timezone.utc).isoformat(),
        records=[],
    )
