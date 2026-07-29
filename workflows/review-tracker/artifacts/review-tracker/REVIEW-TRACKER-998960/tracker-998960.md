# Review 998960 — Live Comment Tracker

**Review:** [https://review.opendev.org/c/openstack/horizon/+/998960](https://review.opendev.org/c/openstack/horizon/+/998960)
**Title:** Add per-provider SSO logout redirect support
**Author:** Owen McGonagle
**Status:** NEW
**Current Patchset:** 7
**Zuul:** Not voted (PS7 pending)
**Files Changed:** 5 ([`openstack_auth/views.py`](https://github.com/openstack/horizon/blob/master/openstack_auth/views.py), [`openstack_auth/defaults.py`](https://github.com/openstack/horizon/blob/master/openstack_auth/defaults.py), [`openstack_auth/tests/unit/test_auth.py`](https://github.com/openstack/horizon/blob/master/openstack_auth/tests/unit/test_auth.py), [`doc/source/configuration/settings.rst`](https://github.com/openstack/horizon/blob/master/doc/source/configuration/settings.rst), release note)
**Reviewers:** None yet (awaiting first review)

---

## Initial Code Review

**Performed by:** `/horizon-code-review` (automated bridge)
**Verdict:** APPROVE
**Full Analysis:** [Code Review](bridge-artifacts/initial-review-998960.md)

### Summary

This change solves LP#2161654 (SSO logout broken in multi-provider deployments) by introducing `WEBSSO_LOGOUT_REDIRECT_MAPPING`, which enables per-provider logout redirect when multiple SSO authentication methods are configured. The implementation uses a 3-tier fallback system (per-provider → global SSO → legacy) with comprehensive test coverage, thorough documentation, and full backward compatibility.

### Blockers

None.

### Suggestions

1. **Minor: Tier 1 should exclude credentials users** — Add `auth_type != "credentials"` check to tier 1 (currently only in tier 2) to prevent misconfigured mapping from redirecting credentials users to SSO logout URLs
2. **Minor: Log message consistency** — Consider using `LOG.info('Using tier 1 logout for auth_type=%s: %s', auth_type, logout_url)` for consistency with tiers 2-3 and easier grepping

---

## Scan Log

| # | Timestamp | Scanner | Notes |
|---|-----------|---------|-------|
| 1 | 2026-07-29T16:58:00Z | AI (Claude) | Initial scan — 0 comment threads from 0 reviewers (no comments yet) |

---

## What Needs to Change

No blocking comments yet. The automated code review found the implementation sound with only minor non-blocking suggestions.

---

## Where Things Are At / What To Do Next

### Overall Status

PS7 was uploaded on 2026-07-29 (commit message update) and marked ready for review. This is the first formal review.

The change introduces `WEBSSO_LOGOUT_REDIRECT_MAPPING` to solve LP#2161654 (SSO logout broken in multi-provider deployments). The automated code review found:
- No plugin API breaking changes (purely additive)
- Comprehensive test coverage (9 new tests covering all tiers and edge cases)
- Excellent documentation (65 lines in settings.rst)
- Proper release note with features and deprecation sections
- Sound tiered fallback logic

The change depends on I8302cd390b954ee8abfa2340ff9fd0df8ad88120 (which introduces `WEBSSO_POST_LOGOUT_URL`). That parent change is still in review (status: NEW).

### Score Summary

| Label | Vote | By |
|-------|------|-----|
| Verified | Pending | Zuul (PS7) |
| Code-Review | None | Awaiting first review |
| Workflow | None | - |

### What You Should Do Next

1. **Wait for Zuul** — PS7 is currently running through CI gates
2. **Address minor suggestions** — Consider adding `auth_type != "credentials"` check to tier 1 for extra safety
3. **Monitor parent change** — This depends on I8302cd3 which is still in review
4. **Prepare for first reviewer** — No human reviewer comments yet

### Open Threads Requiring Attention

No comment threads yet.

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| *(No comments yet)* | 0 | 0 | 0 |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| Zuul CI gates (PS7) | HIGH | PENDING |
| First human Code-Review vote | HIGH | OPEN |
| Parent change I8302cd3 merge | HIGH | BLOCKED (parent still in review) |
| Address minor suggestions | LOW | OPEN |
