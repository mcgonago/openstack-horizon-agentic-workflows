---
name: imock
description: Create interactive testing lab for OpenDev review verification
---

# /imock — Interactive Mock Lab Generator

Create a before/after testing lab for an OpenDev Gerrit review.

## Usage

/imock assessment=TRIASSESSMENT-OSPRH-25872 review=998960 clone=horizon-osprh-25872

## Parameters

- `assessment`: Case ID from artifacts/triassessment/ (required)
- `review`: OpenDev review number (required)
- `clone`: Directory name under repo/ with Horizon checkout (required)

## Output

Lab directory at: `{clone}/lab/`

Quick start:
```bash
cd {clone}/lab
tox -e before   # Without patch
tox -e after    # With patch
```
