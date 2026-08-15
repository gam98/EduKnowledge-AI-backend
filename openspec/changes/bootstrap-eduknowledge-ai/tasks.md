# Tasks: Bootstrap EduKnowledge AI Backend

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | 2,000–3,200 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 → PR 5 |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|---|---|---|---|
| 1 | Runnable foundation | PR 1 | Config, app factory, health, tests, Compose. |
| 2 | Identity and catalog | PR 2 | After PR 1; tenant persistence, JWT/RBAC, programs. |
| 3 | Trusted knowledge | PR 3 | After PR 2; ingestion, embeddings, retrieval. |
| 4 | Grounded chat | PR 4 | After PR 3; workflow, citations, SSE. |
| 5 | Quality and demo | PR 5 | After PR 4; evaluations, seeds, CI/docs. |

## Phase 1: Runnable Foundation (PR 1)

- [x] 1.1 Create pyproject.toml, .env.example, Makefile, and .pre-commit-config.yaml with FastAPI, async SQLAlchemy, Alembic, pytest, Ruff, and mypy.
- [x] 1.2 Create app/main.py, app/core/{config,logging}.py, and app/api/v1/health.py with typed settings, app factory, logs, /health, and dependency-aware /ready.
- [x] 1.3 Create app/db/session.py, Dockerfile, and docker-compose.yml for PostgreSQL/pgvector and Redis; readiness safely reports unavailable dependencies.
- [x] 1.4 Add app/tests/test_health.py for healthy and failed readiness; document local commands in README.md.

## Phase 2: Tenant Identity and Catalog (PR 2)

- [x] 2.1 Add Alembic baseline, tenant/user/audit/program models, and tenant-scoped repositories in app/db/.
- [x] 2.2 Implement JWT/password/RBAC dependencies and auth/program routes in app/api/v1/; all lookups are organization-scoped.
- [x] 2.3 Add CSV validation/import and factual 2–4 program comparison services in app/services/.
- [x] 2.4 Test denied roles, cross-tenant access, invalid CSV atomicity, and factual comparison in app/tests/.

## Phase 3: Trusted Knowledge (PR 3)

- [x] 3.1 Add source/chunk/job models and reversible pgvector HNSW migration with tenant filters.
- [x] 3.2 Implement allow-listed URL and PDF/CSV/text validation, extraction, chunking, provenance, and local job/provider interfaces.
- [x] 3.3 Implement deterministic embeddings and tenant-filtered retrieval repositories/services.
- [x] 3.4 Test rejected sources, chunk metadata, retrieval isolation, and local-provider behavior.

## Phase 4: Grounded Assistant (PR 4)

- [x] 4.1 Define chat/evidence/citation/tool schemas and bounded workflow in app/workflows/ using only typed allow-listed tools.
- [x] 4.2 Implement chat and optional SSE routes with evidence-derived citations, abstention, persistence, rate limits, and telemetry.
- [x] 4.3 Test supported answers, low-evidence abstention, invalid citations, injection text, tool limits, and tenant isolation.

## Phase 5: Evaluation, Demo, and Hardening (PR 5)

- [x] 5.1 Add labeled demo documents, 15+ programs, and 30+ evaluation cases under seed/; no proprietary data.
- [x] 5.2 Implement authorized evaluation datasets/runs and JSON/Markdown reports for recall@k, citation validity, groundedness, abstention, latency, and cost.
- [x] 5.3 Add .github/workflows/ci.yml, integration/Compose checks, and README architecture, threat-model, limitations, and evaluation guidance.
