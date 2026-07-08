# Review 977939 — Live Comment Tracker

**Review:** https://review.opendev.org/c/openstack/horizon/+/977939
**Title:** Add Horizon panel to enable TOTP MFA enrollment
**Author:** Benjamin Lasseye
**Status:** NEW
**Current Patchset:** 25
**Zuul:** Verified +1 (passing)
**Files Changed:** 22 (new MFA panel under `settings/mfa/`, API additions in `keystone.py`, docs, defaults, release notes, requirements)
**Reviewers:** Ivan Anfimov, Radomir Dopieralski, Jan Jasek, Owen McGonagle

---

## Scan Log

| # | Date | Scanner | Notes |
|---|------|---------|-------|
| 1 | 2026-06-19 | AI (Claude) | Initial scan — 28 comment threads from 5 participants (4 reviewers + author) |

---

## Where Things Are At / What To Do Next

### Overall Status

This review adds a new Settings panel for TOTP MFA enrollment in Horizon. It has been through 25 patchsets since February 2026, with feedback from 4 reviewers: Ivan Anfimov (early rounds), Radomir Dopieralski (PS16), Jan Jasek (PS21), and Owen McGonagle (PS25). Most early-round feedback has been addressed. The latest patchset (PS25) has Zuul Verified+1 but no Code-Review or Workflow votes yet.

The review has significant momentum — the author has been responsive to feedback, and the most recent comments (PS25) are nit-level. However, two threads from Jan Jasek on PS21 remain unresolved and require attention before this can progress.

### Score Summary

| Label | Value | Who |
|-------|-------|-----|
| Verified | +1 | Zuul |
| Code-Review | (none) | — |
| Workflow | (none) | — |

### What You Should Do Next

