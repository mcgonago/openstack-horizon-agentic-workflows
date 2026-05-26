# Horizon — Project Knowledge for Code Review

This file is consumed by the AI agent during reviews. Every section is either a **rule to apply to a diff** or **context that changes how the diff should be interpreted**. If a section does not help evaluate a patch, it does not belong here.

---

## Project Links

- Repository: https://opendev.org/openstack/horizon (GitHub mirror: https://github.com/openstack/horizon)
- Bug tracker: https://bugs.launchpad.net/horizon
- Blueprints: https://blueprints.launchpad.net/horizon
- Code review: https://review.opendev.org (Gerrit only — GitHub PRs are not monitored)
- Contributor guide: https://docs.openstack.org/horizon/latest/contributor/
- Merge requirement: **two +2 votes** from Horizon core reviewers plus **Workflow+1**

---

## File Path → Check Mapping

When you see a path in a diff, this table tells you which checks apply:

| Path prefix | What it is | Primary checks |
|---|---|---|
| `horizon/` | Core framework imported by plugins | **Plugin-API stability — highest priority** |
| `openstack_dashboard/api/` | Service client wrappers | SDK migration, pagination, error handling, no mutation |
| `openstack_dashboard/dashboards/` | Views, forms, tables, templates | Context variable renames, UX consistency |
| `openstack_dashboard/static/app/` | Legacy AngularJS panels (being removed) | No new code here; CSRF handling still required for existing panels |
| `openstack_dashboard/defaults.py` | Default values for all settings | New settings must land here with a default |
| `openstack_dashboard/local/` | Local config examples | Never ship secrets; document new settings |
| `openstack_auth/` | Auth middleware | Security-sensitive — extra scrutiny |
| `releasenotes/notes/` | reno release notes | Required for features, security fixes, behavior changes |
| `.zuul.d/` | CI pipeline config | Voting status changes affect gating |

---

## Plugin API Stability (Highest Priority Check)

Any diff touching `horizon/` is potentially breaking for plugin projects. Plugins (Octavia UI, Designate UI, Magnum UI, Heat Dashboard, Manila UI, Ironic UI, etc.) subclass and import directly from `horizon/`.

**BLOCKER — flag if the diff:**
- Removes or renames any public class: `DataTable`, `Action`, `LinkAction`, `BatchAction`, `DeleteAction`, `SelfHandlingForm`, `Workflow`, `Step`, `TabGroup`, `Tab`, `GenericView`, `ModalFormView`, `MultiTableView`, `ModalFormMixin`, `WorkflowView`, `Dashboard`, `Panel`, `PanelGroup`
- Changes a method signature in a non-backward-compatible way on those classes (adds required parameter, removes parameter, changes return type)
- Renames or moves a module under `horizon/` that plugins import
- Renames a URL `name=` argument in `horizon/` that plugins may `reverse()`
- Changes `horizon/templatetags/` in a way that breaks template tags plugin templates use

**Safe — no plugin concern if the diff:**
- Only touches `openstack_dashboard/` (not `horizon/`)
- Adds a new optional parameter with a default value to an existing method
- Adds a new method without removing an existing one

**How plugins register themselves** (context for judging registration-related changes):
```python
# In plugin's enabled file (e.g. _31000_myplugin.py):
PANEL = 'mypanel'
PANEL_DASHBOARD = 'identity'
ADD_PANEL = 'myplugin.content.mypanel.panel.MyPanel'
ADD_INSTALLED_APPS = ['myplugin']
ADD_ANGULAR_MODULES = ['horizon.dashboard.identity.myplugin.mypanel']  # legacy Angular only
ADD_JS_FILES = [...]   # legacy Angular only
ADD_SCSS_FILES = [...]
```
Any change to how `horizon.register()`, `Dashboard.register()`, or `Panel.can_register()` behaves can break all plugins.

---

## Active Codebase Direction — Context for Evaluating Diffs

### De-angularization (Major Ongoing Project — Topic: `de-angularize`)

