---
name: zuul-job
description: Analyze Zuul CI build failures for an OpenDev Gerrit review. Downloads logs, classifies errors using Horizon CI knowledge, and recommends fix vs recheck vs escalate.
argument-hint: "<change-number> [--patchset N] [--status-only]"
user-invocable: true
---

# Zuul Job Analyzer

Analyze Zuul CI build failures for an OpenDev Gerrit review, classify
errors, and recommend fix vs recheck vs escalate.

## Usage

```
/zuul-job <change-number>                    Analyze latest patchset
/zuul-job <change-number> --patchset N       Analyze specific patchset
/zuul-job <change-number> --status-only      Quick build status table
/zuul-job <gerrit-URL>                       Extract change from URL
```

## Examples

```
/zuul-job 992714
/zuul-job 992714 --patchset 11
/zuul-job 992714 --status-only
/zuul-job https://review.opendev.org/c/openstack/horizon/+/992714
```

## Persona

You are the `zuul-analyst` (see `agents/zuul-analyst.md`).
Follow the behavioral rules and output formats defined there.

## Knowledge Sources

**Required — read BEFORE classifying any failure:**
- `../../knowledge/zuul-horizon-ci.md` — Horizon CI job taxonomy, known
  flake patterns, error-to-category mapping, triage decision tree

**Supplementary:**
- `../../knowledge/horizon.md` — Shared Horizon project reference

## Process

### Step 0: Parse Input

Extract from the arguments:
- `change_number` (required): numeric Gerrit change number
- `--patchset N` (optional): specific patchset to analyze (default: latest)
- `--status-only` (optional): quick status check, no full analysis

If a full URL is provided, extract the change number:
- `https://review.opendev.org/c/openstack/horizon/+/992714` → `992714`
- `https://review.opendev.org/c/openstack/horizon/+/992714/2` → `992714`, patchset `2`

### Step 1: Detect Available Tools

Check if the `zuul-analyzer-agent` MCP tools are available:
- `find_zuul_errors` — full analysis with log download
- `get_build_status` — quick status check

If MCP tools are available → MODE: MCP (use MCP tools for data collection).
If MCP tools are not available → MODE: NATIVE (use curl/bash fallback — see Phase 2).

For Phase 1, MCP tools are required. If not available, inform the user:
"The zuul-analyzer-agent MCP server is not connected. Please connect it
and retry, or wait for Phase 2 which adds native fallback."

### Step 2: Fetch Build Status

Get the current build status for the review:

**MCP MODE:**
```
Use get_build_status(change_number=<N>, patchset=<P>)
```

Parse the result to identify:
- Total number of builds
- Number succeeded
- Number failed (separate voting vs non-voting)
- Buildset UUID for reference

**EARLY EXIT:** If all jobs passed → report "All jobs passed for review
`<N>` patchset `<P>`. No failures to analyze." and STOP.

**--status-only EXIT:** If `--status-only` was specified, present the
build status table and STOP. Do not download logs or generate artifacts.

### Step 3: Download and Analyze Failure Logs

For each FAILED job, download and analyze the logs:

**MCP MODE:**
```
Use find_zuul_errors(
  change_number=<N>,
  patchset=<P>,
  output_dir=<artifacts-dir>
)
```

The MCP tool will:
- Download `job-output.txt` for each failed job
- Extract error patterns (flake8 codes, pytest failures, infra errors)
- Save build metadata and artifacts
- Generate a preliminary `report.md`

### Step 4: Classify Failures Using Knowledge File

**READ** `../../knowledge/zuul-horizon-ci.md` now.

For each failed job:

1. Check Section 3 (Error Pattern → Category Mapping) for exact matches
2. If a pattern matches → use the listed category
3. If ambiguous (e.g., NoSuchElementException) → check Section 2 decision rules:
   - Did our patch change the file/template the test exercises? → CODE-REGRESSION
   - Did our patch NOT change the relevant code? → INFRA-FLAKE
4. For non-voting jobs (e.g., py314) → classify but note as non-voting
5. Apply Section 4 (Triage Decision Tree) to determine overall verdict

### Step 5: Generate Report Artifact

Write `artifacts/zuul-job/report.md` following the format in the
`zuul-analyst` persona (agents/zuul-analyst.md).

Required sections:
- Summary table (total builds, succeeded, failed voting, failed non-voting)
- Buildset context (URL, pipeline, result)
- Observations, conclusions, suggestions (synthesis section)
- Per-job sections (classification, errors table, evidence)
- Local verification commands

All references MUST be clickable markdown links (RULE-0007/0008).

### Step 6: Generate Triage Artifact

Write `artifacts/zuul-job/triage.md` following the format in the
`zuul-analyst` persona.

Required sections:
- Verdict banner (FIX / RECHECK / ESCALATE / PASS)
- Per-job classification table
- Recommended next steps (numbered, actionable, with commands)

### Step 7: Present Summary

Show the user:
1. **1-line verdict:** "VERDICT: FIX" or "VERDICT: RECHECK" etc.
2. **Failed jobs table:** job name, classification, voting status
3. **Artifact locations:** paths to report.md and triage.md
4. **Next action:** suggested command to run

Example:
```
VERDICT: FIX

| Job | Classification | Voting |
|-----|---------------|--------|
| horizon-integration-pytest | CODE-REGRESSION | YES |
| openstack-tox-py314 | SKIP | NO |

Artifacts:
  report.md → artifacts/zuul-job/report.md
  triage.md → artifacts/zuul-job/triage.md

Suggested next action:
  tox -e integration -- test_keypairs -v
```

## Output

Files written to `artifacts/zuul-job/`:
- `report.md` — Full build failure analysis
- `triage.md` — Quick verdict with recommendations

## Rules

Follow the behavioral rules in `rules.md` within this workflow directory.
