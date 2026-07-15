# Review 986458 — Live Comment Tracker

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986458](https://review.opendev.org/c/openstack/horizon/+/986458)
**Title:** Add activate/deactivate row actions to Images table
**Author:** Owen McGonagle
**Status:** NEW
**Current Patchset:** PS6
**Zuul:** Verified +1 (PS6 — build succeeded)
**Files Changed:** 2 ([`openstack_dashboard/dashboards/project/images/images/tables.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py), [`openstack_dashboard/dashboards/project/images/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/tests.py))
**Reviewers:** Tatiana Ovchinnikova, Radomir Dopieralski

---

## Initial Code Review

**Status:** Unavailable — bridge to `/horizon-code-review` failed.
Run `/horizon-code-review 986458` manually for code analysis.

---

## Scan Log

| # | Date | Scanner | Notes |
|---|------|---------|-------|
| 1 | 2026-07-15 | AI (Claude) | Initial scan — 1 comment thread from 1 reviewer |
| 2 | 2026-07-15 | AI (Claude) | Recheck — PS5 commit message update, WIP removed, PS6 rebase. All votes reset. |
| 3 | 2026-07-15 | AI (Claude) | Recheck — New reviewer Radomir Dopieralski: Code-Review -1 with 2 inline threads on `tables.py`. Zuul Verified +1 on PS6. Deep-dive analysis on both threads. |

---

## Change Log

### Scan #3 — 2026-07-15

1. **NEW** [CMT-RAD-1](#cmt-rad-1): Radomir Dopieralski commented on `tables.py:233` — questions whether `allowed()` is redundant with `policy_rules` on DeactivateImage
2. **NEW** [CMT-RAD-2](#cmt-rad-2): Radomir Dopieralski commented on `tables.py:265` — same question on ReactivateImage
3. **UPDATED** [Score Summary](#score-summary): Zuul Verified +1 on PS6; Code-Review -1 from Radomir Dopieralski
4. **NEW** [What Needs to Change — Scan #3](#scan-3--2026-07-15-1): Radomir's feedback on `allowed()` vs RBAC policy — respond to clarify the complementary design
5. **NEW** Deep-dive bridge artifacts: [CMT-RAD-1 analysis](bridge-artifacts/cmt-rad-1-analysis.md), [CMT-RAD-2 analysis](bridge-artifacts/cmt-rad-2-analysis.md)

### Scan #2 — 2026-07-15

1. **UPDATED** [Header](#review-986458--live-comment-tracker): PS4 → PS6, WIP removed, Zuul pending
2. **UPDATED** [Score Summary](#score-summary): All votes reset (PS5 outdated Code-Review -1, PS6 rebase outdated Verified)
3. **UPDATED** [What Needs to Change](#what-needs-to-change): ~~CMT-TAT-1~~ struck through — commit message amended in PS5
4. **UPDATED** [Key Remaining Items](#key-remaining-items-before-this-can-merge): Blueprint reference RESOLVED, WIP RESOLVED

---

## What Needs to Change

This section gives concrete, code-level guidance for every open blocking comment.
Each entry is tied to a scan — new entries accumulate on recheck, resolved ones
get strikethrough.

### Scan #1 — 2026-07-15

~~**CMT-TAT-1: Add blueprint reference to commit message**~~

~~- **File:** `/COMMIT_MSG`~~
~~- **What the code does now:** The commit message describes the feature but does not reference the upstream blueprint for the de-angularize initiative.~~
~~- **What the reviewer wants:** Add `Partially-Implements: blueprint removing-angularjs` to the commit message footer to properly track this work against the blueprint.~~
~~- **Suggested fix:**~~
  ~~```~~
  ~~# before (commit message footer)~~
  ~~Change-Id: I6edd21a2b2fa5f77cf27b5ddd076aaed0d2c928f~~

  ~~# after (commit message footer)~~
  ~~Partially-Implements: blueprint removing-angularjs~~
  ~~Change-Id: I6edd21a2b2fa5f77cf27b5ddd076aaed0d2c928f~~
  ~~```~~
~~- **Why:** The de-angularize topic has an associated Launchpad blueprint (`removing-angularjs`). Referencing it in the commit message enables tracking which patches contribute to the initiative and generates proper links in the release notes.~~

**Resolved in PS5** — commit message amended with blueprint reference.

### Scan #3 — 2026-07-15

**CMT-RAD-1: Clarify why `allowed()` is needed alongside `policy_rules` on DeactivateImage**

- **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:233`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L233)
- **What the code does now:** `DeactivateImage` defines both `policy_rules = (("image", "deactivate"),)` and an `allowed()` method that checks `image.protected`, `image.owner`, and `image.status == "active"`.
- **What the reviewer asks:** Whether the `allowed()` method is redundant given `policy_rules` already handles authorization.
- **Action required:** Respond on Gerrit explaining the complementary design. No code change needed — `allowed()` handles state-based visibility (status check), `policy_rules` handles RBAC authorization. The framework combines them with AND logic. See [deep-dive analysis](bridge-artifacts/cmt-rad-1-analysis.md).
- **Why:** Radomir initially thought `allowed()` duplicated the RBAC check, then noticed `policy_rules` exists and asked if `allowed()` is unnecessary. The answer is that `allowed()` is needed for the status filter — without it, the Deactivate button would appear on already-deactivated images.

**CMT-RAD-2: Same clarification needed on ReactivateImage**

- **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:265`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L265)
- **What the code does now:** `ReactivateImage` defines `policy_rules = (("image", "reactivate"),)` and `allowed()` checks `image.owner` and `image.status == "deactivated"`.
- **What the reviewer asks:** Same as CMT-RAD-1 — references "Same here".
- **Action required:** Respond on Gerrit referencing the DeactivateImage explanation. No code change needed. See [deep-dive analysis](bridge-artifacts/cmt-rad-2-analysis.md).

---

## Where Things Are At / What To Do Next

### Overall Status

This review adds Deactivate and Reactivate row actions to the Images table as part of the de-angularize initiative (topic: `de-angularize`). The implementation is clean — two new `BatchAction` subclasses (`DeactivateImage`, `ReactivateImage`) wired into `ImagesTable.row_actions`, with test updates for the new action count.

**Since Scan #2:** Zuul Verified +1 on PS6 (CI passes). Radomir Dopieralski reviewed PS6 and left Code-Review -1 with 2 inline threads on `tables.py`. He questions whether the `allowed()` method is redundant with `policy_rules` on both `DeactivateImage` (line 233) and `ReactivateImage` (line 265). After posting his initial comment, Radomir self-corrected — he noticed `policy_rules` was already defined and asked if `allowed()` is then unnecessary. Deep-dive analysis confirms `allowed()` IS needed for state-based visibility (status check), and the ownership check follows existing patterns in this file.

### Score Summary

| Label | Value | From |
|-------|-------|------|
| Verified | +1 | Zuul (PS6, 2026-07-15) |
| Code-Review | -1 | Radomir Dopieralski (PS6, 2026-07-15) |
| Workflow | 0 | — |

### What You Should Do Next

1. **Respond to Radomir on Gerrit** — Use the suggested responses from the deep-dive analysis to explain why `allowed()` is needed alongside `policy_rules`. The framework's `_allowed()` method (horizon/tables/actions.py:130) combines both with AND logic. No code change required.
2. **Wait for re-review** — After responding, wait for Radomir to acknowledge the explanation and potentially update his vote
3. **Get Code-Review +2 (x2) and Workflow +1** — Still need two +2 votes from core reviewers

### Open Threads Requiring Attention

| Thread | File | Status | Owner | Priority |
|--------|------|--------|-------|----------|
| [CMT-RAD-1](#cmt-rad-1) | tables.py:233 | NEEDS YOUR RESPONSE | Owen | HIGH |
| [CMT-RAD-2](#cmt-rad-2) | tables.py:265 | NEEDS YOUR RESPONSE | Owen | HIGH |
| [CMT-TAT-1](#cmt-tat-1) | /PATCHSET_LEVEL | RESOLVED | — | — |

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

**Status for Owen McGonagle:** Done. Commit message amended in PS5 with `Partially-Implements: blueprint removing-angularjs`. Code-Review -1 has been outdated.

---

## Inline Comments — Radomir Dopieralski

<a name="cmt-rad-1"></a>

### CMT-RAD-1 — `allowed()` vs `policy_rules` on DeactivateImage — NEEDS YOUR RESPONSE

**Author:** Radomir Dopieralski | **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:233`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L233) | **PS:** 6

> I think this should be an RBAC policy check -- the logic you have here matches the default policy, but this can be changed in a particular OpenStack install. I believe the policy for this is in glance and is called "deactivate". You will need to pass the image as the target to the check.

**Reply (Radomir Dopieralski, PS6):**
> Sorry, I didn't notice that you already have policy_rules defined on this action. In this case the allowed method should not be needed?

**AI Assessment:** This is a blocking question (Code-Review -1). Radomir initially thought the code was missing RBAC policy integration, then noticed `policy_rules` was already defined and pivoted to asking whether `allowed()` is then redundant. This is a nuanced architectural question — the answer is that `policy_rules` and `allowed()` serve complementary roles in Horizon's framework, and both are needed.

**Deep Dive:** [Code Analysis](bridge-artifacts/cmt-rad-1-analysis.md)

**Answer Summary:**
- The framework's `_allowed()` method (horizon/tables/actions.py:130) combines `policy_check(policy_rules)` AND `allowed()` with AND logic — they are complementary, not redundant
- `policy_rules` handles RBAC authorization ("can this user deactivate?"); `allowed()` handles state-based visibility ("should the button show on this image?")
- Without `allowed()`, the Deactivate button would appear on already-deactivated images
- 58 actions in the codebase use both `policy_rules` and `allowed()` — this is the standard pattern
- The ownership check follows existing patterns from DeleteImage (line 135) and EditImage (line 163) in the same file

**Suggested Response:**
> Good point! The `allowed()` method and `policy_rules` serve complementary roles in Horizon's framework — `_allowed()` in `horizon/tables/actions.py:130` combines them with AND logic. `policy_rules` handles RBAC authorization ("can this user deactivate?"), while `allowed()` handles state-based visibility ("should we show the button on this specific image?"). Without the status check in `allowed()`, the Deactivate button would appear on already-deactivated images. The ownership check follows the existing pattern from `DeleteImage` (line 135) and `EditImage` (line 163) in this same file. Happy to discuss if you'd prefer a different approach.

**Status for Owen McGonagle:** Copy the suggested response to Gerrit.

<a name="cmt-rad-2"></a>

### CMT-RAD-2 — `allowed()` vs `policy_rules` on ReactivateImage — NEEDS YOUR RESPONSE

**Author:** Radomir Dopieralski | **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:265`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L265) | **PS:** 6

> Same here, the policy is called "reactivate".

**AI Assessment:** This is a blocking reference comment tied to CMT-RAD-1. Radomir is flagging the same `allowed()` vs `policy_rules` question on the `ReactivateImage` action. The same analysis applies — `allowed()` is needed for the status check (`image.status == "deactivated"`).

**Deep Dive:** [Code Analysis](bridge-artifacts/cmt-rad-2-analysis.md)

**Answer Summary:**
- Same analysis as CMT-RAD-1 — `policy_rules` handles RBAC, `allowed()` handles state filtering
- Without `allowed()`, the Reactivate button would appear on active images
- See [CMT-RAD-1 analysis](bridge-artifacts/cmt-rad-1-analysis.md) for the complete investigation

**Suggested Response:**
> Same analysis as above — `policy_rules` handles RBAC ("can this user reactivate?") and `allowed()` handles state visibility ("only show on deactivated images"). Both are needed. See my reply on the DeactivateImage comment for the full reasoning.

**Status for Owen McGonagle:** Copy the suggested response to Gerrit.

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| Tatiana Ovchinnikova | 1 | 1 | 0 |
| Radomir Dopieralski | 3 | 0 | 3 |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| ~~Add `Partially-Implements: blueprint removing-angularjs` to commit message~~ | ~~HIGH~~ | ~~RESOLVED~~ |
| ~~Remove WIP status~~ | ~~MEDIUM~~ | ~~RESOLVED~~ |
| Respond to Radomir on `allowed()` vs `policy_rules` (CMT-RAD-1, CMT-RAD-2) | HIGH | OPEN |
| Get Code-Review +2 (×2) and Workflow +1 | HIGH | OPEN |
| ~~Zuul Verified +1 on PS6~~ | ~~MEDIUM~~ | ~~RESOLVED~~ |