**What it is:** AngularJS 1.x has been end-of-life since December 2021. Horizon is panel-by-panel migrating all Angular-based panels to native Django class-based views + `DataTable`. All changes use the Gerrit topic `de-angularize`. This is a project priority — migration patches should be encouraged and not held up on minor style points.

**Which panels still use Angular** is tracked by `ANGULAR_FEATURES` in `defaults.py` — any panel with `True` is still Angular and a migration candidate. When `ANGULAR_FEATURES['foo_panel']` flips from `True` → `False` in a diff, that is a **migration completion** — a positive signal.

**New Angular code is not acceptable.** Flag as a blocker any patch that:
- Adds a new Angular controller / service / directive
- Adds a new `openstack_dashboard/api/rest/` endpoint (these only exist to serve Angular)
- Adds `ADD_ANGULAR_MODULES` to an enabled file
- Adds a new `.spec.js` Karma test (except when fixing existing Angular tests before migration)

**What a correct migration patch looks like:**

```
# Files ADDED (Django replacement):
openstack_dashboard/dashboards/<panel>/views.py       ← class-based views
openstack_dashboard/dashboards/<panel>/forms.py       ← SelfHandlingForm subclasses
openstack_dashboard/dashboards/<panel>/tables.py      ← DataTable + Actions
openstack_dashboard/dashboards/<panel>/urls.py
openstack_dashboard/dashboards/<panel>/templates/     ← extend base.html
openstack_dashboard/dashboards/<panel>/tests.py

# Files REMOVED (Angular cleanup):
openstack_dashboard/static/app/<panel>/*.module.js
openstack_dashboard/static/app/<panel>/*.controller.js
openstack_dashboard/static/app/<panel>/*.spec.js
openstack_dashboard/api/rest/<service>.py             ← only if no other Angular panel uses it
```

**What to flag in migration patches:**
1. `ADD_ANGULAR_MODULES` / `ADD_JS_FILES` / `ADD_SCSS_FILES` still present in enabled file after migration
2. Angular REST endpoint left in `api/rest/` with no remaining Angular callers — should be deleted
3. Old `.spec.js` Karma test files left orphaned
4. `ANGULAR_FEATURES` default not flipped to `False` after full panel migration
5. `REST_API_REQUIRED_SETTINGS` entries only needed by the removed Angular panel — should be removed

### SDK Migration (neutronclient → openstack SDK)

Horizon is replacing all individual Python service clients with the unified OpenStack SDK (`openstack` / `openstacksdk`). The `neutron.py` migration is mostly complete; `nova.py` and `cinder.py` are in progress. Track: LP bug 1999774.

**Flag as suggestion (new code) or blocker (if it adds NEW client calls):**
- New `from neutronclient...` imports in `openstack_dashboard/api/`
- New `neutronclient(request)` calls where an SDK equivalent exists
- New code in `nova.py` or `cinder.py` using the legacy clients rather than SDK

**Critical SDK object pitfall — flag this pattern anywhere in the diff:**
```python
# WRONG: looks like a dict, but is NOT
port = sdk_client.get_port(port_id)
port['custom_key'] = value          # assignment works silently
'custom_key' in port                # Returns False — the key is invisible to 'in'
json.dumps(dict(port))              # Drops 'custom_key' — data silently lost

# CORRECT: use a plain separate dict for any data not in the SDK schema
extra = {port.id: {'custom_key': value}}
```
This is a real bug class introduced during the `neutron.py` migration. Any code that assigns custom attributes to SDK objects and then tests membership (`in`) or serialises them is broken.

### Django 5.2 Compatibility

Django 5.2 is now a voting job. Django 5.x enforces POST-only logout.

**Flag as BLOCKER:**
- `<a href="...logout...">` links — these send GET and get HTTP 405 under Django 5.2. Must be a POST form with CSRF token.
- `redirect(settings.LOGOUT_URL)` from a GET handler — same problem.
- Any `HttpResponseRedirect` to a logout URL from a non-POST handler.

