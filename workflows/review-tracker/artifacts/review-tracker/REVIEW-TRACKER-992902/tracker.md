# Review 992902 — Live Comment Tracker

**Review:** [https://review.opendev.org/c/openstack/horizon/+/992902](https://review.opendev.org/c/openstack/horizon/+/992902)
**Title:** Fix key pair create success message lost on page redirect
**Author:** Owen McGonagle
**Status:** ✅ MERGED (2026-07-09 15:32:43)
**Current Patchset:** 6
**Zuul:** Verified+2 (PS6 — gate pipeline succeeded)
**Files Changed:** 1 ([`openstack_dashboard/dashboards/project/key_pairs/views.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/key_pairs/views.py))
**Reviewers:** Jan Jasek, Radomir Dopieralski, Dmitriy Rabotyagov, Tatiana Ovchinnikova

---

## Scan Log

| # | Date | Scanner | Notes |
|---|------|---------|-------|
| 5 | 2026-07-10 | AI (Claude) | **MERGED** — Owen addressed all feedback in PS5-6, Radomir flipped to +2, Tatiana approved with Workflow+1, gate passed |
| 4 | 2026-07-08 | AI (Claude) | Full bridge automation — executed research steps, generated analysis artifacts for CMT-RAD-1 and CMT-RAD-2 |
| 3 | 2026-07-08 | AI (Claude) | Deep-dive enhancement — restructured research guidance for CMT-RAD-1 and CMT-RAD-2 |
| 2 | 2026-07-08 | AI (Claude) | Recheck with deep-dive — topic changed to de-angularize, no new comments |
| 1 | 2026-07-07 | AI (Claude) | Initial scan — 3 recheck comments, 1 LGTM from Jan, 2 inline questions from Radomir |

---

## Change Log

### Scan #5 — 2026-07-10

1. **MERGED** Review successfully merged on 2026-07-09 15:32:43
2. **PS5** Owen removed defensive `hasattr()` checks in response to [CMT-RAD-1](#cmt-rad-1) and [CMT-RAD-2](#cmt-rad-2)
3. **PS6** Owen updated commit message (addressing [CMT-JAN-1](#cmt-jan-1))
4. **RESOLVED** [CMT-RAD-1](#cmt-rad-1): Owen explained defensive checks were unnecessary, removed them
5. **RESOLVED** [CMT-RAD-2](#cmt-rad-2): Owen explained `async_messages` always exists, removed nested check
6. **RESOLVED** [CMT-JAN-1](#cmt-jan-1): Owen addressed Depends-On suggestion (no Depends-On found in any patchset)
7. **NEW** [CMT-RAD-3](#cmt-rad-3): Radomir confirmed fix works, gave Code-Review+2
8. **NEW** [CMT-DIM-1](#cmt-dim-1): Dmitriy Rabotyagov gave Code-Review+1
9. **NEW** [CMT-TAT-1](#cmt-tat-1): Tatiana Ovchinnikova gave Code-Review+2 + Workflow+1
10. **UPDATED** [Score Summary](#score-summary): Final votes — Radomir +2, Dmitriy +1, Tatiana +2 + Workflow+1, Zuul Verified+2

### Scan #4 — 2026-07-08

1. **BRIDGE** [CMT-RAD-1](#cmt-rad-1): Executed research steps, generated full analysis artifact with findings and suggested Gerrit response
2. **BRIDGE** [CMT-RAD-2](#cmt-rad-2): Executed research steps, generated full analysis artifact with findings and suggested Gerrit response

### Scan #3 — 2026-07-08

1. **ENHANCED** [CMT-RAD-1](#cmt-rad-1): Restructured deep-dive note with numbered research steps and suggested approach
2. **ENHANCED** [CMT-RAD-2](#cmt-rad-2): Restructured deep-dive note with numbered research steps and suggested approach

### Scan #2 — 2026-07-08

1. **METADATA** Topic changed from `fix/keypair-create-message-delivery` to `de-angularize` on 2026-07-07 at 21:03
2. **UPDATED** [CMT-RAD-1](#cmt-rad-1): Added deep-dive note for code-archaeology question
3. **UPDATED** [CMT-RAD-2](#cmt-rad-2): Added deep-dive note for code-archaeology question

---

## What Needs to Change

### ✅ All Items Completed — Review Merged!

~~**[CMT-RAD-1](#cmt-rad-1): Clarify when self.request.horizon attribute might be missing**~~

- ~~**File:** `openstack_dashboard/dashboards/project/key_pairs/views.py:101`~~
- ~~**What the code does now:** Defensive check `if hasattr(self.request, 'horizon')` before accessing async_messages~~
- ~~**What the reviewer wants:** Radomir wants to understand the edge cases — when would `self.request` NOT have the `horizon` attribute?~~
- ~~**Why:** Understanding the defensive coding rationale helps assess whether this check is necessary or if it's overly cautious. This may be a pattern from other views or a specific edge case Owen encountered.~~
- **✅ RESOLVED:** Owen analyzed the middleware, confirmed `horizon` is always set, removed the defensive check in PS5

~~**[CMT-RAD-2](#cmt-rad-2): Clarify when self.request.horizon.async_messages might be missing**~~

- ~~**File:** `openstack_dashboard/dashboards/project/key_pairs/views.py:103`~~
- ~~**What the code does now:** Nested check `if hasattr(self.request.horizon, 'async_messages')` before appending messages~~
- ~~**What the reviewer wants:** Radomir wants to know when the `horizon` object would exist but NOT have the `async_messages` attribute~~
- ~~**Why:** Similar to CMT-RAD-1, this helps validate the defensive pattern. If these attributes are always present in production, the checks might be unnecessary boilerplate.~~
- **✅ RESOLVED:** Owen confirmed `async_messages` is always initialized with `horizon`, removed the nested check in PS5

---

## Where Things Are At / What To Do Next

### Overall Status

🎉 **MERGED on 2026-07-09!** 

This bug fix addressed a UX issue where the success message disappears after creating a keypair. The Django view triggers a file download (the private key) which causes a redirect, and Django messages don't persist across that redirect. Owen's fix uses Horizon's `async_messages` mechanism to preserve the message.

**Timeline:**
- PS1-3: CI issues
- PS4 (2026-06-25): Zuul Verified+1, Jan +2 (LGTM), Radomir -1 (two clarification questions)
- PS5 (2026-07-08): Owen removed defensive `hasattr()` checks after analyzing middleware
- PS6 (2026-07-08): Owen updated commit message
- 2026-07-09: Radomir +2 (tested, confirmed fix works), Dmitriy +1, Tatiana +2 + Workflow+1
- 2026-07-09: Zuul gate Verified+2, **MERGED**

**Key dynamic:** Owen's thoughtful response to Radomir's questions — backed by code analysis showing the defensive checks were unnecessary — converted a -1 into a +2. The bridge analysis artifacts ([CMT-RAD-1 analysis](bridge-artifacts/cmt-rad-1-analysis.md), [CMT-RAD-2 analysis](bridge-artifacts/cmt-rad-2-analysis.md)) provided the code archaeology that informed Owen's decision to simplify.

<a name="score-summary"></a>

### Score Summary

| Label | Voter | Value |
|-------|-------|-------|
| Verified | Zuul | +2 (PS6 — gate pipeline succeeded) |
| Code-Review | Jan Jasek | +2 |
| Code-Review | Radomir Dopieralski | +2 |
| Code-Review | Dmitriy Rabotyagov | +1 |
| Code-Review | Tatiana Ovchinnikova | +2 |
| Workflow | Tatiana Ovchinnikova | +1 |

### What You Should Do Next

✅ **Nothing — this change is merged!**

All open threads were resolved, all reviewers approved, and Zuul gate pipeline passed. The fix is now part of the Horizon codebase.

### Open Threads Requiring Attention

**None — all threads resolved and change merged.**

---

## Patchset-Level Comments

### CMT-OWN-1 — Recheck (PS3) — RESOLVED

**Author:** Owen McGonagle | **File:** /PATCHSET_LEVEL | **PS:** 3

> recheck

**AI Assessment:** Routine CI recheck. No action needed.

**Status for Owen:** No action needed.

---

### CMT-OWN-2 — Recheck (PS4) — RESOLVED

**Author:** Owen McGonagle | **File:** /PATCHSET_LEVEL | **PS:** 4

> recheck

**AI Assessment:** Routine CI recheck. No action needed.

**Status for Owen:** No action needed.

---

### CMT-OWN-3 — Recheck (PS4) — RESOLVED

**Author:** Owen McGonagle | **File:** /PATCHSET_LEVEL | **PS:** 4

> recheck

**AI Assessment:** Second recheck on PS4. No action needed.

**Status for Owen:** No action needed.

---

<a name="cmt-jan-1"></a>

### CMT-JAN-1 — Drop unnecessary Depends-On — ✅ RESOLVED

**Author:** Jan Jasek | **File:** /PATCHSET_LEVEL | **PS:** 4

> LGTM, tested in devstack.
> I think that this Depends-On is not necessary here. I would drop it so this patch is not blocked on an unrelated change.

**AI Assessment:** This was a **suggestion** (Jan already gave +2, so not blocking). Jan tested the fix in DevStack and confirms it works. He suggested removing a `Depends-On:` tag from the commit message that's blocking this patch on an unrelated change.

**Owen's Response:** PS6 updated the commit message. Analysis of all patchsets shows no `Depends-On` was ever present, so either Owen already removed it before PS4 or Jan's suggestion was preemptive. Either way, the commit message was finalized in PS6.

**Status for Owen:** ✅ Resolved — commit message finalized in PS6.

---

<a name="cmt-rad-3"></a>

### CMT-RAD-3 — Code tested, fix confirmed — ✅ RESOLVED

**Author:** Radomir Dopieralski | **File:** /PATCHSET_LEVEL | **PS:** 6

> the code looks good, and I have tested it to confirm the message now appears

**AI Assessment:** This is Radomir's **approval** after Owen's PS5 code changes. He tested the fix and confirmed the success message now appears correctly. This comment accompanied his Code-Review +2 vote.

**Status for Owen:** ✅ Resolved — Radomir approved and tested.

---

<a name="cmt-dim-1"></a>

### CMT-DIM-1 — Code-Review +1 — ✅ RESOLVED

**Author:** Dmitriy Rabotyagov | **File:** /PATCHSET_LEVEL | **PS:** 6

> (voted Code-Review +1, no comment text)

**AI Assessment:** Dmitriy gave a +1 vote on PS6. This is a positive signal from another core reviewer.

**Status for Owen:** ✅ Resolved — additional approval.

---

<a name="cmt-tat-1"></a>

### CMT-TAT-1 — LGTM, Workflow+1 — ✅ RESOLVED

**Author:** Tatiana Ovchinnikova | **File:** /PATCHSET_LEVEL | **PS:** 6

> LGTM, thank you!

**AI Assessment:** Tatiana gave the final **approval** with Code-Review +2 and Workflow+1, which allowed the change to enter the gate pipeline. Her "LGTM, thank you!" confirms she reviewed the fix and is satisfied.

**Status for Owen:** ✅ Resolved — final approval, change merged.

---

## Inline Comments — Radomir Dopieralski

<a name="cmt-rad-1"></a>

### CMT-RAD-1 — When is self.request.horizon missing? — ✅ RESOLVED

**Author:** Radomir Dopieralski | **File:** `openstack_dashboard/dashboards/project/key_pairs/views.py:101` | **PS:** 4

**Radomir's Question:**
> is there any case where self.request doesn't have the horizon attribute? when?

**Owen's Response (PS5):**
> I could not find other places that check for the `horizon` attribute before using it, or checking for `async_messages`.
> 
> If we can assume that all authenticated requests go through `_process_request()` as part of the middleware stack, then the `horizon` attribute always gets defined, as well as `async_messages`:
> 
> https://github.com/openstack/horizon/blob/master/horizon/middleware/base.py#L60
> 
>     def _process_request(self, request):
>         """Adds data necessary for Horizon to function to the request."""
> 
>         request.horizon = {'dashboard': None,
>                            'panel': None,
>                            'async_messages': []}
> 
> **A few thoughts:**
> - It does not hurt to have this check. Keep the check "just in case" we missed something?
> - Or, remove it, based on my analysis that the `horizon` attribute should always be set properly.
> 
> **I am leaning towards removing it (as I just did)**
> 
> Let me know your thoughts.
> 
> **As an fyi** - I found another place where we directly access `request.horizon['async_messages']` without a check:
> 
> https://github.com/openstack/horizon/blob/master/horizon/messages.py
> 
>     def horizon_message_already_queued(request, message):
>         _message = force_str(message)
>         if http_utils.is_ajax(request):
>             for tag, msg, extra in request.horizon['async_messages']:
>                 if _message == msg:
>                     return True
>         else:
>             for msg in _messages.get_messages(request)._queued_messages:
>                 if msg.message == _message:
>                     return True
>         return False

**Owen's Action:** Removed the defensive `hasattr(self.request, 'horizon')` check in PS5.

**AI Assessment:** Owen's analysis was thorough and correct. The [bridge analysis](bridge-artifacts/cmt-rad-1-analysis.md) found that `request.horizon` is set by middleware on EVERY request, and only 2 defensive checks existed in the entire codebase (Owen's + the middleware itself). The check was safe but unnecessary in production. Owen made the right call to simplify.

**Radomir's Verdict:** ✅ Code-Review +2 after testing PS6 (which kept the simplified code from PS5).

**Status for Owen:** ✅ RESOLVED — question answered, code simplified, approved, merged.

---

<a name="cmt-rad-2"></a>

### CMT-RAD-2 — When is async_messages missing? — ✅ RESOLVED

**Author:** Radomir Dopieralski | **File:** `openstack_dashboard/dashboards/project/key_pairs/views.py:103` | **PS:** 4

**Radomir's Question:**
> is there any case where there is self.request.horizon but it doesn't have async_messages? when?

**Owen's Response (PS5):**
> see above

**AI Assessment:** Owen's response to CMT-RAD-1 covered both questions. The middleware initializes `horizon` and `async_messages` together in a single dict:

```python
request.horizon = {'dashboard': None,
                   'panel': None,
                   'async_messages': []}
```

The [bridge analysis](bridge-artifacts/cmt-rad-2-analysis.md) found ZERO defensive checks for `async_messages` in the entire codebase (Owen's was the only one). All other Horizon code directly accesses `request.horizon['async_messages']` without checking. The nested check was completely unnecessary.

**Owen's Action:** Removed the nested `hasattr(self.request.horizon, 'async_messages')` check in PS5.

**Radomir's Verdict:** ✅ Code-Review +2 after testing PS6.

**Status for Owen:** ✅ RESOLVED — question answered, code simplified, approved, merged.

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| Owen McGonagle | 3 | 3 | 0 |
| Jan Jasek | 1 | 1 | 0 |
| Radomir Dopieralski | 3 | 3 | 0 |
| Dmitriy Rabotyagov | 1 | 1 | 0 |
| Tatiana Ovchinnikova | 1 | 1 | 0 |

---

## Key Remaining Items Before This Can Merge

**✅ ALL ITEMS COMPLETED — REVIEW MERGED!**

| Item | Severity | Status |
|------|----------|--------|
| ~~Answer Radomir's question about self.request.horizon availability (CMT-RAD-1)~~ | HIGH | ✅ RESOLVED (PS5) |
| ~~Answer Radomir's question about async_messages availability (CMT-RAD-2)~~ | HIGH | ✅ RESOLVED (PS5) |
| ~~Get Radomir's Code-Review -1 resolved~~ | HIGH | ✅ RESOLVED (Radomir +2 on PS6) |
| ~~Consider dropping Depends-On per Jan's suggestion (CMT-JAN-1)~~ | MEDIUM | ✅ RESOLVED (PS6 commit message update) |
| ~~Get a second +2 Code-Review vote from core reviewers~~ | HIGH | ✅ RESOLVED (Tatiana +2) |
| ~~Get Workflow +1~~ | HIGH | ✅ RESOLVED (Tatiana Workflow+1) |
| ~~Zuul gate pipeline pass~~ | HIGH | ✅ RESOLVED (Verified+2, merged) |
