# OpenStack Horizon -- Support Case Investigation Knowledge

## Purpose

This document provides structured knowledge for investigating customer
support cases related to OpenStack Horizon (the dashboard service).
It covers symptom classification, code tracing methodology, version
regression analysis, and investigation output formats.

When investigating a support case, reference this document to apply
Horizon-specific investigation patterns rather than relying on
general-purpose troubleshooting.

---

## 1. Symptom Classification

Classify the reported symptom into one of these categories FIRST.
The category determines which investigation path to follow.

| Category | Symptoms | Investigation Path |
|---|---|---|
| API Proxy Failure | 4xx/5xx from Horizon API calls, "Unable to ..." errors, operations that work in CLI but fail in dashboard | Trace the API proxy path (Section 2.1) |
| RBAC / Policy | "You are not authorized", actions or buttons missing from UI, operations fail for certain user roles | Check policy files and scope_types (Section 4) |
| Upgrade Regression | "Worked in version X, broke in version Y", any symptom appearing after an upgrade | Version comparison analysis (Section 3) |
| UI Rendering | Blank panels, broken forms, JavaScript errors in browser console, missing page elements | Check template + static file changes (Section 5) |
| Session / Auth | Login failures, session timeouts, SSO problems, token errors, redirect loops | Check Keystone auth flow (Section 7) |
| Performance | Slow page loads, request timeouts, high memory usage, dashboard unresponsive under load | Check API call patterns + caching (Section 7) |

### Classification Decision Tree

```
Customer reports a problem
    |
    +-- Does it involve an upgrade? ---------> UPGRADE REGRESSION (Section 3)
    |                                          (also check RBAC if policy-related)
    |
    +-- Does it mention "not authorized" ----> RBAC / POLICY (Section 4)
    |   or missing buttons/actions?
    |
    +-- Does it mention an error message ----> API PROXY FAILURE (Section 2)
    |   like "Unable to ..." or a 4xx/5xx?
    |
    +-- Does it mention blank pages, -------> UI RENDERING (Section 5)
    |   broken layout, or JS errors?
    |
    +-- Does it mention login, session, ----> SESSION / AUTH (Section 7)
    |   or token problems?
    |
    +-- Does it mention slowness or --------> PERFORMANCE (Section 7)
        timeouts?
```

---

## 2. Code Tracing Methodology

### 2.1 API Proxy Path (Most Common Investigation Pattern)

When Horizon shows an API error, trace the call chain from the UI action
through to the backend service:

```
+==============================================================+
|            HORIZON API PROXY CALL CHAIN                      |
+==============================================================+
|                                                              |
|  USER CLICKS BUTTON IN HORIZON UI                            |
|      |                                                       |
|      v                                                       |
|  JavaScript/AJAX call to Horizon endpoint                    |
|  (static/dashboard/ JS files or form POST)                   |
|      |                                                       |
|      v                                                       |
|  Django URL router                                           |
|  (openstack_dashboard/dashboards/<panel>/urls.py)            |
|      |                                                       |
|      v                                                       |
|  Django view or REST API handler                             |
|  (openstack_dashboard/dashboards/<panel>/views.py  or        |
|   openstack_dashboard/api/rest/<service>.py)                 |
|      |                                                       |
|      v                                                       |
|  API abstraction layer                                       |
|  (openstack_dashboard/api/<service>.py)                      |
|  Files: nova.py, neutron.py, cinder.py, keystone.py,         |
|         glance.py, heat.py                                   |
|      |                                                       |
|      v                                                       |
|  OpenStack SDK / client library call                         |
|  (openstacksdk, novaclient, neutronclient, etc.)             |
|      |                                                       |
|      v                                                       |
|  OpenStack service API                                       |
|  (Keystone, Nova, Neutron, Cinder, Glance, Heat)             |
|                                                              |
+==============================================================+
```

### 2.2 Key Files by Service

