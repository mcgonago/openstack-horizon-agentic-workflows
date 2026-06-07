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

# Re-run analysis only (no code changes, no PR)
/feature tag=pqc OSPRH-28889 --artifacts-only

# Full re-run in isolated worktree (implement + compare vs PR)
/feature tag=pqc OSPRH-28889 --dry-run

# Clean-room: implement without seeing existing PRs, then compare
/feature tag=pqc OSPRH-28889 --dry-run --blind

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
4. Code Change Requirements (intent + constraints)
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

## Safety Guardrails

This repo includes a `.claude/settings.json` at the repository root
with a `deny` list that blocks remote-mutating commands:

- `git push`
- `gh pr create`, `gh pr close`, `gh pr comment`, `gh pr merge`, `gh pr edit`
- `gh issue create`, `gh issue close`, `gh issue comment`

**These deny rules override any allow list**, including permissive
"do not ask for permissions" sessions. This is intentional — it
prevents the AI from autonomously pushing code or creating PRs.

The skill also includes an idempotency check (Step 1.5) that detects
existing PRs and branches for a ticket before attempting to implement.
If prior work exists, the skill reports status and stops.

**Do not weaken or remove these guardrails.** If you need to push
or create a PR, the skill will present the commands for you to run
manually.

Two read-only re-run modes are available:

- **`--artifacts-only`**: Re-run analysis without modifying any files.
  Compares knowledge-derived changes against actual PR/branch state.
  Useful for investigation dashboards and cross-run comparisons.

- **`--dry-run`**: Full implementation in an isolated git worktree,
  then compare the implemented changes against the existing PR.
  Useful for verifying that the skill reproduces correct code changes.
  The worktree is automatically cleaned up after artifacts are generated.

- **`--dry-run --blind`**: Same as `--dry-run` but with an information
  barrier: the AI cannot see existing PRs, branches, or reference
  implementations until AFTER implementation is complete. This ensures
  the AI derives the code independently from requirements alone.
  The assessment discloses that `--blind` mode was used.

## Related Workflows

- `horizon-review/` -- Code review (Jan Jasek)
- `support-case/` -- Support investigation (AI Jam #6)
