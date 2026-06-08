# Horizon Code Review — Artifact Profiles

This file defines the artifact contracts for `/horizon-code-review --artifacts`.
When the agent detects `--artifacts` in the user input, it reads this file
to determine which artifacts to generate and what each must contain.

## Review Mode

The review mode is auto-detected from Gerrit change status (see SKILL.md
Step 0.5). Each artifact adapts its framing based on the mode:

| Mode | Gerrit Status | Artifact Framing |
|---|---|---|
| `pre-merge` | NEW / OPEN | Standard — findings gate the merge |
| `post-merge` | MERGED | Retrospective — findings become follow-up items |
| `historical` | ABANDONED | Lessons learned — no action expected |

Each artifact contract below includes a **Mode Adaptation** subsection
describing how content changes per mode.

## Artifact Set

When `--artifacts` is provided, generate ALL of the following artifacts
inside `artifacts/horizon-review/code-{change-number}/`:

---

### 1. review.md — Core Review

**Audience:** Reviewer, engineer
**Purpose:** The Gerrit review comment. Same content as the default
single-artifact output (`code-{change-number}.md`).

**Required sections:**

```
# Code Review: {brief description}

**Change**: {Gerrit URL}
**Files**: {count and summary}
**Date**: {date}
**Verdict**: {APPROVE / REQUEST_CHANGES / COMMENT}

## Summary
## Review History
## Blockers
### Plugin API Impact
### Missing Regression Test
### Intent or Architecture Issues
## Suggestions
## Nits
## Positive Feedback
## Files Reviewed
```

**Mode Adaptation:**

- **pre-merge**: Verdict from {APPROVE, REQUEST_CHANGES, COMMENT}.
  Blockers are merge-blocking.
- **post-merge**: Verdict from {POST_MERGE_OK, FOLLOW_UP_NEEDED, COMMENT}.
  Blockers section renamed to "Follow-Up Items (Would Have Been Blockers)".
  Each finding includes a follow-up action: file bug, submit patch, or monitor.
- **historical**: Verdict from {HISTORICAL_OK, HISTORICAL_CONCERNS}.
  Blockers section renamed to "Historical Concerns". Framed as lessons learned.

---

### 2. design-analysis.md — Design Analysis

**Audience:** Engineer, reviewer
**Purpose:** Deep walkthrough of what the code does, how it changes
behavior, and what edge cases exist.

**Required sections:**

```
# Design Analysis: {brief description}

## Change Overview
## Before/After Walkthrough
## Horizon Architecture Fit
## Edge Cases
## Plugin Ecosystem Impact
```

**Content guidance:**

- **Change Overview:** What changed, in what files, and why (2-3 paragraphs)
- **Before/After Walkthrough:** Code flow BEFORE vs AFTER the patch.
  Use inline code references. For auth changes: trace the request
  lifecycle. For API changes: trace the client call chain.
- **Horizon Architecture Fit:** Reference `knowledge/horizon.md` for
  pattern matching. Note divergence from conventions.
- **Edge Cases:** Numbered list. Each with Scenario, Analysis, and
  Risk level (Low/Medium/High). Minimum 3 edge cases.
- **Plugin Ecosystem Impact:** Reference `knowledge/horizon.md` plugin
  API stability rules. If no impact: "No plugin impact."

**Mode Adaptation:**

- **pre-merge / historical**: No change — design analysis is objective.
- **post-merge**: Add a "Post-Merge Observations" subsection noting any
  issues discovered that could inform follow-up work.

---

### 3. testing-guide.md — Testing Guide

**Audience:** Engineer, QE
**Purpose:** Manual testing procedures for aspects of the change
that CI cannot cover.

**Required sections:**

```
# Testing Guide: {brief description}

## Quick Reference
## Background
## Prerequisites
## Test Flow
## Test Cases
### TC-01: {title}
### TC-02: {title}
### TC-03: {title}
## Automated Validation
## Verification Checklist
```

**Content guidance:**

- **Quick Reference:** Table with Review URL, Repo, Files Changed
- **Background:** What the bug/feature is and how the fix works
  (2-3 paragraphs, accessible to someone unfamiliar with the code)
- **Prerequisites:** Environment setup. For auth changes: IdP config.
  For API changes: service endpoints. For templates: browser + DevTools.
- **Test Flow:** ASCII diagram showing the interaction sequence
- **Test Cases:** Numbered TC-01 through TC-N. Each is a table:

  | Step | Action | Expected |
  |------|--------|----------|
  | 1 | ... | ... |

- **Automated Validation:** tox commands the reviewer can run
- **Verification Checklist:** Checkbox list, 8-12 items

**Mode Adaptation:**

- **pre-merge**: Title "Testing Guide". Framed as "test before approving".
  Prerequisites assume dev/staging environment.
