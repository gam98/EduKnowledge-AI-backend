# Program Catalog Specification

## Purpose
Manage and discover tenant academic-program facts.

## Requirements

### Requirement: Tenant program catalog
The system MUST offer role-authorized tenant CRUD and validated CSV import for structured program facts, and MUST filter or compare two to four accessible programs using stored facts only.

#### Scenario: Valid management
- GIVEN an authorized editor
- WHEN valid program data is submitted
- THEN it persists only in that organization

#### Scenario: Invalid or inaccessible request
- GIVEN invalid CSV data or another tenant ID
- WHEN processed
- THEN no unsafe partial write or data disclosure occurs