**Correct pattern:**
```python
# Wrong: redirects to LOGOUT_URL as GET
return redirect(settings.LOGOUT_URL)

# Correct: server-side logout + redirect to login
from django.contrib.auth import logout as auth_logout
auth_logout(request)
return redirect(settings.LOGIN_URL)
```
Django 5.x also requires `{% csrf_token %}` in all POST forms. New forms missing it will fail with 403 in hardened deployments.

### Python Version Support

Supported: 3.10, 3.11, 3.12, 3.13. Non-voting/in-progress: 3.14. Dropped: 3.9 (2025).
Flag any new code requiring Python < 3.10 compatibility accommodations as unnecessary.

---

## API Layer Rules (`openstack_dashboard/api/`)

| Rule | What to look for | Severity |
|---|---|---|
| `request` first | Every public function must take `request` as first arg | Blocker |
| No raw client outside `api/` | `novaclient()`, `neutronclient()` etc. must not appear in views, forms, or templates | Blocker |
| No unlimited `.list()` | `.list()` with no limit/marker on collections that can be large (ports, servers, images) | Blocker |
| Proper error handling | Client exceptions caught with `horizon.exceptions.handle(request, ...)` for user-facing errors | Blocker |
| No in-place mutation | Service catalog and session objects must not be modified directly — always `copy.deepcopy()` first | Blocker |
| `project_id` filter on port lists | Port lists in non-admin context must pass `project_id=request.user.tenant_id` | Suggestion |
| No unnecessary API calls | Don't fetch data the UI doesn't display (e.g. flavor extra specs, full port details when only ID is needed) | Suggestion |
| SDK preferred | New code should use `openstack` SDK, not `neutronclient`/`novaclient` | Suggestion |
| Nova microversions | Feature-gated Nova API calls must pass `microversion=N` explicitly | Blocker |

**Don't mutate service catalog:**
```python
# WRONG — mutations persist across requests (catalog is session-cached)
request.user.service_catalog['something'] = modified

# CORRECT
import copy
catalog = copy.deepcopy(request.user.service_catalog)
catalog['something'] = modified
```

---

## Testing Rules

| Situation | Requirement | Severity |
|---|---|---|
| Bug fix | Unit test that fails without the fix | Blocker |
| New view | Unit test covering success + error paths | Blocker |
| New form | Unit test calling `assertNoFormErrors()` on valid POST | Blocker |
| New `api/` function | Unit test with mocked client at the API boundary | Blocker |
| Existing Angular JS file modified | `.spec.js` Karma test updated | Suggestion |
| New JS file (any) | New `.spec.js` alongside it | Suggestion |

**Mocking conventions:**
- Mock at `openstack_dashboard.api.{service}.{function}` — not the underlying raw client
- Reuse fixtures from `openstack_dashboard/test/test_data/` — do not create parallel fixture sets
- `IsHttpRequest()` and `IsA()` matchers from `openstack_dashboard.test.helpers`
- `assertNoFormErrors(response)` after every form POST test
- `assertMessageCount(response, N)` and `assertNoMessages(response)` for checking alert messages

**Integration test selector rule** — flag when new row actions are added to a table that had only one action before:
```python
# WRONG after adding a second action (will click wrong action)
row.find_element(By.CSS_SELECTOR, "td.actions_column").click()

# CORRECT — selects action by visible name
actions_col = row.find_element(By.CSS_SELECTOR, "td.actions_column")
widgets.select_from_dropdown(actions_col, "Delete Rule")
```

---

## AngularJS/Django Migration — Detailed Code Checklist

See the "De-angularization" section above for project context and what files to expect removed/added. When reviewing the code in a migration diff, additionally check:

1. **API call kwargs**: `api.glance.image_update_properties(request, image_id, **data)` not `(request, image_id, data)` — passing a dict as positional arg is a silent no-op
2. **Regex character class**: `-` must be last inside `[...]` or escaped: `[A-Za-z0-9 \-]` ✓, `[A-Za-z0-9 -]` with `-` not last ✗
3. **Post-creation table refresh**: after resource creation + file download (e.g. keypair), the table must refresh without manual reload — use a redirect after POST
4. **No debug leftovers**: no `console.log()`, no unused template files, no duplicate buttons from debugging sessions
5. **UX parity**: boolean metadata → checkbox (not "True"/"False" text); read-only image properties (`os_hash_algo`, `os_hash_value`, `os_hidden`, defined in `IMAGE_RO_PROPERTIES`) must not be editable
6. **Chevron labels**: don't repeat resource type — "Name" not "Key Pair Name" under a Key Pair row
7. **Scope**: unrelated test fixes or form changes must go in a separate patch — reviewers will ask

