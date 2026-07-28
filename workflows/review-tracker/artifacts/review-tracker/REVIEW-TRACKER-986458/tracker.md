# Review 986458 — Live Comment Tracker

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986458](https://review.opendev.org/c/openstack/horizon/+/986458)
**Title:** Add activate/deactivate row actions to Images table
**Author:** Owen McGonagle
**Status:** NEW (in gate pipeline)
**Current Patchset:** PS8
**Zuul:** Verified +1 (PS8 — build succeeded, gate jobs started)
**Files Changed:** 2 ([`openstack_dashboard/dashboards/project/images/images/tables.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py), [`openstack_dashboard/dashboards/project/images/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/tests.py))
**Reviewers:** Tatiana Ovchinnikova, Radomir Dopieralski, Jan Jasek

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
| 6 | 2026-07-16T15:45:00Z | AI (Claude) | Recheck — Owen posted detailed response on CMT-RAD-1 (15:38 UTC) addressing owner check concern with codebase evidence. CMT-RAD-1 now POSTED — WAITING FOR RESPONSE from Radomir. CMT-RAD-2 still needs response. |
| 7 | 2026-07-21T15:30:00Z | AI (Claude) | Recheck — Major progress: Owen responded on CMT-RAD-2 (Jul 16). Radomir accepted approach, gave CR+2, deferred owner check to follow-up (Jul 17). Jan Jasek tested in devstack, gave CR+2/W+1 (Jul 21). PS6 gate failed (merge conflict). Radomir rebased to PS7/PS8 fixing conflict, re-voted CR+2/W+1. Zuul Verified +1 on PS8. Review now in gate pipeline. All threads RESOLVED. |

---

## Change Log

### Scan #7 — 2026-07-21T15:30:00Z

1. **UPDATED** [CMT-RAD-2](#cmt-rad-2): Owen responded (16:52 UTC Jul 16) referencing CMT-RAD-1 discussion. Thread status → RESOLVED.
2. **NEW** [CMT-RAD-3](#cmt-rad-3): Radomir accepted the approach (06:56 UTC Jul 17) — "Let's explore this in followup patches. The code looks good otherwise, thank you for your contribution." Code-Review +2.
3. **NEW** [CMT-JAN-1](#cmt-jan-1): Jan Jasek tested in devstack and approved (11:42 UTC Jul 21) — "Works in devstack, code looks good to me, thanks!" Code-Review +2, Workflow +1.
4. **UPDATED** [CMT-RAD-1](#cmt-rad-1): Thread status → RESOLVED. Radomir's CR+2 and patchset-level comment ("Let's explore this in followup patches") effectively close the owner check discussion.
5. **UPDATED** [Score Summary](#score-summary): PS6 Verified -2 (merge conflict) → Radomir rebased to PS8 → CR+2 (Radomir), CR+2/W+1 (Jan Jasek, copied), Verified +1 (Zuul PS8).
6. **UPDATED** [Header](#review-986458--live-comment-tracker): PS6 → PS8. Zuul Verified +1. Gate jobs started.
7. **UPDATED** [What Needs to Change](#what-needs-to-change): All entries struck through — both threads resolved by reviewer acceptance.
8. **UPDATED** [Key Remaining Items](#key-remaining-items-before-this-can-merge): CR+2 (x2) RESOLVED, W+1 RESOLVED. Only gate passage remaining.

### Scan #6 — 2026-07-16T15:45:00Z

1. **UPDATED** [CMT-RAD-1](#cmt-rad-1): Owen posted detailed response (15:38 UTC) addressing the owner check concern. Cited admin panel overrides, existing convention (DeleteImage/EditImage/UpdateMetadata), PolicyTargetMixin alternative, and offered follow-up path. Thread status → POSTED — WAITING FOR RESPONSE from Radomir.
2. **UPDATED** [What Needs to Change — Scan #5](#scan-5--2026-07-16): CMT-RAD-1 entry struck through — response posted. CMT-RAD-2 still pending.
3. **UPDATED** [Comment Statistics](#comment-statistics): Owen's comment count 1 → 2.

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

~~**CMT-RAD-1: Respond to Radomir's updated question — is `allowed()` redundant with `policy_rules`?**~~

~~- **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:233`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L233)~~
~~- **What the code does now:** `DeactivateImage` defines both `policy_rules = (("image", "deactivate"),)` and an `allowed()` method that checks `image.protected`, `image.owner`, and `image.status == "active"`.~~
~~- **Comment update:** Radomir self-corrected his original comment. His initial ask was "add RBAC policy check" — but after noticing `policy_rules` is already defined, he pivoted to: "is the `allowed()` method then redundant?" **Address the updated question, not the original.**~~
~~- **Action required:** Respond on Gerrit. Acknowledge his self-correction, then explain that `allowed()` is NOT redundant — it handles state-based visibility (status check), while `policy_rules` handles RBAC authorization. The framework combines them with AND logic. No code change needed. See [deep-dive analysis](bridge-artifacts/cmt-rad-1-analysis.md).~~
~~- **Why:** Without the status check in `allowed()`, the Deactivate button would appear on already-deactivated images. RBAC policy cannot filter by image state. 58 actions in the codebase follow this same dual pattern.~~

**Resolved in Scan #7** — Owen responded on Gerrit (Scans #5-6). Radomir accepted the approach (CR+2, Jul 17): "Let's explore this in followup patches."

~~**CMT-RAD-2: Same owner check concern applies to ReactivateImage**~~

~~- **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:265`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L265)~~
~~- **What the code does now:** `ReactivateImage` defines `policy_rules = (("image", "reactivate"),)` and `allowed()` checks `image.owner` and `image.status == "deactivated"`.~~
~~- **Comment update (inherited from CMT-RAD-1 Scan #5):** Radomir's owner check concern on CMT-RAD-1 applies equally here. Whatever decision is made on the DeactivateImage owner check should be applied consistently to ReactivateImage.~~
~~- **Action required:** Respond on Gerrit referencing the DeactivateImage explanation. The decision on the owner check applies to both actions. See [deep-dive analysis](bridge-artifacts/cmt-rad-2-analysis.md).~~

**Resolved in Scan #7** — Owen responded (Jul 16). Radomir accepted (CR+2, Jul 17), deferred owner check to follow-up.

### Scan #5 — 2026-07-16

~~**CMT-RAD-1: Respond to Radomir's owner check concern**~~

~~- **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:231`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L231)~~
~~- **Action required:** Respond to Radomir. Three possible approaches — see [deep-dive analysis](bridge-artifacts/cmt-rad-1-analysis.md).~~

**Resolved in Scan #6** — Owen posted detailed response on Gerrit (15:38 UTC Jul 16) citing admin panel overrides, existing convention, and offering `PolicyTargetMixin` follow-up. Waiting for Radomir's decision.

**Resolved in Scan #7** — Radomir accepted: "Let's explore this in followup patches." (CR+2, Jul 17)

---

## Where Things Are At / What To Do Next

### Overall Status

This review adds Deactivate and Reactivate row actions to the Images table as part of the de-angularize initiative (topic: `de-angularize`). The review has been **approved and is in the gate pipeline**.

**Since Scan #6:** The owner check discussion concluded — Radomir accepted Owen's approach and deferred the owner check question to follow-up patches (Code-Review +2, Jul 17). Jan Jasek independently tested in devstack and gave Code-Review +2 + Workflow +1 (Jul 21). PS6 hit a merge conflict in the gate. Radomir helpfully rebased the change (PS7→PS8), resolved the conflict in `tables.py`, and re-voted Code-Review +2 + Workflow +1. Zuul passed check on PS8 and the review entered the gate pipeline (Jul 21 15:24 UTC).

### Score Summary

| Label | Value | From |
|-------|-------|------|
| Verified | +1 | Zuul (PS8, 2026-07-21) — gate jobs started |
| Code-Review | +2 | Radomir Dopieralski (PS8, 2026-07-21) |
| Code-Review | +2 | Jan Jasek (PS6, 2026-07-21, copied to PS8) |
| Workflow | +1 | Radomir Dopieralski (PS8, 2026-07-21) |

### PS6 Merge Failure — What Happened

The gate pipeline attempted to merge PS6 but failed with:

> Merge Failed. This change or one of its cross-repo dependencies was unable to be automatically merged with the current state of its repository. Please rebase the change and upload a new patchset.

This is a **merge conflict**, not a code quality issue. Between when PS6 was uploaded (Jul 15) and when it entered the gate (Jul 21), other changes merged to `master` that modified `openstack_dashboard/dashboards/project/images/images/tables.py`, creating a conflict. Radomir rebased the change (PS7), resolved the Git conflict in `tables.py`, published PS8, and re-voted. No code logic changed — only the rebase resolution.

### What You Should Do Next

1. **Wait for the gate** — PS8 is in the gate pipeline now (started 15:24 UTC Jul 21). If gate passes, the review merges automatically.
2. **If gate fails again** — rebase and push PS9 (another merge conflict is possible if the gate queue is long)
3. **Follow-up work** — Radomir wants a follow-up patch exploring `PolicyTargetMixin` for image actions (to let RBAC handle cross-project ownership instead of hardcoded owner checks)

### Open Threads Requiring Attention

| Thread | File | Status | Owner | Priority |
|--------|------|--------|-------|----------|
| [CMT-TAT-1](#cmt-tat-1) | /PATCHSET_LEVEL | RESOLVED | — | — |
| [CMT-RAD-1](#cmt-rad-1) | tables.py:233 | RESOLVED | — | — |
| [CMT-RAD-2](#cmt-rad-2) | tables.py:265 | RESOLVED | — | — |
| [CMT-RAD-3](#cmt-rad-3) | /PATCHSET_LEVEL | RESOLVED (acceptance) | — | — |
| [CMT-JAN-1](#cmt-jan-1) | /PATCHSET_LEVEL | RESOLVED (approval) | — | — |

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

<a name="cmt-rad-3"></a>

### CMT-RAD-3 — Reviewer acceptance, owner check deferred — RESOLVED

**Author:** Radomir Dopieralski | **File:** /PATCHSET_LEVEL | **PS:** 6

> Let's explore this in followup patches. The code looks good otherwise, thank you for your contribution.

**AI Assessment:** This is Radomir's resolution of the owner check discussion (CMT-RAD-1/CMT-RAD-2). He accepted Owen's approach — keep the current owner check for consistency with existing image actions, and explore `PolicyTargetMixin` as a follow-up. Accompanied by Code-Review +2, signaling full approval.

**Status for Owen McGonagle:** No action needed. Radomir approved. Consider filing a follow-up patch for `PolicyTargetMixin` exploration as discussed.

<a name="cmt-jan-1"></a>

### CMT-JAN-1 — Devstack testing approval — RESOLVED

**Author:** Jan Jasek | **File:** /PATCHSET_LEVEL | **PS:** 6

> Works in devstack, code looks good to me, thanks!

**AI Assessment:** Jan tested the change in devstack (functional validation) and reviewed the code. Code-Review +2 and Workflow +1. This is the second +2 vote needed for merge.

**Status for Owen McGonagle:** No action needed. Second CR+2 and W+1 secured.

---

## Inline Comments — Radomir Dopieralski

<a name="cmt-rad-1"></a>

### CMT-RAD-1 — Owner check in `DeactivateImage.allowed()` — RESOLVED

**Author:** Radomir Dopieralski | **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:233`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L233) | **PS:** 6

> I think this should be an RBAC policy check -- the logic you have here matches the default policy, but this can be changed in a particular OpenStack install. I believe the policy for this is in glance and is called "deactivate". You will need to pass the image as the target to the check.

**Self-Correction (Radomir Dopieralski, PS6, 15:37 UTC):**
> Sorry, I didn't notice that you already have policy_rules defined on this action. In this case the allowed method should not be needed?

**Owen's Reply (PS6, 01:59 UTC Jul 16):**
> I believe without the check on allowed() we de-activate button may appear on already de-activiated messages - I am testing that theory right now.

**Radomir's Follow-Up (PS6, 07:30 UTC Jul 16):**
> Good point. But the owner check seems harmful, especially if the policy is changed to allow changing images that are not yours?

**Owen's Response (PS6, 15:38 UTC Jul 16):**
> For reference, the admin panel overrides the owner check entirely -- it trusts RBAC policy. AdminDeleteImage and AdminEditImage both return True without owner checks:
>
> https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L29-L41
>
>     class AdminDeleteImage(project_tables.DeleteImage):
>         def allowed(self, request, image=None):
>             if image and image.protected:
>                 return False
>             return True   # No owner check
>
>     class AdminEditImage(project_tables.EditImage):
>         def allowed(self, request, image=None):
>             return True   # No owner check
>
> Notably, the admin panel does not have Deactivate/Reactivate actions at all today.
>
> If a Glance policy is `changed to let users deactivate` images from other projects, the Deactivate button would still not appear in the project panel due to this check.
>
> I do not think removing the check is the right thing to do today:
>
> - DeleteImage (line 135) and EditImage (line 163) both have the same owner check
> - Removing it only from Deactivate/Reactivate would be inconsistent with the existing image actions
>
> They use `PolicyTargetMixin` to pass resource ownership to the RBAC check, letting policy decide:
>
> https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47
>
>     class VolumePolicyTargetMixin(policy.PolicyTargetMixin):
>         policy_target_attrs = (("project_id", 'os-vol-tenant-attr:tenant_id'),)
>
> Image actions don't use this pattern today.
>
> `As a follow-up`, we could explore adopting PolicyTargetMixin for image actions -- that would let operators who modify the Glance policy to allow cross-project deactivation see the button appear correctly, without hardcoding ownership logic in allowed().

**Resolution (Radomir, PS6, 06:56 UTC Jul 17):**
Radomir accepted Owen's approach via patchset-level comment: "Let's explore this in followup patches. The code looks good otherwise, thank you for your contribution." Accompanied by Code-Review +2.

**AI Assessment:** This thread evolved through four phases and reached resolution:
1. "Add RBAC" — resolved: `policy_rules` already exists
2. "Is `allowed()` redundant?" — resolved: Radomir accepts the status check is needed ("Good point")
3. "The owner check is harmful" — Owen responded with convention evidence and admin panel precedent
4. **Resolved** — Radomir accepted the current approach, deferred owner check to follow-up patches

The discussion was productive and led to a concrete follow-up item (`PolicyTargetMixin` for image actions).

**Deep Dive:** [Code Analysis](bridge-artifacts/cmt-rad-1-analysis.md)

**Status for Owen McGonagle:** Done. Thread resolved. Consider filing a follow-up patch for `PolicyTargetMixin`.

<a name="cmt-rad-2"></a>

### CMT-RAD-2 — Owner check in `ReactivateImage.allowed()` — RESOLVED

**Author:** Radomir Dopieralski | **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:265`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L265) | **PS:** 6

> Same here, the policy is called "reactivate".

**Owen's Reply (PS6, 16:52 UTC Jul 16):**
> I believe my last response above applies here also.

**AI Assessment:** Blocking reference comment tied to CMT-RAD-1 (Code-Review -1). Resolved by Owen's response referencing the CMT-RAD-1 discussion, and Radomir's acceptance (CR+2, Jul 17).

**Deep Dive:** [Code Analysis](bridge-artifacts/cmt-rad-2-analysis.md)

**Status for Owen McGonagle:** Done. Thread resolved alongside CMT-RAD-1.

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| Tatiana Ovchinnikova | 1 | 1 | 0 |
| Radomir Dopieralski | 5 | 5 | 0 |
| Owen McGonagle | 3 | 3 | 0 |
| Jan Jasek | 1 | 1 | 0 |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| ~~Add `Partially-Implements: blueprint removing-angularjs` to commit message~~ | ~~HIGH~~ | ~~RESOLVED~~ |
| ~~Remove WIP status~~ | ~~MEDIUM~~ | ~~RESOLVED~~ |
| ~~Respond to Radomir on CMT-RAD-1 owner check concern~~ | ~~HIGH~~ | ~~RESOLVED (posted 15:38 UTC Jul 16)~~ |
| ~~Respond to Radomir on CMT-RAD-2 (reference CMT-RAD-1 response)~~ | ~~MEDIUM~~ | ~~RESOLVED (posted 16:52 UTC Jul 16)~~ |
| ~~Wait for Radomir's decision on owner check approach~~ | ~~HIGH~~ | ~~RESOLVED (accepted Jul 17, CR+2)~~ |
| ~~Get Code-Review +2 (x2) and Workflow +1~~ | ~~HIGH~~ | ~~RESOLVED (Radomir CR+2, Jan CR+2/W+1)~~ |
| ~~Zuul Verified +1~~ | ~~MEDIUM~~ | ~~RESOLVED (PS8)~~ |
| ~~PS6 merge conflict~~ | ~~HIGH~~ | ~~RESOLVED (Radomir rebased to PS8)~~ |
| Gate pipeline passage | HIGH | IN PROGRESS (started 15:24 UTC Jul 21) |
