# Bridge Analysis: CMT-RAD-1

**Question:** Is there any case where `self.request` doesn't have the `horizon` attribute?

**Reviewer:** Radomir Dopieralski  
**Review:** 992902  
**File:** [`openstack_dashboard/dashboards/project/key_pairs/views.py:101`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/key_pairs/views.py#L101)

---

## Investigation

### 1. Where is `request.horizon` set?

**Source:** [`horizon/middleware/base.py:60`](https://github.com/openstack/horizon/blob/master/horizon/middleware/base.py#L60)

```python
def _process_request(self, request):
    """Adds data necessary for Horizon to function to the request."""
    
    request.horizon = {'dashboard': None,
                       'panel': None,
                       'async_messages': []}
```

**Lifecycle:** Set by `HorizonMiddleware._process_request()` on EVERY authenticated request that goes through the middleware stack.

**When it runs:** Django middleware executes in `MIDDLEWARE` order defined in `settings.py`. `HorizonMiddleware` is registered early in the stack, so `request.horizon` exists for all view handlers.

### 2. Edge cases where it might be missing

| Scenario | `horizon` present? | Why |
|----------|-------------------|-----|
| Production views | ✅ Yes | Middleware always runs before views |
| Unit tests (mocked request) | ❌ No | Tests often create mock Request objects without running middleware |
| Error handlers (500/404) | ✅ Yes | Middleware runs before errors are raised |
| Admin vs. project context | ✅ Yes | Same middleware for both |
| Unauthenticated requests | ✅ Yes | Middleware sets `horizon` dict even before auth check (line 60 runs unconditionally) |

### 3. How common is this defensive pattern?

**Defensive check count:** Only **2 occurrences** in the entire codebase

**Found at:**
1. [`horizon/middleware/base.py`](https://github.com/openstack/horizon/blob/master/horizon/middleware/base.py) — Checks `hasattr(request, 'horizon')` in AJAX handler (middleware checking its own state)
2. [`openstack_dashboard/dashboards/project/key_pairs/views.py:101`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/key_pairs/views.py#L101) — **Your code** (the one Radomir is asking about)

**Verdict:** This is NOT a common defensive pattern. Only 2 places check for `horizon` attribute existence, and one is the middleware itself.

### 4. Is the defensive check necessary?

**Answer:** The check is **safe but unnecessary in production**.

**Why it's safe:**
- No harm in checking — if middleware didn't run, the check prevents AttributeError
- Protects against test environments where middleware might be mocked out

**Why it's unnecessary:**
- Django guarantees middleware runs in order before views
- If `request.horizon` is missing in production, something catastrophic has already happened (middleware crashed or was removed from settings)
- Other Horizon code (e.g., [`horizon/messages.py`](https://github.com/openstack/horizon/blob/master/horizon/messages.py)) accesses `request.horizon['async_messages']` directly without defensive checks

**Recommendation:** 
- Keep the check if you want to be defensive for test environments
- Remove it if you prefer cleaner code and trust Django's middleware execution

---

## Suggested Response

> Good question! `request.horizon` is set by `HorizonMiddleware._process_request()` (line 60 in [`horizon/middleware/base.py`](https://github.com/openstack/horizon/blob/master/horizon/middleware/base.py#L60)) on every request before any view runs. It's guaranteed to exist in production.
>
> The defensive check is safe but unnecessary — only 2 places in the entire codebase check for it. Most Horizon code (like [`horizon/messages.py`](https://github.com/openstack/horizon/blob/master/horizon/messages.py)) directly accesses `request.horizon['async_messages']` without checking.
>
> I can remove the check if you prefer cleaner code, or keep it for extra safety in test environments. Your call!

---

## References

- [`horizon/middleware/base.py:57-62`](https://github.com/openstack/horizon/blob/master/horizon/middleware/base.py#L57-L62) — Where `request.horizon` is initialized
- [`horizon/messages.py`](https://github.com/openstack/horizon/blob/master/horizon/messages.py) — Example of direct access without defensive checks
- Django middleware documentation: Middleware runs in `MIDDLEWARE` order before all views
