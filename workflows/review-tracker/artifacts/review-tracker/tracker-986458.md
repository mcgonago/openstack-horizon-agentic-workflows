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

| # | Timestamp | Scanner | Notes |
|---|-----------|---------|-------|
| 1 | 2026-07-15 | AI (Claude) | Initial scan — 1 comment thread from 1 reviewer |
| 2 | 2026-07-15 | AI (Claude) | Recheck — PS5 commit message update, WIP removed, PS6 rebase. All votes reset. |
| 3 | 2026-07-15 | AI (Claude) | Recheck — New reviewer Radomir Dopieralski: Code-Review -1 with 2 inline threads on `tables.py`. Zuul Verified +1 on PS6. Deep-dive analysis on both threads. |
| 4 | 2026-07-16T01:27:00Z | AI (Claude) | Recheck — No new Gerrit activity. Surfaced Radomir's self-correction on CMT-RAD-1 as explicit Comment Update — reframed thread assessments and What Needs to Change around his updated question. Upgraded Scan Log to ISO timestamps. |
| 5 | 2026-07-16T13:45:00Z | AI (Claude) | Recheck — New replies: Owen responded on CMT-RAD-1 (01:59 UTC), Radomir followed up (07:30 UTC) pivoting to owner check concern. Deep-dive regenerated. |

---

## Change Log

### Scan #5 — 2026-07-16T13:45:00Z

