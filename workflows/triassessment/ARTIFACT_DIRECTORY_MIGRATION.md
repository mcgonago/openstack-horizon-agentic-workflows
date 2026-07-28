# Triassessment Artifact Directory Migration

## Problem Identified

**Date:** 2026-07-28  
**Issue:** Triassessment skill was overwriting artifacts across different ticket assessments

### Root Cause

The skill wrote all artifacts to a flat directory:
```
artifacts/triassessment/
├── triage_assessment.md      ← OVERWRITES every /triassessment call
├── related_tickets.md         ← OVERWRITES every /triassessment call
└── proposed_fixes.md          ← OVERWRITES every /triassessment call
```

**Consequences:**
- Every `/triassessment OSPRH-XXXXX` overwrote the previous ticket's work
- Unless git-committed after each assessment, previous analysis was lost
- Cross-contamination: OSPRH-28773 recheck files appeared in OSPRH-33457 runs
- No audit trail of individual ticket assessments in git history

## Solution

**Changed to per-ticket subdirectories:**
```
artifacts/triassessment/
├── TRIASSESSMENT-OSPRH-33457/
│   ├── triage_assessment.md
│   ├── related_tickets.md
│   └── proposed_fixes.md
├── TRIASSESSMENT-LP-2161292/
│   ├── triage_assessment.md
│   └── related_tickets.md
└── TRIASSESSMENT-OSPRH-28773/
    ├── triage_assessment.md
    └── related_tickets.md
```

**Benefits:**
- ✅ No overwrites across different ticket assessments
- ✅ Clean git history (each assessment is a separate directory)
- ✅ Easy archival/deployment (copy entire subdirectories)
- ✅ Matches dashboard's per-case investigation structure

## Changes Made

### 1. SKILL.md Updated

**File:** `.claude/skills/triassessment/SKILL.md`

**Changed paths:**
- Step 4.5: `artifacts/triassessment/proposed_fixes.md` → `artifacts/triassessment/{CASE_ID}/proposed_fixes.md`
- Step 5: `artifacts/triassessment/triage_assessment.md` → `artifacts/triassessment/{CASE_ID}/triage_assessment.md`
- Step 6: `artifacts/triassessment/related_tickets.md` → `artifacts/triassessment/{CASE_ID}/related_tickets.md`

**Changed ingestion call:**
```bash
# OLD:
--skill-type triassessment

# NEW:
--skill-type triassessment/<CASE_ID>
```

### 2. Output Documentation

Added directory structure diagram and explanation to SKILL.md Output section.

## Dashboard Status Audit

**Existing assessments preserved in dashboard:**

| Case ID | Runs | Notes |
|---------|------|-------|
| TRIASSESSMENT-OSPRH-27628 | 1 | Clean |
| TRIASSESSMENT-OSPRH-28773 | 3 | Run-003 has legitimate `*_recheck.md` files |
| TRIASSESSMENT-OSPRH-31340 | 2 | Clean |
| TRIASSESSMENT-OSPRH-31345 | 2 | Clean |
| TRIASSESSMENT-OSPRH-33457 | 3 | ❌ Runs 1-3 have OSPRH-28773 recheck files (cross-contamination) |
| TRIASSESSMENT-LP-2161292 | 3 | Clean Launchpad bug assessment |
| TRIASSESSMENT-GH-install_yamls-1158 | 1 | Clean GitHub issue assessment |

**Good news:** The dashboard has preserved all work in per-run directories.  
**Bad news:** Flat artifacts directory caused cross-contamination in OSPRH-33457.

## Migration Strategy

### For New Assessments (Going Forward)

Use the updated skill — it will automatically create per-ticket subdirectories.

**Example:**
```bash
/triassessment OSPRH-12345 --deep --update-artifact-dashboard
```

Will create:
- `artifacts/triassessment/TRIASSESSMENT-OSPRH-12345/triage_assessment.md`
- `artifacts/triassessment/TRIASSESSMENT-OSPRH-12345/related_tickets.md`

### For Existing Flat Artifacts

**Current state:**
```
artifacts/triassessment/
├── proposed_fixes.md          (OSPRH-33457, partially edited)
├── related_tickets.md         (OSPRH-28773, old)
├── related_tickets_recheck.md (OSPRH-28773)
├── triage_assessment.md       (OSPRH-33457, partially edited)
└── triage_assessment_recheck.md (OSPRH-28773)
```

**Options:**

1. **Clean slate (recommended):**
   ```bash
   # Remove all flat artifacts (work is preserved in dashboard)
   rm artifacts/triassessment/*.md
   
   # Re-run OSPRH-33457 with new structure
   /triassessment OSPRH-33457 --deep --generate-fix --update-artifact-dashboard
   ```

2. **Migrate manually:**
   ```bash
   mkdir -p artifacts/triassessment/TRIASSESSMENT-OSPRH-33457
   mv artifacts/triassessment/triage_assessment.md \
      artifacts/triassessment/TRIASSESSMENT-OSPRH-33457/
   # ... (incomplete, missing related_tickets and proposed_fixes for 33457)
   ```

**Recommendation:** Option 1 (clean slate) — the dashboard has the complete history.

## Deployment Checklist

Before deploying ioshaworkflow server:

- [x] Update SKILL.md to use per-ticket subdirectories
- [ ] Clean flat artifacts directory (remove `*.md` files)
- [ ] Re-run current assessment (OSPRH-33457) with new structure
- [ ] Verify dashboard ingestion works with new `--skill-type triassessment/<CASE_ID>` format
- [ ] Git commit the new per-ticket directories
- [ ] Deploy to server

## Recovery from Dashboard (If Needed)

All assessment history is preserved in the dashboard. To recover:

```bash
cd /home/omcgonag/Work/mymcp/workspace/iproject/projects/ioshaworkflow/repo/ioshaworkflow/data/investigations

# Example: recover OSPRH-28773 run-002
cp -r TRIASSESSMENT-OSPRH-28773/runs/run-002/*.md \
  ../../../openstack-horizon-agentic-workflows/workflows/triassessment/artifacts/triassessment/TRIASSESSMENT-OSPRH-28773/
```

---

**Generated:** 2026-07-28  
**Author:** AI (Claude)  
**Reviewed by:** (pending human review)
