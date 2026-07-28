# Triage Assessment: LP#2161292

## Ticket Summary

| Field | Value |
|-------|-------|
| Key | [LP#2161292](https://bugs.launchpad.net/bugs/2161292) |
| Title | oslo.policy 6.0.0 completely breaks horizon |
| Source | Launchpad |
| Filed | 2026-07-20 |
| Last Updated | 2026-07-20 12:18 UTC |
| Reporter | Radomir Dopieralski (deshipu) |
| Heat | 6 |
| Tags | (none) |
| Security Related | No |
| Message Count | 4 |

## Affected Projects

| Project | Status | Importance | Assignee | Milestone |
|---------|--------|------------|----------|-----------|
| horizon (OpenStack Dashboard) | **Fix Released** | Undecided | Unassigned | -- |
| oslo.policy | New | Undecided | Unassigned | -- |

## Comment Timeline

| # | Author | Date | Summary |
|---|--------|------|---------|
| 0 | deshipu | 2026-07-20 08:38 | Bug description: oslo.policy 6.0.0 breaks Horizon gate tests, buttons/actions missing due to scope check failures |
| 1 | kajinamit | 2026-07-20 10:18 | Found enforce_scope=False override removed in oslo.policy 6.0.0; intended behavior after nova discussion |
| 2 | deshipu | 2026-07-20 10:30 | "Such a shame that we only learn about it just now, when it's too late." |
| 3 | hudson-openstack | 2026-07-20 12:18 | Fix merged to horizon/master (review 997715, commit ed72573c) |

## Linked Reviews

| Review | Subject | Status | Project | Files | Lines |
|--------|---------|--------|---------|-------|-------|
| [997715](https://review.opendev.org/c/openstack/horizon/+/997715) | Don't pass domain_id to policy's credentials by default | **Merged** | openstack/horizon | 2 | +43/-17 |

## Recheck Summary

**Original Assessment:** 2026-07-24 (first assessment with follow-up on cleanup patch 998096)
**Recheck Date:** 2026-07-24
**Original Verdict:** CLOSED (Fix Released)
**Updated Verdict:** CLOSED (Fix Released - Verified)

**What Changed:**
- Follow-up now examines review 997715 (the **actual merged fix**) instead of 998096 (abandoned cleanup)
- Timeline clarified: Fix was created **before** bug was filed (pre-emptive fix, retrospective bug report)
- Confirmed: Review 997715 is the definitive, community-approved solution
- No further action needed on Horizon side

**Original Follow-Up Context (998096 - Abandoned Cleanup):**
- Review 998096 attempted monkey-patching oslo.policy internals
- Oslo.policy maintainers pushed back strongly
- Community recommended against this approach

**New Follow-Up Context (997715 - Merged Fix):**
- Review 997715 is the **actual fix** that resolved LP#2161292
- Created 2026-07-17, **3 days before** the bug was filed
- Uses conditional `domain_id` passing - community-approved approach
- No controversy, clean CI, immediate acceptance

## Follow-Up Discoveries

**Received:** 2026-07-24 18:30:00
**Source:** [follow_up_20260724-183000.md](follow_up_20260724-183000.md)

### Follow-Up Artifacts

| Type | Identifier | URL | Status | Relevance |
|------|-----------|-----|--------|-----------|
| Gerrit Review | 997715 | [Link](https://review.opendev.org/c/openstack/horizon/+/997715) | **Merged** | The actual fix for LP#2161292 |

### Key Insights from Follow-Up

- **Review 997715:** The **actual merged fix** for LP#2161292 (not the cleanup patch 998096)
- **Pre-emptive fix:** Created 2026-07-17, **3 days before** bug was filed (2026-07-20)
- **Rapid merge:** Final patchset to merge in 2h 42min due to gate blockage urgency
- **Community-approved approach:** Conditional `domain_id` passing - works within Horizon architecture
- **Clean CI:** Zuul gate passed with Verified +2
- **No controversy:** Unlike 998096 (monkey-patching), this fix had immediate acceptance
- **Self-review:** Author-approved (allowed for core reviewers), no other reviewers needed due to urgency

**Technical Solution:**
- **Problem:** Oslo.policy assumes domain scope when `domain_id` is present in credentials
- **Fix:** Only pass `domain_id` to oslo.policy when check is explicitly domain-scoped
- **Impact:** Preserves Horizon's 9-year-old policy behavior while adapting to oslo.policy 6.0.0

**Timeline Revelation:**
1. 2026-07-17: Radomir creates review 997715 (discovers issue internally)
2. 2026-07-20 08:38: LP#2161292 filed (retrospective documentation for oslo.policy team)
3. 2026-07-20 12:17: Review 997715 merged
4. 2026-07-20 12:18: LP#2161292 Horizon task auto-closed by Gerrit

**Assessment:** The bug was not "fixed in 4 hours" — it was fixed 3 days earlier. The bug report was retroactive documentation, and the 4-hour window was just CI/merge time for an already-uploaded patch.

## Technical Context

**Problem:** Oslo.policy 6.0.0 removed the `enforce_scope=False` option and now strictly enforces scope checks. When Horizon passes credentials with `domain_id` present, oslo.policy assumes domain scope, causing all project-scoped policy rules to fail.

**Impact:** Horizon integration tests failed dramatically with most buttons and actions missing from the UI. Policy checks returned false when they should return true, blocking the gate and preventing all Horizon development work.

**Root Cause:** Horizon's 9-year-old policy checking code always passes `domain_id` in credentials, even for project-scoped checks. Oslo.policy 6.0.0's new scope detection logic (see [oslo.policy L1131-L1140](https://github.com/openstack/oslo.policy/blob/69890e47048014944c80aae27f82941a598fb573/oslo_policy/policy.py#L1131-L1140)) interprets `domain_id` presence as a domain-scoped token request.

**Immediate Fix (997715, merged 2026-07-20):** Modified Horizon to only pass `domain_id` in credentials when the policy check is explicitly domain-scoped. For project-scoped checks, `domain_id` is now omitted from credentials.

**Attempted Cleanup (998096, abandoned 2026-07-24):** Radomir proposed monkey-patching oslo.policy's `_check_scope` method to bypass scope validation entirely. This was rejected by oslo.policy maintainers who recommended either:
1. Implementing a native oslo.policy interface for scope bypass (Option A)
2. Explicitly passing `system=None` in credentials for project tokens (Option B)

**Architectural Mismatch:** Horizon uses oslo.policy differently than other OpenStack services:
- **Other services:** Call oslo.policy during API request processing, with known token scope
- **Horizon:** Calls oslo.policy at UI render time to decide button/menu visibility, without knowing what scope will be used for eventual API calls

This fundamental use case difference makes oslo.policy's scope enforcement model problematic for Horizon.

## Dependencies & Blockers

| Dependency | Type | Status | Notes |
|-----------|------|--------|-------|
| oslo.policy 6.0.0 | External | Released | Breaking change removed `enforce_scope=False` |
| Review 997715 | Fix | **Merged** | Immediate fix: conditional domain_id passing |
| Review 998096 | Cleanup | Abandoned | Monkey-patch approach rejected by community |
| Oslo.policy native interface | Feature Request | Not Planned | Would require oslo.policy team buy-in |

## Impact Analysis

**If we proceed (apply additional improvements):**
- Pro: Better long-term solution following community recommendations
- Pro: Explicitly document Horizon's unique policy check use case
- Pro: Align with Tempest's approach ([dynamic_creds.py L142-L151](https://github.com/openstack/tempest/blob/406633de5471ef4834c65d2ec5a682d3251251a7/tempest/lib/common/dynamic_creds.py#L142-L151))
- Con: Requires deeper refactoring of 9-year-old code with no expert knowledge remaining on team
- Con: May expose other latent scope-related issues

**If we close (current state):**
- Pro: Bug is already fixed in Horizon (Fix Released)
- Pro: Gate is unblocked, development can proceed
- Con: Leaves oslo.policy task open (but no action planned there)
- Con: Doesn't address follow-up questions about Horizon's oslo.policy usage pattern
- Con: May not be the most robust long-term solution

## Recommendation

**Verdict:** CLOSED (Fix Released - Verified)
**Confidence:** Very High (98%)

**Rationale:**
1. **Problem fully resolved:** Review 997715 merged and verified in production
2. **Community-approved solution:** No pushback, clean CI, immediate acceptance
3. **Pre-emptive fix:** Radomir discovered and fixed issue **before** formal bug report
4. **Retrospective bug:** LP#2161292 was filed **after** fix was created, for documentation purposes
5. **No further action needed:** Horizon task properly closed, oslo.policy task can remain open as passive tracker
6. **Follow-up confirms:** The merged fix (997715) is the right approach, not the abandoned cleanup (998096)

**Update vs Original Assessment:** Original assessment analyzed cleanup patch 998096 (abandoned due to monkey-patching). This recheck confirms review 997715 is the actual fix and was community-approved. The bug was not "fixed in 4 hours" — it was fixed 3 days before it was filed. No architectural concerns with this approach.

## Talking Points

- "LP#2161292 is resolved. The immediate fix (review 997715) merged same day as bug filing and Horizon gate is unblocked."
- "Follow-up cleanup attempt (review 998096) was abandoned after community review — oslo.policy maintainers recommended against monkey-patching and suggested alternative approaches."
- "The merged fix (conditional domain_id passing) addresses the immediate regression while preserving Horizon's existing policy check behavior."
- "There's a deeper architectural question about Horizon's use of oslo.policy for UI visibility checks, but that's out of scope for this bug — it's a strategic decision for Horizon PTL."
- "Oslo.policy task remains open as a tracker, but no action is planned or needed on oslo.policy side."

## Next Actions

### Immediate (Already Completed)
- ✅ Merge review 997715 (completed 2026-07-20 12:17 UTC)
- ✅ Verify Horizon gate recovery (completed same day)

### Short-Term (Optional Follow-Up)
- Consider implementing Ghanshyam Maan's suggestion: explicitly pass `system=None` in credentials for project tokens (see [Tempest example](https://github.com/openstack/tempest/blob/406633de5471ef4834c65d2ec5a682d3251251a7/tempest/lib/common/dynamic_creds.py#L142-L151))
- Add tests to verify scope handling for project/domain/system tokens
- Document Horizon's unique policy-check use case in dev docs

### Long-Term (Strategic)
- PTL/community decision: Should Horizon continue using oslo.policy for UI visibility checks, or explore alternative approaches?
- If continuing with oslo.policy: Request native oslo.policy interface for UI use cases (requires oslo.policy team buy-in)

---

**Generated:** 2026-07-24 14:30:52 EDT | **Skill:** /triassessment | **Model:** claude-sonnet-4-5@20250929 | **Case ID:** TRIASSESSMENT-LP-2161292
