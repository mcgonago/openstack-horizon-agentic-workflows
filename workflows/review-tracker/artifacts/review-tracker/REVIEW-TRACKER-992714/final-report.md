# Final Report -- Review 992714: Switch Default Key Pairs Panel from AngularJS to Python

**Review:** [https://review.opendev.org/c/openstack/horizon/+/992714](https://review.opendev.org/c/openstack/horizon/+/992714)
**Author:** Owen McGonagle
**Final Status:** MERGED (2026-07-14 10:57 UTC)
**Total Patchsets:** 13
**Total Duration:** 34 days (2026-06-10 to 2026-07-14)
**Total Comments:** 18 across 7 threads from 4 reviewers
**Tracker:** [tracker-992714.md](./tracker-992714.md)
**Depends-On:** [Review 992902](https://review.opendev.org/c/openstack/horizon/+/992902) (views.py cleanup — merged first)

---

## Executive Summary

This review switched the default Key Pairs panel in OpenStack Horizon from the legacy AngularJS implementation to the native Python/Django implementation. The change itself was small — flipping `ANGULAR_FEATURES['key_pairs_panel']` from `True` to `False` in `defaults.py` — but it represented the completion of a broader de-angularization effort where the Django replacement had been implemented in prior patches. The review also included Selenium test assertion improvements, documentation updates, and a release note.

The review went through three distinct phases: a rapid development iteration (PS1-PS6 over 2 days, achieving first CI pass), a 12-day idle period while WIP, and an active review cycle (PS8-PS13 over 20 days) involving feedback from Jan Jasek, Tatiana Ovchinnikova, Radomir Dopieralski, and Ivan Anfimov. All 4 blocking comment threads were addressed, and the review received two +2 Code-Review votes plus Workflow+1 from Jan Jasek, who confirmed he tested the panel in devstack.

This was the second review tracked end-to-end by the `/review-tracker` skill, and the first to exercise the full lifecycle from initial scan through MERGED status across 9 incremental scans.

---

## Review Timeline

| Date | Day # | Event | Details |
|------|-------|-------|---------|
| 2026-06-10 | 1 | First push | PS1 uploaded, immediately marked Work In Progress |
| 2026-06-10 | 1 | CI failure | PS1 Verified-1 (check pipeline) |
| 2026-06-10 | 1 | PS2 uploaded | REWORK — fixing CI failures |
| 2026-06-10 | 1 | CI failure | PS2 Verified-1 |
| 2026-06-10 | 1 | PS3 uploaded | REWORK — continued CI fixes |
| 2026-06-10 | 1 | CI failure | PS3 Verified-1 |
| 2026-06-11 | 2 | PS4 uploaded | REWORK — continued CI fixes |
| 2026-06-11 | 2 | CI failure | PS4 Verified-1 |
| 2026-06-11 | 2 | PS5 uploaded | REWORK — continued CI fixes |
| 2026-06-11 | 2 | CI failure | PS5 Verified-1 |
| 2026-06-11 | 2 | PS6 uploaded | NO_CODE_CHANGE — commit message update |
| 2026-06-11 | 2 | **First CI pass** | PS6 Verified+1 — first green build |
| 2026-06-11 | 2 | Recheck | Owen triggered recheck on PS6 |
| 2026-06-11 | 2 | CI failure | PS6 Verified-1 (recheck — intermittent) |
| 2026-06-12 | 3 | Recheck | Owen triggered second recheck on PS6 |
| 2026-06-12 | 3 | PS7 uploaded | TRIVIAL_REBASE — rebase on master |
| 2026-06-12 | 3 | CI pass | PS7 Verified+1 |
| 2026-06-12 | 3 | PS8 uploaded | NO_CODE_CHANGE — commit message update |
| 2026-06-12 | 3 | CI pass | PS8 Verified+1 |
| 2026-06-12 | 3 | Recheck | Owen triggered recheck on PS8 |
| 2026-06-24 | 15 | Recheck | Owen rechecked PS8 (after idle period) |
| 2026-06-24 | 15 | Ready for review | Owen marked PS8 ready for review |
| 2026-06-25 | 16 | **First reviewer feedback** | Jan Jasek: Code-Review -1, 2 inline comments on Selenium test assertions |
| 2026-06-26 | 17 | PS9 uploaded | REWORK — addressed Jan's feedback on test assertions |
| 2026-06-26 | 17 | Owen replied "Done" | Responded to both CMT-JAN-1 and CMT-JAN-2 |
| 2026-06-26 | 17 | CI pass | PS9 Verified+1 |
| 2026-06-26 | 17 | **Tracker scan #1** | AI initial scan — 2 threads from 1 reviewer |
| 2026-06-26 | 17 | **Tracker scan #2** | Playwright browser verification — confirmed Jan's finding |
| 2026-06-26 | 17 | **Tracker scan #3** | Recheck — PS9 uploaded, Owen replied "Done" |
| 2026-06-30 | 21 | Tatiana CR-1 | Tatiana Ovchinnikova: Code-Review -1, commit message needs blueprint reference |
| 2026-07-07 | 28 | Owen replied | Clarification questions about blueprint name format |
| 2026-07-07 | 28 | **Tracker scan #4** | Zuul +1 on PS9, new CR-1 from Tatiana |
| 2026-07-07 | 28 | **Tracker scan #5** | Tatiana edited comment, Owen asked follow-up |
| 2026-07-07 | 28 | **Tracker scan #6** | Owen confirmed blueprint name |
| 2026-07-08 | 29 | PS10 uploaded | TRIVIAL_REBASE |
| 2026-07-08 | 29 | PS11 uploaded | TRIVIAL_REBASE + commit message update (added blueprint tag) |
| 2026-07-08 | 29 | Tatiana replied | Confirmed format: short name, no URL |
| 2026-07-08 | 29 | Owen resolved CMT-TAT-1 | Marked thread resolved |
| 2026-07-08 | 29 | Radomir CR+2 | "looks good to me, I didn't test it" |
| 2026-07-08 | 29 | CI failure | PS11 Verified-1 (random timeout) |
| 2026-07-08 | 29 | **Tracker scan #7** | PS10/11 uploaded, CMT-TAT-1 resolved |
| 2026-07-13 | 34 | Radomir recheck | "recheck random timeout" |
| 2026-07-13 | 34 | CI pass | PS11 Verified+1 (recheck succeeded) |
| 2026-07-13 | 34 | Ivan CR+1 | Ivan Anfimov: Code-Review+1 |
| 2026-07-13 | 34 | Tatiana CR-1 | New inline comment: docs deprecation marker needs fixing |
| 2026-07-13 | 34 | PS12 uploaded | TRIVIAL_REBASE |
| 2026-07-13 | 34 | PS13 uploaded | REWORK — fixed docs deprecation markers |
| 2026-07-13 | 34 | Owen replied "Done" | Resolved CMT-TAT-2 |
| 2026-07-13 | 34 | CI pass | PS13 Verified+1 |
| 2026-07-13 | 34 | **Tracker scan #8** | Radomir CR+2, Ivan CR+1, Tatiana CR-1 |
| 2026-07-14 | 35 | Radomir CR+2 | Re-approved on PS13 |
| 2026-07-14 | 35 | **Jan CR+2 + W+1** | "Tested in devstack, code looks good, Thanks!" |
| 2026-07-14 | 35 | Gate pipeline | Zuul gate started |
| 2026-07-14 | 35 | **MERGED** | Gate pipeline succeeded, change merged at 10:57 UTC |
| 2026-07-14 | 35 | **Tracker scan #9** | Final scan — MERGED status |

---

## Patchset History

| PS | Date | Kind | Reason | CI Result |
|----|------|------|--------|-----------|
| 1 | 2026-06-10 16:11 | REWORK | Initial implementation | Verified-1 |
| 2 | 2026-06-10 19:23 | REWORK | Fix CI failures | Verified-1 |
| 3 | 2026-06-10 21:54 | REWORK | Fix CI failures | Verified-1 |
| 4 | 2026-06-11 00:49 | REWORK | Fix CI failures | Verified-1 |
| 5 | 2026-06-11 02:51 | REWORK | Fix CI failures | Verified-1 |
| 6 | 2026-06-11 14:09 | NO_CODE_CHANGE | Commit message update | Verified+1 (first pass) |
| 7 | 2026-06-12 12:31 | TRIVIAL_REBASE | Rebase on master | Verified+1 |
| 8 | 2026-06-12 14:35 | NO_CODE_CHANGE | Commit message update | Verified+1 |
| 9 | 2026-06-26 21:46 | REWORK | Address Jan's Selenium test assertion feedback | Verified+1 |
| 10 | 2026-07-08 13:53 | TRIVIAL_REBASE | Rebase on master | (superseded by PS11) |
| 11 | 2026-07-08 13:58 | REBASE+MSG | Add "Partially-Implements: blueprint removing-angularjs" | Verified+1 (after recheck) |
| 12 | 2026-07-13 20:55 | TRIVIAL_REBASE | Rebase on master | (superseded by PS13) |
| 13 | 2026-07-13 21:12 | REWORK | Fix docs deprecation markers (CMT-TAT-2) | Verified+1 → Verified+2 (gate) |

### Phase Narrative

**Development phase (PS1-PS6, Day 1-2):** Owen pushed the initial implementation and spent ~22 hours iterating through 5 CI failures before achieving the first green build on PS6. This was a high-velocity development cycle — 5 patchsets in under 12 hours — typical for getting a new change through Horizon's comprehensive CI pipeline for the first time.

**Stabilization phase (PS7-PS8, Day 3):** Two quick housekeeping patchsets — a rebase and a commit message update. CI was consistently green at this point.

**Idle period (Day 3-15):** 12 days with no activity. The review was still marked WIP during most of this period. Owen rechecked and marked it ready for review on Day 15.

**First review cycle (PS9, Day 16-17):** Jan Jasek provided the first reviewer feedback on Day 16. Owen addressed both comments within 33 hours by pushing PS9 with improved Selenium test assertions.

**Blueprint cycle (PS10-PS11, Day 28-29):** Tatiana Ovchinnikova requested a blueprint reference in the commit message. After a clarification exchange about the correct format (7.1 days), Owen pushed PS10 (rebase) and PS11 (commit message with blueprint tag). Radomir Dopieralski gave Code-Review+2 the same day.

**Final fix (PS12-PS13, Day 34-35):** Tatiana flagged a docs issue — Owen's patch had replaced the original Zed deprecation marker instead of keeping it alongside a new one. Owen fixed this in PS13 within 2.7 hours. Jan tested in devstack and gave the final CR+2 + W+1 the next morning. Merged at 10:57 UTC on Day 35.

---

## Reviewer Engagement

### Jan Jasek

- **First contact:** 2026-06-25 (Day 16)
- **Role:** Initial reviewer → final approver (CR+2 + W+1)
- **Comments:** 2 inline blocking comments (PS8), 1 patchset-level approval (PS13)
- **Vote history:** CR-1 (PS8) → 0 (cleared by PS9) → CR+2 + W+1 (PS13)
- **Key contribution:** Identified that Selenium test assertions only checked if the keypair name existed anywhere in the message, not the full success/error string. This was independently validated by Playwright browser testing (tracker scan #2).
- **Final action:** Tested the full panel in devstack before approving — "Tested in devstack, code looks good, Thanks!"

### Tatiana Ovchinnikova

- **First contact:** 2026-06-30 (Day 21)
- **Role:** Process and documentation reviewer
- **Comments:** 1 patchset-level blocking (PS9), 1 inline blocking (PS11), plus format guidance replies
- **Vote history:** CR-1 (PS9) → CR-1 (PS11, carried) → cleared by PS13
- **Key contributions:**
  1. Required `Partially-Implements: blueprint removing-angularjs` in commit message — standard OpenStack practice for tracking de-angularization work
  2. Caught that Owen's docs patch replaced the existing Zed deprecation marker instead of keeping it alongside a new Key Pairs marker
- **Notable:** Edited her initial comment to correct the blueprint name ("de-angularize" → "removing-angularjs"), demonstrating attention to accuracy

### Radomir Dopieralski

- **First contact:** 2026-07-08 (Day 29)
- **Role:** Core reviewer (CR+2)
- **Comments:** 1 patchset-level approval (PS11), 1 recheck trigger (PS11)
- **Vote history:** CR+2 (PS11) → CR+2 (PS13, re-approved)
- **Key contribution:** Provided the first +2 vote. Noted "looks good to me, I didn't test it" — honest about review scope. Triggered a recheck after PS11's random CI timeout.

### Ivan Anfimov

- **First contact:** 2026-07-13 (Day 34)
- **Role:** Additional reviewer (CR+1)
- **Comments:** 0 (vote only)
- **Vote history:** CR+1 (PS11, cleared by PS13)
- **Key contribution:** Added a supporting +1 vote

---

## Comment Thread Analysis

| Thread ID | Author | Type | Severity | Posted | Responded | Response Time | Resolution |
|-----------|--------|------|----------|--------|-----------|---------------|------------|
| [CMT-JAN-1](./tracker-992714.md#cmt-jan-1) | Jan Jasek | Inline / Blocking | HIGH | 2026-06-25 12:49 | 2026-06-26 21:48 | 33.0h | PS9 fix — improved assertion to check full success message string |
| [CMT-JAN-2](./tracker-992714.md#cmt-jan-2) | Jan Jasek | Inline / Blocking | HIGH | 2026-06-25 12:49 | 2026-06-26 21:48 | 33.0h | PS9 fix — improved assertion to check full delete message string |
| [CMT-TAT-1](./tracker-992714.md#cmt-tat-1) | Tatiana Ovchinnikova | PL / Blocking | HIGH | 2026-06-30 16:59 | 2026-07-07 20:13 | 171.2h (7.1d) | PS11 fix — added blueprint tag to commit message |
| [CMT-TAT-2](./tracker-992714.md#cmt-tat-2) | Tatiana Ovchinnikova | Inline / Blocking | HIGH | 2026-07-13 18:30 | 2026-07-13 21:15 | 2.7h | PS13 fix — kept Zed deprecation marker, added new Key Pairs marker |
| [CMT-RAD-1](./tracker-992714.md#cmt-rad-1) | Radomir Dopieralski | PL / Informational | LOW | 2026-07-08 15:03 | — | — | No response needed — CR+2 approval comment |
| [CMT-RAD-2](./tracker-992714.md#cmt-rad-2) | Radomir Dopieralski | PL / Informational | LOW | 2026-07-13 15:12 | — | — | No response needed — recheck trigger |
| [CMT-JAN-3](./tracker-992714.md#cmt-jan-3) | Jan Jasek | PL / Informational | LOW | 2026-07-14 09:30 | — | — | No response needed — CR+2 + W+1 approval |

---

## Response Time Metrics

### Comment Response Latency (Blocking Threads Only)

| Metric | Value |
|--------|-------|
| Median response time | 33.0 hours |
| Mean response time | 52.5 hours |
| Fastest response | 2.7 hours (CMT-TAT-2 — docs deprecation fix) |
| Slowest response | 171.2 hours / 7.1 days (CMT-TAT-1 — blueprint tag) |
| Total blocking threads | 4 |
| All resolved | Yes |

### Fix Implementation Velocity

| Thread | Comment Date | Fix Pushed | Elapsed | Patchset | Fix Description |
|--------|-------------|------------|---------|----------|-----------------|
| CMT-JAN-1 | 2026-06-25 12:49 | 2026-06-26 21:46 (PS9) | 33.0h | REWORK | Selenium assertion checks full success message |
| CMT-JAN-2 | 2026-06-25 12:49 | 2026-06-26 21:46 (PS9) | 33.0h | REWORK | Selenium assertion checks full delete message |
| CMT-TAT-1 | 2026-06-30 16:59 | 2026-07-08 13:58 (PS11) | 7.9d | REBASE+MSG | Added blueprint tag to commit message |
| CMT-TAT-2 | 2026-07-13 18:30 | 2026-07-13 21:12 (PS13) | 2.7h | REWORK | Separate deprecation markers for Zed and 2026.2 |

### Response Time Analysis

The 7.1-day response time on CMT-TAT-1 is the significant outlier. This was Tatiana's request for a blueprint reference in the commit message. The delay was partly due to the comment arriving on June 30 (Monday) and Owen not responding until July 7 (following Monday). The response included legitimate clarification questions about the correct blueprint name format (Tatiana had originally written "de-angularize" and later corrected to "removing-angularjs") and whether to include the full URL.

Once clarification was received, Owen pushed PS11 with the fix the same day (July 8). The actual implementation time was < 1 hour — the delay was in the communication cycle.

The CMT-TAT-2 response of 2.7 hours demonstrates the capability for fast turnaround when the request is clear and unambiguous.

---

## CI Performance

### Per-Patchset CI Results

| PS | Upload Time | CI Result | CI Time | Duration | Notes |
|----|------------|-----------|---------|----------|-------|
| 1 | 2026-06-10 16:11 | Verified-1 | 2026-06-10 17:04 | 53 min | Initial failures |
| 2 | 2026-06-10 19:23 | Verified-1 | 2026-06-10 20:05 | 42 min | |
| 3 | 2026-06-10 21:54 | Verified-1 | 2026-06-10 22:59 | 65 min | |
| 4 | 2026-06-11 00:49 | Verified-1 | 2026-06-11 01:53 | 64 min | |
| 5 | 2026-06-11 02:51 | Verified-1 | 2026-06-11 03:45 | 54 min | |
| 6 | 2026-06-11 14:09 | Verified+1 | 2026-06-11 15:44 | 95 min | **First pass** |
| 6r | (recheck) | Verified-1 | 2026-06-11 19:53 | — | Intermittent failure on recheck |
| 7 | 2026-06-12 12:31 | Verified+1 | 2026-06-12 14:06 | 95 min | |
| 8 | 2026-06-12 14:35 | Verified+1 | 2026-06-12 15:38 | 63 min | |
| 9 | 2026-06-26 21:46 | Verified+1 | 2026-06-26 22:48 | 62 min | |
| 11 | 2026-07-08 13:58 | Verified-1 | 2026-07-08 15:05 | 67 min | Random timeout |
| 11r | (recheck) | Verified+1 | 2026-07-13 16:16 | — | Radomir-triggered recheck passed |
| 13 | 2026-07-13 21:12 | Verified+1 | 2026-07-13 22:40 | 88 min | |
| 13g | (gate) | Verified+2 | 2026-07-14 10:57 | 86 min | Gate pipeline — merge |

### CI Summary

| Metric | Value |
|--------|-------|
| Total check pipeline runs | 13 |
| Check passes | 6 (46.2%) |
| Check failures | 7 (53.8%) |
| Gate pipeline runs | 1 |
| Gate passes | 1 (100%) |
| Rechecks triggered | 4 (by Owen: 3, by Radomir: 1) |
| Average build time (check) | ~68 minutes |
| Development CI failures (PS1-PS5) | 5 consecutive |
| Post-development CI failures | 2 (1 intermittent recheck, 1 random timeout) |

### CI Analysis

The 46.2% check pass rate looks concerning at face value, but context matters. The 5 consecutive failures on PS1-PS5 were during initial development — Owen was iterating on the implementation to get it through Horizon's CI pipeline. This is a normal development pattern for a first-time contribution to a panel with complex test dependencies.

After PS6 achieved the first green build, the CI pass rate for subsequent *new* patchsets was 5/6 (83.3%). The two post-development failures were:
1. PS6 recheck: intermittent failure (not reproducible — likely infrastructure)
2. PS11: random timeout (confirmed by Radomir's "recheck random timeout" comment — infrastructure issue)

Neither post-development failure was caused by code defects.

---

## Code Evolution Metrics

| Metric | Value |
|--------|-------|
| Total patchsets | 13 |
| REWORK (code changes) | 7 (PS1-5, PS9, PS13) |
| TRIVIAL_REBASE | 3 (PS7, PS10, PS12) |
| NO_CODE_CHANGE (commit msg only) | 2 (PS6, PS8) |
| REBASE + message update | 1 (PS11) |
| Development iterations (PS1-PS6) | 6 (5 failures + first pass) |
| Post-review iterations (PS9-PS13) | 5 (addressing 4 threads across 2 reviewers) |
| Longest patchset gap | 14 days 7 hours (PS8 → PS9) |
| Second longest gap | 11 days 16 hours (PS9 → PS10) |
| Shortest patchset gap | 5 minutes (PS10 → PS11) |

### Evolution Analysis

The 13 patchsets break down into a clear pattern:
- **45% were code changes** (REWORK) — the actual development and review fixes
- **31% were rebases** — keeping the change current with master during the 34-day lifecycle
- **23% were commit message updates** — formatting and adding the blueprint reference

The high rebase count (4 total) reflects the long review cycle. Each time the review sat idle for more than a week, a rebase was needed before the next CI run.

---

## AI-Assisted Tracking Summary

This review was tracked by the `/review-tracker` skill across **9 scans** over **19 days** (2026-06-26 to 2026-07-14).

### Scan History

| # | Date | Key Finding |
|---|------|-------------|
| 1 | 2026-06-26 | Initial scan — 2 comment threads from Jan Jasek, 4 recheck comments |
| 2 | 2026-06-26 | Playwright browser verification — confirmed Jan's assertion finding (T2 fail, T3 pass) |
| 3 | 2026-06-26 | Recheck — PS9 uploaded, Owen replied "Done" to both threads |
| 4 | 2026-07-07 | Recheck — Zuul Verified+1 on PS9, new Code-Review -1 from Tatiana |
| 5 | 2026-07-07 | Recheck — Tatiana edited comment, Owen asked clarification |
| 6 | 2026-07-07 | Recheck — Owen confirmed he sees corrected blueprint name |
| 7 | 2026-07-08 | Recheck — PS10/11 uploaded, CMT-TAT-1 resolved, Radomir CR+2 |
| 8 | 2026-07-13 | Recheck — Zuul +1, Radomir +2, Ivan +1, new Tatiana CR-1 (docs) |
| 9 | 2026-07-14 | Recheck — **MERGED**. All threads resolved. |

### Tracker Capabilities Exercised

| Capability | Used | Details |
|------------|------|---------|
| Initial scan | Yes | Full comment thread analysis and classification |
| Incremental recheck | Yes | 8 rechecks with change detection |
| Early exit (no changes) | No | Every recheck found new activity |
| Playwright browser verification | Yes | 4 tests (3 pass, 1 fail — validated Jan's finding) |
| Deep-dive bridge analysis | No | Not requested for this review |
| Create-patch automation | No | Not used |
| Verify-patch tox testing | No | Not used |
| Dashboard publishing | Yes | Published across 17 runs |
| Final report | Yes | This document |

### Value Delivered

1. **Independent validation of reviewer feedback:** Playwright browser testing (scan #2) independently confirmed Jan's concern about the Selenium test assertion — the create-keypair flow genuinely produced an empty success message. This strengthened the case for the fix.

2. **Structured "What Needs to Change" guidance:** Each blocking comment was translated into specific, code-level fix instructions with before/after snippets, reducing ambiguity in the required changes.

3. **Continuous status awareness:** 9 scans across 19 days meant the developer always had an up-to-date picture of what needed attention, without manually re-reading Gerrit comment threads.

4. **Merge readiness tracking:** The "Key Remaining Items" table provided a clear checklist of what was still needed, updated automatically on each recheck.

---

## Key Milestones

| Milestone | Date | Day # | Elapsed Since Previous |
|-----------|------|-------|------------------------|
| First push (PS1) | 2026-06-10 16:11 | 1 | — |
| First CI pass (PS6) | 2026-06-11 15:44 | 2 | 23h 33m |
| Marked ready for review | 2026-06-24 14:03 | 15 | 12d 22h |
| First reviewer feedback (Jan CR-1) | 2026-06-25 12:49 | 16 | 22h 46m |
| All initial feedback addressed (PS9) | 2026-06-26 21:46 | 17 | 32h 57m |
| Second reviewer feedback (Tatiana CR-1) | 2026-06-30 16:59 | 21 | 3d 19h |
| Blueprint tag added (PS11) | 2026-07-08 13:58 | 29 | 7d 21h |
| First +2 vote (Radomir) | 2026-07-08 15:03 | 29 | 1h 5m |
| Docs fix pushed (PS13) | 2026-07-13 21:12 | 34 | 5d 6h |
| Final approval (Jan CR+2 + W+1) | 2026-07-14 09:30 | 35 | 12h 18m |
| **MERGED** | 2026-07-14 10:57 | 35 | 1h 27m (gate pipeline) |

### Phase Durations

| Phase | Start | End | Duration |
|-------|-------|-----|----------|
| Development (PS1 → first CI pass) | Day 1 | Day 2 | 23.5 hours |
| Idle / WIP | Day 3 | Day 15 | 12 days |
| Review wait (ready → first feedback) | Day 15 | Day 16 | 23 hours |
| First review cycle (Jan's feedback → fix) | Day 16 | Day 17 | 33 hours |
| Second review cycle (Tatiana's feedback → fix) | Day 21 | Day 29 | 8 days |
| Final review cycle (docs fix → merge) | Day 34 | Day 35 | 16 hours |
| **Total wall-clock** | Day 1 | Day 35 | **34 days** |
| **Active work time (excluding idle)** | — | — | **~22 days** |

---

## Lessons Learned

### What Went Well

1. **Fast initial development cycle:** 5 patchsets in 12 hours to work through CI failures, followed by first green build. This rapid iteration showed persistent debugging rather than abandoning the approach.

2. **Quick response to Jan's feedback (33h):** Owen addressed both Selenium test assertion comments within 33 hours, including writing improved test assertions that check the full success/error message string — not just the keypair name.

3. **Same-day turnaround on docs fix (2.7h):** When Tatiana flagged the deprecation marker issue on Day 34, Owen pushed the fix within 2.7 hours. This fast turnaround on the final blocking issue enabled the merge the next morning.

4. **Reviewer diversity:** 4 different reviewers participated, each bringing different perspectives — Jan on testing quality, Tatiana on process/documentation, Radomir on code quality, Ivan as an additional reviewer. Jan's final approval included actual devstack testing.

5. **AI-assisted tracking:** The `/review-tracker` skill provided continuous visibility into the review state, with Playwright browser testing independently validating a reviewer's concern. The "What Needs to Change" section gave concrete, actionable fix guidance.

### What Could Improve

1. **7-day response gap on CMT-TAT-1:** Tatiana's comment on June 30 was not addressed until July 7. While some of this was due to legitimate clarification needs (the blueprint name was initially incorrect), a quicker initial response — even acknowledging the comment and asking questions sooner — would have shortened the review cycle by up to a week.

2. **5 consecutive CI failures (PS1-PS5):** Five failures before the first green build suggests the initial development may have benefited from running `tox -e pep8` and `tox -e py311` locally before each push. While CI iteration is normal, reducing the failure count would project more confidence to reviewers.

3. **12-day idle period (Day 3-15):** The review sat WIP for nearly two weeks after CI was green. While there may have been valid reasons (waiting for the dependency review 992902 to progress, other priorities), this idle time added 12 days to the total review lifecycle.

4. **Patchset proliferation from rebases:** 4 of 13 patchsets were rebases. This is a consequence of the long review cycle — the longer a review stays open, the more rebases are needed. Reducing the overall cycle time would reduce the rebase count.

### Patterns to Repeat

1. **Address blocking comments with a dedicated patchset** — PS9 addressed Jan's feedback cleanly, PS13 addressed Tatiana's docs issue cleanly. Each fix was focused and easy for the reviewer to verify.

2. **Use Playwright/browser testing to validate reviewer concerns** — independently confirming Jan's finding about the empty success message strengthened the fix and showed thoroughness.

3. **Track the review with `/review-tracker`** — the living document provided structure through a 34-day review cycle with multiple rounds of feedback. Without it, tracking the state across 13 patchsets and 4 reviewers would have been significantly harder.

4. **Push the fix and reply in the same session** — every time Owen addressed a comment, he both pushed the fix patchset and replied "Done" on the thread. This gives the reviewer a clear signal that the feedback was addressed.

---

## Appendix A: Vote History

| Date | Voter | Label | Value | Patchset | Notes |
|------|-------|-------|-------|----------|-------|
| 2026-06-25 12:49 | Jan Jasek | Code-Review | -1 | PS8 | Two inline comments on Selenium tests |
| 2026-06-30 16:59 | Tatiana Ovchinnikova | Code-Review | -1 | PS9 | Commit message needs blueprint reference |
| 2026-07-08 13:59 | Tatiana Ovchinnikova | Code-Review | -1 | PS10 | Carried from PS9 (blueprint not yet added) |
| 2026-07-08 15:03 | Radomir Dopieralski | Code-Review | +2 | PS11 | "looks good to me, I didn't test it" |
| 2026-07-13 17:03 | Ivan Anfimov | Code-Review | +1 | PS11 | |
| 2026-07-13 18:30 | Tatiana Ovchinnikova | Code-Review | -1 | PS11 | Docs deprecation marker issue |
| 2026-07-14 07:22 | Radomir Dopieralski | Code-Review | +2 | PS13 | Re-approved |
| 2026-07-14 09:30 | Jan Jasek | Code-Review | +2 | PS13 | "Tested in devstack" |
| 2026-07-14 09:30 | Jan Jasek | Workflow | +1 | PS13 | Final merge approval |

## Appendix B: Files Changed

| File | Purpose in This Review |
|------|----------------------|
| [`openstack_dashboard/defaults.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/defaults.py) | Flip `ANGULAR_FEATURES['key_pairs_panel']` from `True` to `False` |
| [`openstack_dashboard/dashboards/project/key_pairs/views.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/key_pairs/views.py) | Views cleanup for Django panel |
| [`openstack_dashboard/test/selenium/integration/test_keypairs.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/test/selenium/integration/test_keypairs.py) | Improved Selenium test assertions per Jan's feedback |
| [`doc/source/configuration/settings.rst`](https://github.com/openstack/horizon/blob/master/doc/source/configuration/settings.rst) | Deprecation markers for ANGULAR_FEATURES |
| [`releasenotes/notes/`](https://github.com/openstack/horizon/tree/master/releasenotes/notes) | Release note for the default switch |
