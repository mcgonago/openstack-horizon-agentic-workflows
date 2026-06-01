---
name: support-case-investigation
description: Investigate OpenStack Horizon customer support cases using structured knowledge
---

# Support Case Investigation

Investigate a support case related to OpenStack Horizon
(the OpenStack Dashboard service).

## Usage

/support-case-investigation <case-number-or-description>

## Examples

/support-case-investigation "Horizon attach-interface fails after Train to Wallaby upgrade"
/support-case-investigation "Unable to retrieve networks after upgrade"
/support-case-investigation "Not Authorized error on admin actions"

## What This Skill Does

1. Reads the support investigation knowledge layer
   (knowledge/support-investigation.md)
2. Classifies the symptom using the taxonomy
3. Traces the code path from UI action to backend API call
4. Performs version comparison if upgrade-related
5. Analyzes RBAC/policy if authorization-related
6. Generates a structured investigation report

## Output

Files are written to artifacts/support-case/:

- investigation_report.md -- Root cause analysis with evidence
- customer_response.md -- Customer-facing summary with next steps
- code_trace.md -- Detailed code path analysis

## Knowledge Sources

- knowledge/support-investigation.md -- Investigation methodology,
  symptom classification, code tracing, version maps
- knowledge/horizon.md -- Horizon project reference (reused from
  the horizon-review workflow)

## Agent Persona

Uses the support-investigator persona defined in
agents/support-investigator.md.

## Rules

Follow the behavioral rules in rules.md within this workflow directory.
