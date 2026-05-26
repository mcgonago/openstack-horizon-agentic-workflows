# Horizon — Project Reference

Horizon is OpenStack's official web-based dashboard. It is a Django application that provides a GUI for interacting with OpenStack services (Nova, Neutron, Cinder, Keystone, Glance, Swift, etc.).

## Project Links

- **Repository**: https://opendev.org/openstack/horizon (GitHub mirror: https://github.com/openstack/horizon)
- **Bug tracking**: https://bugs.launchpad.net/horizon
- **Code review**: Gerrit at https://review.opendev.org (not GitHub PRs — GitHub PRs are not monitored)
- **Docs**: https://docs.openstack.org/horizon/latest/
- **Contributor guide**: https://docs.openstack.org/horizon/latest/contributor/
- **Blueprints**: https://blueprints.launchpad.net/horizon
- **IRC**: `#openstack-horizon` on OFTC
- **Mailing list**: `openstack-discuss` with `[horizon]` tag

## Architecture Overview

```
horizon/                        # Core framework (reusable by plugins)
├── base.py                     # Base views, Horizon registry
├── tables/                     # DataTable framework
├── tabs/                       # TabGroup/Tab framework
├── forms/                      # SelfHandlingForm framework
├── workflows/                  # Workflow/Step framework
└── templatetags/               # Custom Django template tags

openstack_dashboard/            # The actual OpenStack dashboard
├── api/                        # REST API client wrappers (one module per service)
│   ├── nova.py                 # Nova client calls
│   ├── neutron.py              # Neutron client calls
│   ├── cinder.py               # Cinder client calls
│   ├── keystone.py             # Keystone client calls
│   └── ...
├── dashboards/                 # Dashboard panels
│   ├── admin/                  # Admin panel group
│   ├── project/                # Project panel group
│   └── identity/               # Identity panel group
├── contrib/                    # Optional/contrib panels
└── test/                       # Test infrastructure

openstack_auth/                 # Authentication middleware (Django auth backend)
```

## Plugin System

Horizon's plugin system is critical. Third-party projects (Octavia, Designate, Magnum, Sahara, etc.) ship dashboards as Django apps that plug into Horizon.

**Plugin-breaking changes are blockers.** These include:
- Removing or renaming public classes in `horizon/` (DataTable, SelfHandlingForm, Workflow, TabGroup, etc.)
- Changing method signatures on public base classes that plugins subclass
- Changing how panels register themselves (`horizon.register()`)
- Renaming URL names that plugins may `reverse()`
- Changing context variable names that plugin templates use

**How to identify public API**: anything in `horizon/` that a plugin is likely to import or subclass is public. When in doubt, check if it is imported from `horizon` (not `openstack_dashboard`) in the existing codebase.

## OpenStack Client API Layer (`openstack_dashboard/api/`)

Each module wraps a Python client library (novaclient, neutronclient, cinderclient, etc.). Conventions to watch for:
- Functions should accept `request` as first argument and extract the client via helpers like `novaclient(request)`
- Avoid exposing raw client objects outside the `api/` layer
- Pagination: use `nova.server_list_paged()` patterns; do not load all objects blindly
- Error handling: wrap client exceptions in user-facing messages; never let raw API exceptions bubble to templates

## Deterministic Checks (CI enforces — do NOT re-check manually)

| Check | Command |
|---|---|
| Python style (PEP8 + hacking) | `tox -e pep8` |
| Python unit tests | `tox -e py3` |
| JavaScript lint | `npm run lint` |
| JavaScript unit tests | `npm run test` |
| Django compatibility | CI jobs `horizon-tox-python3-djangoXXX` |

Do **not** manually re-check import ordering, flake8 errors, or anything a linter catches automatically.

## Conventions Requiring Human Judgement

These CI cannot fully enforce — reviewers must watch for them:

- **Plugin API stability**: changes to `horizon/` public classes that third-party plugins subclass
- **Correct API client usage**: using the right client functions, proper pagination, correct error handling
- **UX consistency**: new UI patterns should match existing Horizon design conventions; new actions/buttons should follow the table action model
- **Template context**: context variable names passed from views to templates are not statically checked — renaming one breaks templates silently
- **AngularJS module registration**: new Angular modules must be registered in the correct `static/app/` structure and added to the module registry
- **Test quality**: coverage of important branches, proper use of `test_data` fixtures, `assertNoFormErrors()` after form POSTs

## Testing Requirements

- **Every bug fix must have a regression test** (Python unit test at minimum)
- **New features must have unit tests** for all new views, forms, tables, and API wrappers
- **JavaScript changes**: if JS is added or modified, a corresponding Jasmine test (`.spec.js`) is expected
- **Integration tests** (`tox -e integration`) are Selenium-based and catch browser-level regressions; not always required but appreciated for complex UI changes
- Horizon uses `horizon/test/helpers.py` helpers; use `assertNoFormErrors()`, `assertMessageCount()`, `assertNoMessages()` appropriately

## Blueprint and Bug Process

- **Bug fixes**: file a Launchpad bug first, reference with `Closes-Bug: #NNNNNN` or `Related-Bug: #NNNNNN` in commit message
- **Features**: file a blueprint at https://blueprints.launchpad.net/horizon — lightweight, no separate specs repo. Reference with `Implements: blueprint {name}` in commit message. No feature freeze after milestone 3.
- Features do **not** require a formal spec document (unlike Nova) — a blueprint description is enough
- No major governance gate before proposing feature code

## Commit Conventions

- Horizon uses **Gerrit**, not GitHub PRs
- Commit message should have a short subject line (≤72 chars) and a body explaining the why
- Tags: `Closes-Bug: #NNNNNN`, `Related-Bug: #NNNNNN`, `Implements: blueprint {slug}`, `Partial-Bug: #NNNNNN`
- Release notes: use `reno` for user-visible changes, deprecations, security fixes, and upgrade notes
  - Create with: `reno new {slug}` in the Horizon repo
  - Not required for trivial fixes or internal refactors

## Merge Requirements

- **Two +2 votes** from Horizon core reviewers
- **Workflow+1** from a core reviewer to trigger merge
- CI must be green (Zuul gate jobs)
- Core team list: https://review.opendev.org/admin/groups/horizon-core

## Release Notes (`reno`)

Changes that need a release note:
- New features or feature removals
- Deprecations (Python API or configuration)
- Security fixes
- Changes affecting operators (config options, behavior changes)
- Upgrade-impacting changes

Changes that do NOT need a release note:
- Pure bug fixes with no user-visible behavior change
- Internal refactors
- Test-only changes
- Documentation-only changes
