# Feature Tag: PQC Compliance for Horizon-Operator

Tag: pqc
Domain: Post-Quantum Cryptography compliance for OpenStack horizon-operator

## 1. Domain Fundamentals

### What is Post-Quantum Cryptography?

Post-Quantum Cryptography (PQC) refers to cryptographic algorithms
designed to resist attacks by quantum computers. NIST standardized
ML-KEM (Module-Lattice-Based Key-Encapsulation Mechanism, FIPS 203)
as the primary key exchange algorithm for post-quantum TLS.

### The Go 1.24+ Connection

Go 1.24 and later automatically enable **X25519MLKEM768** hybrid key
exchange for TLS 1.3 sessions. This means:

- If the Go binary negotiates TLS 1.3, ML-KEM is used by default
- If the Go binary falls back to TLS 1.2, ML-KEM is NOT available
- Therefore: enforcing TLS 1.3 MinVersion is the PRIMARY action
  needed for PQC readiness in Go applications

### Why !kRSA Matters

Static RSA key exchange (kRSA) does not provide forward secrecy.
A quantum computer could retroactively decrypt recorded traffic
encrypted with static RSA. Blocking kRSA forces ephemeral key
exchange (ECDHE/DHE), which provides forward secrecy regardless
of quantum computing advances.

## 2. Scope

### Epic and Story Breakdown

