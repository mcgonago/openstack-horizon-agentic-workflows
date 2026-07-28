# GitHub PR Analysis

## PR #1158: Dynamic Password Generation (Merged)

**Repository:** openstack-k8s-operators/install_yamls  
**Author:** abays  
**Status:** Merged on 2026-07-16  
**Files Changed:** 21 files (+313/-86 lines)

### Summary

This PR replaced all hardcoded passwords and secrets in install_yamls with dynamically generated values. A new `scripts/gen-secrets.sh` script creates a gitignored `.secrets.env` file containing randomly generated credentials for all OpenStack services.

### Key Changes

1. **New Secret Generation Script** (`scripts/gen-secrets.sh`):
   - Generates 30+ unique passwords and encryption keys
   - Creates `.secrets.env` file with `chmod 600` permissions
   - Uses OpenSSL for secure random generation
   - Skips regeneration if file already exists

2. **Makefile Integration**:
   - Added `-include .secrets.env` to load generated secrets
   - New targets: `make secrets`, `make secrets_clean`
   - Legacy `PASSWORD` override preserved for backward compatibility
   - All service-specific passwords now use dedicated variables

3. **Per-Service Credentials** (replacing single `PASSWORD=12345678`):
   - `ADMIN_PASSWORD` (was `PASSWORD`)
   - `DB_ROOT_PASSWORD` (was `PASSWORD`)
   - Individual passwords for: Aodh, Barbican, Ceilometer, CloudKitty, Designate, Glance, Neutron, Cinder, Ironic, Octavia, Nova, Manila, Heat, Swift, Watcher, etc.

4. **Infrastructure Passwords**:
   - `KUBEADMIN_PWD` (CRC/OCP admin)
   - `BMAAS_REDFISH_PASSWORD` (bare metal provisioning)
   - `EDPM_ROOT_PASSWORD` (compute node root)
   - `RGW_PASS` (Ceph RGW)
   - `BGP_PEER_PASSWORD` (MetalLB)

5. **Updated Scripts** (21 files):
   - All references to hardcoded `PASSWORD=12345678` replaced with specific variables
   - Database cleanup commands now use `DB_ROOT_PASSWORD`
   - EDPM node provisioning uses `EDPM_ROOT_PASSWORD`
   - BMaaS sushy-emulator uses `BMAAS_REDFISH_PASSWORD`

### Breaking Change Impact

**Root Cause of Component Pipeline Failures:**

The PR merged on July 16, 2026. Component pipeline failures started Sunday (likely July 20). Timeline matches the inquiry.

**What broke:**
- Test fixtures in `horizon-operator` and downstream repos expected static `ADMIN_PASSWORD=12345678`
- After this PR, `ADMIN_PASSWORD` is randomly generated per `.secrets.env` file
- Horizon integration tests authenticate using hardcoded password from pod injection
- OpenStack cloud config now uses different dynamically-generated password
- Auth mismatch → OpenStackSDK connection failures

**Backward Compatibility Attempt:**

The PR preserved a legacy override mechanism:

