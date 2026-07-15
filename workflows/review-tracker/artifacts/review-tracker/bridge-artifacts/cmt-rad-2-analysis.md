# Bridge Analysis: CMT-RAD-2

**Question:** "Same here, the policy is called 'reactivate'."

**Reviewer:** Radomir Dopieralski
**Review:** [https://review.opendev.org/c/openstack/horizon/+/986458](https://review.opendev.org/c/openstack/horizon/+/986458)
**File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:265`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L265)

---

## Investigation

This comment references the same architectural question as [CMT-RAD-1](cmt-rad-1-analysis.md)
applied to the `ReactivateImage` action.

### 1. Current code

```python
class ReactivateImage(tables.BatchAction):
    name = "reactivate"
    icon = "play"
    policy_rules = (("image", "reactivate"),)

    def allowed(self, request, image=None):
        if image is None:
            return True
        if image.owner != request.user.tenant_id:
            return False
        return image.status == "deactivated"
```

### 2. Analysis

The `policy_rules = (("image", "reactivate"),)` is correctly defined and handles RBAC
authorization. The `allowed()` method provides:

1. **Status check** (`image.status == "deactivated"`) — NECESSARY. Without it, the
   Reactivate button would appear on active images. RBAC policy cannot filter by image state.
2. **Ownership check** (`image.owner != request.user.tenant_id`) — follows existing patterns
   in this file (same as DeactivateImage, DeleteImage, EditImage).

See [CMT-RAD-1 analysis](cmt-rad-1-analysis.md) for the full framework investigation,
including the `_allowed()` AND-combination logic and the 58-action pattern survey.

### 3. Verdict

**Verdict:** Same as CMT-RAD-1 — `allowed()` is NECESSARY for the status check. The
ownership check is CONSISTENT with existing image action patterns.

---

## Suggested Response

> Same analysis as above — `policy_rules` handles RBAC ("can this user reactivate?") and `allowed()` handles state visibility ("only show on deactivated images"). Both are needed. See my reply on the DeactivateImage comment for the full reasoning.

---

## References

- See [CMT-RAD-1 analysis](cmt-rad-1-analysis.md) for complete framework investigation
- [`openstack_dashboard/dashboards/project/images/images/tables.py:260-265`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L260-L265) — ReactivateImage.allowed()
