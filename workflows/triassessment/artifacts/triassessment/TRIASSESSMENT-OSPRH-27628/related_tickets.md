# Related Tickets: OSPRH-27628

**Generated:** 2026-07-07T10:45:00

---

## Ticket Hierarchy

| Level | Ticket | Title | Status | Tier |
|-------|--------|-------|--------|------|
| Strategy | [RHOSSTRAT-965](https://redhat.atlassian.net/browse/RHOSSTRAT-965) | PQC Parent Strategy | Open | — |
| Epic | [OSPRH-27427](https://redhat.atlassian.net/browse/OSPRH-27427) | Configuration horizon-operator to be PQC compliant | Open | — |
| Story | [OSPRH-28888](https://redhat.atlassian.net/browse/OSPRH-28888) | horizon-operator/cert-manager PQC Compliance | **Closed** | N/A (upstream) |
| Story | [OSPRH-28889](https://redhat.atlassian.net/browse/OSPRH-28889) | horizon-operator/tls-config PQC Compliance | Ready | 2 (per-operator) |
| Story | [OSPRH-28890](https://redhat.atlassian.net/browse/OSPRH-28890) | python-django-horizon/jsencrypt PQC Compliance | Open (BLOCKED) | 3 (cross-team) |
| Story | [OSPRH-28891](https://redhat.atlassian.net/browse/OSPRH-28891) | horizon-operator/apache-ssl-ciphersuite PQC Compliance | Open | 1 (central) |
| Story | [OSPRH-28892](https://redhat.atlassian.net/browse/OSPRH-28892) | horizon-operator/ssl-protocol PQC Compliance | Open | 1 (central) |
| Story | **[OSPRH-27628](https://redhat.atlassian.net/browse/OSPRH-27628)** | **Use PQC algorithm for show-server-password** | **Closed (Won't Do)** | **3 (cross-team)** |
| Cross-team | [OSPRH-27588](https://redhat.atlassian.net/browse/OSPRH-27588) | PQC analysis UI dependency (Nova team) | Open | — |

---

## Blocking Chain

```
Nova (os-server-password API — RSA encryption)
  │
  ├── blocks → OSPRH-27628 (Horizon: use PQC algorithm — CLOSED WON'T DO)
  │
  └── blocks → OSPRH-28890 (Horizon: jsencrypt PQC — OPEN, BLOCKED)
                  │
                  └── tracked via → OSPRH-27588 (cross-team dependency ticket)
```

**Independent (not blocked):**

```
OSPRH-28889 (TLS 1.3 MinVersion)     → Tier 2, implement directly in horizon-operator
OSPRH-28891 (ssl.conf cipher suite)   → Tier 1, defer to lib-common central PR
OSPRH-28892 (ssl.conf protocol)       → Tier 1, defer to lib-common central PR
OSPRH-28888 (cert-manager)            → CLOSED, handled upstream
```

---

## Cross-Team Dependencies

| Dependency | Team | Status | Contact | Notes |
|-----------|------|--------|---------|-------|
| Nova os-server-password API | Nova team | No plans to migrate | Via OSPRH-27588 | Must change RSA encryption to PQC |
| cloud-init key injection | cloud-init team | Unknown | — | Must support new key types |
| lib-common ssl.conf templates | Core operators (Mauricio Harley) | Pending | Mauricio Harley | OSPRH-28891 + 28892 should be central PRs |
| cert-manager PQC algorithms | cert-manager upstream | Waiting on ML-DSA support | — | OSPRH-28888 closed, upstream owns this |

---

## Resolution Paths (for the blocked items)

### Path A: Nova deprecates RSA password storage
- Nova removes or deprecates the os-server-password API
- Horizon removes the "Retrieve Password" UI
- **Horizon action:** Remove jsencrypt and password retrieval code
- **Likelihood:** Low — API is stable and used by some deployments

### Path B: Nova adds PQC algorithm support
- Nova encrypts with a PQC algorithm (e.g., ML-KEM)
- Nova communicates the algorithm used (new API field or metadata)
- Horizon adds multi-algorithm decryption support
- **Horizon action:** Add PQC decryption library alongside jsencrypt
- **Likelihood:** Medium-long term — depends on Nova team prioritization

### Path C: Accept the risk
- Document the HNDL exposure (low — transient password, authenticated API)
- Keep OSPRH-28890 open as a tracking ticket
- Close OSPRH-27628 as Won't Do (current recommendation)
- **Horizon action:** None; monitor Nova team progress
- **Likelihood:** This is the current path and recommended approach

---

## Summary

Of the 6 stories under the PQC epic (OSPRH-27427):

| Status | Count | Tickets |
|--------|-------|---------|
| Closed (done) | 1 | OSPRH-28888 (cert-manager, upstream) |
| Closed (won't do) | 1 | OSPRH-27628 (show-server-password, cross-team) |
| Ready to implement | 1 | OSPRH-28889 (TLS 1.3, Tier 2) |
| Deferred to lib-common | 2 | OSPRH-28891, OSPRH-28892 (ssl.conf, Tier 1) |
| Blocked on Nova | 1 | OSPRH-28890 (jsencrypt, Tier 3) |
