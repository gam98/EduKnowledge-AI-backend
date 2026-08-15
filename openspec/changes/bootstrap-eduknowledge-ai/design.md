# Design: Bootstrap EduKnowledge AI Backend

## Technical Approach
Build the empty repository root as a modular FastAPI service: thin `/api/v1` routes compose typed schemas, services, and repositories through FastAPI dependencies. SQLAlchemy async models/migrations own persistent state; PostgreSQL/pgvector performs tenant-filtered HNSW retrieval. All providers (LLM, embeddings, storage, tracing) are protocols with deterministic local implementations, so Docker and tests work without keys. Implement in auto-chained slices: foundation → identity/catalog → ingestion/retrieval → grounded chat → evaluation/hardening.

## Architecture Decisions

| Decision | Alternatives considered | Choice and rationale |
|---|---|---|
| Root layout | Prompt's nested `backend/`; flat root | Use `app/`, `scripts/`, `seed/` at repository root, because the approved proposal explicitly corrects the monorepo example and prevents a redundant backend directory. |
| Boundaries | Fat routes/ORM access; framework-bound domain | Routes call services; repositories isolate SQLAlchemy; provider protocols isolate external APIs. This follows config rules and makes deterministic tests possible. |
| Tenant enforcement | Filter only at route level | Carry `organization_id` in authenticated context and require it in every repository query/write. Database FKs/indexes support it; services never accept an unscoped lookup. |
| Grounding | Prompt-only citations | Citation objects are derived only from retrieved evidence/tool results and validated before persistence/response; low confidence yields abstention. |
| Background work | Production queue now | Define an ingestion job interface and use FastAPI/local execution initially; defer queue adapters to later deployment work. |
| Provider selection | Require cloud keys | Settings choose OpenAI/Anthropic/Gemini adapters or deterministic local LLM/embedding adapters, preserving offline Docker/test behavior. |

## Data Flow

```
HTTP request → auth dependency → role/tenant context → route → service → repository → PostgreSQL/Redis
                                                     └→ provider protocol → local or configured adapter
Upload/URL/text → validator/storage → extractor → normalizer/chunker → embeddings → chunks + HNSW index
Chat → validate/classify → tenant-filtered retrieval ─┬→ catalog tools (allow-listed)
       → grounded generation → citation/safety validation → messages, metrics, response/SSE
```

Documents are treated as untrusted data: extraction text is evidence only, never workflow instructions. URL ingestion accepts only configured allow-listed domains; tool schemas prohibit SQL, shell, arbitrary fetching, and side effects.

## File Changes

| File | Action | Description |
|---|---|---|
| `pyproject.toml`, `.pre-commit-config.yaml`, `.env.example`, `Makefile` | Create | Python/tooling/settings contract and repeatable commands. |
| `app/main.py`, `app/api/v1/`, `app/core/` | Create | App factory, versioned routing, dependencies, security, logging, limits, observability. |
| `app/db/{base,session}.py`, `app/db/models/`, `app/db/repositories/`, `alembic/`, `alembic.ini` | Create | Async persistence, tenant-scoped models/repositories, migrations, pgvector indexes. |
| `app/schemas/`, `app/services/`, `app/workflows/`, `app/workers/` | Create | Typed contracts, domain services, adapters, RAG graph, local ingestion jobs. |
| `app/tests/`, `seed/`, `scripts/` | Create | Unit/integration coverage, explicitly demo data, seed/evaluation commands. |
| `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `README.md` | Create | Local stack, CI, operational/security/evaluation documentation. |

## Interfaces / Contracts

```python
class RequestContext(BaseModel):
    user_id: UUID | None
    organization_id: UUID
    role: Role

class Evidence(BaseModel):
    chunk_id: UUID; source_document_id: UUID; title: str
    excerpt: str; score: float; source_url_or_path: str | None; category: str

class EmbeddingsProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
class LLMProvider(Protocol):
    async def generate_grounded(self, request: GroundedPrompt) -> ModelResult: ...
class TraceAdapter(Protocol):
    def span(self, name: str, **attributes: object) -> ContextManager: ...
```

`ChatResponse` returns answer, citations, retrieved sources, allowed-tool summary, model metadata, latency/cost, and `abstained` plus nullable reason. Tool input/output use Pydantic models and receive `RequestContext`; program comparison permits only 2–4 IDs.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | chunking, filters, permissions, citation validation, abstention, tool schemas, injection resistance | deterministic adapters and pure services. |
| Integration | auth, tenant boundaries, ingestion, retrieval, programs, chat/rate limits | async httpx client plus documented PostgreSQL/Redis test strategy. |
| System | Compose health/readiness, migration/seed path, CI build | Make targets and GitHub Actions; measure core-service coverage once runner exists. |

## Migration / Rollout
No migration required before the first slice. Create Alembic baseline early; each later schema slice adds a reversible migration. Compose health checks gate API startup; local providers remain default. Roll back a slice by reverting its code and Alembic revision after backing up affected data.

## Open Questions
- [ ] Confirm preferred pgvector embedding dimension/default local embedding strategy before the retrieval migration; make it a validated setting.
- [ ] Decide whether SSE uses native `StreamingResponse` only or a future broker-backed resume mechanism (initial slice uses native SSE).
