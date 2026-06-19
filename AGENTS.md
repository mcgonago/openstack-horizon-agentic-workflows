# OpenStack Horizon Agentic Workflows

This repository contains workflow definitions for OpenStack Horizon development. Each workflow provides structured processes — skills, rules, and project-specific knowledge — that guide AI agents through Horizon tasks like code review, bug triage, and more.

All content is authored once and discovered by multiple tools through standard conventions and symlinks.

## Available Workflows

| Workflow | Description | Skills |
|---|---|---|
| horizon-review | Review Horizon Gerrit patches against project conventions, plugin-API stability, and testing requirements | `/horizon-code-review` |
| review-tracker | Track Gerrit review lifecycle — comment threads, votes, action items — with living documents | `/review-tracker` |

## Skill Prefix Table

| Prefix | Workflow |
|---|---|
| `horizon-` | horizon-review |
| `review-` | review-tracker |

## Agent Personas

| Persona | File | Expertise | Used By |
|---|---|---|---|
| Horizon Core Reviewer | `agents/horizon-core.md` | Plugin-API stability, Django/Horizon framework, OpenStack API client conventions, testing patterns | horizon-review |
| Review Tracker | `agents/review-tracker.md` | Gerrit comment analysis, thread grouping, status classification, change detection | review-tracker |

## Shared Knowledge

| File | Contents |
|---|---|
| `knowledge/horizon.md` | Horizon architecture, directory structure, plugin system, API client conventions, testing requirements, review process, commit conventions |
| `knowledge/review-tracking.md` | Gerrit REST API reference, comment data model, label/voting system, patchset lifecycle, thread ID conventions |

## Repository Structure

```
.agents/
└── skills/
    ├── horizon-code-review/       → workflows/horizon-review/.claude/skills/horizon-code-review
    └── review-tracker/            → workflows/review-tracker/.claude/skills/review-tracker
.cursor/
├── agents/
│   ├── horizon-core.md            → agents/horizon-core.md
│   └── review-tracker.md          → agents/review-tracker.md
└── rules/
    └── horizon-rules.mdc          references rules.md
agents/
├── horizon-core.md
└── review-tracker.md
knowledge/
├── horizon.md
└── review-tracking.md
workflows/
├── horizon-review/
│   ├── .ambient/
│   │   └── ambient.json
│   ├── .claude/
│   │   └── skills/
│   │       └── horizon-code-review/
│   │           └── SKILL.md
│   ├── artifacts/
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── rules.md
│   └── README.md
└── review-tracker/
    ├── .ambient/
    │   └── ambient.json
    ├── .claude/
    │   └── skills/
    │       └── review-tracker/
    │           └── SKILL.md
    ├── artifacts/
    │   └── review-tracker/
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── rules.md
    └── README.md
AGENTS.md
CLAUDE.md
README.md
```

## Design Principles

- Do not duplicate deterministic checks. If CI already enforces a rule (`tox -e pep8`, `npm run lint`), the workflow does not re-check it.
- Use in-tree docs as the source of truth. Reference Horizon's contributor documentation rather than duplicating rules here.
- Multi-tool, zero duplication. Skills, rules, and knowledge are authored once and discovered by multiple tools via symlinks.
- Human decides, agent assists. Workflows provide analysis and draft comments, but the human makes the final Gerrit vote.
