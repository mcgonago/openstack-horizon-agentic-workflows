# Related Artifacts: install_yamls#1158

**Primary Investigation:** install_yamls PR #1158 (dynamic password generation)

---

## 1. GitHub Pull Requests

| Repository | PR | Title | Status | Role | Merged |
|------------|-----|-------|--------|------|--------|
| **openstack-k8s-operators/install_yamls** | **[#1158](https://github.com/openstack-k8s-operators/install_yamls/pull/1158)** | Replace hardcoded passwords with dynamic generation | **Merged** | **Root cause** | 2026-07-16 |
| openstack-k8s-operators/tcib | [#408](https://github.com/openstack-k8s-operators/tcib/pull/408) | Fix horizontest admin auth by loading password from OS cloud config | Open | Proposed fix | — |
| openstack-k8s-operators/test-operator | [#473](https://github.com/openstack-k8s-operators/test-operator/pull/473) | Remove default AdminPassword/AdminUsername | Open | Dependency (blocker) | — |
| openstack-k8s-operators/ci-framework | [#4071](https://github.com/openstack-k8s-operators/ci-framework/pull/4071) | Remove hardcoded test config | Open | Dependency (blocker) | — |

---

## 2. Commits

| Repository | SHA | Message | Date | Role |
|------------|-----|---------|------|------|
| openstack-k8s-operators/horizon-operator | [427781ab](https://github.com/openstack-k8s-operators/horizon-operator/commit/427781ab94fc381b57ad4689e48ed6a171e528e0) | Update dependencies (OpenStackSDK bump) | 2026-07-xx | Contributing factor (red herring) |

---

## 3. Dependency Chain

```
Root Cause:
  install_yamls PR #1158 (Merged 2026-07-16)
    |
    +-> Changed: PASSWORD=12345678 (static)
    |           TO: ADMIN_PASSWORD=<random> (dynamic)
    |
    +-> Broke: Component pipeline tests
             (Test pods still inject hardcoded 12345678)

Proposed Fix:
  tcib PR #408 (Open, blocked)
    |
    +-> Blocked by:
         |
         +-> test-operator PR #473 (remove AdminPassword default)
         +-> ci-framework PR #4071 (remove hardcoded config)
```

---

## 4. External Logs

| Type | Build ID | URL | Status |
|------|----------|-----|--------|
| Zuul CI Log | ac832f9a... | [Link](https://sf.apps.int.gpc.ocp-hub.prod.psi.redhat.com/logs/ac8/components-integration/ac832f9aca7d40ff8d271d5bcf6c3418/controller/ci-framework-data/tests/test_operator/horizon/ui_integration_test_results.html.gz?sort=result) | Failure evidence |

---

## 5. Cross-Repository Impact

### Affected Components

- **install_yamls** - Dynamic password generation (root cause)
- **tcib** - Test container runtime (fix location)
- **test-operator** - Test pod configuration (needs update)
- **ci-framework** - CI test configuration (needs update)
- **horizon-operator** - Integration tests (victim of regression)

### Timeline

- **2026-07-16** - install_yamls PR #1158 merged
- **2026-07-20** - Component pipeline failures started (Sunday)
- **2026-07-22** - tcib PR #408 opened (proposed fix)
- **2026-07-23** - Issue reported by Jan Jasek

---

**No Jira tickets are related to this investigation.** This is a pure GitHub PR/CI pipeline issue.

---

Generated: 2026-07-24 | Skill: /triassessment | Model: claude-sonnet-4-5@20250929
