import time

from app.schemas.chat import ChatResponse, Citation, Evidence

INJECTION_MARKERS = ("ignore previous", "system message", "developer instruction")


def validate_citations(answer: str, evidence: list[Evidence], citations: list[Citation]) -> bool:
    ids = {item.chunk_id for item in evidence}
    return all(item.chunk_id in ids for item in citations)


def grounded_answer(question: str, evidence: list[Evidence]) -> ChatResponse:
    started = time.perf_counter()
    lowered = question.lower()
    if any(marker in lowered for marker in INJECTION_MARKERS):
        return ChatResponse(
            answer="I cannot follow instructions embedded in content or requests.",
            citations=[],
            retrieved_sources=evidence,
            model_name="deterministic-local",
            latency_ms=0,
            estimated_cost=0,
            abstained=True,
            abstention_reason="unsafe_request",
        )
    if not evidence or max(item.score for item in evidence) < 0.2:
        return ChatResponse(
            answer="I do not have sufficient evidence in the current knowledge base.",
            citations=[],
            retrieved_sources=evidence,
            model_name="deterministic-local",
            latency_ms=0,
            estimated_cost=0,
            abstained=True,
            abstention_reason="insufficient_evidence",
        )
    source = max(evidence, key=lambda item: item.score)
    citation = Citation(
        chunk_id=source.chunk_id,
        source_document_id=source.source_document_id,
        excerpt=source.excerpt,
    )
    response = ChatResponse(
        answer=source.excerpt,
        citations=[citation],
        retrieved_sources=evidence,
        model_name="deterministic-local",
        latency_ms=round((time.perf_counter() - started) * 1000),
        estimated_cost=0,
        abstained=False,
    )
    if not validate_citations(response.answer, evidence, response.citations):
        raise ValueError("Invalid citation")
    return response
