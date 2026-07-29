# Code Review: Add per-provider SSO logout redirect support

**Change**: [https://review.opendev.org/c/openstack/horizon/+/998960](https://review.opendev.org/c/openstack/horizon/+/998960)
**Files**: 5 files changed (316 insertions, 3 deletions) — auth views, tests, config, docs, release note
**Date**: 2026-07-29
**Verdict**: APPROVE

## Summary

This change solves LP#2161654 (SSO logout broken in multi-provider deployments) by introducing `WEBSSO_LOGOUT_REDIRECT_MAPPING`, which enables per-provider logout redirect when multiple SSO authentication methods are configured. The implementation uses a 3-tier fallback system (per-provider → global SSO → legacy) with comprehensive test coverage (9 new tests), thorough documentation (65 lines), and full backward compatibility. The change is purely additive with no plugin API impact.

## Review History

No prior reviewer comments — this is the first review (PS7, marked ready for review on 2026-07-29).

## Blockers

None.

### Plugin API Impact

**No breaking changes.** The change is purely additive:
- New config option `WEBSSO_LOGOUT_REDIRECT_MAPPING = {}` with safe default (empty dict)
- The `logout()` function signature is unchanged (`logout(request, login_url=None, **kwargs)`)
- Uses `hasattr()` and `.get()` for safe access to new config
- No changes to `horizon/` base classes that plugins might extend

Existing deployments continue working unchanged. Behavior only changes when the new config is explicitly set.

### Missing Regression Test

**Not applicable.** The change includes comprehensive regression test coverage:
- Test #3 (`test_websso_logout_tier2_post_logout_url`) serves as the primary regression test for LP#2161654 — multi-provider deployments now use tier 2 (WEBSSO_POST_LOGOUT_URL) instead of incorrectly falling back to tier 3 (legacy single-provider)
- 9 total tests cover all code paths, edge cases, and precedence rules

### Intent or Architecture Issues

**None.** The change correctly implements the stated intent and fits Horizon's architecture:
- Tiered fallback matches Horizon's "specific → general → default" pattern (similar to region selection, endpoint resolution)
- Configuration naming follows established `WEBSSO_*` prefix convention
- Deprecation approach is sound: legacy tier 3 still works, but docs recommend tier 1/2 for multi-provider deployments

## Suggestions

### Minor: Tier 1 should exclude credentials users

**File**: `openstack_auth/views.py:302-306`

Tier 2 (line 309) includes a gate condition `auth_type != "credentials"` to prevent credentials users from hitting SSO logout. Tier 1 doesn't have this check. While extremely unlikely in practice (why would an operator map `"credentials"` to an SSO logout URL?), adding the same check to tier 1 would make the logic more robust:

```python
# Current (line 302):
if auth_type and hasattr(settings, 'WEBSSO_LOGOUT_REDIRECT_MAPPING'):

# Suggested:
if auth_type and auth_type != "credentials" and hasattr(settings, 'WEBSSO_LOGOUT_REDIRECT_MAPPING'):
```

This prevents a misconfigured `WEBSSO_LOGOUT_REDIRECT_MAPPING = {"credentials": "..."}` from redirecting credentials users to an SSO logout URL.

### Minor: Log message consistency

**File**: `openstack_auth/views.py:305-306`

The tier 1 log message uses both the `auth_type` variable and a string literal placeholder. For easier grepping and consistency with tiers 2-3, consider:

```python
# Current:
LOG.info('Redirecting logout to SSO provider "%s": %s',
         auth_type, logout_url)

# Suggested (matches tier 2/3 pattern):
LOG.info('Using tier 1 logout for auth_type=%s: %s', 
         auth_type, logout_url)
```

## Nits

None.

## Positive Feedback

**Excellent test coverage:** 9 tests covering all branches, edge cases, and precedence rules. Tests use realistic session manipulation and check exact redirect URLs (not just status codes).

**Outstanding documentation:** 65 lines of settings documentation with:
- Clear explanation of the 3-tier fallback system
- Realistic multi-IdP example configuration
- Guidance on when to use each tier
- Backward compatibility notes
- Proper versioning (`.. versionadded:: Caracal`)

**Good logging for debugging:** Each tier logs which configuration option was used and the target URL, making troubleshooting SSO logout issues straightforward.

**Thoughtful backward compatibility:** The tiered approach allows existing single-provider deployments (tier 3) to continue working while enabling new multi-provider deployments (tier 1) without breaking changes.

## Files Reviewed

| File | Type | Notes |
|---|---|---|
| `openstack_auth/views.py` | Modified | Implements 3-tier logout redirect logic (38 insertions) |
| `openstack_auth/defaults.py` | Modified | Adds `WEBSSO_LOGOUT_REDIRECT_MAPPING = {}` with docstring (14 insertions) |
| `openstack_auth/tests/unit/test_auth.py` | Modified | 9 new tests covering all tiers and edge cases (157 insertions) |
| `doc/source/configuration/settings.rst` | Modified | 65 lines of configuration documentation with examples |
| `releasenotes/notes/websso-logout-redirect-mapping-*.yaml` | Added | Release note with features section and deprecation notice (45 lines) |