1. **UPDATED** [CMT-RAD-1](#cmt-rad-1): Two new replies — Owen's response (01:59 UTC) defending status check, then Radomir's follow-up (07:30 UTC) pivoting to **owner check** concern: "the owner check seems harmful, especially if the policy is changed to allow changing images that are not yours?" Thread evolves from "is allowed() redundant?" to "is the owner check harmful?"
2. **UPDATED** [Deep Dive](bridge-artifacts/cmt-rad-1-analysis.md): Regenerated analysis — owner check matches all existing image actions (DeleteImage, EditImage, UpdateMetadata). Admin panel overrides remove it. Radomir's concern is valid in principle but removing it only here would be inconsistent.
3. **UPDATED** [What Needs to Change — Scan #5](#scan-5--2026-07-16): New entry addressing owner check question with three response options.
4. **UPDATED** [CMT-RAD-2](#cmt-rad-2): No new replies, but status updated — owner check concern from CMT-RAD-1 applies here too.

### Scan #4 — 2026-07-16T01:27:00Z

1. **UPDATED** [CMT-RAD-1](#cmt-rad-1): Surfaced Radomir's self-correction as a **Comment Update** — his reply supersedes the original ask (changed from "add RBAC" to "is `allowed()` redundant?"). AI Assessment, Suggested Response, and What Needs to Change updated to address the corrected question explicitly.
2. **UPDATED** [CMT-RAD-2](#cmt-rad-2): Added Comment Update noting this comment inherits the self-correction context from CMT-RAD-1.
3. **UPDATED** [What Needs to Change — Scan #3](#scan-3--2026-07-15-1): Reframed both entries around Radomir's updated question, not the original.
4. **UPDATED** [Scan Log](#scan-log): Upgraded from day-only dates to ISO 8601 timestamps.

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

**CMT-RAD-1: Respond to Radomir's updated question — is `allowed()` redundant with `policy_rules`?**

- **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:233`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L233)
- **What the code does now:** `DeactivateImage` defines both `policy_rules = (("image", "deactivate"),)` and an `allowed()` method that checks `image.protected`, `image.owner`, and `image.status == "active"`.
- **Comment update:** Radomir self-corrected his original comment. His initial ask was "add RBAC policy check" — but after noticing `policy_rules` is already defined, he pivoted to: "is the `allowed()` method then redundant?" **Address the updated question, not the original.**
- **Action required:** Respond on Gerrit. Acknowledge his self-correction, then explain that `allowed()` is NOT redundant — it handles state-based visibility (status check), while `policy_rules` handles RBAC authorization. The framework combines them with AND logic. No code change needed. See [deep-dive analysis](bridge-artifacts/cmt-rad-1-analysis.md).
- **Why:** Without the status check in `allowed()`, the Deactivate button would appear on already-deactivated images. RBAC policy cannot filter by image state. 58 actions in the codebase follow this same dual pattern.

**CMT-RAD-2: Same owner check concern applies to ReactivateImage**

- **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:265`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L265)
- **What the code does now:** `ReactivateImage` defines `policy_rules = (("image", "reactivate"),)` and `allowed()` checks `image.owner` and `image.status == "deactivated"`.
- **Comment update (inherited from CMT-RAD-1 Scan #5):** Radomir's owner check concern on CMT-RAD-1 applies equally here. Whatever decision is made on the DeactivateImage owner check should be applied consistently to ReactivateImage.
- **Action required:** Respond on Gerrit referencing the DeactivateImage explanation. The decision on the owner check applies to both actions. See [deep-dive analysis](bridge-artifacts/cmt-rad-2-analysis.md).

### Scan #5 — 2026-07-16

**CMT-RAD-1: Respond to Radomir's owner check concern**

- **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:231`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L231)
- **What the code does now:** `DeactivateImage.allowed()` returns `False` when `image.owner != request.user.tenant_id`, hiding the button on images not owned by the current user's project.
- **Context:** Radomir accepted the status check is needed (his earlier concern) but now flags the owner check as "harmful" because it overrides RBAC policy flexibility. If an operator changes Glance policy to let users deactivate other projects' images, the Horizon button still won't appear.
- **Investigation findings (deep-dive):**
  - The owner check matches ALL existing image actions: `DeleteImage` ([line 135](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L135)), `EditImage` ([line 163](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L163)), `UpdateMetadata` ([line 201](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L201))
  - The admin panel overrides remove the check: `AdminDeleteImage` and `AdminEditImage` both return `True` without owner checks ([admin/images/tables.py:29-41](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L29-L41))
  - The admin panel currently has NO Deactivate/Reactivate actions at all
  - The volume panel uses `PolicyTargetMixin` with `policy_target_attrs` as the proper architectural alternative, but image actions don't use this pattern
- **Action required:** Respond to Radomir. Three possible approaches — see [deep-dive analysis](bridge-artifacts/cmt-rad-1-analysis.md) for the suggested response offering Radomir the choice.
- **Why:** This is a valid architectural concern, but removing the owner check only from this patch while keeping it on DeleteImage/EditImage would be inconsistent. The response should acknowledge the concern and let Radomir decide the scope.

---

## Where Things Are At / What To Do Next

### Overall Status

This review adds Deactivate and Reactivate row actions to the Images table as part of the de-angularize initiative (topic: `de-angularize`). The implementation is clean — two new `BatchAction` subclasses (`DeactivateImage`, `ReactivateImage`) wired into `ImagesTable.row_actions`, with test updates for the new action count.

**Since Scan #4:** Owen replied on CMT-RAD-1 (01:59 UTC Jul 16) defending the status check in `allowed()`. Radomir responded (07:30 UTC Jul 16) accepting the status check but pivoting to a new concern: the **owner check** (`image.owner != request.user.tenant_id`) is "harmful" because it overrides RBAC policy flexibility. Deep-dive analysis confirms the owner check matches all existing image actions (`DeleteImage`, `EditImage`, `UpdateMetadata`) and the admin panel overrides remove it. Radomir's concern is architecturally valid but the convention is established. The conversation now needs a decision: keep for consistency, remove here, or address all image actions together.

### Score Summary

| Label | Value | From |
|-------|-------|------|
| Verified | +1 | Zuul (PS6, 2026-07-15) |
| Code-Review | -1 | Radomir Dopieralski (PS6, 2026-07-15) |
| Workflow | 0 | — |

### What You Should Do Next

1. **Respond to Radomir on Gerrit (CMT-RAD-1 and CMT-RAD-2)** — Use the suggested responses from the deep-dive analysis. Acknowledge his valid concern about the owner check overriding RBAC, show you've researched the codebase convention, and offer him the choice: (a) keep for consistency, (b) remove here, or (c) address all image actions in a separate patch.
2. **Wait for Radomir's decision** — The outcome may require a code change (removing owner checks) or not (keeping for consistency). No action until he responds.
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

### CMT-RAD-1 — Owner check in `DeactivateImage.allowed()` — NEEDS YOUR RESPONSE

**Author:** Radomir Dopieralski | **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:233`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L233) | **PS:** 6

> I think this should be an RBAC policy check -- the logic you have here matches the default policy, but this can be changed in a particular OpenStack install. I believe the policy for this is in glance and is called "deactivate". You will need to pass the image as the target to the check.

**Self-Correction (Radomir Dopieralski, PS6, 15:37 UTC):**
> Sorry, I didn't notice that you already have policy_rules defined on this action. In this case the allowed method should not be needed?

**Owen's Reply (PS6, 01:59 UTC Jul 16):**
> I believe without the check on allowed() we de-activate button may appear on already de-activiated messages - I am testing that theory right now.

**Radomir's Follow-Up (PS6, 07:30 UTC Jul 16):**
> Good point. But the owner check seems harmful, especially if the policy is changed to allow changing images that are not yours?

**Comment Update (Scan #5):** The conversation has evolved through three phases:
1. "Add RBAC" — resolved: `policy_rules` already exists
2. "Is `allowed()` redundant?" — resolved: Radomir accepts the status check is needed ("Good point")
3. **"The owner check is harmful"** — current question. Radomir's concern: the hardcoded `image.owner != request.user.tenant_id` check overrides RBAC policy flexibility. If an operator changes Glance policy to let users act on images they don't own, the Horizon button still won't appear.

**AI Assessment:** Blocking concern (Code-Review -1). Radomir's point is architecturally valid — hardcoded owner checks override RBAC policy flexibility. However, this is the established convention for ALL image actions in the project panel (`DeleteImage`, `EditImage`, `UpdateMetadata` all have the same check). The admin panel overrides to remove them (`AdminDeleteImage`, `AdminEditImage` return `True`). Removing the owner check only from `DeactivateImage` while keeping it on `DeleteImage`/`EditImage` would be inconsistent. This needs a decision from Radomir: keep for consistency, remove here, or address all image actions together.

**Deep Dive:** [Code Analysis](bridge-artifacts/cmt-rad-1-analysis.md)

**Answer Summary:**
- Radomir accepts the status check is needed; his concern has narrowed to the **owner check** specifically
- The owner check matches ALL existing image actions: `DeleteImage` ([line 135](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L135)), `EditImage` ([line 163](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L163)), `UpdateMetadata` ([line 201](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L201))
- The admin panel overrides remove the check: `AdminDeleteImage` and `AdminEditImage` both return `True` ([admin/images/tables.py:29-41](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L29-L41))
- The admin panel currently has NO Deactivate/Reactivate actions — admins can't use these through the UI
- The volume panel uses `PolicyTargetMixin` as the proper architectural alternative, but no image action uses it

**Suggested Response:**
> Good point -- you're right that the hardcoded owner check does override RBAC flexibility. If an operator changes the Glance policy to let non-owners deactivate images, the button still wouldn't appear.
>
> I kept the owner check because it matches the existing convention for all image actions in the project panel -- DeleteImage (line 135), EditImage (line 163), and UpdateMetadata (line 201) all do the same check. The admin panel overrides it (AdminDeleteImage and AdminEditImage both return True without owner checks).
>
> I can go either way:
> 1. Keep the owner check for consistency with the existing actions (and add AdminDeactivateImage/AdminReactivateImage to the admin panel in a follow-up)
> 2. Remove the owner check from DeactivateImage/ReactivateImage to be more policy-flexible -- but that would make them inconsistent with Delete/Edit
>
> Which approach would you prefer? Or should the owner check removal be a separate patch that addresses all image actions together?

**Status for Owen McGonagle:** Copy the suggested response to Gerrit. This response acknowledges Radomir's valid concern, shows you've researched the codebase convention, and gives him the choice on how to proceed.

<a name="cmt-rad-2"></a>

### CMT-RAD-2 — Owner check in `ReactivateImage.allowed()` — NEEDS YOUR RESPONSE

**Author:** Radomir Dopieralski | **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:265`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L265) | **PS:** 6

> Same here, the policy is called "reactivate".

**Comment Update (inherited from CMT-RAD-1 Scan #5):** This comment was posted before
Radomir's self-correction and follow-ups on CMT-RAD-1, but "Same here" logically
inherits all the context. Radomir's latest concern (the owner check being harmful)
applies equally to `ReactivateImage`, which has the same `image.owner != request.user.tenant_id`
check at [line 263](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L263).

**AI Assessment:** Blocking reference comment tied to CMT-RAD-1 (Code-Review -1). Whatever decision is made about the owner check on `DeactivateImage` should be applied consistently to `ReactivateImage`. The status check (`image.status == "deactivated"`) is needed regardless — without it, the Reactivate button would appear on active images.

**Deep Dive:** [Code Analysis](bridge-artifacts/cmt-rad-2-analysis.md)

**Answer Summary:**
- Same analysis as CMT-RAD-1 — owner check concern applies equally
- Status check is needed regardless of owner check decision
- Whatever approach Radomir picks for CMT-RAD-1 should apply here too
- See [CMT-RAD-1 analysis](bridge-artifacts/cmt-rad-1-analysis.md) for the complete investigation

**Suggested Response:**
> Same approach here -- whatever we decide about the owner check on DeactivateImage will apply to ReactivateImage too. The status check (only showing Reactivate on deactivated images) is needed either way. See my reply on the DeactivateImage comment for the full details and the options.

**Status for Owen McGonagle:** Copy the suggested response to Gerrit. Reference your CMT-RAD-1 response for the full owner check discussion.

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| Tatiana Ovchinnikova | 1 | 1 | 0 |
| Radomir Dopieralski | 4 | 0 | 4 |
| Owen McGonagle | 1 | 0 | 1 |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| ~~Add `Partially-Implements: blueprint removing-angularjs` to commit message~~ | ~~HIGH~~ | ~~RESOLVED~~ |
| ~~Remove WIP status~~ | ~~MEDIUM~~ | ~~RESOLVED~~ |
| Respond to Radomir on owner check concern (CMT-RAD-1, CMT-RAD-2) | HIGH | OPEN |
| Get Code-Review +2 (×2) and Workflow +1 | HIGH | OPEN |
| ~~Zuul Verified +1 on PS6~~ | ~~MEDIUM~~ | ~~RESOLVED~~ |
