# Review 986478 — Live Comment Tracker

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
**Title:** Update filtering in the Images table
**Author:** Owen McGonagle
**Status:** NEW
**Current Patchset:** 2
**Zuul:** Verified-1 (build failed on PS2, 2026-04-28)
**Files Changed:** 4 ([`openstack_dashboard/dashboards/project/images/images/tables.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py), [`openstack_dashboard/dashboards/project/images/views.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/views.py), [`openstack_dashboard/dashboards/project/images/images/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tests.py), [`releasenotes/notes/images-project-filter-action-osprh16422.yaml`](https://github.com/openstack/horizon/blob/master/releasenotes/notes/images-project-filter-action-osprh16422.yaml))
**Reviewers:** Tatiana Ovchinnikova

---

## Initial Code Review

**Performed by:** `/horizon-code-review` (automated bridge)
**Verdict:** COMMENT
**Full Analysis:** [Code Review](bridge-artifacts/initial-review-986478.md)

### Summary

Replaces the tab-based `OwnerFilter` with a server-side `ImageFilterAction` search dropdown
in the project Images table. Mirrors the existing admin Images filter pattern. Includes tests
and a release note.

### Blockers

None

### Suggestions

1. Missing `disk_format` → `container_format` mapping for Docker images (admin view has this)
2. Defensive `filter_action and` guard inconsistent with admin pattern
3. UX change from tabs to search — confirm intent to fully replace tabs

---

## Scan Log

| # | Date | Scanner | Notes |
|---|------|---------|-------|
| 1 | 2026-07-15 | AI (Claude) | Initial scan — 1 comment thread from 1 reviewer |

---

## What Needs to Change

### Scan #1 — 2026-07-15

**CMT-TAT-1: Add blueprint reference to commit message**

- **File:** `/COMMIT_MSG`
- **What the code does now:** Commit message has no blueprint reference
- **What the reviewer wants:** Add `Partially-Implements: blueprint removing-angularjs` to the commit message since this is part of the de-angularize topic
- **Suggested fix:**
  ```
  # before (end of commit message)
  Change-Id: ...

  # after
  Partially-Implements: blueprint removing-angularjs
  Change-Id: ...
  ```
- **Why:** Tatiana wants de-angularize work tracked against the removing-angularjs blueprint for project tracking purposes

---

## Where Things Are At / What To Do Next

### Overall Status

Review 986478 was created on 2026-04-28 with 2 patchsets (PS2 was a commit message update).
CI failed on PS2 with Zuul Verified-1. Tatiana reviewed on 2026-06-30, giving Code-Review-1
with one patchset-level comment requesting a blueprint reference. The review has been idle
since 2026-06-30.

### Score Summary

| Label | Value | Who | Date |
|-------|-------|-----|------|
| Verified | -1 | Zuul | 2026-04-28 |
| Code-Review | -1 | Tatiana Ovchinnikova | 2026-06-30 |
| Workflow | 0 | — | — |

### What You Should Do Next

1. **Fix the CI failure** — PS2 has Zuul Verified-1. Investigate the build failure and push a new patchset that passes CI
2. **Add blueprint reference** — Add `Partially-Implements: blueprint removing-angularjs` to the commit message as Tatiana requested
3. **Consider code suggestions** — Review the docker format mapping and filter guard consistency points from the initial code review

### Open Threads Requiring Attention

| Thread | File | Status | Owner | Priority |
|--------|------|--------|-------|----------|
| [CMT-TAT-1](#cmt-tat-1) | /PATCHSET_LEVEL | POSTED — NEEDS YOUR RESPONSE | Owen | HIGH |

---

## Patchset-Level Comments

<a name="cmt-tat-1"></a>

### CMT-TAT-1 — Blueprint reference request — POSTED — NEEDS YOUR RESPONSE

**Author:** Tatiana Ovchinnikova | **File:** /PATCHSET_LEVEL | **PS:** 2

> Thank you for the patch! Let's start tracking this initiative properly: please add the following line into the commit message:
>
> Partially-Implements: blueprint removing-angularjs
>
> -1 to just mark it as an action item

**AI Assessment:** Tatiana is asking for standard OpenStack commit message hygiene — linking de-angularize work to the removing-angularjs blueprint. This is a straightforward request. The CR-1 is purely to flag this as a required action, not a code quality objection.

**Status for Owen:** Add `Partially-Implements: blueprint removing-angularjs` to the commit message in the next patchset. This can be combined with the CI fix push.

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| Tatiana Ovchinnikova | 1 | 0 | 1 |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| Fix Zuul CI failure (Verified-1) | HIGH | OPEN |
| Add `Partially-Implements: blueprint removing-angularjs` to commit message | HIGH | OPEN |
| Address docker format mapping suggestion (optional) | LOW | OPEN |
