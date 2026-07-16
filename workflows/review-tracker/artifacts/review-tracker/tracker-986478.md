# Review 986478 — Live Comment Tracker

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
**Title:** Update filtering in the Images table
**Author:** Owen McGonagle
**Status:** NEW
**Current Patchset:** 4
**Zuul:** Pending (PS4 just uploaded 2026-07-15, awaiting CI)
**Files Changed:** 5 ([`openstack_dashboard/dashboards/project/images/images/tables.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py), [`openstack_dashboard/dashboards/project/images/views.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/views.py), [`openstack_dashboard/dashboards/project/images/images/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tests.py), [`openstack_dashboard/dashboards/project/images/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/tests.py), [`openstack_dashboard/dashboards/project/instances/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/instances/tests.py))
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
| 2 | 2026-07-15 | AI (Claude) | Recheck — PS3+PS4 uploaded, CMT-TAT-1 resolved, all votes reset, new file added |

---

## Change Log

### Scan #2 — 2026-07-15

1. **UPDATED** Header: Patchset 2 → 4, Zuul status pending, files 4 → 5
2. **UPDATED** [CMT-TAT-1](#cmt-tat-1): Status POSTED → RESOLVED (unresolved=false, blueprint reference added in PS3)
3. **UPDATED** [Score Summary](#score-summary): All votes reset to 0 (CR-1 outdated by PS3, Verified-1 outdated by PS4)
4. **NEW** PS3 uploaded (2026-07-15): Commit message update — added blueprint reference
5. **NEW** PS4 uploaded (2026-07-15): Code rework — new file `instances/tests.py`, updated `images/tests.py`
6. **UPDATED** What Needs to Change: ~~CMT-TAT-1 blueprint reference~~ resolved

---

## What Needs to Change

### Scan #1 — 2026-07-15

~~**CMT-TAT-1: Add blueprint reference to commit message**~~

- ~~**File:** `/COMMIT_MSG`~~
- ~~**What the code does now:** Commit message has no blueprint reference~~
- ~~**What the reviewer wants:** Add `Partially-Implements: blueprint removing-angularjs` to the commit message since this is part of the de-angularize topic~~
- ~~**Resolved:** Blueprint reference added in PS3 (commit message update, 2026-07-15)~~

---

## Where Things Are At / What To Do Next

### Overall Status

Review 986478 was created on 2026-04-28. After Tatiana's CR-1 requesting a blueprint reference
(2026-06-30), Owen pushed PS3 (commit message update adding the blueprint reference) and PS4
(code rework) on 2026-07-15. All votes have been reset — Tatiana's CR-1 was outdated by PS3,
and Zuul's Verified-1 on PS3 was outdated by PS4. CI is pending on PS4. The file set grew
from 4 to 5 files (added `instances/tests.py`, changed `images/tests.py`). Tatiana's only
comment thread is now resolved.

### Score Summary

| Label | Value | Who | Date |
|-------|-------|-----|------|
| Verified | 0 | Zuul | (pending on PS4) |
| Code-Review | 0 | Tatiana Ovchinnikova | (outdated by PS3) |
| Workflow | 0 | — | — |

### What You Should Do Next

1. **Wait for CI on PS4** — Zuul is running on the new patchset. Monitor for pass/fail
2. **Request re-review from Tatiana** — All her concerns are addressed; she needs to re-review PS4
3. **Consider code suggestions** — Review the docker format mapping and filter guard consistency points from the initial code review

### Open Threads Requiring Attention

| Thread | File | Status | Owner | Priority |
|--------|------|--------|-------|----------|
| ~~[CMT-TAT-1](#cmt-tat-1)~~ | ~~/PATCHSET_LEVEL~~ | ~~RESOLVED~~ | ~~—~~ | ~~—~~ |

---

## Patchset-Level Comments

<a name="cmt-tat-1"></a>

### CMT-TAT-1 — Blueprint reference request — RESOLVED

**Author:** Tatiana Ovchinnikova | **File:** /PATCHSET_LEVEL | **PS:** 2

> Thank you for the patch! Let's start tracking this initiative properly: please add the following line into the commit message:
>
> Partially-Implements: blueprint removing-angularjs
>
> -1 to just mark it as an action item

**AI Assessment:** Tatiana is asking for standard OpenStack commit message hygiene — linking de-angularize work to the removing-angularjs blueprint. This is a straightforward request. The CR-1 is purely to flag this as a required action, not a code quality objection.

**Status for Owen:** ~~Add blueprint reference~~ — Done. Blueprint reference added in PS3. Thread resolved.

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| Tatiana Ovchinnikova | 1 | 1 | 0 |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| Wait for Zuul CI on PS4 | HIGH | OPEN |
| ~~Add `Partially-Implements: blueprint removing-angularjs` to commit message~~ | ~~HIGH~~ | ~~RESOLVED (PS3)~~ |
| Request re-review from Tatiana | MEDIUM | OPEN |
| Address docker format mapping suggestion (optional) | LOW | OPEN |
