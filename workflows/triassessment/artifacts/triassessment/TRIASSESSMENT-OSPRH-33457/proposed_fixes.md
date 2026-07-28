# Proposed Fixes: OSPRH-33457

**Ticket:** [OSPRH-33457](https://redhat.atlassian.net/browse/OSPRH-33457) — RCA of bug Horizon workload SA granted hostmount-anyuid SCC and pod CRUD with allowPrivilegeEscalation true  
**Parent Bug:** [OSPRH-33188](https://redhat.atlassian.net/browse/OSPRH-33188) (CVSS 7.3, Moderate severity)  
**Epic:** [OSPRH-33189](https://redhat.atlassian.net/browse/OSPRH-33189)  
**Generated:** 2026-07-27  
**Confidence:** HIGH (all affected files located, security context fully analyzed)

---

## Summary

The horizon-operator unconditionally grants excessive privileges to the internet-facing Horizon workload: `hostmount-anyuid` SCC, full pod CRUD, and `AllowPrivilegeEscalation: true`. An attacker who achieves code execution in the web-facing Django/Apache container can read the auto-mounted ServiceAccount token and POST a Pod with `hostPath: {path: "/"}` to the kube-apiserver — admitted because the SA has both `use: hostmount-anyuid` and `pods: create` — yielding node filesystem read/write.

**Fix strategy:** Apply defense-in-depth by removing unnecessary privileges at multiple layers:
1. Remove `hostmount-anyuid` from SCC grant (Horizon uses no hostPath volumes)
2. Remove pod CRUD verbs from the workload Role (Django/Apache doesn't call k8s API)
3. Set `AllowPrivilegeEscalation: false` (no functional need for escalation)
4. Set `automountServiceAccountToken: false` (web container doesn't need API access)
5. Drop all capabilities and add back only required ones

---

## Affected Files

| File | Change Type | Lines | Complexity | Risk |
|------|-------------|-------|------------|------|
| `pkg/horizon/funcs.go` | Modify | 9-18 | Low | Low (security hardening) |
| `controllers/horizon_controller.go` | Modify | 1215-1227 | Medium | Medium (RBAC changes) |
| `pkg/horizon/deployment.go` | Modify | ~122 | Low | Low (add one field) |

---

## Fix 1: Harden Container Security Context

**File:** `pkg/horizon/funcs.go`  
**Lines:** 9-18  
**Complexity:** Low  
**Risk:** Low (security hardening, no API changes)

### Current Code

```go
// HttpdSecurityContext -
func HttpdSecurityContext() *corev1.SecurityContext {
	return &corev1.SecurityContext{
		Capabilities: &corev1.Capabilities{
			Drop: []corev1.Capability{
				"MKNOD",
			},
		},
		RunAsUser:                ptr.To(ApacheUID),
		RunAsGroup:               ptr.To(KollaUID),
		AllowPrivilegeEscalation: ptr.To(true),
	}
}
```

### Proposed Change

```go
// HttpdSecurityContext -
func HttpdSecurityContext() *corev1.SecurityContext {
	return &corev1.SecurityContext{
		Capabilities: &corev1.Capabilities{
			Drop: []corev1.Capability{
				"ALL",  // FIX: Drop all capabilities instead of just MKNOD (OSPRH-33188)
			},
			// Add back only strictly required capabilities here if needed
			// Add: []corev1.Capability{},
		},
		RunAsUser:                ptr.To(ApacheUID),
		RunAsGroup:               ptr.To(KollaUID),
		AllowPrivilegeEscalation: ptr.To(false),  // FIX: Changed from true (OSPRH-33188)
	}
}
```

### Rationale

**Problem:** The current configuration:
- Explicitly sets `AllowPrivilegeEscalation: true` despite no functional need for privilege escalation
- Only drops the `MKNOD` capability, leaving many dangerous capabilities enabled (e.g., `CHOWN`, `SETUID`, `SETGID`, `NET_BIND_SERVICE`)

**Fix:**
- Set `AllowPrivilegeEscalation: false` — Horizon Django/Apache workload has no legitimate need to escalate privileges
- Drop all capabilities (`Drop: ["ALL"]`) following security best practice
- The commented-out `Add` section is a placeholder in case specific capabilities are discovered to be required during testing

**Security impact:**
- Prevents container from gaining additional privileges beyond those assigned at pod startup
- Reduces attack surface by removing unnecessary Linux capabilities
- Aligns with CIS Kubernetes Benchmark 5.2.5 ("Minimize the admission of containers with allowPrivilegeEscalation")

### Testing Strategy

**Unit tests:**
- Verify `HttpdSecurityContext()` returns `AllowPrivilegeEscalation: false`
- Verify capabilities drop includes `ALL`

**Integration tests:**
- Deploy Horizon CR with the patched operator
- Verify both containers (`horizon-log` and `horizon`) start successfully
- Check pod security context with:
  ```bash
  oc get pod <horizon-pod> -o jsonpath='{.spec.containers[*].securityContext.allowPrivilegeEscalation}'
  # Expected: false false
  ```

**Functional verification:**
- Access Horizon dashboard through Route
- Verify all core operations work:
  - Login/logout
  - List instances/volumes/networks
  - Create key pairs
  - Launch instance workflow
- Check Apache/Django logs for capability-related errors

**Rollback plan:**
- If unexpected capability errors appear, add specific capabilities to the `Add` array incrementally
- Most common legitimate needs for Apache/Django: none (runs as unprivileged user)
- If rollback needed: revert `AllowPrivilegeEscalation` to `true` temporarily

### Migration Notes

**Compatibility:** No breaking changes. This is a security hardening enhancement.

**Upgrade path:** Existing Horizon CRs will be reconciled with the new security context on the next operator restart or CR update. No manual intervention required.

**Feature flags:** None needed. This is a security fix, not a feature.

---

## Fix 2: Remove Excessive RBAC Grants

**File:** `controllers/horizon_controller.go`  
**Lines:** 1215-1227  
**Complexity:** Medium  
**Risk:** Medium (changes RBAC, affects SCC admission)

### Current Code

```go
func configureHorizonRbac(ctx context.Context, helper *helper.Helper, instance *horizonv1beta1.Horizon) (rbacResult ctrl.Result, err error) {
	rbacRules := []rbacv1.PolicyRule{
		{
			APIGroups:     []string{"security.openshift.io"},
			ResourceNames: []string{"anyuid", "hostmount-anyuid"},
			Resources:     []string{"securitycontextconstraints"},
			Verbs:         []string{"use"},
		},
		{
			APIGroups: []string{""},
			Resources: []string{"pods"},
			Verbs:     []string{"create", "get", "list", "watch", "update", "patch", "delete"},
		},
	}
	return common_rbac.ReconcileRbac(ctx, helper, instance, rbacRules)
}
```

### Proposed Change

```go
func configureHorizonRbac(ctx context.Context, helper *helper.Helper, instance *horizonv1beta1.Horizon) (rbacResult ctrl.Result, err error) {
	rbacRules := []rbacv1.PolicyRule{
		{
			APIGroups:     []string{"security.openshift.io"},
			ResourceNames: []string{"anyuid"},  // FIX: Removed "hostmount-anyuid" (OSPRH-33188)
			Resources:     []string{"securitycontextconstraints"},
			Verbs:         []string{"use"},
		},
		// FIX: Removed pod CRUD rule entirely — Horizon workload does not call k8s API (OSPRH-33188)
	}
	return common_rbac.ReconcileRbac(ctx, helper, instance, rbacRules)
}
```

### Rationale

**Problem:**
- Horizon workload ServiceAccount is granted `use` on **both** `anyuid` and `hostmount-anyuid` SCCs
- Review of `pkg/horizon/volumes.go` confirms Horizon uses **only** ConfigMap, Secret, and EmptyDir volumes — no hostPath
- `hostmount-anyuid` SCC is gratuitous and creates an attack vector (allows `hostPath: {path: "/"}` pod creation)
- Full pod CRUD (`create/delete/get/list/patch/update/watch`) is granted despite Horizon Django/Apache never calling the Kubernetes API

**Fix:**
- Remove `"hostmount-anyuid"` from SCC ResourceNames — `anyuid` alone is sufficient for Horizon's non-root user requirement
- Remove the entire pod CRUD PolicyRule — the workload has no legitimate need for Kubernetes API access

**Security impact:**
- Blocks the primary attack vector: attacker with code execution can no longer create `hostPath` pods (SCC admission denies)
- Follows principle of least privilege: remove all permissions not actively used
- Aligns with OWASP K8s K01 (Insecure Workload Configuration) and CIS Kubernetes 5.2.12

**Alternative (if `anyuid` proves insufficient):**
- Consider `nonroot-v2` SCC if feasible (even more restrictive than `anyuid`)
- Only fall back to `anyuid` if non-root enforcement fails

### Testing Strategy

**Prerequisite verification:**
- Before applying the patch, audit `pkg/horizon/volumes.go` to confirm no hostPath volumes exist
  ```bash
  grep -i "hostpath" /home/omcgonag/Work/cursor/horizon-operator/pkg/horizon/volumes.go
  # Expected: no matches
  ```

**Unit tests:**
- Verify `configureHorizonRbac()` returns RBAC rules without `hostmount-anyuid`
- Verify pod CRUD rule is absent

**Integration tests:**
- Deploy Horizon CR with the patched operator
- Verify Horizon deployment reconciles successfully
- Check the generated Role/RoleBinding:
  ```bash
  oc get role horizon-<instance>-role -o yaml
  # Verify: resourceNames contains "anyuid" only
  # Verify: no "pods" resource in rules
  ```

**Functional verification:**
- Horizon pod starts and runs (proves `anyuid` SCC is sufficient)
- All dashboard operations work (proves pod CRUD is not needed)

**Negative testing (security validation):**
- Exec into the Horizon pod and attempt to create a pod via ServiceAccount token:
  ```bash
  oc exec -it <horizon-pod> -- bash
  # Inside pod:
  TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
  curl -k -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -X POST https://kubernetes.default.svc/api/v1/namespaces/<ns>/pods \
    -d '{"apiVersion":"v1","kind":"Pod","metadata":{"name":"attack"},"spec":{"containers":[{"name":"c","image":"busybox","volumeMounts":[{"name":"host","mountPath":"/host"}]}],"volumes":[{"name":"host","hostPath":{"path":"/"}}]}}'
  # Expected: 403 Forbidden (both due to missing pod CRUD and SCC denial)
  ```

### Migration Notes

**Compatibility:** This is a **breaking change** if:
- Any downstream tooling/scripts rely on Horizon SA having pod CRUD permissions (unlikely — not a standard Horizon use case)
- Horizon workload actually uses hostPath volumes despite none appearing in `volumes.go` (needs verification)

**Upgrade path:**
1. Audit existing Horizon deployments for unexpected hostPath usage:
   ```bash
   oc get pods -l service=horizon -o jsonpath='{.items[*].spec.volumes[*].hostPath}' | grep -q . && echo "HOSTPATH FOUND" || echo "Clean"
   ```
2. If clean, proceed with RBAC change
3. If hostPath found, investigate root cause before applying fix

**Rollback plan:**
- If Horizon pod fails to start with SCC admission error, check pod events:
  ```bash
  oc describe pod <horizon-pod>
  # Look for "unable to validate against any security context constraint"
  ```
- If `anyuid` proves insufficient, temporarily restore `hostmount-anyuid` **and file a ticket** to investigate the root cause
- Pod CRUD removal is lower risk — only restore if unexplained failures occur

---

## Fix 3: Disable ServiceAccount Token Auto-Mount

**File:** `pkg/horizon/deployment.go`  
**Lines:** ~122 (add field to PodSpec)  
**Complexity:** Low  
**Risk:** Low (defense-in-depth measure)

### Current Code

```go
Spec: corev1.PodSpec{
	ServiceAccountName: instance.RbacResourceName(),
	Containers: []corev1.Container{
		{
			Name: instance.Name + "-log",
			Command: []string{
				"/bin/bash",
			},
			Args:            []string{"-c", "tail -n+1 -F " + LogFile},
			Image:           instance.Spec.ContainerImage,
			SecurityContext: HttpdSecurityContext(),
			// ... rest of container spec
		},
		// ... second container
	},
	// ... volumes, etc.
}
```

### Proposed Change

```go
Spec: corev1.PodSpec{
	ServiceAccountName:           instance.RbacResourceName(),
	AutomountServiceAccountToken: ptr.To(false),  // FIX: Prevent SA token mounting (OSPRH-33188)
	Containers: []corev1.Container{
		{
			Name: instance.Name + "-log",
			Command: []string{
				"/bin/bash",
			},
			Args:            []string{"-c", "tail -n+1 -F " + LogFile},
			Image:           instance.Spec.ContainerImage,
			SecurityContext: HttpdSecurityContext(),
			// ... rest of container spec
		},
		// ... second container
	},
	// ... volumes, etc.
}
```

### Rationale

**Problem:**
- By default, Kubernetes auto-mounts the ServiceAccount token into `/var/run/secrets/kubernetes.io/serviceaccount/token` in every container
- The internet-facing Horizon Django/Apache workload **does not call the Kubernetes API** — it serves a web UI for OpenStack operations
- Auto-mounting the token creates an unnecessary attack vector: if an attacker achieves RCE in Horizon, they can read the token and use it for API calls (even after Fix 2 removes pod CRUD, other permissions might exist)

**Fix:**
- Set `AutomountServiceAccountToken: ptr.To(false)` to prevent the token from being mounted
- This is a defense-in-depth measure: even if RBAC grants are later re-added accidentally, the token is not present in the container to be stolen

**Security impact:**
- Removes the ServiceAccount token from the container filesystem entirely
- Aligns with the principle of least privilege (no API access → no token needed)
- Mitigates the attack scenario even if Fix 2 is later reverted

### Testing Strategy

**Unit tests:**
- Verify `AutomountServiceAccountToken` is set to `false` in the PodSpec

**Integration tests:**
- Deploy Horizon CR with the patched operator
- Verify the token is not mounted:
  ```bash
  oc exec -it <horizon-pod> -- ls /var/run/secrets/kubernetes.io/serviceaccount/
  # Expected: "ls: cannot access ... : No such file or directory"
  ```

**Functional verification:**
- Access Horizon dashboard and verify all operations work (proves no dependency on k8s API)
- Check Django/Apache logs for any Kubernetes client initialization errors (should be none)

**Rollback plan:**
- If unexpected k8s API client errors appear (very unlikely for Horizon), set `AutomountServiceAccountToken: ptr.To(true)` temporarily
- Investigate the code path that requires API access and file a bug — Horizon dashboard should not call k8s API

### Migration Notes

**Compatibility:** No breaking changes. Horizon workload does not use the Kubernetes API.

**Upgrade path:** Existing Horizon pods will be recreated on the next reconcile with the token mount disabled. No manual intervention required.

---

## Implementation Checklist

- [ ] Review proposed fixes with horizon-operator maintainers
- [ ] Verify no hostPath volumes in `pkg/horizon/volumes.go` (grep for "hostPath")
- [ ] Create feature branch from `main`: `git checkout -b fix/osprh-33188-remove-excessive-privileges`
- [ ] Implement Fix 1: Harden `HttpdSecurityContext()` in `pkg/horizon/funcs.go`
- [ ] Implement Fix 2: Remove excessive RBAC grants in `controllers/horizon_controller.go`
- [ ] Implement Fix 3: Disable token auto-mount in `pkg/horizon/deployment.go`
- [ ] Run unit tests: `make test`
- [ ] Run static analysis: `make lint`
- [ ] Deploy to test cluster and run integration tests
- [ ] Perform functional verification (Horizon dashboard operations)
- [ ] Perform negative security testing (attempt pod creation from within Horizon container)
- [ ] Update kubebuilder RBAC markers in `horizon_controller.go` (lines 122-123):
  ```go
  // REMOVE: +kubebuilder:rbac:groups="security.openshift.io",resourceNames=hostmount-anyuid,resources=securitycontextconstraints,verbs=use
  // REMOVE: +kubebuilder:rbac:groups="",resources=pods,verbs=create;delete;get;list;patch;update;watch
  ```
- [ ] Regenerate RBAC manifests: `make manifests`
- [ ] Submit Gerrit review to `https://github.com/openstack-k8s-operators/horizon-operator`
- [ ] Link Gerrit review to OSPRH-33188 (bug ticket) in commit message:
  ```
  Fix excessive RBAC grants and security context (OSPRH-33188)
  
  The horizon-operator unconditionally grants hostmount-anyuid SCC
  and full pod CRUD to the internet-facing workload, creating a
  privilege escalation attack vector (CVSS 7.3).
  
  This patch applies defense-in-depth by:
  - Removing hostmount-anyuid (Horizon uses no hostPath volumes)
  - Removing pod CRUD (workload doesn't call k8s API)
  - Setting AllowPrivilegeEscalation: false
  - Dropping all capabilities (previously only MKNOD)
  - Disabling ServiceAccount token auto-mount
  
  Resolves: OSPRH-33188
  ```
- [ ] Update OSPRH-33457 (RCA spike) with link to Gerrit review

---

## Additional Considerations

### Performance Impact
**None expected.** All changes are security hardening with no performance overhead:
- Security context changes apply at pod startup (one-time validation)
- RBAC changes affect admission control (negligible latency)
- Token auto-mount removal saves a volume mount (marginal improvement)

### Monitoring & Observability
No new monitoring required. Existing pod startup logs and SCC admission events in OpenShift audit logs will reflect the changes.

### Documentation Updates
- Update horizon-operator README to document the security posture changes
- Add a security best practices section referencing this fix
- Update deployment examples if they mention RBAC or security contexts

### Related Work
- **OSPRH-33189** (parent epic) may have sibling tickets for other operators with similar issues
- Consider running the same ProjectGlasswing audit against other openstack-k8s-operators (nova, cinder, etc.)

---

**Disclaimer:** These proposals are AI-generated based on ticket OSPRH-33188 description and code analysis of horizon-operator at `/home/omcgonag/Work/cursor/horizon-operator`. Review carefully with the horizon-operator team before implementation. All code snippets are extracted from the repository as of 2025-11-19 (last commit date in the checked-out version).

---

Generated: 2026-07-27 | Skill: /triassessment --generate-fix | Model: claude-sonnet-4-5@20250929
