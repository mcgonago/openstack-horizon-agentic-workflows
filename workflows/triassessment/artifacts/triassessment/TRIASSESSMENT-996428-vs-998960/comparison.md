# Review Comparison: 996428 vs 998960

**Primary Review:** [996428](https://review.opendev.org/c/openstack/horizon/+/996428)  
**Comparison Review:** [998960](https://review.opendev.org/c/openstack/horizon/+/998960)  
**Both address:** SSO logout redirect configuration (different tickets: LP#2161654 vs OSPRH-25872/RHOSRFE-300)  
**Generated:** 2026-07-28 16:25:00

---

## Side-by-Side Summary

| Aspect | Review 996428 | Review 998960 |
|--------|---------------|---------------|
| Subject | Add `WEBSSO_POST_LOGOUT_URL` setting for proper SSO/OIDC logout | Add per-provider SSO logout redirect support |
| Status | CI Failing (Verified -1) | Under Review (Verified +1) |
| Owner | Freerk-Ole Zakfeld (freerkzakfeld) | Owen McGonagle (omcgonag) |
| Files Changed | 5 files | 4 files |
| Lines Changed | +68/-0 | +123/-0 |
| Patchset | #6 | #2 |
| Code-Review | -1 (x1) | (none yet) |
| Verified | -1 (Zuul) | +1 (Zuul) |
| Created | 2026-07-08 08:44 | 2026-07-28 14:33 |
| Updated | 2026-07-28 12:55 | 2026-07-28 20:25 |
| Topic | websso-post-logout | (none) |
| Addresses | LP#2161654 (logout broken in Gazpacho) | OSPRH-25872 + RHOSRFE-300 (multi-provider logout) |
| Test Coverage | Yes (unit tests added) | No (no tests added yet) |

## Overlap Analysis

**Common Files Modified:**

| File | Review 996428 | Review 998960 |
|------|---------------|---------------|
| doc/source/configuration/settings.rst | +16/-0 | +56/-0 |
| openstack_auth/defaults.py | +10/-0 | +17/-0 |
| openstack_auth/views.py | +8/-0 | +17/-0 |

**Unique to Review 996428:**
- openstack_auth/tests/unit/test_auth.py (+27/-0)
- releasenotes/notes/websso-post-logout-url-cb65d71cda668e1a.yaml (+7/-0)

**Unique to Review 998960:**
- releasenotes/notes/websso-logout-redirect-mapping-cb65d71cda668e1a.yaml (+33/-0)

**File Overlap:** 75% (3 of 4 unique files are common)

## Approach Comparison

### Review 996428 Approach

**Problem:** Single setting for SSO logout redirect.

**Solution:** Add `WEBSSO_POST_LOGOUT_URL` setting that applies to all WebSSO users (those with `auth_type != "credentials"`). When a WebSSO user logs out, redirect them to this URL instead of the login page.

**Implementation:**
- Adds one new setting: `WEBSSO_POST_LOGOUT_URL` (default: None)
- Modifies `logout()` view to check auth_type and use this URL if set
- Simple boolean check: "is this a WebSSO user? Then redirect to POST_LOGOUT_URL"

**Configuration example:**
```python
WEBSSO_POST_LOGOUT_URL = "https://idp.example.com/oidc/logout"
```

**Strengths:**
- Simple, minimal change
- Addresses the immediate LP#2161654 issue (logout broken in Gazpacho)
- Backward compatible (defaults to None = current behavior)
- Includes unit tests

**Limitations:**
- Only supports single SSO provider
- Multi-provider deployments (OIDC + SAML2) cannot configure different logout URLs per provider
- Does not fully address RHOSRFE-300 requirement ("multiple login methods")

### Review 998960 Approach

**Problem:** Multi-provider SSO logout redirect.

**Solution:** Add `WEBSSO_LOGOUT_REDIRECT_MAPPING` dictionary that maps authentication method identifiers to their respective logout URLs. The logout view reads the session's `auth_type` to determine which logout URL to use.

**Implementation:**
- Adds one new setting: `WEBSSO_LOGOUT_REDIRECT_MAPPING` (default: {})
- Modifies `logout()` view to look up auth_type in mapping dict
- Falls back to existing `WEBSSO_DEFAULT_REDIRECT_LOGOUT` if no mapping match

**Configuration example:**
```python
WEBSSO_LOGOUT_REDIRECT_MAPPING = {
    "oidc": "https://idp.example.com/oidc/logout",
    "saml2": "https://idp.example.com/saml2/logout",
}
```

**Strengths:**
- Supports multi-provider deployments (full RHOSRFE-300 requirement)
- Backward compatible with `WEBSSO_DEFAULT_REDIRECT_LOGOUT`
- More flexible/scalable architecture
- Better documentation (56 lines vs 16 lines)

**Limitations:**
- No unit tests yet
- More complex configuration (requires mapping dict)
- Larger diff (+123 vs +68 lines)

## Key Differences

1. **Use Case Coverage:** 996428 solves single-provider; 998960 solves multi-provider
2. **Configuration Complexity:** 996428 uses single string; 998960 uses dictionary mapping
3. **Ticket Scope:** 996428 addresses LP#2161654 (bug fix); 998960 addresses OSPRH-25872 + RHOSRFE-300 (feature request)
4. **Test Coverage:** 996428 has unit tests; 998960 does not
5. **CI Status:** 996428 failing (-1); 998960 passing (+1)
6. **Documentation Depth:** 998960 has more comprehensive docs (+56 vs +16 lines)

## Recommendation

**Preferred:** MERGE_BOTH (with coordination)

**Confidence:** HIGH

**Rationale:**

These reviews address **different scopes of the same problem space**:
- **996428** solves the immediate bug (LP#2161654: logout broken in Gazpacho) with a simple single-provider solution
- **998960** solves the broader feature request (RHOSRFE-300: multi-provider logout) with a more flexible architecture

However, they **conflict architecturally** — both modify the same code paths in `openstack_auth/views.py` and add overlapping settings. They cannot merge as-is.

**Three merge strategies:**

### Strategy 1: Merge 998960 only (RECOMMENDED)

**Why:** 998960's `WEBSSO_LOGOUT_REDIRECT_MAPPING` is a **superset** of 996428's functionality:
- Single-provider deployments: mapping with one key works identically to 996428's string
- Multi-provider deployments: mapping with multiple keys enables the RHOSRFE-300 requirement
- Both LP#2161654 and OSPRH-25872 are satisfied

**Requirements:**
1. Add unit tests to 998960 (borrow from 996428's test_auth.py)
2. Document single-provider use case explicitly (some users may find dict syntax confusing)
3. Update 998960's commit message to reference LP#2161654 as well

**Migration path for 996428 users:**
```python
# Before (996428 approach):
WEBSSO_POST_LOGOUT_URL = "https://idp.example.com/logout"

# After (998960 approach):
WEBSSO_LOGOUT_REDIRECT_MAPPING = {
    "oidc": "https://idp.example.com/logout"  # Single-provider still works
}
```

### Strategy 2: Merge 996428, then extend with 998960 features

**Why:** Get the bug fix (LP#2161654) in quickly, then add multi-provider later

**Requirements:**
1. Merge 996428 first (add more tests, fix CI)
2. Refactor 998960 to **extend** rather than replace 996428
3. Use `WEBSSO_POST_LOGOUT_URL` as default fallback when mapping lookup fails

**Code sketch:**
```python
# In openstack_auth/views.py
auth_type = request.session.get('auth_type')
logout_url = None

# Strategy: check mapping first, then fallback to single URL
if auth_type and WEBSSO_LOGOUT_REDIRECT_MAPPING:
    logout_url = WEBSSO_LOGOUT_REDIRECT_MAPPING.get(auth_type)

if not logout_url and auth_type != "credentials":
    logout_url = WEBSSO_POST_LOGOUT_URL

if logout_url:
    return shortcuts.redirect(logout_url)
```

**Trade-off:** Two settings instead of one (more complex API surface)

### Strategy 3: Merge neither, create unified patch

**Why:** Avoid technical debt from two overlapping settings

**Requirements:**
1. Abandon both reviews
2. Create new unified patch combining best of both:
   - Use 998960's mapping architecture (more flexible)
   - Use 996428's unit tests (better coverage)
   - Reference all tickets: LP#2161654, OSPRH-25872, RHOSRFE-300

**Trade-off:** Delays both fixes while new patch is authored/reviewed

## Path Forward

**Recommended: Strategy 1 (Merge 998960 only)**

1. **998960 author (omcgonag):** Add unit tests from 996428
   - Copy `openstack_auth/tests/unit/test_auth.py` changes
   - Adapt tests to use `WEBSSO_LOGOUT_REDIRECT_MAPPING` instead of `WEBSSO_POST_LOGOUT_URL`
   - Test both single-provider (mapping with one key) and multi-provider scenarios

2. **998960 author:** Update commit message
   - Add `Closes-Bug: #2161654` (addresses 996428's ticket too)
   - Keep existing `Related-Bug: OSPRH-25872` and `Related-Bug: RHOSRFE-300`

3. **998960 author:** Enhance documentation
   - Add example showing single-provider deployment (for users migrating from simpler configs)
   - Clarify backward compat with `WEBSSO_DEFAULT_REDIRECT_LOGOUT`

4. **996428 author (freerkzakfeld):** Coordinate with 998960
   - Option A: Abandon 996428 in favor of 998960 (comment explaining why)
   - Option B: Wait for 998960 to merge, then rebase 996428 as docs/test enhancement patch

5. **Core reviewers:** Prioritize 998960
   - It solves both use cases (single + multi provider)
   - CI is passing (unlike 996428)
   - More comprehensive docs

**Timeline:**
- 998960 tests added: ~1-2 hours
- 998960 re-review + merge: ~1-3 days (depends on core reviewer availability)
- 996428 decision (abandon or rebase): after 998960 merges

---

**Generated:** 2026-07-28 16:25:00 | Skill: /triassessment --gerrit --compare | Model: claude-sonnet-4.5
