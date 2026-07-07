---
name: triassessment
description: Quick triage and assessment of Jira tickets with dependency mapping and recommendation
---

# Triage Assessment

Perform a quick triage and assessment of a Jira ticket, producing a
structured recommendation for stakeholder communication.

## Usage

/triassessment <TICKET-ID> [--update-artifact-dashboard] [--deep]

## Examples

/triassessment OSPRH-27628
/triassessment OSPRH-27628 --update-artifact-dashboard
/triassessment OSPRH-27628 --deep --update-artifact-dashboard

## Process

### Step 0: Parse Input

Extract the ticket ID from the arguments. Detect flags:
- `--update-artifact-dashboard` → set PUBLISH=true
- `--deep` → set DEEP=true

### Step 1: Fetch Ticket Details

Use the Jira MCP tool to fetch the ticket:
- Tool: `mcp__user-jiraMcp__jira_get_issue` with `issue_key = <TICKET-ID>`

Extract: summary, description, status, type, priority, labels, components,
fix versions, reporter, assignee, parent epic, linked tickets.

### Step 2: Fetch Related Tickets

For the parent epic and all linked tickets mentioned in the description,
fetch their details too using the same Jira MCP tool.

Build:
- Ticket hierarchy (epic → stories)
- Blocking chain (what blocks what)
- Cross-team dependencies

Cap at 10 related ticket fetches. Note truncation if more exist.

### Step 3: Cross-Reference Knowledge Bases

Scan the ticket description for keywords and load matching knowledge:

| Match | Knowledge Base |
|-------|---------------|
| PQC, quantum, TLS, kRSA, ML-KEM, post-quantum, cipher | `../../knowledge/feature-pqc.md` |
| Horizon, dashboard, panel, Angular, Django | `../../knowledge/horizon.md` |
| support, upgrade, regression, must-gather | `../../knowledge/support-investigation.md` |
| review, gerrit, comment, tracker | `../../knowledge/review-tracking.md` |

Read matching knowledge files before generating the assessment.

### Step 4: Deep Analysis (if --deep)

If DEEP=true, additionally:
- Search for related PRs on GitHub/OpenDev
- Identify code paths affected
- Map cross-team dependencies with contact info
- Check if existing PRs address this ticket

### Step 5: Generate Triage Assessment

Write `artifacts/triassessment/triage_assessment.md` with sections:

1. **Ticket Summary** — Key/value table of ticket fields
2. **Technical Context** — Plain language explanation of the ask
3. **Dependencies & Blockers** — Table of related tickets and their status
4. **Impact Analysis** — What happens if we proceed vs close
5. **Recommendation** — Verdict (CLOSE/IMPLEMENT/DEFER/ESCALATE), confidence, rationale
6. **Talking Points** — Bullet points for stakeholder response
7. **Deep Analysis** — (only if --deep) Extended code/PR references

Include a footer: `Generated: <timestamp> | Skill: /triassessment | Model: <model-id>`

**Auto-linkable references:** When citing knowledge files, use the format:
- `(per feature-pqc.md, Section 2)` — auto-links to GitHub knowledge file
- `(from horizon.md)` — auto-links without section
- Jira tickets (`OSPRH-12345`, `RHOSSTRAT-123`) — auto-link
- Patterns: `(per|from|see|via) <filename>.md[, Section N]`

### Step 6: Generate Related Tickets Summary

Write `artifacts/triassessment/related_tickets.md` with sections:

1. **Ticket Hierarchy** — Table: Level, Ticket, Title, Status, Owner
2. **Blocking Chain** — Visual representation of blocking relationships
3. **Cross-Team Dependencies** — Table: Dependency, Team, Status, Notes
4. **Resolution Paths** — For blocked tickets, list possible paths forward

### Step 7: Publish to Dashboard (if --update-artifact-dashboard)

If PUBLISH=true, inform the user to ingest artifacts:

```
Artifacts written to: artifacts/triassessment/
Case ID: TRIASSESSMENT-<TICKET-ID>

To ingest into dashboard:
cd /home/omcgonag/Work/mymcp/workspace/iproject/projects/ioshaworkflow/repo/ioshaworkflow
python scripts/ingest_artifacts.py \
  --case-id TRIASSESSMENT-<TICKET-ID> \
  --skill triassessment \
  --title "<ticket-summary>" \
  --summary "Triage assessment of <TICKET-ID>" \
  --source-dir ../openstack-horizon-agentic-workflows/workflows/triassessment/artifacts/triassessment/
```

Or use the dashboard "Ingest Artifacts" button at:
http://10.0.151.101:8072/investigations/TRIASSESSMENT-<TICKET-ID>

## Output

Files written to artifacts/triassessment/:

- triage_assessment.md — Structured assessment with recommendation
- related_tickets.md — Related ticket hierarchy and dependencies

## Knowledge Sources

Loaded conditionally based on ticket content:
- knowledge/feature-pqc.md — PQC compliance context
- knowledge/horizon.md — Horizon project reference
- knowledge/support-investigation.md — Support investigation patterns

## Rules

Follow the behavioral rules in rules.md within this workflow directory.
