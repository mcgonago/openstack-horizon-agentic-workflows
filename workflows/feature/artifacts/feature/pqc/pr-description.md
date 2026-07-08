# PR Description: [OSPRH-28889](https://issues.redhat.com/browse/OSPRH-28889)

Ready-to-paste pull request body for [horizon-operator](https://github.com/openstack-k8s-operators/horizon-operator).

---

## Summary

- Enforce TLS 1.3 MinVersion for the operator manager's metrics/webhook
  endpoints to enable PQC-ready key exchange (X25519MLKEM768)
- Go 1.24+ automatically negotiates ML-KEM hybrid key exchange for TLS 1.3
  sessions, making this a zero-dependency PQC compliance fix
- Part of the [OSPRH-27427](https://issues.redhat.com/browse/OSPRH-27427) PQC epic ([RHOSSTRAT-965](https://issues.redhat.com/browse/RHOSSTRAT-965))

## Changes

- `cmd/main.go`: Add `tls.Config.MinVersion = tls.VersionTLS13` TLS option
  after the existing `disableHTTP2` block (~line 126, +6 lines)

## Why TLS 1.3 Only

Go 1.24 enables X25519MLKEM768 (hybrid ML-KEM, FIPS 203) by default for
TLS 1.3 connections. Setting MinVersion to TLS 1.3 ensures the operator
always negotiates quantum-safe key exchange without additional libraries
or configuration.

## Scope

This PR addresses **only** [OSPRH-28889](https://issues.redhat.com/browse/OSPRH-28889) (Tier 2, per-operator). Related
Tier 1 changes (ssl.conf cipher/protocol hardening for [OSPRH-28891](https://issues.redhat.com/browse/OSPRH-28891)/[OSPRH-28892](https://issues.redhat.com/browse/OSPRH-28892))
are deferred to lib-common centralization per coordination with Mauricio
Harley.

## Test plan

- [x] `go build ./...` -- clean compilation
- [x] `go fmt ./...` -- no formatting issues
- [x] `go vet ./...` -- no static analysis warnings
- [x] `make test` -- 36/36 Ginkgo specs pass (~75% coverage)
- [x] `go test ./...` -- all unit tests pass
- [ ] Post-deploy: `openssl s_client -connect <endpoint>:443 -tls1_3`
  confirms TLSv1.3 negotiation

## References

- Epic: [OSPRH-27427](https://issues.redhat.com/browse/OSPRH-27427)
- Story: [OSPRH-28889](https://issues.redhat.com/browse/OSPRH-28889)
- Parent: [RHOSSTRAT-965](https://issues.redhat.com/browse/RHOSSTRAT-965)
- PQC Tracking: [Google Sheets](https://docs.google.com/spreadsheets/d/1Zr4Hw1Ca-yuDAr7Z1_Iwiic6659C8tae-P6F28D17Eg/edit?gid=1687906488#gid=1687906488)
