# Triage Assessment: OSPRH-27628

**Generated:** 2026-07-07T10:45:00
**Skill:** /triassessment
**Model:** claude-opus-4-6

---

## Ticket Summary

| Field | Value |
|-------|-------|
| Key | [OSPRH-27628](https://redhat.atlassian.net/browse/OSPRH-27628) |
| Summary | Use a post-quantum-safe algorithm for the show-server-password endpoint |
| Status | Closed (Won't Do) |
| Type | Story |
| Epic | [OSPRH-27427](https://redhat.atlassian.net/browse/OSPRH-27427) — Configuration horizon-operator to be PQC compliant |
| Related | [OSPRH-28890](https://redhat.atlassian.net/browse/OSPRH-28890) — python-django-horizon/jsencrypt PQC Compliance |
| Cross-team | [OSPRH-27588](https://redhat.atlassian.net/browse/OSPRH-27588) — PQC analysis UI dependency (Nova team) |

---

## Technical Context

The Nova compute API endpoint [`show-server-password`](https://docs.openstack.org/api-ref/compute/#show-server-password) returns an instance's admin password encrypted with the instance's SSH public key. Today, that key is always RSA — it is an assumption baked into both Nova (encryption side) and Horizon (decryption side via the `jsencrypt` JavaScript library).

OSPRH-27628 asked: "make Horizon use a post-quantum-safe algorithm for this endpoint." The problem is that Horizon cannot unilaterally change the algorithm — the encryption happens in Nova, the key injection happens via cloud-init, and the decryption happens in Horizon/CLI. All three must migrate together. There is no Horizon-only fix.

This is classified as **Tier 3 (cross-team)** in the PQC compliance knowledge base (per feature-pqc.md, Section 2): changes blocked on another team. The Nova team owns the encryption side and would need to either:
- Deprecate the RSA password storage mechanism entirely, OR
- Add PQC algorithm support and communicate the algorithm used

Neither has happened, and no Nova-side work is planned.

---

## Dependencies & Blockers

| Ticket | Relationship | Status | Impact |
|--------|-------------|--------|--------|
| [OSPRH-27427](https://redhat.atlassian.net/browse/OSPRH-27427) | Parent Epic | Open | PQC compliance epic for horizon-operator |
| [OSPRH-28890](https://redhat.atlassian.net/browse/OSPRH-28890) | Sibling Story (same fix area) | Open | jsencrypt PQC — explicitly BLOCKED on Nova |
| [OSPRH-27588](https://redhat.atlassian.net/browse/OSPRH-27588) | Cross-team dependency | Open | Nova team asked to investigate; no resolution yet |
| [OSPRH-28889](https://redhat.atlassian.net/browse/OSPRH-28889) | Sibling Story (different fix) | Ready | TLS 1.3 MinVersion in cmd/main.go — Tier 2, implementable now |
| [OSPRH-28891](https://redhat.atlassian.net/browse/OSPRH-28891) | Sibling Story (different fix) | Open | Apache ssl.conf cipher suite — Tier 1, deferred to lib-common |
| [OSPRH-28892](https://redhat.atlassian.net/browse/OSPRH-28892) | Sibling Story (different fix) | Open | Apache ssl.conf protocol — Tier 1, deferred to lib-common |
| [OSPRH-28888](https://redhat.atlassian.net/browse/OSPRH-28888) | Sibling Story (resolved) | Closed | cert-manager — handled upstream |

---

## Impact Analysis

### If we close OSPRH-27628 as Won't Do:

- **Accepted risk is LOW.** The show-server-password feature is rarely used in production. The vulnerability is "Harvest Now, Decrypt Later" (HNDL) — an attacker would need to intercept the encrypted password in transit AND store it for future quantum decryption. The password is transient (used once at instance boot) and the API endpoint is already authenticated.
- **No Horizon-only fix exists.** Even if we wanted to implement this, we cannot — Nova must change first. Closing as Won't Do accurately reflects that Horizon cannot act alone.
- **OSPRH-28890 covers the same ground.** The sibling story OSPRH-28890 already tracks the jsencrypt/RSA dependency on Nova. Keeping both open is redundant.
- **The parent epic (OSPRH-27427) is NOT blocked.** The other sibling stories (OSPRH-28889 TLS config, OSPRH-28891/28892 ssl.conf) are independent and can proceed regardless.

### If we keep OSPRH-27628 open:

- It remains permanently blocked with no path to resolution until Nova acts.
- It creates noise in sprint planning and backlog grooming.
- OSPRH-28890 already serves as the tracking ticket for this dependency.

### Who else is affected:

- **Nova team** — owns the encryption side; OSPRH-27588 is their tracking ticket
- **Mauricio Harley** (PQC Engineer Lead) — coordinates cross-team PQC effort
- **cloud-init team** — would need to support new key types for injection

---

## Recommendation

| | |
|---|---|
| **Verdict** | **CLOSE AS WON'T DO** |
| **Confidence** | **HIGH** |

**Rationale:**

1. **No Horizon-only fix is possible.** The encryption algorithm is chosen by Nova. Horizon merely decrypts what Nova provides. Until Nova migrates, Horizon cannot change its decryption algorithm (per feature-pqc.md, Section 2 — OSPRH-28890 Block Details).

2. **The risk exposure is low.** The show-server-password endpoint is authenticated, the password is transient, and the HNDL attack vector requires both network interception and future quantum computing capability.

3. **Duplicate tracking exists.** OSPRH-28890 ("python-django-horizon/jsencrypt PQC Compliance — dependent on Nova team") explicitly tracks the same dependency. It is the correct home for this work if/when Nova acts.

4. **Closing this does not block the PQC epic.** The remaining Horizon-side PQC work (OSPRH-28889, OSPRH-28891, OSPRH-28892) is independent and can proceed.

---

## Talking Points

For responding to the stakeholder:

1. **Yes, we are okay closing OSPRH-27628 as Won't Do.** The show-server-password endpoint uses RSA because that's what Nova encrypts with — Horizon can't unilaterally change the decryption algorithm.

2. **This is a cross-project dependency, not a Horizon bug.** Nova, cloud-init, and Horizon/CLI would all need to migrate together. No Nova-side work is planned.

3. **We're not ignoring it — OSPRH-28890 tracks the dependency.** If Nova ever migrates to a PQC algorithm, OSPRH-28890 is where Horizon's follow-up work would be tracked.

4. **The risk is low.** The password is transient (used once at boot), the API is authenticated, and HNDL attacks on this specific vector are impractical.

5. **The rest of our PQC work is unblocked.** OSPRH-28889 (TLS 1.3 MinVersion) is ready for implementation. OSPRH-28891/28892 (ssl.conf hardening) are deferred to lib-common as a central fix.
