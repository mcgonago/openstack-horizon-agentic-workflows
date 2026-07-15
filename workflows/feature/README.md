# Feature Implementation Workflow (Tag-Based)

A tag-based feature implementation workflow for OpenStack operators.
Each domain (PQC compliance, logging, RBAC, etc.) is a "tag" with
its own knowledge file. The workflow framework is shared.

## Quick Start

```bash
# Navigate into the workflow
cd workflows/feature

# Launch Claude Code
claude

# Run with an explicit tag
/feature tag=pqc OSPRH-28889

# Or let the AI infer the tag from a ticket key
/feature OSPRH-28889

# List available tags
/feature --tags

# Check status for a tag
/feature tag=pqc --status
```

## Available Tags

| Tag | Knowledge File | Domain |
|-----|---------------|--------|
| pqc | knowledge/feature-pqc.md | PQC/TLS compliance for horizon-operator |

## How Tags Work

Each tag has a dedicated knowledge file at `knowledge/feature-<tag>.md`
following a standardized 7-section structure:

1. Domain Fundamentals
2. Scope (tickets, routing, tiers)
3. Target Repository
4. Code Change Catalog (BEFORE/AFTER)
5. Architecture Patterns
6. Validation Commands
7. Delivery Pattern

The SKILL.md, agent persona, and rules are SHARED across all tags.
Adding a new domain = adding ONE knowledge file.

## Adding a New Tag

1. Create `knowledge/feature-<tag>.md` following the 7-section standard
2. Done. The /feature skill discovers it automatically.

## Multi-Tool Support

This workflow works with:
- **Claude Code**: `cd workflows/feature && claude`
- **Cursor**: Skills auto-discovered via `.agents/skills/feature/`
- **ACP**: Configure via `.ambient/ambient.json`

## Related Workflows

- `horizon-review/` -- Code review (Jan Jasek)
- `support-case/` -- Support investigation (AI Jam #6)
