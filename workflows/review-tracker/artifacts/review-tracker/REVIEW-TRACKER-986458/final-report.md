# Final Report -- Review 986458: Add Activate/Deactivate Row Actions to Images Table

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986458](https://review.opendev.org/c/openstack/horizon/+/986458)
**Author:** Owen McGonagle
**Final Status:** MERGED (2026-07-21 16:43 UTC)
**Total Patchsets:** 8
**Total Duration:** 85 days (2026-04-27 to 2026-07-21)
**Total Comments:** 10 across 5 threads from 3 reviewers
**Tracker:** [tracker-986458.md](./tracker-986458.md)

---

## Executive Summary

This review added Deactivate and Reactivate row actions to the Images table in OpenStack Horizon as part of the de-angularization initiative (topic: `de-angularize`). The implementation added two new `PolicyAction` subclasses — `DeactivateImage` and `ReactivateImage` — with RBAC policy checks, image state validation, and owner-based visibility controls.

The review had an unusual lifecycle: a rapid initial push (PS1-PS4 over 2 days in late April) followed by a 78-day dormant period while WIP. Active review began on July 15 when Owen rebased and marked it ready. Radomir Dopieralski provided substantive feedback within an hour, raising a thoughtful question about whether the `allowed()` method was redundant with `policy_rules` — which evolved into a multi-day discussion about owner check design patterns. The technical debate was resolved constructively, with Radomir accepting the current approach and suggesting `PolicyTargetMixin` as a follow-up. Jan Jasek independently tested in devstack and gave final approval.

Notably, Radomir went beyond his reviewer role to resolve a merge conflict himself — rebasing PS6 to PS7/PS8 and re-voting — which unblocked the gate pipeline without requiring action from the author.

This was the third review tracked end-to-end by the `/review-tracker` skill, and the first to exercise the deep-dive bridge analysis capability across 7 incremental scans with 2 bridge artifacts.

---

## Review Timeline

| Date | Day # | Event | Details |
|------|-------|-------|---------|
| 2026-04-27 | 1 | First push | PS1 uploaded |
| 2026-04-27 | 1 | PS2 uploaded | NO_CODE_CHANGE — commit message update |
| 2026-04-27 | 1 | CI pass | PS1 Verified+1, PS2 Verified+1 |
| 2026-04-28 | 2 | PS3-PS4 uploaded | NO_CODE_CHANGE — commit message updates |
| 2026-04-28 | 2 | CI pass | PS3 Verified+1, PS4 Verified+1 |
| 2026-06-30 | 65 | Tatiana CR-1 | Blueprint reference request (CMT-TAT-1) |
| 2026-07-15 | 80 | PS5 uploaded | NO_CODE_CHANGE — commit message update (added blueprint reference) |
| 2026-07-15 | 80 | Ready for review | Owen marked PS5/PS6 ready for review |
| 2026-07-15 | 80 | PS6 uploaded | TRIVIAL_REBASE — rebase on master |
| 2026-07-15 | 80 | **First substantive review** | Radomir Dopieralski: Code-Review -1, 2 inline comments on `tables.py` |
| 2026-07-15 | 80 | Radomir self-corrects | Noticed `policy_rules` already present, pivoted question (CMT-RAD-1) |
| 2026-07-15 | 80 | **Tracker scan #1-3** | Initial scan, recheck, deep-dive bridge analysis |
| 2026-07-16 | 81 | Owen responds | Defended `allowed()` status check — deactivate button on inactive images |
| 2026-07-16 | 81 | Radomir pivots | "The owner check seems harmful" — new concern |
| 2026-07-16 | 81 | **Tracker scans #4-6** | Self-correction surfaced, deep-dive regenerated, Owen's response tracked |
| 2026-07-16 | 81 | Owen responds again | Cited admin panel pattern, 58 existing actions, offered follow-up path |
| 2026-07-17 | 82 | **Radomir accepts** | CR+2: "Let's explore this in followup patches. The code looks good otherwise." |
| 2026-07-21 | 86 | **Jan approves** | CR+2 + W+1: "Works in devstack, code looks good to me, thanks!" |
| 2026-07-21 | 86 | Gate failure | PS6 Verified-2 — merge conflict with master |
| 2026-07-21 | 86 | **Radomir resolves conflict** | Rebased to PS7, resolved conflict, published PS8, re-voted CR+2 + W+1 |
| 2026-07-21 | 86 | CI pass | PS8 Verified+1 |
| 2026-07-21 | 86 | **MERGED** | Gate pipeline succeeded, change merged at 16:43 UTC |
| 2026-07-21 | 86 | **Tracker scan #7** | Final scan — all threads resolved, gate entered |

---

## Patchset History

| PS | Date | Kind | Reason | CI Result |
|----|------|------|--------|-----------|
| 1 | 2026-04-27 20:25 | REWORK | Initial implementation | Verified+1 |
| 2 | 2026-04-27 20:42 | NO_CODE_CHANGE | Commit message update | Verified+1 |
| 3 | 2026-04-28 02:24 | NO_CODE_CHANGE | Commit message update | Verified+1 |
| 4 | 2026-04-28 02:27 | NO_CODE_CHANGE | Commit message update | Verified+1 |
| 5 | 2026-07-15 14:33 | NO_CODE_CHANGE | Add blueprint reference (CMT-TAT-1) | (superseded by PS6) |
| 6 | 2026-07-15 14:34 | TRIVIAL_REBASE | Rebase on master | Verified+1, then Verified-2 (gate merge conflict) |
| 7 | 2026-07-21 13:47 | REWORK | Radomir rebased — resolved merge conflict | (superseded by PS8) |
| 8 | 2026-07-21 13:48 | REWORK | Radomir published edit on PS7 | Verified+2 (gate — merge) |

### Phase Narrative

**Development phase (PS1, Day 1):** Owen pushed the initial implementation. Unlike many Horizon patches, this one passed CI on the first try — `DeactivateImage` and `ReactivateImage` were straightforward `PolicyAction` subclasses following established patterns (`DeleteImage`, `EditImage`).

**Commit message polishing (PS2-PS4, Days 1-2):** Three commit message updates in quick succession. No code changes. CI passed each time.

**Dormant period (Days 2-65):** The review sat as WIP for over two months. On Day 65, Tatiana Ovchinnikova left a Code-Review -1 requesting a blueprint reference — the only activity during this period.

**Reactivation (PS5-PS6, Day 80):** Owen returned on July 15, added the blueprint reference (PS5), rebased (PS6), and marked the review ready. The 78-day gap is the dominant factor in the overall review duration.

**Active review (PS6, Days 80-82):** Radomir Dopieralski reviewed within 56 minutes of PS6 being marked ready. His feedback triggered a nuanced 3-day discussion about `allowed()` vs `policy_rules` vs owner check design patterns. The conversation evolved through three stages: (1) "add RBAC policy check" → (2) "is `allowed()` redundant?" → (3) "is the owner check harmful?" — each stage demonstrating deeper understanding. Owen's responses were technically detailed, citing 58 existing actions with the same pattern and the admin panel's PolicyTargetMixin approach. Radomir accepted on Day 82.

**Merge (Day 86):** Jan Jasek tested in devstack and gave CR+2 + W+1. PS6 failed the gate with a merge conflict (other changes had landed on `master` in the 6 days since PS6 was uploaded). Radomir took initiative, rebased the change himself, resolved the Git conflict, and re-voted — the review merged the same day.

---

## Reviewer Engagement

### Tatiana Ovchinnikova

- **First contact:** 2026-06-30 (Day 65)
- **Role:** Process reviewer
- **Comments:** 1 patchset-level blocking comment
- **Vote history:** CR-1 (PS4) → outdated by PS5
- **Key contribution:** Requested `Partially-Implements: blueprint removing-angularjs` — standard de-angularize process requirement. Her early comment (while the review was still WIP) ensured the blueprint reference was in place before active review began.

### Radomir Dopieralski

- **First contact:** 2026-07-15 (Day 80)
- **Role:** Core reviewer → conflict resolver → final approver
- **Comments:** 2 inline blocking (PS6), 1 self-correction (PS6), 2 follow-up replies (PS6), 1 patchset-level acceptance (PS6)
- **Vote history:** CR-1 (PS6) → CR+2 (PS6, Jul 17) → CR+2 + W+1 (PS8, Jul 21)
- **Key contributions:**
  1. Raised a substantive design question about `allowed()` vs `policy_rules` redundancy
  2. Self-corrected within 7 minutes after noticing `policy_rules` was already defined
  3. Pivoted to a deeper question about owner check design that led to a productive discussion
  4. Accepted the approach gracefully: "Let's explore this in followup patches"
  5. Resolved a merge conflict himself (PS7→PS8) instead of waiting for the author — exceptional reviewer behavior

### Jan Jasek

- **First contact:** 2026-07-21 (Day 86)
- **Role:** Final approver
- **Comments:** 1 patchset-level approval
- **Vote history:** CR+2 + W+1 (PS6, copied to PS8)
- **Key contribution:** Tested the change in devstack before approving — functional validation that the activate/deactivate buttons work correctly on live images.

---

## Comment Thread Analysis

| Thread ID | Author | Type | Severity | Posted | Responded | Response Time | Resolution |
|-----------|--------|------|----------|--------|-----------|---------------|------------|
| [CMT-TAT-1](./tracker-986458.md#cmt-tat-1) | Tatiana Ovchinnikova | PL / Blocking | HIGH | 2026-06-30 17:06 | 2026-07-15 14:33 | 15.0 days | PS5 fix — blueprint reference added |
| [CMT-RAD-1](./tracker-986458.md#cmt-rad-1) | Radomir Dopieralski | Inline / Blocking | HIGH | 2026-07-15 15:30 | 2026-07-16 01:59 | 10.5h | Discussion resolved — Radomir accepted approach (CR+2) |
| [CMT-RAD-2](./tracker-986458.md#cmt-rad-2) | Radomir Dopieralski | Inline / Blocking | MEDIUM | 2026-07-15 15:30 | 2026-07-16 16:52 | 25.4h | Owen referenced CMT-RAD-1 discussion — resolved by Radomir acceptance |
| [CMT-RAD-3](./tracker-986458.md#cmt-rad-3) | Radomir Dopieralski | PL / Informational | LOW | 2026-07-17 06:56 | — | — | No response needed — CR+2 acceptance |
| [CMT-JAN-1](./tracker-986458.md#cmt-jan-1) | Jan Jasek | PL / Informational | LOW | 2026-07-21 11:42 | — | — | No response needed — devstack approval |

---

## Response Time Metrics

### Comment Response Latency (Blocking Threads Only)

| Metric | Value |
|--------|-------|
| Median response time | 15.0 days |
| Mean response time | 5.8 days |
| Fastest response | 10.5 hours (CMT-RAD-1 — `allowed()` discussion) |
| Slowest response | 15.0 days (CMT-TAT-1 — blueprint tag, review was dormant) |
| Total blocking threads | 3 |
| All resolved | Yes |

### Fix Implementation Velocity

| Thread | Comment Date | Response/Fix Date | Elapsed | Fix Description |
|--------|-------------|-------------------|---------|-----------------|
| CMT-TAT-1 | 2026-06-30 17:06 | 2026-07-15 14:33 (PS5) | 15.0d | Blueprint reference added to commit message |
| CMT-RAD-1 | 2026-07-15 15:30 | 2026-07-16 01:59 (reply) | 10.5h | Gerrit response defending `allowed()` design |
| CMT-RAD-2 | 2026-07-15 15:30 | 2026-07-16 16:52 (reply) | 25.4h | Referenced CMT-RAD-1 discussion |

### Response Time Analysis

The 15-day response time on CMT-TAT-1 is the dominant outlier, but it's misleading without context. Tatiana's comment arrived on June 30 while the review was dormant/WIP. Owen returned to the review on July 15 and addressed it immediately as part of the reactivation (PS5). The actual turnaround from "decided to work on this review" to "fix pushed" was effectively immediate.

Once the review was active, response times were strong. Owen responded to Radomir's first inline comment within 10.5 hours (overnight — the comment arrived at 15:30 UTC, Owen replied at 01:59 UTC the next day). The second response (CMT-RAD-2) came 15 hours later, as Owen chose to let the CMT-RAD-1 discussion settle before responding to the related thread.

---

## CI Performance

### Per-Patchset CI Results

| PS | Upload Time | CI Result | Notes |
|----|------------|-----------|-------|
| 1 | 2026-04-27 20:25 | Verified+1 | First-time pass |
| 2 | 2026-04-27 20:42 | Verified+1 | |
| 3 | 2026-04-28 02:24 | Verified+1 | |
| 4 | 2026-04-28 02:27 | Verified+1 | |
| 6 | 2026-07-15 14:34 | Verified+1 (check), Verified-2 (gate) | Gate: merge conflict |
| 8 | 2026-07-21 13:48 | Verified+2 | Gate pipeline — merge |

### CI Summary

| Metric | Value |
|--------|-------|
| Total check pipeline runs | 6 |
| Check passes | 6 (100%) |
| Check failures | 0 |
| Gate pipeline runs | 2 |
| Gate passes | 1 (50%) |
| Gate failure cause | Merge conflict (not code defect) |
| Rechecks triggered | 0 |

### CI Analysis

A perfect 100% check pass rate — every patchset passed CI on the first try. This is notable for a Horizon contribution and reflects the straightforward nature of the implementation: `DeactivateImage` and `ReactivateImage` follow well-established patterns from existing actions.

The single gate failure was a merge conflict, not a code issue. Between PS6 upload (Jul 15) and gate entry (Jul 21), other changes merged to `master` that touched `tables.py`, creating a conflict. Radomir resolved this by rebasing.

---

## Code Evolution Metrics

| Metric | Value |
|--------|-------|
| Total patchsets | 8 |
| REWORK (code changes) | 3 (PS1 initial, PS7-PS8 rebase resolution by Radomir) |
| NO_CODE_CHANGE (commit msg only) | 4 (PS2, PS3, PS4, PS5) |
| TRIVIAL_REBASE | 1 (PS6) |
| Development iterations to first CI pass | 1 (PS1 — first-time pass) |
| Patchsets by author (Owen) | 6 (PS1-PS6) |
| Patchsets by reviewer (Radomir) | 2 (PS7-PS8 — conflict resolution) |
| Longest patchset gap | 78 days (PS4 → PS5, dormant period) |
| Shortest patchset gap | 1 minute (PS7 → PS8, Radomir's edit) |

### Evolution Analysis

The 8 patchsets break down clearly:
- **1 code patchset** by the author (PS1) — the actual implementation
- **4 commit message updates** — polishing and adding the blueprint reference
- **1 rebase** by the author — catching up with master
- **2 patchsets by a reviewer** (Radomir) — conflict resolution and merge-readiness

The unusually low code iteration count (1 REWORK by the author) reflects a clean implementation that needed no code changes during review. The owner check discussion was resolved by accepting the existing approach rather than requiring code modifications.

---

## AI-Assisted Tracking Summary

This review was tracked by the `/review-tracker` skill across **7 scans** over **7 days** (2026-07-15 to 2026-07-21).

### Scan History

| # | Date | Key Finding |
|---|------|-------------|
| 1 | 2026-07-15 | Initial scan — 1 comment thread from Tatiana (blueprint reference) |
| 2 | 2026-07-15 | Recheck — PS5/PS6, WIP removed, votes reset |
| 3 | 2026-07-15 | Recheck — Radomir CR-1, 2 inline threads. Deep-dive bridge analysis on both |
| 4 | 2026-07-16 | Recheck — Surfaced Radomir's self-correction. Upgraded scan log to ISO timestamps |
| 5 | 2026-07-16 | Recheck — Owen responded, Radomir pivoted to owner check. Deep-dive regenerated |
| 6 | 2026-07-16 | Recheck — Owen's detailed response on owner check concern |
| 7 | 2026-07-21 | Recheck — **All threads resolved.** Radomir CR+2, Jan CR+2/W+1, PS6 gate failed, Radomir rebased to PS8, gate entered |

### Tracker Capabilities Exercised

| Capability | Used | Details |
|------------|------|---------|
| Initial scan | Yes | Full comment thread analysis and classification |
| Incremental recheck | Yes | 6 rechecks with change detection |
| Early exit (no changes) | No | Every recheck found new activity |
| Deep-dive bridge analysis | Yes | 2 bridge artifacts (CMT-RAD-1, CMT-RAD-2) with code archaeology |
| Self-correction detection | Yes | Radomir's self-correction surfaced and tracked across 3 scans |
| Comment evolution tracking | Yes | Tracked CMT-RAD-1 through 3 stages of question evolution |
| Playwright browser verification | No | Not requested for this review |
| Create-patch automation | No | No code changes needed — discussion resolved by acceptance |
| Verify-patch tox testing | No | Not used |
| Dashboard publishing | Yes | Published across 11 runs |
| Final report | Yes | This document |

### Value Delivered

1. **Deep-dive bridge analysis:** The code archaeology investigation on CMT-RAD-1 found that 58 actions across the codebase use the same `allowed()` + `policy_rules` dual pattern. This evidence was directly cited in Owen's Gerrit response and helped resolve the discussion constructively.

2. **Self-correction tracking:** The tracker detected Radomir's 7-minute self-correction and surfaced it explicitly (Scan #4), ensuring Owen's response addressed the *updated* question ("is `allowed()` redundant?") rather than the original ("add RBAC policy check"). This prevented a potentially confusing cross-talk.

3. **Comment evolution narrative:** Tracking the thread through three stages (RBAC policy → `allowed()` redundancy → owner check concern) provided a clear story of how the technical discussion evolved, making it easier for Owen to formulate targeted responses.

4. **Suggested responses:** Bridge artifacts included ready-to-paste Gerrit responses that Owen could adapt, reducing the effort of formulating technically precise replies.

---

## Key Milestones

| Milestone | Date | Day # | Elapsed Since Previous |
|-----------|------|-------|------------------------|
| First push (PS1) | 2026-04-27 20:25 | 1 | — |
| First CI pass (PS1) | 2026-04-27 ~21:30 | 1 | ~1h (estimated) |
| Blueprint comment (Tatiana CR-1) | 2026-06-30 17:06 | 65 | 63 days (dormant) |
| Reactivated (PS5/PS6, marked ready) | 2026-07-15 14:33 | 80 | 15 days |
| First substantive review (Radomir CR-1) | 2026-07-15 15:30 | 80 | 57 minutes |
| Owner check discussion resolved | 2026-07-17 06:56 | 82 | 1.6 days |
| Jan devstack approval (CR+2 + W+1) | 2026-07-21 11:42 | 86 | 4.2 days |
| Gate merge conflict (PS6) | 2026-07-21 ~13:00 | 86 | 1.3 hours |
| Radomir resolves conflict (PS8) | 2026-07-21 13:48 | 86 | ~48 minutes |
| **MERGED** | 2026-07-21 16:43 | 86 | 2h 55m (gate pipeline) |

### Phase Durations

| Phase | Start | End | Duration |
|-------|-------|-----|----------|
| Development (PS1 → first CI pass) | Day 1 | Day 1 | ~1 hour |
| Commit message polish (PS2-PS4) | Day 1 | Day 2 | 6 hours |
| Dormant / WIP | Day 2 | Day 80 | 78 days |
| Reactivation (blueprint fix + rebase) | Day 80 | Day 80 | < 1 hour |
| Review wait (ready → first review) | Day 80 | Day 80 | 57 minutes |
| Active review (Radomir discussion) | Day 80 | Day 82 | 1.6 days |
| Wait for second approval | Day 82 | Day 86 | 4.2 days |
| Gate + merge conflict resolution | Day 86 | Day 86 | 3.7 hours |
| **Total wall-clock** | Day 1 | Day 86 | **85 days** |
| **Active work time (excluding dormant)** | — | — | **~7 days** |

---

## Lessons Learned

### What Went Well

1. **Clean implementation — 100% CI pass rate:** PS1 passed CI on the first try, and every subsequent patchset also passed. This is the ideal case: a well-scoped change that follows established patterns (`DeleteImage`, `EditImage` as models) and doesn't fight the CI pipeline.

2. **Fast reviewer response time (57 minutes):** Radomir reviewed within an hour of the review being marked ready. This suggests good timing (the review was ready when reviewers were available) and that the change was approachable.

3. **Constructive technical discussion:** The owner check debate was a model of good open-source review culture. Radomir raised a valid design concern, self-corrected when he saw more context, Owen provided detailed evidence (58 actions, admin panel precedent), and Radomir accepted gracefully — "Let's explore this in followup patches." No ego, no deadlock.

4. **Reviewer went above and beyond:** Radomir resolved the merge conflict himself (PS7→PS8) rather than just reporting it. This saved a round-trip and enabled same-day merge.

5. **AI-assisted deep-dive analysis:** The bridge investigation found concrete evidence (58 action instances, lifecycle trace, edge case matrix) that directly informed Owen's Gerrit responses and helped close the discussion efficiently.

### What Could Improve

1. **78-day dormant period:** The review sat inactive from April 28 to July 15. While the code was ready (CI green from PS1), it was left as WIP for over two months. Publishing earlier would have shortened the total lifecycle significantly.

2. **15-day response to Tatiana's comment:** Tatiana's blueprint reference request arrived on June 30 but wasn't addressed until July 15. Even a brief acknowledgment ("Will add, thanks — working on this review next week") would have been better than silence. The actual fix took seconds.

3. **4 commit message patchsets (PS2-PS4):** Three consecutive commit message updates on Day 1-2 could have been a single patchset with `git commit --amend`. While harmless, they add noise to the patchset history.

### Patterns to Repeat

1. **Follow established action patterns** — `DeactivateImage` and `ReactivateImage` were modeled after existing actions (`DeleteImage`, `EditImage`), which is why they passed CI immediately and the code structure was familiar to reviewers.

2. **Provide evidence in review discussions** — Owen's response to Radomir cited 58 existing actions with the same pattern, specific file:line references, and the admin panel's approach. Data-driven responses resolve design discussions faster than opinions.

3. **Use deep-dive bridge analysis for substantive questions** — the code archaeology investigation produced the evidence Owen needed (lifecycle trace, edge case matrix, pattern count) in a structured format that was easy to adapt into Gerrit responses.

4. **Accept "let's do that in a follow-up" gracefully** — Radomir's resolution shows a healthy review culture. Not every improvement needs to block the current patch. Track it and address it next.

---

## Appendix A: Vote History

| Date | Voter | Label | Value | Patchset | Notes |
|------|-------|-------|-------|----------|-------|
| 2026-06-30 17:06 | Tatiana Ovchinnikova | Code-Review | -1 | PS4 | Blueprint reference request |
| 2026-07-15 15:30 | Radomir Dopieralski | Code-Review | -1 | PS6 | 2 inline comments on owner check / `allowed()` |
| 2026-07-17 06:56 | Radomir Dopieralski | Code-Review | +2 | PS6 | Accepted approach, deferred owner check |
| 2026-07-21 11:42 | Jan Jasek | Code-Review | +2 | PS6 | "Works in devstack" |
| 2026-07-21 11:42 | Jan Jasek | Workflow | +1 | PS6 | Final merge approval |
| 2026-07-21 13:48 | Radomir Dopieralski | Code-Review | +2 | PS8 | Re-approved after conflict resolution |
| 2026-07-21 13:48 | Radomir Dopieralski | Workflow | +1 | PS8 | Re-approved after conflict resolution |
| 2026-07-21 16:43 | Zuul | Verified | +2 | PS8 | Gate pipeline — merge |

## Appendix B: Files Changed

| File | Purpose in This Review |
|------|----------------------|
| [`openstack_dashboard/dashboards/project/images/images/tables.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py) | Added `DeactivateImage` and `ReactivateImage` action classes with `policy_rules`, `allowed()` state/owner checks, and `action()` implementations |
| [`openstack_dashboard/dashboards/project/images/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/tests.py) | Unit tests for activate/deactivate row actions |