---

## CSRF in AngularJS Templates

Applies to the two remaining Angular panels (Images, Roles) until they are fully migrated. AngularJS panels make AJAX POST/PUT/DELETE requests via `$http`. Check:
- The Angular CSRF interceptor (`X-CSRFToken` header injection) is in place — it is set up globally in `app.module.js` via `$http.defaults.headers.common['X-CSRFToken']`
- Templates that introduce new POST actions use `{% csrf_token %}` or rely on that interceptor
- Deployments with `CSRF_COOKIE_HTTPONLY=True` + `SESSION_COOKIE_SECURE=True` will produce silent 403s if CSRF is missing — this is a production failure that does not appear in CI

---

## Settings — How to Evaluate in a Diff

**Adding a new setting — full checklist:**
1. Default value in `openstack_dashboard/defaults.py` (not only in `settings.py`)
2. Documentation in `doc/source/configuration/settings.rst`
3. Example in `openstack_dashboard/local/local_settings.py.example`
4. If an AngularJS panel reads it: must be added to `REST_API_REQUIRED_SETTINGS` in `defaults.py`

The authoritative defaults (from `defaults.py`) are:
```python
ANGULAR_FEATURES = {
    # key_pairs_panel migration is DONE (see de-angularize section) — default lags behind in tree
    'images_panel': True, 'key_pairs_panel': True, 'flavors_panel': False,
    'domains_panel': False, 'users_panel': False, 'groups_panel': False, 'roles_panel': True
}
OPENSTACK_NEUTRON_NETWORK = {
    'enable_router': True, 'enable_ipv6': True, 'enable_quotas': True,
    'enable_rbac_policy': True, 'enable_distributed_router': False,
    'enable_ha_router': False, 'enable_fip_topology_check': True,
    'enable_auto_allocated_network': False, 'show_agents_column': True,
    'supported_provider_types': ['*'], 'supported_vnic_types': ['*'],
    'segmentation_id_range': {}, 'extra_provider_types': {},
    'default_dns_nameservers': [], 'physical_networks': [],
}
OPENSTACK_HYPERVISOR_FEATURES = {
    'can_set_mount_point': False, 'can_set_password': False,
    'enable_quotas': True, 'requires_keypair': False,
}
LAUNCH_INSTANCE_DEFAULTS = {
    'config_drive': False, 'create_volume': True, 'hide_create_volume': False,
    'disable_image': False, 'disable_instance_snapshot': False,
    'disable_volume': False, 'disable_volume_snapshot': False,
    'enable_scheduler_hints': True, 'enable_metadata': True,
    'enable_net_ports': True, 'default_availability_zone': 'Any',
}
OPENSTACK_CINDER_FEATURES = {'enable_backup': False}
OPENSTACK_API_VERSIONS = {"identity": 3, "image": 2, "volume": 3, "compute": 2}
REST_API_REQUIRED_SETTINGS = [
    'CREATE_IMAGE_DEFAULTS', 'DEFAULT_BOOT_SOURCE', 'ENFORCE_PASSWORD_CHECK',
    'LAUNCH_INSTANCE_DEFAULTS', 'OPENSTACK_HYPERVISOR_FEATURES',
    'OPENSTACK_IMAGE_FORMATS', 'OPENSTACK_KEYSTONE_BACKEND',
    'OPENSTACK_KEYSTONE_DEFAULT_DOMAIN',
]
```

**Security-sensitive settings — flag any diff that weakens these defaults:**