**Source:** [install_yamls/Makefile](https://github.com/openstack-k8s-operators/install_yamls/blob/main/Makefile)
```makefile
PASSWORD ?=
ifneq ($(PASSWORD),)
ADMIN_PASSWORD = $(PASSWORD)
# ... all other passwords follow PASSWORD
endif
```

However, this only works if `PASSWORD` env var is explicitly set. Test pods that inject `ADMIN_PASSWORD=12345678` directly bypass this mechanism.

### Review Comments

1. **stuggi (2026-07-15):** Suggested making more targets depend on `../.secrets.env` to ensure generation before use
2. **stuggi (2026-07-15):** Recommended `chmod 600` on secrets file (implemented)
3. Both comments were addressed before merge

### CI Results

Multiple CI pipeline failures during PR review (adoption-standalone-to-crc tests), but PR was merged after approvals from abays (author) and stuggi.

---

## PR #408: Fix for Horizon Test Breakage (Open)

**Repository:** openstack-k8s-operators/tcib  
**Author:** HanzJas (Jan Jasek)  
**Status:** Open (created 2026-07-22, 6 days after PR #1158 merged)  
**Files Changed:** 1 file (+2/-0 lines)

### Summary

This PR fixes the Horizon component pipeline test failures caused by PR #1158 by reading the admin password from OpenStack cloud config instead of using the hardcoded injected value.

### The Fix

**File:** `container-images/tcib/base/os/horizontest/run_horizontest.sh`

**Change:**

**Source:** [tcib PR #408](https://github.com/openstack-k8s-operators/tcib/pull/408)
```bash
+ADMIN_PASSWORD=$(python3 -c "from openstack.config import OpenStackConfig; print(OpenStackConfig().get_one(cloud='default').auth['password'])")
+
 # assert mandatory variables have been set
 [[ -z ${ADMIN_USERNAME} ]] && echo "ADMIN_USERNAME not set" && exit 1
 [[ -z ${ADMIN_PASSWORD} ]] && echo "ADMIN_PASSWORD not set" && exit 1
```

**Effect:**
- Dynamically reads the actual admin password from OpenStackConfig (clouds.yaml + secure.yaml)
- Overrides the hardcoded pod-injected `ADMIN_PASSWORD=12345678`
- Aligns test auth with the working CLI auth flow

### Discussion Thread

**kstrenkova (2026-07-23 09:07):**
- Suggests implementing the fix in `test-operator` instead of TCIB (higher level)
- Concerns about losing ability to override password via CR
- Proposes conditional default approach:
  ```bash
  if [[ -z "${ADMIN_PASSWORD}" ]]; then
      ADMIN_PASSWORD=$(python3 -c "from openstack.config import OpenStackConfig; ...")
  fi
  ```
- References PRs #473 (test-operator) and #4071 (ci-framework) that remove hardcoded defaults
- Suggests deprecation path for `AdminPassword` and `AdminUsername` parameters

**HanzJas (2026-07-23 10:36):**
- Agrees TCIB is lowest level, but questions if fix is needed at higher level
- Notes no current jobs override `ADMIN_PASSWORD` in horizontest
- Suggests parameter may not need to be overridable

**kstrenkova (2026-07-23 12:31):**
- Notes test-operator is shipped to customers, can't remove parameters without deprecation
- Proposes conditional approach to allow CR override during deprecation period
- Links to test-operator PR #473 and ci-framework PR #4071

**HanzJas (2026-07-23 15:19):**
- Agrees to wait for test-operator PRs to merge before proceeding
- Will test conditional approach once dependencies are in place

### Status

**PR State:** Open, needs revision  
**Blocker:** Waiting for test-operator PR #473 and ci-framework PR #4071 to merge  
**Approved by:** xtmprsqzntwlfb  
**Needs approval from:** gibizer (OWNERS)  
**Next Step:** Author will update to conditional approach once dependencies merge

---

## Relationship Between PRs

```
PR #1158 (install_yamls)          PR #408 (tcib)
   └─> Merged 2026-07-16             └─> Proposed Fix 2026-07-22
       │                                  │
       └─> Dynamic passwords             └─> Read from OpenStackConfig
           generated in .secrets.env         instead of hardcoded injection
           │
           └─> Component pipeline fails
               (Sunday 2026-07-20)
               │
               └─> OpenStackSDK connection errors
                   (auth mismatch)
```

## Technical Analysis

### Root Cause Chain

1. **Pre-PR #1158:** All services and tests use `PASSWORD=12345678`
2. **PR #1158 merges:** Passwords now dynamic, stored in `.secrets.env`
3. **OpenStack deployed:** Uses new random `ADMIN_PASSWORD` from `.secrets.env`
4. **Test pods launched:** Inject `ADMIN_PASSWORD=12345678` (hardcoded in test-operator CR)
5. **OpenStackSDK connection attempt:** Uses injected password (12345678)
6. **Keystone authentication:** Expects password from `.secrets.env` (different random value)
7. **Result:** HTTP 401 Unauthorized → test failures

### Why Legacy Override Didn't Help

The legacy `PASSWORD` override in install_yamls Makefile:

**Source:** [install_yamls/Makefile](https://github.com/openstack-k8s-operators/install_yamls/blob/main/Makefile)
```makefile
PASSWORD ?=
ifneq ($(PASSWORD),)
ADMIN_PASSWORD = $(PASSWORD)
endif
```

This only works if:
- `PASSWORD` env var is set when running `make input`
- The value propagates to OpenStack deployment

But test pods are configured separately via test-operator CRs, which directly inject:

**Source:** [test-operator CRD example](https://github.com/openstack-k8s-operators/test-operator/tree/main/config/samples)
```yaml
env:
  - name: ADMIN_PASSWORD
    value: "12345678"
```

This bypasses the Makefile entirely.

### Contributing Factor: OpenStackSDK Bump

Jan's inquiry mentions commit `427781ab` also bumped OpenStackSDK version. While this may have changed connection initialization behavior, it is NOT the root cause. The auth failure would occur regardless of SDK version if passwords don't match.

## Recommendations

See main triage assessment for recommendations and next actions.
