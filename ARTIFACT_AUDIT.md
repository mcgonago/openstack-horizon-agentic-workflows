# Artifact Directory Audit - All Workflows

**Date:** 2026-07-28  
**Purpose:** Identify which workflows have flat artifact directories that need migration

## Summary

**Total workflows with skills:** 5  
**Workflows using per-case subdirectories:** 1 (verify) + 1 (triassessment, just fixed)  
**Workflows needing migration:** 1 (support-case)  
**Workflows with no existing cases:** 2 (feature, horizon-review)

## Detailed Audit

### ✅ verify - CORRECT (Already Per-Case)

**Structure:**
```
workflows/verify/artifacts/
├── verify-986458/
│   ├── verify_report.md
│   └── manual_testing_guide.md
├── verify-986478/
└── verify-992714/
```

**Dashboard cases:** (none found - verify may use REVIEW- prefix)

**Status:** ✅ Already using per-case subdirectories - no migration needed

**Note:** .gitignore has exception: `!workflows/verify/artifacts/`

---

### ✅ triassessment - FIXED

**Old structure (BROKEN):**
```
workflows/triassessment/artifacts/triassessment/
├── triage_assessment.md      ← OVERWRITES
├── related_tickets.md         ← OVERWRITES
└── proposed_fixes.md          ← OVERWRITES
```

**New structure (FIXED):**
```
workflows/triassessment/artifacts/triassessment/
├── TRIASSESSMENT-OSPRH-33457/
│   ├── triage_assessment.md
│   ├── related_tickets.md
│   └── proposed_fixes.md
├── TRIASSESSMENT-LP-2161292/
└── ... (7 cases total)
```

**Dashboard cases:** 7 (OSPRH-27628, OSPRH-28773, OSPRH-31340, OSPRH-31345, OSPRH-33457, LP-2161292, GH-install_yamls-1158)

**Status:** ✅ Migrated on 2026-07-28 (commit: 43afde8)

**SKILL.md:** ✅ Updated to use `artifacts/triassessment/{CASE_ID}/`

**Backfill:** ✅ Complete - all 7 cases restored from dashboard runs

---

### ⚠️ support-case - NEEDS MIGRATION

**Current structure (BROKEN):**
```
workflows/support-case/artifacts/support-case/
├── investigation_report.md   ← OVERWRITES
├── customer_response.md      ← OVERWRITES
└── code_trace.md             ← OVERWRITES
```

**Dashboard cases:** 1 (SUPPORT-04426889 with 3 runs)

**Problem:** If a second support case is opened, these files will be overwritten

**Risk:** LOW (only 1 case exists, but problem will occur on next case)

**Recommended structure:**
```
workflows/support-case/artifacts/support-case/
├── SUPPORT-04426889/
│   ├── investigation_report.md
│   ├── customer_response.md
│   └── code_trace.md
└── SUPPORT-XXXXXX/  (future cases)
```

**Required changes:**
1. Update SKILL.md to write to `artifacts/support-case/{CASE_ID}/`
2. Update ingestion call to use `--skill-type support-case/<CASE_ID>`
3. Backfill SUPPORT-04426889 from dashboard run-003
4. Add .gitignore exception: `!workflows/support-case/artifacts/`

**Backfill command:**
```bash
mkdir -p workflows/support-case/artifacts/support-case/SUPPORT-04426889
cp ioshaworkflow/data/investigations/SUPPORT-04426889/runs/run-003/*.md \
   workflows/support-case/artifacts/support-case/SUPPORT-04426889/
# (exclude what_ai_did.md)
```

---

### ℹ️ feature - NO EXISTING CASES

**Current structure:**
```
workflows/feature/artifacts/  (empty)
```

**Dashboard cases:** 1 (FEATURE-OSPRH-28889)

**Status:** No flat artifacts currently exist, but SKILL.md should be checked

**Action:** Review SKILL.md and update to per-case structure BEFORE first usage

---

### ℹ️ horizon-review - NO EXISTING CASES

**Current structure:**
```
workflows/horizon-review/  (no artifacts directory)
```

**Dashboard cases:** 0

**Status:** Skill may not produce artifacts, or hasn't been used yet

**Action:** Review SKILL.md to determine if artifacts are produced

---

## .gitignore Status

**Root .gitignore:**
```gitignore
# Review and analysis artifacts — generated output, not source
artifacts/
# But keep verify and triassessment artifacts
!workflows/verify/artifacts/
!workflows/triassessment/artifacts/  ← Added 2026-07-28
```

**Missing exceptions:**
- `!workflows/support-case/artifacts/` (needed if we migrate)
- `!workflows/feature/artifacts/` (needed if skill produces artifacts)

## Dashboard Data Audit

**All investigation types in ioshaworkflow/data/investigations/:**

| Type | Count | Example Cases |
|------|-------|---------------|
| TRIASSESSMENT | 7 | OSPRH-33457, LP-2161292, GH-install_yamls-1158 |
| REVIEW | 7 | REVIEW-977939, REVIEW-TRACKER-986458 |
| ZUUL | 2 | ZUUL-JOB-986478, ZUUL-JOB-992714 |
| SUPPORT | 1 | SUPPORT-04426889 |
| FEATURE | 1 | FEATURE-OSPRH-28889 |

**Total:** 18 cases

**Git status:** All committed except TRIASSESSMENT-OSPRH-33457 run-002/003 (just committed)

## Recommendations

### Immediate (Before Deployment)

1. ✅ triassessment - Already migrated
2. ⚠️ support-case - Migrate if time permits (LOW risk - only 1 case exists)
3. ℹ️ feature - Update SKILL.md before first usage

### Post-Deployment

1. Establish convention: ALL new skills MUST use per-case subdirectories
2. Add to skill template: `artifacts/{skill-name}/{CASE_ID}/`
3. Update CLAUDE.md with artifact directory standards
4. Create skill scaffold generator that enforces correct structure

## Migration Priority

**Priority 1 (CRITICAL):** None - triassessment already fixed

**Priority 2 (MEDIUM):** support-case
- Risk: Will overwrite on next case
- Effort: ~15 minutes (same process as triassessment)
- Data at risk: 1 case with 3 runs (preserved in dashboard)

**Priority 3 (LOW):** feature, horizon-review
- Risk: No cases exist yet
- Effort: Update SKILL.md only
- Data at risk: None

## Decision

**For today's deployment:**
- ✅ triassessment is ready
- ⚠️ support-case can be deployed as-is (flat artifacts) with note to migrate on next case
- ℹ️ Other workflows have no data at risk

**Recommend:** Deploy as-is, migrate support-case in next session

---

**Generated:** 2026-07-28  
**Author:** AI audit  
**Related:** ARTIFACT_DIRECTORY_MIGRATION.md (triassessment-specific)
