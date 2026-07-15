# Related Tickets: OSPRH-28773

## 1. Ticket Hierarchy

| Level | Ticket | Title | Status | Owner |
|-------|--------|-------|--------|-------|
| **Epic** | OSPRH-28232 | Evaluate PSI Migration Options - Ops - Platform Services | In Progress | (No assignee) |
| **Story** | OSPRH-28773 | File decomission ticket for rhos-dfg-UI when workloads are moved | In Progress | Owen McGonagle |

## 2. Parent Epic Details

### OSPRH-28232: Evaluate PSI Migration Options - Ops - Platform Services

**Status:** In Progress  
**Priority:** Undefined  
**Scope:** Multi-team PSI migration coordination

**Migration Complete for rhos-dfg-ui:**
- ✅ All devstack VMs migrated to ITUp tenant (2026-07-09 verified)
- ✅ ServiceNow decommission ticket filed: UR0207195 (2026-07-10)
- ⏳ Awaiting ServiceNow response on decommission approach

**Other Teams (pidone, security):**
- Status unknown — separate tracking

## 3. Blocking Chain

```
Completion sequence (executed):
  1. ✅ OSPRH-28773 (Assess workloads) — COMPLETE
  2. ✅ Migrate workloads to ITUp — COMPLETE (2026-07-09)
  3. ✅ File ServiceNow decommission ticket — COMPLETE (UR0207195, 2026-07-10)
  4. ⏳ ServiceNow resolution — WAITING (blocks OSPRH-28773 closure)
  5. ⏳ Close OSPRH-28773 — READY (after ServiceNow response)
  6. ⏳ Update OSPRH-28232 — PENDING (mark rhos-dfg-ui complete)
```

**Current Blocker:**
- ServiceNow ticket UR0207195 — awaiting decommission approval
- No technical blockers — administrative process only

## 4. Cross-Team Dependencies

| Dependency | Team | Status | Notes |
|------------|------|--------|-------|
| ServiceNow decommission | IT Infrastructure | Pending | Ticket UR0207195 filed, awaiting response |
| Parent epic completion | rhos-dfg-pidone | Unknown | Separate PSI migration tracking |
| Parent epic completion | rhos-dfg-security | Unknown | Separate PSI migration tracking |

**Contact Points:**
- **Michael Orazi** (morazi@redhat.com) — Epic reporter, PSI migration lead
- **Owen McGonagle** (omcgonag@redhat.com) — Story assignee, rhos-dfg-ui team

## 5. Resolution Paths

### Current State: Waiting on ServiceNow Response

**Executed Path: ITUp Migration (Path 2)**
- ✅ All devstack VMs migrated to ITUp tenant
- ✅ Team verified new environment (2026-07-09)
- ✅ ServiceNow decommission ticket filed (UR0207195, 2026-07-10)
- ⏳ Awaiting ServiceNow decision: immediate decommission vs "end of life" labeling

**Next Steps:**

**Option A: ServiceNow Approves Immediate Decommission**
1. Close OSPRH-28773 as DONE (link ServiceNow ticket)
2. Update parent epic OSPRH-28232 (mark rhos-dfg-ui complete)
3. **Estimated Effort:** < 30 minutes (administrative closure)

**Option B: ServiceNow Approves "End of Life" Labeling**
1. Verify approach with team (old env preserved for comparison)
2. Close OSPRH-28773 as DONE (document preservation approach)
3. Update parent epic OSPRH-28232 (mark rhos-dfg-ui complete)
4. **Estimated Effort:** < 1 hour (verification + documentation)

**Option C: ServiceNow Requests Additional Action**
1. Execute requested action (unlikely based on ticket content)
2. Update OSPRH-28773 with new status
3. Close when all requirements satisfied
4. **Estimated Effort:** Variable (depends on request)

## 6. Recommended Next Actions

### Immediate (Before Sprint 28 Ends: 2026-07-13)

1. **Monitor ServiceNow Ticket UR0207195**
   - Check for response on decommission approach
   - Respond to any IT questions promptly

2. **Close OSPRH-28773 When ServiceNow Resolves**
   - Transition to DONE state
   - Link ServiceNow ticket in closure comment
   - Document final outcome (immediate decommission or EOL labeling)

3. **Update Parent Epic OSPRH-28232**
   - Add comment: "rhos-dfg-ui migration complete"
   - Link to OSPRH-28773 closure
   - Check if other teams (pidone, security) need coordination

### No Further Technical Work Required
- Migration complete
- No blockers within team control
- Administrative closure only

## 7. Sprint Health Indicators

### Status: GREEN (On Track for Closure)

**Work Complete:**
- ✅ PSI workload assessment complete
- ✅ ITUp migration executed and verified
- ✅ ServiceNow decommission ticket filed

**Waiting On:**
- ⏳ ServiceNow response (external, non-blocking to team)

**Expected Closure:**
- Before sprint 28 ends (2026-07-13)
- No technical risk
- Administrative process only

---

**Generated:** 2026-07-10 | Skill: /triassessment | Model: claude-sonnet-4-5@20250929
