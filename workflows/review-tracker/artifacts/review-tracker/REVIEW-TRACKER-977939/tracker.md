# Review 977939 — Live Comment Tracker

**Review:** [https://review.opendev.org/c/openstack/horizon/+/977939](https://review.opendev.org/c/openstack/horizon/+/977939)
**Title:** Add Horizon panel to enable TOTP MFA enrollment
**Author:** Benjamin Lasseye
**Status:** NEW
**Current Patchset:** 27
**Zuul:** Verified +1 (passing)
**Code-Review:** Jan Jasek -1
**Files Changed:** 22 (new MFA panel under `settings/mfa/`, API additions in `keystone.py`, docs, defaults, release notes, requirements)
**Reviewers:** Ivan Anfimov, Radomir Dopieralski, Jan Jasek, Owen McGonagle

---

## Scan Log

| # | Date | Scanner | Notes |
|---|------|---------|-------|
| 1 | 2026-06-19 | AI (Claude) | Initial scan — 28 comment threads from 5 participants (4 reviewers + author) |
| 2 | 2026-07-14 | AI (Claude) | Recheck — PS25→27, 8 threads RESOLVED, 1 new thread (MFA workflow issue), Jan CR-1, abandon/restore misclick |

---

## Change Log

### Scan #2 — 2026-07-14

1. **UPDATED** Header: PS 25→27, added Code-Review: Jan Jasek -1
2. **UPDATED** [CMT-JAN-1](#cmt-jan-1): Changed POSTED → RESOLVED (Benjamin: "Done", resolved on Gerrit)
3. **UPDATED** [CMT-JAN-2](#cmt-jan-2): Changed POSTED → RESOLVED (Benjamin fixed URL, Jan confirmed: "Works fine now, thanks!")
4. **UPDATED** [CMT-JAN-3](#cmt-jan-3): Changed POSTED → RESOLVED (Benjamin: "Done", dead code removed)
5. **UPDATED** [CMT-IVA-8](#cmt-iva-8): Changed POSTED → RESOLVED (Benjamin: "Done")
6. **UPDATED** [CMT-IVA-9](#cmt-iva-9): Changed POSTED → RESOLVED (Benjamin: "Done")
7. **UPDATED** [CMT-OWN-1](#cmt-own-1): Changed POSTED → RESOLVED (Benjamin: "Done")
8. **UPDATED** [CMT-OWN-2](#cmt-own-2): Changed POSTED → RESOLVED (back-and-forth discussion, Owen accepted either solution)
9. **UPDATED** [CMT-OWN-3](#cmt-own-3): Changed POSTED → RESOLVED (Benjamin: "Done")
10. **NEW** [CMT-OWN-5](#cmt-own-5): MFA credential delete workflow concern (views.py:230, PS26) — extensive 9-comment discussion between Owen, Benjamin, Jan — OPEN
11. **NEW** [CMT-BEN-1](#cmt-ben-1): Abandon/restore misclick explanation (PS27, patchset-level) — INFORMATIONAL
12. **UPDATED** Comment Statistics: recalculated with new comments
13. **UPDATED** Key Remaining Items: 7 items struck through (resolved), 2 new items added

---

## Where Things Are At / What To Do Next

### Overall Status

This review has seen major progress since scan #1. Benjamin addressed all outstanding feedback from Ivan, Radomir, Jan, and Owen in PS26-27, resolving 8 previously open threads. The hardcoded URL bug ([CMT-JAN-2](#cmt-jan-2)) that was causing 404s in WEBROOT deployments is now fixed and confirmed working by Jan.

However, a new discussion thread ([CMT-OWN-5](#cmt-own-5)) has emerged about MFA credential deletion workflow behavior. Owen reported an issue where deleting MFA credentials can leave the user unable to log in. Benjamin attributes this to a Keystone bug, not a Horizon issue. Jan tested Owen's steps but could not reproduce. Jan gave Code-Review -1 partly related to this discussion.

The review was briefly abandoned and immediately restored on 2026-06-24 (misclick by Benjamin). PS27 has Zuul Verified+1 but carries Jan's CR-1.

### Score Summary

| Label | Value | Who |
|-------|-------|-----|
| Verified | +1 | Zuul |
| Code-Review | -1 | Jan Jasek |
| Workflow | (none) | — |

### What You Should Do Next

1. **HIGH** — Resolve the MFA credential delete workflow issue ([CMT-OWN-5](#cmt-own-5)) — Jan can't reproduce your reported problem. Provide more specific reproduction steps or investigate whether it's a configuration issue in your devstack
2. **HIGH** — Get Jan's CR-1 cleared — this requires resolving the views.py discussion
3. **MEDIUM** — Solicit CR+2 votes from core reviewers (need 2x CR+2 for merge)

### Open Threads Requiring Attention

| Thread | File | Status | Owner | Priority |
|--------|------|--------|-------|----------|
| [CMT-OWN-5](#cmt-own-5) | `views.py:230` | NEEDS YOUR RESPONSE | Owen McGonagle | HIGH |

---

## Patchset-Level Comments

<a name="cmt-iva-1"></a>

### CMT-IVA-1 — Release note request — RESOLVED

**Author:** Ivan Anfimov | **PS:** 1

> Hello,
>
> Please add release note.

**Reply (Ivan Anfimov, PS1):**
> https://review.opendev.org/c/openstack/horizon/+/977978?usp=search

**AI Assessment:** Ivan pointed the author to a related release note review. The author subsequently added a release note to this patch. Thread resolved.

**Status for Owen:** No action needed.

---

<a name="cmt-iva-2"></a>

### CMT-IVA-2 — JS file translation support — RESOLVED

**Author:** Ivan Anfimov | **PS:** 3

> Please add support translation in JS files.

**Reply (Benjamin Lasseye, PS3):**
> I removed the JS files to have a code architecture that is as similar as possible to the rest of the project.

**Reply (Ivan Anfimov, PS3):**
> Done

**AI Assessment:** Ivan requested JS translation support. Benjamin removed JS files entirely to follow standard Django architecture. Ivan accepted this approach. Thread resolved.

**Status for Owen:** No action needed.

---

<a name="cmt-rad-1"></a>

### CMT-RAD-1 — Radomir's initial review note — INFORMATIONAL

**Author:** Radomir Dopieralski | **PS:** 16

> Some comments I have by just looking at the code. I'm going to test it some more, and probably have more notes. Thank you for working on it.

**AI Assessment:** Introductory note accompanying Radomir's inline comments on PS16. Not actionable on its own. Radomir has not posted follow-up patchset-level comments.

**Status for Owen:** No action needed. Note that Radomir mentioned he would test further — no follow-up has been posted since April 2026.

---

<a name="cmt-jan-1"></a>

### CMT-JAN-1 — Wizard UX feedback (asterisk position + button flow) — RESOLVED

**Author:** Jan Jasek | **PS:** 21

> Hello @blasseye@ikmail.com, thank you for your patch and your patience!
> There are a few things where I would ask for a fix or clarification.
>
> A few points from a user/visual perspective.
> 1) In `Enable Multi-Factor Authentication` form:
> `I understand and have an authenticator app ready` (checkbox) has an asterisk (meaning it is required) but the asterisk is weirdly located under the checkbox. It looks really odd. I tried different sizes of windows, still the same. Would be possible to move it beside of the checkbox?
>
> 2) The first tab is `Security Notice`, this part of the form has buttons `Cancel` and `Enable MFA` both immediately available, but `Enable MFA` click does nothing. You need to go through all the tabs (`Security Notice`, `TOTP Credential & QR Code`, `Verify Code`), fill them and then the `Enable MFA` button in the form works and does something.
> So I would prefer to change the `Enable MFA` button in the form to the `Next` button for the first two tabs, so this button will move you to the next tab and only the last one will have an `Enable MFA` button for example the same like it is for create network. Buttons cancel, back, next (which turn to create at the last tab). WDYT? I think that it will be much more user friendly.

**Reply (Benjamin Lasseye, PS21):**
> Thank you for prompting me to look into this; I had overlooked the "wizard = True" option.

**Reply (Benjamin Lasseye, PS21):**
> Done

**AI Assessment:** Jan raised two UX issues: (1) misplaced asterisk on required checkbox, (2) confusing button flow where "Enable MFA" is visible but non-functional on early tabs. Benjamin acknowledged and implemented `wizard = True` to fix the button flow. Thread resolved on Gerrit.

**Status for Owen:** No action needed — resolved.

---

<a name="cmt-iva-7"></a>

### CMT-IVA-7 — Google Authenticator mention — RESOLVED

**Author:** Ivan Anfimov | **PS:** 21

> Hello, I think more friendly add information about Google app 😉

**Reply (Benjamin Lasseye, PS21):**
> I intentionally chose to focus only on free and open-source applications. I'm open to change.

**AI Assessment:** Ivan suggested mentioning Google Authenticator. Benjamin explained the FOSS-only choice but left room for change. Thread marked resolved on Gerrit. Related inline suggestions ([CMT-IVA-8](#cmt-iva-8), [CMT-IVA-9](#cmt-iva-9)) to add Google Authenticator to the app list are now also resolved.

**Status for Owen:** No action needed.

---

<a name="cmt-recheck-1"></a>

### CMT-RECHECK-1 — Recheck (PS22) — INFORMATIONAL

**Author:** Benjamin Lasseye | **PS:** 22

> recheck

**AI Assessment:** Two recheck comments on PS22 to trigger CI re-runs. Informational only.

**Status for Owen:** No action needed.

---

<a name="cmt-own-1"></a>

### CMT-OWN-1 — Commit message typos — RESOLVED

**Author:** Owen McGonagle | **PS:** 25

> I found a few typos in the commit message
> "activited" -> "activated"
> "Custome" -> "Custom"
> "exemple" ->"example"
>
> first pass at testing the creation of my new credential using FreeOTP is working nicely.

**Reply (Benjamin Lasseye, PS25):**
> Thanks, I'll take care of it.

**Reply (Benjamin Lasseye, PS25):**
> Done

**AI Assessment:** Owen identified three typos in the commit message and noted positive testing results with FreeOTP. Benjamin acknowledged and fixed. Thread resolved on Gerrit.

**Status for Owen:** No action needed — resolved.

---

<a name="cmt-ben-1"></a>

### CMT-BEN-1 — Abandon/restore misclick — INFORMATIONAL

**Author:** Benjamin Lasseye | **PS:** 27

> Miss click...

**AI Assessment:** Benjamin accidentally abandoned the review on 2026-06-24 and immediately restored it (~25 seconds later). No impact on the review state. PS27 continues normally with Zuul Verified+1.

**Status for Owen:** No action needed — accidental, fully recovered.

---

## Inline Comments — Ivan Anfimov

<a name="cmt-iva-3"></a>

### CMT-IVA-3 — Commit message example formatting — RESOLVED

**Author:** Ivan Anfimov | **File:** `/COMMIT_MSG` L37 | **PS:** 10

> ```suggestion
> example: OPENSTACK_MFA_ROLES = [ 'admin', 'mfa-role']
> ```

**Reply (Benjamin Lasseye, PS10):**
> Done

**AI Assessment:** Minor formatting suggestion for the commit message example. Resolved.

**Status for Owen:** No action needed.

---

<a name="cmt-iva-4"></a>

### CMT-IVA-4 — Doc settings.rst underline fix — RESOLVED

**Author:** Ivan Anfimov | **File:** `doc/source/configuration/settings.rst` L655 | **PS:** 15

> ```suggestion
> -------------------
> ```

**Reply (Benjamin Lasseye, PS15):** Done. Patchset 16*

**AI Assessment:** RST formatting fix — underline length must match heading. Resolved in PS16.

**Status for Owen:** No action needed.

---

<a name="cmt-iva-5"></a>

### CMT-IVA-5 — Doc version already 2026.2 (L657) — RESOLVED

**Author:** Ivan Anfimov | **File:** `doc/source/configuration/settings.rst` L657 | **PS:** 15

> Already 2026.2

**Reply (Benjamin Lasseye, PS15):** Done. Patchset 16*

**AI Assessment:** Version string correction. Resolved in PS16.

**Status for Owen:** No action needed.

---

<a name="cmt-iva-6a"></a>

### CMT-IVA-6a — MFA roles: "member" too? — RESOLVED

**Author:** Ivan Anfimov | **File:** `doc/source/configuration/settings.rst` L659 | **PS:** 15

> Hmm, may be member too?

**Reply (Benjamin Lasseye, PS15):**
> By default, I only assign the "admin" role, because for the dashboard to function properly, the user must have the necessary role to modify the options --enable-multi-factor-auth and --multi-factor-auth-rule and view their TOTP credentials, and by default in Keystone, only users with the "admin" role have this permission.

**Reply (Ivan Anfimov, PS15):**
> Done

**AI Assessment:** Ivan asked about including "member" role in MFA defaults. Benjamin explained the Keystone permission model requiring admin role. Ivan accepted the explanation. This is useful context — the MFA panel requires admin-level Keystone permissions by default.

**Status for Owen:** No action needed. Good context: MFA enrollment requires admin role by default due to Keystone permission model.

---

<a name="cmt-iva-6b"></a>

### CMT-IVA-6b — Doc settings.rst underline fix (L666) — RESOLVED

**Author:** Ivan Anfimov | **File:** `doc/source/configuration/settings.rst` L666 | **PS:** 15

> ```suggestion
> ----------------------------
> ```

**Reply (Benjamin Lasseye, PS15):** Done. Patchset 16*

**AI Assessment:** RST underline length fix. Resolved in PS16.

**Status for Owen:** No action needed.

---

<a name="cmt-iva-6c"></a>

### CMT-IVA-6c — Doc version already 2026.2 (L668) — RESOLVED

**Author:** Ivan Anfimov | **File:** `doc/source/configuration/settings.rst` L668 | **PS:** 15

> Already 2026.2

**Reply (Benjamin Lasseye, PS15):** Done. Patchset 16*

**AI Assessment:** Version string correction. Resolved in PS16.

**Status for Owen:** No action needed.

---

<a name="cmt-iva-8"></a>

### CMT-IVA-8 — Add Google Authenticator to app list (L41) — RESOLVED

**Author:** Ivan Anfimov | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L41 | **PS:** 21

> ```suggestion
>             "- You will need an authenticator app (Google Authenticator, "
> ```

**Reply (Benjamin Lasseye, PS21):**
> Done

**AI Assessment:** Suggestion to add Google Authenticator to the list of authenticator apps mentioned in the help text. Benjamin accepted and resolved. The earlier FOSS-only position ([CMT-IVA-7](#cmt-iva-7)) was relaxed — Google Authenticator is now included.

**Status for Owen:** No action needed — resolved.

---

<a name="cmt-iva-9"></a>

### CMT-IVA-9 — Add Aegis Authenticator to app list (L42) — RESOLVED

**Author:** Ivan Anfimov | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L42 | **PS:** 21

> ```suggestion
>             "Aegis Authenticator, FreeOTP, etc.).\n"
> ```

**Reply (Benjamin Lasseye, PS21):**
> Done

**AI Assessment:** Companion to [CMT-IVA-8](#cmt-iva-8). Benjamin accepted and resolved.

**Status for Owen:** No action needed — resolved.

---

## Inline Comments — Radomir Dopieralski

<a name="cmt-rad-2"></a>

### CMT-RAD-2 — Deduplicate keystone API function — RESOLVED

**Author:** Radomir Dopieralski | **File:** `openstack_dashboard/api/keystone.py` L519 | **PS:** 16

> Can this function just call the previous function, instead of duplicating its code? Something like:
>
> ```python
> def user_update_own_options(request, **options):
>   return user_update_options(request, request.user.id, **options)
> ```

**Reply (Benjamin Lasseye, PS16):**
> Good point, I'll look into that. I just need to be careful with admin permissions. We don't want users to be blocked from changing their own options.

**Reply (Benjamin Lasseye, PS16):**
> Done

**AI Assessment:** Radomir identified code duplication in the keystone API layer. Benjamin initially flagged a permission concern (admin vs self-service), then resolved. Good code quality suggestion — reduces maintenance burden.

**Status for Owen:** No action needed.

---

<a name="cmt-rad-3"></a>

### CMT-RAD-3 — Policy check vs separate setting for panel visibility — RESOLVED

**Author:** Radomir Dopieralski | **File:** `openstack_dashboard/dashboards/settings/mfa/panel.py` L32 | **PS:** 16

> should this be based on policy checks, rather than a separate setting?

**Reply (Benjamin Lasseye, PS16):**
> I think you've got a better lead. I'll take a look at it.

**Reply (Benjamin Lasseye, PS16):**
> Done

**AI Assessment:** Radomir suggested using Keystone policy checks instead of a custom setting to control panel visibility. This aligns with Horizon's standard pattern (`POLICY_CHECK_FUNCTION`). Benjamin agreed and implemented the change. Resolved.

**Status for Owen:** No action needed. Good architectural improvement.

---

<a name="cmt-rad-4"></a>

### CMT-RAD-4 — Add cryptography to requirements.txt — RESOLVED

**Author:** Radomir Dopieralski | **File:** `openstack_dashboard/dashboards/settings/mfa/utils.py` L17 | **PS:** 16

> do we need to add this library to requirements.txt?

**Reply (Benjamin Lasseye, PS16):**
> I drew heavily on the totp.py plugin from the Keystone project: keystone/auth/plugins/totp.py and it is listed in the requirements: [...]
>
> I'll add it

**Reply (Benjamin Lasseye, PS16):**
> Done

**AI Assessment:** Radomir correctly identified that the `cryptography` library import needed to be added to `requirements.txt`. Benjamin confirmed and added it. Resolved.

**Status for Owen:** No action needed.

---

<a name="cmt-rad-5"></a>

### CMT-RAD-5 — Multi-line string for help_text — RESOLVED

**Author:** Radomir Dopieralski | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L45 | **PS:** 16

> perhaps a multi-line string (with """) would work here better

**Reply (Benjamin Lasseye, PS16):**
> We don't typically use multi-line triple-quoted strings for help_text in Horizon. Also, indentation in """ strings may introduce unintended whitespace, so I used the \n format for consistency and to avoid formatting issues.

**Reply (Benjamin Lasseye, PS16):**
> Done

**AI Assessment:** Radomir suggested triple-quoted strings for readability. Benjamin explained Horizon convention and whitespace concerns. Benjamin eventually resolved — likely adjusted formatting without switching to triple-quotes. This is a reasonable style decision following existing Horizon patterns.

**Status for Owen:** No action needed.

---

## Inline Comments — Jan Jasek

<a name="cmt-jan-2"></a>

### CMT-JAN-2 — Hardcoded URL breaks WEBROOT deployments (404 bug) — RESOLVED

**Author:** Jan Jasek | **File:** `openstack_dashboard/dashboards/settings/mfa/templates/mfa/_select_credential_with_qr.html` L112 | **PS:** 21

> As this Django URL is registered correctly in `urls.py`, what is the reason to use `/settings/mfa/credential/` hardcoded here. If I am right then with this implementation it is expected that Horizon is at the site root which can be (I think quite often is) customized using `WEBROOT` or proxy prefix.
>
> edit: Now when I am verifying your patch practically, I can not see QR code at all and I am getting 404 in inspect->network, because the code is calling `http://xxxx/settings/mfa/credential/__new__/qr/`
> But reality of my deployment is: `http://xxxx/dashboard/settings/mfa/....`

**Reply (Benjamin Lasseye, PS21):**
> I've made the change. Can you confirm that the problem is no longer occurring on your end? Normally, the URL is now resolved using Django.

**Reply (Jan Jasek, PS21):**
> Works fine now, thanks!

**AI Assessment:** **This was a functional bug now fixed.** Jan confirmed a 404 error when Horizon is deployed with a custom `WEBROOT` (e.g., `/dashboard/`). The template hardcoded `/settings/mfa/credential/` instead of using Django's URL resolution. Benjamin fixed it in PS26/27 and Jan confirmed it works. Thread resolved on Gerrit.

**Status for Owen:** No action needed — resolved. The QR code now displays correctly in WEBROOT deployments.

---

<a name="cmt-jan-3"></a>

### CMT-JAN-3 — OPENSTACK_KEYSTONE_MFA_ISSUER undefined setting + dead code — RESOLVED

**Author:** Jan Jasek | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L216 | **PS:** 21

> I am a little bit confused. I am not familiar with all possible OpenStack settings but what exactly is `OPENSTACK_KEYSTONE_MFA_ISSUER` and where is it coming from? I can not find it in OpenStack documentation, neither defined here in the patch.
> Should it be `OPENSTACK_TOTP_QRCODE_ISSUER`? Or am I missing something?
>
> I wonder if `OPENSTACK_KEYSTONE_MFA_ISSUER` was meant as a companion to `OPENSTACK_KEYSTONE_MFA_TOTP_ENABLED`, but I only found `OPENSTACK_TOTP_QRCODE_ISSUER` defined and documented in this patch. Could you please clarify it for me?
>
> Also... `success_message/failure_message` does not contain `%s` so this override never runs I guess?

**Reply (Benjamin Lasseye, PS21):**
> Thanks for your review. It was a feature I had used before but modified, and I didn't pay attention to it since it wasn't causing any errors.
>
> This function is no longer useful. I'm going to delete it.

**Reply (Benjamin Lasseye, PS21):**
> Done

**AI Assessment:** Jan found two issues: (1) reference to an undefined setting `OPENSTACK_KEYSTONE_MFA_ISSUER` that should be `OPENSTACK_TOTP_QRCODE_ISSUER`, and (2) dead code in success/failure message formatting (missing `%s` placeholder). Benjamin deleted the function as promised. Thread resolved on Gerrit.

**Status for Owen:** No action needed — resolved.

---

## Inline Comments — Owen McGonagle

<a name="cmt-own-2"></a>

### CMT-OWN-2 — Dropdown wording nit — RESOLVED

**Author:** Owen McGonagle | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L80 | **PS:** 25

> Just a nit pick... before the first credential is created, the dropdown is not yet there...
>
> Mabye change it to:
> "After you create your first credential, select one from the provided dropdown list"
>
> btw - so far, so good - I was able to create my credential using the FreeOTP app

**Reply (Benjamin Lasseye, PS25):**
> I'm sorry, I don't understand. If there aren't any totps created yet, don't you think that's unclear [...]

**Reply (Owen McGonagle, PS25):**
> Looking at the "TOTP Credential & QR Code" panel again, and seeing the TOP Credential "Create a new [...]

**Reply (Benjamin Lasseye, PS25):**
> Oh yes true... i understand, now i see the error. There are 2 solutions: [...]

**Reply (Owen McGonagle, PS25):**
> I am good with either option - you can pick one

**AI Assessment:** Owen pointed out the help text references a dropdown that doesn't exist before the first credential is created. After some back-and-forth clarification, Benjamin understood the issue and proposed two solutions. Owen accepted either option. Thread resolved on Gerrit.

**Status for Owen:** No action needed — resolved.

---

<a name="cmt-own-3"></a>

### CMT-OWN-3 — Missing space after "current" — RESOLVED

**Author:** Owen McGonagle | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L123 | **PS:** 25

> missing space after current

**Reply (Benjamin Lasseye, PS25):**
> Right ! Thanks

**Reply (Benjamin Lasseye, PS25):**
> Done

**AI Assessment:** Typo-level nit — missing whitespace in a string. Fixed by Benjamin. Thread resolved on Gerrit.

**Status for Owen:** No action needed — resolved.

---

<a name="cmt-own-4"></a>

### CMT-OWN-4 — OPENSTACK_KEYSTONE_MFA_TOTP_ENABLED default location — RESOLVED

**Author:** Owen McGonagle | **File:** `openstack_dashboard/defaults.py` L584 | **PS:** 25

> I am just starting the review...
>
> Figured I would mention this, as I see this during my initial review...
>
> I believe we need to also set this default setting:
>
> ```
> # Enable TOTP MFA enrollment panel in Settings dashboard.
> OPENSTACK_KEYSTONE_MFA_TOTP_ENABLED = False
> ```

**Reply (Jan Jasek, PS25):**
> Hello @omcgonag@redhat.com,
> I do not think we need, as it is already in `openstack_auth/defaults.py`
>
> https://github.com/openstack/horizon/blob/e4837ab45aa52891465c31d7191d60c7e32de491/openstack_auth/defaults.py#L186

**Reply (Owen McGonagle, PS25):**
> Thx, I did not see that, all set

**AI Assessment:** Owen suggested the default needed to be in `openstack_dashboard/defaults.py`, but Jan correctly pointed out it already exists in `openstack_auth/defaults.py`. Owen accepted the clarification. Resolved.

**Status for Owen:** No action needed — you resolved this yourself.

---

<a name="cmt-own-5"></a>

### CMT-OWN-5 — MFA credential delete workflow concern — NEEDS YOUR RESPONSE

**Author:** Owen McGonagle | **File:** [openstack_dashboard/dashboards/settings/mfa/views.py:230](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/settings/mfa/views.py#L230) | **PS:** 26

> Not sure if this is the best place to add my comment about a workflow question I have about if/when [the user deletes their MFA credential...]

**Reply (Benjamin Lasseye, PS26):**
> I didn't have that problem on my test/dev stack. Do you have a specific configuration? Report it to [...]

**Reply (Owen McGonagle, PS26):**
> I have a very generic devstack setup - all default settings. I have another setup that I can point t[o...]

**Reply (Jan Jasek, PS27):**
> Hi @omcgonag@redhat.com, Could you be a little more specific what are your steps and the issue you a[re facing...]

**Reply (Jan Jasek, PS27):**
> Okay, I am not sure if it is exactly the issue that you are facing but when I enable MFA, then there [...]

**Reply (Benjamin Lasseye, PS27):**
> I've noticed that getting stuck if you delete the credential is an issue. But this bug is in Keyston[e, not Horizon...]

**Reply (Benjamin Lasseye, PS27):**
> ```
> openstack user set --enable-multi-factor-auth --multi-factor-auth-rule password,totp mfa-member [...]
> ```

**Reply (Owen McGonagle, PS27):**
> My steps were (1) create new credentials (2) add new FreeOTP credential (4) go back to MFA panel (3) [delete credential...]

**Reply (Jan Jasek, PS27 — 2026-07-14):**
> Hi @omcgonag@redhat.com, I tried your steps but I am not facing this issue in my environment. When I [delete the credential, it works fine...]

**AI Assessment:** Owen raised a concern about the user workflow when deleting MFA credentials — specifically, whether deleting a credential can leave the user locked out. This spawned a 9-comment discussion thread:

- **Benjamin's position:** The credential-deletion lockout is a Keystone-side bug, not a Horizon issue. He provided CLI commands to recover.
- **Jan's position:** He tested Owen's exact steps and could not reproduce the issue. He asked for more specific reproduction steps.
- **Owen's position:** Reported the issue on a generic devstack setup with default settings.

Jan gave CR-1 partly related to this unresolved discussion. The thread remains open — Owen needs to respond to Jan's latest comment (2026-07-14) confirming he cannot reproduce.

This is a significant blocker: Jan's CR-1 needs to be cleared before this review can progress. Whether the issue is a Horizon bug or a Keystone bug, the discussion needs resolution.

**Status for Owen:** HIGH priority — Jan tested your steps on 2026-07-14 and cannot reproduce. You need to:
1. Try to reproduce again with a clean devstack
2. If reproducible: provide exact steps, devstack version, and Keystone config
3. If not reproducible: reply acknowledging and resolve the thread
4. If it's a Keystone issue: consider opening a separate Keystone bug and resolving this thread

---

## Inline Comments — Zuul

<a name="cmt-zuul-1"></a>

### CMT-ZUUL-1 — Unused import (pep8 F401) — RESOLVED (by new patchset)

**Author:** Zuul | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L15 | **PS:** 23

> pep8: F401 'django.conf.settings as django_settings' imported but unused

**AI Assessment:** Automated pep8 finding from PS23. The unused import `django_settings` was left over from the `OPENSTACK_KEYSTONE_MFA_ISSUER` code that Benjamin removed (see [CMT-JAN-3](#cmt-jan-3)). Fixed in subsequent patchsets — PS27 passes CI.

**Status for Owen:** No action needed — fixed by subsequent patchset.

---

## Inline Comments — Releasenotes

<a name="cmt-rad-6"></a>

### CMT-RAD-6 — Mention new settings in release notes — RESOLVED

**Author:** Radomir Dopieralski | **File:** `releasenotes/notes/enable-mfa-from-horizon-d53fd6f4453b2abb.yaml` L14 | **PS:** 16

> Would be nice to also mention the new settings here.

**Reply (Benjamin Lasseye, PS16):**
> Done

**AI Assessment:** Radomir suggested expanding release notes to cover new settings. Resolved.

**Status for Owen:** No action needed.

---

## Comment Statistics

| Reviewer | Total Comments | Resolved | Pending |
|----------|--------------|----------|---------|
| Ivan Anfimov | 14 | 14 | 0 |
| Benjamin Lasseye (author) | 30 | 26 | 4 |
| Radomir Dopieralski | 6 | 6 | 0 |
| Jan Jasek | 7 | 3 | 4 |
| Owen McGonagle | 9 | 5 | 4 |
| Zuul | 1 | 1 | 0 |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| ~~Hardcoded URL breaks WEBROOT deployments (404 for QR code)~~ | ~~HIGH~~ | ~~RESOLVED~~ |
| ~~Verify dead code removal (`OPENSTACK_KEYSTONE_MFA_ISSUER` / L216 function)~~ | ~~HIGH~~ | ~~RESOLVED~~ |
| ~~Jan Jasek wizard UX confirmation needed~~ | ~~MEDIUM~~ | ~~RESOLVED~~ |
| ~~Ivan's Google Authenticator suggestions (2 inline threads)~~ | ~~MEDIUM~~ | ~~RESOLVED~~ |
| ~~Commit message typos (3 typos)~~ | ~~LOW~~ | ~~RESOLVED~~ |
| ~~Help text wording nit (dropdown reference)~~ | ~~LOW~~ | ~~RESOLVED~~ |
| ~~Missing space in string~~ | ~~LOW~~ | ~~RESOLVED~~ |
| MFA credential delete workflow issue — Jan can't reproduce Owen's report | HIGH | OPEN |
| Jan Jasek Code-Review -1 needs to be cleared | HIGH | OPEN |
| No CR+2 votes yet — needs 2x CR+2 from core reviewers | HIGH | OPEN |
