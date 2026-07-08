# Investigation Report: Case 04426889

**Component:** Nova / Horizon (Attach Interface)
**OpenStack Version:** RHOSP 16.2 (Train) -> RHOSP 17.1 (Wallaby)
**Date:** 2026-06-01
**Classification:** Upgrade Regression + RBAC/Policy

## Symptom

Attach Interface operation fails after upgrading from RHOSP 16.2 to RHOSP 17.1.
The "Attach Interface" button is visible in the Horizon dashboard, but clicking
it either produces a "Not Authorized" error or shows no available networks in
the dropdown.

## Environment

- OpenStack version (before): RHOSP 16.2 (OpenStack Train, Horizon stable/train)
- OpenStack version (after): RHOSP 17.1 (OpenStack Wallaby, Horizon stable/wallaby)
- Affected component: Horizon (Dashboard) + Nova (Compute API)
- Affected operation: Attach Interface on an instance (Project > Compute > Instances)
- Deployment type: Director-based

## Root Cause Analysis

Two contributing factors, both triggered by the Train-to-Wallaby upgrade.

### Factor 1: Nova Policy Rule Split (Primary Cause)

In Nova 21.0.0 (Wallaby), the single policy rule `os_compute_api:os-attach-interfaces`
was split into four granular rules as part of the policy defaults refresh. Horizon's
`AttachInterface` table action was NOT updated to reference the new granular rule names,
creating a mismatch between button visibility and API authorization.

**The mismatch:**

| Layer | Policy Rule Checked | Result |
|---|---|---|
| Horizon button visibility | `os_compute_api:os-attach-interfaces` (legacy catch-all) | Aliased to `:list` via deprecation -> `rule:project_reader_or_admin` -> **PASSES** for any project member |
| Nova API authorization | `os_compute_api:os-attach-interfaces:create` (granular) | `rule:project_member_or_admin` -> May **FAIL** depending on scope and custom policy |

**Horizon code reference:**

