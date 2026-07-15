# Verify Skill

End-to-end Horizon Gerrit review verification using Playwright.

## Quick Start
```bash
python3 run.py <review_number> --execute --devstack <HOST>
```

## Architecture
7-phase pipeline: Context → Environment → Deploy Before → Test Before → Deploy After → Test After → Report

## Key Files
- `run.py` — CLI entry, phase orchestration
- `context.py` — Gerrit API, recipe matching
- `environment.py` — DevStack SSH, preflight
- `deploy.py` — Clone, configure, tox
- `test_runner.py` — Playwright test dispatch
- `report.py` — Verdict, parity matrix, markdown report
- `recipes/keypairs/` — Key Pairs panel test groups A-G