| Service | Horizon API File | Dashboard Panels | Client Library |
|---|---|---|---|
| Nova | [openstack_dashboard/api/nova.py](https://opendev.org/openstack/horizon/src/branch/master/openstack_dashboard/api/nova.py) | project/instances/, admin/instances/ | novaclient / openstacksdk |
| Neutron | [openstack_dashboard/api/neutron.py](https://opendev.org/openstack/horizon/src/branch/master/openstack_dashboard/api/neutron.py) | project/networks/, admin/networks/ | openstacksdk (migrating from neutronclient) |
| Cinder | [openstack_dashboard/api/cinder.py](https://opendev.org/openstack/horizon/src/branch/master/openstack_dashboard/api/cinder.py) | project/volumes/, admin/volumes/ | cinderclient / openstacksdk |
| Keystone | [openstack_dashboard/api/keystone.py](https://opendev.org/openstack/horizon/src/branch/master/openstack_dashboard/api/keystone.py) | identity/ | keystoneclient |
| Glance | [openstack_dashboard/api/glance.py](https://opendev.org/openstack/horizon/src/branch/master/openstack_dashboard/api/glance.py) | project/images/, admin/images/ | glanceclient |
| Heat | [openstack_dashboard/api/heat.py](https://opendev.org/openstack/horizon/src/branch/master/openstack_dashboard/api/heat.py) | project/stacks/ | heatclient |

### 2.3 Panel File Structure

Each Horizon panel follows a consistent Django layout:

```
openstack_dashboard/dashboards/<dashboard>/<panel>/
+-- __init__.py
+-- forms.py          <-- form classes (input validation + API calls)
+-- panel.py          <-- panel registration
+-- tables.py         <-- table actions (buttons, row actions)
+-- tabs.py           <-- tab definitions
+-- tests.py          <-- unit tests
+-- urls.py           <-- URL routing
+-- views.py          <-- Django views
+-- templates/<panel>/
    +-- *.html        <-- Jinja2/Django templates
```

### 2.4 Network Scoping Pattern (Common Post-Upgrade Issue)

Many post-upgrade failures trace to how Horizon scopes API queries.
The pattern:

```
BEFORE (older versions -- admin sees everything):
  api.neutron.network_list(request)
  --> No project_id filter
  --> ALL networks returned

AFTER (newer versions -- project-scoped queries):
  tenant_id = request.user.tenant_id
  api.neutron.network_list_for_tenant(request, tenant_id)
  --> Filtered by project
  --> Only project-owned + shared networks returned
  --> Admin user in "admin" project sees NO tenant networks
```

**Critical file**: [openstack_dashboard/dashboards/project/instances/utils.py](https://opendev.org/openstack/horizon/src/branch/master/openstack_dashboard/dashboards/project/instances/utils.py)

The function `network_field_data()` at line ~95 uses
`request.user.tenant_id` to scope network queries. When an admin
user operates from the admin project, this returns only networks owned
by or shared with the admin project -- NOT the networks belonging to
the VM's actual project.

---

## 3. Version Regression Detection

### 3.1 OpenStack Release Version Map

| OpenStack Release | Horizon Branch | Key Changes |
|---|---|---|
| Queens | [stable/queens](https://opendev.org/openstack/horizon/src/branch/stable/queens) | AngularJS panels, legacy policy |
| Train | [stable/train](https://opendev.org/openstack/horizon/src/branch/stable/train) | neutronclient, Angular panels |
| Wallaby | [stable/wallaby](https://opendev.org/openstack/horizon/src/branch/stable/wallaby) | SDK migration started, SRBAC introduced, policy deprecations |
| 2023.2 (Antelope) | [stable/2023.2](https://opendev.org/openstack/horizon/src/branch/stable/2023.2) | De-angularization, openstacksdk default, Django 4.2 |

### 3.2 Regression Detection Workflow

```
+==============================================================+
|          VERSION REGRESSION DETECTION PROCESS                |
+==============================================================+
|                                                              |
|  Step 1: IDENTIFY VERSION PAIR                               |
|  +-------------------------------------------------------+   |
|  | Before upgrade: Distro X.Y = OpenStack <release-A>    |   |
|  | After upgrade:  Distro X.Y = OpenStack <release-B>    |   |
|  | Use the version map above to find branch names        |   |
|  +-------------------------------------------------------+   |
|      |                                                       |
|      v                                                       |
|  Step 2: DIFF THE AFFECTED CODE PATH                         |
|  +-------------------------------------------------------+   |
|  | git diff stable/<release-A>..stable/<release-B>       |   |
|  |          -- <file-path>                               |   |
|  |                                                       |   |
|  | Example for Train->Wallaby:                           |   |
|  |   git diff stable/train..stable/wallaby --            |   |
|  |     openstack_dashboard/dashboards/project/           |   |
|  |     instances/forms.py                                |   |
|  +-------------------------------------------------------+   |
|      |                                                       |
|      v                                                       |
|  Step 3: CATEGORIZE THE CHANGES                              |
|  +-------------------------------------------------------+   |
|  | Look for:                                             |   |
|  | - Function signature changes (new/removed params)     |   |
|  | - SDK migration (neutronclient -> openstacksdk)       |   |
|  | - Policy rule renames or splits (deprecation)         |   |
|  | - Scope enforcement additions (scope_types)           |   |
|  | - Removed functions or classes                        |   |
|  | - New configuration options with different defaults   |   |
|  +-------------------------------------------------------+   |
|      |                                                       |
|      v                                                       |
|  Step 4: CHECK UPSTREAM RELEASE NOTES                        |
|  +-------------------------------------------------------+   |
|  | docs.openstack.org/releasenotes/nova/<release>        |   |
|  | docs.openstack.org/releasenotes/horizon/...           |   |
|  | Look for: deprecation notices, upgrade notes,         |   |
|  |           known issues, incompatible changes          |   |
|  +-------------------------------------------------------+   |
|                                                              |
+==============================================================+
```

### 3.3 Worked Example: Train to Wallaby Policy Split

The Nova `os-attach-interfaces` policy was split between Train and
Wallaby, illustrating a common upgrade regression pattern:

**Train -- single rule:**
```yaml
"os_compute_api:os-attach-interfaces": "rule:admin_or_owner"
```

**Wallaby -- split into four rules:**
```yaml
"os_compute_api:os-attach-interfaces:list":   "rule:project_reader_or_admin"
"os_compute_api:os-attach-interfaces:show":   "rule:project_reader_or_admin"
"os_compute_api:os-attach-interfaces:create": "rule:project_member_or_admin"
"os_compute_api:os-attach-interfaces:delete": "rule:project_member_or_admin"
```

The old rule name is aliased to `:list` via
[oslo.policy](https://docs.openstack.org/oslo.policy/latest/) deprecation
handling. Horizon's table action still references the old name, so the
button visibility check uses the `:list` rule while the actual API call
uses `:create`.

---

## 4. RBAC and oslo.policy Analysis

### 4.1 Scope Types (Critical Post-Upgrade)

OpenStack introduced `scope_types` in oslo.policy to enforce whether an
API operation requires system-scope or project-scope credentials:

```
OLD-STYLE POLICY (no scope enforcement):
+-------------------------------------------------------+
| "network:attach_interface": "rule:admin_or_owner"     |
| --> admin passes always, regardless of project scope  |
+-------------------------------------------------------+

NEW-STYLE POLICY (scope enforced):
+-------------------------------------------------------+
| "os_compute_api:os-attach-interfaces:create":         |
|     rule: "rule:project_member_or_admin"              |
|     scope_types: ["project"]                          |
| --> admin must be scoped to the correct project       |
+-------------------------------------------------------+
```

### 4.2 Key Configuration Settings

| Setting | Location | Default | Effect |
|---|---|---|---|
| `enforce_scope` | `/etc/<service>/<service>.conf [oslo_policy]` | False (most services) | When True, rejects tokens with wrong scope_type |
| `enforce_new_defaults` | `/etc/<service>/<service>.conf [oslo_policy]` | False (most services) | When True, uses new-style rules only |
| `policy_file` | `/etc/<service>/<service>.conf [oslo_policy]` | `policy.yaml` | Custom policy overrides |

### 4.3 Horizon's Own Policy Defaults

Horizon sets its own policy enforcement defaults at
[openstack_auth/policy.py](https://opendev.org/openstack/horizon/src/branch/master/openstack_auth/policy.py):

```python
policy_opts.set_defaults(conf,
                         enforce_scope=False,
                         enforce_new_defaults=False)
```

This means Horizon's CLIENT-SIDE policy checks are lenient. But the
BACKEND SERVICE (Nova, Neutron, etc.) may have different settings,
causing a mismatch:
- Horizon shows the button (client-side check passes)
- Backend rejects the API call (server-side check fails)

### 4.4 Investigation Steps for Policy Issues

1. Identify the policy rule name used by the Horizon action
   (look in `tables.py` for `policy_rules`)
2. Find the policy file for the backend service:
   - Nova: `/etc/nova/policy.yaml` or `/etc/nova/policy.d/`
   - Neutron: `/etc/neutron/policy.yaml`
   - Keystone: `/etc/keystone/policy.yaml`
   - Cinder: `/etc/cinder/policy.yaml`
3. Check `enforce_scope` and `enforce_new_defaults` in the service config
4. Compare the policy rule between old and new versions
5. Check the Horizon-bundled policy reference:
   [openstack_dashboard/conf/nova_policy.yaml](https://opendev.org/openstack/horizon/src/branch/master/openstack_dashboard/conf/nova_policy.yaml)
6. Look for deprecation notices in the policy file comments

---

## 5. Horizon-Specific Failure Patterns

### 5.1 Common Post-Upgrade Breakages

| Pattern | Symptom | Root Cause | Fix Direction |
|---|---|---|---|
| Missing dropdown options | "No networks available", empty select fields | Scoping filter added or changed in newer version | Check API call params in forms.py, compare `tenant_id` handling |
| "Not Authorized" on admin actions | Button visible but clicking it shows error | Policy scope_types enforcement enabled | Check policy.yaml + `enforce_scope` setting in service config |
| JavaScript errors in console | Panel fails to load, blank page, broken layout | Angular component removed in de-angularization | Check if panel was migrated from Angular to vanilla JS |
| "Unable to retrieve X" | Generic error message, partial data on page | SDK migration changed exception handling or API signature | Check api/*.py wrapper, look for neutronclient -> openstacksdk |
| Session expires unexpectedly | Redirect to login after short time | Token scope change or Fernet key rotation issue | Check Keystone token config, `TOKEN_TIMEOUT_MARGIN` in local_settings.py |
| Form validation error | Dialog opens but submission fails with form error | New required field added in newer version | Compare form class between old and new Horizon branches |

### 5.2 Error Message Translation

Horizon frequently hides the real error from the user:

```
+==============================================================+
|         HORIZON ERROR MESSAGE TRANSLATION                    |
+==============================================================+
|                                                              |
|  What the USER sees:          What ACTUALLY happened:        |
|  +------------------------+  +----------------------------+  |
|  | "An error occurred.    |  | Nova returned HTTP 403     |  |
|  |  Please try again      |  | Forbidden because the      |  |
|  |  later."               |  | user's project scope does  |  |
|  |                        |  | not match the VM's project |  |
|  +------------------------+  +----------------------------+  |
|                                                              |
|  What the USER sees:          What ACTUALLY happened:        |
|  +------------------------+  +----------------------------+  |
|  | "Unable to retrieve    |  | Neutron returned empty     |  |
|  |  networks."            |  | list because query was     |  |
|  |                        |  | filtered by admin project  |  |
|  |                        |  | which owns no networks     |  |
|  +------------------------+  +----------------------------+  |
|                                                              |
|  INVESTIGATION TIP:                                          |
|  Always check the backend service log, not just Horizon's    |
|  log. The real error is usually in Nova/Neutron/Keystone.    |
|                                                              |
+==============================================================+
```

### 5.3 De-Angularization Status

Horizon is actively migrating from AngularJS to vanilla JavaScript.
When investigating UI-rendering issues, determine whether the affected
panel was de-angularized between versions:

- **Angular panels (legacy)**: `static/dashboard/<panel>/<panel>.module.js`
- **Vanilla JS panels (new)**: Django template with minimal inline JS
- **Hybrid panels**: Some Angular components remaining alongside Django

Key de-angularization commits are tracked in the [Horizon Storyboard](https://storyboard.openstack.org/#!/project/openstack/horizon).

---

## 6. Must-Gather / SOSreport Analysis

### 6.1 Key Log Files

| Component | Log Path | What to Look For |
|---|---|---|
| Horizon | `/var/log/horizon/horizon.log` | Python stack traces, API errors, template rendering errors |
| Horizon (Apache) | `/var/log/httpd/horizon_error.log` | WSGI errors, mod_wsgi segfaults, SSL issues |
| Horizon (Apache access) | `/var/log/httpd/horizon_access.log` | HTTP status codes, slow requests, 4xx/5xx patterns |
| Keystone | `/var/log/keystone/keystone.log` | Auth failures, token validation errors, federation issues |
| Nova API | `/var/log/nova/nova-api.log` | Policy rejections (403), API errors, scope violations |
| Neutron | `/var/log/neutron/server.log` | Network API errors, RBAC failures, quota issues |
| Cinder | `/var/log/cinder/cinder-api.log` | Volume API errors, attachment failures |

### 6.2 Extracting Relevant Logs from SOSreport

```bash
# Unpack the SOSreport
tar xf sosreport-*.tar.xz
cd sosreport-*/

# Find all Horizon-related logs
find . -path "*/horizon*" -name "*.log"

# Search for error patterns in Horizon logs
grep -rn "ERROR\|CRITICAL\|Traceback" var/log/horizon/

# Search for policy rejections in Nova
grep -rn "Policy.*not authorized\|HTTP 403\|PolicyNotAuthorized" var/log/nova/

# Check installed Horizon packages
cat installed-rpms | grep -i "horizon\|openstack-dashboard"

# Check Horizon configuration
cat etc/openstack-dashboard/local_settings.py 2>/dev/null \
  || cat etc/openstack-dashboard/local_settings 2>/dev/null

# Check service policy files
cat etc/nova/policy.yaml 2>/dev/null
cat etc/neutron/policy.yaml 2>/dev/null

# Check for enforce_scope settings
grep -rn "enforce_scope\|enforce_new_defaults" etc/nova/ etc/neutron/ etc/keystone/
```

### 6.3 Must-Gather (OpenShift-based Deployments)

For OpenShift-based deployments (e.g. OpenStack 2023.2+), logs are collected differently:

```bash
# Extract must-gather archive
tar xf must-gather-*.tar.gz

# Find Horizon pod logs
find . -name "*horizon*" -o -name "*dashboard*"

# Check pod status
cat */cluster-scoped-resources/core/pods/*.yaml | grep -A5 "horizon"
```

---

## 7. Cross-Service Dependency Tracing

### 7.1 Horizon Service Dependencies

```
+==============================================================+
|                 HORIZON SERVICE DEPENDENCIES                 |
+==============================================================+
|                                                              |
|  Horizon (openstack-dashboard)                               |
|  +---+                                                       |
|      |                                                       |
|      +---> Keystone (ALWAYS -- authentication + catalog)     |
|      |     Every Horizon request validates a Keystone token. |
|      |     Service catalog determines available endpoints.   |
|      |                                                       |
|      +---> Nova (instances, flavors, keypairs, interfaces)   |
|      |     Project > Compute panel. Admin > Instances panel. |
|      |     attach_interface, detach_interface actions.       |
|      |                                                       |
|      +---> Neutron (networks, subnets, ports, routers, FIPs) |
|      |     Project > Network panel. Network dropdowns in     |
|      |     instance launch, attach-interface, floating IP.   |
|      |                                                       |
|      +---> Cinder (volumes, snapshots, backups)              |
|      |     Project > Volumes panel. Volume attach.           |
|      |                                                       |
|      +---> Glance (images, metadata definitions)             |
|      |     Project > Images panel. Image select in launch.   |
|      |                                                       |
|      +---> Heat (stacks, templates) [if enabled]             |
|      |     Project > Orchestration panel.                    |
|      |                                                       |
|      +---> Swift (containers, objects) [if enabled]          |
|            Project > Object Store panel.                     |
|                                                              |
+==============================================================+
```

### 7.2 Failure Propagation Patterns

When a backend service fails, Horizon shows different symptoms depending
on how the API abstraction layer handles the error:

| Backend Failure | Horizon Behavior | Where to Look |
|---|---|---|
| Service returns HTTP 403 | "Not authorized" or generic error | Check policy in backend service config |
| Service returns HTTP 404 | "Unable to retrieve [resource]" | Check if resource exists, endpoint URL correct |
| Service returns HTTP 500 | "Error: An error occurred" | Check backend service log for stack trace |
| Service is unreachable | Panel load timeout or blank panel | Check service endpoint in Keystone catalog |
| Service returns empty list | Dropdown has no options, table is empty | Check query filters (project_id scoping) |

### 7.3 Cross-Service Investigation Pattern

```
SYMPTOM: "Attach Interface fails in admin project"
    |
    +---> Check HORIZON code (where does the error appear?)
    |     tables.py -> forms.py -> utils.py -> api/neutron.py
    |
    +---> Check NEUTRON (is the network query returning results?)
    |     api.neutron.network_list_for_tenant(request, tenant_id)
    |     What tenant_id is being passed?
    |
    +---> Check NOVA (is the API call being rejected?)
    |     POST /servers/{id}/os-interface
    |     What policy rule is checked? What scope is the token?
    |
    +---> Check KEYSTONE (is the token valid and correctly scoped?)
          Is the admin user scoped to the correct project?
          Does the token have the right roles?
```

---

## 8. Investigation Output Format

Structure every investigation report using this template to ensure
consistency and completeness.

### 8.1 investigation_report.md Template

Every section below is REQUIRED unless marked (if applicable). Do not
skip sections or merge them. The checkpoints under each section are
mandatory items -- if a checkpoint does not apply, write "N/A" with a
one-line reason rather than omitting it.

```markdown
# Investigation Report: [Case Number or Identifier]

**Component:** [Primary OpenStack component]
**OpenStack Version:** [Version info, including upgrade path if applicable]
**Date:** [Investigation date]
**Classification:** [Category from Section 1 taxonomy, e.g. "Upgrade Regression + RBAC/Policy"]

## Symptom
[What was reported, in the reporter's words if available]

## Environment
- OpenStack version: [before and after if upgrade]
- Affected component: [Horizon, Nova, Neutron, etc.]
- Affected operation: [specific action that fails]
- Deployment type: [Director / OpenShift-based]

## Root Cause Analysis

For EACH contributing factor, include ALL of the following:

### Factor N: [Title]

**Checkpoint 1 -- Code reference:** Cite the specific file, function,
and line number. Include a code snippet showing the relevant code.
Link to upstream source on opendev.org.

**Checkpoint 2 -- Policy alignment:** For every Horizon action traced,
document:
- What policy rule does the Horizon button/action check? (tables.py
  policy_rules attribute)
- What policy rule does the backend service enforce? (server-side)
- Do they match? If not, explain the mismatch.

**Checkpoint 3 -- Authorization path:** For every API call in the
traced path, document:
- Does the Horizon API wrapper have a @policy_check decorator? (Yes/No)
- Is authorization enforced client-side, server-side, or both?
- What happens when the server rejects the call? (error message,
  HTTP status code, how Horizon surfaces it to the user)

**Checkpoint 4 -- Scope and filtering:** For API calls that query
lists (networks, ports, instances, etc.), document:
- What project/tenant ID is used to scope the query?
- Is it the current user's project or the target resource's project?
- What is excluded from the results? (external networks, other
  projects, etc.)

**Checkpoint 5 -- Asymmetry check:** Compare the affected action with
related sibling actions (e.g. AttachInterface vs DetachInterface,
Create vs Delete). Document whether siblings are correctly
implemented and whether the affected action is an outlier.

## Evidence
[Log excerpts, code diffs, policy comparisons]

Checkpoints:
- Each claim in Root Cause Analysis must have a corresponding
  evidence entry here
- Policy rules: show BEFORE and AFTER side by side (table format)
- Code: show the relevant snippet with file path and line number
- Upstream commits: list SHA, date, author, description for each
  relevant commit

## Version Comparison (if upgrade-related)
[Side-by-side comparison of relevant code/config between versions]

Checkpoints:
- List every file that changed between versions in the affected
  code path
- For each file: summarize what changed and whether it contributes
  to the reported symptom
- Note any files that did NOT change (to confirm pre-existing
  behavior vs regression)

## Severity Assessment
| Dimension | Rating | Rationale |
|---|---|---|
| Impact | [High/Medium/Low] | [Why] |
| Urgency | [High/Medium/Low] | [Why] |
| Scope | [Wide/Narrow] | [How many users/deployments affected] |
| Workaround | [Available/None] | [What it is] |

## Proposed Resolution
[Specific fix or workaround with step-by-step instructions]
[Include CLI commands where applicable]
[Note any risks or caveats]

Checkpoints:
- At least one immediate workaround (no code change required)
- At least one long-term fix (code or config change)
- Each resolution option must include verification steps
- "Always test in a non-production environment first" must appear

## Related Findings (if applicable)
[Issues discovered during investigation that are outside the
reported symptom scope. Note each one but do not investigate.]

## References
[Upstream bugs, commits, release notes, documentation links]
```

### 8.2 customer_response.md Template

```markdown
# Operator Response: [Case Number or Identifier]

## Summary
[1-2 sentence plain-language summary of the finding]

## What We Found
[Non-technical explanation of the root cause]
[Avoid internal jargon; write for the operator]

## Recommended Action
[Step-by-step instructions the operator can follow]
[Include exact commands if CLI is needed]

## What To Verify
[How the operator can confirm the fix worked]

## Additional Notes
[Any related considerations, future risks, or escalation paths]
```
