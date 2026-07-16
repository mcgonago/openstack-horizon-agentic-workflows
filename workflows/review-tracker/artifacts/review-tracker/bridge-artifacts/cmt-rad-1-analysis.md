# Bridge Analysis: CMT-RAD-1

**Reviewer:** Radomir Dopieralski
**Review:** [https://review.opendev.org/c/openstack/horizon/+/986458](https://review.opendev.org/c/openstack/horizon/+/986458)
**File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:233`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L233)

---

## Comment Evolution

### Original Comment (PS6, 15:30 UTC)

> I think this should be an RBAC policy check -- the logic you have here matches the default policy, but this can be changed in a particular OpenStack install. I believe the policy for this is in glance and is called "deactivate". You will need to pass the image as the target to the check.

**Radomir's ask:** Replace the `allowed()` logic with an RBAC policy check using Glance's "deactivate" policy.

### Self-Correction (PS6, 15:37 UTC)

> Sorry, I didn't notice that you already have policy_rules defined on this action. In this case the allowed method should not be needed?

**Updated ask:** Since `policy_rules = (("image", "deactivate"),)` is already defined, is the `allowed()` method redundant?

### What Changed

Radomir's original comment assumed RBAC was missing. His self-correction acknowledges
RBAC is already handled by `policy_rules` and pivots to a different question: whether
`allowed()` is then unnecessary. **The analysis below addresses the updated question.**

---

## Investigation

### 1. How do `policy_rules` and `allowed()` interact?

*Answers the updated question: "In this case the allowed method should not be needed?"*

**Source:** [`horizon/tables/actions.py:130-137`](https://github.com/openstack/horizon/blob/master/horizon/tables/actions.py#L130-L137)
```python
def _allowed(self, request, datum):
    policy_check = utils_settings.import_setting("POLICY_CHECK_FUNCTION")
    if policy_check and self.policy_rules:
        target = self.get_policy_target(request, datum)
        return (policy_check(self.policy_rules, request, target) and
                self.allowed(request, datum))
    return self.allowed(request, datum)
```

**Lifecycle:** The framework combines both with AND logic:
- `policy_rules` -> RBAC: "Is this user authorized to perform this action?" (Keystone/Glance policy)
- `allowed()` -> State: "Is this action applicable to this particular datum?" (image status, ownership)

Both must pass for the action button to appear.

### 2. Is `allowed()` needed when `policy_rules` exists?

*Directly addresses Radomir's self-correction: "the allowed method should not be needed?"*

**Yes -- for the status check.** Without `allowed()`, the Deactivate button would appear on
already-deactivated images (and on images with any status) as long as the user has RBAC
permission. The RBAC policy "deactivate" controls *who* can deactivate, not *which images*
should show the button.

**Pattern evidence -- 58 actions** in the codebase use both `policy_rules` AND `allowed()`:

| Action | policy_rules | allowed() checks |
|--------|-------------|------------------|
| `DisableDomainsAction` | `identity:update_domain` | `datum.enabled` (state) |
| `EnableDomainsAction` | `identity:update_domain` | `not datum.enabled` (state) |
| `TogglePause` | `compute:os-pause-server` | instance status check |
| `DeleteImage` | `delete_image` | `image.protected`, `image.owner` |
| `EditImage` | `modify_image` | `image.status`, `image.owner` |
| **`DeactivateImage`** | **`deactivate`** | **`image.status == "active"`** |

The `DisableDomainsAction` / `EnableDomainsAction` pair is the closest analogue -- same
activate/deactivate pattern, both use `policy_rules` + `allowed()` with state checks only.

### 3. What about the ownership check?

*Addresses the original comment's implicit concern about matching "the default policy."*

The ownership check (`image.owner != request.user.tenant_id`) follows the existing pattern
in this file -- [`DeleteImage` (line 135)](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L135), [`EditImage` (line 163)](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L163), and [`UpdateMetadata` (line 201)](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L201) all perform the same check.

However, no image action overrides `get_policy_target()` -- the RBAC check runs with an
empty target dict `{}`. This means Glance's owner-based policy rules cannot evaluate at
the Horizon level. The `allowed()` ownership check fills this gap as defense-in-depth.

**Radomir is architecturally correct** that ideally this would be handled by RBAC alone,
but that would require:
1. Overriding `get_policy_target()` to pass the image as target
2. Ensuring the Glance policy file is available to Horizon's policy engine
3. This is not done by any existing image action in the codebase

### 4. Is the ownership check strictly necessary?

*Explores whether Radomir's original intuition (RBAC should handle everything) could work.*

| Scenario | Without ownership check | With ownership check |
|----------|------------------------|---------------------|
| User's own images | Deactivate shows (correct) | Deactivate shows (correct) |
| Other user's images (default policy) | RBAC policy hides it (probably) | `allowed()` hides it (definitely) |
| Admin on other's images (permissive policy) | Deactivate shows (correct for admin) | `allowed()` HIDES it (may be wrong for admin) |

The admin case is the tradeoff: the hardcoded ownership check prevents admins from using
the action even if their RBAC policy permits it. However, this matches the existing behavior
of `DeleteImage`, `EditImage`, and `UpdateMetadata` in this same file.

### 5. Verdict

**Verdict:** The `allowed()` method is NECESSARY for the status check (answers Radomir's
updated question). The ownership check is CONSISTENT with existing patterns but could
theoretically be replaced by proper RBAC target propagation -- a larger refactor not scoped
to this patch (acknowledges the spirit of Radomir's original comment).

---

## Suggested Response

> Good catch noticing the `policy_rules`! You're right that RBAC is already handled there. The `allowed()` method serves a different purpose though -- `_allowed()` in `horizon/tables/actions.py:130` combines them with AND logic. `policy_rules` handles RBAC authorization ("can this user deactivate?"), while `allowed()` handles state-based visibility ("should we show the button on this specific image?"). Without the status check in `allowed()`, the Deactivate button would appear on already-deactivated images. The ownership check follows the existing pattern from `DeleteImage` (line 135) and `EditImage` (line 163) in this same file. Happy to discuss if you'd prefer a different approach.

---

## References

- [`horizon/tables/actions.py:130-137`](https://github.com/openstack/horizon/blob/master/horizon/tables/actions.py#L130-L137) -- `_allowed()` combining policy_check and allowed()
- [`horizon/tables/actions.py:115-121`](https://github.com/openstack/horizon/blob/master/horizon/tables/actions.py#L115-L121) -- `get_policy_target()` returns empty dict by default
- [`openstack_dashboard/dashboards/project/images/images/tables.py:130-137`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L130-L137) -- DeleteImage.allowed() with same ownership pattern
- [`openstack_dashboard/dashboards/project/images/images/tables.py:160-166`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L160-L166) -- EditImage.allowed() with same ownership pattern
- [`openstack_dashboard/dashboards/project/images/images/tables.py:197-201`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L197-L201) -- UpdateMetadata.allowed() with same ownership pattern
- [`openstack_dashboard/dashboards/identity/domains/tables.py:147-149`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/identity/domains/tables.py#L147-L149) -- DisableDomainsAction.allowed() with state-only check (closest pattern match)
- 58 total actions in codebase with both `policy_rules` and `allowed()`
