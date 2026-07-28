# Triage Assessment: OSPRH-33457

## Ticket Summary

| Field | Value |
|-------|-------|
| Key | [OSPRH-33457](https://redhat.atlassian.net/browse/OSPRH-33457) |
| Title | RCA of bug Horizon workload SA granted hostmount-anyuid SCC and pod CRUD with allowPrivilegeEscalation true |
| Source | Jira |
| Type | Spike |
| Status | Backlog |
| Priority | Major |
| Assignee | Jan Jasek |
| Reporter | Dea Marin |
| Created | 2026-07-27 |
| Updated | 2026-07-27 |
| Sprint | UI Sprint 30 (2026-07-27 to 2026-08-10) |
| Parent | [OSPRH-33189](https://redhat.atlassian.net/browse/OSPRH-33189) (Epic: Horizon workload SA granted hostmount-anyuid SCC and pod CRUD with allowPrivilegeEscalation true) |
| Root Bug | [OSPRH-33188](https://redhat.atlassian.net/browse/OSPRH-33188) (Security vulnerability, CVSS 7.3) |
| Components | (none) |
| Fix Versions | (none) |
| Labels | (none) |

## Technical Context

This ticket is a **root cause analysis spike** for a **Moderate-severity security vulnerability** (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N — score 7.3) in the **horizon-operator**.

**What the bug is:**

The horizon-operator unconditionally grants the Horizon workload ServiceAccount excessive permissions that create a privilege escalation path:

1. **Overprivileged SCC grants:** The ServiceAccount is granted `use` on BOTH `anyuid` AND `hostmount-anyuid` SCCs, despite the Horizon workload using only ConfigMap, Secret, and EmptyDir volumes — no hostPath volumes.

2. **Full pod CRUD:** The ServiceAccount is granted full pod operations (`create/get/list/watch/update/patch/delete`) on the Kubernetes API, even though the Horizon Django/Apache web container does not call the Kubernetes API.

3. **AllowPrivilegeEscalation: true:** The pod SecurityContext explicitly sets `AllowPrivilegeEscalation: true` with no functional justification.

4. **Auto-mounted SA token:** The ServiceAccount token is auto-mounted into the internet/tenant-facing Django/Apache container (HTTP Route is an untrusted boundary) with no `automountServiceAccountToken: false`.

5. **Weak capability drop:** Only `MKNOD` is dropped from capabilities — no `Drop: ["ALL"]` baseline.

**Why this is exploitable:**

An attacker who obtains code execution in the web-facing Horizon container (via separate RCE, malicious plugin, or supply-chain image) can:
- Read the auto-mounted SA token from `/var/run/secrets/kubernetes.io/serviceaccount/token`
- POST a Pod manifest with `hostPath: {path: "/"}` to the kube-apiserver
- The Pod is admitted because the SA has both `use: hostmount-anyuid` AND `pods: create`
- Result: **node filesystem read/write** — full compromise of the OpenShift worker node

**Affected code paths (from OSPRH-33188):**

| File | Issue |
|------|-------|
| `pkg/horizon/funcs.go:9-19` | `HttpdSecurityContext()` returns `AllowPrivilegeEscalation: ptr.To(true)`, `RunAsUser: 48`, `RunAsGroup: 42400`, `Capabilities: {Drop: ["MKNOD"]}` |
| `controllers/horizon_controller.go:1215-1229` | `configureHorizonRbac()` builds rbacRules granting (a) `use` on SCCs `anyuid` AND `hostmount-anyuid`, and (b) full pod CRUD on `core/v1` |
| `pkg/horizon/deployment.go:~135` | Sets `SecurityContext: HttpdSecurityContext()` on both containers and `ServiceAccountName: instance.RbacResourceName()`, binding the internet-facing pod to the SCC-granted SA |
| `pkg/horizon/volumes.go` | Defines only ConfigMap, Secret, and EmptyDir volumes — confirms `hostmount-anyuid` is unnecessary |
| No `AutomountServiceAccountToken: false` anywhere in PodSpec | SA token is auto-mounted by default |

**Reachability:** `reconcileNormal()` calls `configureHorizonRbac(ctx, helper, instance)` unconditionally at line 652 on every Horizon CR reconcile. Every Horizon deployment is affected.

**Preconditions for exploit:**
1. Attacker must first obtain code execution inside the internet-facing Horizon Django/Apache container
2. No external admission controller (Gatekeeper/Kyverno) in the target namespace blocks hostPath Pod creation — default OpenShift relies solely on SCC

**Classification:**
- **Category:** OWASP K8s K01 — Insecure Workload Config; CIS K8s 5.2.5, 5.2.12
- **Severity:** Moderate (CVSS 7.3)
- **Confidence:** 8/10

### Why These Permissions Are Excessive

**Evidence from code analysis** (see `proposed_fixes.md` for detailed code snippets):

1. **`hostmount-anyuid` is gratuitous:**
   - `pkg/horizon/volumes.go` defines only ConfigMap, Secret, and EmptyDir volumes
   - **No hostPath volumes exist** in the Horizon workload
   - `anyuid` SCC alone is sufficient for the non-root user requirement

2. **Pod CRUD is unnecessary:**
   - Horizon is a **Django/Apache web dashboard** for OpenStack (not Kubernetes)
   - The workload serves HTTP traffic and calls OpenStack APIs (Nova, Neutron, etc.)
   - **Horizon never calls the Kubernetes API** — pod CRUD permissions are dead code

3. **`AllowPrivilegeEscalation: true` has no justification:**
   - Horizon runs as unprivileged user (UID 48, GID 42400)
   - No functional need for privilege escalation
   - Explicitly setting this to `true` violates security best practices

4. **Capabilities are under-restricted:**
   - Only `MKNOD` capability is dropped
   - Best practice: `Drop: ["ALL"]` and add back only required capabilities

5. **ServiceAccount token is auto-mounted:**
   - Default Kubernetes behavior mounts token into `/var/run/secrets/...`
   - Horizon workload doesn't need this token (doesn't call k8s API)
   - Creates unnecessary attack vector if RCE is achieved

### Affected Code

| File | Function/Section | Issue |
|------|------------------|-------|
| `pkg/horizon/funcs.go` | `HttpdSecurityContext()` lines 9-18 | `AllowPrivilegeEscalation: true`, capabilities only drop MKNOD |
| `controllers/horizon_controller.go` | `configureHorizonRbac()` lines 1215-1227 | Grants `hostmount-anyuid` SCC and pod CRUD |
| `pkg/horizon/deployment.go` | PodSpec lines ~122 | No `AutomountServiceAccountToken: false` |

**Repository:** `https://github.com/openstack-k8s-operators/horizon-operator`  
**Code analysis performed on:** `/home/omcgonag/Work/cursor/horizon-operator` (2025-11-19 checkout)

---

## Dependencies & Blockers

| Dependency | Assignee | Status | Notes |
|-----------|----------|--------|-------|
| RCA Spike Completion | Jan Jasek | Backlog | This ticket (OSPRH-33457) |
| Fix Implementation | TBD | Pending RCA | Follow-up ticket needed after RCA |
| Security Review | ProjectGlasswing / Security Team | Completed | Audit report filed as OSPRH-33188 |
| Upstream horizon-operator maintainer review | TBD | Pending | Must review fix proposals before implementation |

**No hard blockers.** The RCA is complete (see `proposed_fixes.md`). Next step is to create an implementation ticket and assign to horizon-operator team.

---

## Impact Analysis

### If We Proceed (Implement Fixes)

**Benefits:**
- **Eliminate CVSS 7.3 vulnerability** — Remove privilege escalation attack vector
- **Reduce attack surface** — Apply principle of least privilege across RBAC, SCC, and security context
- **Defense in depth** — Multiple mitigations (even if one is bypassed, others remain)
- **Compliance** — Align with OWASP K8s and CIS benchmarks
- **No functional impact** — All changes are security hardening; no Horizon features rely on the excessive permissions

**Costs:**
- **Engineering effort:** ~1-2 days for implementation + testing + review
- **Testing burden:** Requires functional verification (Horizon dashboard operations), negative security testing (attempt pod creation), and SCC admission validation
- **Risk of regression:** Low (changes remove unused permissions), but requires thorough testing to confirm no hidden dependencies

### If We Close/Defer

**Risks:**
- **Active vulnerability remains** — Horizon continues to be exploitable if an attacker achieves RCE in the web container
- **Compliance gap** — Fails OWASP K8s K01 and CIS 5.2.5/5.2.12
- **Downstream impact** — All RHOS deployments with Horizon are affected
- **Audit finding unresolved** — ProjectGlasswing report remains open

**Justification for deferral:** None. The fix is straightforward, low-risk, and addresses a Moderate severity security issue.

---

## Recommendation

**Verdict:** **IMPLEMENT**  
**Confidence:** HIGH  
**Priority:** Medium-High (Moderate severity vulnerability, but requires RCE precondition)

### Rationale

1. **Clear security benefit:** Removes a documented CVSS 7.3 privilege escalation path
2. **Low implementation risk:** All proposed fixes remove unused permissions — no functional dependencies identified
3. **Defense in depth:** Multiple layers of mitigation (RBAC + SCC + SecurityContext + token auto-mount)
4. **Audit requirement:** Addressing a security audit finding is table-stakes for compliance

### Proposed Implementation Plan

**Phase 1: RCA Completion (This Ticket)**
- [x] Analyze affected code in horizon-operator
- [x] Generate proposed fixes with code diffs, rationale, and testing strategies
- [x] Document attack scenario and security impact
- [ ] **ACTION:** Review `proposed_fixes.md` with Jan Jasek (assignee) and horizon-operator maintainers
- [ ] **ACTION:** Close OSPRH-33457 when RCA is approved

**Phase 2: Fix Implementation (New Ticket)**
- [ ] Create follow-up implementation ticket: "Fix excessive RBAC grants and security context (OSPRH-33188)"
- [ ] Assign to horizon-operator team (suggest: Jan Jasek or Owen McGonagle)
- [ ] Implement three fixes:
  1. Harden `HttpdSecurityContext()` in `pkg/horizon/funcs.go`
  2. Remove excessive RBAC grants in `controllers/horizon_controller.go`
  3. Disable token auto-mount in `pkg/horizon/deployment.go`
- [ ] Update kubebuilder RBAC markers
- [ ] Run test suite + security validation
- [ ] Submit Gerrit review to `openstack-k8s-operators/horizon-operator`

**Phase 3: Validation & Backport**
- [ ] Merge upstream review
- [ ] Backport to RHOS release branches if applicable
- [ ] Update OSPRH-33188 (bug) and OSPRH-33189 (epic) with resolution

---

## Talking Points

For stakeholder communication (PM, security team, customers):

- **What:** Security vulnerability in horizon-operator grants excessive privileges to internet-facing workload (CVSS 7.3)
- **Risk:** If an attacker achieves code execution in Horizon dashboard, they can escalate to node filesystem access
- **Fix:** Remove unnecessary RBAC/SCC grants and harden security context (3-file patch, low complexity)
- **Impact:** No functional changes — fixes remove unused permissions
- **Timeline:** RCA complete, implementation ~1-2 days, testing ~1 day, review ~2-3 days → ~1 week total
- **Backport:** May need backporting to RHOS 18.0 and 19.0 if vulnerability affects released versions

**Key message:** "We've identified and documented a privilege escalation vulnerability in Horizon's Kubernetes deployment. The fix is straightforward (removing permissions the workload doesn't use) and carries minimal risk. Recommend proceeding with implementation in the next sprint."

---

## Deep Analysis

### Attack Prerequisites

Per OSPRH-33188, an attacker must first achieve **code execution inside the Horizon Django/Apache container**. Possible vectors:

1. **Remote Code Execution (RCE) vulnerability** in Django, Apache, or Python dependencies (CVE in upstream)
2. **Malicious Horizon plugin** — If customer installs untrusted Horizon dashboard plugins
3. **Supply chain attack** — Compromised container image or Python package in the build
4. **SSRF → RCE escalation** — Server-Side Request Forgery leading to code execution

**Note:** The vulnerability does NOT provide initial access — it's a **privilege escalation path after RCE**.

### Missing Mitigations (from OSPRH-33188)

- No `automountServiceAccountToken: false` on the PodSpec
- No NetworkPolicy restricting pod creation from this SA
- No external admission controller (Gatekeeper/Kyverno) blocking hostPath pods (relies solely on SCC, which is granted)
- `AllowPrivilegeEscalation: true` explicitly set
- Only `MKNOD` dropped from capabilities

### Reachability Analysis

**Code path (from horizon-operator):**

```
main.go
  └─> HorizonReconciler.Reconcile()
        └─> reconcileNormal() (controllers/horizon_controller.go:652)
              ├─> configureHorizonRbac(ctx, helper, instance)  // Grants excessive RBAC
              │     └─> common_rbac.ReconcileRbac()            // Applies Role/RoleBinding
              └─> EnsureDeployment()
                    └─> horizon.Deployment() (pkg/horizon/deployment.go)
                          └─> Sets SecurityContext: HttpdSecurityContext()  // AllowPrivilegeEscalation: true
                          └─> Sets ServiceAccountName: instance.RbacResourceName()
```

**This runs unconditionally** on every Horizon CR reconcile. The excessive permissions are **always granted**, not gated by any feature flag or configuration.

### Proposed Fix Validation

All three proposed fixes in `proposed_fixes.md` have been **validated against the actual code**:

1. **Fix 1** (`pkg/horizon/funcs.go`): Code matches OSPRH-33188 description — `AllowPrivilegeEscalation: true` is explicit, capabilities only drop `MKNOD`
2. **Fix 2** (`controllers/horizon_controller.go`): RBAC rules include `"hostmount-anyuid"` in ResourceNames and full pod CRUD verbs — both unnecessary
3. **Fix 3** (`pkg/horizon/deployment.go`): No `AutomountServiceAccountToken` field is set (defaults to true) — token is auto-mounted

**Confidence:** HIGH. All affected files located, code snippets extracted, and fixes proposed with line-level precision.

---

Generated: 2026-07-27 | Skill: /triassessment --deep --generate-fix | Model: claude-sonnet-4-5@20250929