Parent epic: [OSPRH-27427](https://issues.redhat.com/browse/OSPRH-27427)
PQC Tracking Sheet: [Google Sheets](https://docs.google.com/spreadsheets/d/1Zr4Hw1Ca-yuDAr7Z1_Iwiic6659C8tae-P6F28D17Eg/edit?gid=1687906488#gid=1687906488)
PQC Engineer Lead: Mauricio Harley
Parent Jira: [RHOSSTRAT-965](https://issues.redhat.com/browse/RHOSSTRAT-965)

| Story | Component | Status | Tier | Action |
|-------|-----------|--------|------|--------|
| OSPRH-28888 | cert-manager | CLOSED | N/A | Handled upstream |
| OSPRH-28889 | cmd/main.go | READY | 2 (per-operator) | PR to horizon-operator |
| OSPRH-28890 | jsencrypt/RSA | BLOCKED | 3 (cross-team) | Nova dependency |
| OSPRH-28891 | ssl.conf cipher | DEFER | 1 (central) | lib-common scope |
| OSPRH-28892 | ssl.conf protocol | DEFER | 1 (central) | lib-common scope |

### Ticket Routing

- OSPRH-28889 -> PR #1 (cmd/main.go only) -- Tier 2, implement directly
- OSPRH-28891 -> PR #2 (ssl.conf only) -- Tier 1, defer to lib-common
- OSPRH-28892 -> PR #2 (ssl.conf only) -- Tier 1, defer to lib-common
- OSPRH-28890 -> BLOCKED (explain Nova dependency, do NOT implement)
- OSPRH-28888 -> CLOSED (no action needed)
- OSPRH-27427 -> Both PRs (parent epic)

### Tier Classification

- **Tier 1 (CENTRAL)**: Changes to lib-common CommonTemplates.
  Core operators team scope. Coordinate with Mauricio Harley.
  Do NOT submit per-operator PRs for Tier 1 changes.

- **Tier 2 (PER-OPERATOR)**: Changes to operator-specific code
  (e.g., cmd/main.go). Horizon team scope. Submit PR directly.

- **Tier 3 (CROSS-TEAM)**: Changes blocked on another team.
  Track in PQC Tracking Sheet. Coordinate via Mauricio.

### OSPRH-28890 Block Details

Blocked on Nova team (OSPRH-27628). The jsencrypt RSA password
decryption depends on Nova's os-server-password API.

Three resolution paths:
- A: Nova deprecates RSA password storage -> Horizon removes UI
- B: Nova adds PQC -> Horizon adds multi-algorithm decryption
- C: Accept risk -> Document HNDL exposure (low -- transient)

## 3. Target Repository

- **Repository**: openstack-k8s-operators/horizon-operator
- **URL**: https://github.com/openstack-k8s-operators/horizon-operator
- **Branch**: main
- **Language**: Go + Apache config templates
- **Build**: Go modules + Makefile + Ginkgo test framework
- **Go version**: 1.24+ required (for ML-KEM default behavior)
- **Dependency**: lib-common (openstack-k8s-operators/lib-common)

### Key Files

| File | Purpose |
|------|---------|
| `cmd/main.go` | Operator manager entry point; TLS config at L124-135 |
| `templates/horizon/config/ssl.conf` | Apache SSL configuration (local override) |
| `go.mod` | Go module definition (check Go version here) |
| `Makefile` | Build targets including `test` |

## 4. Code Change Requirements

This section describes WHAT needs to change and WHY. The AI must
derive the actual code from reading the target repository, guided
by these requirements and the architecture patterns in Section 5.

Do NOT provide exact code to copy. The AI should read `cmd/main.go`,
understand the TLS configuration flow, and produce the correct change
independently.

### Change #1: Enforce TLS 1.3 minimum (OSPRH-28889)

**Tier**: 2 (per-operator) -- implement directly

**Intent**: Set TLS 1.3 as the minimum protocol version for the
operator's webhook and metrics servers, so that Go 1.24+'s automatic
X25519MLKEM768 hybrid post-quantum key exchange is always negotiated.

**Why**: Without an explicit MinVersion, Go defaults to TLS 1.0,
allowing TLS 1.2 connections that cannot negotiate ML-KEM. This
leaves the operator vulnerable to Harvest Now, Decrypt Later (HNDL)
quantum attacks.

#### Code Flow Walkthrough (cmd/main.go)

The TLS configuration in `cmd/main.go` follows the kubebuilder
convention of accumulating options as a slice of closure functions.
Understanding this flow is essential for placing the change correctly:

1. **Declaration (~line 84):** `var tlsOpts []func(*tls.Config)`
   An empty slice that will hold TLS configuration closures.
   Each closure receives a `*tls.Config` and mutates it.

2. **disableHTTP2 block (~lines 118-121):** The first closure is
   conditionally appended. When `--enable-http2` is NOT set, a
   closure that nils out `NextProtos` is appended to `tlsOpts`.
   This is the EXISTING TLS configuration -- the new MinVersion
   closure should be inserted AFTER this block.

3. **Insertion point (~line 126):** Immediately after the
   disableHTTP2 conditional block. This is where the new closure
   that sets `c.MinVersion = tls.VersionTLS13` should be appended
   to `tlsOpts`. Placing it here keeps all TLS configuration
   closures together in the same logical section.

4. **Webhook server (~line 131):** `webhook.Server{TLSOpts: tlsOpts}`
   The webhook server receives a COPY of the tlsOpts slice.
   Because our closure is already in the slice, the webhook server
   will enforce TLS 1.3.

5. **Metrics server (~line 164):** The metrics bind address
   configuration also consumes `tlsOpts`. Both servers share the
   same base configuration -- this is WHY a single append to
   `tlsOpts` covers both servers.

**Key insight:** Because both servers read from the same `tlsOpts`
slice, a single `append` at the declaration site (step 3) propagates
to all TLS consumers. Do NOT configure servers individually.

**What happens without MinVersion:** When `MinVersion` is not set,
Go's `crypto/tls` defaults to TLS 1.0 (`tls.VersionTLS10`). This
means a client can negotiate TLS 1.2, which does not support ML-KEM
hybrid key exchange. The operator would function correctly but
without post-quantum protection -- vulnerable to HNDL attacks where
an adversary records TLS 1.2 traffic today and decrypts it with a
future quantum computer.

**Constraints**:
- The change must apply to BOTH the webhook server and the metrics
  server -- find the shared TLS configuration point, do not configure
  them separately
- Use the standard Go `crypto/tls` package (already imported)
- Use the `tls.VersionTLS13` constant (do not hardcode `0x0304`)
- Follow the existing pattern: TLS options are accumulated in a
  slice of `func(*tls.Config)` functions
- Insert the new option near the existing TLS configuration block
  (the `disableHTTP2` conditional), not at an arbitrary location
- Include a brief comment explaining the PQC rationale

**What NOT to do**:
- Do not add new imports (crypto/tls is already imported)
- Do not modify the disableHTTP2 logic
- Do not change any other TLS settings (ciphers, curves, etc.)
- Do not touch the webhook or metrics server creation code

#### Compatibility Analysis

Setting `MinVersion = tls.VersionTLS13` affects all TLS clients
connecting to the operator's webhook and metrics endpoints:

| Client | TLS 1.3 Support | Impact |
|--------|-----------------|--------|
| Kubernetes API server | Since K8s 1.13 (2018) | None -- all supported K8s versions work |
| cert-manager | Full support | None |
| Prometheus/monitoring | Full support | None |
| Custom admission webhooks | Go 1.13+ (2019) | None for Go clients |
| Older curl/openssl clients | Requires OpenSSL 1.1.1+ | Minimal risk (operator endpoints are not user-facing) |

**Breaking change risk: LOW.** Operator webhook and metrics endpoints
are internal cluster services, not user-facing APIs. All Kubernetes
components that connect to these endpoints support TLS 1.3.

### Change #2: Apache SSL Hardening (OSPRH-28891 + 28892)

**Tier**: 1 (central) -- DEFER to lib-common. Do NOT implement as
a per-operator change.

**Intent**: Block static RSA key exchange (!kRSA) and whitelist
TLS 1.2/1.3 protocols in Apache's ssl.conf.

**Why these belong in lib-common, not here**:
- ssl.conf is distributed via lib-common CommonTemplates
- A per-operator override creates divergence and only fixes one operator
- The correct fix is a single lib-common PR that fixes ALL operators

**Action**: Do NOT implement. Propose the requirements to
Mauricio Harley for a lib-common central PR. The requirements are:
- Remove MEDIUM from SSLCipherSuite (raises cipher strength floor)
- Add !kRSA to SSLCipherSuite (blocks static RSA key exchange)
- Switch SSLProtocol from blacklist to whitelist approach
- Allow only TLSv1.2 and TLSv1.3

## 5. Architecture Patterns

### 5.1 lib-common Template Override Mechanism

The ssl.conf is NOT edited in place. The horizon-operator originally
inherited ssl.conf from lib-common's CommonTemplates (commit `858b826`).

To customize: create a LOCAL file at `templates/horizon/config/ssl.conf`.
lib-common's `template_util.go` (L302-305) confirms: "local operator
templates rendered below overwrite the common ones."

DO NOT:
- Modify lib-common's ssl.conf directly
- Remove the lib-common dependency
- Use a different filename (must match exactly)

### 5.2 PQC Centralization Strategy

The PQC compliance effort across all OpenStack operators is coordinated
centrally:

- **Engineer Lead**: Mauricio Harley
- **Tracking**: PQC Tracking Sheet (Google Sheets)
- **Tabs**: Analyzed Repositories, Common Findings, per-operator
- **Parent Jira**: RHOSSTRAT-965
- **Key insight**: lib-common templates are CORE TEAM responsibility

When implementing PQC changes:
1. FIRST classify the change tier (see Section 2)
2. For Tier 1 (central): do NOT create a per-operator PR.
   Instead, propose the changes to Mauricio for a lib-common PR.
3. For Tier 2 (per-operator): proceed with normal PR workflow.
4. For Tier 3 (cross-team): track status, do not implement.

### 5.3 Why Local Overrides Are Incorrect for ssl.conf

Creating per-operator ssl.conf overrides leads to:
- Only one operator gets the fix; others remain vulnerable
- Template divergence when lib-common eventually fixes centrally
- Multiple operators making the same change independently
- Inconsistency across the fleet

The correct approach: propose the exact cipher/protocol values
to the core team for a SINGLE lib-common PR that fixes ALL
operators simultaneously.

## 6. Validation Commands

Run these in the horizon-operator checkout after changes. ALL must pass.

| Command | What It Checks | Expected Result |
|---------|----------------|-----------------|
| `go build ./...` | Compilation | Clean, no errors |
| `go fmt ./...` | Formatting | No output (already formatted) |
| `go vet ./...` | Static analysis | No warnings |
| `make test` | Ginkgo suite | 36/36 specs, ~75% coverage |
| `go test ./...` | Unit tests | All pass |

### Post-Deployment Verification

```bash
# Verify TLS 1.3 is negotiated
openssl s_client -connect <horizon-endpoint>:443 -tls1_3
# Expected: Protocol: TLSv1.3, TLS_AES_256_GCM_SHA384

# Verify kRSA ciphers are NOT available
openssl s_client -connect <horizon-endpoint>:443 -cipher kRSA
# Expected: handshake failure (no shared cipher)
```

## 7. Delivery Pattern

### Commit Message Format

```
OSPRH-XXXXX: PQC compliance -- <brief description>
```

### PR Description Template

```markdown
## Summary
- <1-3 bullet points>

## Changes
- <file>: <what changed>

## Test plan
- [ ] go build ./...
- [ ] go test ./...
- [ ] make test
- [ ] Verify TLS 1.3 with openssl s_client
```

### GitHub Workflow

1. Fork: `gh repo fork openstack-k8s-operators/horizon-operator`
2. Branch: `git checkout -b osprh-XXXXX-pqc-compliance`
3. Push: `git push -u origin osprh-XXXXX-pqc-compliance`
4. PR: `gh pr create --repo openstack-k8s-operators/horizon-operator`
5. Default: `gh repo set-default openstack-k8s-operators/horizon-operator`

## 9. Assessment Structure

The assessment artifact MUST follow this structure. Use these
templates to produce a complete, auditable analysis.

### Executive Summary Table

Every assessment opens with this table:

| Field | Value |
|-------|-------|
| Risk Level | [Low / Medium / High / Critical] |
| Recommendation | [Merge / Merge with conditions / Defer / Block] |
| Confidence | [High / Medium / Low -- explain if not High] |
| Breaking Changes | [None / Conditional -- list affected clients] |

### Risk Assessment Rubric

Use these definitions consistently:

- **Critical**: Breaks existing TLS connections or disables encryption.
  Operator pods fail to start, webhooks unreachable, metrics scrapers
  rejected. Requires immediate rollback.
- **High**: Weakens security posture below baseline. Allows downgrade
  attacks, disables forward secrecy, or exposes key material.
- **Medium**: Compliance gap without a direct exploit path. Feature
  works but does not meet PQC requirements (e.g., TLS 1.2 still
  permitted, kRSA not blocked).
- **Low**: Cosmetic, documentation-only, or non-functional gap.
  No security impact. Example: missing comment, suboptimal cipher
  ordering.

### Compliance Checklist

One row per PQC requirement. Every row needs evidence:

| Requirement | Status | Evidence |
|-------------|--------|----------|
| TLS 1.3 enforced (MinVersion = tls.VersionTLS13) | PASS / FAIL / N-A | file:line or validation cmd |
| kRSA blocked (no static RSA key exchange) | PASS / FAIL / N-A | file:line or validation cmd |
| X25519MLKEM768 enabled (Go 1.24+ default on TLS 1.3) | PASS / FAIL / N-A | Go version from go.mod |
| Forward secrecy guaranteed (ephemeral key exchange only) | PASS / FAIL / N-A | cipher suite analysis |
| Both webhook and metrics servers covered | PASS / FAIL / N-A | code path trace |

### Sibling Stories Table

Status of all tickets under the parent epic:

| Ticket | Component | Tier | Status | This Run |
|--------|-----------|------|--------|----------|
| OSPRH-28889 | cmd/main.go | 2 | [status] | [analyzed / implemented / skipped] |
| OSPRH-28891 | ssl.conf cipher | 1 | DEFER | documented requirements only |
| OSPRH-28892 | ssl.conf protocol | 1 | DEFER | documented requirements only |
| OSPRH-28890 | jsencrypt/RSA | 3 | BLOCKED | dependency explained |
| OSPRH-28888 | cert-manager | N/A | CLOSED | no action |

## 10. Design Templates

### Per-Subsystem Design Sections

The design artifact should contain one subsection per code subsystem
affected. For PQC, the relevant subsystems are:

**Go TLS Config subsystem (cmd/main.go)**
- Architecture: the `[]func(*tls.Config)` closure-append pattern
- Code flow: declaration -> disableHTTP2 append -> MinVersion append
  -> webhook consumption -> metrics consumption
- Insertion point: after the disableHTTP2 conditional block
- Expected content: Current State excerpts (BEFORE), Proposed Change
  (AFTER), rationale for placement, impact on both servers

**Apache SSL subsystem (templates/horizon/config/ssl.conf)**
- Current directives: SSLCipherSuite, SSLProtocol values
- Proposed directives: HIGH:!aNULL:!MD5:!RC4:!3DES:!kRSA for ciphers,
  -all +TLSv1.3 +TLSv1.2 for protocol
- lib-common integration: why this is Tier 1, what the central PR
  should contain, who to coordinate with

### Before/After Table Format

Use this structure for every proposed code change:

| Component | Before | After | Validation |
|-----------|--------|-------|------------|
| TLS MinVersion | Not set (defaults to TLS 1.0) | tls.VersionTLS13 | openssl s_client -tls1_2 fails |
| Cipher suite | Inherited from lib-common | HIGH:!aNULL:!MD5:!RC4:!3DES:!kRSA | openssl ciphers check |
| Protocol | Inherited from lib-common | -all +TLSv1.3 +TLSv1.2 | openssl s_client -tls1_3 succeeds |

### Risk Assessment Table Format

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| TLS 1.2 clients rejected | Low | High | All K8s components support TLS 1.3 |
| ML-KEM not negotiated | Very Low | Medium | Verify Go 1.24+ in go.mod |
| Rollback needed | Low | Medium | Keep prior operator image as fallback |
| CI test failures | Low | Low | MinVersion does not affect unit tests |

## 11. Quality Expectations

### Artifact Depth Targets

| Artifact | Minimum Words | Recommended | Key Depth Indicators |
|----------|---------------|-------------|----------------------|
| assessment.md | 1,200 | 1,400-1,500 | Executive Summary table, Compliance Checklist, per-file analysis |
| design.md | 800 | 1,000-1,200 | Subsystem breakdown, Before/After tables, risk assessment |
| testing.md | 400 | 500-600 | Per-command detail, negative test cases, expected output |
| pr-description.md | 200 | 250-300 | Copy-paste ready, all ticket links |
| next-steps.md | 250 | 300-350 | Exact commands, conditional paths |
| what-ai-did.md | 400 | 450-500 | Actual execution data, step-to-SKILL.md mapping |
| **Total** | **3,250** | **3,800-4,500** | |

### Evidence Standards

- Every code claim MUST include file:line references
- Show BOTH the current state (BEFORE) and proposed change (AFTER)
- Compliance Checklist rows must cite specific evidence (file:line
  for code, command output for validation, go.mod for version)
- Domain knowledge statements (e.g., "ML-KEM is FIPS 203") do NOT
  require file:line references
- Procedural steps (e.g., "run go build") do NOT require file:line

### What "Substantive" Means

Bad (generic filler):
> Code Analysis: Found some issues in the TLS configuration.

Good (domain-specific, evidence-backed):
> Code Analysis (cmd/main.go:84-164): The tlsOpts slice is declared
> at line 84 as []func(*tls.Config). Currently, MinVersion is not
> set, defaulting to TLS 1.0. The disableHTTP2 closure at lines
> 118-121 is the only existing TLS option. Proposed: append a new
> closure at line 126 setting c.MinVersion = tls.VersionTLS13.
> Both the webhook server (line 131) and metrics server (line 164)
> consume tlsOpts, so both are covered by a single append.

## 8. Reference Implementation (Post-Hoc)

**PURPOSE**: This section records what a successful implementation
looks like AFTER it was produced and validated. It is NOT input for
the AI during implementation -- Section 4 provides the requirements.

This section exists for:
- **--dry-run comparison**: verify the AI independently derived the
  same solution
- **Cross-operator replication**: when applying the same pattern to
  other operators, this shows what the end result should look like
- **Review validation**: reviewers can compare a new PR against
  the reference

### Reference: Change #1 -- TLS 1.3 MinVersion (PR #593)

**Source**: PR https://github.com/openstack-k8s-operators/horizon-operator/pull/593
**Created by**: /pqc skill (ipatchset), 2026-05-09
**CI status**: All checks passing

**Diff** (cmd/main.go, after the disableHTTP2 block):
```go
+// PQC: Enforce TLS 1.3 minimum for quantum-safe key exchange
+// (X25519MLKEM768). Go 1.24+ enables hybrid ML-KEM by default,
+// but only when TLS 1.3 is negotiated.
+tlsOpts = append(tlsOpts, func(c *tls.Config) {
+    c.MinVersion = tls.VersionTLS13
+})
```

### Reference: Change #2 -- Apache SSL Hardening (NOT IMPLEMENTED)

No reference implementation exists. This is a Tier 1 (central)
change that belongs in lib-common. The proposed values are:

```apache
SSLCipherSuite HIGH:!aNULL:!MD5:!RC4:!3DES:!kRSA
SSLProtocol -all +TLSv1.3 +TLSv1.2
```

These have not been submitted. Coordinate with Mauricio Harley.