File: [openstack_dashboard/dashboards/project/instances/tables.py](https://opendev.org/openstack/horizon/src/branch/stable/wallaby/openstack_dashboard/dashboards/project/instances/tables.py) line ~978

```python
class AttachInterface(policy.PolicyTargetMixin, tables.LinkAction):
    name = "attach_interface"
    verbose_name = _("Attach Interface")
    url = "horizon:project:instances:attach_interface"
    policy_rules = (("compute", "os_compute_api:os-attach-interfaces"),)
```

The `policy_rules` attribute checks the **legacy undifferentiated** rule, not
`os_compute_api:os-attach-interfaces:create`.

For comparison, `DetachInterface` (line ~991) already uses the correct granular rule:

```python
class DetachInterface(policy.PolicyTargetMixin, tables.LinkAction):
    policy_rules = (("compute", "os_compute_api:os-attach-interfaces:delete"),)
```

This asymmetry confirms that Horizon partially adopted the new policy names
but missed `AttachInterface`.

**Nova policy evolution (Train -> Wallaby):**

Train (Nova 20.x) -- three rules with identical check strings:

```json
"os_compute_api:os-attach-interfaces": "rule:admin_or_owner",
"os_compute_api:os-attach-interfaces:create": "rule:admin_or_owner",
"os_compute_api:os-attach-interfaces:delete": "rule:admin_or_owner"
```

Wallaby (Nova 23.x) -- base rule deprecated, four granular rules with new defaults:

```yaml
"os_compute_api:os-attach-interfaces:list":   "rule:project_reader_or_admin"
"os_compute_api:os-attach-interfaces:show":   "rule:project_reader_or_admin"
"os_compute_api:os-attach-interfaces:create": "rule:project_member_or_admin"
"os_compute_api:os-attach-interfaces:delete": "rule:project_member_or_admin"
```

The deprecated base rule is aliased to `:list` via `oslo.policy.DeprecatedRule`,
so Horizon's button visibility check evaluates read access (`:list`) while the
actual `POST /servers/{id}/os-interface` enforces write access (`:create`).

**Key upstream commit:** `01948df1a0` (Ghanshyam Mann, 2020-03-07) -- introduced
new default roles and deprecation aliases for attach-interfaces policy.

**When this breaks:**

With default settings (`enforce_scope=False`, `enforce_new_defaults=False`),
the old `rule:admin_or_owner` fallback keeps working via the deprecation alias.
The failure occurs when:

1. The deployment sets `enforce_new_defaults=True` in Nova's `oslo_policy`
   configuration, disabling the deprecation alias fallback
2. OR the deployment has custom policy overrides using the old rule name only,
   which map to `:list` but not to `:create`
3. OR the token scope doesn't satisfy `rule:project_member_or_admin`
   (e.g., a user with only `reader` role, or an admin scoped to the wrong
   project when `enforce_scope=True`)

### Factor 2: Network Scoping in Attach Interface Form (Contributing Factor)

The `AttachInterface` form populates its network dropdown via
`network_field_data()`, which scopes network queries to
`request.user.tenant_id`.

File: [openstack_dashboard/dashboards/project/instances/utils.py](https://opendev.org/openstack/horizon/src/branch/stable/wallaby/openstack_dashboard/dashboards/project/instances/utils.py) line ~83

```python
def network_field_data(request, include_empty_option=False, with_cidr=False,
                       for_launch=False):
    tenant_id = request.user.tenant_id
    networks = []
    if api.base.is_service_enabled(request, 'network'):
        try:
            networks = api.neutron.network_list_for_tenant(
                request, tenant_id)
```

`network_list_for_tenant()` retrieves:
1. Networks owned by `tenant_id` (filtered by `tenant_id`, `shared=False`)
2. Shared networks (no tenant filter)
3. External networks are NOT included (default `include_external=False`)

**Impact:** If an admin user operates from the "admin" project and attempts to
attach an interface to a VM in another project, the network dropdown only shows
networks owned by or shared with the admin project -- NOT the networks belonging
to the VM's actual project. This results in an empty or incomplete network list.

This behavior is identical between Train and Wallaby -- it is a pre-existing
design limitation, not a regression. It becomes more noticeable when combined
with the policy mismatch (the button appears due to the lenient `:list` check,
but the form cannot display the correct networks).

## Evidence

### Policy Rule Comparison (Train vs Wallaby)

| Aspect | Train (RHOSP 16.2) | Wallaby (RHOSP 17.1) |
|---|---|---|
| Config format | `nova_policy.json` | `nova_policy.yaml` (commented defaults, relies on Nova code) |
| Base rule `os-attach-interfaces` | `rule:admin_or_owner` (active) | Deprecated, aliased to `:list` |
| `:list` rule | Not present | `rule:project_reader_or_admin` |
| `:show` rule | Not present | `rule:project_reader_or_admin` |
| `:create` rule | `rule:admin_or_owner` | `rule:project_member_or_admin` |
| `:delete` rule | `rule:admin_or_owner` | `rule:project_member_or_admin` |
| `scope_types` | None | `['project']` |

### Horizon Code Asymmetry

| Action | Policy Rule in `tables.py` | Correct? |
|---|---|---|
| AttachInterface | `os_compute_api:os-attach-interfaces` (legacy catch-all) | **No** -- should use `:create` |
| DetachInterface | `os_compute_api:os-attach-interfaces:delete` (granular) | Yes |

### Key Upstream Commits

| SHA | Date | Author | Description |
|---|---|---|---|
| `616102a9ff` | 2016-08-09 | Andrew Laski | Initial create/delete split in Nova (Bug 1610069) |
| `01948df1a0` | 2020-03-07 | Ghanshyam Mann | New default roles + deprecation aliases |
| `6cfc912ea5` | 2020-03-04 | Ghanshyam Mann | Introduce `scope_types=['system', 'project']` |
| `d7be635fb4` | 2022-02-09 | Ghanshyam Mann | Narrow scope_types to `['project']` only |
| `909b0b0247` | 2022-08-24 | Ghanshyam Mann | Keep legacy admin behaviour in new RBAC |

## Severity Assessment

| Dimension | Rating | Rationale |
|---|---|---|
| Impact | High | Attach Interface is a core VM operation; failure blocks network configuration |
| Urgency | Medium | Workaround available (CLI); only affects Horizon UI, not programmatic access |
| Scope | Wide | Affects all RHOSP 16.2->17.1 upgrades with `enforce_new_defaults=True` or custom policy |
| Workaround | Available | Use OpenStack CLI or correct the Horizon policy reference (see below) |

## Proposed Resolution

### Immediate Workaround (no code change required)

**Option A: Ensure deprecated policy defaults are active (recommended)**

Verify that Nova is NOT enforcing new defaults prematurely:

```bash
grep -r "enforce_new_defaults\|enforce_scope" /etc/nova/nova.conf

# Expected safe values:
# [oslo_policy]
# enforce_scope = false
# enforce_new_defaults = false
```

If either is set to `true`, the deprecated policy alias for the legacy
`os_compute_api:os-attach-interfaces` rule is disabled, and Horizon's
button visibility check diverges from Nova's API authorization.

**Option B: Use CLI as workaround**

```bash
# Attach an interface via CLI (bypasses Horizon entirely)
openstack server add port <server-id> <port-id>

# Or with a network (auto-assigns port):
openstack port create --network <network-id> --project <project-id> my-port
openstack server add port <server-id> my-port
```

**Option C: Add explicit policy override**

If `enforce_new_defaults=True` is required, add an explicit override in
`/etc/nova/policy.yaml`:

```yaml
# Restore backward compatibility for Horizon's button check
"os_compute_api:os-attach-interfaces": "rule:project_member_or_admin"
```

This makes the legacy catch-all rule equivalent to `:create`, so Horizon's
button visibility aligns with the actual API authorization.

### Long-Term Fix (Horizon code change)

Update `AttachInterface.policy_rules` in `tables.py` to use the granular rule:

```python
class AttachInterface(policy.PolicyTargetMixin, tables.LinkAction):
    policy_rules = (("compute", "os_compute_api:os-attach-interfaces:create"),)
```

This aligns with how `DetachInterface` already references `:delete`.

**Always test any fix in a non-production environment first.**

## Related Findings

1. **Network scoping limitation**: The attach-interface form always scopes
   network queries to the current user's project, not the target VM's project.
   This is a pre-existing design limitation, not a regression.

2. **DetachInterface is correctly implemented**: The `DetachInterface` action
   already uses the granular rule, confirming Horizon partially adopted the
   new policy names but missed `AttachInterface`.

## References

- [Nova Policy Default Refresh Spec](https://specs.openstack.org/openstack/nova-specs/specs/ussuri/implemented/policy-defaults-refresh.html)
- [Nova Wallaby Sample Policy](https://docs.openstack.org/nova/wallaby/configuration/sample-policy.html)
- [oslo.policy Deprecation Mechanism](https://docs.openstack.org/oslo.policy/latest/)
- [Horizon instances tables.py (wallaby)](https://opendev.org/openstack/horizon/src/branch/stable/wallaby/openstack_dashboard/dashboards/project/instances/tables.py)
- [Nova attach_interfaces.py policy (wallaby)](https://opendev.org/openstack/nova/src/branch/stable/wallaby/nova/policies/attach_interfaces.py)
- [Launchpad Bug 1610069](https://bugs.launchpad.net/nova/+bug/1610069) -- Original create/delete policy split

