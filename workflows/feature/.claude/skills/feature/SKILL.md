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
/feature tag=<tag> <ticket-key> --artifacts-only
/feature tag=<tag> <ticket-key> --dry-run
/feature tag=<tag> <ticket-key> --dry-run --blind
/feature tag=<tag> --status
/feature --tags
/feature <ticket-key>

## Examples

/feature tag=pqc OSPRH-28889
/feature tag=pqc OSPRH-28889 --artifacts-only
/feature tag=pqc OSPRH-28889 --dry-run
/feature tag=pqc OSPRH-28889 --dry-run --blind
/feature tag=pqc --status
/feature --tags
/feature OSPRH-28889

## Modes

| Flag | Implements? | Sees existing PRs? | Compares? | Pushes? | Use case |
|------|------------|-------------------|-----------|---------|----------|
| (default) | Yes | Yes (blocks if found) | No | User decides | First-time implementation |
| --artifacts-only | No | Yes (as context) | Yes (knowledge vs actual) | No | Re-run analysis for dashboard |
| --dry-run | Yes (in worktree) | Yes (as context) | Yes (implemented vs actual) | No | Verify skill reproduces correct changes |
| --dry-run --blind | Yes (in worktree) | **No (until after impl)** | Yes (implemented vs actual) | No | Clean-room verification |

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

**Step 1.5: CHECK FOR EXISTING WORK**
  Before implementing, check for prior work on this ticket:
  - Search for open PRs in the target repo matching the ticket key
    (gh pr list --search "<ticket-key>" --state open)
  - Search for branches matching the ticket key or tag
    (git branch -r | grep -i "<ticket-key-or-tag>")
  - Check if artifacts/feature/<tag>/assessment-<ticket>.md exists
  **Default mode:** If any exist, report current status (PR URL,
  branch, CI state) and STOP. Do NOT re-implement or create
  duplicate work. Only proceed if the user explicitly says to
  start fresh.
  **--artifacts-only mode:** Report existing work as context and
  CONTINUE. Record PR URL, branch, and CI state for use in
  Step 3.5 and the assessment artifact.
  **--dry-run mode:** Same as --artifacts-only -- report as context
  and CONTINUE.
  **--dry-run --blind mode:** SKIP this step entirely. Do NOT search
  for existing PRs, branches, or prior work. The first time existing
  work is discovered is in Step 5.5, AFTER implementation is complete.
  This creates an information barrier so the implementation in
  Steps 3-4 is not influenced by prior solutions.

**Step 2: ANALYZE TARGET REPOSITORY**
  Read Section 3 (Target Repository) of the tag knowledge file.
  If local checkout available: read the target files.
  Verify version and dependency requirements.
  **--dry-run mode:** Set up a clean working copy for implementation:
  1. If a local checkout exists: create a git worktree from the base
     branch (e.g., main) -- this gives a clean state with no prior
     changes for this ticket
  2. If no local checkout: clone the target repo into a temporary
     directory and checkout the base branch
  All implementation in Step 4 targets this worktree/clone.

  **Required assessment sections** (collected here, written in Step 6a):
  - Executive Summary: table with Risk Level, Recommendation,
    Confidence, Breaking Changes
  - Code Analysis: per-component findings with file:line references
  - Compliance Checklist: each requirement from the knowledge file
    with PASS/FAIL/N-A and evidence
  - Sibling Stories: table of related tickets from knowledge Section 2
    with status and relationship

**Step 2.5: DESIGN DOCUMENT**
  Write design.md to artifacts/feature/<tag>/ with these sections:
  - **Overview:** problem statement and proposed solution (2-3 sentences)
  - **Scope:** In-scope / Out-of-scope / Deferred items
  - **Current State:** code excerpts with file:line references showing
    the code BEFORE changes
  - **Proposed Changes:** insertion points, new/modified code, and a
    Before/After comparison table
  - **Success Criteria:** numbered list, each with a verification method
  This document is generated in ALL modes.

**Step 3: DETERMINE CODE CHANGES**
  Read Section 4 (Code Change Requirements) of the tag knowledge file
  for INTENT and CONSTRAINTS -- not exact code.
  Read the target repository source files to understand the current
  code structure, then derive the implementation independently.
  Cross-reference with Section 5 (Architecture Patterns).
  Do NOT read Section 8 (Reference Implementation) during this step
  -- that section exists only for post-hoc comparison in Step 5.5.

**Step 3.5: COMPARE WITH ACTUAL** (--artifacts-only mode ONLY)
  If existing work was found in Step 1.5:
  1. Read the actual code changes from the PR/branch
     (gh pr diff <number> or git diff against base branch)
  2. Compare them against the changes derived from the knowledge
     file in Step 3
  3. Note any differences: drift, missing changes, extra changes
  4. Feed the comparison into the assessment artifact in Step 6
  Skip this step in default mode.

**Step 4: IMPLEMENT CHANGES** (SKIP in --artifacts-only mode)
  Apply code changes per Section 4.
  Follow architecture patterns from Section 5.
  **--dry-run mode:** Apply changes in the worktree/clone from
  Step 2, NOT in the user's working directory.

**Step 5: RUN VALIDATION**
  Execute ALL commands from Section 6 (Validation Commands).
  Report pass/fail for each command individually.
  If any fail: analyze and fix before proceeding.
  **--dry-run mode:** Run validation in the worktree/clone.

