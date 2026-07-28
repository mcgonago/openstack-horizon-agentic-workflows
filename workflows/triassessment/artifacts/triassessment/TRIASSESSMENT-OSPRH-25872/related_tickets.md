# Related Tickets: OSPRH-25872

**Ticket:** [OSPRH-25872](https://redhat.atlassian.net/browse/OSPRH-25872)  
**Generated:** 2026-07-28

---

## Ticket Hierarchy

| Level | Ticket | Title | Type | Status | Assignee | Created | Updated |
|-------|--------|-------|------|--------|----------|---------|---------|
| **RFE** | [RHOSRFE-300](https://redhat.atlassian.net/browse/RHOSRFE-300) | SSO logout from Horizon | Feature Request | Refinement | (unassigned) | (unknown) | (unknown) |
| **Epic** | [OSPRH-25871](https://redhat.atlassian.net/browse/OSPRH-25871) | Make Horizon redirect the user on logout to the right SSO logout page | Epic | In Progress | (unassigned) | (unknown) | (unknown) |
| **Spike** | [OSPRH-25872](https://redhat.atlassian.net/browse/OSPRH-25872) | Research customer needs for the SSO logout redirect in Horizon | Spike | In Progress | Owen McGonagle | 2026-01-28 | 2026-07-27 |

**Hierarchy flow:**
```
RHOSRFE-300 (Feature Request from customers)
    │
    ├── triggers ──> OSPRH-25871 (Epic: Implement the feature)
                          │
                          └── parent of ──> OSPRH-25872 (Spike: Research requirements)
```

---

## Related Customer Cases & Documentation Tasks

| Ticket | Title | Type | Status | Priority | Relationship |
|--------|-------|------|--------|----------|--------------|
| [RHOSPPRIO-814](https://redhat.atlassian.net/browse/RHOSPPRIO-814) | Telefónica EU audit: OIDC logout cookie persistence | Task (customer case) | Closed | Critical | Historical customer pain point — **closed**, but pattern repeats |
| [OSPRH-15245](https://redhat.atlassian.net/browse/OSPRH-15245) | Horizon "Logout" doesn't work with federation / oidc | (unknown) | (unknown) | (unknown) | Early bug report (~2020-2022 era) |
| [OSPRH-19420](https://redhat.atlassian.net/browse/OSPRH-19420) | Create and test a RHOSO procedure that logs customers out of SSO when they log out of Horizon | Story | Backlog | Undefined | Documentation task **blocked until** OSPRH-25871 is implemented |

---

## Blocking Chain

**Current state:** No blockers for OSPRH-25872 (spike work is independent).

**Post-spike blocking:**

```
┌─────────────────────────────────────────────────────────────────┐
│ OSPRH-25872 (THIS SPIKE)                                        │
│ Status: In Progress                                             │
│ Output: Requirements collected (triage_assessment.md)           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ completes
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ OSPRH-25871 (EPIC) — Implementation Story                       │
│ Status: In Progress                                             │
│ Estimated effort: 8 story points (implementation) + 3 (QE)      │
└──────────────────────────┬──────────────────────────────────────┘
                           │ must complete before
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ OSPRH-19420 (Documentation)                                     │
│ Status: Backlog                                                 │
│ Blocked by: Need working feature to document                   │
└─────────────────────────────────────────────────────────────────┘
```

**Critical path:**
1. Close OSPRH-25872 (spike) → provides requirements
2. Implement OSPRH-25871 → enables feature
3. QE validates feature per OSPRH-19420 acceptance criteria
4. Assign OSPRH-19420 to docs team with tested procedure

---

## Cross-Team Dependencies

| Dependency | Team | Status | Notes |
|------------|------|--------|-------|
| Horizon upstream alignment | OpenStack Horizon core team | ✅ Aligned | Radomir Dopieralski (OSPRH team lead + upstream core) is both reporter and epic owner — no upstream objection expected |
| Customer IdP configurations | Customer Success / Support | ⚠️ Needed for QE validation | Must test with real OIDC, SAML2, and ADFS deployments (reference RHOSPPRIO-814 for Telefónica config) |
| Documentation procedure | RHOSO Docs team | ⏸️ Waiting | Blocked until OSPRH-19420 is ready (after implementation + QE) |
| QE test matrix | RHOSO QE | ⏸️ Waiting | Waiting for implementation story to complete |

---

## Resolution Paths

### Current Situation

**OSPRH-25872 (this spike):** In progress, UI Sprint 30 (ends 2026-08-10).

**Recommended path forward:**

1. **This sprint (UI Sprint 30):**
   - ✅ Complete spike research (this document = deliverable)
   - ✅ Generate fix proposals (see `proposed_fixes.md`)
   - ➡️ Demo findings to team (sprint review)
   - ➡️ Create implementation story under OSPRH-25871 (or assign work to existing sibling ticket)

2. **Next sprint (UI Sprint 31, starts ~2026-08-10):**
   - Implement `WEBSSO_LOGOUT_REDIRECT_MAPPING` setting
   - Modify `openstack_auth/views.py:logout()` to read `request.session['auth_type']`
   - Write unit tests for multi-provider logout scenarios
   - Update Horizon settings documentation
   - Submit patch to upstream `openstack/horizon` (Gerrit topic: `websso-multi-provider-logout`)

3. **Sprint 32 or 33:**
   - QE validation with real IdP configurations (OIDC, SAML2, ADFS)
   - Address review feedback from upstream (if any)
   - Backport upstream patch to RHOSO if needed
   - Assign OSPRH-19420 to docs team with tested procedure

### If Blocked (Unlikely)

**Potential blocker:** Upstream Horizon core reviewers prefer different approach than `WEBSSO_LOGOUT_REDIRECT_MAPPING`.

**Mitigation:**
- Radomir Dopieralski (upstream core + OSPRH team lead) is the reporter → unlikely to object to his own design
- Review 996428 shows external contributors proposing similar solutions → validates approach
- If upstream wants different implementation, we can align during patch review (pre-merge feedback is cheap)

---

## Upstream Context

**OpenDev Gerrit Reviews:**

| Review | Subject | Status | Relevance |
|--------|---------|--------|-----------|
| [996428](https://review.opendev.org/c/openstack/horizon/+/996428) | Add `WEBSSO_POST_LOGOUT_URL` setting for proper SSO/OIDC logout | NEW | **Duplicate effort** — solves same problem as existing `WEBSSO_DEFAULT_REDIRECT_LOGOUT` for single-provider case only |
| [988164](https://review.opendev.org/c/openstack/horizon/+/988164) | Fix WebSSO logout to clear both sessions | MERGED | Related — ensures session cleanup happens correctly |
| 986441 | Enable WebSSO configuration | MERGED | Foundational work for WebSSO support |

**Key insight from review 996428:**
> "This only works when you only have configured a single websso login -- because you can only configure a single redirect URL. We are working on a more versatile solution, where you can configure separate redirect URLs for multiple websso providers."  
> — Radomir Dopieralski (upstream Horizon core)

**Translation:** The upstream community knows the limitation exists and expects a multi-provider solution. This epic (OSPRH-25871) IS that solution.

---

## External References

- [Horizon WebSSO configuration docs](https://docs.openstack.org/horizon/latest/configuration/settings.html#websso-default-redirect-logout) — single-provider logout redirect (current state)
- [Deploying RHOSO with federated IDP](https://docs.redhat.com/en/documentation/red_hat_openstack_services_on_openshift/18.0/html/configuring_security_services/assembly_rhoso-federation#proc_deploying-rhoso-with-a-federated-idp_rhoso-federation) — RHOSO federation setup procedure
- [RHOSO Dashboard configuration guide](https://docs.redhat.com/en/documentation/red_hat_openstack_services_on_openshift/18.0/html/configuring_the_dashboard/) — where OSPRH-19420 procedure will land

---

Generated: 2026-07-28 | Skill: /triassessment | Model: claude-sonnet-4-5@20250929
