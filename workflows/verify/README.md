# /verify — Horizon Review Verification Skill

Automated end-to-end functional verification of OpenStack Horizon Gerrit reviews using Python async Playwright.

## Usage

```bash
python3 run.py 992714 --execute --devstack 10.0.149.xxx
```

## Features

- 7-phase pipeline with JSON state resumability
- Before/after comparison (AngularJS vs Python panel)
- 31 Playwright tests across 7 groups (A-G)
- Auto-numbered screenshot evidence
- Parity matrix verification report
- Dashboard integration via workflow YAML

## First Target

Review 992714 — Switch default Key Pairs panel from AngularJS to Python
