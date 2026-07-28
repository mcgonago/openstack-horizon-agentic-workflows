# views.py Changes: From Standalone to Depends-On

**File:** `openstack_auth/views.py`

---

## Current 998960 Code (Standalone, Conflicts with 996428)

```python
def logout(request):
    """Log out the user if logged in. Then redirect them to the log-in page."""
    # ... existing logout logic ...
    
    # YOUR CURRENT CODE (conflicts with 996428):
    auth_type = request.session.get('auth_type')
    
    # Check mapping only
    if auth_type and settings.WEBSSO_LOGOUT_REDIRECT_MAPPING:
        logout_url = settings.WEBSSO_LOGOUT_REDIRECT_MAPPING.get(auth_type)
        if logout_url:
            return shortcuts.redirect(logout_url)
    
    # Fall back to login
    return shortcuts.redirect(settings.LOGIN_URL)
```

**Problem:** This ignores 996428's `WEBSSO_POST_LOGOUT_URL` setting, causing a conflict.

---

## Updated 998960 Code (Extends 996428, No Conflict)

```python
def logout(request):
    """Log out the user if logged in. Then redirect them to the log-in page."""
    # ... existing logout logic ...
    
    # UPDATED CODE (extends 996428 with tiered fallback):
    auth_type = request.session.get('auth_type')
    logout_url = None
    
    # Tier 1: Check per-provider mapping (most specific)
    # This is YOUR contribution (998960)
    if auth_type and settings.WEBSSO_LOGOUT_REDIRECT_MAPPING:
        logout_url = settings.WEBSSO_LOGOUT_REDIRECT_MAPPING.get(auth_type)
    
    # Tier 2: Check global SSO logout URL (from 996428)
    # This is the 996428 contribution you're extending
    if not logout_url and auth_type != "credentials":
        logout_url = getattr(settings, 'WEBSSO_POST_LOGOUT_URL', None)
    
    # Tier 3: Check legacy default redirect (existing Horizon)
    # This was already there before both patches
    if not logout_url and auth_type != "credentials":
        logout_url = getattr(settings, 'WEBSSO_DEFAULT_REDIRECT_LOGOUT', None)
    
    # If we found a logout URL anywhere, use it
    if logout_url:
        return shortcuts.redirect(logout_url)
    
    # Otherwise, default behavior (redirect to login)
    return shortcuts.redirect(settings.LOGIN_URL)
```

**Benefits:** 
- No conflict with 996428
- Respects all three settings in priority order
- Works for simple AND complex deployments

---

## Side-by-Side Comparison

| Line | Current 998960 (Conflicts) | Updated 998960 (Extends) |
|------|----------------------------|--------------------------|
| 1 | `auth_type = request.session.get('auth_type')` | `auth_type = request.session.get('auth_type')` |
| 2 | -- | `logout_url = None` ← **NEW** |
| 3 | `if auth_type and settings.WEBSSO_LOGOUT_REDIRECT_MAPPING:` | `if auth_type and settings.WEBSSO_LOGOUT_REDIRECT_MAPPING:` |
| 4 | `logout_url = settings.WEBSSO_LOGOUT_REDIRECT_MAPPING.get(auth_type)` | `logout_url = settings.WEBSSO_LOGOUT_REDIRECT_MAPPING.get(auth_type)` |
| 5 | `if logout_url:` ← **WRONG** | -- |
| 6 | `return shortcuts.redirect(logout_url)` | -- |
| 7 | -- | `if not logout_url and auth_type != "credentials":` ← **NEW** |
| 8 | -- | `logout_url = getattr(settings, 'WEBSSO_POST_LOGOUT_URL', None)` ← **NEW (from 996428)** |
| 9 | -- | `if not logout_url and auth_type != "credentials":` ← **NEW** |
| 10 | -- | `logout_url = getattr(settings, 'WEBSSO_DEFAULT_REDIRECT_LOGOUT', None)` ← **NEW** |
| 11 | -- | `if logout_url:` ← **BETTER** |
| 12 | -- | `return shortcuts.redirect(logout_url)` |
| 13 | `return shortcuts.redirect(settings.LOGIN_URL)` | `return shortcuts.redirect(settings.LOGIN_URL)` |

---

## Key Changes

1. **Initialize `logout_url = None`** at the start (line 2)
   - Allows us to check it once at the end

2. **Remove early return** after mapping check (old lines 5-6)
   - Don't `return` immediately if mapping found
   - Just set `logout_url` and continue

3. **Add Tier 2 check** for `WEBSSO_POST_LOGOUT_URL` (lines 7-8)
   - This is the 996428 setting you're extending
   - Only check if mapping didn't find a match

4. **Add Tier 3 check** for `WEBSSO_DEFAULT_REDIRECT_LOGOUT` (lines 9-10)
   - Existing Horizon setting for backward compat
   - Only check if mapping and POST_LOGOUT_URL didn't find a match

5. **Single redirect decision** at the end (lines 11-12)
   - If any tier found a URL, redirect to it
   - Otherwise, fall back to login

---

## Why This Works

**Scenario 1: Multi-provider deployment (your use case)**

```python
WEBSSO_LOGOUT_REDIRECT_MAPPING = {
    "oidc": "https://idp.example.com/oidc/logout",
    "saml2": "https://idp.example.com/saml2/logout",
}
```

Flow:
1. Tier 1: auth_type="oidc" → `logout_url = "https://idp.example.com/oidc/logout"`
2. Tier 2: Skipped (logout_url already set)
3. Tier 3: Skipped (logout_url already set)
4. Redirect to OIDC logout ✅

