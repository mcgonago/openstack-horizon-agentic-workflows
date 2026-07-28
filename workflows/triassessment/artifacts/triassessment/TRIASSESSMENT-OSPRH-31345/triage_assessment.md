# Triage Assessment: OSPRH-31345

**Ticket:** [OSPRH-31345](https://redhat.atlassian.net/browse/OSPRH-31345)
**Parent:** [RHOSSTRAT-1355](https://redhat.atlassian.net/browse/RHOSSTRAT-1355) — Remove angular.js from Key Pair view in Horizon UI
**Gerrit Topic:** [de-angularize](https://review.opendev.org/q/topic:de-angularize+project:openstack/horizon)

---

## Ticket Summary

| Field | Value |
|-------|-------|
| Key | [OSPRH-31345](https://redhat.atlassian.net/browse/OSPRH-31345) |
| Type | Epic |
| Status | In Progress |
| Priority | Normal |
| Component | python-django-horizon |
| Assignee | Owen McGonagle |
| Reporter | Radomir Dopieralski |
| Team | rhos-dfg-ui / rhos-ops-platform-services-ui |
| Fix Version | rhos-19.0.0 GA |
| Created | 2026-06-16 |
| Updated | 2026-06-16 |
| Labels | (none) |
| Parent | [RHOSSTRAT-1355](https://redhat.atlassian.net/browse/RHOSSTRAT-1355) (Initiative, In Progress) |

---

## Epic Progress Summary

| Metric | Value |
|--------|-------|
| Total Children | 6 |
| Closed / Done | **6 (100%)** |
| In Progress | 0 |
| Backlog / To Do | 0 |
| Blocked | 0 |
| With Active Gerrit Reviews | 0 |
| Gerrit Reviews Merged | 6 |

---

## Epic Children Status

| Key | Summary | Type | Status | Assignee | Created | Updated | Review | Review Status |
|-----|---------|------|--------|----------|---------|---------|--------|---------------|
| [OSPRH-12802](https://redhat.atlassian.net/browse/OSPRH-12802) | Implement key pair create form in Python | Task | Closed | Owen McGonagle | 2025-01-08 | 2026-06-16 | [967269](https://review.opendev.org/c/openstack/horizon/+/967269), [966349](https://review.opendev.org/c/openstack/horizon/+/966349) | **Merged**, **Merged** |
| [OSPRH-12803](https://redhat.atlassian.net/browse/OSPRH-12803) | Add chevrons to the key pair table | Task | Closed | Owen McGonagle | 2025-01-08 | 2026-06-16 | [966349](https://review.opendev.org/c/openstack/horizon/+/966349) | **Merged** |
| [OSPRH-22199](https://redhat.atlassian.net/browse/OSPRH-22199) | Investigate create keypair behavioral differences in Django/Angular | Spike | Closed | Unassigned | 2025-11-18 | 2026-07-13 | — | — |
| [OSPRH-22200](https://redhat.atlassian.net/browse/OSPRH-22200) | Fix row margins for Django rows with chevrons | Task | Closed | Tatiana Ovchinnikova | 2025-11-18 | 2026-06-16 | [967773](https://review.opendev.org/c/openstack/horizon/+/967773) | **Merged** |
| [OSPRH-22201](https://redhat.atlassian.net/browse/OSPRH-22201) | Fix items amount in Django tables with chevrons | Task | Closed | Tatiana Ovchinnikova | 2025-11-18 | 2026-06-16 | [969532](https://review.opendev.org/c/openstack/horizon/+/969532) | **Merged** |
| [OSPRH-31021](https://redhat.atlassian.net/browse/OSPRH-31021) | Switch default Key Pairs panel from AngularJS to Python | Task | Closed | Owen McGonagle | 2026-06-10 | 2026-07-14 | [992714](https://review.opendev.org/c/openstack/horizon/+/992714), [992902](https://review.opendev.org/c/openstack/horizon/+/992902) | **Merged**, **Merged** |

---

## Technical Context

This epic represents the **completed** de-angularization of the Key Pairs panel in Horizon (from horizon.md). The work followed the standard migration pattern:

1. **Implement Python replacement** — Django class-based views with `DataTable` for the Key Pairs panel (OSPRH-12802, OSPRH-12803)
2. **Fix UX parity issues** — Row margins and item counts with chevrons (OSPRH-22200, OSPRH-22201)
3. **Investigate behavioral differences** — Spike to audit gaps between Angular and Django create forms (OSPRH-22199)
4. **Flip the default** — `ANGULAR_FEATURES['key_pairs_panel']` switched from `True` to `False` (OSPRH-31021, review [992714](https://review.opendev.org/c/openstack/horizon/+/992714))
5. **Fix regression** — Key pair create success message lost on redirect (review [992902](https://review.opendev.org/c/openstack/horizon/+/992902))

All 6 upstream Gerrit patches are **merged**. The switchover review [992714](https://review.opendev.org/c/openstack/horizon/+/992714) merged on 2026-07-14, completing the migration.

**Note:** `ANGULAR_FEATURES['key_pairs_panel']` in `defaults.py` currently still shows `True` in the knowledge base snapshot (from horizon.md), but the switchover patch has been merged. The knowledge base should be updated to reflect `key_pairs_panel: False`.

---

## Dependencies & Blockers

| Dependency | Assignee | Team | Status | Notes |
|-----------|----------|------|--------|-------|
| Python form implementation | Owen McGonagle | rhos-dfg-ui | **Done** | Reviews 967269, 966349 merged |
| Chevrons for key pair table | Owen McGonagle | rhos-dfg-ui | **Done** | Review 966349 merged |
| Behavioral investigation | Unassigned | rhos-dfg-ui | **Done** | OSPRH-22199 closed |
| UX fixes (margins, item counts) | Tatiana Ovchinnikova | Horizon upstream | **Done** | Reviews 967773, 969532 merged |
| Default switchover | Owen McGonagle | rhos-dfg-ui | **Done** | Review 992714 merged 2026-07-14 |
| Post-switchover fix | Owen McGonagle | rhos-dfg-ui | **Done** | Review 992902 merged 2026-07-09 |

No outstanding dependencies or blockers.

---

## Impact Analysis

**Current state:** All work is complete. The Key Pairs panel now defaults to the Python version.

**What was achieved:**
- Removed AngularJS dependency from the Key Pairs panel
- Eliminated EOL JavaScript framework risk for this panel
- Enabled Angular code cleanup (controllers, `.spec.js` tests, REST endpoints)
- Established the migration pattern now being followed by the Images panel ([OSPRH-31340](https://redhat.atlassian.net/browse/OSPRH-31340))

**Remaining action:** The epic status is "In Progress" in Jira but all children are closed. Recommend closing the epic.

---

## Recommendation

| Dimension | Assessment |
|-----------|-----------|
| Verdict | **CLOSE** |
| Confidence | High |
| Rationale | All 6 children closed, all 6 Gerrit patches merged, switchover complete |

### Rationale

Assessment indicates this epic should be closed. All work items are complete:
- 6/6 children closed
- 6/6 Gerrit reviews merged
- The switchover patch ([992714](https://review.opendev.org/c/openstack/horizon/+/992714)) merged on 2026-07-14
- A post-switchover regression fix ([992902](https://review.opendev.org/c/openstack/horizon/+/992902)) was also merged

**Recommended actions:**
1. Close [OSPRH-31345](https://redhat.atlassian.net/browse/OSPRH-31345) as Done
2. Update parent initiative [RHOSSTRAT-1355](https://redhat.atlassian.net/browse/RHOSSTRAT-1355) — mark Key Pairs migration complete
3. Consider whether Angular cleanup tasks (removing JS files, REST endpoints, `.spec.js` tests) need separate tickets or were included in the switchover patch
4. This epic serves as the proven precedent for the sister epic [OSPRH-31340](https://redhat.atlassian.net/browse/OSPRH-31340) (Images panel)

---

## Talking Points

- The Key Pairs panel de-angularization is **100% complete** — all 6 children closed, all 6 Gerrit patches merged
- The switchover patch merged on 2026-07-14 — Key Pairs now defaults to the Python version
- A post-switchover regression was caught and fixed promptly (success message redirect issue)
- This epic is the **proven precedent** for the Images panel migration ([OSPRH-31340](https://redhat.atlassian.net/browse/OSPRH-31340)), which is at 40%
- The epic Jira status is still "In Progress" — recommend closing it as Done
- Timeline: work started 2025-01-08, completed 2026-07-14 (~18 months total, with significant gaps)
- Contributors: Owen McGonagle (lead), Tatiana Ovchinnikova (UX fixes), Radomir Dopieralski (reporter/oversight)

---

## Deep Analysis

### Code Paths Affected (Post-Migration)

| Path | Role | Status |
|------|------|--------|
| `openstack_dashboard/dashboards/project/key_pairs/` | Django views (replacement) | Active — now the default |
| `openstack_dashboard/static/app/core/keypairs/` | Angular controllers (deprecated) | Still in tree — cleanup candidate |
| `openstack_dashboard/api/nova.py` | Nova API layer (keypair calls) | Shared by both; no migration impact |
| `openstack_dashboard/defaults.py` | `ANGULAR_FEATURES['key_pairs_panel']` | Flipped to `False` by review 992714 |

### Complete Gerrit Review History

| Review | Subject | Author | Status | Patchset | Topic | Merged |
|--------|---------|--------|--------|----------|-------|--------|
| [966349](https://review.opendev.org/c/openstack/horizon/+/966349) | De-angularize the Key Pairs table | Owen McGonagle | **Merged** | ps21 | de-angularize | 2025-11-20 |
| [967269](https://review.opendev.org/c/openstack/horizon/+/967269) | De-angularize Key Pairs: create and download | Owen McGonagle | **Merged** | ps32 | patchset-22-revert | 2026-03-18 |
| [967773](https://review.opendev.org/c/openstack/horizon/+/967773) | Fix inconsistent borders for rows with chevrons | Tatiana Ovchinnikova | **Merged** | ps4 | fix_marins | 2025-12-02 |
| [969532](https://review.opendev.org/c/openstack/horizon/+/969532) | Fix "Displaying n items" count for tables with chevrons | Tatiana Ovchinnikova | **Merged** | ps2 | items | 2026-01-20 |
| [992714](https://review.opendev.org/c/openstack/horizon/+/992714) | Switch default Key Pairs panel from AngularJS to Python | Owen McGonagle | **Merged** | ps13 | de-angularize | 2026-07-14 |
| [992902](https://review.opendev.org/c/openstack/horizon/+/992902) | Fix key pair create success message lost on page redirect | Owen McGonagle | **Merged** | ps6 | fix/key-pair-success-message | 2026-07-09 |

### Relationship to Images Panel Epic

This epic and [OSPRH-31340](https://redhat.atlassian.net/browse/OSPRH-31340) (Images panel) are siblings under the same de-angularization initiative. They share:
- Same Gerrit topic (`de-angularize`)
- Same team (rhos-dfg-ui)
- Same migration pattern (audit → implement → switchover → cleanup)
- Same code infrastructure (chevrons, `DataTable`, `ANGULAR_FEATURES`)

Key Pairs completion de-risks the Images panel effort — the pattern is validated, and shared infrastructure fixes (chevron margins, item counts) apply to both panels.

### Post-Switchover Cleanup Checklist

Per the migration checklist (from horizon.md):
1. Remove `ADD_ANGULAR_MODULES` and `ADD_JS_FILES` from Key Pairs enabled file — verify if done in 992714
2. Delete Angular REST endpoints used only by Key Pairs — verify if any remain
3. Remove orphaned `.spec.js` Karma test files under `static/app/core/keypairs/`
4. Clean up `REST_API_REQUIRED_SETTINGS` entries only needed by Angular Key Pairs
5. Remove Angular controller/service files under `static/app/core/keypairs/`

These cleanup items may need separate tickets if not addressed in the switchover patch.

---

Generated: 2026-07-15 | Skill: /triassessment | Model: claude-opus-4-6
