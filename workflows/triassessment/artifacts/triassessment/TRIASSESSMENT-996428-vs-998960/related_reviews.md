# Related Reviews: 996428 vs 998960

**Generated:** 2026-07-28 16:25:00

---

## Review Network

These two reviews solve **overlapping problems** in the SSO logout space but address **different tickets** with different scope.

```
Problem Space: SSO Logout Redirect
|
+-- LP#2161654 (Bug: logout broken in Gazpacho)
|   |
|   +-- Review 996428 (single-provider solution)
|       Topic: websso-post-logout
|       Status: CI Failing (-1)
|       Files: 5 (+68/-0)
|
+-- OSPRH-25872 / RHOSRFE-300 (Feature: multi-provider logout)
    |
    +-- Review 998960 (multi-provider solution)
        Topic: (none)
        Status: Under Review (+1)
        Files: 4 (+123/-0)
```

## Ticket Context

### LP#2161654: logout is broken in Gazpacho and newer when WEBSSO is enabled

**Source:** Launchpad bug  
**Severity:** Bug (breaks existing functionality)  
**Scope:** Single-provider SSO deployments  

**Problem:** Recent Django 5.2+ compatibility patches broke logout for ALL users when WEBSSO is enabled (federated or not). This is a regression.

**Addressed by:** Review 996428

**Urgency:** HIGH (broken functionality)

---

### OSPRH-25872: Research customer needs for the SSO logout redirect in Horizon

**Source:** Red Hat Jira (internal)  
**Type:** Research/Requirements gathering  
**Scope:** Multi-provider SSO deployments  

**Description:** Investigate customer requirements for SSO logout redirect in Horizon, specifically for deployments with multiple authentication methods (OIDC + SAML2, etc.).

**Addressed by:** Review 998960

**Urgency:** MEDIUM (feature request, not broken functionality)

---

### RHOSRFE-300: SSO logout from Horizon

**Source:** Red Hat Feature Request  
**Type:** Enhancement  
**Scope:** Multi-provider SSO logout  

**Requirements:**
- Current behavior: `WEBSSO_DEFAULT_REDIRECT_LOGOUT` only supports single provider
- Requirement: Support multiple login methods with different logout URLs
- Business justification: Customers find current behavior confusing, security concerns
- Prior bug: OSPRH-15245 (related earlier issue)

**Addressed by:** Review 998960

**Urgency:** MEDIUM (customer request)

## Alternative Implementations

### Review 996428: Simple Single-Provider Approach

**Architecture:**
```python
# Setting
WEBSSO_POST_LOGOUT_URL = "https://idp.example.com/logout"

# Logic in views.py
if auth_type != "credentials" and WEBSSO_POST_LOGOUT_URL:
    return redirect(WEBSSO_POST_LOGOUT_URL)
```

**Pros:**
- Simple configuration (single string)
- Minimal code change (+68 lines)
- Includes unit tests
- Fixes LP#2161654

**Cons:**
- Single-provider only
- Does NOT solve RHOSRFE-300 requirement
- CI failing

---

### Review 998960: Flexible Multi-Provider Approach

**Architecture:**
```python
# Setting
WEBSSO_LOGOUT_REDIRECT_MAPPING = {
    "oidc": "https://idp.example.com/oidc/logout",
    "saml2": "https://idp.example.com/saml2/logout",
}

# Logic in views.py
auth_type = request.session.get('auth_type')
logout_url = WEBSSO_LOGOUT_REDIRECT_MAPPING.get(auth_type)
if logout_url:
    return redirect(logout_url)
# Fallback to WEBSSO_DEFAULT_REDIRECT_LOGOUT
```

**Pros:**
- Multi-provider support (RHOSRFE-300 requirement)
- Also works for single-provider (mapping with one key)
- Scalable (add providers via config)
- CI passing
- Comprehensive docs

**Cons:**
- More complex config (dict vs string)
- Larger diff (+123 lines)
- No unit tests yet

## Merge Dependencies

**No direct Depends-On chain:**
- 996428 does NOT depend on 998960
- 998960 does NOT depend on 996428

**Conflict:**
- Both modify the same functions in `openstack_auth/views.py`
- Both add overlapping settings in `openstack_auth/defaults.py`
- They CANNOT both merge as-is (will conflict)

## Path Forward

See `comparison.md` for detailed merge strategy recommendations.

**Executive summary:**

1. **Recommended:** Merge 998960 only (after adding tests)
   - Solves both LP#2161654 and RHOSRFE-300
   - 996428's functionality is a subset of 998960's
   - Single-provider configs work with mapping containing one key

2. **Alternative:** Merge 996428 first (if urgent), then adapt 998960
   - Get bug fix (LP#2161654) in quickly
   - Refactor 998960 to extend rather than replace 996428
   - Results in two settings (more API surface)

3. **Not recommended:** Merge both independently
   - Creates merge conflict
   - Confusing for operators (which setting to use?)

## Related Topics

**Topic: websso-post-logout**
- Only review 996428 uses this topic
- No other active reviews found

**No Topic:**
- Review 998960 has no topic set
- Suggestion: Add topic `websso-multi-provider-logout` or similar

---

**Generated:** 2026-07-28 16:25:00 | Skill: /triassessment --gerrit --compare | Model: claude-sonnet-4.5
