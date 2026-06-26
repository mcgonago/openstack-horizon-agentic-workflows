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

## 4. Code Change Catalog

### PR #1: cmd/main.go -- TLS 1.3 MinVersion (OSPRH-28889)

**Tier**: 2 (per-operator) -- implement directly

**Location**: After the `disableHTTP2` TLS option block (~line 126)

**BEFORE** (no MinVersion set -- defaults to TLS 1.0):
```go
	tlsOpts = append(tlsOpts, disableHTTP2)
}

// Create watchers for metrics and webhooks certificates
```

**AFTER** (TLS 1.3 enforced):
```go
	tlsOpts = append(tlsOpts, disableHTTP2)
}

// PQC: Enforce TLS 1.3 minimum for quantum-safe key exchange
// (X25519MLKEM768). Go 1.24+ enables hybrid ML-KEM by default,
// but only when TLS 1.3 is negotiated.
tlsOpts = append(tlsOpts, func(c *tls.Config) {
	c.MinVersion = tls.VersionTLS13
})

// Create watchers for metrics and webhooks certificates
```

**Lines changed**: +6

### PR #2: ssl.conf -- Apache SSL Hardening (OSPRH-28891 + 28892)

**Tier**: 1 (central) -- DEFER to lib-common. Do NOT implement as
a per-operator change. Propose these values to the core team.

**PROPOSED CHANGES** (for lib-common central PR):

**BEFORE** (lib-common default):
```apache
  SSLCipherSuite HIGH:MEDIUM:!aNULL:!MD5:!RC4:!3DES
  SSLProtocol all -SSLv2 -SSLv3 -TLSv1
```

**AFTER** (PQC-hardened):
```apache
  SSLCipherSuite HIGH:!aNULL:!MD5:!RC4:!3DES:!kRSA
  SSLProtocol -all +TLSv1.3 +TLSv1.2
```

**Changes explained**:
- `MEDIUM` removed: raises cipher strength floor
- `!kRSA` added: blocks static RSA (enforces forward secrecy)
- `-all +TLSv1.3 +TLSv1.2`: whitelist > blacklist, closes TLSv1.1 gap

**NOTE**: These values are correct. They just belong in lib-common,
not in horizon-operator. Contact Mauricio Harley to coordinate.

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
