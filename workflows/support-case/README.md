# Support Case Investigation Workflow

Investigate OpenStack Horizon support cases using structured knowledge
and an AI agent persona.

## Quick Start

1. Navigate into this workflow directory:
   cd workflows/support-case/

2. Launch Claude Code:
   claude

3. Run the investigation:
   /support-case-investigation "Horizon attach-interface fails after Train to Wallaby upgrade"

## What It Does

This workflow uses the support-investigator agent persona and the
support-investigation knowledge layer to investigate support cases. It:

- Classifies the reported symptom
- Traces the code path from UI to backend
- Compares code between OpenStack releases (if upgrade-related)
- Analyzes RBAC/policy configuration (if authorization-related)
- Produces a structured investigation report

## Input

The skill accepts a symptom description or case identifier:

| Input Type             | Example                                          |
|------------------------|--------------------------------------------------|
| Free-text description  | "Horizon attach-interface fails after upgrade"   |
| Upstream bug reference | "LP#NNNNNN"                                      |
| Case identifier        | Any tracking number your organization uses       |

## Output

Generated artifacts are written to artifacts/support-case/:

- investigation_report.md -- Root cause analysis with evidence
- operator_response.md -- Operator-facing summary
- code_trace.md -- Code path analysis

## Knowledge Sources

- knowledge/support-investigation.md -- Investigation methodology
- knowledge/horizon.md -- Horizon project reference

## Agent Persona

- agents/support-investigator.md -- Senior support engineer persona

## Related

- workflows/horizon-review/ -- The code review workflow (Jan's original)
