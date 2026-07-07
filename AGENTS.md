# OpenStack Horizon Agentic Workflows

This repository contains workflow definitions for OpenStack Horizon development. Each workflow provides structured processes — skills, rules, and project-specific knowledge — that guide AI agents through Horizon tasks like code review, bug triage, and more.

All content is authored once and discovered by multiple tools through standard conventions and symlinks.

## Available Workflows

| Workflow | Description | Skills |
|---|---|---|
| horizon-review | Review Horizon Gerrit patches against project conventions, plugin-API stability, and testing requirements | `/horizon-code-review` |
| support-case | Investigate Horizon customer support cases using structured investigation methodology | `/support-case-investigation` |
| triassessment | Quick triage and assessment of Jira tickets with dependency mapping and recommendation | `/triassessment` |

## Skill Prefix Table

| Prefix | Workflow |
|---|---|
| `horizon-` | horizon-review |
| `support-` | support-case |
| `tri-` | triassessment |

## Agent Personas

| Persona | File | Expertise | Used By |
|---|---|---|---|
| Horizon Core Reviewer | `agents/horizon-core.md` | Plugin-API stability, Django/Horizon framework, OpenStack API client conventions, testing patterns | horizon-review |
| Support Case Investigator | `agents/support-investigator.md` | OpenStack upgrades, Horizon architecture, RBAC/policy, cross-service dependencies, must-gather analysis | support-case |

## Shared Knowledge

| File | Contents |
|---|---|
| `knowledge/horizon.md` | Horizon architecture, directory structure, plugin system, API client conventions, testing requirements, review process, commit conventions |
| `knowledge/support-investigation.md` | Support case investigation methodology, symptom classification, code tracing, version regression, RBAC analysis, failure patterns |

## Repository Structure

```
.agents/
└── skills/
    ├── horizon-code-review/           → workflows/horizon-review/.claude/skills/horizon-code-review
    ├── support-case-investigation/    → workflows/support-case/.claude/skills/support-case-investigation
    └── triassessment/                 → workflows/triassessment/.claude/skills/triassessment
.cursor/
├── agents/
│   ├── horizon-core.md               → agents/horizon-core.md
│   └── support-investigator.md       → agents/support-investigator.md
└── rules/
    ├── horizon-rules.mdc             references rules.md
    └── support-rules.mdc             support case investigation rules
agents/
├── horizon-core.md
└── support-investigator.md
knowledge/
├── horizon.md
└── support-investigation.md
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
└── support-case/
    ├── .ambient/
    │   └── ambient.json
    ├── .claude/
    │   └── skills/
    │       └── support-case-investigation/
    │           └── SKILL.md
    ├── artifacts/
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
