# Bridge Analysis: CMT-RAD-2

**Question:** Is there any case where `self.request.horizon` exists but doesn't have the `async_messages` attribute?

**Reviewer:** Radomir Dopieralski  
**Review:** 992902  
**File:** [`openstack_dashboard/dashboards/project/key_pairs/views.py:103`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/key_pairs/views.py#L103)

---

## Investigation

### 1. Where is `async_messages` set?

**Source:** [`horizon/middleware/base.py:60-62`](https://github.com/openstack/horizon/blob/master/horizon/middleware/base.py#L60-L62)

```python
def _process_request(self, request):
    """Adds data necessary for Horizon to function to the request."""
    
    request.horizon = {'dashboard': None,
                       'panel': None,
                       'async_messages': []}
```

**Lifecycle:** `async_messages` is ALWAYS initialized as part of the `request.horizon` dict. They are created together in a single assignment. There is no code path where `request.horizon` exists but `async_messages` is missing.

### 2. Edge cases where it might be missing

| Scenario | `async_messages` present? | Why |
|----------|--------------------------|-----|
| Production views | ✅ Yes | Initialized alongside `request.horizon` in middleware |
| Unit tests (mocked request) | ⚠️ Maybe | Tests that manually create `request.horizon` might forget to add `async_messages` |
| Error handlers (500/404) | ✅ Yes | Middleware runs before errors |
| Modified by other code | ❌ Theoretically | If something deletes the `async_messages` key (extremely unlikely) |

### 3. How common is nested defensive checking for `async_messages`?

**Check count:** **ZERO** occurrences in the entire codebase

Your code at line 103 is the **only place** that checks `hasattr(self.request.horizon, 'async_messages')`.

**How everyone else accesses it:**

```python
# horizon/messages.py — DIRECT ACCESS (no hasattr check)
for tag, msg, extra in request.horizon['async_messages']:
    ...

# horizon/messages.py — DIRECT APPEND (no hasattr check)  
request.horizon['async_messages'].append([tag, message, extra_tags])

# horizon/middleware/base.py — DIRECT ACCESS (no hasattr check)
queued_msgs = request.horizon['async_messages']
```

(See [`horizon/messages.py`](https://github.com/openstack/horizon/blob/master/horizon/messages.py) and [`horizon/middleware/base.py`](https://github.com/openstack/horizon/blob/master/horizon/middleware/base.py) for full code)

**Verdict:** NO other code in Horizon checks for `async_messages` existence. Everyone assumes it's always there if `request.horizon` exists.

### 4. Is the nested defensive check necessary?

**Answer:** The nested check is **completely unnecessary**.

**Why:**
1. `request.horizon` is a dict created with `async_messages` key in a single statement
2. If `request.horizon` exists (checked by outer `hasattr`), then `async_messages` MUST exist
3. The middleware never modifies this structure after creation
4. No other Horizon code checks for it — everyone directly accesses `request.horizon['async_messages']`

**The simpler pattern:**

```python
# Current (overly defensive):
if hasattr(self.request, 'horizon'):
    if hasattr(self.request.horizon, 'async_messages'):
        messages = self.request.horizon['async_messages']

# Simpler (what rest of Horizon does):
if hasattr(self.request, 'horizon'):
    messages = self.request.horizon.get('async_messages', [])

# Or even simpler (safest dict access):
messages = getattr(self.request, 'horizon', {}).get('async_messages', [])
```

---

## Suggested Response

> Great catch! The nested check isn't needed. Once `request.horizon` exists (outer check passes), `async_messages` is guaranteed to be a key in that dict — they're initialized together in `HorizonMiddleware` (line 60-62).
>
> No other code in Horizon checks for `async_messages` existence. Places like `horizon/messages.py` directly access `request.horizon['async_messages']` without any defensive checks.
>
> I can simplify to:
> ```python
> if hasattr(self.request, 'horizon'):
>     messages = self.request.horizon.get('async_messages', [])
> ```
>
> Or even cleaner:
> ```python
> messages = getattr(self.request, 'horizon', {}).get('async_messages', [])
> ```

---

## References

- [`horizon/middleware/base.py:60-62`](https://github.com/openstack/horizon/blob/master/horizon/middleware/base.py#L60-L62) — Where `request.horizon` dict is created with `async_messages` key
- [`horizon/messages.py`](https://github.com/openstack/horizon/blob/master/horizon/messages.py) — Examples of direct `request.horizon['async_messages']` access without defensive checks
- [`horizon/middleware/base.py:85`](https://github.com/openstack/horizon/blob/master/horizon/middleware/base.py#L85) — Another example of direct access: `queued_msgs = request.horizon['async_messages']`