1. **HIGH** — Address Jan Jasek's hardcoded URL bug ([CMT-JAN-2](#cmt-jan-2)) — this is a functional defect (404 when WEBROOT is customized)
2. **HIGH** — Verify Jan Jasek's `OPENSTACK_KEYSTONE_MFA_ISSUER` concern ([CMT-JAN-3](#cmt-jan-3)) has been fixed in PS25
3. **MEDIUM** — Address Ivan Anfimov's suggestion to add Google Authenticator to app list ([CMT-IVA-8](#cmt-iva-8), [CMT-IVA-9](#cmt-iva-9))
4. **LOW** — Fix commit message typos per Owen's comment ([CMT-OWN-1](#cmt-own-1))
5. **LOW** — Fix nit: dropdown wording ([CMT-OWN-2](#cmt-own-2)) and missing space ([CMT-OWN-3](#cmt-own-3))
6. **LOW** — Address Jan Jasek's wizard UX feedback ([CMT-JAN-1](#cmt-jan-1)) — author already acknowledged and implemented `wizard=True`

### Open Threads Requiring Attention

| Thread | File | Status | Owner | Priority |
|--------|------|--------|-------|----------|
| [CMT-JAN-2](#cmt-jan-2) | `_select_credential_with_qr.html` | NEEDS FIX | Author (Benjamin) | HIGH |
| [CMT-JAN-3](#cmt-jan-3) | `workflows.py` | VERIFY FIX | Author (Benjamin) | HIGH |
| [CMT-IVA-8](#cmt-iva-8) | `workflows.py` | POSTED — WAITING FOR RESPONSE | Author (Benjamin) | MEDIUM |
| [CMT-IVA-9](#cmt-iva-9) | `workflows.py` | POSTED — WAITING FOR RESPONSE | Author (Benjamin) | MEDIUM |
| [CMT-JAN-1](#cmt-jan-1) | Patchset-level | POSTED — AUTHOR REPLIED | Jan Jasek | MEDIUM |
| [CMT-OWN-1](#cmt-own-1) | Patchset-level | POSTED — WAITING FOR RESPONSE | Author (Benjamin) | LOW |
| [CMT-OWN-2](#cmt-own-2) | `workflows.py` | POSTED — WAITING FOR RESPONSE | Author (Benjamin) | LOW |
| [CMT-OWN-3](#cmt-own-3) | `workflows.py` | POSTED — WAITING FOR RESPONSE | Author (Benjamin) | LOW |

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
### CMT-JAN-1 — Wizard UX feedback (asterisk position + button flow) — POSTED — AUTHOR REPLIED

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

**AI Assessment:** Jan raised two UX issues: (1) misplaced asterisk on required checkbox, (2) confusing button flow where "Enable MFA" is visible but non-functional on early tabs. Benjamin acknowledged and indicated he would use `wizard = True` to fix the button flow. This is a suggestion-level improvement. The author appears to have implemented the wizard change (later patchsets exist), but Jan has not confirmed resolution.

**Status for Owen:** Jan's feedback is valid UX improvement. The author acknowledged and likely addressed in PS22+. This thread should be verified by Jan on the latest patchset.

---

<a name="cmt-iva-7"></a>
### CMT-IVA-7 — Google Authenticator mention — RESOLVED

**Author:** Ivan Anfimov | **PS:** 21

> Hello, I think more friendly add information about Google app 😉

**Reply (Benjamin Lasseye, PS21):**
> I intentionally chose to focus only on free and open-source applications. I'm open to change.

**AI Assessment:** Ivan suggested mentioning Google Authenticator. Benjamin explained the FOSS-only choice but left room for change. Thread marked resolved on Gerrit. Related inline suggestions ([CMT-IVA-8](#cmt-iva-8), [CMT-IVA-9](#cmt-iva-9)) to add Google Authenticator to the app list remain unresolved.

**Status for Owen:** No action needed on this patchset-level thread. See inline threads for the specific code suggestions.

---

<a name="cmt-recheck-1"></a>
### CMT-RECHECK-1 — Recheck (PS22) — INFORMATIONAL

**Author:** Benjamin Lasseye | **PS:** 22

> recheck

**AI Assessment:** Two recheck comments on PS22 to trigger CI re-runs. Informational only.

**Status for Owen:** No action needed.

---

<a name="cmt-own-1"></a>
### CMT-OWN-1 — Commit message typos — POSTED — WAITING FOR RESPONSE

**Author:** Owen McGonagle | **PS:** 25

> I found a few typos in the commit message
> "activited" -> "activated"
> "Custome" -> "Custom"
> "exemple" ->"example"
>
> first pass at testing the creation of my new credential using FreeOTP is working nicely.

**AI Assessment:** Owen identified three typos in the commit message and noted positive testing results with FreeOTP. Nit-level fix required. The positive testing note is encouraging for the review.

**Status for Owen:** This is your comment. Waiting for Benjamin to fix the typos in the next patchset.

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
### CMT-IVA-8 — Add Google Authenticator to app list (L41) — POSTED — WAITING FOR RESPONSE

**Author:** Ivan Anfimov | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L41 | **PS:** 21

> ```suggestion
>             "- You will need an authenticator app (Google Authenticator, "
> ```

**AI Assessment:** Suggestion to add Google Authenticator to the list of authenticator apps mentioned in the help text. Related to [CMT-IVA-7](#cmt-iva-7) patchset-level discussion about FOSS-only policy. Still unresolved — the author has not responded to this inline suggestion specifically. Ivan's patchset-level comment was marked resolved, but these inline suggestions remain open.

**Status for Owen:** Low priority. The author expressed a preference for FOSS-only apps. This is a judgment call — Google Authenticator is widely known and would help users, but is not FOSS. No action needed from you; author should decide.

---

<a name="cmt-iva-9"></a>
### CMT-IVA-9 — Add Aegis Authenticator to app list (L42) — POSTED — WAITING FOR RESPONSE

**Author:** Ivan Anfimov | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L42 | **PS:** 21

> ```suggestion
>             "Aegis Authenticator, FreeOTP, etc.).\n"
> ```

**AI Assessment:** Companion to [CMT-IVA-8](#cmt-iva-8). Suggests adding "Aegis Authenticator" to the list. Still unresolved.

**Status for Owen:** Same as CMT-IVA-8. Author should decide on app list.

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

**AI Assessment:** Radomir correctly identified that the `cryptography` library import needed to be added to `requirements.txt`. Benjamin confirmed and added it. The `requirements.txt` diff in PS25 shows `+1` line added. Resolved.

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
### CMT-JAN-2 — Hardcoded URL breaks WEBROOT deployments (404 bug) — POSTED — WAITING FOR RESPONSE

**Author:** Jan Jasek | **File:** `openstack_dashboard/dashboards/settings/mfa/templates/mfa/_select_credential_with_qr.html` L112 | **PS:** 21

> As this Django URL is registered correctly in `urls.py`, what is the reason to use `/settings/mfa/credential/` hardcoded here. If I am right then with this implementation it is expected that Horizon is at the site root which can be (I think quite often is) customized using `WEBROOT` or proxy prefix.
>
> edit: Now when I am verifying your patch practically, I can not see QR code at all and I am getting 404 in inspect->network, because the code is calling `http://xxxx/settings/mfa/credential/__new__/qr/`
> But reality of my deployment is: `http://xxxx/dashboard/settings/mfa/....`

**AI Assessment:** **This is a functional bug, not just a style issue.** Jan confirmed a 404 error when Horizon is deployed with a custom `WEBROOT` (e.g., `/dashboard/`). The template hardcodes `/settings/mfa/credential/` instead of using Django's `{% url %}` template tag, which respects `WEBROOT`. This will break any deployment where Horizon is not at the site root. This is blocking — the QR code cannot be displayed in WEBROOT-configured deployments.

**Status for Owen:** HIGH priority. This is a real bug confirmed by Jan's testing. The fix should use `{% url 'horizon:settings:mfa:credential' %}` or equivalent Django URL resolution instead of the hardcoded path. Check if PS25 addressed this — if not, flag to the author.

---

<a name="cmt-jan-3"></a>
### CMT-JAN-3 — OPENSTACK_KEYSTONE_MFA_ISSUER undefined setting + dead code — POSTED — AUTHOR REPLIED

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

**AI Assessment:** Jan found two issues: (1) reference to an undefined setting `OPENSTACK_KEYSTONE_MFA_ISSUER` that should be `OPENSTACK_TOTP_QRCODE_ISSUER`, and (2) dead code in success/failure message formatting (missing `%s` placeholder). Benjamin acknowledged both and said he would delete the function. Thread is still unresolved — needs verification that PS25 contains the fix.

**Status for Owen:** HIGH priority to verify. Benjamin said he'd delete the function — check if the code at L216 in `workflows.py` still exists in PS25. If the dead code is gone, this can be considered addressed (pending Jan's confirmation).

---

## Inline Comments — Owen McGonagle

<a name="cmt-own-2"></a>
### CMT-OWN-2 — Dropdown wording nit — POSTED — WAITING FOR RESPONSE

**Author:** Owen McGonagle | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L80 | **PS:** 25

> Just a nit pick... before the first credential is created, the dropdown is not yet there...
>
> Mabye change it to:
> "After you create your first credential, select one from the provided dropdown list"
>
> btw - so far, so good - I was able to create my credential using the FreeOTP app

**AI Assessment:** Nit — Owen suggests improving the help text wording because it references a dropdown that doesn't exist yet. Good UX observation. The positive testing note confirms FreeOTP integration works.

**Status for Owen:** This is your comment. Waiting for author to address in next patchset.

---

<a name="cmt-own-3"></a>
### CMT-OWN-3 — Missing space after "current" — POSTED — WAITING FOR RESPONSE

**Author:** Owen McGonagle | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L123 | **PS:** 25

> missing space after current

**AI Assessment:** Typo-level nit — missing whitespace in a string. Simple fix.

**Status for Owen:** This is your comment. Waiting for author to fix.

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

## Inline Comments — Zuul

<a name="cmt-zuul-1"></a>
### CMT-ZUUL-1 — Unused import (pep8 F401) — RESOLVED (by new patchset)

**Author:** Zuul | **File:** `openstack_dashboard/dashboards/settings/mfa/workflows.py` L15 | **PS:** 23

> pep8: F401 'django.conf.settings as django_settings' imported but unused

**AI Assessment:** Automated pep8 finding from PS23. The unused import `django_settings` was likely left over from the `OPENSTACK_KEYSTONE_MFA_ISSUER` code that Benjamin said he would remove (see [CMT-JAN-3](#cmt-jan-3)). PS25 exists and has Verified+1, so this was presumably fixed.

**Status for Owen:** No action needed — fixed by subsequent patchset (PS25 passes CI).

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
| Ivan Anfimov | 14 | 11 | 3 |
| Benjamin Lasseye (author) | 21 | 21 | 0 |
| Radomir Dopieralski | 6 | 6 | 0 |
| Jan Jasek | 4 | 0 | 4 |
| Owen McGonagle | 6 | 2 | 4 |
| Zuul | 1 | 1 | 0 |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| Hardcoded URL breaks WEBROOT deployments (404 for QR code) | HIGH | OPEN |
| Verify dead code removal (`OPENSTACK_KEYSTONE_MFA_ISSUER` / L216 function) | HIGH | OPEN |
| Jan Jasek wizard UX confirmation needed | MEDIUM | OPEN |
| Ivan's Google Authenticator suggestions (2 inline threads) | MEDIUM | OPEN |
| Commit message typos (3 typos) | LOW | OPEN |
| Help text wording nit (dropdown reference) | LOW | OPEN |
| Missing space in string | LOW | OPEN |
| No Code-Review votes yet — needs 2x CR+2 from core reviewers | HIGH | OPEN |
