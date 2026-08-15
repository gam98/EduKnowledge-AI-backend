# Knowledge Ingestion Specification

## Purpose
Create trustworthy tenant-scoped knowledge.

## Requirements

### Requirement: Validated ingestion
The system MUST validate PDF, allow-listed HTML, CSV, and manual text; asynchronously track status, extract/normalize/chunk, retain provenance, embed/index, and safely record failures with telemetry/audits.

#### Scenario: Indexed source
- GIVEN a valid tenant source
- WHEN processing completes
- THEN chunks retain source, category, language, tenant, and index metadata

#### Scenario: Rejected source
- GIVEN a disallowed URL, type, or size
- WHEN submitted
- THEN it is rejected before processing

### Requirement: Demo fixtures
The system MUST seed labeled demo admissions, scholarships, regulations, and 15+ programs.

#### Scenario: Seed
- GIVEN an empty local environment
- WHEN seeding runs
- THEN only demo/public-style records are created
