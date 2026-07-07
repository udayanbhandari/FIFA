"""FastAPI Transport Router for AI-driven multilingual assistance."""


from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request

from app.models import AssistantResponse, FanAssistantQuery, FanQueryRecord
from app.assistant.gemini import get_fan_assistance
from app.deps import get_repository
from app.rate_limit import limiter
from app.repository.base import FanQueryRepository

router = APIRouter(prefix="/assist", tags=["assistant"])


@router.post("", response_model=AssistantResponse)
@limiter.limit("10/minute")
async def ask_assistant(
    request: Request,
    query: FanAssistantQuery,
    repo: FanQueryRepository = Depends(get_repository),
) -> AssistantResponse:
    """Answer fan queries using Gemini with automated logging and rate limits."""
    # Obtain assistant answer (utilizes Gemini with grace fallback)
    response = await get_fan_assistance(query)

    # Log record to repository for operators analytical reporting
    record = FanQueryRecord(
        device_id=query.device_id,
        question=query.question,
        answer=response.answer,
        source=response.source,
        language=query.language,
        created_at=datetime.now(timezone.utc),
    )
    await repo.async_add(record)

    return response


@router.get("/history/{device_id}", response_model=list[FanQueryRecord])
async def get_history(
    device_id: str,
    repo: FanQueryRepository = Depends(get_repository),
) -> list[FanQueryRecord]:
    """Retrieve chat history snapshot associated with anonymous device ID."""
    return await repo.async_list_by_device(device_id)
