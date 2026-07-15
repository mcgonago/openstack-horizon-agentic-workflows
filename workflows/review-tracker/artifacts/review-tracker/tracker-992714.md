# Review 992714 — Live Comment Tracker

**Review:** [https://review.opendev.org/c/openstack/horizon/+/992714](https://review.opendev.org/c/openstack/horizon/+/992714)
**Title:** Switch default Key Pairs panel from AngularJS to Python
**Author:** Owen McGonagle
**Status:** MERGED (2026-07-14 10:57 UTC)
**Current Patchset:** 13
**Zuul:** Verified+2 (PS13 — gate pipeline succeeded 2026-07-14)
**Files Changed:** 5 (defaults.py toggle, views.py cleanup, Selenium test update, docs, reno)
**Reviewers:** Jan Jasek, Tatiana Ovchinnikova, Radomir Dopieralski, Ivan Anfimov

---

## Scan Log

| # | Date | Scanner | Notes |
|---|------|---------|-------|
| 1 | 2026-06-26 | AI (Claude) | Initial scan — 2 comment threads from 1 reviewer, 4 recheck comments |
| 2 | 2026-06-26 | AI (Claude) + Playwright | Playwright browser verification — 3 PASS, 1 FAIL (T2 is a real finding) |
| 3 | 2026-06-26 | AI (Claude) | Recheck — PS9 uploaded, Owen replied "Done" to both threads, all votes reset |
| 4 | 2026-07-07 | AI (Claude) | Recheck — Zuul Verified+1 on PS9, NEW Code-Review -1 from Tatiana (commit message update needed) |
| 5 | 2026-07-07 | AI (Claude) | Recheck — Tatiana edited CMT-TAT-1 (corrected blueprint name), Owen replied with clarification questions |
| 6 | 2026-07-07 | AI (Claude) | Recheck — Owen added follow-up: confirms he sees corrected name, asks URL vs name-only format |
| 7 | 2026-07-08 | AI (Claude) | Recheck — PS10/11 uploaded with blueprint tag, Tatiana answered format questions, CMT-TAT-1 RESOLVED |
| 8 | 2026-07-13 | AI (Claude) | Recheck — Zuul Verified+1 PS11, Radomir CR+2, Ivan CR+1, NEW Tatiana CR-1 (docs deprecation marker on settings.rst) |
| 9 | 2026-07-14 | AI (Claude) | Recheck — **MERGED.** Owen fixed docs (PS13), CMT-TAT-2 RESOLVED. Jan CR+2 + W+1 ("Tested in devstack"). Radomir re-approved CR+2. Gate passed, merged 2026-07-14 10:57 UTC. |

---

## What Needs to Change

### Scan #8 — 2026-07-13

~~**[CMT-TAT-2](#cmt-tat-2): Update deprecation marker in settings.rst — keep existing marker, add new one for Key Pairs — RESOLVED in PS13**~~

- ~~**File:** `doc/source/configuration/settings.rst:48`~~
- ~~**Status:** RESOLVED — Owen pushed PS13 with the fix (separate deprecation markers for Zed and 2026.2), replied "Done" to Tatiana's thread~~

---

### Scan #4 — 2026-07-07

~~**[CMT-TAT-1](#cmt-tat-1): Add "Partially-Implements: blueprint removing-angularjs" — RESOLVED in PS11**~~

- ~~**File:** `/COMMIT_MSG`~~
- ~~**Status:** RESOLVED — Owen pushed PS11 with `Partially-Implements: blueprint removing-angularjs` (short name format, no URL)~~
- ~~**Tatiana's guidance:** Use short name only, no URL; Gerrit topic `de-angularize` can stay (it's shorter/clearer)~~

---

### Scan #1 — 2026-06-26

~~**[CMT-JAN-1](#cmt-jan-1): Selenium test asserts keypair name exists anywhere in message — should assert the full success/error string**~~

- ~~**File:** `openstack_dashboard/test/selenium/integration/test_keypairs.py:61`~~
- ~~**Status:** RESOLVED — Owen replied "Done" and pushed PS9 with the fix~~

~~**[CMT-JAN-2](#cmt-jan-2): Same issue on the delete test assertion (line 82)**~~

- ~~**File:** `openstack_dashboard/test/selenium/integration/test_keypairs.py:82`~~
- ~~**Status:** RESOLVED — Owen replied "Done" and pushed PS9 with the fix~~

---

## Change Log

### Scan #9 — 2026-07-14

1. **UPDATED** [Header](#): Status NEW → **MERGED** (2026-07-14 10:57 UTC)
2. **UPDATED** [Header](#): Current Patchset 11 → 13 (PS12 rebase, PS13 docs deprecation fix)
3. **UPDATED** [Header](#): Zuul Verified+1 → Verified+2 (gate pipeline succeeded)
4. **UPDATED** [Score Summary](#score-summary): Jan CR+2 + W+1, Radomir re-approved CR+2, Tatiana -1 cleared by PS13
5. **UPDATED** [CMT-TAT-2](#cmt-tat-2): Owen replied "Done" (PS13) — status → RESOLVED (unresolved: false)
6. **NEW** [CMT-JAN-3](#cmt-jan-3): Jan's "Tested in devstack, code looks good, Thanks!" + CR+2 + W+1
7. **UPDATED** [What Needs to Change](#what-needs-to-change): Scan #8 CMT-TAT-2 entry struck through (docs fix pushed in PS13)
8. **UPDATED** [Key Remaining Items](#key-remaining-items): All items RESOLVED — review merged
9. **UPDATED** [Open Threads](#open-threads-requiring-attention): Table empty — no open threads remain
10. **UPDATED** [Comment Statistics](#comment-statistics): Owen 11 (+1 "Done"), Jan 3 (+1 "Tested in devstack")

### Scan #8 — 2026-07-13

1. **UPDATED** [Header](#): Zuul Pending → Verified+1 (PS11 build succeeded 2026-07-13)
2. **UPDATED** [Header](#): Reviewers — added Radomir Dopieralski, Ivan Anfimov
3. **UPDATED** [Score Summary](#score-summary): Radomir Code-Review+2, Ivan Code-Review+1, Tatiana Code-Review -1 (new)
4. **NEW** [CMT-RAD-1](#cmt-rad-1): Radomir's Code-Review+2 with "looks good to me, I didn't test it"
5. **NEW** [CMT-RAD-2](#cmt-rad-2): Radomir's "recheck random timeout" (triggered CI rerun)
6. **NEW** [CMT-TAT-2](#cmt-tat-2): Tatiana's inline comment on `settings.rst:48` — keep existing deprecation marker, add new one for Key Pairs
7. **UPDATED** [What Needs to Change](#what-needs-to-change): Added Scan #8 entry for docs deprecation marker fix
8. **UPDATED** [Key Remaining Items](#key-remaining-items): Zuul CI ~~OPEN~~ → PASS, added docs deprecation marker and Tatiana's new -1
9. **UPDATED** [Open Threads](#open-threads-requiring-attention): CMT-TAT-2 added (inline, HIGH priority)
10. **UPDATED** [Comment Statistics](#comment-statistics): Radomir 2 total (new), Tatiana 4 total (+1 inline), Ivan 0 (vote only)

### Scan #7 — 2026-07-08

1. **UPDATED** [Header](#): Current Patchset 9 → 11 (PS10 rebase, PS11 commit message update)
2. **UPDATED** [Header](#): Zuul Verified+1 → Pending (PS11 not yet voted)
3. **UPDATED** [Score Summary](#score-summary): All votes reset to 0 (Verified+1 outdated by PS10, Code-Review -1 outdated by PS11)
4. **UPDATED** [CMT-TAT-1](#cmt-tat-1): Tatiana answered format questions — short name only (no URL), topic can stay `de-angularize`
5. **UPDATED** [CMT-TAT-1](#cmt-tat-1): Owen pushed PS11 with `Partially-Implements: blueprint removing-angularjs` and marked thread resolved
6. **UPDATED** [CMT-TAT-1](#cmt-tat-1): Thread status → RESOLVED (unresolved: false)
7. **UPDATED** [What Needs to Change](#what-needs-to-change): Scan #4 entry struck through (blueprint tag added in PS11)
8. **UPDATED** [Key Remaining Items](#key-remaining-items): Blueprint tag and Tatiana's -1 resolved; now awaiting Zuul and re-reviews
9. **UPDATED** [Open Threads](#open-threads-requiring-attention): CMT-TAT-1 removed (resolved)
10. **UPDATED** [Comment Statistics](#comment-statistics): Owen 10 total (+2 replies), Tatiana 3 total (+2 format guidance replies)

### Scan #6 — 2026-07-07

1. **UPDATED** [CMT-TAT-1](#cmt-tat-1): Owen added follow-up reply — confirms he now sees Tatiana's corrected "removing-angularjs" and simplifies question to just URL format
2. **UPDATED** [Comment Statistics](#comment-statistics): Owen 8 total (+1 follow-up clarification)

### Scan #5 — 2026-07-07

1. **UPDATED** [CMT-TAT-1](#cmt-tat-1): Tatiana **edited her comment** — changed "blueprint de-angularize" → "blueprint removing-angularjs"
2. **UPDATED** [CMT-TAT-1](#cmt-tat-1): Owen replied with clarification questions about blueprint name format, URL inclusion, and Gerrit topic naming
3. **UPDATED** [CMT-TAT-1](#cmt-tat-1): Thread status → NEEDS TATIANA'S RESPONSE (Owen's questions are unresolved)
4. **UPDATED** [What Needs to Change](#what-needs-to-change): Updated Scan #4 entry to reflect Tatiana's corrected blueprint name
5. **UPDATED** [Comment Statistics](#comment-statistics): Owen 7 total (+1 clarification reply)

### Scan #4 — 2026-07-07

1. **UPDATED** [Header](#): Zuul Pending → Verified+1 (PS9 build succeeded 2026-06-26)
2. **UPDATED** [Header](#): Reviewers — added Tatiana Ovchinnikova
3. **UPDATED** [Score Summary](#score-summary): Zuul Verified+1 on PS9, Tatiana Code-Review -1
4. **NEW** [CMT-TAT-1](#cmt-tat-1): Tatiana requests commit message update with "Partially-Implements: blueprint de-angularize"
5. **UPDATED** [What Needs to Change](#what-needs-to-change): Added Scan #4 entry for commit message update
6. **UPDATED** [Key Remaining Items](#key-remaining-items): ~~Zuul CI~~ resolved, added commit message update and Tatiana's -1
7. **UPDATED** [Comment Statistics](#comment-statistics): Tatiana 1 total (new), Owen 6 total (unchanged)
8. **UPDATED** [Open Threads](#open-threads-requiring-attention): CMT-TAT-1 added (patchset-level, HIGH priority)

### Scan #3 — 2026-06-26

1. **UPDATED** Header: Current Patchset 8 → 9, Zuul → Pending (PS9 not yet voted)
2. **UPDATED** [Score Summary](#score-summary): All votes reset to 0 — Jan's Code-Review -1 cleared by PS9
3. **UPDATED** [CMT-JAN-1](#cmt-jan-1): Owen replied "Done" (PS9) — status → RESOLVED
4. **UPDATED** [CMT-JAN-2](#cmt-jan-2): Owen replied "Done" (PS9) — status → RESOLVED
5. **UPDATED** [What Needs to Change](#what-needs-to-change): Both entries struck through (fixes pushed in PS9)
6. **UPDATED** [Key Remaining Items](#key-remaining-items): Test assertion fixes and Jan's -1 resolved
7. **UPDATED** [Comment Statistics](#comment-statistics): Owen 6 total (+2 "Done" replies)

### Scan #2 — 2026-06-26

1. **NEW** [Playwright Verification Results](#playwright-results): Browser testing confirms T2 finding — create-keypair success message is empty (validates CMT-JAN-1)
2. **UPDATED** [CMT-JAN-1](#cmt-jan-1): Playwright T2 independently confirms the missing success message Jan flagged
3. **UPDATED** [CMT-JAN-2](#cmt-jan-2): Playwright T3 confirms the delete message works correctly ("Success: Deleted Key Pair: verify-pw-test")
4. **UPDATED** [Key Remaining Items](#key-remaining-items): Added Playwright verification evidence

---

## Where Things Are At / What To Do Next

### Overall Status

This is a de-angularize patch (topic: `de-angularize`) that flips the `key_pairs_panel` default from `True` (Angular) to `False` (Django) in `defaults.py`. The Django replacement was already implemented in prior patches — this change switches the default and cleans up. PS1–PS5 had CI failures; PS6 got the first Verified+1. PS7 was a rebase, PS8 a commit message update. CI has been green since PS6.

The review sat idle from June 12–24, was marked ready for review on June 24, and received Jan Jasek's first review on June 25 with Code-Review -1 and two inline comments on the Selenium test assertions. Owen addressed both comments in PS9 (pushed 2026-06-26) and replied "Done" to both threads. Jan's Code-Review -1 was cleared by the new patchset.

**Latest developments (as of Scan #9 — 2026-07-14):**
- **Owen pushed PS12** (2026-07-13) — rebase
- **Owen pushed PS13** (2026-07-13) — docs deprecation fix (separate markers for Zed and 2026.2), replied "Done" to CMT-TAT-2
- **Zuul Verified+1** (2026-07-13) — PS13 check pipeline succeeded
- **Radomir Dopieralski Code-Review+2** (2026-07-14) — re-approved on PS13
- **Jan Jasek Code-Review+2 + Workflow+1** (2026-07-14) — "Tested in devstack, code looks good, Thanks!"
- **Zuul Verified+2** (2026-07-14) — gate pipeline succeeded
- **MERGED** (2026-07-14 10:57 UTC) — change successfully merged

**Timeline to merge:** First submitted 2026-05-28, first reviewer feedback 2026-06-25 (Jan), 13 patchsets, merged 2026-07-14 — 47 days total, 19 days from first review feedback to merge.

<a name="score-summary"></a>

### Score Summary (Final — at merge)

| Label | Voter | Value |
|-------|-------|-------|
| Verified | Zuul | +2 (PS13 gate pipeline succeeded 2026-07-14) |
| Code-Review | Radomir Dopieralski | +2 (2026-07-14, re-approved on PS13) |
| Code-Review | Jan Jasek | +2 (2026-07-14, "Tested in devstack") |
| Code-Review | Ivan Anfimov | +1 (2026-07-13, vote on PS11, cleared by PS13) |
| Code-Review | Tatiana Ovchinnikova | -1 (2026-07-13, vote on PS11, cleared by PS13) |
| Workflow | Jan Jasek | +1 (2026-07-14) |

### Review Complete

This review has been **MERGED**. All comment threads are resolved. No further action needed.

**Post-merge follow-up:**
1. **Track progress on the blueprint** — Tatiana suggested Owen could "take care of the BP" by adding his patches to [https://blueprints.launchpad.net/horizon/+spec/removing-angularjs](https://blueprints.launchpad.net/horizon/+spec/removing-angularjs) and tracking progress there.

### Open Threads Requiring Attention

*None — all threads resolved, review merged.*

---

## Patchset-Level Comments

<a name="cmt-tat-1"></a>

### CMT-TAT-1 — Add blueprint reference to commit message — RESOLVED

**Author:** Tatiana Ovchinnikova | **File:** /PATCHSET_LEVEL | **PS:** 9

> Thank you for the patch! Let's start tracking this initiative properly: please add the following line into the commit message:
> 
> Partially-Implements: blueprint removing-angularjs
> 
> -1 to just mark it as an action item

**Reply (Owen McGonagle, 2026-07-07 20:13):**
> I found the blueprint at
> https://blueprints.launchpad.net/horizon/+spec/removing-angularjs
> 
> I think we need to use removing-angularjs instead of de-angularize?
> Partially-Implements: blueprint removing-angularjs
> 
> Should we include the full url:
> Partially-Implements: blueprint https://blueprints.launchpad.net/horizon/+spec/removing-angularjs
> 
> Should we change the Gerrit topic to match the launchpad blueprint name of removing-angularjs? or
> is it ok to have different names?

**Follow-up (Owen McGonagle, 2026-07-07 20:20):**
> I am not sure what I viewed before - but I now see you put in the correct name you have as 'removing-angularjs'
> 
> Do we put in the url, or the name is good enough>

**Reply (Tatiana Ovchinnikova, 2026-07-08 13:59):**
> Hey, the topic can stay, "de-angularize" is shorter and clearer. The idea is to track all the deangularization activity in a blueprint, which you just add to your commit message.

**Reply (Owen McGonagle, 2026-07-08 13:59):**
> I went without the url - marking this as resolved, thank you for catching this...

**Reply (Tatiana Ovchinnikova, 2026-07-08 14:03):**
> That's a standard way, I'm not sure the url will work in the commit message, actually. Also, if you could take care of the BP, that would be great :) You could add your patches there as well and track the progress.

**AI Assessment:** This thread is now **RESOLVED** (unresolved: false). Owen pushed PS11 on 2026-07-08 with the commit message updated to include `Partially-Implements: blueprint removing-angularjs` (short name format, no URL). Tatiana confirmed this is the standard format and noted the URL might not work in commit messages. She also confirmed the Gerrit topic `de-angularize` can stay as-is (it's shorter and clearer than `removing-angularjs`).

**What changed in PS11:**

The commit message now includes:
```
Depends-On: https://review.opendev.org/c/openstack/horizon/+/992902
Partially-Implements: blueprint removing-angularjs
Change-Id: I7eba0c58d853bdbf8730bbe07bbd347b9458245b
Signed-off-by: Owen McGonagle <omcgonag@redhat.com>
```

This properly tracks the de-angularization work in the Launchpad blueprint: https://blueprints.launchpad.net/horizon/+spec/removing-angularjs

**Tatiana's suggestion:** Owen could "take care of the BP" by adding his patches to the blueprint and tracking progress there. This would help coordinate the broader removing-angularjs initiative across the team.

**Status for Owen:** ~~No action needed — resolved.~~ Wait for Tatiana's re-review to confirm the blueprint tag is correct and clear her -1.

---

<a name="cmt-rad-1"></a>

### CMT-RAD-1 — Code-Review+2: "looks good to me" — RESOLVED

**Author:** Radomir Dopieralski | **File:** /PATCHSET_LEVEL | **PS:** 11

> looks good to me, I didn't test it

**AI Assessment:** This is an **INFORMATIONAL** comment accompanying Radomir's Code-Review+2 vote. He reviewed the code and approved it but notes he didn't test the Key Pairs panel in a browser. This is a positive signal — one of the two required +2 votes is now in place.

**Status for Owen:** No action needed — this is a +2 approval.

---

<a name="cmt-rad-2"></a>

### CMT-RAD-2 — Recheck random timeout — RESOLVED

**Author:** Radomir Dopieralski | **File:** /PATCHSET_LEVEL | **PS:** 11

> recheck random timeout

**AI Assessment:** Radomir triggered a CI recheck after PS11's initial Zuul build failed with a random timeout. The recheck succeeded — Zuul Verified+1 on 2026-07-13.

**Status for Owen:** No action needed — CI is green.

---

### CMT-OWN-1 — Recheck (PS6) — RESOLVED

**Author:** Owen McGonagle | **File:** /PATCHSET_LEVEL | **PS:** 6

> recheck

**AI Assessment:** Routine CI recheck. No action needed.

**Status for Owen:** No action needed.

---

### CMT-OWN-2 — Recheck (PS6) — RESOLVED

**Author:** Owen McGonagle | **File:** /PATCHSET_LEVEL | **PS:** 6

> recheck

**AI Assessment:** Second recheck on PS6 after CI failure. No action needed.

**Status for Owen:** No action needed.

---

### CMT-OWN-3 — Recheck (PS8) — RESOLVED

**Author:** Owen McGonagle | **File:** /PATCHSET_LEVEL | **PS:** 8

> recheck

**AI Assessment:** Routine CI recheck on PS8. No action needed.

**Status for Owen:** No action needed.

---

### CMT-OWN-4 — Recheck (PS8) — RESOLVED

**Author:** Owen McGonagle | **File:** /PATCHSET_LEVEL | **PS:** 8

> recheck

**AI Assessment:** Second recheck on PS8 (likely after marking ready for review). No action needed.

**Status for Owen:** No action needed.

---

<a name="cmt-jan-3"></a>

### CMT-JAN-3 — Tested in devstack, code looks good — RESOLVED

**Author:** Jan Jasek | **File:** /PATCHSET_LEVEL | **PS:** 13

> Tested in devstack, code looks good, Thanks!

**AI Assessment:** This is Jan's **final approval** comment accompanying his Code-Review+2 and Workflow+1 votes. He confirmed he tested the Key Pairs panel in a devstack environment — this goes beyond just code reading (note Radomir's earlier +2 explicitly said "I didn't test it"). Jan's Workflow+1 was the final gate that sent the change to Zuul's gate pipeline for merge.

**Status for Owen:** No action needed — this was the merge-enabling vote.

---

## Inline Comments — Tatiana Ovchinnikova

<a name="cmt-tat-2"></a>

### CMT-TAT-2 — Settings.rst deprecation marker structure — RESOLVED

**Author:** Tatiana Ovchinnikova | **File:** [`doc/source/configuration/settings.rst:48`](https://github.com/openstack/horizon/blob/master/doc/source/configuration/settings.rst#L48) | **PS:** 11

> This should be changed as well. Since we only switch Key Pairs to Django, probably we should keep this marker and add a new one for Key Pairs?

**Reply (Owen McGonagle, PS13):**
> Done

**AI Assessment:** This was a **blocking** comment (accompanied Code-Review -1). Tatiana pointed out that Owen's patch replaced the entire Zed-era `.. deprecated:: 22.2.0(Zed)` block — which covered `images_panel` and `roles_panel` — with new text that only talked about Key Pairs. Owen fixed this in PS13 by keeping the original Zed deprecation marker and adding a separate `.. deprecated:: 2026.2` marker for Key Pairs. The thread is now resolved (`unresolved: false`).

**Status for Owen:** ~~No action needed — resolved. Review merged.~~

---

## Inline Comments — Jan Jasek

<a name="cmt-jan-1"></a>

### CMT-JAN-1 — Selenium test assertion method — RESOLVED

**Author:** Jan Jasek | **File:** `openstack_dashboard/test/selenium/integration/test_keypairs.py:61` | **PS:** 8

> Hi @omcgonag@redhat.com,
> Your current implementation just checks if the name is existing in the message and it does not care in what context it is there.
> So if the message will be:
> ```
> Success: Deleted Key Pair: lalala - test pass
> Error: Unable to delete key pair: lalala - test pass
> ```
> Etc…
>
> I would definitely prefer to stay with the current implementation, just with modified messages for Django message output.

**Reply (Owen McGonagle, PS9):**
> Done

**AI Assessment:** This was a **blocking** comment (accompanied Code-Review -1). Jan pointed out that the test only checked whether the keypair name appeared somewhere in the notification message, which would pass even on error messages. Owen addressed this in PS9 by updating the assertion to check the full success message string: `f'Success: Successfully created key pair "{keypair_name}". Your private key is ready for download.'`. The thread is now resolved (`unresolved: false`).

**Status for Owen:** ~~No action needed — resolved.~~ Wait for Jan's re-review of PS9.

---

<a name="cmt-jan-2"></a>

### CMT-JAN-2 — Same assertion issue (second location) — RESOLVED

**Author:** Jan Jasek | **File:** `openstack_dashboard/test/selenium/integration/test_keypairs.py:82` | **PS:** 8

> ditto

**Reply (Owen McGonagle, PS9):**
> Done

**AI Assessment:** This was the same concern as [CMT-JAN-1](#cmt-jan-1) applied to a second test assertion at line 82. Owen addressed this in PS9 by updating the assertion to check the full delete message string: `f"Success: Deleted Key Pair: {new_keypair_demo.name}"`. The thread is now resolved (`unresolved: false`).

**Status for Owen:** ~~No action needed — resolved.~~ Wait for Jan's re-review of PS9.

---

<a name="playwright-results"></a>

## Playwright Verification Results (Scan #2 — 2026-06-26)

**Method:** Playwright browser testing against a live dev server (`tox -e runserver -- 0.0.0.0:9000`) running review 992714 PS8 code on the `horizon-devstack` VM, with `ANGULAR_FEATURES = {'key_pairs_panel': False}`.

| Test | Description | Result | Evidence |
|------|-------------|--------|----------|
| T0_login | Login as admin | **PASS** | Redirected to `/project/`, screenshot `001_login_ok.png` |
| T1_panel_loads | Navigate to `/project/key_pairs/` | **PASS** | Django panel rendered with DataTable, screenshot `002_keypairs_panel.png` |
| T2_create_message | Create keypair, check for success message | **FAIL** | Keypair created (visible in table) but success message banner is **empty** — screenshot `003_create_done.png` |
| T3_delete_message | Delete keypair, check for success message | **PASS** | Green banner: "Success: Deleted Key Pair: verify-pw-test" — screenshot `004_delete_done.png` |

### T2 Failure Analysis — Real Finding

The T2 failure is **not** a test infrastructure issue. The Playwright test:

1. Clicked "Create Key Pair"
2. Entered name `verify-pw-test`, selected SSH type
3. Submitted the form (private key download triggered)
4. Checked for a `.messages .alert` element containing `'Successfully created key pair "verify-pw-test"'`
5. Found the messages container but its text was **empty**

The screenshot `003_create_done.png` confirms: the Key Pairs table shows `verify-pw-test` in the list (the keypair was created), but there is no green success message banner above the table.

This independently validates [CMT-JAN-1](#cmt-jan-1): Jan's concern about the assertion checking only the keypair name is well-founded — the create flow doesn't emit a visible success message at all, so even the name-only check would fail in a real browser.

### T3 Success — Delete Message Works

The T3 test confirms the delete flow correctly displays `"Success: Deleted Key Pair: verify-pw-test"`. This means:

- The `DeleteKeyPairs` table action's `action_past()` format works
- Django messages are rendering correctly in the template
- Only the create flow has the missing message issue

### Implications for CMT-JAN-1 and CMT-JAN-2

| Thread | Playwright Evidence | Action |
|--------|-------------------|--------|
| CMT-JAN-1 (create assertion) | T2 FAIL confirms the issue — the success message is empty, not just poorly asserted | Fix the create-keypair form to actually emit a success message via `messages.success()`, then fix the test assertion |
| CMT-JAN-2 (delete assertion) | T3 PASS confirms the delete message works — `"Deleted Key Pair: verify-pw-test"` appears with "Success: " prefix | Fix the test assertion to check the full message string: `f"Deleted Key Pair: {name}"` |

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| Owen McGonagle | 11 | 11 | 0 |
| Jan Jasek | 3 | 3 | 0 |
| Tatiana Ovchinnikova | 4 | 4 | 0 |
| Radomir Dopieralski | 2 | 2 | 0 |
| Ivan Anfimov | 0 (vote only) | — | — |

---

<a name="key-remaining-items"></a>

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| ~~Fix create-keypair form to emit success message (Playwright T2 confirms it's empty)~~ | ~~HIGH~~ | ~~FIXED in PS9~~ |
| ~~Fix Selenium test assertions to check full message format (CMT-JAN-1, CMT-JAN-2)~~ | ~~HIGH~~ | ~~FIXED in PS9~~ |
| ~~Get Jan Jasek's Code-Review -1 resolved~~ | ~~HIGH~~ | ~~CLEARED (vote reset by PS9)~~ |
| ~~Wait for Zuul CI on PS9~~ | ~~HIGH~~ | ~~PASS (Verified+1 on 2026-06-26)~~ |
| ~~Add commit message "Partially-Implements: blueprint removing-angularjs" (CMT-TAT-1)~~ | ~~HIGH~~ | ~~FIXED in PS11~~ |
| ~~Get Tatiana's Code-Review -1 cleared after commit message update~~ | ~~HIGH~~ | ~~CLEARED (vote reset by PS11)~~ |
| ~~Wait for Zuul CI on PS11~~ | ~~HIGH~~ | ~~PASS (Verified+1 on 2026-07-13)~~ |
| ~~Get Tatiana's re-review to confirm blueprint tag (CMT-TAT-1)~~ | ~~HIGH~~ | ~~CMT-TAT-1 RESOLVED~~ |
| ~~Fix `settings.rst` deprecation markers (CMT-TAT-2)~~ | ~~HIGH~~ | ~~FIXED in PS13~~ |
| ~~Get Tatiana's -1 cleared after docs fix~~ | ~~HIGH~~ | ~~CLEARED (vote reset by PS13)~~ |
| ~~Get Jan's re-review of PS9 fixes~~ | ~~HIGH~~ | ~~Jan CR+2 + W+1 (2026-07-14, "Tested in devstack")~~ |
| ~~Obtain first +2 Code-Review vote~~ | ~~HIGH~~ | ~~Radomir +2 (2026-07-08)~~ |
| ~~Obtain second +2 Code-Review vote from a core reviewer~~ | ~~HIGH~~ | ~~Jan +2 (2026-07-14)~~ |
| ~~Get Workflow +1~~ | ~~HIGH~~ | ~~Jan W+1 (2026-07-14)~~ |
| ~~Verify delete message works in browser~~ | ~~MEDIUM~~ | ~~VERIFIED (Playwright T3 PASS)~~ |
| **MERGED** | — | **2026-07-14 10:57 UTC** |
