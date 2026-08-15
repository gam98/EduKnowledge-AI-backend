# Grounded Assistant Specification

## Purpose
Answer safely from authorized evidence and controlled tools.

## Requirements

### Requirement: Grounded assistant
The system MUST run bounded validate/classify/retrieve/tool/generate/validate/persist steps; cite only retrieved chunks or tool facts; authorize typed knowledge/program tools and confirmation-gated drafts; treat documents as untrusted; and MAY stream validated SSE results.

#### Scenario: Supported question
- GIVEN authorized relevant evidence
- WHEN a message is submitted
- THEN answer, citations, sources, tool summary, latency, and cost are returned

#### Scenario: No evidence or injection
- GIVEN weak evidence or source instructions
- WHEN processed
- THEN it abstains safely or treats text only as evidence
