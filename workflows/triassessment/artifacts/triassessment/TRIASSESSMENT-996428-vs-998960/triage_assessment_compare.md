# Triage Assessment: Review 998960

**Review:** [998960](https://review.opendev.org/c/openstack/horizon/+/998960)  
**Generated:** 2026-07-28 16:25:00  
**Source:** OpenDev Gerrit  
**Skill:** /triassessment --gerrit --compare

---

## Review Summary

| Field | Value |
|-------|-------|
| Review | [998960](https://review.opendev.org/c/openstack/horizon/+/998960) |
| Subject | Add per-provider SSO logout redirect support |
| Project | openstack/horizon |
| Branch | master |
| Status | Under Review |
| Topic | (none) |
| Owner | Owen McGonagle (omcgonag) |
| Created | 2026-07-28 14:33:42 |
| Updated | 2026-07-28 20:25:06 |
| Patchset | #2 |
| Files Changed | 4 files (+123/-0 lines) |
| Code-Review | (none yet) |
| Verified | +1 (Zuul) |
| Workflow | -- |

## Commit Message

```
Add per-provider SSO logout redirect support

Enable Horizon to redirect to the correct SSO logout URL when multiple
authentication methods are configured. This addresses a critical gap
where operators using Keystone + OIDC + SAML2 (or any combination)
cannot configure per-provider logout URLs.

Current behavior:
- WEBSSO_DEFAULT_REDIRECT_LOGOUT only supports single-provider deployments
- Users logged in via SSO remain logged in after "logging out" of Horizon
- This causes security audit failures and confusing UX

This change introduces WEBSSO_LOGOUT_REDIRECT_MAPPING, a dictionary that
maps authentication method identifiers (from WEBSSO_CHOICES or
WEBSSO_IDP_MAPPING) to their respective logout URLs. The logout view
reads the user's session auth_type (already tracked during login) to
determine which logout URL to redirect to.

Example configuration:
    WEBSSO_LOGOUT_REDIRECT_MAPPING = {
        "oidc": "https://idp.example.com/oidc/logout",
        "saml2": "https://idp.example.com/saml2/logout",
    }

Changes:
- openstack_auth/defaults.py: Add WEBSSO_LOGOUT_REDIRECT_MAPPING setting
- openstack_auth/views.py: Modify logout() to use auth_type mapping
- doc/source/configuration/settings.rst: Document new setting
- releasenotes/notes: Add release note

Backward compatibility: Existing single-provider deployments using
WEBSSO_DEFAULT_REDIRECT_LOGOUT continue to work unchanged.

Related-Bug: OSPRH-25872
Related-Bug: RHOSRFE-300
Change-Id: If11079a9a9e7cddff1bedf2dac0bdd10fd461f07
Signed-off-by: Owen McGonagle <omcgonag@redhat.com>
```

## Jira Cross-Reference

| Ticket | Summary | Status | Type | Assignee |
|--------|---------|--------|------|----------|
| [OSPRH-25872](https://redhat.atlassian.net/browse/OSPRH-25872) | Research customer needs for the SSO logout redirect in Horizon | (status unavailable) | (type unavailable) | (assignee unavailable) |
| [RHOSRFE-300](https://redhat.atlassian.net/browse/RHOSRFE-300) | SSO logout from Horizon | (status unavailable) | Feature Request | (assignee unavailable) |

## Changed Files

| File | Status | Lines | Complexity |
|------|--------|-------|------------|
| doc/source/configuration/settings.rst | Modified | +56/-0 | Low |
| openstack_auth/defaults.py | Modified | +17/-0 | Low |
| openstack_auth/views.py | Modified | +17/-0 | Low |
| releasenotes/notes/websso-logout-redirect-mapping-cb65d71cda668e1a.yaml | Added | +33/-0 | Low |

**Total:** 4 files, +123 lines, 0 deletions

## Related Reviews

**Same Jira Ticket: OSPRH-25872**

No other active reviews found addressing this ticket.

**Alternative Implementation:**

Review [996428](https://review.opendev.org/c/openstack/horizon/+/996428) addresses a related problem (LP#2161654) with a simpler single-provider approach. See comparison.md for detailed analysis.

## Technical Context

**What this review does:**

This patch enables **multi-provider SSO logout** in Horizon. The problem: operators running Keystone with multiple federated identity providers (e.g., both OIDC and SAML2) cannot configure different logout URLs for each provider. The existing `WEBSSO_DEFAULT_REDIRECT_LOGOUT` setting only supports one logout URL, so multi-provider deployments either:
1. Leave logout broken for some providers
2. Don't configure logout redirect at all (security issue)

**Solution approach:**

Add a new setting `WEBSSO_LOGOUT_REDIRECT_MAPPING` — a dictionary mapping authentication method identifiers to their respective logout URLs. When a user logs out, the view checks their session's `auth_type` field (set during login) and looks it up in the mapping to determine the correct logout URL.

**Key implementation details:**

1. **Setting addition** (`openstack_auth/defaults.py`):
   ```python
   WEBSSO_LOGOUT_REDIRECT_MAPPING = {}
   ```

2. **Logout view modification** (`openstack_auth/views.py`):
   - Check session's `auth_type` field
   - Look up auth_type in `WEBSSO_LOGOUT_REDIRECT_MAPPING`
   - If found, redirect to that URL
   - Otherwise, fall back to existing `WEBSSO_DEFAULT_REDIRECT_LOGOUT` logic

3. **Configuration example**:
   ```python
   WEBSSO_LOGOUT_REDIRECT_MAPPING = {
       "oidc": "https://idp.example.com/oidc/logout",
       "saml2": "https://idp.example.com/saml2/logout",
   }
   ```

**Scope:**

This is a **multi-provider solution** that also works for single-provider deployments (mapping with one key). It fully addresses RHOSRFE-300's requirement for "multiple login methods" support.

## Impact Analysis

**If Merged:**

**Positive:**
- Enables multi-provider SSO logout (RHOSRFE-300 requirement)
- Operators can configure per-provider logout URLs
- Backward compatible with existing `WEBSSO_DEFAULT_REDIRECT_LOGOUT`
- More scalable architecture (add new providers without code changes)
- Better security (proper logout per provider)
- Also fixes LP#2161654 (same bug as review 996428)

**Negative:**
- More complex configuration (dict vs string)
- No unit tests yet (must add before merge)
- Larger diff than simple single-provider solution (+123 vs +68)

**Breaking Changes:** None (defaults to empty dict = current behavior)

**API Stability:** No impact on plugin API (changes only in openstack_auth, not horizon/)

**If Abandoned:**

- RHOSRFE-300 remains unfulfilled
- Multi-provider operators cannot configure proper logout
- Single-provider operators must use review 996428 or similar
- Security audit failures continue for customers

## Recommendation

**Verdict:** MERGE (after adding tests)

**Confidence:** HIGH

**Rationale:**

This review **addresses the full multi-provider use case** (RHOSRFE-300) while also solving the single-provider bug (LP#2161654, same as review 996428). The architecture is **more flexible and scalable** than 996428's single-string approach.

**Why merge this over 996428:**

1. **Superset functionality:** Mapping with one key = single-provider (996428's use case)
2. **Future-proof:** Adding new providers requires only config change, not code
3. **CI passing:** Zuul +1 (unlike 996428's -1)
4. **Better docs:** +56 lines of documentation vs 996428's +16

**Requirements before merge:**

1. **BLOCKER:** Add unit tests
   - Borrow test structure from review 996428's `test_auth.py` changes
   - Test single-provider case (one key in mapping)
   - Test multi-provider case (multiple keys in mapping)
   - Test fallback to `WEBSSO_DEFAULT_REDIRECT_LOGOUT` when mapping empty
   - Test non-WebSSO users still get login redirect

2. **RECOMMENDED:** Update commit message
   - Add `Closes-Bug: #2161654` (addresses 996428's bug too)
   - Clarifies this patch solves both single and multi-provider cases

3. **RECOMMENDED:** Add single-provider example to docs
   - Some operators may find dict syntax confusing for simple use cases
   - Show that `{"oidc": "https://..."}` works identically to a string setting

## Review Points

- [X] Addresses RHOSRFE-300 feature request fully
- [X] Backward compatible with WEBSSO_DEFAULT_REDIRECT_LOGOUT
- [X] Includes comprehensive documentation (+56 lines)
- [X] Includes release note with examples
- [X] CI passing (Zuul Verified +1)
- [X] No breaking changes (defaults to empty dict)
- [ ] **BLOCKER:** Missing unit tests — must add before merge
- [ ] **SUGGESTION:** Add Closes-Bug: #2161654 to commit message
- [ ] **SUGGESTION:** Document single-provider use case explicitly
- [ ] **SUGGESTION:** Coordinate with review 996428 author (overlap/conflict)

---

**Generated:** 2026-07-28 16:25:00 | Skill: /triassessment --gerrit | Model: claude-sonnet-4.5
