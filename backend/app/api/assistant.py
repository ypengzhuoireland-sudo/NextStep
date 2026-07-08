from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.knowledge_component import KnowledgeComponent
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.services.ai.assistant_intent_service import parse_assistant_intent
from app.services.assistant_service import build_assistant_recommendation
from app.services.student_auth_service import get_user_model_from_token


router = APIRouter(tags=["assistant"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/assistant/chat", response_model=AssistantChatResponse)
def chat_with_study_assistant(
    request: AssistantChatRequest,
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AssistantChatResponse:
    """Authenticate the student and return one assistant exercise recommendation."""
    if auth_credentials is None:
        _raise_unauthorized("Missing Authorization header")

    user = get_user_model_from_token(db, auth_credentials.credentials)
    if user is None:
        _raise_unauthorized("Invalid or expired student token")

    # The intent parser needs the live KC map so it cannot return stale KC codes.
    available_kcs = dict(
        db.execute(
            select(KnowledgeComponent.id, KnowledgeComponent.name)
            .order_by(KnowledgeComponent.id)
        ).all()
    )
    intent_result = parse_assistant_intent(
        message=request.message,
        available_kcs=available_kcs,
    )

    return build_assistant_recommendation(
        db,
        student_id=user.student_id,
        request=request,
        intent_result=intent_result,
    )


def _raise_unauthorized(detail: str) -> NoReturn:
    """Raise one consistent Bearer authentication response for this router."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
