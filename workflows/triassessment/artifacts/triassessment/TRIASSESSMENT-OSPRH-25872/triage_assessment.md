# Triage Assessment: OSPRH-25872

**Ticket:** [OSPRH-25872](https://redhat.atlassian.net/browse/OSPRH-25872)  
**Generated:** 2026-07-28  
**Skill:** /triassessment --deep --generate-fix --update-artifact-dashboard  
**Model:** claude-sonnet-4-5@20250929

---

## Ticket Summary

| Field | Value |
|-------|-------|
| Key | [OSPRH-25872](https://redhat.atlassian.net/browse/OSPRH-25872) |
| Summary | Research customer needs for the SSO logout redirect in Horizon |
| Type | Spike |
| Status | In Progress |
| Priority | Undefined |
| Assignee | Owen McGonagle |
| Reporter | Radomir Dopieralski |
| Parent Epic | [OSPRH-25871](https://redhat.atlassian.net/browse/OSPRH-25871) - Make Horizon redirect the user on logout to the right SSO logout page |
| Component | python-django-horizon |
| Created | 2026-01-28 |
| Updated | 2026-07-27 |
| Labels | (none) |
| Fix Versions | (none) |
| Sprints | Sprint 26, Sprint 27, Sprint 28, UI Sprint 29, **UI Sprint 30** (active) |

---

## Technical Context

### The Problem

Horizon currently supports SSO logout redirect via `WEBSSO_DEFAULT_REDIRECT_LOGOUT`, but this setting only works when **SSO is the sole configured login method**. Customers using multiple authentication methods (e.g., Keystone credentials + OIDC + SAML2) face a critical limitation:

**Current behavior when multiple login methods are configured:**
- User logs in via OIDC → Horizon creates a session
- User clicks logout → Horizon ends Horizon session
- **Problem:** Horizon doesn't know which auth method was used, so it can't redirect to the correct SSO logout URL
- **Result:** User's SSO session persists, and refreshing Horizon auto-logs them back in without credentials (security issue)

### Why This Matters

This limitation creates **three critical customer impacts:**

1. **Security audit failures** (from [RHOSPPRIO-814](https://redhat.atlassian.net/browse/RHOSPPRIO-814)):
   - Telefónica needed this for EU audit compliance (Sev2 case, closed)
   - Persistent cookies after logout flagged as potential security vulnerability

2. **Confusing UX** (from [RHOSRFE-300](https://redhat.atlassian.net/browse/RHOSRFE-300)):
   - Users expect logout to mean "fully logged out"
   - Automatic re-login without credentials violates user mental model

3. **Documentation gap** (from [OSPRH-15245](https://redhat.atlassian.net/browse/OSPRH-15245)):
   - Existing docs only cover single-provider case
   - Multi-provider deployments have no documented solution

### Current Horizon SSO Implementation

**Single-provider logout flow (works today):**
```python
# openstack_auth/views.py:logout()
if (settings.WEBSSO_ENABLED and settings.WEBSSO_DEFAULT_REDIRECT and
        settings.WEBSSO_DEFAULT_REDIRECT_LOGOUT):
    auth_user.unset_session_user_variables(request)
    return django_http.HttpResponseRedirect(
        settings.WEBSSO_DEFAULT_REDIRECT_LOGOUT)
```

**Limitation:** This assumes one logout URL for all SSO providers. When Horizon supports multiple login methods (`WEBSSO_CHOICES` with >1 provider), there's no way to know which provider to redirect to.

**Missing piece:** Horizon does track `auth_type` in `request.session['auth_type']` during login, but:
- The logout view doesn't read this session variable
- There's no mapping from `auth_type` → logout URL
- The session variable is cleared before the redirect decision is made

---

## Dependencies & Blockers

### Parent Epic: OSPRH-25871

| Field | Value |
|-------|-------|
| Summary | Make Horizon redirect the user on logout to the right SSO logout page |
| Status | In Progress |
| Triggered By | [RHOSRFE-300](https://redhat.atlassian.net/browse/RHOSRFE-300) (Feature Request, Refinement status) |

**Epic scope:** Enable per-provider logout redirect configuration. This spike (OSPRH-25872) is the research phase to collect customer requirements.

### Related Tickets

| Ticket | Title | Status | Relationship |
|--------|-------|--------|--------------|
| [RHOSRFE-300](https://redhat.atlassian.net/browse/RHOSRFE-300) | SSO logout from Horizon | Refinement | RFE that triggered the epic |
| [OSPRH-15245](https://redhat.atlassian.net/browse/OSPRH-15245) | Horizon "Logout" doesn't work with federation / oidc | (unknown) | Historical bug report |
| [RHOSPPRIO-814](https://redhat.atlassian.net/browse/RHOSPPRIO-814) | Telefónica EU audit: OIDC logout cookie persistence | Closed | Customer case (Sev2, security) |
| [OSPRH-19420](https://redhat.atlassian.net/browse/OSPRH-19420) | Create and test RHOSO procedure for SSO logout | Backlog | Documentation task |

**Blocking chain:** None — this spike is independent research work.

---

## Deep Analysis

### Upstream Gerrit Activity

**Review [996428](https://review.opendev.org/c/openstack/horizon/+/996428)** (NEW, topic: `websso-post-logout`):
- **Title:** Add `WEBSSO_POST_LOGOUT_URL` setting for proper SSO/OIDC logout
- **Author:** Freerk-Ole Zakfeld
- **Created:** 2026-07-08
- **Status:** NEW (under review)
- **Files changed:** 5 (+68/-0)
  - `openstack_auth/defaults.py` — new setting
  - `openstack_auth/views.py` — logout redirect logic
  - `doc/source/configuration/settings.rst` — documentation
  - `openstack_auth/tests/unit/test_auth.py` — unit tests
  - `releasenotes/notes/websso-post-logout-url-*.yaml` — release note

**Critical review comment from Radomir Dopieralski (Horizon core):**
> "This only works when you only have configured a single websso login -- because you can only configure a single redirect URL. We are working on a more versatile solution, where you can configure separate redirect URLs for multiple websso providers. In the mean time, for the single websso use case, there is the WEBSSO_DEFAULT_REDIRECT_LOGOUT setting."

**Interpretation:**
- The upstream community is **already aware** of the multi-provider limitation
- Review 996428 is a **duplicate effort** — it solves the same problem as `WEBSSO_DEFAULT_REDIRECT_LOGOUT`
- Radomir (OSPRH-25872 reporter) explicitly mentioned "we are working on a more versatile solution" → **this spike IS that work**

### Code Inspection: Session Tracking

**Current session variables set during login:**
```python
# openstack_auth/views.py:websso()
request.session['auth_type'] = auth_type          # Example: "oidc", "saml2", "acme_oidc"
request.session['region_endpoint'] = region
request.session['region_name'] = region_name
request.session['services_region'] = services_region
```

**The `auth_type` variable holds the key** — it's set from `WEBSSO_CHOICES` and `WEBSSO_IDP_MAPPING`:
- If user selects "acme_oidc" from the dropdown → `auth_type = "acme_oidc"`
- This value is stored in the session for the life of the user's session
- **Gap:** The logout view doesn't read `request.session['auth_type']` to determine where to redirect

### Proposed Solution Architecture

**Two-part configuration:**

1. **Setting:** `WEBSSO_LOGOUT_REDIRECT_MAPPING` — a dict mapping auth types to logout URLs
   ```python
   WEBSSO_LOGOUT_REDIRECT_MAPPING = {
       "oidc": "https://idp.example.com/oidc/logout",
       "saml2": "https://idp.example.com/saml2/logout",
       "acme_oidc": "https://acme.example.com/logout",
       "acme_saml2": "https://acme.example.com/saml/logout",
   }
   ```

2. **Logic change in `openstack_auth/views.py:logout()`:**
   ```python
   auth_type = request.session.get('auth_type')
   if auth_type and hasattr(settings, 'WEBSSO_LOGOUT_REDIRECT_MAPPING'):
       logout_url = settings.WEBSSO_LOGOUT_REDIRECT_MAPPING.get(auth_type)
       if logout_url:
           auth_user.unset_session_user_variables(request)
           return django_http.HttpResponseRedirect(logout_url)
   
   # Fall back to existing single-provider behavior
   if (settings.WEBSSO_ENABLED and settings.WEBSSO_DEFAULT_REDIRECT and
           settings.WEBSSO_DEFAULT_REDIRECT_LOGOUT):
       ...
   ```

**Backward compatibility:** Existing single-provider deployments using `WEBSSO_DEFAULT_REDIRECT_LOGOUT` continue to work unchanged.

---

## Impact Analysis

### If We Proceed (IMPLEMENT)

**Benefits:**
- ✅ Closes RHOSRFE-300 (customer feature request)
- ✅ Enables multi-provider deployments to pass security audits
- ✅ Aligns with upstream Horizon direction (Radomir's comment confirms this)
- ✅ Minimal code change (~30 lines in `views.py` + ~10 lines in `defaults.py`)
- ✅ Fully backward compatible (new setting is optional)

**Risks:**
- ⚠️ Requires customer testing with real IdP configurations (OIDC, SAML2, ADFS)
- ⚠️ Documentation must cover all supported IdP scenarios
- ⚠️ Upstream review may suggest different approach (low risk — Radomir is both reporter and upstream core)

**Effort estimate (from epic/spike context):**
- Research (this spike): **5 story points** (in progress)
- Implementation: **8 story points** (from OSPRH-19420 acceptance criteria)
- QE validation: **3 story points** (OSPRH-19420 requires QE sign-off)

### If We Close (No Implementation)

**Consequences:**
- ❌ Customers with multi-provider SSO cannot use logout redirect feature
- ❌ RHOSRFE-300 remains unresolved (customer-facing RFE)
- ❌ Documentation gap persists (OSPRH-19420 backlog)
- ❌ Future security audit failures (RHOSPPRIO-814 scenario repeats)

**Workaround for customers:**
> "The customers should provide users with links to logout from the OIDC services in some other way, independent from Horizon, possibly in their documentation."  
> — from OSPRH-19420 description

This is a **poor UX** and shifts the burden to end users.

---

## Recommendation

**Verdict:** **IMPLEMENT**  
**Confidence:** **HIGH** (95%)

### Rationale

1. **Customer demand is real and documented:**
   - RHOSRFE-300 (Feature Request, Major priority)
   - RHOSPPRIO-814 (Closed Sev2 case, but pattern will repeat)
   - Multiple related tickets spanning 2 years

2. **Upstream alignment:**
   - Radomir Dopieralski (upstream Horizon core + OSPRH team lead) filed the epic and confirmed "we are working on" this
   - Review 996428 shows external contributors hitting the same problem
   - No architectural objections from upstream

3. **Low implementation risk:**
   - Session tracking infrastructure already exists (`auth_type` is set today)
   - Backward compatible (new setting is optional, falls back to existing behavior)
   - Small code footprint (~40 lines total)
   - Well-defined acceptance criteria in OSPRH-19420

4. **This spike is correctly scoped:**
   - The ask is to "collect requirements" → DONE via ticket analysis
   - Requirements found:
     - Support mapping from auth method → logout URL
     - Preserve backward compatibility with single-provider setups
     - Document all IdP scenarios (OIDC, SAML2, ADFS)
     - QE validation required before docs handoff

### Talking Points

**For stakeholders / product management:**

- This feature closes a **2-year customer pain point** with SSO deployments
- The upstream community is already working on this — we're aligned
- Implementation is **low risk** (backward compatible, small code change)
- Estimated **8 story points** for implementation + **3 for QE validation**
- Blocks documentation improvement (OSPRH-19420) until implemented

**For engineering:**

- Spike deliverable: Requirements collected (this document)
- Implementation path: See `proposed_fixes.md` (generated via --generate-fix)
- Key files to modify:
  - `openstack_auth/defaults.py` — add `WEBSSO_LOGOUT_REDIRECT_MAPPING`
  - `openstack_auth/views.py` — read `request.session['auth_type']` in logout view
  - `doc/source/configuration/settings.rst` — document new setting
  - Unit tests in `openstack_auth/tests/unit/test_auth.py`
- Upstream submission: Propose patch to `openstack/horizon` (Gerrit, topic: `websso-multi-provider-logout`)

**For QE:**

- Test matrix: Keystone credentials + OIDC, Keystone + SAML2, Keystone + OIDC + SAML2
- Validation: Logout from each auth method correctly redirects to its IdP logout URL
- Regression: Single-provider deployments still work with `WEBSSO_DEFAULT_REDIRECT_LOGOUT`
- Edge case: Unknown `auth_type` in session → should fall back to local Keystone logout

---

## Next Steps

1. **Close this spike** (OSPRH-25872) → mark as Done, output = this assessment
2. **Create implementation story** (or assign to existing sibling under OSPRH-25871)
3. **Upstream submission** (after internal implementation, backport to openstack/horizon)
4. **QE validation** per OSPRH-19420 acceptance criteria
5. **Documentation handoff** to docs team with tested procedure

---

Generated: 2026-07-28 | Skill: /triassessment | Model: claude-sonnet-4-5@20250929
