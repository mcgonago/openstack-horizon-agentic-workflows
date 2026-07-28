# Related Tickets: OSPRH-33457

**Spike:** [OSPRH-33457](https://redhat.atlassian.net/browse/OSPRH-33457) — RCA of bug Horizon workload SA granted hostmount-anyuid SCC and pod CRUD with allowPrivilegeEscalation true

---

## 1. Ticket Hierarchy

| Level | Ticket | Title | Status | Assignee | Created | Updated |
|-------|--------|-------|--------|----------|---------|---------|
| **Epic** | [OSPRH-33189](https://redhat.atlassian.net/browse/OSPRH-33189) | [BugEpic]: Horizon workload SA granted hostmount-anyuid SCC and pod CRUD with allowPrivilegeEscalation true | (unknown) | (unknown) | (unknown) | (unknown) |
| **Bug** | [OSPRH-33188](https://redhat.atlassian.net/browse/OSPRH-33188) | Horizon workload SA granted hostmount-anyuid SCC and pod CRUD with allowPrivilegeEscalation true | (unknown) | (unknown) | (unknown) | (unknown) |
| **Spike** | [OSPRH-33457](https://redhat.atlassian.net/browse/OSPRH-33457) | RCA of bug Horizon workload SA granted hostmount-anyuid SCC and pod CRUD with allowPrivilegeEscalation true | Backlog | Jan Jasek | 2026-07-15 | 2026-07-15 |

---

## 2. Blocking Chain

```
OSPRH-33189 (BugEpic)
  │
  ├── OSPRH-33188 (Bug: Security vulnerability CVSS 7.3) [NEEDS RCA]
  │     │
  │     └── OSPRH-33457 (Spike: RCA) [IN PROGRESS] ✅ RCA Complete
  │           │
  │           └── [NEW TICKET NEEDED] Implementation: Fix excessive RBAC grants and security context
  │
  └── [POSSIBLE SIBLINGS] Other operators with similar issues?
        (ProjectGlasswing audit may have found similar patterns in nova-operator, cinder-operator, etc.)
```

**Current state:** RCA is complete. Detailed fix proposals generated (see `proposed_fixes.md`). Next action: create implementation ticket and assign to horizon-operator team.

---

## 3. Cross-Team Dependencies

| Dependency | Team | Status | Notes |
|-----------|------|--------|-------|
| RCA Spike (this ticket) | horizon-operator | **Complete** | Jan Jasek assigned, fix proposals ready for review |
| Fix Implementation | horizon-operator | Pending | New ticket needed after RCA approval |
| Security Audit | ProjectGlasswing | Complete | Audit report filed as OSPRH-33188 |
| Upstream Review | openstack-k8s-operators maintainers | Pending | Must review fix proposals before merge |
| Backport Coordination | RHOS release engineering | Pending | May need backports to RHOS 18.0, 19.0 if affected |

**No external blockers.** horizon-operator team has full ownership. Fix is self-contained (3 files, no API changes).

---

## 4. Resolution Paths

### Current State: RCA COMPLETE

**Completed:**
- ✅ Analyzed affected code in horizon-operator (pkg/, controllers/)
- ✅ Generated proposed fixes with code diffs and rationale
- ✅ Documented attack scenario and security impact
- ✅ Validated fixes against actual codebase

**Next Steps:**
1. **Review RCA findings** with Jan Jasek (assignee) and horizon-operator maintainers
2. **Approve fix proposals** in `proposed_fixes.md`
3. **Close OSPRH-33457** when RCA is approved
4. **Create implementation ticket** for Phase 2:
   - Title: "Fix excessive RBAC grants and security context (OSPRH-33188)"
   - Type: Task
   - Parent: OSPRH-33189 (BugEpic)
   - Assignee: horizon-operator team (Jan Jasek or Owen McGonagle)
   - Story Points: 3 (1-2 days implementation + testing)
5. **Implementation** (new ticket):
   - Apply Fix 1: Harden `HttpdSecurityContext()` in `pkg/horizon/funcs.go`
   - Apply Fix 2: Remove excessive RBAC in `controllers/horizon_controller.go`
   - Apply Fix 3: Disable token auto-mount in `pkg/horizon/deployment.go`
   - Update kubebuilder RBAC markers
   - Run test suite + security validation
6. **Gerrit Review** to `openstack-k8s-operators/horizon-operator`
7. **Backport** to RHOS release branches if applicable

---

## 5. Related Security Context

### ProjectGlasswing Audit

**Source:** Security audit of openstack-k8s-operators (FIND-002)  
**Scope:** Kubernetes workload configuration across all operators  
**Finding:** Horizon workload has insecure configuration (CVSS 7.3)

**Other affected operators (potential):**  
The audit methodology likely applied to all openstack-k8s-operators. Check if similar findings exist for:
- nova-operator
- cinder-operator
- neutron-operator
- glance-operator
- keystone-operator

**Recommendation:** Search Jira for other OSPRH-333XX tickets from the same audit batch.

### Security Category

**OWASP Kubernetes Top 10:**
- **K01** — Insecure Workload Configuration (PRIMARY)
- **K04** — Lack of Centralized Policy Enforcement (no admission controller blocking hostPath)

**CIS Kubernetes Benchmarks:**
- **5.2.5** — Minimize the admission of containers with allowPrivilegeEscalation
- **5.2.12** — Minimize the admission of HostPath volumes

**NIST Controls:**
- **AC-6** — Least Privilege
- **CM-7** — Least Functionality

---

## 6. Fix Proposal Summary

| Fix | File | Risk | Effort | Impact |
|-----|------|------|--------|--------|
| Fix 1: Harden SecurityContext | `pkg/horizon/funcs.go` | Low | Low (5 lines) | High security value |
| Fix 2: Remove RBAC grants | `controllers/horizon_controller.go` | Medium | Low (remove 1 SCC + 1 rule) | High security value |
| Fix 3: Disable token mount | `pkg/horizon/deployment.go` | Low | Low (1 line) | Defense-in-depth |

**Combined effort:** ~1-2 days (implementation + testing)  
**Risk:** Low (removes unused permissions, no functional dependencies identified)  
**Security impact:** Eliminates CVSS 7.3 privilege escalation path

---

## 7. Stakeholder Communication Template

**For PM/Security Team:**

> **Subject:** Security RCA Complete — OSPRH-33457 (Horizon Privilege Escalation)
> 
> **Status:** RCA complete, ready for implementation approval
> 
> **Finding:** Horizon-operator grants excessive privileges (hostmount-anyuid SCC, pod CRUD, AllowPrivilegeEscalation: true) to internet-facing workload. If an attacker achieves code execution in Horizon dashboard, they can escalate to node filesystem access (CVSS 7.3).
> 
> **Fix:** Remove unnecessary permissions across RBAC, SCC, and security context (3-file patch, ~10 lines changed). No functional impact — fixes remove permissions the workload doesn't use.
> 
> **Timeline:** Implementation ~1-2 days, testing ~1 day, review ~2-3 days → ~1 week total
> 
> **Next Action:** Approve fix proposals in `proposed_fixes.md` and create implementation ticket
> 
> **Attachments:** `triage_assessment.md`, `proposed_fixes.md`

---

Generated: 2026-07-27 | Skill: /triassessment | Model: claude-sonnet-4-5@20250929
