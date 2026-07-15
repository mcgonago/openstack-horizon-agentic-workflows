# Review 986458 — Live Comment Tracker

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986458](https://review.opendev.org/c/openstack/horizon/+/986458)
**Title:** Add activate/deactivate row actions to Images table
**Author:** Owen McGonagle
**Status:** NEW (Work in Progress)
**Current Patchset:** PS4
**Zuul:** Verified+1 (PS4)
**Files Changed:** 2 ([`openstack_dashboard/dashboards/project/images/images/tables.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py), [`openstack_dashboard/dashboards/project/images/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/tests.py))
**Reviewers:** Tatiana Ovchinnikova

---

## Initial Code Review

**Status:** Unavailable — bridge to `/horizon-code-review` failed.
Run `/horizon-code-review 986458` manually for code analysis.

---

## Scan Log

| # | Date | Scanner | Notes |
|---|------|---------|-------|
| 1 | 2026-07-15 | AI (Claude) | Initial scan — 1 comment thread from 1 reviewer |

---

## What Needs to Change

This section gives concrete, code-level guidance for every open blocking comment.
Each entry is tied to a scan — new entries accumulate on recheck, resolved ones
get strikethrough.

### Scan #1 — 2026-07-15

**CMT-TAT-1: Add blueprint reference to commit message**

- **File:** `/COMMIT_MSG`
- **What the code does now:** The commit message describes the feature but does not reference the upstream blueprint for the de-angularize initiative.
- **What the reviewer wants:** Add `Partially-Implements: blueprint removing-angularjs` to the commit message footer to properly track this work against the blueprint.
- **Suggested fix:**
  ```
  # before (commit message footer)
  Change-Id: I6edd21a2b2fa5f77cf27b5ddd076aaed0d2c928f

  # after (commit message footer)
  Partially-Implements: blueprint removing-angularjs
  Change-Id: I6edd21a2b2fa5f77cf27b5ddd076aaed0d2c928f
  ```
- **Why:** The de-angularize topic has an associated Launchpad blueprint (`removing-angularjs`). Referencing it in the commit message enables tracking which patches contribute to the initiative and generates proper links in the release notes.

---

## Where Things Are At / What To Do Next

### Overall Status

This review adds Deactivate and Reactivate row actions to the Images table as part of the de-angularize initiative (topic: `de-angularize`). The implementation is clean — two new `BatchAction` subclasses (`DeactivateImage`, `ReactivateImage`) wired into `ImagesTable.row_actions`, with test updates for the new action count. The review is marked **Work in Progress** and has 4 patchsets (PS2–PS4 were commit message updates only, no code changes since PS1).

Tatiana Ovchinnikova reviewed on 2026-06-30 and gave **Code-Review -1** with a single, straightforward request: add `Partially-Implements: blueprint removing-angularjs` to the commit message. CI is green (Verified+1 on PS4).

### Score Summary

| Label | Value | From |
|-------|-------|------|
| Verified | +1 | Zuul (PS4) |
| Code-Review | -1 | Tatiana Ovchinnikova |
| Workflow | 0 | — |

### What You Should Do Next

1. **Amend the commit message** to add `Partially-Implements: blueprint removing-angularjs` — this is the only action item blocking progress
2. **Remove WIP status** when ready for full review — the review is currently marked Work in Progress (`has_review_started: false`)
3. Wait for Zuul to re-verify the new patchset (no code change, so this should pass quickly)

### Open Threads Requiring Attention

| Thread | File | Status | Owner | Priority |
|--------|------|--------|-------|----------|
| [CMT-TAT-1](#cmt-tat-1) | /PATCHSET_LEVEL | RESOLVED (action pending) | Owen McGonagle | HIGH |

---

## Patchset-Level Comments

<a name="cmt-tat-1"></a>

### CMT-TAT-1 — Blueprint reference in commit message — RESOLVED

**Author:** Tatiana Ovchinnikova | **File:** /PATCHSET_LEVEL | **PS:** 4

> Thank you for the patch! Let's start tracking this initiative properly: please add the following line into the commit message:
>
> Partially-Implements: blueprint removing-angularjs
>
> -1 to just mark it as an action item

**AI Assessment:** This is a blocking procedural request (Code-Review -1). Tatiana is asking for the standard blueprint reference that all de-angularize patches should carry. The -1 is not about code quality — it's a process gate to ensure proper initiative tracking. Straightforward fix: amend the commit message and push a new patchset.

**Status for Owen McGonagle:** Amend the commit message to add `Partially-Implements: blueprint removing-angularjs` before the `Change-Id` line. Then push the updated patchset. The thread is marked resolved on Gerrit, but the requested change has not yet been made.

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| Tatiana Ovchinnikova | 1 | 1 | 0 |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| Add `Partially-Implements: blueprint removing-angularjs` to commit message | HIGH | OPEN |
| Remove WIP status | MEDIUM | OPEN |
| Get Code-Review +2 (×2) and Workflow +1 | HIGH | OPEN |
