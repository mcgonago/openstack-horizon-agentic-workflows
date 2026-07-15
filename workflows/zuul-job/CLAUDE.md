# Zuul Job Analyzer Workflow

This workflow analyzes Zuul CI build failures for OpenDev Gerrit reviews.

## Available Skills

- `/zuul-job` — Analyze Zuul CI failures, classify errors, recommend action

## Agents

See AGENTS.md for the zuul-analyst persona.

## Knowledge

- `knowledge/zuul-horizon-ci.md` — Horizon CI job taxonomy, known flake patterns, triage decision tree
- `knowledge/horizon.md` — Shared Horizon project reference

## MCP Dependencies

- `zuul-analyzer-agent` — Provides `find_zuul_errors` and `get_build_status` tools
  (optional in Phase 2; required in Phase 1)