- **post-merge**: Title "Production Verification Guide". Framed as "verify
  the merged change works correctly in production". Prerequisites assume
  access to a deployed environment running the merged code. Test cases focus
  on confirming correct behavior rather than discovering issues.
- **historical**: Title "Testing Reference". Framed as "these tests would
  have been relevant". No urgency.

**Depth rules:**

Generate a FULL testing guide (5+ test cases) when:
- Changes touch `openstack_auth/` (authentication)
- Changes involve WebSSO, federation, or session handling
- Changes modify `openstack_dashboard/api/` (API client layer)
- Changes modify `horizon/` public classes (plugin API)
- Changes involve Django version compatibility
- Agent classifies the change as security-sensitive

Generate a MINIMAL testing guide (2-3 test cases) when:
- Template-only changes
- Documentation changes
- Test-only changes
- Simple bug fixes with existing test coverage

---

### 4. risk-assessment.md — Risk Assessment

**Audience:** Reviewer, manager
**Purpose:** Formal risk table for quick executive scanning.

**Required sections:**

```
# Risk Assessment: {brief description}

## Risk Summary
## Risk Table
## Security Considerations
## Rollback Strategy
## Recommendation
```

**Content guidance:**

- **Risk Summary:** 1 paragraph overview of overall risk level
- **Risk Table:**

  | # | Risk | Severity | Mitigation | Status |
  |---|------|----------|------------|--------|
  | 1 | ... | Critical/High/Medium/Low | ... | Open/Mitigated |

  Minimum 3 risk vectors. Draw from:
  - `knowledge/horizon.md`: Settings Security Checklist
  - `knowledge/horizon.md`: Performance-Sensitive Settings
  - `knowledge/horizon.md`: `@memoized` decorator silent failure
  - `knowledge/horizon.md`: Plugin API stability
  - Django 5.2 compatibility
  - SDK migration pitfalls
  - General security (CSRF, XSS, session handling)

- **Security Considerations:** If auth/sessions/CSRF/settings touched,
  enumerate concerns. If not: "No security-sensitive changes."
- **Rollback Strategy:** Is revert safe? Migrations to undo? Config
  changes to revert?
- **Recommendation:** Proceed / Proceed with caution / Block

**Mode Adaptation:**

- **pre-merge**: Recommendation uses "Proceed" / "Proceed with caution" / "Block".
- **post-merge**: Recommendation uses "No action needed" / "File follow-up
  bug" / "Consider revert". Risk severity is preserved but actions shift
  from gating to monitoring.
- **historical**: Recommendation uses "No action needed" / "Pattern to watch
  in future reviews".

---

### 5. what-ai-did.md — AI Transparency Report

**Audience:** Anyone
**Purpose:** What the AI checked, what tools it used, what it
couldn't check.

**Required sections:**

```
# What AI Did: Review of {change-number}

## Checks Performed
## Knowledge Sources Consulted
## Gerrit Context
## Limitations
## Agent Collaboration
```

**Content guidance:**

- **Checks Performed:** Bulleted list of review steps executed
- **Knowledge Sources Consulted:** Which `knowledge/` files used,
  with line counts and key sections referenced
- **Gerrit Context:** Was MCP available? Were prior comments examined?
- **Limitations:** What the AI could NOT check. Be honest — this
  builds more trust than any positive claim.
- **Agent Collaboration:** Was @horizon-core invoked? What did it
  contribute?

**Mode Adaptation:**

- All modes: Include the detected review mode and explain why.
  "Review mode: post-merge (change status: MERGED)."

---

### 6. what-you-do-next.md — Human Handoff

**Audience:** Reviewer
**Purpose:** After reading all artifacts, what should the reviewer do?

**Required sections:**

```
# What You Do Next: Review {change-number}

## Verdict
## Immediate Actions
## Posting to Gerrit
## If Changes Are Needed
## Follow-Up Items
```

**Content guidance:**

- **Verdict:** One line — the review recommendation
- **Immediate Actions:** Numbered list, 3-5 items
- **Posting to Gerrit:** MCP command, REST curl, or manual copy-paste
  instructions depending on availability
- **If Changes Are Needed:** What to tell the patch author, referencing
  specific blockers
- **Follow-Up Items:** Deferred checks, related changes to watch

**Mode Adaptation:**

- **pre-merge**: Verdict is the Gerrit vote recommendation. Immediate Actions
  focus on posting to Gerrit, requesting changes, or approving.
- **post-merge**: Verdict is the retrospective assessment. Immediate Actions
  focus on: (1) deciding whether to file follow-up bugs, (2) verifying in
  production, (3) monitoring for related issues. "Posting to Gerrit" section
  becomes "Posting Retrospective Comment (optional)".
- **historical**: Verdict is the historical assessment. Immediate Actions
  focus on: (1) documenting lessons learned, (2) updating review checklists
  if the change revealed a gap.
