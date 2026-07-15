# Triassessment Workflow

Quick triage and assessment of Jira tickets.

## Usage

```
/triassessment <TICKET-ID> [--recheck] [--update-artifact-dashboard] [--deep]
```

**Flags:**
- `--recheck` - Run a fresh assessment on an existing ticket (creates a new run)
- `--update-artifact-dashboard` - Publish artifacts to ioshaworkflow dashboard
- `--deep` - Perform deeper analysis with additional context

## What It Does

1. Fetches Jira ticket details and related tickets
2. Cross-references relevant knowledge bases
3. Generates a structured triage assessment with recommendation
4. Optionally publishes to the ioshaworkflow dashboard

## Artifacts

| Artifact | Description |
|----------|-------------|
| `triage_assessment.md` | Context, dependencies, impact analysis, recommendation, talking points |
| `related_tickets.md` | Ticket hierarchy, blocking chains, cross-team dependencies |

## Dashboard

When published, artifacts appear at:
`http://10.0.151.101:8072/investigations/TRIASSESSMENT-<TICKET-ID>`
