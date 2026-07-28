# Triage Assessment: Review 996428

**Review:** [996428](https://review.opendev.org/c/openstack/horizon/+/996428)  
**Generated:** 2026-07-28 16:25:00  
**Source:** OpenDev Gerrit  
**Skill:** /triassessment --gerrit --compare

---

## Review Summary

| Field | Value |
|-------|-------|
| Review | [996428](https://review.opendev.org/c/openstack/horizon/+/996428) |
| Subject | Add `WEBSSO_POST_LOGOUT_URL` setting for proper SSO/OIDC logout |
| Project | openstack/horizon |
| Branch | master |
| Status | CI Failing |
| Topic | websso-post-logout |
| Owner | Freerk-Ole Zakfeld (freerkzakfeld) |
| Created | 2026-07-08 08:44:40 |
| Updated | 2026-07-28 12:55:36 |
| Patchset | #6 |
| Files Changed | 5 files (+68/-0 lines) |
| Code-Review | -1 (x1) |
| Verified | -1 (Zuul) |
| Workflow | -- |

## Commit Message

```
Add `WEBSSO_POST_LOGOUT_URL` setting for proper SSO/OIDC logout

Once a WebSSO user's session has been terminated by the logout view, they
will be redirected to the URL specified in this variable, instead of the
login page. This only applies to users who authenticated via WebSSO (i.e.
their session's ``auth_type`` is not ``credentials``).
This is unrelated to ``LOGOUT_URL``, which just points the logout
link/button at the logout view and does not by itself terminate the
session.

Closes-Bug: #2161654
Change-Id: I8302cd390b954ee8abfa2340ff9fd0df8ad88120
Assisted-By: Claude:claude-sonnet-4-6
Signed-off-by: Freerk-Ole Zakfeld <fzakfeld@scaleuptech.com>
```

## Launchpad Cross-Reference

| Bug | Title | Status | Importance |
|-----|-------|--------|------------|
| [LP#2161654](https://bugs.launchpad.net/bugs/2161654) | logout is broken in Gazpacho and newer when WEBSSO is enabled | New | Undecided |

## Changed Files

| File | Status | Lines | Complexity |
|------|--------|-------|------------|
| releasenotes/notes/websso-post-logout-url-cb65d71cda668e1a.yaml | Added | +7/-0 | Low |
| doc/source/configuration/settings.rst | Modified | +16/-0 | Low |
| openstack_auth/defaults.py | Modified | +10/-0 | Low |
| openstack_auth/tests/unit/test_auth.py | Modified | +27/-0 | Low |
| openstack_auth/views.py | Modified | +8/-0 | Low |

**Total:** 5 files, +68 lines, 0 deletions

## Related Reviews

**Same Topic: websso-post-logout**

No other active reviews found with this topic.

**Same Launchpad Bug: LP#2161654**

No other active reviews found addressing this bug.

## Technical Context

**What this review does:**

This patch addresses a broken logout flow for WebSSO users in Horizon. The problem: when WEBSSO is enabled and a user logs out, they're redirected to the login page but remain logged into their SSO provider. This creates a confusing UX where "logging out" doesn't actually log the user out.

**Solution approach:**

Add a new setting `WEBSSO_POST_LOGOUT_URL` that specifies where to redirect WebSSO users after logout. The logout view checks the session's `auth_type` field — if it's not "credentials" (meaning it's a federated/SSO user), redirect to this URL instead of the login page.

**Key implementation details:**

1. **Setting addition** (`openstack_auth/defaults.py`):
   ```python
   WEBSSO_POST_LOGOUT_URL = None
   ```

2. **Logout view modification** (`openstack_auth/views.py`):
   - Check if user authenticated via WebSSO (auth_type != "credentials")
   - If yes and `WEBSSO_POST_LOGOUT_URL` is set, redirect there
   - Otherwise, use default behavior (redirect to login)

3. **Test coverage** (`openstack_auth/tests/unit/test_auth.py`):
   - Tests logout redirect for WebSSO users
   - Tests that non-WebSSO users still get login redirect

**Scope:**

This is a **single-provider solution**. It assumes all SSO users use the same logout endpoint. Deployments with multiple SSO providers (e.g., both OIDC and SAML2) cannot configure different logout URLs per provider.

## Impact Analysis

**If Merged:**

**Positive:**
- Fixes LP#2161654 (logout broken in Gazpacho with WEBSSO)
- Operators can configure proper SSO logout flow
- Better security posture (users actually logged out)
- Improved UX (no "ghost sessions")

**Negative:**
- Adds another setting to openstack_auth (more config surface area)
- Only solves single-provider use case
- May confuse operators who need multi-provider support

**Breaking Changes:** None (defaults to None = current behavior)

**API Stability:** No impact on plugin API (changes only in openstack_auth, not horizon/)

**If Abandoned:**

- LP#2161654 remains unfixed
- Operators with SSO deployments continue to have broken logout
- Security audit failures for customers
- Alternative: wait for more comprehensive multi-provider solution (review 998960)

## Recommendation

**Verdict:** NEEDS_REVISION

**Confidence:** HIGH

**Rationale:**

This review **addresses a real bug** (LP#2161654) and has **solid test coverage**. However, it currently has **two blockers**:

1. **CI failing (Zuul -1)** — must be resolved before merge
2. **Architecture overlap with 998960** — both modify same code paths

The **single-provider limitation** is not a blocker for this specific bug (LP#2161654), but operators needing multi-provider support (OSPRH-25872, RHOSRFE-300) will need review 998960 instead.

**Recommended path forward:**

See comparison.md for detailed merge strategy analysis. **Short version:**

- **Option A (RECOMMENDED):** Abandon this in favor of 998960
  - 998960's mapping approach is a superset of this functionality
  - Single-provider configs work fine with a mapping containing one key
  - Both LP#2161654 and OSPRH-25872 are satisfied

- **Option B:** Fix CI, coordinate merge order with 998960
  - If 998960 doesn't land soon, this could merge first as interim fix
  - Requires explicit plan for how two settings coexist or which deprecates

## Review Points

- [X] Adds new setting with safe default (None)
- [X] Includes unit tests
- [X] Includes release note
- [X] Documents new setting in configuration guide
- [X] Backward compatible (no breaking changes)
- [ ] **BLOCKER:** CI failing (Zuul Verified -1) — must fix
- [ ] **CONCERN:** Overlaps with review 998960 — coordinate merge strategy
- [ ] **CONCERN:** Single-provider only — operators with multi-provider need 998960
- [ ] **SUGGESTION:** Consider consolidating with 998960's mapping approach

---

**Generated:** 2026-07-28 16:25:00 | Skill: /triassessment --gerrit | Model: claude-sonnet-4.5
