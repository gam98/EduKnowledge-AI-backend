from uuid import UUID

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    chunk_id: UUID
    source_document_id: UUID
    title: str
    excerpt: str
    score: float
    category: str
    source_url_or_path: str | None = None


class Citation(BaseModel):
    chunk_id: UUID
    source_document_id: UUID
    excerpt: str


class ChatMessage(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieved_sources: list[Evidence]
    tool_summary: list[str] = []
    model_name: str
    latency_ms: int
    estimated_cost: float
    abstained: bool
    abstention_reason: str | None = None
