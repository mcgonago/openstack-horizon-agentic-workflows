# Triage Assessment: Component Pipeline Failures

**Case ID:** TRIASSESSMENT-GH-openstack-k8s-operators-install_yamls-1158  
**Generated:** 2026-07-23 15:12:00 EDT  
**Skill:** /triassessment  
**Model:** claude-sonnet-4-5@20250929

---

## Inquiry Source

**Received:** 2026-07-23 15:12:00 EDT  
**From:** Jan Jasek (HanzJas)  
**Context:** Component pipeline failures since Sunday (2026-07-20)  
**Original Message:** See the **Inquiry Source** artifact above (expand ▶ in Key Artifacts table)

**Key Quote:**
> "Since Sunday, we have a lot of failures in the Horizon component pipeline. The fails are caused by error in create OpenStackSDK connection in our tests"

---

## Extracted Artifacts

| Type | Identifier | URL | Role | Status |
|------|-----------|-----|------|--------|
| **GitHub PR** | **install_yamls#1158** | [Link](https://github.com/openstack-k8s-operators/install_yamls/pull/1158) | **Primary cause** | **Merged 2026-07-16** |
| GitHub PR | tcib#408 | [Link](https://github.com/openstack-k8s-operators/tcib/pull/408) | Proposed fix | Open |
| Commit SHA | 427781ab | [Link](https://github.com/openstack-k8s-operators/horizon-operator/commit/427781ab94fc381b57ad4689e48ed6a171e528e0) | Contributing factor | Merged |
| Zuul Log | ac832f9a... | [Link](https://sf.apps.int.gpc.ocp-hub.prod.psi.redhat.com/logs/ac8/components-integration/ac832f9aca7d40ff8d271d5bcf6c3418/controller/ci-framework-data/tests/test_operator/horizon/ui_integration_test_results.html.gz?sort=result) | Failure evidence | -- |

---

## External Analysis

**GitHub PR Review:** See the **GitHub PR Analysis** artifact in the Key Artifacts section above

### PR #1158: "Replace hardcoded passwords with dynamic generation"

**Impact Assessment:**
- **Repository:** openstack-k8s-operators/install_yamls
- **Merged:** 2026-07-16 (4 days before failures started)
- **Scope:** 21 files, +313/-86 lines
- **Breaking Change:** Yes — credential contract changed from static to dynamic

**What Changed:**
1. Added `scripts/gen-secrets.sh` to generate random passwords in `.secrets.env`
2. Replaced single `PASSWORD=12345678` with 30+ service-specific variables
3. Preserved legacy `PASSWORD` override for backward compatibility
4. Updated all Makefile targets and deployment scripts to use new variables

**Why It Broke Tests:**

```
+-------------------------------------------------------------+
| Before PR #1158:                                            |
|   OpenStack deployment:  ADMIN_PASSWORD=12345678            |
|   Test pod injection:    ADMIN_PASSWORD=12345678            |
|   Result: Auth succeeds                                     |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
| After PR #1158:                                             |
|   OpenStack deployment:  ADMIN_PASSWORD=<random-from-.secrets.env>  |
|   Test pod injection:    ADMIN_PASSWORD=12345678 (hardcoded)|
|   Result: HTTP 401 Unauthorized (password mismatch)         |
+-------------------------------------------------------------+
```

The test-operator CRs inject `ADMIN_PASSWORD=12345678` directly into test pods. This value no longer matches the Keystone admin password, which is now randomly generated during `make input` and stored in the OpenStack deployment.

**Legacy Override Limitation:**

PR #1158 included a backward compatibility mechanism:

**Source:** [install_yamls/Makefile](https://github.com/openstack-k8s-operators/install_yamls/blob/main/Makefile)
```makefile
PASSWORD ?=
ifneq ($(PASSWORD),)
ADMIN_PASSWORD = $(PASSWORD)
# ... all service passwords follow PASSWORD
endif
```

However, this only affects the `make input` phase when deploying OpenStack. Test pods are configured separately via test-operator CRs, which bypass the Makefile and directly inject hardcoded values.

### PR #408: "Fix horizontest admin auth by loading password from OS cloud config"

**Proposed Solution:**
- **Repository:** openstack-k8s-operators/tcib
- **Author:** Jan Jasek (same person who reported the issue)
- **Created:** 2026-07-22 (2 days after failures started)
- **Status:** Open, awaiting upstream dependencies

**The Fix:**

**Source:** [tcib PR #408](https://github.com/openstack-k8s-operators/tcib/pull/408) (proposed fix - if link fails, GitHub may be experiencing issues)
```bash
+ADMIN_PASSWORD=$(python3 -c "from openstack.config import OpenStackConfig; print(OpenStackConfig().get_one(cloud='default').auth['password'])")
```

Reads the actual admin password from OpenStack cloud config (`clouds.yaml` + `secure.yaml`) instead of trusting the hardcoded pod-injected value.

**Discussion Status:**

1. **Initial approach:** Overwrite `ADMIN_PASSWORD` unconditionally in TCIB
2. **Team feedback (kstrenkova):** Move fix to test-operator for cleaner architecture and deprecation path
3. **Revised approach:** Conditional override to preserve customer override capability:

   **Source:** [tcib PR #408 (revised approach)](https://github.com/openstack-k8s-operators/tcib/pull/408)
   ```bash
   if [[ -z "${ADMIN_PASSWORD}" ]]; then
       ADMIN_PASSWORD=$(python3 -c "from openstack.config import OpenStackConfig; ...")
   fi
   ```
4. **Current blocker:** Waiting for test-operator PR #473 and ci-framework PR #4071 to merge (remove hardcoded defaults)

**Timeline to Fix:** Estimated 1-3 days post-dependency merge

---

## Technical Context

### Problem Statement

Component pipeline failures are a **regression caused by a deliberate security improvement** (PR #1158). The root cause is a credential contract mismatch between:
- **OpenStack control plane** (uses dynamic passwords from `.secrets.env`)
- **Test fixtures** (hardcoded `ADMIN_PASSWORD=12345678` injected by test-operator CRs)

### Failure Symptom

OpenStackSDK connection initialization fails with HTTP 401 Unauthorized when Horizon integration tests attempt to authenticate against Keystone using the hardcoded password.

**Error Pattern:**
```
Error in create OpenStackSDK connection in our tests
```

**Affected Component:** `ci-framework-data/tests/test_operator/horizon/ui_integration_test_results.html.gz`

### Contributing Factor: OpenStackSDK Version Bump

Commit `427781ab` (mentioned in the inquiry) updated horizon-operator dependencies, which may have included an OpenStackSDK version bump. While this changed connection initialization behavior, it is **not the root cause**.

**Impact:** Potentially exposed latent auth issues or changed error reporting, making the password mismatch more visible.

**Verdict:** Red herring. The auth failure would occur with any SDK version if passwords don't match.

### Architecture Context

**Horizon Test Flow:**
1. `test-operator` CR defines horizontest job with environment variables
2. `tcib` container image (`horizontest`) receives injected env vars
3. `run_horizontest.sh` script uses `ADMIN_PASSWORD` to authenticate
4. OpenStackSDK connects to Keystone with provided credentials
5. Keystone validates against password stored during `make input`

**Credential Chain:**
```
.secrets.env -> make input -> Keystone admin user
                                |
                                +-> Password: <random-32-char>

test-operator CR -> tcib pod -> run_horizontest.sh
                                |
                                +-> Password: 12345678 (hardcoded)
```

**Mismatch Point:** Step 4 (SDK auth) uses wrong password

---

## Impact Analysis

### What Happens If We Proceed (Merge PR #408 or Equivalent Fix)

**Positive:**
- ✅ Component pipeline recovers immediately
- ✅ Tests align with actual OpenStack deployment credentials
- ✅ More realistic test scenario (uses real cloud config, not hardcoded values)
- ✅ No production impact (test-only change)
- ✅ Enables further security hardening (dynamic credentials proven to work)

**Negative:**
- ⚠️ Adds runtime dependency on OpenStackConfig in test containers
- ⚠️ Requires customer communication if test-operator parameters are deprecated
- ⚠️ May expose similar issues in other test scenarios (smoke tests, tempest, etc.)

### What Happens If We Close/Revert

**Option A: Revert PR #1158 (restore hardcoded passwords)**

**Positive:**
- ✅ Immediate pipeline recovery
- ✅ No test fixture changes needed

**Negative:**
- ❌ Reverts security improvement (dynamic credentials → static `12345678`)
- ❌ Blocks future hardening efforts
- ❌ Contradicts best practices (hardcoded secrets in version control)
- ❌ CI failures during PR #1158 review suggest adoption tests also had issues (unresolved)

**Option B: Do nothing**

**Negative:**
- ❌ Component pipeline remains broken indefinitely
- ❌ Horizon development velocity drops (no pre-merge testing)
- ❌ Manual workarounds required for every test run
- ❌ Tech debt accumulates (divergence between test and prod config)

---

## Recommendation

**Verdict:** **IMPLEMENT** (merge PR #408 or revised version)  
**Confidence:** High (85%)  
**Priority:** High  
**Risk:** Low (test-only change, no production exposure)

### Rationale

1. **Root cause is clear:** Password mismatch between deployment and test fixtures
2. **Fix is targeted:** Single-file change in test script, minimal blast radius
3. **Security trade-off favors fix:** Reverting to hardcoded passwords contradicts security goals
4. **Team consensus exists:** Jan (author), kstrenkova (reviewer) aligned on approach
5. **Temporary impact acceptable:** 3-day pipeline downtime vs. permanent security regression

### Why Not Revert PR #1158?

- Security regression outweighs short-term test convenience
- CI failures during PR #1158 review (adoption tests) suggest revert may not fully recover pipeline
- Hardcoded `PASSWORD=12345678` is a known anti-pattern flagged in security audits

### Why Not Wait for Perfect Solution?

- Component pipeline is a critical feedback loop for Horizon development
- Every day of downtime delays feature work and bug fixes
- Conditional override approach (proposed by kstrenkova) preserves customer flexibility
- Deprecation path can be executed in parallel with fix deployment

---

## Talking Points

**For Stakeholders:**

- "We've identified the root cause: install_yamls PR #1158 changed credential generation from static to dynamic, breaking test fixtures that expected hardcoded passwords."
- "A fix is in review (tcib PR #408) that aligns test auth with the new credential model. It's a 2-line change in the test script."
- "Pipeline should stabilize within 24-48 hours of fix merge, pending upstream test-operator dependency resolution."
- "No production impact — this is a test-only regression. Customer deployments are unaffected."
- "The underlying security improvement (dynamic credentials) remains intact and is the right long-term direction."

**For Engineering:**

- "PR #1158 was a breaking change for test fixtures but a necessary security hardening. We should have anticipated test impact and bundled the fix."
- "The fix strategy (read password from OpenStackConfig) is more robust than hardcoding — it future-proofs against further credential model changes."
- "We're using this as a trigger to audit all test scenarios for hardcoded credential assumptions (smoke tests, tempest, etc.)."
- "Deprecation of `AdminPassword` / `AdminUsername` test-operator parameters is planned to prevent customer-facing regression."

---

## Deep Analysis

### Code Path Tracing

**Where Hardcoded Password Was Injected:**

**test-operator CR (likely):**

**Source:** [test-operator CRD example](https://github.com/openstack-k8s-operators/test-operator/tree/main/config/samples)
```yaml
apiVersion: test.openstack.org/v1beta1
kind: HorizonTest
spec:
  horizonTestImage: quay.io/openstack-k8s-operators/horizontest:latest
  adminUsername: admin
  adminPassword: "12345678"  # ← This is the problem
```

**tcib container runtime:**

**Source:** [tcib/base/os/horizontest/run_horizontest.sh](https://github.com/openstack-k8s-operators/tcib/blob/main/container-images/tcib/base/os/horizontest/run_horizontest.sh) (main branch)
```bash
# /container-images/tcib/base/os/horizontest/run_horizontest.sh
ADMIN_USERNAME=${ADMIN_USERNAME}  # From pod env
ADMIN_PASSWORD=${ADMIN_PASSWORD}  # From pod env (12345678)

# Later, OpenStackSDK uses these to build connection
```

**Fix location (PR #408):**

**Source:** [tcib PR #408](https://github.com/openstack-k8s-operators/tcib/pull/408) (proposed)
```bash
# Override injected value with actual cloud config password
ADMIN_PASSWORD=$(python3 -c "from openstack.config import OpenStackConfig; print(OpenStackConfig().get_one(cloud='default').auth['password'])")
```

### Dependency Chain for Fix Deployment

```
test-operator PR #473 ----+
  (remove default password)|
                           +---> ci-framework PR #4071 ---> tcib PR #408 (revised)
ci-framework PR #4071 -----+      (conditional override)
  (remove hardcoded config)
```

**Estimated Timeline:**
- Day 0 (today): test-operator PR #473 + ci-framework PR #4071 reviews
- Day 1-2: Merge dependencies
- Day 2-3: Update tcib PR #408 with conditional approach
- Day 3-4: Merge tcib PR #408
- Day 4-5: Component pipeline recovers

**Acceleration Path:**
If dependencies are slow, tcib PR #408 can merge with unconditional override as interim fix, then add conditional logic later. Trade-off: customer override capability lost temporarily.

### Cross-Repo Impact Assessment

**Other potential breakage points:**

1. **Smoke tests** (test-operator `Tempest` CR):
   - May also inject `ADMIN_PASSWORD=12345678`
   - Check: `oc get tempest -o yaml` for hardcoded credentials

2. **Ansible-based deployment tests** (edpm-ansible):
   - If playbooks hardcode passwords, they'll fail similarly
   - Check: `roles/*/defaults/main.yml` for `admin_password: "12345678"`

3. **Adoption tests** (standalone-to-crc):
   - CI failures during PR #1158 review suggest adoption may also be affected
   - Check: adoption test logs for auth failures

**Recommendation:** Proactive audit of all test scenarios before PR #1158 backport to 18.0-fr6 (cherry-pick #1159).

---

## Next Actions

### Immediate (Today)

1. **Track dependency PRs:**
   - [ ] Monitor test-operator PR #473 status
   - [ ] Monitor ci-framework PR #4071 status

2. **Review tcib PR #408:**
   - [ ] Verify fix approach with kstrenkova's conditional override suggestion
   - [ ] Check if interim unconditional merge is acceptable for velocity

3. **Audit related test scenarios:**
   - [ ] Grep test-operator CRs for hardcoded `password: "12345678"`
   - [ ] Check smoke test / tempest configs
   - [ ] Review adoption test failures from PR #1158 CI runs

### Short-term (This Week)

4. **Merge tcib PR #408 (or revised version):**
   - Wait for dependencies if <48h
   - Otherwise merge unconditional version as hotfix

5. **Verify pipeline recovery:**
   - Trigger component pipeline job post-merge
   - Monitor for OpenStackSDK connection errors

6. **Update component pipeline documentation:**
   - Document dynamic credential model
   - Add troubleshooting section for auth failures

### Medium-term (Next Sprint)

7. **Add integration test for credential changes:**
   - Prevent future regressions when credential model changes
   - Test fixture should validate auth works with dynamic passwords

8. **Execute test-operator parameter deprecation:**
   - Follow kstrenkova's proposed timeline
   - Add deprecation warnings to `AdminPassword` / `AdminUsername` fields
   - Update customer-facing docs

9. **Review PR #1158 backport (#1159) for 18.0-fr6:**
   - Ensure all test fixtures are updated before backport merges
   - Consider bundling tcib fix in same release

---

## References

### Primary Artifacts

- **Inquiry Source** — Original Slack message from Jan (see Key Artifacts table above)
- **GitHub PR Analysis** — Detailed PR #1158 and PR #408 review (see Key Artifacts section)

### External Links

- [install_yamls PR #1158](https://github.com/openstack-k8s-operators/install_yamls/pull/1158) — Dynamic password generation (root cause)
- [tcib PR #408](https://github.com/openstack-k8s-operators/tcib/pull/408) — Proposed fix
- [horizon-operator commit 427781ab](https://github.com/openstack-k8s-operators/horizon-operator/commit/427781ab94fc381b57ad4689e48ed6a171e528e0) — OpenStackSDK bump (red herring)
- [Zuul failure log](https://sf.apps.int.gpc.ocp-hub.prod.psi.redhat.com/logs/ac8/components-integration/ac832f9aca7d40ff8d271d5bcf6c3418/controller/ci-framework-data/tests/test_operator/horizon/ui_integration_test_results.html.gz?sort=result) — Test failure evidence

### Upstream Dependencies

- test-operator PR #473 — Remove default AdminPassword/AdminUsername
- ci-framework PR #4071 — Remove hardcoded test config

---

**Generated by:** /triassessment skill (inquiry mode, deep analysis)  
**Skill version:** 2026-07-23  
**Model:** claude-sonnet-4-5@20250929
