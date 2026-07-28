# Related Tickets: OSPRH-31340

**Epic:** [OSPRH-31340](https://redhat.atlassian.net/browse/OSPRH-31340) — Switch off the Angular.js version of the Images panel and default to Python version

---

## 1. Ticket Hierarchy

| Level | Ticket | Title | Status | Assignee | Created | Updated |
|-------|--------|-------|--------|----------|---------|---------|
| **Initiative** | [RHOSSTRAT-1354](https://redhat.atlassian.net/browse/RHOSSTRAT-1354) | Remove angular.js from Images view in Horizon UI | In Progress | — | — | — |
| **Epic** | [OSPRH-31340](https://redhat.atlassian.net/browse/OSPRH-31340) | Switch off the Angular.js version of the Images panel and default to Python version | In Progress | Radomir Dopieralski | 2026-06-16 | 2026-06-16 |
| Spike | [OSPRH-14464](https://redhat.atlassian.net/browse/OSPRH-14464) | Identify all differences between Angular and Python for the Images panel | Closed | Radomir Dopieralski | 2025-03-04 | 2026-06-16 |
| Task | [OSPRH-16421](https://redhat.atlassian.net/browse/OSPRH-16421) | Add chevrons to the Images table | Closed | Owen McGonagle | 2025-05-06 | 2026-06-16 |
| Task | [OSPRH-16422](https://redhat.atlassian.net/browse/OSPRH-16422) | Update filtering in the Images table | In Progress | Owen McGonagle | 2025-05-06 | 2026-07-16 |
| Task | [OSPRH-16423](https://redhat.atlassian.net/browse/OSPRH-16423) | Add missing fields to the Image Create/Edit form | Backlog | Unassigned | 2025-05-06 | 2026-06-16 |
| Task | [OSPRH-16424](https://redhat.atlassian.net/browse/OSPRH-16424) | Update visibility settings in the Image Create/Edit form | Backlog | Unassigned | 2025-05-06 | 2026-06-16 |
| Task | [OSPRH-16425](https://redhat.atlassian.net/browse/OSPRH-16425) | Add image metadata to the Image Create/Edit form | Closed | Radomir Dopieralski | 2025-05-06 | 2026-06-16 |
| Task | [OSPRH-16426](https://redhat.atlassian.net/browse/OSPRH-16426) | Add activate/deactivate actions to the Images view | In Progress | Owen McGonagle | 2025-05-06 | 2026-07-13 |
| Task | [OSPRH-26419](https://redhat.atlassian.net/browse/OSPRH-26419) | Add filtering to the image metadata form | Backlog | Radomir Dopieralski | 2026-02-10 | 2026-07-13 |
| Task | [OSPRH-26420](https://redhat.atlassian.net/browse/OSPRH-26420) | Add support for enum and bool type fields to image metadata | Backlog | Unassigned | 2026-02-10 | 2026-06-16 |
| Task | [OSPRH-26421](https://redhat.atlassian.net/browse/OSPRH-26421) | Write separated UI tests for the image metadata form | Closed | Radomir Dopieralski | 2026-02-10 | 2026-07-10 |

---

## 2. Blocking Chain

```
RHOSSTRAT-1354 (Initiative: Remove Angular.js from Images view)
  └── OSPRH-31340 (Epic: Switch off Angular.js Images panel) [In Progress]
        │
        ├── DONE ────────────────────────────────────────────────────
        │   ├── OSPRH-14464 (Spike: Identify differences) ✅ Closed
        │   ├── OSPRH-16421 (Chevrons) ✅ Closed → Review 982600 Merged
        │   ├── OSPRH-16425 (Image metadata form) ✅ Closed → Review 969791 Merged
        │   └── OSPRH-26421 (UI tests for metadata) ✅ Closed → Review 980459 Merged
        │
        ├── IN PROGRESS ─────────────────────────────────────────────
        │   ├── OSPRH-16422 (Filtering) 🔄 → Review 986478 Under Review (ps5)
        │   └── OSPRH-16426 (Activate/deactivate) 🔄 → Review 986458 Needs Revision (CR-1)
        │
        ├── BACKLOG ─────────────────────────────────────────────────
        │   ├── OSPRH-16423 (Missing form fields) ⬜ Unassigned
        │   ├── OSPRH-16424 (Visibility settings) ⬜ Unassigned
        │   ├── OSPRH-26419 (Metadata filtering) ⬜ Assigned: rdopiera
        │   └── OSPRH-26420 (Enum/bool metadata) ⬜ Unassigned
        │
        └── SWITCHOVER (no child ticket) ────────────────────────────
            └── Review 992675 (Switch default to Python) ⚠️ WIP, CI failing
```

**Sequencing notes:**
- The backlog items (form fields, visibility, metadata enhancements) can be worked in parallel
- The switchover patch (992675) depends on ALL feature-parity items being complete
- Post-switchover cleanup (Angular code removal) is not yet tracked as a child ticket

---

## 3. Cross-Team Dependencies

| Dependency | Team | Status | Notes |
|-----------|------|--------|-------|
| Gerrit core reviewer bandwidth | Horizon Core (upstream) | Ongoing | Reviews 986478 and 986458 need +2 votes |
| CI infrastructure | OpenDev Zuul | Available | Standard voting jobs |

**No cross-team blockers.** This epic is entirely within the rhos-dfg-ui team's scope and the upstream Horizon project. All patches land in the same repository (`openstack/horizon`).

---

## 4. Resolution Paths

### Path A: Complete All Feature-Parity Items First (Recommended)

1. Resolve CR-1 on [986458](https://review.opendev.org/c/openstack/horizon/+/986458) (activate/deactivate)
2. Get [986478](https://review.opendev.org/c/openstack/horizon/+/986478) (filtering) reviewed and merged
3. Assign and implement remaining 3 backlog items (OSPRH-16423, OSPRH-16424, OSPRH-26420)
4. OSPRH-26419 (metadata filtering) is assigned to rdopiera — confirm timeline
5. Un-WIP review [992675](https://review.opendev.org/c/openstack/horizon/+/992675) and fix CI
6. Merge switchover patch
7. Post-switchover: remove Angular code, REST endpoints, orphaned tests

**Estimated remaining effort:** 4-6 sprints (based on current velocity of ~1 merged patch per sprint)

### Path B: Partial Switchover (Not Recommended)

Switch the default to Python now and accept the missing features as known gaps. This would:
- Unblock the switchover sooner
- Risk user-visible feature regression (missing Kernel/Ramdisk fields, missing visibility controls)
- Require follow-up tickets for parity gaps

**Not recommended** because the remaining items are relatively small and the Angular version is stable in the interim.

### Path C: Defer Entire Epic

Stop work and leave the Angular Images panel as-is. This would:
- Accept ongoing AngularJS security risk
- Keep Angular CI jobs running (build pipeline overhead)
- Waste the 40% already completed

**Not recommended** — the work is well underway and the pattern is proven.

---

## 5. Contact Points

| Role | Name | Email | Relevance |
|------|------|-------|-----------|
| Epic owner / Reporter | Radomir Dopieralski | rdopiera@redhat.com | Technical lead, backlog items assigned |
| Active contributor | Owen McGonagle | omcgonag@redhat.com | In-progress reviews, switchover patch |
| Upstream reviewer | Tatiana Ovchinnikova | — | Set 992675 to WIP, review gatekeeper |

---

## 6. Gerrit Review Summary

| Review | Subject | Author | Status | Patchset | Key Votes | Topic |
|--------|---------|--------|--------|----------|-----------|-------|
| [982600](https://review.opendev.org/c/openstack/horizon/+/982600) | Add chevrons to the Images table | Owen McGonagle | **Merged** | ps10 | CR+2x2, W+1 | de-angularize |
| [969791](https://review.opendev.org/c/openstack/horizon/+/969791) | Add python-based images metadata form | Radomir Dopieralski | **Merged** | ps11 | CR+2x2, W+1 | images-metadata |
| [980459](https://review.opendev.org/c/openstack/horizon/+/980459) | Add ui tests for the image metadata form | Radomir Dopieralski | **Merged** | ps6 | CR+2x2, W+1 | metadata-tests |
| [986478](https://review.opendev.org/c/openstack/horizon/+/986478) | Update filtering in the Images table | Owen McGonagle | Under Review | ps5 | No +2 votes | de-angularize |
| [986458](https://review.opendev.org/c/openstack/horizon/+/986458) | Add activate/deactivate row actions to Images table | Owen McGonagle | Needs Revision | ps6 | CR-1 | de-angularize |
| [992675](https://review.opendev.org/c/openstack/horizon/+/992675) | Switch default Images panel from AngularJS to Python | Owen McGonagle | WIP | ps3 | V-1, W-1 | de-angularize |

---

Generated: 2026-07-15 | Skill: /triassessment | Model: claude-opus-4-6
