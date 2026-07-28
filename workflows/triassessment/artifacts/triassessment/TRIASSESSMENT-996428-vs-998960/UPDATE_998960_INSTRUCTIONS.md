# Instructions to Update Review 998960 to Depend On 996428

**Goal:** Make your review 998960 extend (not conflict with) review 996428 by adding Depends-On and updating the code to work as a tiered fallback system.

---

## Prerequisites

- Local Horizon checkout with your 998960 changes
- Git configured for Gerrit (git-review installed)

---

## Step 1: Check Current State

```bash
cd /path/to/horizon
git branch  # Should show your 998960 branch
git log -1 --oneline  # Should show your 998960 commit
```

---

## Step 2: Update openstack_auth/views.py

**Current code in your 998960 (approximately):**

```python
# Around line 320 in logout() function
auth_type = request.session.get('auth_type')

# Your current approach
if auth_type and settings.WEBSSO_LOGOUT_REDIRECT_MAPPING:
    logout_url = settings.WEBSSO_LOGOUT_REDIRECT_MAPPING.get(auth_type)
    if logout_url:
        return shortcuts.redirect(logout_url)
```

**Change to (tiered fallback approach):**

```python
# Around line 320 in logout() function
auth_type = request.session.get('auth_type')
logout_url = None

# Tier 1: Check per-provider mapping (most specific)
if auth_type and settings.WEBSSO_LOGOUT_REDIRECT_MAPPING:
    logout_url = settings.WEBSSO_LOGOUT_REDIRECT_MAPPING.get(auth_type)

# Tier 2: Check global SSO logout URL (from 996428's WEBSSO_POST_LOGOUT_URL)
if not logout_url and auth_type != "credentials":
    logout_url = getattr(settings, 'WEBSSO_POST_LOGOUT_URL', None)

# Tier 3: Check legacy default redirect (existing Horizon setting)
if not logout_url and auth_type != "credentials":
    logout_url = getattr(settings, 'WEBSSO_DEFAULT_REDIRECT_LOGOUT', None)

# If we found a logout URL, redirect to it
if logout_url:
    return shortcuts.redirect(logout_url)

# Otherwise, fall back to default behavior (redirect to login)
```

**Key changes:**
1. Initialize `logout_url = None` at the start
2. Check WEBSSO_LOGOUT_REDIRECT_MAPPING first (Tier 1)
3. Check WEBSSO_POST_LOGOUT_URL second (Tier 2, from 996428)
4. Check WEBSSO_DEFAULT_REDIRECT_LOGOUT third (Tier 3, existing)
5. Single `if logout_url:` check at the end

---

## Step 3: Update Commit Message

**Add Depends-On line and reference all bugs:**

```bash
git commit --amend
```

**New commit message:**

```
Add per-provider SSO logout redirect support

This patch extends the WEBSSO_POST_LOGOUT_URL setting to support
multi-provider deployments where different SSO methods require
different logout URLs.

When WEBSSO_LOGOUT_REDIRECT_MAPPING is configured, the logout view
checks the user's auth_type and redirects to the provider-specific
logout URL. If no mapping is found, it falls back to
WEBSSO_POST_LOGOUT_URL (for all SSO users) or the existing
WEBSSO_DEFAULT_REDIRECT_LOGOUT.

Configuration tiers (priority order):
1. WEBSSO_LOGOUT_REDIRECT_MAPPING[auth_type] (most specific)
2. WEBSSO_POST_LOGOUT_URL (all SSO users, from parent patch)
3. WEBSSO_DEFAULT_REDIRECT_LOGOUT (legacy single-provider)

Example multi-provider configuration:
    WEBSSO_LOGOUT_REDIRECT_MAPPING = {
        "oidc": "https://idp.example.com/oidc/logout",
        "saml2": "https://idp.example.com/saml2/logout",
    }

Simple deployments can continue using WEBSSO_POST_LOGOUT_URL without
needing a dictionary.

Depends-On: I8302cd390b954ee8abfa2340ff9fd0df8ad88120
Closes-Bug: #2161654
Related-Bug: OSPRH-25872
Related-Bug: RHOSRFE-300
Change-Id: If11079a9a9e7cddff1bedf2dac0bdd10fd461f07
Signed-off-by: Owen McGonagle <omcgonag@redhat.com>
```

**Important:** Keep the same Change-Id! This updates the existing review instead of creating a new one.

---

## Step 4: Update Documentation (doc/source/configuration/settings.rst)

**Add a paragraph explaining the relationship with WEBSSO_POST_LOGOUT_URL:**

```rst
WEBSSO_LOGOUT_REDIRECT_MAPPING
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: <version>

Default: ``{}``

For multi-provider SSO deployments, this setting maps authentication
method identifiers to their respective logout URLs. This extends
:ref:`WEBSSO_POST_LOGOUT_URL` to support different logout URLs per
provider.

The logout view checks this mapping first. If the user's ``auth_type``
is found in the mapping, that URL is used. Otherwise, it falls back to
``WEBSSO_POST_LOGOUT_URL`` (if set), then ``WEBSSO_DEFAULT_REDIRECT_LOGOUT``.

Example for multi-provider deployment::

    WEBSSO_LOGOUT_REDIRECT_MAPPING = {
        "oidc": "https://idp.example.com/oidc/logout",
        "saml2": "https://idp.example.com/saml2/logout",
    }

For simple single-provider deployments, use ``WEBSSO_POST_LOGOUT_URL``
instead - no dictionary needed.

.. note::
   This setting depends on the ``WEBSSO_POST_LOGOUT_URL`` setting from
   patch I8302cd390b954ee8abfa2340ff9fd0df8ad88120. The tiered fallback
   ensures backward compatibility with existing configurations.
```

