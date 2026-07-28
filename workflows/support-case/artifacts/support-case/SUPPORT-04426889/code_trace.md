# Code Trace: Attach Interface (Case 04426889)

## UI Action Entry Point

**User action:** Click "Attach Interface" on an instance row in
Project > Compute > Instances.

## Call Chain Overview

```
User clicks "Attach Interface" button
    |
    v
[1] AttachInterface (tables.py)
    policy_rules = ("compute", "os_compute_api:os-attach-interfaces")
    --> Horizon checks legacy catch-all rule for button visibility
    --> In Wallaby: aliased to :list via DeprecatedRule
    --> rule:project_reader_or_admin -> PASSES (button shown)
    |
    v
[2] AttachInterface modal form (forms.py)
    __init__() calls network_field_data()
    |
    v
[3] network_field_data (utils.py)
    tenant_id = request.user.tenant_id
    networks = api.neutron.network_list_for_tenant(request, tenant_id)
    --> Scoped to current user's project (NOT the VM's project)
    |
    v
[4] network_list_for_tenant (neutron.py)
    Fetches: owned networks (tenant_id filter) + shared networks (no filter)
    Returns: merged list for dropdown population
    |
    v
[5] User submits form -> forms.py handle()
    api.nova.interface_attach(request, instance_id, net_id, fixed_ip, port_id)
    |
    v
[6] interface_attach (nova.py)
    novaclient(request).servers.interface_attach(server, port_id, net_id, fixed_ip)
    --> NO @policy_check decorator
    --> Direct novaclient call -> POST /servers/{id}/os-interface
    |
    v
[7] Nova API (server-side)
    Checks: os_compute_api:os-attach-interfaces:create
    --> rule:project_member_or_admin (Wallaby)
    --> If token scope/role doesn't match -> HTTP 403 Forbidden
```

## Detailed Code References

### [1] Button Visibility Check -- tables.py