| Setting | Default | Flag if changed to... |
|---|---|---|
| `DISALLOW_IFRAME_EMBED` | `True` | `False` — removes clickjacking protection |
| `OPENSTACK_SSL_NO_VERIFY` | `False` | `True` — disables SSL certificate checks |
| `OPENSTACK_KEYSTONE_DOMAIN_DROPDOWN` | `False` | `True` in a public cloud context — exposes domain list to unauthenticated users |
| `DEBUG` | `True` (dev default) | Must be `False` in production; flag if a diff sets it `True` in non-test config |
| `TOKEN_DELETION_DISABLED` | `False` | `True` — tokens survive logout, security risk |
| `POLICY_CHECK_FUNCTION` | `'openstack_auth.policy.check'` | `None` — bypasses all policy checks |
| `OPERATION_LOG_OPTIONS['mask_fields']` | includes `'password'` | Removing `password` fields from masking |

**Performance-relevant settings** (flag new API code that ignores these):

| Setting | Default | What new code should respect |
|---|---|---|
| `OPENSTACK_INSTANCE_RETRIEVE_IP_ADDRESSES` | `True` | New instance list code fetching Neutron ports should be guarded by this |
| `OPENSTACK_USE_SIMPLE_TENANT_USAGE` | `True` | New usage overview code should check this before calling SimpleTenantUsage |
| `FILTER_DATA_FIRST` | all `False` | New large admin panel lists should check this before auto-loading all objects |
| `SWIFT_PANEL_FULL_LISTING` | `True` | New Swift panel list code should respect this (full listing is expensive) |
| `API_RESULT_LIMIT` | `1000` | Max objects per Swift/Glance page; new paging code should use this |
| `API_RESULT_PAGE_SIZE` | `20` | Items per page for server-side paginated APIs |
| `OVERVIEW_DAYS_RANGE` | `1` | New overview queries should not ignore this — `None` means full month (very slow) |
| `DROPDOWN_MAX_ITEMS` | `30` | Dropdowns should not load more than this many items without search/filtering |
| `MEMOIZED_MAX_SIZE_DEFAULT` | `25` (horizon default) | New `@memoized` usage; cache size should be at least 2× expected thread count |

---

## Commit Message and Release Note Rules

**Commit message:**
- Subject ≤ 72 characters; body explains the **why**
- Must be specific: "Fix snapshots not visible in Volumes in **Admin** tab" — if a bug only affects Admin context, say so (it works correctly in Project view)
- Bug fix: `Closes-Bug: #NNNNNN` or `Related-Bug: #NNNNNN`
- Feature: `Implements: blueprint {slug}`

**Release note required for:**
- New features or removed features
- Configuration options added, changed, or deprecated
- Security fixes (also: CVE hashtag added to Gerrit change after merge)
- Behavior changes operators need to know about
- Upgrade-impacting changes

**Release note NOT required for:**
- Bug fix with no user-visible behavior change
- Internal refactor
- Test-only changes, doc-only changes

Release note wording is reviewed inline. The `fixes:` section describes user-facing impact, not internal code changes. The `upgrade:` section goes in release notes for operator-facing changes.

---

## `@memoized` Decorator Rule

`horizon/utils/memoized.py` provides `@memoized`. The decorator must **not** silently catch `TypeError`. If a diff introduces code that catches `TypeError` in or around a memoized call and treats it as a cache miss, flag it — this hides genuine bugs (wrong argument types, attribute access on `None`).

---

## What CI Already Enforces — Do Not Re-flag

| What | How CI catches it |
|---|---|
| PEP8, flake8, import ordering | `tox -e pep8` (via pre-commit) |
| Horizon-specific hacking check M322 (mutable default args) | `tox -e pep8` |
| JavaScript lint | `horizon-nodejs20-run-lint` job |
| JavaScript unit tests | `horizon-nodejs20-run-test` job |
| Django 4.2 / 5.2 compatibility | `horizon-tox-python3-django42/52` jobs |
| Python unit tests | `openstack-tox-py311/313` jobs |
| Security static analysis (bandit) | `horizon-tox-bandit-baseline` job |
| Documentation build | `openstack-tox-docs` job |

Only raise a comment about one of these if you see a **logic error** that passes automated checks but is semantically wrong. Do not comment on code style.
