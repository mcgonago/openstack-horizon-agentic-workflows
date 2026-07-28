# Review 986478 — Live Comment Tracker

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
**Title:** Update filtering in the Images table
**Author:** Owen McGonagle
**Status:** NEW
**Current Patchset:** PS5
**Zuul:** Verified +1 (PS5 — build succeeded)
**Files Changed:** 5 ([`openstack_dashboard/dashboards/project/images/images/tables.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py), [`openstack_dashboard/dashboards/project/images/views.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/views.py), [`openstack_dashboard/dashboards/project/images/images/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tests.py), [`openstack_dashboard/dashboards/project/images/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/tests.py), [`openstack_dashboard/dashboards/project/instances/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/instances/tests.py))
**Reviewers:** Tatiana Ovchinnikova, Radomir Dopieralski

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

| # | Timestamp | Scanner | Notes |
|---|-----------|---------|-------|
| 1 | 2026-07-15 | AI (Claude) | Initial scan — 1 comment thread from 1 reviewer |
| 2 | 2026-07-15 | AI (Claude) | Recheck — PS3+PS4 uploaded, CMT-TAT-1 resolved, all votes reset, new file added |
| 3 | 2026-07-16T16:00:00Z | AI (Claude) | Recheck — PS5 uploaded (commit message update), marked Ready For Review, Zuul Verified +1. New reviewer Radomir Dopieralski: Code-Review -1 with 2 comments. Deep-dive analysis on both threads. |

---

## Change Log

### Scan #3 — 2026-07-16T16:00:00Z

1. **UPDATED** Header: Patchset 4 → 5, Zuul Verified +1, Ready For Review, added Radomir Dopieralski to reviewers
2. **NEW** [CMT-RAD-1](#cmt-rad-1): Radomir (patchset-level) — positive feedback + suggestion to use substring matching for image name filter
3. **NEW** [CMT-RAD-2](#cmt-rad-2): Radomir (inline on `tables.py:210`) — requests adding visibility and owner as filter options
4. **UPDATED** [Score Summary](#score-summary): Zuul Verified +1 (PS5), Code-Review -1 from Radomir (PS5)
5. **NEW** [What Needs to Change — Scan #3](#scan-3--2026-07-16): Two new entries for Radomir's filter suggestions
6. **NEW** Deep-dive bridge artifacts: [CMT-RAD-1 analysis](bridge-artifacts/986478-cmt-rad-1-analysis.md), [CMT-RAD-2 analysis](bridge-artifacts/986478-cmt-rad-2-analysis.md)

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

### Scan #3 — 2026-07-16

~~**CMT-RAD-2: Add visibility and owner to filter_choices**~~

- ~~**File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:210`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L210)~~
- ~~**What the code does now:** `ImageFilterAction.filter_choices` includes `name`, `status`, and `disk_format` only.~~
- ~~**What the reviewer wants:** Add `visibility` and `owner` as additional filter options in the dropdown.~~
- ~~**Resolved via `--update-feature` on 2026-07-16.** Both `visibility` and `owner` added to filter_choices. See [design doc](../../../../../ioshaworkflow/docs/IOSHAWORKFLOW_REVIEW_986478_ADD_VISIBILITY_OWNER_DESIGN.md).~~

---

## Feature Updates

### Review 986478 — Add Visibility and Owner Filter Choices — 2026-07-16

**Source:** [IOSHAWORKFLOW_REVIEW_986478_ADD_VISIBILITY_OWNER_IMPLEMENTATION.md](/home/omcgonag/Work/mymcp/workspace/iproject/projects/ioshaworkflow/repo/ioshaworkflow/docs/IOSHAWORKFLOW_REVIEW_986478_ADD_VISIBILITY_OWNER_IMPLEMENTATION.md)
**Design:** [IOSHAWORKFLOW_REVIEW_986478_ADD_VISIBILITY_OWNER_DESIGN.md](/home/omcgonag/Work/mymcp/workspace/iproject/projects/ioshaworkflow/repo/ioshaworkflow/docs/IOSHAWORKFLOW_REVIEW_986478_ADD_VISIBILITY_OWNER_DESIGN.md)
**Threads Addressed:** CMT-RAD-2

| # | File | Change | Status |
|---|------|--------|--------|
| 1 | `openstack_dashboard/dashboards/project/images/images/tables.py:206-210` | Add visibility and owner to filter_choices | APPLIED |
| 2 | `openstack_dashboard/dashboards/project/images/images/tests.py:363-368` | Add assertIn for visibility and owner | APPLIED |

**Checkout:** `/home/omcgonag/Work/mymcp/workspace/iproject/projects/review_986478/reviews/horizon-review-986478`
**Commit:** `d7da19c2f`

---

## Where Things Are At / What To Do Next

### Overall Status

Review 986478 replaces the tab-based `OwnerFilter` with a server-side `ImageFilterAction` search dropdown in the project Images table, mirroring the admin panel pattern. Owen pushed PS5 (commit message update, 2026-07-16 01:52 UTC), marked Ready For Review, and Zuul passed (+1). Radomir Dopieralski reviewed and gave Code-Review -1 with two comments: (1) a patchset-level suggestion to use substring matching for the name filter (marked resolved by Radomir, so more of a suggestion than a blocker), and (2) an inline request to add visibility and owner as filter choices (marked unresolved). Deep-dive analysis shows the substring match is a Glance API limitation (not easily changed), while adding visibility is straightforward and should be done.

### Score Summary

| Label | Value | From | Date |
|-------|-------|------|------|
| Verified | +1 | Zuul (PS5) | 2026-07-16 |
| Code-Review | -1 | Radomir Dopieralski (PS5) | 2026-07-16 |
| Workflow | 0 | — | — |

### What You Should Do Next

1. **Add `visibility` to filter_choices (CMT-RAD-2)** — This is the actionable request. Add `('visibility', _('Visibility ='), True)` to `ImageFilterAction.filter_choices`. Ask Radomir whether `owner` is also needed (requires UUID, less user-friendly).
2. **Respond to Radomir on CMT-RAD-1** — Explain the substring matching is a Glance API limitation, consistent with admin panel. This is marked resolved so likely not blocking.
3. **Respond to Radomir on CMT-RAD-2** — Acknowledge and confirm you'll add visibility. Clarify whether owner is also needed.
4. **Push updated patchset** — After adding visibility, push PS6 and wait for CI + re-review.
5. **Get Code-Review +2 (x2) and Workflow +1** — Need two +2 votes from core reviewers.

### Open Threads Requiring Attention

| Thread | File | Status | Owner | Priority |
|--------|------|--------|-------|----------|
| [CMT-RAD-1](#cmt-rad-1) | /PATCHSET_LEVEL | NEEDS YOUR RESPONSE | Owen | MEDIUM |
| [CMT-RAD-2](#cmt-rad-2) | tables.py:210 | NEEDS YOUR RESPONSE | Owen | HIGH |
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

<a name="cmt-rad-1"></a>

### CMT-RAD-1 — Substring matching for image name filter — NEEDS YOUR RESPONSE

**Author:** Radomir Dopieralski | **File:** /PATCHSET_LEVEL | **PS:** 5

> This looks great, thanks.
>
> I noticed that the image name must match exactly to be shown by the filter, wouldn't it make more sense to make the filter show all images that contain the string?

**AI Assessment:** Suggestion, not a hard blocker. Radomir marked this comment as `unresolved: false`, indicating it's more of a "have you considered" question than a blocking concern. The exact-match behavior is inherited from the Glance v2 API's `name` filter, and it matches the existing admin Images panel filter (`AdminImageFilterAction` also uses `"Image Name ="` with exact match). Changing to substring would require either client-side filtering (breaking server-side pagination) or a hybrid approach not used anywhere else in Horizon.

**Deep Dive:** [Code Analysis](bridge-artifacts/986478-cmt-rad-1-analysis.md)

**Answer Summary:**
- The Glance v2 API `name` filter performs exact matching — this is an API limitation, not a code choice
- The admin Images panel (`AdminImageFilterAction`) uses the same exact-match behavior with `"Image Name ="`
- Every server-type filter across all Horizon panels uses exact match (`=` labels)
- Changing to substring would require client-side filtering (breaks pagination) or a custom hybrid approach
- No other panel implements substring matching

**Suggested Response:**
> Thanks! The exact-match behavior is inherited from the Glance v2 API -- the name filter doesn't support substring matching. This matches how the admin Images filter works too (same filter_choices with "Image Name ="). Changing to substring would require either client-side filtering (which breaks pagination for large image lists) or a hybrid approach that no other panel uses. I kept it consistent with the admin pattern, but happy to explore a follow-up if there's demand for substring search.

**Status for Owen McGonagle:** Respond on Gerrit explaining the Glance API limitation. This is low priority since Radomir marked it resolved.

---

## Inline Comments — Radomir Dopieralski

<a name="cmt-rad-2"></a>

### CMT-RAD-2 — Add visibility and owner filter choices — NEEDS YOUR RESPONSE

**Author:** Radomir Dopieralski | **File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:210`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L210) | **PS:** 5

> could we also have visibility and owner as the possible filters?

**AI Assessment:** Actionable suggestion (Code-Review -1). Radomir is asking for additional filter choices. Both `visibility` and `owner` are valid Glance v2 API filter parameters. Adding `visibility` is straightforward and restores the filtering capability that was lost when the old `OwnerFilter` tabs were removed (users could previously filter by "Project", "Public", "Shared", etc.). The `owner` filter is technically valid but requires users to type a project UUID, which is less user-friendly than the old tab-based `OwnerFilter` that abstracted this away. Recommend adding at least `visibility`.

**Deep Dive:** [Code Analysis](bridge-artifacts/986478-cmt-rad-2-analysis.md)

**Answer Summary:**
- Both `visibility` and `owner` are valid Glance v2 API filter parameters, supported by Horizon's `glance.py`
- The admin panel (`AdminImageFilterAction`) doesn't have these filters either
- Adding `visibility` is a 1-line addition: `('visibility', _('Visibility ='), True)`
- Adding `owner` is valid but requires UUID input, less user-friendly than the old `OwnerFilter` tabs
- The old `OwnerFilter` did client-side categorization (Project/Public/Shared tabs) — adding `visibility` as a server-side filter partially restores this capability

**Suggested Response:**
> Good idea. I can add visibility -- that's a straightforward Glance v2 filter and would restore the ability to filter by public/private/shared/community that the old OwnerFilter tabs provided. For owner, the Glance API expects a project UUID which isn't very user-friendly (the old tabs abstracted this away). I'll add visibility in the next patchset. Want me to add owner as well, or is visibility sufficient?

**Status for Owen McGonagle:** Add `visibility` to `filter_choices`, respond on Gerrit confirming and asking about `owner`. Push a new patchset.

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| Tatiana Ovchinnikova | 1 | 1 | 0 |
| Radomir Dopieralski | 2 | 0 | 2 |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| ~~Add `Partially-Implements: blueprint removing-angularjs` to commit message~~ | ~~HIGH~~ | ~~RESOLVED (PS3)~~ |
| Add `visibility` to filter_choices (CMT-RAD-2) | HIGH | OPEN |
| Respond to Radomir on substring matching (CMT-RAD-1) | MEDIUM | OPEN |
| Clarify with Radomir whether `owner` filter is also needed | MEDIUM | OPEN |
| ~~Wait for Zuul CI on PS4~~ | ~~HIGH~~ | ~~RESOLVED (PS5 Verified +1)~~ |
| Get Code-Review +2 (x2) and Workflow +1 | HIGH | OPEN |
