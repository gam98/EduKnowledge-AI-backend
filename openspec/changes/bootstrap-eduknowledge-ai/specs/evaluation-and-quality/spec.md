# Evaluation and Quality Specification

## Purpose
Measure and document quality honestly.

## Requirements

### Requirement: Transparent evaluation
The system MUST manage authorized datasets, cases, runs, JSON/Markdown reports, and 30+ demo domain/no-answer/injection cases; report recall@k, citation validity, groundedness heuristic, abstention, latency, and cost; label heuristic/model judgments non-objective; and test citations, isolation, permissions, ingestion, retrieval, abstention, limits, and injection resistance.

#### Scenario: Evaluation completion
- GIVEN a dataset and authorized runner
- WHEN a run completes
- THEN status, configuration, and reports persist

#### Scenario: Invalid evaluation result
- GIVEN a viewer or cited non-retrieved chunk
- WHEN a run or validation executes
- THEN it is denied or rejected