**Branch:** stable/wallaby
**File:** [openstack_dashboard/dashboards/project/instances/tables.py](https://opendev.org/openstack/horizon/src/branch/stable/wallaby/openstack_dashboard/dashboards/project/instances/tables.py)
**Lines:** ~973-988

```python
class AttachInterface(policy.PolicyTargetMixin, tables.LinkAction):
    name = "attach_interface"
    verbose_name = _("Attach Interface")
    classes = ("btn-confirm", "ajax-modal")
    url = "horizon:project:instances:attach_interface"
    policy_rules = (("compute", "os_compute_api:os-attach-interfaces"),)

    def allowed(self, request, instance):
        return ((instance.status in ACTIVE_STATES or
                 instance.status == 'SHUTOFF') and
                not is_deleting(instance) and
                api.base.is_service_enabled(request, 'network'))
```

**Issue:** `policy_rules` references the legacy catch-all rule.
In Wallaby, this rule is deprecated and aliased to `:list` by oslo.policy.
The deprecation alias means the rule evaluates as:

```
os_compute_api:os-attach-interfaces
  -> DeprecatedRule -> maps to os_compute_api:os-attach-interfaces:list
  -> check_str: rule:project_reader_or_admin
```

This is a READ permission check for a WRITE operation button.

**Contrast with DetachInterface** (same file, ~line 991):

```python
class DetachInterface(policy.PolicyTargetMixin, tables.LinkAction):
    policy_rules = (("compute", "os_compute_api:os-attach-interfaces:delete"),)
```

DetachInterface correctly uses the granular `:delete` rule.

### [2] Form Initialization -- forms.py

**Branch:** stable/wallaby
**File:** [openstack_dashboard/dashboards/project/instances/forms.py](https://opendev.org/openstack/horizon/src/branch/stable/wallaby/openstack_dashboard/dashboards/project/instances/forms.py)
**Lines:** ~291-373

```python
class AttachInterface(forms.SelfHandlingForm):
    instance_id = forms.CharField(widget=forms.HiddenInput())
    network = forms.ThemableChoiceField(label=_("Network"))
    fixed_ip = forms.IPField(label=_("Fixed IP Address"), required=False)
    port = forms.ThemableChoiceField(label=_("Port"), required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        networks = instance_utils.network_field_data(
            request, include_empty_option=True, with_cidr=True)
        self.fields['network'].choices = networks
```

No policy check at form init. The network dropdown is populated unconditionally
if the button was shown.

### [3] Network Scoping -- utils.py

**Branch:** stable/wallaby
**File:** [openstack_dashboard/dashboards/project/instances/utils.py](https://opendev.org/openstack/horizon/src/branch/stable/wallaby/openstack_dashboard/dashboards/project/instances/utils.py)
**Lines:** ~83-120

```python
def network_field_data(request, include_empty_option=False, with_cidr=False,
                       for_launch=False):
    tenant_id = request.user.tenant_id    # <-- Current user's project, NOT VM's project
    networks = []
    if api.base.is_service_enabled(request, 'network'):
        extra_params = {}
        if for_launch:
            extra_params['include_pre_auto_allocate'] = True
        try:
            networks = api.neutron.network_list_for_tenant(
                request, tenant_id, **extra_params)
```

**Scoping behavior:** Uses `request.user.tenant_id`, which is the project
the user is currently scoped to. If an admin user is in the "admin" project
and opens attach-interface for a VM in "customer-project", the dropdown shows
only admin-project networks and shared networks -- NOT customer-project networks.

### [4] Network List -- neutron.py

**Branch:** stable/wallaby
**File:** [openstack_dashboard/api/neutron.py](https://opendev.org/openstack/horizon/src/branch/stable/wallaby/openstack_dashboard/api/neutron.py)
**Lines:** ~1055-1101

```python
def network_list_for_tenant(request, tenant_id, include_external=False,
                            include_pre_auto_allocate=False, **kwargs):
    tenant_networks = network_list(request, tenant_id=tenant_id,
                                   shared=False, **kwargs)
    shared_networks = network_list(request, shared=True, **kwargs)

    networks = tenant_networks + shared_networks
    # ... deduplication and optional external network inclusion ...
    return networks
```

Returns: tenant-owned + shared networks. External networks excluded by default.

### [5-6] Form Submission and API Call

**forms.py** `handle()` method (line ~352):

```python
def handle(self, request, data):
    instance_id = data['instance_id']
    network = data.get('network')
    port = data.get('port')
    fixed_ip = data.get('fixed_ip')
    # ...
    api.nova.interface_attach(request, instance_id,
                              net_id=net_id, fixed_ip=fixed_ip,
                              port_id=port_id)
```

**nova.py** `interface_attach()` (line ~1008):

```python
@profiler.trace
def interface_attach(request,
                     server, port_id=None, net_id=None, fixed_ip=None):
    return _nova.novaclient(request).servers.interface_attach(
        server, port_id, net_id, fixed_ip)
```

No `@policy_check` decorator. The function sends `POST /servers/{id}/os-interface`
directly to Nova. Authorization is enforced server-side.

### [7] Nova Server-Side Policy Check

**Branch:** stable/wallaby
**File:** [nova/policies/attach_interfaces.py](https://opendev.org/openstack/nova/src/branch/stable/wallaby/nova/policies/attach_interfaces.py)

```python
DEPRECATED_INTERFACES_POLICY = policy.DeprecatedRule(
    'os_compute_api:os-attach-interfaces',
    base.RULE_ADMIN_OR_OWNER,
)

attach_interfaces_policies = [
    policy.DocumentedRuleDefault(
        name='os_compute_api:os-attach-interfaces:create',
        check_str=base.SYSTEM_ADMIN_OR_OWNER,
        description="Attach an interface to a server",
        operations=[{'method': 'POST',
                     'path': '/servers/{server_id}/os-interface'}],
        scope_types=['system', 'project'],
        deprecated_rule=DEPRECATED_INTERFACES_POLICY,
        deprecated_reason="...",
        deprecated_since='21.0.0',
    ),
    # ... :list, :show, :delete similarly defined ...
]
```

Key commit: `01948df1a0` (Ghanshyam Mann, 2020-03-07)

## Policy Check Flow (Detailed)

```
+==============================================================+
|              POLICY CHECK: BUTTON VISIBILITY                 |
+==============================================================+
|                                                              |
|  AttachInterface.policy_rules:                               |
|    ("compute", "os_compute_api:os-attach-interfaces")        |
|        |                                                     |
|        v                                                     |
|  Horizon policy engine (openstack_auth/policy.py)            |
|  Looks up rule in bundled nova_policy.yaml                   |
|        |                                                     |
|        v                                                     |
|  TRAIN: "os_compute_api:os-attach-interfaces"                |
|         = "rule:admin_or_owner"                              |
|         --> Admin or project owner? YES -> Show button       |
|                                                              |
|  WALLABY: "os_compute_api:os-attach-interfaces"              |
|           = DEPRECATED, aliased to :list                     |
|           = "rule:project_reader_or_admin"                   |
|           --> Any project member or admin? YES -> Show button |
|                                                              |
+==============================================================+

+==============================================================+
|              POLICY CHECK: API AUTHORIZATION                 |
+==============================================================+
|                                                              |
|  Nova receives: POST /servers/{id}/os-interface              |
|        |                                                     |
|        v                                                     |
|  Nova policy engine checks:                                  |
|    "os_compute_api:os-attach-interfaces:create"              |
|        |                                                     |
|        v                                                     |
|  TRAIN: "rule:admin_or_owner"                                |
|         --> Same as button check -> CONSISTENT               |
|                                                              |
|  WALLABY (enforce_new_defaults=False):                       |
|         Falls back to deprecated rule:admin_or_owner         |
|         --> CONSISTENT (still works)                         |
|                                                              |
|  WALLABY (enforce_new_defaults=True):                        |
|         "rule:project_member_or_admin"                       |
|         --> Requires 'member' role scoped to correct project |
|         --> May DIVERGE from button check                    |
|         --> HTTP 403 if user has only 'reader' role          |
|         --> HTTP 403 if admin scoped to wrong project        |
|                                                              |
+==============================================================+
```

## Network Scoping Flow

```
+==============================================================+
|          NETWORK DROPDOWN POPULATION                         |
+==============================================================+
|                                                              |
|  network_field_data(request)                                 |
|      |                                                       |
|      v                                                       |
|  tenant_id = request.user.tenant_id                          |
|  (This is the CURRENT USER'S project, not the VM's project) |
|      |                                                       |
|      v                                                       |
|  network_list_for_tenant(request, tenant_id)                 |
|      |                                                       |
|      +---> network_list(tenant_id=tenant_id, shared=False)   |
|      |     Returns: networks OWNED by current project        |
|      |                                                       |
|      +---> network_list(shared=True)                         |
|      |     Returns: shared networks (visible to all)         |
|      |                                                       |
|      +---> (external networks NOT included by default)       |
|      |                                                       |
|      v                                                       |
|  Result: merged list = owned + shared                        |
|                                                              |
|  PROBLEM SCENARIO:                                           |
|  Admin user in "admin" project -> attach interface to VM     |
|  in "tenant-A" project -> dropdown shows admin-project       |
|  networks + shared networks -> tenant-A networks MISSING     |
|                                                              |
+==============================================================+
```

## Asymmetry: AttachInterface vs DetachInterface

```
+==============================================================+
|          HORIZON POLICY RULE ASYMMETRY                       |
+==============================================================+
|                                                              |
|  AttachInterface (tables.py ~978):                           |
|    policy_rules = (("compute",                               |
|      "os_compute_api:os-attach-interfaces"),)                |
|    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                  |
|    LEGACY catch-all rule -- aliased to :list in Wallaby      |
|    Checks READ access for a WRITE operation                  |
|                                                              |
|  DetachInterface (tables.py ~991):                           |
|    policy_rules = (("compute",                               |
|      "os_compute_api:os-attach-interfaces:delete"),)         |
|    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^          |
|    GRANULAR rule -- correct for Wallaby                      |
|    Checks DELETE access for a DELETE operation               |
|                                                              |
|  CONCLUSION: DetachInterface was updated to use granular     |
|  policy names. AttachInterface was not. This is the bug.     |
|                                                              |
+==============================================================+
```

## Version Comparison Summary

```
TRAIN (RHOSP 16.2)                          WALLABY (RHOSP 17.1)
================================             ================================
tables.py:                                   tables.py:
  policy_rules =                               policy_rules =
    "os-attach-interfaces"                       "os-attach-interfaces"
  (catch-all, resolves to                      (catch-all, DEPRECATED,
   rule:admin_or_owner)                         aliased to :list ->
                                                rule:project_reader_or_admin)

nova_policy.json:                            nova_policy.yaml:
  "os-attach-interfaces":                      (all commented out, uses
    "rule:admin_or_owner"                       Nova server-side defaults)
  "os-attach-interfaces:create":
    "rule:admin_or_owner"                    Nova defaults:
  "os-attach-interfaces:delete":               :list   -> project_reader_or_admin
    "rule:admin_or_owner"                      :show   -> project_reader_or_admin
                                               :create -> project_member_or_admin
  (All three rules have SAME                   :delete -> project_member_or_admin
   check_str, so no mismatch)
                                             (Button checks :list, API checks
                                              :create -> MISMATCH possible)

Result: Button + API agree                   Result: Button may show when API
                                              will reject (if enforce_new_defaults
                                              is true or custom policy is set)
```

## Fix Points

1. **Horizon tables.py** -- Change `AttachInterface.policy_rules` to
   `("compute", "os_compute_api:os-attach-interfaces:create")`

2. **Nova policy.yaml** (operator workaround) -- Add explicit override:
   `"os_compute_api:os-attach-interfaces": "rule:project_member_or_admin"`

3. **Network scoping** (separate issue) -- `network_field_data()` should
   optionally accept a target `project_id` for cross-project operations
