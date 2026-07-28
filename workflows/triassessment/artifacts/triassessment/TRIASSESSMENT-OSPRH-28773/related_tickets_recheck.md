# Related Tickets RECHECK: OSPRH-28773

## Migration Complete — Decommission Phase

**Status:** 🎯 Final Step — File ServiceNow decommission ticket

---

## 1. Ticket Hierarchy (Updated)

| Level | Ticket | Title | Status | Owner | Progress |
|-------|--------|-------|--------|-------|----------|
| **Epic** | [OSPRH-28232](https://issues.redhat.com/browse/OSPRH-28232) | Evaluate PSI Migration Options - Ops - Platform Services | In Progress | (No assignee) | Multi-team (rhos-dfg-ui nearing completion) |
| **Story** | [OSPRH-28773](https://issues.redhat.com/browse/OSPRH-28773) | File decommission ticket for rhos-dfg-UI when workloads are moved | In Progress | Owen McGonagle | 80% complete (migration done, paperwork remains) |

## 2. Migration Timeline

```
COMPLETED PHASES:
├─ Phase 0: Planning & Assessment ............................ ✅ DONE (Apr-May 2026)
├─ Phase 1: ITUp Tenant Onboarding ........................... ✅ DONE (May 2026)
│   ├─ Rover group creation: rhos-role-ui
│   ├─ AppCode acquisition
│   ├─ CMDB ID assignment
│   └─ ServiceNow tenant request filed & approved
├─ Phase 2: ITUp Tenant Configuration ........................ ✅ DONE (May-Jun 2026)
│   ├─ Quota/limits tuned
│   ├─ Egress firewall rules configured
│   ├─ VM templates created
│   └─ ESS compliance prep
├─ Phase 3: Workload Migration ............................... ✅ DONE (Jun 2026)
│   ├─ Owen's VMs migrated (9 instances → ITUp)
│   ├─ Jan's VMs migrated (9 instances → ITUp)
│   ├─ Ashish's VMs migrated (3 instances → ITUp)
│   └─ PSI instances deleted
└─ Phase 4: PSI Decommission ................................. 🔄 IN PROGRESS
    ├─ Verify all workloads migrated ........................ ✅ DONE
    ├─ File ServiceNow decommission ticket .................. ⬅️ DO TOMORROW
    ├─ Wait for IT to close PSI project ..................... ⏳ PENDING
    └─ Close OSPRH-28773 .................................... ⏳ PENDING
```

## 3. Blocking Chain (Current State)

```
COMPLETED WORK:
  ✅ OSPRH-28773 (Assess workloads) 
  ✅ [Implied] Plan ITUp migration
  ✅ [Implied] Execute ITUp migration
  ✅ [Implied] Validate ITUp VMs operational
  ✅ [Implied] Delete PSI instances

REMAINING WORK:
  ⬅️ File ServiceNow decommission ticket (TOMORROW)
       ↓
  ⏳ Wait for IT to process (1-3 weeks)
       ↓
  ⏳ Close OSPRH-28773 (once ServiceNow resolves)
       ↓
  ⏳ Update OSPRH-28232 parent epic (rhos-dfg-ui complete)
```

**Notes:**
- No technical blockers remain
- Only administrative cleanup pending
- ServiceNow ticket is the final gate

## 4. Cross-Team Dependencies (Updated)

| Dependency | Team | Ticket | Status | Notes |
|------------|------|--------|--------|-------|
| Parent epic coordination | rhos-dfg-pidone | Unknown | Unknown | Parallel effort (check with Mike Orazi) |
| Parent epic coordination | rhos-dfg-security | Unknown | Unknown | Parallel effort (check with Mike Orazi) |
| ServiceNow processing | IT Cloud Services | (Filed tomorrow) | Pending | 1-3 week SLA expected |
| Epic closure approval | PSI Migration Leads | OSPRH-28232 | In Progress | morazi, mburns, artom |

**Contact Points:**
- **Michael Orazi** (morazi@redhat.com) — Epic reporter, PSI migration lead — notify when decommission ticket filed
- **Julio Morrondo** (jmorrondo@redhat.com) — IT Cloud OpenShift lead — CC on ServiceNow ticket if issues arise
- **IT Cloud Services** — ServiceNow assignee group

## 5. Resolution Path: FINAL STEP

### Current State: ✅ Migration Complete, ServiceNow Filing Pending

**Tomorrow's Workflow:**

**Step 1: Pre-Flight Check (10 minutes)**
- Verify zero PSI instances: `openstack --os-cloud openstack server list`
- Verify ITUp VMs operational: `oc get vms -n rhos-dfg-ui--runtime-int`
- Confirm team migrated: Check with Jan, Ashish

**Step 2: File ServiceNow Ticket (20 minutes)**
- Navigate to: https://redhat.service-now.com/
- Search for: "PSI tenant decommission" form
- Fill out details (see Section 3 of triage_assessment_recheck.md for full template)
- Submit and copy ticket number (e.g., RITM2345678)

**Step 3: Update Tracking (10 minutes)**
- Add comment to OSPRH-28773: "ServiceNow decommission ticket filed: RITM[number]"
- Ping Michael Orazi on Slack: "@morazi rhos-dfg-ui decommission ticket filed: RITM[number]"
- Update parent epic OSPRH-28232 if it has a tracking field

**Step 4: Monitor (Passive — 1-3 weeks)**
- Day 3: Check ServiceNow ticket status
- Week 1: Ping #help-it-cloud-openshift if no movement
- Week 2: Escalate to Michael Orazi if stuck
- Week 3: Escalate to Julio Morrondo if still stuck

**Step 5: Close OSPRH-28773 (5 minutes — when ServiceNow resolves)**
- Transition ticket to "Done"
- Add final comment with ServiceNow resolution date
- Update parent epic with rhos-dfg-ui completion

**Total Active Time:** ~45 minutes tomorrow, then passive waiting

---

## 6. Success Metrics

### Migration Success Indicators (All ✅ Complete)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Workloads migrated** | 100% | 21/21 instances | ✅ DONE |
| **PSI instances deleted** | 0 remaining | 0 | ✅ DONE |
| **ITUp VMs operational** | All team VMs running | Owen, Jan, Ashish confirmed | ✅ DONE |
| **Documentation created** | Complete migration guide | 40+ docs at imigrate server | ✅ DONE |
| **Team trained** | All members can use ITUp | Owen, Jan, Ashish operational | ✅ DONE |

### Decommission Success Indicators (Pending Tomorrow)

| Metric | Target | Status |
|--------|--------|--------|
| **ServiceNow ticket filed** | Filed within 1 business day | ⬜ DO TOMORROW |
| **IT response time** | <3 business days | ⏳ PENDING |
| **PSI project closure** | <3 weeks from filing | ⏳ PENDING |
| **OSPRH-28773 closed** | Within 1 day of ServiceNow resolution | ⏳ PENDING |
| **OSPRH-28232 updated** | rhos-dfg-ui marked complete | ⏳ PENDING |

---

## 7. Lessons Learned (For Other Teams)

Based on rhos-dfg-ui's successful migration, here's what worked well:

### What Worked Well

1. **Comprehensive Documentation** — The imigrate server (http://10.0.151.101:8074/) with 40+ docs provided clear step-by-step guidance
2. **Phased Approach** — Breaking migration into 4 phases prevented overwhelming the team
3. **Team Coordination** — All 3 team members (Owen, Jan, Ashish) coordinated migration to avoid conflicts
4. **Reference from Other DFGs** — Learning from DFG:Security's RITM2304473 decommission ticket
5. **ITUp Primer** — David Peacock's technical guide made VM provisioning straightforward

### Recommendations for Other Teams

**DO:**
- ✅ Document your PSI inventory **first** (instance names, sizes, purposes)
- ✅ Create comprehensive migration docs **before** you start migrating
- ✅ Test ITUp VM creation with **one instance** before migrating everything
- ✅ Keep PSI instances **until** ITUp VMs are validated operational
- ✅ Reference other teams' ServiceNow tickets for decommission template

**DON'T:**
- ❌ Delete PSI instances before confirming ITUp VMs work
- ❌ Rush the migration without team coordination
- ❌ Assume ITUp works exactly like PSI (networking, SSH, quotas all differ)
- ❌ Skip documentation — future you will thank present you
- ❌ Forget to file the ServiceNow decommission ticket (this story!)

---

## 8. Sprint Health (Final Assessment)

### 🟢 GREEN — Ready for Closure

**Reasons:**
- ✅ Migration **100% complete** (all workloads on ITUp)
- ✅ Documentation **comprehensive** (imigrate server operational)
- ✅ Team **operational** (no blockers reported)
- ✅ Final step **clearly defined** (ServiceNow ticket template ready)
- ✅ Timeline **realistic** (45 minutes of work, 1-3 weeks passive wait)

**Risk Level:** **LOW**
- ServiceNow filing is administrative, not technical
- Precedent exists (DFG:Security RITM2304473)
- No dependencies on external teams beyond IT processing

**Confidence:** **95%** that this story will close successfully

---

## 9. Post-Closure: What's Next for rhos-dfg-ui

Once OSPRH-28773 is closed, the team should:

1. **Celebrate** 🎉 — Major infrastructure migration successfully completed
2. **Archive PSI docs** — Keep them for reference but mark as historical
3. **Update team onboarding** — New members need ITUp instructions, not PSI
4. **Share knowledge** — Present migration experience at RHOS team meeting
5. **Monitor ITUp** — Ensure ongoing operations remain stable
6. **Plan for ITUp optimizations** — Tune quotas, refine VM templates, explore CI/CD integration

**ITUp Operations Resources:**
- Console: [prod-stable-spoke1-dc-iad2](https://console-openshift-console.apps.prod-stable-spoke1-dc-iad2.itup.redhat.com/)
- Slack: #help-it-cloud-openshift
- Docs: http://10.0.151.101:8074/

---

**Generated:** 2026-07-09 21:30:00 UTC  
**Skill:** /triassessment --recheck  
**Model:** claude-sonnet-4-5@20250929  
**Ticket:** [OSPRH-28773](https://issues.redhat.com/browse/OSPRH-28773)  
**Run:** run-002 (recheck after migration completion)
