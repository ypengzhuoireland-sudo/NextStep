from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.kcs import KnowledgeComponentDetail, KnowledgeComponentListResponse
from app.services.kc_service import get_knowledge_component_by_code, list_knowledge_components


router = APIRouter()


@router.get("/kcs", response_model=KnowledgeComponentListResponse)
def get_kcs(db: Session = Depends(get_db)) -> KnowledgeComponentListResponse:
    return list_knowledge_components(db)


@router.get("/kcs/{code}", response_model=KnowledgeComponentDetail)
def get_kc(
    code: str,
    db: Session = Depends(get_db),
) -> KnowledgeComponentDetail:
    kc = get_knowledge_component_by_code(db, code)

    if kc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge component not found",
        )

    return kc
