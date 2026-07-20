# Related Tickets: OSPRH-31345

**Epic:** [OSPRH-31345](https://redhat.atlassian.net/browse/OSPRH-31345) — Switch off the Angular.js version of the Key Pairs panel and default to the Python version

---

## 1. Ticket Hierarchy

| Level | Ticket | Title | Status | Assignee | Created | Updated |
|-------|--------|-------|--------|----------|---------|---------|
| **Initiative** | [RHOSSTRAT-1355](https://redhat.atlassian.net/browse/RHOSSTRAT-1355) | Remove angular.js from Key Pair view in Horizon UI | In Progress | — | — | — |
| **Epic** | [OSPRH-31345](https://redhat.atlassian.net/browse/OSPRH-31345) | Switch off Angular.js Key Pairs panel, default to Python | In Progress | Owen McGonagle | 2026-06-16 | 2026-06-16 |
| Task | [OSPRH-12802](https://redhat.atlassian.net/browse/OSPRH-12802) | Implement key pair create form in Python | Closed | Owen McGonagle | 2025-01-08 | 2026-06-16 |
| Task | [OSPRH-12803](https://redhat.atlassian.net/browse/OSPRH-12803) | Add chevrons to the key pair table | Closed | Owen McGonagle | 2025-01-08 | 2026-06-16 |
| Spike | [OSPRH-22199](https://redhat.atlassian.net/browse/OSPRH-22199) | Investigate create keypair behavioral differences | Closed | Unassigned | 2025-11-18 | 2026-07-13 |
| Task | [OSPRH-22200](https://redhat.atlassian.net/browse/OSPRH-22200) | Fix row margins for Django rows with chevrons | Closed | Tatiana Ovchinnikova | 2025-11-18 | 2026-06-16 |
| Task | [OSPRH-22201](https://redhat.atlassian.net/browse/OSPRH-22201) | Fix items amount in Django tables with chevrons | Closed | Tatiana Ovchinnikova | 2025-11-18 | 2026-06-16 |
| Task | [OSPRH-31021](https://redhat.atlassian.net/browse/OSPRH-31021) | Switch default Key Pairs panel from AngularJS to Python | Closed | Owen McGonagle | 2026-06-10 | 2026-07-14 |

---

## 2. Blocking Chain

```
RHOSSTRAT-1355 (Initiative: Remove Angular.js from Key Pair view)
  └── OSPRH-31345 (Epic: Switch off Angular.js Key Pairs panel) [ALL DONE]
        │
        ├── PHASE 1: Build Python replacement ──────────────────────
        │   ├── OSPRH-12803 (Chevrons for table) ✅ → Review 966349 Merged (2025-11-20)
        │   └── OSPRH-12802 (Create form in Python) ✅ → Reviews 967269, 966349 Merged
        │
        ├── PHASE 2: Fix UX parity issues ──────────────────────────
        │   ├── OSPRH-22199 (Investigate differences) ✅ Closed (Spike)
        │   ├── OSPRH-22200 (Fix row margins) ✅ → Review 967773 Merged (2025-12-02)
        │   └── OSPRH-22201 (Fix item counts) ✅ → Review 969532 Merged (2026-01-20)
        │
        └── PHASE 3: Switchover ────────────────────────────────────
            └── OSPRH-31021 (Flip default to Python) ✅ → Review 992714 Merged (2026-07-14)
                └── Post-switchover fix → Review 992902 Merged (2026-07-09)
```

**No blockers remain.** All phases complete.

---

## 3. Cross-Team Dependencies

| Dependency | Team | Status | Notes |
|-----------|------|--------|-------|
| Horizon core reviewer bandwidth | Horizon Core (upstream) | Resolved | All reviews merged |
| Chevron infrastructure | Shared (used by Images panel too) | Done | Reviews 967773, 969532 fix both panels |

**No outstanding cross-team dependencies.** This is a self-contained effort within rhos-dfg-ui / Horizon upstream.

---

## 4. Resolution Paths

### Current State: COMPLETE

All children closed. All Gerrit reviews merged. The Key Pairs panel now defaults to the Python/Django version.

**Recommended next steps:**
1. Close the epic [OSPRH-31345](https://redhat.atlassian.net/browse/OSPRH-31345) as Done
2. Update initiative [RHOSSTRAT-1355](https://redhat.atlassian.net/browse/RHOSSTRAT-1355) — Key Pairs migration complete
3. Verify Angular cleanup is complete or create follow-up tickets for:
   - Removing Angular JS files under `static/app/core/keypairs/`
   - Removing orphaned `.spec.js` Karma tests
   - Cleaning up `ADD_ANGULAR_MODULES` / `ADD_JS_FILES` from enabled file

---

## 5. Sister Epic Comparison

| Dimension | Key Pairs (OSPRH-31345) | Images (OSPRH-31340) |
|-----------|------------------------|---------------------|
| Status | **100% Complete** | 40% Complete |
| Children Total | 6 | 10 |
| Children Closed | 6 | 4 |
| Gerrit Reviews Merged | 6 | 3 |
| Active Reviews | 0 | 2 |
| Backlog Items | 0 | 4 |
| Switchover Patch | [992714](https://review.opendev.org/c/openstack/horizon/+/992714) **Merged** | [992675](https://review.opendev.org/c/openstack/horizon/+/992675) WIP |
| Fix Version | rhos-19.0.0 GA | (none) |
| Initiative Parent | [RHOSSTRAT-1355](https://redhat.atlassian.net/browse/RHOSSTRAT-1355) | [RHOSSTRAT-1354](https://redhat.atlassian.net/browse/RHOSSTRAT-1354) |

Key Pairs is the proven template for Images. The shared infrastructure fixes (chevrons, item counts) already benefit both panels.

---

## 6. Gerrit Review Summary

| Review | Subject | Author | Status | Patchset | Topic | Merged |
|--------|---------|--------|--------|----------|-------|--------|
| [966349](https://review.opendev.org/c/openstack/horizon/+/966349) | De-angularize the Key Pairs table | Owen McGonagle | **Merged** | ps21 | de-angularize | 2025-11-20 |
| [967269](https://review.opendev.org/c/openstack/horizon/+/967269) | De-angularize Key Pairs: create and download | Owen McGonagle | **Merged** | ps32 | patchset-22-revert | 2026-03-18 |
| [967773](https://review.opendev.org/c/openstack/horizon/+/967773) | Fix inconsistent borders for rows with chevrons | Tatiana Ovchinnikova | **Merged** | ps4 | fix_marins | 2025-12-02 |
| [969532](https://review.opendev.org/c/openstack/horizon/+/969532) | Fix "Displaying n items" count for tables with chevrons | Tatiana Ovchinnikova | **Merged** | ps2 | items | 2026-01-20 |
| [992714](https://review.opendev.org/c/openstack/horizon/+/992714) | Switch default Key Pairs panel from AngularJS to Python | Owen McGonagle | **Merged** | ps13 | de-angularize | 2026-07-14 |
| [992902](https://review.opendev.org/c/openstack/horizon/+/992902) | Fix key pair create success message lost on page redirect | Owen McGonagle | **Merged** | ps6 | fix/key-pair-success-message | 2026-07-09 |

---

Generated: 2026-07-15 | Skill: /triassessment | Model: claude-opus-4-6
