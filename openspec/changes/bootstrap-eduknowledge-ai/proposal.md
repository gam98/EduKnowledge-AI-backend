# Proposal: Bootstrap EduKnowledge AI Backend

## Intent
Create a demo-only institutional AI assistant with grounded RAG, controlled tools, tenant isolation, and local baseline.

## Scope

### In Scope
- Bootstrap the backend **at this repository root**: `app/`, `scripts/`, `seed/`, Docker, tooling, CI, and docs. Do **not** introduce a redundant `backend/` directory.
- Deliver FastAPI, PostgreSQL/pgvector, Redis, Alembic, JWT/RBAC, and tenant-scoped APIs.
- Implement ingestion/retrieval, mockable providers, grounded LangGraph/tools, citations, abstention, observability, evaluations, demo seeds, and tests.
- Split implementation into chained, independently verifiable work units; auto-chain strategy is authorized because the expected change far exceeds 400 lines.

### Out of Scope
- Institutional, QS, proprietary, or non-demo data; affiliation claims or branding.
- Production queue/cloud storage, unrestricted SQL/URL/shell/email tools, or external side effects.
- Objective claims for heuristic or model-judged evaluation metrics.

## Capabilities

### New Capabilities
- `platform-foundation`: configuration, async persistence, migrations, Docker, CI, health, and observability.
- `identity-and-tenancy`: JWT, RBAC, organization isolation, rate limiting, and audit logging.
- `knowledge-ingestion`: validated PDF/HTML/CSV/text ingestion, embeddings, indexing, and demo documents.
- `grounded-assistant`: tenant-filtered retrieval, LangGraph RAG/tools, citations, abstention, chat, and streaming APIs.
- `program-catalog`: tenant-scoped academic-program CRUD, CSV import, structured discovery, and factual comparison.
- `evaluation-and-quality`: datasets/runs/reports, safety/citation checks, tests, and documentation.

### Modified Capabilities
None; `openspec/specs/` is empty.

## Approach
Use thin routes, typed services/repositories, and provider protocols. PostgreSQL/pgvector provides HNSW retrieval; validate answers/citations against evidence. Local providers support Docker/tests without keys; configure OpenAI, Anthropic, or Gemini when available.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `app/` | New | API, services, persistence, workflows, workers, tests |
| `seed/`, `scripts/` | New | Demo fixtures and commands |
| Root config | New | Python, Docker, Alembic, environment, CI, README |
| `openspec/` | Modified | Change artifacts and future specifications |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Broad scope/review overload | High | Auto-chain small work units, each with tests and rollback |
| Provider or infrastructure unavailable | Med | Protocols, deterministic mocks, Compose health checks |
| Unsafe/ungrounded answers | Med | RBAC, evidence-only citations, abstention, injection defenses |

## Rollback Plan
Revert the affected work unit/PR and migration; retain backups before destructive schema changes. Disable providers via environment configuration and use local mocks.

## Dependencies
- Docker/Compose, PostgreSQL 16 with pgvector, and Redis images.
- Provider keys are optional; mocks support local/test runs.

## Success Criteria
- [ ] Dockerized API runs migrations, demo seeds, health/readiness checks, and documented commands.
- [ ] All specified APIs enforce tenant/RBAC boundaries and return only validated citations or abstentions.
- [ ] Ingestion, retrieval, chat/tools, evaluation, observability, CI, and meaningful tests are delivered as chained work units.
