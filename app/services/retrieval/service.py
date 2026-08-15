from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Evidence:
    chunk_id: UUID
    source_document_id: UUID
    organization_id: UUID
    content: str
    category: str
    language: str
    embedding: list[float]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


def retrieve(
    query: list[float],
    evidence: list[Evidence],
    organization_id: UUID,
    top_k: int = 5,
    minimum_score: float = 0.2,
    category: str | None = None,
    language: str | None = None,
) -> list[tuple[Evidence, float]]:
    filtered = [
        item
        for item in evidence
        if item.organization_id == organization_id
        and (category is None or item.category == category)
        and (language is None or item.language == language)
    ]
    return [
        (item, score)
        for item, score in sorted(
            ((item, cosine(query, item.embedding)) for item in filtered),
            key=lambda pair: pair[1],
            reverse=True,
        )[:top_k]
        if score >= minimum_score
    ]