---

**Scenario 2: Simple deployment (996428 use case)**

```python
WEBSSO_POST_LOGOUT_URL = "https://idp.example.com/logout"
# WEBSSO_LOGOUT_REDIRECT_MAPPING not set (defaults to {})
```

Flow:
1. Tier 1: WEBSSO_LOGOUT_REDIRECT_MAPPING is {} → `logout_url = None`
2. Tier 2: auth_type="oidc" → `logout_url = "https://idp.example.com/logout"`
3. Tier 3: Skipped (logout_url already set)
4. Redirect to POST_LOGOUT_URL ✅

---

**Scenario 3: Hybrid deployment (best of both)**

```python
WEBSSO_LOGOUT_REDIRECT_MAPPING = {
    "oidc": "https://idp.example.com/oidc/logout",
}
WEBSSO_POST_LOGOUT_URL = "https://idp.example.com/generic-logout"
```

Flow for OIDC user:
1. Tier 1: auth_type="oidc" → `logout_url = "https://idp.example.com/oidc/logout"`
2. Tier 2: Skipped
3. Tier 3: Skipped
4. Redirect to OIDC-specific logout ✅

Flow for SAML2 user (not in mapping):
1. Tier 1: auth_type="saml2", not in mapping → `logout_url = None`
2. Tier 2: auth_type="saml2" → `logout_url = "https://idp.example.com/generic-logout"`
3. Tier 3: Skipped
4. Redirect to generic logout (catch-all) ✅

---

**Scenario 4: Legacy deployment (backward compat)**

```python
WEBSSO_DEFAULT_REDIRECT_LOGOUT = "https://old-idp.example.com/logout"
# No WEBSSO_LOGOUT_REDIRECT_MAPPING
# No WEBSSO_POST_LOGOUT_URL
```

Flow:
1. Tier 1: WEBSSO_LOGOUT_REDIRECT_MAPPING is {} → `logout_url = None`
2. Tier 2: WEBSSO_POST_LOGOUT_URL not set → `logout_url = None`
3. Tier 3: auth_type="oidc" → `logout_url = "https://old-idp.example.com/logout"`
4. Redirect to legacy logout ✅

---

## Testing Each Tier

You can add unit tests for each scenario:

```python
# In openstack_auth/tests/unit/test_auth.py

def test_logout_multi_provider_mapping(self):
    """Test Tier 1: WEBSSO_LOGOUT_REDIRECT_MAPPING"""
    settings.WEBSSO_LOGOUT_REDIRECT_MAPPING = {
        "oidc": "https://idp.example.com/oidc/logout",
        "saml2": "https://idp.example.com/saml2/logout",
    }
    # Set session auth_type
    session = self.client.session
    session['auth_type'] = 'oidc'
    session.save()
    
    response = self.client.get(reverse('logout'))
    self.assertRedirects(response, "https://idp.example.com/oidc/logout")

def test_logout_single_provider_post_url(self):
    """Test Tier 2: WEBSSO_POST_LOGOUT_URL (996428's setting)"""
    settings.WEBSSO_POST_LOGOUT_URL = "https://idp.example.com/logout"
    settings.WEBSSO_LOGOUT_REDIRECT_MAPPING = {}  # Empty mapping
    
    session = self.client.session
    session['auth_type'] = 'oidc'
    session.save()
    
    response = self.client.get(reverse('logout'))
    self.assertRedirects(response, "https://idp.example.com/logout")

def test_logout_legacy_default_redirect(self):
    """Test Tier 3: WEBSSO_DEFAULT_REDIRECT_LOGOUT (existing)"""
    settings.WEBSSO_DEFAULT_REDIRECT_LOGOUT = "https://legacy.example.com/logout"
    settings.WEBSSO_LOGOUT_REDIRECT_MAPPING = {}
    delattr(settings, 'WEBSSO_POST_LOGOUT_URL')  # Not set
    
    session = self.client.session
    session['auth_type'] = 'saml2'
    session.save()
    
    response = self.client.get(reverse('logout'))
    self.assertRedirects(response, "https://legacy.example.com/logout")

def test_logout_hybrid_fallback(self):
    """Test mapping + fallback: OIDC in mapping, SAML2 falls back"""
    settings.WEBSSO_LOGOUT_REDIRECT_MAPPING = {
        "oidc": "https://idp.example.com/oidc/logout",
    }
    settings.WEBSSO_POST_LOGOUT_URL = "https://idp.example.com/generic-logout"
    
    # OIDC user gets mapped URL
    session = self.client.session
    session['auth_type'] = 'oidc'
    session.save()
    response = self.client.get(reverse('logout'))
    self.assertRedirects(response, "https://idp.example.com/oidc/logout")
    
    # SAML2 user gets fallback URL
    session = self.client.session
    session['auth_type'] = 'saml2'
    session.save()
    response = self.client.get(reverse('logout'))
    self.assertRedirects(response, "https://idp.example.com/generic-logout")
```

---

## Summary

**What to change in views.py:**

1. Add `logout_url = None` initialization
2. Remove early `return` after mapping check
3. Add Tier 2 check (WEBSSO_POST_LOGOUT_URL from 996428)
4. Add Tier 3 check (WEBSSO_DEFAULT_REDIRECT_LOGOUT legacy)
5. Single `if logout_url:` redirect at the end

**Result:** Three-tier fallback system that works for ALL deployment types! 🎉
