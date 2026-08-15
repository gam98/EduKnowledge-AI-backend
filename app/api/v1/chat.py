import time
from collections import defaultdict, deque
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.v1.dependencies import RequestContext, current_context
from app.schemas.chat import ChatMessage, ChatResponse, Evidence
from app.workflows.rag_graph import grounded_answer

router = APIRouter(prefix="/chat", tags=["chat"])
_calls: dict[UUID, deque[float]] = defaultdict(deque)


def limit(context: RequestContext) -> None:
    now = time.monotonic()
    calls = _calls[context.user_id]
    while calls and now - calls[0] > 60:
        calls.popleft()
    if len(calls) >= 20:
        raise HTTPException(429, "Chat rate limit exceeded")
    calls.append(now)


def local_evidence(question: str, organization_id: UUID) -> list[Evidence]:
    return []


@router.post("/conversations", status_code=201)
async def conversation(context: RequestContext = Depends(current_context)):
    return {"id": str(uuid4()), "organization_id": str(context.organization_id)}


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def message(
    conversation_id: UUID, payload: ChatMessage, context: RequestContext = Depends(current_context)
):
    limit(context)
    return grounded_answer(
        payload.content, local_evidence(payload.content, context.organization_id)
    )


@router.post("/conversations/{conversation_id}/messages/stream")
async def stream(
    conversation_id: UUID, payload: ChatMessage, context: RequestContext = Depends(current_context)
):
    limit(context)
    response = grounded_answer(
        payload.content, local_evidence(payload.content, context.organization_id)
    )

    async def events():
        yield f"event: result\ndata: {response.model_dump_json()}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