---

## Step 5: Update Release Note

**Update releasenotes/notes/websso-logout-redirect-mapping-cb65d71cda668e1a.yaml:**

Add a paragraph about extending WEBSSO_POST_LOGOUT_URL:

```yaml
---
features:
  - |
    Adds ``WEBSSO_LOGOUT_REDIRECT_MAPPING`` setting to support multi-provider
    SSO logout redirect. This extends the ``WEBSSO_POST_LOGOUT_URL`` setting
    (from I8302cd390b954ee8abfa2340ff9fd0df8ad88120) to enable operators to
    configure different logout URLs for different SSO providers.

    For deployments with multiple authentication methods (OIDC + SAML2, etc.),
    operators can now configure per-provider logout URLs::

        WEBSSO_LOGOUT_REDIRECT_MAPPING = {
            "oidc": "https://idp.example.com/oidc/logout",
            "saml2": "https://idp.example.com/saml2/logout",
        }

    The logout view uses a tiered fallback system:

    1. Check ``WEBSSO_LOGOUT_REDIRECT_MAPPING[auth_type]`` (most specific)
    2. Check ``WEBSSO_POST_LOGOUT_URL`` (all SSO users)
    3. Check ``WEBSSO_DEFAULT_REDIRECT_LOGOUT`` (legacy)

    Simple single-provider deployments can continue using
    ``WEBSSO_POST_LOGOUT_URL`` without needing a dictionary.

    Closes-Bug: #2161654
    Related-Bug: OSPRH-25872
    Related-Bug: RHOSRFE-300
```

---

## Step 6: Verify Changes

```bash
# Check what changed
git diff HEAD~1

# Should show:
# - Modified views.py (tiered fallback logic)
# - Modified commit message (Depends-On added)
# - Modified docs (extended explanation)
# - Modified release note (extended explanation)
```

---

## Step 7: Push Updated Review

```bash
# This updates the existing review 998960 (same Change-Id)
git review

# You'll see something like:
# remote: Processing changes: refs: 1, new: 0, updated: 1, done
# remote: Updated Changes:
# remote:   https://review.opendev.org/c/openstack/horizon/+/998960 Add per-provider SSO logout redirect support
```

---

## Step 8: Verify in Gerrit UI

1. Go to https://review.opendev.org/c/openstack/horizon/+/998960
2. You should see:
   - New patchset (#3)
   - "Depends-On" relationship showing link to 996428
   - Updated commit message
3. Check the "Related Changes" tab - should show 996428 as a dependency

---

## What Happens Next

**Gerrit Behavior:**

- Your 998960 will show as "depends on 996428"
- CI won't run on 998960 until 996428 merges (or you can test locally with both patches)
- When 996428 merges, Zuul will automatically test 998960 on top of it
- Core reviewers will see the dependency chain and can review both together

**Review Strategy:**

- 996428 needs to fix CI first (currently Verified -1)
- You can add unit tests to your 998960 that test the tiered fallback
- Both patches become mutually beneficial:
  - 996428 = simple single-provider solution + tests
  - 998960 = multi-provider extension with fallback

---

## Testing Locally (Optional)

If you want to test both patches together before 996428 merges:

```bash
# Download 996428
git review -d 996428

# Note the commit SHA
git log -1 --oneline  # Copy the SHA

# Switch to your branch
git checkout <your-998960-branch>

# Rebase onto 996428
git rebase <996428-commit-sha>

# Test locally
tox -e py311  # Run tests
tox -e pep8   # Run linters
```

---

## Benefits of This Approach

1. **No conflict** - Your code extends, not replaces
2. **Updates existing review** - Same Change-Id = same review number
3. **Gerrit shows dependency** - Clear relationship in UI
4. **Tiered fallback** - Works for simple AND complex deployments
5. **Both patches valuable** - 996428 provides base, 998960 extends it

---

## Summary

**What you're changing:**

1. Code: Add tiered fallback (check mapping → check POST_LOGOUT_URL → check DEFAULT_REDIRECT_LOGOUT)
2. Commit message: Add `Depends-On: I8302cd390b954ee8abfa2340ff9fd0df8ad88120`
3. Docs: Explain relationship with WEBSSO_POST_LOGOUT_URL
4. Release note: Explain tiered fallback system

**Result:**

- Review 998960 updates with new patchset #3
- Shows as depending on 996428 in Gerrit
- When 996428 merges, your 998960 automatically becomes ready
- Both authors get credit for their contributions!

---

**Questions?** Check the comparison assessment at:
http://10.0.151.101:8072/investigations/TRIASSESSMENT-996428-vs-998960
