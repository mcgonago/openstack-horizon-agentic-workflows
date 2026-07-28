# Triage Assessment: OSPRH-31340

**Ticket:** [OSPRH-31340](https://redhat.atlassian.net/browse/OSPRH-31340)
**Parent:** [RHOSSTRAT-1354](https://redhat.atlassian.net/browse/RHOSSTRAT-1354) — Remove angular.js from Images view in Horizon UI
**Gerrit Topic:** [de-angularize](https://review.opendev.org/q/topic:de-angularize+project:openstack/horizon)

---

## Ticket Summary

| Field | Value |
|-------|-------|
| Key | [OSPRH-31340](https://redhat.atlassian.net/browse/OSPRH-31340) |
| Type | Epic |
| Status | In Progress |
| Priority | Undefined |
| Component | python-django-horizon |
| Assignee | Radomir Dopieralski |
| Reporter | Radomir Dopieralski |
| Team | rhos-dfg-ui / rhos-ops-platform-services-ui |
| Created | 2026-06-16 |
| Updated | 2026-06-16 |
| Fix Versions | (none) |
| Labels | (none) |
| Parent | [RHOSSTRAT-1354](https://redhat.atlassian.net/browse/RHOSSTRAT-1354) (Initiative, In Progress) |

---

## Epic Progress Summary

| Metric | Value |
|--------|-------|
| Total Children | 10 |
| Closed / Done | 4 (40%) |
| In Progress | 2 |
| Backlog / To Do | 4 |
| Blocked | 0 |
| With Active Gerrit Reviews | 2 |
| Gerrit Reviews Merged | 3 |

---

## Epic Children Status

| Key | Summary | Type | Status | Assignee | Created | Updated | Review | Review Status |
|-----|---------|------|--------|----------|---------|---------|--------|---------------|
| [OSPRH-14464](https://redhat.atlassian.net/browse/OSPRH-14464) | Identify all differences between Angular and Python for the Images panel | Spike | Closed | Radomir Dopieralski | 2025-03-04 | 2026-06-16 | — | — |
| [OSPRH-16421](https://redhat.atlassian.net/browse/OSPRH-16421) | Add chevrons to the Images table | Task | Closed | Owen McGonagle | 2025-05-06 | 2026-06-16 | [982600](https://review.opendev.org/c/openstack/horizon/+/982600) | **Merged** |
| [OSPRH-16422](https://redhat.atlassian.net/browse/OSPRH-16422) | Update filtering in the Images table | Task | In Progress | Owen McGonagle | 2025-05-06 | 2026-07-16 | [986478](https://review.opendev.org/c/openstack/horizon/+/986478) | Under Review |
| [OSPRH-16423](https://redhat.atlassian.net/browse/OSPRH-16423) | Add missing fields to the Image Create/Edit form | Task | Backlog | Unassigned | 2025-05-06 | 2026-06-16 | — | — |
| [OSPRH-16424](https://redhat.atlassian.net/browse/OSPRH-16424) | Update visibility settings in the Image Create/Edit form | Task | Backlog | Unassigned | 2025-05-06 | 2026-06-16 | — | — |
| [OSPRH-16425](https://redhat.atlassian.net/browse/OSPRH-16425) | Add image metadata to the Image Create/Edit form | Task | Closed | Radomir Dopieralski | 2025-05-06 | 2026-06-16 | [969791](https://review.opendev.org/c/openstack/horizon/+/969791) | **Merged** |
| [OSPRH-16426](https://redhat.atlassian.net/browse/OSPRH-16426) | Add activate/deactivate actions to the Images view | Task | In Progress | Owen McGonagle | 2025-05-06 | 2026-07-13 | [986458](https://review.opendev.org/c/openstack/horizon/+/986458) | Needs Revision |
| [OSPRH-26419](https://redhat.atlassian.net/browse/OSPRH-26419) | Add filtering to the image metadata form | Task | Backlog | Radomir Dopieralski | 2026-02-10 | 2026-07-13 | — | — |
| [OSPRH-26420](https://redhat.atlassian.net/browse/OSPRH-26420) | Add support for enum and bool type fields to image metadata | Task | Backlog | Unassigned | 2026-02-10 | 2026-06-16 | — | — |
| [OSPRH-26421](https://redhat.atlassian.net/browse/OSPRH-26421) | Write separated UI tests for the image metadata form | Task | Closed | Radomir Dopieralski | 2026-02-10 | 2026-07-10 | [980459](https://review.opendev.org/c/openstack/horizon/+/980459) | **Merged** |

---

## Unlinked Reviews (topic: de-angularize)

These Gerrit reviews match the epic's topic but do not reference any child ticket key in their commit message:

| Review | Subject | Status | Author |
|--------|---------|--------|--------|
| [992675](https://review.opendev.org/c/openstack/horizon/+/992675) | Switch default Images panel from AngularJS to Python | WIP (CI Failing) | Owen McGonagle |

**Note:** Review [992675](https://review.opendev.org/c/openstack/horizon/+/992675) is the **actual switchover patch** that flips `ANGULAR_FEATURES['images_panel']` from `True` to `False`. It has Workflow-1 and Verified-1 (set to WIP by Tatiana Ovchinnikova on 2026-07-03). This review has no corresponding child ticket in the epic — recommend creating one to track the final switchover step.

---

## Technical Context

This epic is part of the broader **de-angularization** effort in Horizon (from horizon.md). AngularJS 1.x reached end-of-life in December 2021, and Horizon is migrating all Angular-based panels to native Django class-based views with `DataTable`. The Images panel is one of only two panels still running Angular (the other being Roles).

The work follows a well-established pattern:
1. Audit feature parity between Angular and Python versions (OSPRH-14464, done)
2. Implement missing features in the Python version (chevrons, filtering, forms, actions)
3. Flip the `ANGULAR_FEATURES['images_panel']` default from `True` to `False`
4. Clean up Angular code, REST endpoints, and `.spec.js` tests

A successful precedent exists: the Key Pairs panel switchover ([992714](https://review.opendev.org/c/openstack/horizon/+/992714)) merged on 2026-07-14 using the exact same pattern.

---

## Dependencies & Blockers

| Dependency | Assignee | Team | Status | Notes |
|-----------|----------|------|--------|-------|
| Feature parity audit | Radomir Dopieralski | rhos-dfg-ui | Done | OSPRH-14464, closed |
| Chevrons | Owen McGonagle | rhos-dfg-ui | Done | Review 982600 merged |
| Image metadata form | Radomir Dopieralski | rhos-dfg-ui | Done | Review 969791 merged |
| Image metadata UI tests | Radomir Dopieralski | rhos-dfg-ui | Done | Review 980459 merged |
| Filtering update | Owen McGonagle | rhos-dfg-ui | In Review | Review 986478, ps5, no votes yet |
| Activate/deactivate actions | Owen McGonagle | rhos-dfg-ui | Needs Revision | Review 986458, ps6, has CR-1 |
| Missing form fields (Kernel/Ramdisk) | Unassigned | rhos-dfg-ui | Backlog | OSPRH-16423, unassigned |
| Visibility settings | Unassigned | rhos-dfg-ui | Backlog | OSPRH-16424, unassigned |
| Metadata form filtering | Radomir Dopieralski | rhos-dfg-ui | Backlog | OSPRH-26419 |
| Metadata enum/bool fields | Unassigned | rhos-dfg-ui | Backlog | OSPRH-26420, unassigned |
| Final switchover | Owen McGonagle | rhos-dfg-ui | WIP | Review 992675, CI failing, no child ticket |

No cross-team or external dependencies identified. The entire effort is within the rhos-dfg-ui team and the upstream Horizon project.

---

## Impact Analysis

**If we proceed (IMPLEMENT):**
- Removes the last major Angular dependency from the Images panel, bringing Horizon closer to full de-angularization
- Eliminates security risk of running EOL JavaScript framework (AngularJS 1.x)
- Simplifies the codebase — Angular REST endpoints in `api/rest/glance.py` can be removed
- Enables future removal of the Angular build pipeline entirely (once Roles panel is also migrated)
- Follows proven pattern (Key Pairs switchover already merged)

**If we close or defer:**
- AngularJS security risk persists in the Images panel
- Increases technical debt; Angular-specific CI jobs must continue running
- Blocks full removal of the Angular build pipeline
- The 40% completed work (4 merged patches, 2 in-review) would be wasted

---

## Recommendation

| Dimension | Assessment |
|-----------|-----------|
| Verdict | **IMPLEMENT** |
| Confidence | High |
| Rationale | Clear path to completion, no blockers, precedent exists (Key Pairs), 40% already done |

### Rationale

Assessment indicates this epic should continue. The work is well-decomposed, 40% complete, and follows a proven migration pattern. The remaining 6 items are clearly scoped. Two are already in review, and four backlog items are straightforward feature-parity additions (form fields, visibility settings, metadata enhancements).

**Key actions recommended:**
1. Resolve the CR-1 on review [986458](https://review.opendev.org/c/openstack/horizon/+/986458) (activate/deactivate) — this is blocking progress
2. Get reviewers on [986478](https://review.opendev.org/c/openstack/horizon/+/986478) (filtering) — it has no CR votes yet
3. Assign the 3 unassigned backlog items ([OSPRH-16423](https://redhat.atlassian.net/browse/OSPRH-16423), [OSPRH-16424](https://redhat.atlassian.net/browse/OSPRH-16424), [OSPRH-26420](https://redhat.atlassian.net/browse/OSPRH-26420))
4. Create a child ticket for the final switchover step (currently only tracked as WIP review [992675](https://review.opendev.org/c/openstack/horizon/+/992675))
5. Fix CI on the switchover patch once prerequisites are met

---

## Talking Points

- The Images panel de-angularization is 40% complete (4 of 10 children done) with 3 upstream patches already merged
- The Key Pairs panel switchover merged on 2026-07-14 using the same pattern — strong precedent
- Two active reviews need attention: one needs revision (CR-1), one needs reviewers
- Four backlog items remain, three of which are unassigned — recommend sprint planning to assign
- The final switchover patch exists (WIP) but needs a child ticket for proper tracking
- No cross-team dependencies — this is entirely within rhos-dfg-ui scope
- Completing this removes one of the last two Angular panels in Horizon (Images and Roles)

---

## Deep Analysis

### Code Paths Affected

| Path | Role | Migration Impact |
|------|------|-----------------|
| `openstack_dashboard/dashboards/project/images/` | Django views (replacement) | New/modified views, forms, tables |
| `openstack_dashboard/static/app/core/images/` | Angular controllers (deprecated) | To be removed after switchover |
| `openstack_dashboard/api/glance.py` | Glance API layer | Shared by both Angular and Python; no changes expected |
| `openstack_dashboard/api/rest/glance.py` | REST API for Angular | Candidate for removal after switchover (from horizon.md) |
| `openstack_dashboard/defaults.py` | `ANGULAR_FEATURES['images_panel'] = True` | Must flip to `False` (from horizon.md, Section: De-angularization) |
| `openstack_dashboard/enabled/_1020_project_images_panel.py` | Panel registration | `ADD_ANGULAR_MODULES` / `ADD_JS_FILES` entries to be removed |

### Related Reviews (Context)

| Review | Subject | Status | Author | Relevance |
|--------|---------|--------|--------|-----------|
| [992714](https://review.opendev.org/c/openstack/horizon/+/992714) | Switch default Key Pairs panel from AngularJS to Python | **Merged** | Owen McGonagle | Precedent — same pattern, same topic |
| [968405](https://review.opendev.org/c/openstack/horizon/+/968405) | Add expandable rows with chevrons to Images table | Abandoned | Owen McGonagle | Earlier attempt, superseded by 982600 |
| [966349](https://review.opendev.org/c/openstack/horizon/+/966349) | De-angularize the Key Pairs table | **Merged** | Owen McGonagle | Part of broader de-angularize effort |
| [981026](https://review.opendev.org/c/openstack/horizon/+/981026) | Shorten chevron detail labels in Key Pairs panel | **Merged** | Owen McGonagle | UX refinement after Key Pairs migration |

### Post-Switchover Cleanup Required

Per the migration checklist (from horizon.md):
1. Remove `ADD_ANGULAR_MODULES` and `ADD_JS_FILES` from the Images panel enabled file
2. Delete Angular REST endpoint at `api/rest/glance.py` if no other Angular panel uses it
3. Remove orphaned `.spec.js` Karma test files
4. Clean up `REST_API_REQUIRED_SETTINGS` entries only needed by the Angular Images panel
5. Remove Angular controller/service/directive files under `static/app/core/images/`

### Sprint Context

[OSPRH-16422](https://redhat.atlassian.net/browse/OSPRH-16422) (filtering) is currently in **UI Sprint 29** (2026-07-13 to 2026-07-27, active). This suggests active work is ongoing and the team is prioritizing this epic.

---

Generated: 2026-07-15 | Skill: /triassessment | Model: claude-opus-4-6
