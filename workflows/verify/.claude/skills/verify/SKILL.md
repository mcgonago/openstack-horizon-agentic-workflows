---
name: verify
description: End-to-end functional verification of Horizon Gerrit reviews using Playwright
version: 1.0.0
---

# /verify — Horizon Review Verification

Automates end-to-end functional verification of OpenStack Horizon Gerrit reviews.

## Usage

```
/verify <review_number> [--execute] [--phase N] [--groups A,B,C] [--no-before] [--post-merge] [--cleanup] [--status]
```

## Arguments

- `review_number` — Gerrit review number (e.g., 992714)
- `--execute` — Auto-execute all phases without pausing
- `--phase N` — Resume from phase N (1-7)
- `--groups A,B,C` — Run only specific test groups
- `--no-before` — Skip baseline testing, only test the patched version
- `--post-merge` — Review already merged; use revert technique for baseline
- `--devstack HOST` — Override DevStack host
- `--cleanup` — Delete test resources from DevStack and exit
- `--status` — Print current verification state and exit

## What it does

1. Fetches review from Gerrit, identifies changed files, selects recipe
2. Connects to DevStack, runs preflight checks, creates test resources
3. Deploys Horizon with base branch (AngularJS baseline)
4. Runs Playwright tests against baseline panel
5. Applies review patch, restarts Horizon (Python panel)
6. Runs same tests against patched panel
7. Generates verification report with before/after screenshots and parity matrix

## Implementation

Run the verify pipeline:
```bash
python3 workflows/verify/run.py <review_number> [options]
```