**Step 5.5: COMPARE WITH PR** (--dry-run mode ONLY)
  After validation, compare the worktree changes against the
  existing PR:
  **--dry-run (without --blind):** Compare against PR found in Step 1.5.
  **--dry-run --blind:** This is the FIRST time existing PRs are
  discovered. NOW search for open PRs matching the ticket key
  (gh pr list --search "<ticket-key>" --state open). The
  implementation is already complete -- this cannot influence it.
  Then:
  1. Generate a diff of worktree changes (what the skill produced)
  2. Fetch the PR diff (gh pr diff <number>)
  3. Compare the two diffs:
     - Identical? Skill perfectly reproduces the PR
     - Different? Note what differs and why (whitespace, comments,
       insertion point, extra/missing changes)
  4. Feed the comparison into the assessment artifact in Step 6
  5. In --blind mode: explicitly state in the assessment that the
     AI had NO access to existing PRs during implementation
  Skip this step in default and --artifacts-only modes.

**Step 6: GENERATE ARTIFACTS**
  Write ALL 6 artifacts to artifacts/feature/<tag>/.
  Every artifact is generated in ALL modes (default, --artifacts-only,
  --dry-run, --dry-run --blind).

  **6a: assessment.md** -- Analysis report from Step 2.
  **Target: 1,200-1,500 words.**
  Required sections:
  - Executive Summary table (use template from knowledge Section 9):
    | Field | Value |
    |-------|-------|
    | Risk Level | [Low / Medium / High / Critical] |
    | Recommendation | [Merge / Merge with conditions / Defer / Block] |
    | Confidence | [High / Medium / Low] |
    | Breaking Changes | [None / Conditional] |
  - Code Analysis: for each file in scope, include Current State
    (with file:line excerpts), Finding, Proposed Change (insertion
    point + new code), Validation Point
  - Compliance Checklist (one row per requirement from knowledge
    Section 9, each with PASS/FAIL/N-A and specific evidence):
    | Requirement | Status | Evidence |
    |-------------|--------|----------|
    | [from knowledge file] | PASS/FAIL/N-A | [file:line or cmd] |
  - Sibling Stories (ticket / status / relationship table from
    knowledge Section 9)
  **In --artifacts-only mode**, additionally include:
  - Knowledge-derived changes vs actual changes (from Step 3.5)
  - Existing work status (PR URL, CI state)
  **In --dry-run mode**, additionally include:
  - Implemented changes (skill output in worktree)
  - Implementation comparison (diff-of-diffs: skill vs PR)
  **In --dry-run --blind mode**, additionally include:
  - Blind-mode disclosure and clean-room verification label

  **6b: design.md** -- Design document from Step 2.5.
  **Target: 800-1,200 words.**
  Verify the file written in Step 2.5 is in artifacts/feature/<tag>/.
  Required sections: Overview (including quantum threat context),
  Scope, Current State (with file:line code excerpts), Proposed
  Changes (with Before/After table from knowledge Section 10),
  Risk Assessment (table from knowledge Section 10), Success
  Criteria. For each file in scope, include: Current State excerpt,
  Finding, Proposed Change with insertion point, Validation Point.
  Every code excerpt must include file:line.

  **6c: testing.md** -- Validation evidence from Step 5.
  **Target: 400-600 words.**
  Required format per command:
  ```
  ### Command: <command>
  - **Working directory:** <path>
  - **Status:** PASS | FAIL
  - **Output:**
    ```
    <actual output or summary>
    ```
  - **Why this matters:** <what this command verifies>
  ```
  Include ALL commands from Section 6 of the knowledge file.
  Additionally include at least one **negative test case** showing
  old behavior contrasted with new behavior. Example: show that
  TLS 1.2 negotiation succeeds BEFORE the change, and fails AFTER.
  Include a Post-Deploy Verification section with concrete access
  instructions (e.g., kubectl port-forward command, exact openssl
  invocation, expected output lines).

  **6d: pr-description.md** -- Ready-to-paste PR body.
  **Target: 200-300 words.**
  Required sections: Summary (2-3 sentences), Changes (bullet list
  with file:line refs), Why (domain rationale -- quantum threat,
  PQC readiness), Test Plan (numbered steps with checkboxes),
  Related (ticket links including epic, story, tracking sheet).
  This is always useful as dashboard context even when
  Step 7 is skipped.

  **6e: next-steps.md** -- Human handoff guide.
  **Target: 250-350 words.**
  Mode-aware content:
  - Default: "Push branch, create PR, request review"
  - --artifacts-only: "Review analysis, decide on next action"
  - --dry-run: "Compare worktree results with PR, decide"
  - --dry-run --blind: "Review blind analysis, compare with PR"
  Include exact commands the human should run next.
  Include conditional paths ("If PR is still in review...").
  Include "What NOT to do" section to prevent common mistakes.

  **6f: what-ai-did.md** -- Execution report.
  **Target: 400-500 words.**
  Required sections:
  - Execution Summary (mode, tag, ticket, timestamp)
  - Knowledge Consumed (list each file read with path AND why)
  - Steps Executed (numbered, mapped to SKILL.md step numbers --
    e.g., "Step 0: Tier Classification -> Tier 2, proceed")
  - Artifacts Produced (table: filename / description / word count)
  - Key Decisions (what choices were made and rationale)
  - Known Limitations (what was skipped, what could not be verified)
  Report what ACTUALLY happened, not a template.

**Step 7: PREPARE DELIVERY** (SKIP in --artifacts-only and --dry-run modes)
  Use templates from Section 7 (Delivery Pattern).
  Generate git commit, push, and PR commands.
  Present to user for approval.
  NEVER push or create PR without explicit user consent.

**Cleanup** (--dry-run mode ONLY)
  After artifacts are generated, remove the worktree/clone:
  - git worktree remove <path> (if worktree was used)
  - rm -rf <temp-dir> (if clone was used)
  Do NOT leave temporary checkouts on disk.

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
