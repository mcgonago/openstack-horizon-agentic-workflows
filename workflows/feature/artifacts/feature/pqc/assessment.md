# PQC Compliance Assessment: [OSPRH-28889](https://issues.redhat.com/browse/OSPRH-28889)

## Ticket Classification

| Field | Value |
|-------|-------|
| **Ticket** | [OSPRH-28889](https://issues.redhat.com/browse/OSPRH-28889) |
| **Parent Epic** | [OSPRH-27427](https://issues.redhat.com/browse/OSPRH-27427) |
| **Component** | `cmd/main.go` |
| **Tier** | 2 (per-operator) |
| **Action** | Implement directly via PR to [horizon-operator](https://github.com/openstack-k8s-operators/horizon-operator) |
| **Tag** | pqc |
| **Domain** | Post-Quantum Cryptography compliance |

## Tier Analysis

[OSPRH-28889](https://issues.redhat.com/browse/OSPRH-28889) is classified as **Tier 2 (per-operator)** because it modifies
operator-specific code (`cmd/main.go`), not shared lib-common templates.
This is the correct tier for direct PR submission.

**Related tickets in the PQC epic:**

| Story | Tier | Status | Rationale |
|-------|------|--------|-----------|
| [OSPRH-28888](https://issues.redhat.com/browse/OSPRH-28888) | N/A | CLOSED | cert-manager handled upstream |
| **[OSPRH-28889](https://issues.redhat.com/browse/OSPRH-28889)** | **2** | **READY** | **cmd/main.go TLS 1.3 MinVersion** |
| [OSPRH-28890](https://issues.redhat.com/browse/OSPRH-28890) | 3 | BLOCKED | jsencrypt/RSA depends on Nova ([OSPRH-27628](https://issues.redhat.com/browse/OSPRH-27628)) |
| [OSPRH-28891](https://issues.redhat.com/browse/OSPRH-28891) | 1 | DEFER | ssl.conf cipher belongs in lib-common |
| [OSPRH-28892](https://issues.redhat.com/browse/OSPRH-28892) | 1 | DEFER | ssl.conf protocol belongs in lib-common |

## Technical Analysis

### The Problem

The horizon-operator's manager process (`cmd/main.go`) serves
metrics and webhook endpoints over TLS but does not enforce a
minimum TLS version. The default `tls.Config` allows TLS 1.0,
which:

1. Cannot negotiate ML-KEM (X25519MLKEM768) key exchange
2. Does not benefit from Go 1.24+'s automatic PQC support
3. Falls below NIST PQC readiness requirements

### The Fix

Enforce `tls.VersionTLS13` as `MinVersion` in the TLS configuration.
Go 1.24+ automatically enables X25519MLKEM768 hybrid key exchange
for TLS 1.3 sessions, making the application PQC-ready without any
additional cryptographic library changes.

### Code Change

**File**: `cmd/main.go` (after the `disableHTTP2` block, ~line 126)

**BEFORE** (no MinVersion set):
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

### Why This Works

- Go 1.24+ enables X25519MLKEM768 by default for TLS 1.3
- Setting `MinVersion = tls.VersionTLS13` ensures the hybrid
  ML-KEM key exchange is always available
- No additional dependencies or imports required
- The `crypto/tls` import already exists in `cmd/main.go`

## Validation Results

| Command | Status | Notes |
|---------|--------|-------|
| `go build ./...` | PASS | Clean compilation |
| `go fmt ./...` | PASS | No formatting changes needed |
| `go vet ./...` | PASS | No static analysis warnings |
| `make test` | PASS | 36/36 Ginkgo specs, ~75% coverage |
| `go test ./...` | PASS | All unit tests pass |

## PR History

| PR | Status | Notes |
|----|--------|-------|
| [PR #590](https://github.com/openstack-k8s-operators/horizon-operator/pull/590) | Closed | CI passed, closed per lib-common centralization strategy |
| [PR #593](https://github.com/openstack-k8s-operators/horizon-operator/pull/593) | Open | Resubmitted as Tier 2 only (cmd/main.go), awaiting /lgtm |

## Architecture Notes

### Why NOT ssl.conf Changes Here

[OSPRH-28891](https://issues.redhat.com/browse/OSPRH-28891) and [OSPRH-28892](https://issues.redhat.com/browse/OSPRH-28892) (ssl.conf cipher/protocol hardening)
are **Tier 1 (central)** changes. They belong in lib-common's
`CommonTemplates`, not as per-operator overrides. Creating local
`templates/horizon/config/ssl.conf` would:

- Fix only one operator while others remain vulnerable
- Diverge from lib-common when it eventually adds the fix
- Duplicate effort across multiple operator teams

The correct path: coordinate with Mauricio Harley for a single
lib-common PR that fixes ALL operators.

### [OSPRH-28890](https://issues.redhat.com/browse/OSPRH-28890) Block Status

Blocked on Nova team ([OSPRH-27628](https://issues.redhat.com/browse/OSPRH-27628)). The jsencrypt RSA password
decryption in Horizon depends on Nova's `os-server-password` API.
Three resolution paths are tracked in the [PQC Tracking Sheet](https://docs.google.com/spreadsheets/d/1Zr4Hw1Ca-yuDAr7Z1_Iwiic6659C8tae-P6F28D17Eg/edit?gid=1687906488#gid=1687906488).

## Recommendation

**Proceed with [PR #593](https://github.com/openstack-k8s-operators/horizon-operator/pull/593)** ([OSPRH-28889](https://issues.redhat.com/browse/OSPRH-28889) only). The change is:
- Minimal (6 lines)
- CI-validated (all checks pass)
- Correctly scoped (Tier 2, per-operator)
- Awaiting human `/lgtm` review

Set target version to 5.0.0 on [OSPRH-28889](https://issues.redhat.com/browse/OSPRH-28889) after merge.
