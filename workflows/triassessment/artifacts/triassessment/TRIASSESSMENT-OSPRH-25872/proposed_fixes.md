# Proposed Fixes: OSPRH-25872

**Ticket:** [OSPRH-25872](https://redhat.atlassian.net/browse/OSPRH-25872)  
**Generated:** 2026-07-28  
**Confidence:** **HIGH** — all affected files located, full context available, fix is straightforward

---

## Summary

Enable Horizon to redirect to the correct SSO logout URL when multiple authentication methods are configured. The fix introduces a new setting (`WEBSSO_LOGOUT_REDIRECT_MAPPING`) that maps authentication methods to their respective logout URLs, and modifies the logout view to read the user's session `auth_type` to determine where to redirect.

**Implementation approach:**
1. Add new optional setting to `openstack_auth/defaults.py`
2. Modify logout logic in `openstack_auth/views.py` to use the mapping
3. Document the new setting in `doc/source/configuration/settings.rst`
4. Add unit tests covering multi-provider scenarios

**Backward compatibility:** Existing single-provider deployments using `WEBSSO_DEFAULT_REDIRECT_LOGOUT` continue to work unchanged. The new setting is optional and only activates when configured.

---

## Affected Files

| File | Change Type | Lines | Complexity | Risk |
|------|-------------|-------|------------|------|
| `openstack_auth/defaults.py` | Modify | ~15 | Low | Low (new optional setting) |
| `openstack_auth/views.py` | Modify | ~20 | Medium | Low (reads session, adds fallback logic) |
| `doc/source/configuration/settings.rst` | Modify | ~30 | Low | None (documentation only) |
| `openstack_auth/tests/unit/test_auth.py` | Modify | ~40 | Medium | None (tests only) |
| `releasenotes/notes/websso-logout-redirect-mapping-*.yaml` | Add | ~10 | Low | None (release note) |

**Total estimated changes:** ~115 lines added/modified

---

## Fix 1: Add `WEBSSO_LOGOUT_REDIRECT_MAPPING` Setting

**File:** `openstack_auth/defaults.py`  
**Lines:** After line 156 (after `WEBSSO_DEFAULT_REDIRECT_LOGOUT`)  
**Complexity:** Low  
**Risk:** Low (no API changes, new optional setting)

### Current Code

```python
# openstack_auth/defaults.py (lines 153-157)

# Enables redirection on logout to the method specified on the identity
# provider. Once logout the client will be redirected to the address specified
# in this variable.
WEBSSO_DEFAULT_REDIRECT_LOGOUT = None

# If set this URL will be used for web single-sign-on authentication
# instead of OPENSTACK_KEYSTONE_URL. This is needed in the deployment
# scenarios where network segmentation is used per security requirement.
```

### Proposed Change

```python
# openstack_auth/defaults.py (lines 153-173)

# Enables redirection on logout to the method specified on the identity
# provider. Once logout the client will be redirected to the address specified
# in this variable.
# NOTE: This setting only works when WEBSSO_DEFAULT_REDIRECT is True AND
# there is only one configured authentication method. For deployments with
# multiple authentication methods, use WEBSSO_LOGOUT_REDIRECT_MAPPING instead.
WEBSSO_DEFAULT_REDIRECT_LOGOUT = None

# FIX (OSPRH-25872): Map authentication methods to their logout URLs
# Enables per-provider logout redirect when multiple authentication methods
# are configured. Keys must match values from WEBSSO_CHOICES or WEBSSO_IDP_MAPPING.
# The logout view will read the user's session 'auth_type' to determine which
# logout URL to redirect to.
# Example:
# WEBSSO_LOGOUT_REDIRECT_MAPPING = {
#     "oidc": "https://idp.example.com/oidc/logout",
#     "saml2": "https://idp.example.com/saml2/logout",
#     "acme_oidc": "https://acme.example.com/logout",
# }
WEBSSO_LOGOUT_REDIRECT_MAPPING = {}

# If set this URL will be used for web single-sign-on authentication
# instead of OPENSTACK_KEYSTONE_URL. This is needed in the deployment
# scenarios where network segmentation is used per security requirement.
```

### Rationale

**Why this change fixes the issue:**
- Provides a configuration mechanism for operators to map each `auth_type` (from `WEBSSO_CHOICES`) to its corresponding logout URL
- Keys in the dict must match the keys from `WEBSSO_CHOICES` or `WEBSSO_IDP_MAPPING`, ensuring consistency with login configuration
- Empty dict default (`{}`) means the feature is opt-in — no change for existing deployments

**Why the comment about `WEBSSO_DEFAULT_REDIRECT_LOGOUT` is updated:**
- Clarifies the limitation of the existing setting (single-provider only)
- Points operators to the new setting for multi-provider scenarios

### Testing Strategy

**Unit test scenarios:**
1. `WEBSSO_LOGOUT_REDIRECT_MAPPING` is empty → logout falls back to existing behavior
2. `WEBSSO_LOGOUT_REDIRECT_MAPPING` has one entry, user's `auth_type` matches → redirect to mapped URL
3. `WEBSSO_LOGOUT_REDIRECT_MAPPING` has multiple entries, user's `auth_type` matches "oidc" → redirect to OIDC logout URL
4. `WEBSSO_LOGOUT_REDIRECT_MAPPING` has multiple entries, user's `auth_type` matches "saml2" → redirect to SAML2 logout URL
5. User's `auth_type` is not in the mapping → fall back to local logout

**Integration test (QE):**
- Configure RHOSO with Keystone + OIDC + SAML2
- Log in via OIDC → logout → verify redirect to OIDC logout URL
- Log in via SAML2 → logout → verify redirect to SAML2 logout URL
- Log in via Keystone credentials → logout → verify local logout (no redirect)

### Migration Notes

**For operators upgrading from single-provider to multi-provider:**

Before (single-provider):
```python
WEBSSO_DEFAULT_REDIRECT = True
WEBSSO_DEFAULT_REDIRECT_PROTOCOL = "oidc"
WEBSSO_DEFAULT_REDIRECT_LOGOUT = "https://idp.example.com/oidc/logout"
```

After (multi-provider):
```python
WEBSSO_CHOICES = (
    ("credentials", "Keystone Credentials"),
    ("oidc", "OpenID Connect"),
    ("saml2", "SAML 2.0"),
)
WEBSSO_DEFAULT_REDIRECT = False  # Changed: don't auto-redirect, show login dropdown
WEBSSO_LOGOUT_REDIRECT_MAPPING = {  # New: per-provider logout URLs
    "oidc": "https://idp.example.com/oidc/logout",
    "saml2": "https://idp.example.com/saml2/logout",
}
# WEBSSO_DEFAULT_REDIRECT_LOGOUT is now ignored (comment explains why)
```

**No breaking changes:** Operators who never set `WEBSSO_LOGOUT_REDIRECT_MAPPING` see no behavior change.

---

## Fix 2: Modify Logout View to Use Auth Type Mapping

**File:** `openstack_auth/views.py`  
**Lines:** 305-320 (logout function)  
**Complexity:** Medium  
**Risk:** Low (no existing API changes, adds new code path)

### Current Code

```python
# openstack_auth/views.py (lines 305-326)

@require_POST
def logout(request, login_url=None, **kwargs):
    """Logs out the user if he is logged in. Then redirects to the log-in page.

    :param login_url:
        Once logged out, defines the URL where to redirect after login

    :param kwargs:
        see django.contrib.auth.views.logout_then_login extra parameters.

    """
    msg = 'Logging out user "%(username)s".' % \
        {'username': request.user.username}
    LOG.info(msg)

    """ Securely logs a user out. """
    if (settings.WEBSSO_ENABLED and settings.WEBSSO_DEFAULT_REDIRECT and
            settings.WEBSSO_DEFAULT_REDIRECT_LOGOUT):
        auth_user.unset_session_user_variables(request)
        return django_http.HttpResponseRedirect(
            settings.WEBSSO_DEFAULT_REDIRECT_LOGOUT)

    # Django 5.2 makes the built-in LogoutView POST-only. Calling
    # logout_then_login() here will result in 405 for GET-based logout flows.
    # Enforce POST at this view and perform logout directly.
    auth.logout(request)
    return django_http.HttpResponseRedirect(
        shortcuts.resolve_url(login_url or settings.LOGIN_URL)
    )
```

### Proposed Change

```python
# openstack_auth/views.py (lines 305-340)

@require_POST
def logout(request, login_url=None, **kwargs):
    """Logs out the user if he is logged in. Then redirects to the log-in page.

    :param login_url:
        Once logged out, defines the URL where to redirect after login

    :param kwargs:
        see django.contrib.auth.views.logout_then_login extra parameters.

    """
    msg = 'Logging out user "%(username)s".' % \
        {'username': request.user.username}
    LOG.info(msg)

    """ Securely logs a user out. """
    
    # FIX (OSPRH-25872): Support per-provider logout redirect for multi-auth deployments
    # Check if user logged in via SSO and we have a logout URL mapping
    auth_type = request.session.get('auth_type')
    if auth_type and hasattr(settings, 'WEBSSO_LOGOUT_REDIRECT_MAPPING'):
        logout_url = settings.WEBSSO_LOGOUT_REDIRECT_MAPPING.get(auth_type)
        if logout_url:
            LOG.info('Redirecting logout to SSO provider "%s": %s',
                     auth_type, logout_url)
            auth_user.unset_session_user_variables(request)
            return django_http.HttpResponseRedirect(logout_url)
        else:
            LOG.debug('Auth type "%s" not found in WEBSSO_LOGOUT_REDIRECT_MAPPING, '
                      'falling back to local logout', auth_type)
    
    # Fall back to existing single-provider logout redirect
    if (settings.WEBSSO_ENABLED and settings.WEBSSO_DEFAULT_REDIRECT and
            settings.WEBSSO_DEFAULT_REDIRECT_LOGOUT):
        auth_user.unset_session_user_variables(request)
        return django_http.HttpResponseRedirect(
            settings.WEBSSO_DEFAULT_REDIRECT_LOGOUT)

    # Django 5.2 makes the built-in LogoutView POST-only. Calling
    # logout_then_login() here will result in 405 for GET-based logout flows.
    # Enforce POST at this view and perform logout directly.
    auth.logout(request)
    return django_http.HttpResponseRedirect(
        shortcuts.resolve_url(login_url or settings.LOGIN_URL)
    )
```

### Rationale

**Why this change fixes the issue:**
1. **Reads session `auth_type`:** This variable is set during login in `websso()` view (line ~280) and persists for the user's session
2. **Checks mapping:** If `WEBSSO_LOGOUT_REDIRECT_MAPPING` exists and has an entry for the user's `auth_type`, use that logout URL
3. **Logs decision:** Added INFO log when redirecting to SSO provider, DEBUG log when falling back — helps operators debug configuration issues
4. **Preserves fallback:** If no mapping or `auth_type` not found, falls back to existing `WEBSSO_DEFAULT_REDIRECT_LOGOUT` behavior (single-provider case)
5. **Clears session before redirect:** Calls `auth_user.unset_session_user_variables(request)` BEFORE redirecting to IdP logout, ensuring Horizon session is cleaned up

**Order of precedence (most specific → most general):**
1. Per-provider mapping (`WEBSSO_LOGOUT_REDIRECT_MAPPING[auth_type]`)
2. Single-provider default (`WEBSSO_DEFAULT_REDIRECT_LOGOUT`)
3. Local Keystone logout (no redirect)

### Testing Strategy

**Unit tests to add in `openstack_auth/tests/unit/test_auth.py`:**

```python
@override_settings(
    WEBSSO_LOGOUT_REDIRECT_MAPPING={
        "oidc": "https://idp.example.com/oidc/logout",
        "saml2": "https://idp.example.com/saml2/logout",
    }
)
def test_logout_multi_provider_oidc(self):
    """Test logout redirects to OIDC logout URL when auth_type is oidc."""
    self.client.login(username='test', password='test')
    # Simulate SSO login by setting auth_type session variable
    session = self.client.session
    session['auth_type'] = 'oidc'
    session.save()
    
    response = self.client.post(reverse('logout'))
    self.assertRedirects(response, 'https://idp.example.com/oidc/logout',
                         fetch_redirect_response=False)

@override_settings(
    WEBSSO_LOGOUT_REDIRECT_MAPPING={
        "oidc": "https://idp.example.com/oidc/logout",
        "saml2": "https://idp.example.com/saml2/logout",
    }
)
def test_logout_multi_provider_saml2(self):
    """Test logout redirects to SAML2 logout URL when auth_type is saml2."""
    self.client.login(username='test', password='test')
    session = self.client.session
    session['auth_type'] = 'saml2'
    session.save()
    
    response = self.client.post(reverse('logout'))
    self.assertRedirects(response, 'https://idp.example.com/saml2/logout',
                         fetch_redirect_response=False)

@override_settings(
    WEBSSO_LOGOUT_REDIRECT_MAPPING={
        "oidc": "https://idp.example.com/oidc/logout",
    }
)
def test_logout_multi_provider_fallback_unknown_auth_type(self):
    """Test logout falls back to local logout when auth_type is not in mapping."""
    self.client.login(username='test', password='test')
    session = self.client.session
    session['auth_type'] = 'unknown_provider'
    session.save()
    
    response = self.client.post(reverse('logout'))
    # Should redirect to LOGIN_URL (local logout), not to any SSO logout URL
    self.assertRedirects(response, settings.LOGIN_URL,
                         fetch_redirect_response=False)

@override_settings(
    WEBSSO_ENABLED=True,
    WEBSSO_DEFAULT_REDIRECT=True,
    WEBSSO_DEFAULT_REDIRECT_LOGOUT='https://idp.example.com/legacy/logout',
    WEBSSO_LOGOUT_REDIRECT_MAPPING={}  # Empty mapping
)
def test_logout_single_provider_backward_compat(self):
    """Test existing WEBSSO_DEFAULT_REDIRECT_LOGOUT still works when mapping is empty."""
    self.client.login(username='test', password='test')
    response = self.client.post(reverse('logout'))
    self.assertRedirects(response, 'https://idp.example.com/legacy/logout',
                         fetch_redirect_response=False)
```

### Migration Notes

**Session variable dependency:** This fix assumes `request.session['auth_type']` is set correctly during login. Existing Horizon code already sets this (line ~280 in `views.py:websso()`), so no migration is needed.

**Edge case:** If a user's session was created BEFORE the operator configured `WEBSSO_LOGOUT_REDIRECT_MAPPING`, `auth_type` will be missing from the session → logout falls back to local logout. This is safe (no broken logout) and self-corrects on next login.

---

## Fix 3: Document the New Setting

**File:** `doc/source/configuration/settings.rst`  
**Lines:** Near the existing `WEBSSO_DEFAULT_REDIRECT_LOGOUT` documentation  
**Complexity:** Low  
**Risk:** None (documentation only)

### Proposed Change

```rst
``WEBSSO_LOGOUT_REDIRECT_MAPPING``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: Caracal

Default: ``{}`` (empty dict)

A dictionary mapping authentication method identifiers to their respective
SSO logout URLs. This setting enables per-provider logout redirect when
multiple authentication methods are configured via ``WEBSSO_CHOICES``.

**Use case:** Deployments with multiple IdPs (e.g., Keystone credentials +
OIDC + SAML2) where each SSO provider has a different logout endpoint.

**Keys:** Must match values from ``WEBSSO_CHOICES`` or ``WEBSSO_IDP_MAPPING``.

**Values:** Full logout URLs for each SSO provider.

**How it works:** When a user logs out, Horizon reads the ``auth_type``
stored in the session (set during login) and looks up the corresponding
logout URL in this mapping. If found, Horizon redirects to that URL.
If not found, Horizon falls back to ``WEBSSO_DEFAULT_REDIRECT_LOGOUT``
or local logout.

**Example configuration:**

.. code-block:: python

    WEBSSO_CHOICES = (
        ("credentials", "Keystone Credentials"),
        ("oidc", "OpenID Connect"),
        ("saml2", "SAML 2.0"),
        ("acme_oidc", "ACME - OpenID Connect"),
    )

    WEBSSO_IDP_MAPPING = {
        "acme_oidc": ("acme", "oidc"),
    }

    WEBSSO_LOGOUT_REDIRECT_MAPPING = {
        "oidc": "https://default-idp.example.com/oidc/logout",
        "saml2": "https://default-idp.example.com/saml2/logout",
        "acme_oidc": "https://acme.example.com/logout",
    }

**Backward compatibility:** This setting is optional. Existing deployments
using ``WEBSSO_DEFAULT_REDIRECT_LOGOUT`` (single-provider) continue to work
unchanged. To migrate from single-provider to multi-provider:

1. Set ``WEBSSO_DEFAULT_REDIRECT = False`` (disable auto-redirect to single IdP)
2. Add all providers to ``WEBSSO_CHOICES``
3. Configure ``WEBSSO_LOGOUT_REDIRECT_MAPPING`` with each provider's logout URL

**Related settings:**

- ``WEBSSO_DEFAULT_REDIRECT_LOGOUT``: Single-provider logout redirect (deprecated for multi-provider use cases)
- ``WEBSSO_CHOICES``: List of available authentication methods shown on login screen
- ``WEBSSO_IDP_MAPPING``: Maps auth method keys to (IDP, protocol) tuples
```

### Rationale

- Follows Horizon documentation conventions (reStructuredText format, version annotation)
- Includes practical example matching the test matrix (OIDC, SAML2, custom IDP)
- Explains the relationship to existing settings (`WEBSSO_DEFAULT_REDIRECT_LOGOUT`)
- Provides migration path for single-provider → multi-provider upgrades

---

## Fix 4: Add Release Note

**File:** `releasenotes/notes/websso-logout-redirect-mapping-*.yaml` (new file)  
**Lines:** N/A (new file)  
**Complexity:** Low  
**Risk:** None (release note)

### Proposed Content

```yaml
---
features:
  - |
    Added ``WEBSSO_LOGOUT_REDIRECT_MAPPING`` setting to support per-provider
    logout redirect when multiple SSO authentication methods are configured.
    This enables deployments using Keystone credentials + OIDC + SAML2
    (or any combination of providers) to correctly redirect users to their
    IdP's logout endpoint when logging out.
    
    The setting is a dictionary mapping authentication method identifiers
    (from ``WEBSSO_CHOICES`` or ``WEBSSO_IDP_MAPPING``) to their respective
    logout URLs. When a user logs out, Horizon reads the ``auth_type``
    from the session and redirects to the corresponding logout URL.
    
    Example configuration::
    
        WEBSSO_LOGOUT_REDIRECT_MAPPING = {
            "oidc": "https://idp.example.com/oidc/logout",
            "saml2": "https://idp.example.com/saml2/logout",
        }
    
    This feature is fully backward compatible. Existing deployments using
    ``WEBSSO_DEFAULT_REDIRECT_LOGOUT`` (single-provider) continue to work
    unchanged.
    
    For more information, see the ``WEBSSO_LOGOUT_REDIRECT_MAPPING``
    documentation in the Configuration Reference.
deprecations:
  - |
    ``WEBSSO_DEFAULT_REDIRECT_LOGOUT`` is deprecated for use in multi-provider
    deployments. It continues to work for single-provider scenarios, but
    operators configuring multiple authentication methods should migrate to
    ``WEBSSO_LOGOUT_REDIRECT_MAPPING`` instead.
```

### Rationale

- Follows Reno release note conventions (features + deprecations sections)
- Includes example configuration snippet (reStructuredText literal block)
- Explains backward compatibility clearly
- Notes deprecation of old setting **for multi-provider case only** (not a hard deprecation)

---

## Implementation Checklist

- [ ] Review fix proposals with Horizon team (OSPRH UI team + Radomir Dopieralski)
- [ ] Create feature branch: `git checkout -b websso-multi-provider-logout`
- [ ] **Implement Fix 1:** Add `WEBSSO_LOGOUT_REDIRECT_MAPPING` to `openstack_auth/defaults.py`
- [ ] **Implement Fix 2:** Modify `openstack_auth/views.py:logout()` to use auth type mapping
- [ ] **Implement Fix 3:** Document new setting in `doc/source/configuration/settings.rst`
- [ ] **Implement Fix 4:** Add release note `releasenotes/notes/websso-logout-redirect-mapping-*.yaml`
- [ ] **Add unit tests** in `openstack_auth/tests/unit/test_auth.py` (4 new test methods)
- [ ] Run test suite: `tox -e py311` (unit tests), `tox -e pep8` (linting)
- [ ] Manual verification: Deploy RHOSO with Keystone + OIDC + SAML2, test logout from each method
- [ ] Submit Gerrit review: `git review -t websso-multi-provider-logout`
- [ ] Link Gerrit review to OSPRH-25871 (epic) and RHOSRFE-300 (RFE) in commit message:
  ```
  Implements: blueprint websso-multi-provider-logout
  Closes-Bug: #RHOSRFE-300
  Related-Bug: #OSPRH-25871
  ```
- [ ] Address upstream review feedback (if any)
- [ ] QE validation per OSPRH-19420 acceptance criteria
- [ ] Assign OSPRH-19420 to docs team with tested procedure

---

## Disclaimer

These proposals are AI-generated based on ticket description and available code context (Horizon source code inspection + upstream Gerrit review analysis). The code changes have been verified against the current Horizon codebase structure, but **must be reviewed by the Horizon team before implementation**.

**Key assumptions validated:**
- ✅ `request.session['auth_type']` is set during login (confirmed in `openstack_auth/views.py:websso()`)
- ✅ `WEBSSO_CHOICES` and `WEBSSO_IDP_MAPPING` are the authoritative sources for auth method identifiers
- ✅ Django 5.2 POST-only logout requirement is already handled in current code (`@require_POST` decorator)
- ✅ Session cleanup (`auth_user.unset_session_user_variables`) is the correct approach before redirect

**Confidence level:** HIGH (95%) — Implementation path is clear, no architectural changes needed, full backward compatibility.

---

Generated: 2026-07-28 | Skill: /triassessment --generate-fix | Model: claude-sonnet-4-5@20250929
