---
name: feature
description: Implement feature changes for OpenStack operators using tag-specific knowledge. Use tag=xxx to specify the domain (e.g., tag=pqc for PQC compliance). Run /feature --tags to list available domains.
---

# Feature Implementation (Tag-Based)

Implement feature changes for OpenStack operators guided by
domain-specific knowledge files. Each domain is a "tag" with
its own knowledge file at knowledge/feature-<tag>.md.

## Usage

/feature tag=<tag> <ticket-key-or-description>
/feature tag=<tag> --status
/feature --tags
/feature <ticket-key>

## Examples

/feature tag=pqc OSPRH-28889
/feature tag=pqc --status
/feature --tags
/feature OSPRH-28889

## Tag Resolution

Tags are CASE-INSENSITIVE. Normalize to lowercase before lookup.
tag=PQC, tag=Pqc, and tag=pqc all resolve to knowledge/feature-pqc.md.

1. If tag= is provided:
   - Normalize tag value to lowercase
   - Load knowledge/feature-<tag>.md
   - If not found: list available tags and stop

2. If tag= is NOT provided but a ticket key is:
   - Scan all knowledge/feature-*.md files
   - Search Section 2 (Scope) for the ticket key
   - If exactly one match: use that tag
   - If multiple matches: ask user to specify tag=
   - If no match: list available tags and stop

3. If --tags is provided:
   - List all knowledge/feature-*.md files with their
     tag name and description from the file header

## Process Steps

Once the tag is resolved and the knowledge file is loaded:

**Step 0: TIER CLASSIFICATION**
  Read Section 2 (Scope) for tier classification.
  - Tier 1 (CENTRAL): STOP. Output proposed changes and advise
    user to coordinate with the responsible team. Do NOT implement.
  - Tier 2 (PER-OPERATOR): Continue with Steps 1-7.
  - Tier 3 (CROSS-TEAM BLOCKED): STOP. Explain the dependency.

**Step 1: CLASSIFY THE REQUEST**
  Read Section 2 (Scope) of the tag knowledge file.
  Determine which ticket(s), which PR(s), which files.
  Check for blocked or closed tickets.

**Step 2: ANALYZE TARGET REPOSITORY**
  Read Section 3 (Target Repository) of the tag knowledge file.
  If local checkout available: read the target files.
  Verify version and dependency requirements.

**Step 3: DETERMINE CODE CHANGES**
  Read Section 4 (Code Change Catalog) of the tag knowledge file.
  Cross-reference with Section 5 (Architecture Patterns).

**Step 4: IMPLEMENT CHANGES**
  Apply code changes per Section 4.
  Follow architecture patterns from Section 5.

**Step 5: RUN VALIDATION**
  Execute ALL commands from Section 6 (Validation Commands).
  Report pass/fail for each command individually.
  If any fail: analyze and fix before proceeding.

**Step 6: GENERATE ARTIFACTS**
  Write to artifacts/feature/<tag>/:
  - assessment-<ticket>.md (full analysis + validation results)
  - pr-description-<ticket>.md (ready-to-paste PR body)

**Step 7: PREPARE DELIVERY**
  Use templates from Section 7 (Delivery Pattern).
  Generate git commit, push, and PR commands.
  Present to user for approval.
  NEVER push or create PR without explicit user consent.

## Knowledge Sources

- knowledge/feature-<tag>.md -- Tag-specific domain knowledge
  (loaded dynamically based on the resolved tag)
- knowledge/horizon.md -- Horizon project reference (shared
  context, reused from the horizon-review workflow)

## Agent Persona

Uses the feature-engineer persona defined in
agents/feature-engineer.md.

## Rules

Follow the behavioral rules in rules.md within this workflow
directory.
