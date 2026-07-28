# Bridge Analysis: CMT-RAD-1

**Reviewer:** Radomir Dopieralski
**Review:** [https://review.opendev.org/c/openstack/horizon/+/986458](https://review.opendev.org/c/openstack/horizon/+/986458)
**File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:233`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L233)

---

## Comment Evolution

### Original Comment (PS6, 15:30 UTC)

> I think this should be an RBAC policy check -- the logic you have here matches the default policy, but this can be changed in a particular OpenStack install. I believe the policy for this is in glance and is called "deactivate". You will need to pass the image as the target to the check.

**Reviewer's ask:** Replace the `allowed()` logic with an RBAC policy check using Glance's "deactivate" policy.

### Self-Correction (PS6, 15:37 UTC)

> Sorry, I didn't notice that you already have policy_rules defined on this action. In this case the allowed method should not be needed?

**Updated ask:** Since `policy_rules = (("image", "deactivate"),)` is already defined, is the `allowed()` method redundant?

### Owen's Reply (PS6, 01:59 UTC Jul 16)

> I believe without the check on allowed() we de-activate button may appear on already de-activiated messages - I am testing that theory right now.

**Owen's response:** Defending the status check in `allowed()` as needed to prevent the button appearing on already-deactivated images.

### Radomir's Follow-Up (PS6, 07:30 UTC Jul 16)

> Good point. But the owner check seems harmful, especially if the policy is changed to allow changing images that are not yours?

**Latest ask:** Radomir accepts the status check is needed but now specifically objects to the **owner check** (`image.owner != request.user.tenant_id`) as it overrides RBAC policy flexibility.

### Owen's Detailed Response (PS6, 15:38 UTC Jul 16)

Owen posted a comprehensive response citing:
- Admin panel overrides (`AdminDeleteImage`/`AdminEditImage` return `True` without owner checks)
- Existing convention: all image actions (`DeleteImage`, `EditImage`, `UpdateMetadata`) have the same owner check
- Admin panel lacks Deactivate/Reactivate actions entirely
- `PolicyTargetMixin` as the proper architectural follow-up
- Offered to explore adopting `PolicyTargetMixin` for image actions as a follow-up

**Current state:** Ball is in Radomir's court. Waiting for his decision.

### What Changed

The conversation has evolved through four phases:
1. "Add RBAC" (original) -- resolved: `policy_rules` already exists
2. "Is `allowed()` redundant?" (self-correction) -- resolved: status check is needed
3. "The owner check is harmful" (follow-up) -- Owen responded with evidence
4. **Waiting for Radomir's decision** (current) -- Owen's response is posted, no reply yet

**The analysis below addresses Radomir's owner check concern. Owen has since responded on Gerrit using this analysis.**

---

## Investigation

*Answers the latest question: "the owner check seems harmful, especially if the policy is changed to allow changing images that are not yours?"*

### 1. What does the owner check do?

**Source:** [`openstack_dashboard/dashboards/project/images/images/tables.py:231`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L231)
```python
def allowed(self, request, image=None):
    if image is None:
        return True
    if image.protected:
        return False
    if image.owner != request.user.tenant_id:
        return False          # <-- the line Radomir flags
    return image.status == "active"
```

The owner check hides the Deactivate button on images not owned by the current user's project. This runs AFTER the RBAC policy check (`policy_rules`), so even if Glance policy allows a user to deactivate other projects' images, the button still won't appear.

### 2. Is this a project-panel convention?

**Yes -- ALL existing image actions in the project panel have the same owner check:**

| Action | Owner Check | Source |
|--------|------------|--------|
| `DeleteImage` | `image.owner == request.user.tenant_id` | [`tables.py:135`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L135) |
| `EditImage` | `image.owner == request.user.tenant_id` | [`tables.py:163`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L163) |
| `UpdateMetadata` | `image.owner == request.user.project_id` | [`tables.py:201`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L201) |
| **`DeactivateImage`** | **`image.owner != request.user.tenant_id`** | **`tables.py:231`** |
| **`ReactivateImage`** | **`image.owner != request.user.tenant_id`** | **`tables.py:263`** |

The owner check is NOT unique to this patch -- it follows the established convention.

### 3. How does the admin panel handle this?

**The admin panel OVERRIDES the owner check for admins:**

**Source:** [`openstack_dashboard/dashboards/admin/images/tables.py:29-41`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L29-L41)
```python
class AdminDeleteImage(project_tables.DeleteImage):
    def allowed(self, request, image=None):
        if image and image.protected:
            return False
        return True   # No owner check -- admins can delete any image

class AdminEditImage(project_tables.EditImage):
    def allowed(self, request, image=None):
        return True   # No owner check -- admins can edit any image
```

This is the established Horizon pattern:
- **Project panel** = owner check (defense-in-depth, assumes default policy)
- **Admin panel** = no owner check (trusts RBAC, admins act on any resource)

### 4. Is Radomir's concern valid?

**Yes, architecturally.** The hardcoded owner check does override RBAC flexibility. If an operator modifies Glance policy to let users deactivate images from other projects, the Horizon button still won't appear.

**But the concern applies equally to DeleteImage and EditImage**, which have had the same check for years. Removing it only from DeactivateImage/ReactivateImage while keeping it on DeleteImage/EditImage would be inconsistent.

### 5. Alternative patterns in the codebase

The volume and instance panels use `PolicyTargetMixin` to pass resource ownership to the RBAC check, letting policy decide:

**Source:** [`openstack_dashboard/dashboards/project/volumes/tables.py:47`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47)
```python
class VolumePolicyTargetMixin(policy.PolicyTargetMixin):
    policy_target_attrs = (("project_id", 'os-vol-tenant-attr:tenant_id'),)
```

Image actions do NOT use `PolicyTargetMixin`. Adopting it would be the correct architectural fix but is a larger refactor affecting all image actions, not scoped to this patch.

### 6. The missing admin actions

**The admin panel currently has NO Deactivate/Reactivate actions** -- `AdminImagesTable.row_actions` only includes `AdminEditImage`, `UpdateMetadata`, and `AdminDeleteImage`. This means admins currently cannot deactivate/reactivate images through the Horizon UI at all (they must use the CLI).

Adding `AdminDeactivateImage` and `AdminReactivateImage` (without owner checks) to the admin panel would be the natural follow-up.

### 7. Verdict

**Verdict:** Radomir's concern about the owner check is **VALID in principle** but:

1. The owner check **matches all existing image actions** in the project panel (DeleteImage, EditImage, UpdateMetadata)
2. The admin panel **overrides** to remove it -- this is the established convention
3. Removing it only from DeactivateImage would be **inconsistent**
4. The proper fix (PolicyTargetMixin or removing all owner checks) is a **larger refactor** not scoped to this patch

**Recommended approach:** Keep the owner check for consistency, offer to either (a) remove it if Radomir feels strongly (but then all image actions should change together), or (b) add admin panel actions without owner checks as a follow-up.

---

## Suggested Response

> Good point -- you're right that the hardcoded owner check does override RBAC flexibility. If an operator changes the Glance policy to let non-owners deactivate images, the button still wouldn't appear.
>
> I kept the owner check because it matches the existing convention for all image actions in the project panel -- DeleteImage (line 135), EditImage (line 163), and UpdateMetadata (line 201) all do the same check. The admin panel overrides it (AdminDeleteImage and AdminEditImage both return True without owner checks).
>
> I can go either way:
> 1. Keep the owner check for consistency with the existing actions (and add AdminDeactivateImage/AdminReactivateImage to the admin panel in a follow-up)
> 2. Remove the owner check from DeactivateImage/ReactivateImage to be more policy-flexible -- but that would make them inconsistent with Delete/Edit
>
> Which approach would you prefer? Or should the owner check removal be a separate patch that addresses all image actions together?

---

## References

- [`horizon/tables/actions.py:130-137`](https://github.com/openstack/horizon/blob/master/horizon/tables/actions.py#L130-L137) -- `_allowed()` combining policy_check and allowed()
- [`openstack_dashboard/dashboards/project/images/images/tables.py:130-137`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L130-L137) -- DeleteImage.allowed() with same owner check
- [`openstack_dashboard/dashboards/project/images/images/tables.py:160-166`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L160-L166) -- EditImage.allowed() with same owner check
- [`openstack_dashboard/dashboards/project/images/images/tables.py:197-201`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L197-L201) -- UpdateMetadata.allowed() with same owner check
- [`openstack_dashboard/dashboards/admin/images/tables.py:29-34`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L29-L34) -- AdminDeleteImage overrides to remove owner check
- [`openstack_dashboard/dashboards/admin/images/tables.py:37-41`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L37-L41) -- AdminEditImage overrides to remove owner check
- [`openstack_dashboard/dashboards/admin/images/tables.py:87-91`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L87-L91) -- AdminImagesTable.row_actions (no deactivate/reactivate)
- [`openstack_dashboard/dashboards/project/volumes/tables.py:47`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47) -- VolumePolicyTargetMixin using policy_target_attrs (alternative pattern)
