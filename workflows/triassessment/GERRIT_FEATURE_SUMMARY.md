# Gerrit Source Support for /triassessment

## Overview

The `/triassessment` skill now supports analyzing OpenDev Gerrit reviews in addition to Jira tickets and Launchpad bugs. This enables:

1. **Single review assessment** - Analyze one Gerrit review in depth
2. **Review comparison** - Side-by-side comparison of two reviews (e.g., alternative implementations)
3. **Jira/Launchpad cross-reference** - Auto-extract and fetch tickets referenced in commit messages
4. **Related review discovery** - Find reviews in the same topic, Depends-On chain, or addressing the same ticket

## Usage Examples

### Single Review Assessment

```bash
# By review number with --gerrit flag
/triassessment 996428 --gerrit --deep --update-artifact-dashboard

# By full Gerrit URL (auto-detects as Gerrit)
/triassessment https://review.opendev.org/c/openstack/horizon/+/996428 --deep

# With fix proposals
/triassessment 996428 --gerrit --deep --generate-fix --update-artifact-dashboard
```

### Review Comparison

```bash
# Compare two reviews addressing the same issue
/triassessment 996428 --gerrit --compare 998960 --deep --update-artifact-dashboard

# With full URLs
/triassessment https://review.opendev.org/c/openstack/horizon/+/996428 --compare 998960 --deep
```

## What Gets Analyzed

### Step 1-G: Review Metadata Fetch

- Review number, subject, project, branch, status
- Owner information (name, email, username)
- Patchset information (current revision, number)
- Full commit message including footers
- Changed files with line counts
- Code-Review, Verified, Workflow votes
- Comment thread

### Step 2-G: Related Reviews & Cross-References

**Jira Cross-Reference:**
- Extracts Jira ticket keys from commit message
- Fetches full ticket details via Jira MCP
- Shows ticket summary, status, type, assignee

**Launchpad Cross-Reference:**
- Extracts `Closes-Bug`, `Partial-Bug`, `Related-Bug` references
- Fetches bug details via Launchpad API
- Shows bug title, status, importance per project

**Related Reviews:**
- **Depends-On chain** - Reviews that must merge first
- **Same topic** - Other reviews in the same Gerrit topic
- **Same Jira ticket** - Alternative implementations or related patches

### Step 5-G: Assessment Output

**Single Review:**
- `triage_assessment.md` - Review summary, analysis, recommendation
- `related_reviews.md` - Related review network

**Comparison Mode:**
- `triage_assessment_primary.md` - Assessment of primary review
- `triage_assessment_compare.md` - Assessment of comparison review
- `comparison.md` - Side-by-side comparison with recommendation
- `related_reviews.md` - Combined review network

## Output Structure

### Review Summary Table

```markdown
| Field | Value |
|-------|-------|
| Review | [996428](https://review.opendev.org/c/openstack/horizon/+/996428) |
| Subject | Add RoleName to IdentityAPIAccessControlsTestCase |
| Project | openstack/horizon |
| Branch | master |
| Status | Under Review |
| Topic | OSPRH-25872 |
| Owner | John Doe (jdoe) |
| Created | 2026-07-15 14:32 |
| Updated | 2026-07-28 09:15 |
| Patchset | #3 |
| Files Changed | 2 files (+15/-5 lines) |
| Code-Review | +1 (×2) |
| Verified | +1 (Zuul) |
| Workflow | -- |
```

### Comparison Summary Table

```markdown
| Aspect | Review 996428 | Review 998960 |
|--------|---------------|---------------|
| Subject | Add RoleName to tests | Expand scope coverage |
| Status | Under Review | Under Review |
| Owner | John Doe | Jane Smith |
| Files Changed | 2 files | 3 files |
| Lines Changed | +15/-5 | +45/-12 |
| Code-Review | +1 (×2) | +2 (×1) |
| Test Coverage | Partial | Yes |
```

### Overlap Analysis

```markdown
## Overlap Analysis

**Common Files Modified:**

| File | Review 996428 | Review 998960 |
|------|---------------|---------------|
| openstack_dashboard/test/identity_tests.py | +10/-3 | +15/-5 |

**Unique to Review 996428:**
- openstack_dashboard/dashboards/identity/policy/tests.py (+5/-2)

**Unique to Review 998960:**
- openstack_dashboard/static/app/core/policy.service.js (+20/-5)
- openstack_dashboard/test/integration/test_policy.py (+10/-2)
```

## Status Mapping

Reviews are mapped to human-readable status:

| Gerrit State | Display |
|---|---|
| MERGED | **Merged** |
| ABANDONED | Abandoned |
| NEW + work_in_progress=true | WIP |
| NEW + Code-Review -1 or -2 | Needs Revision |
| NEW + Verified -1 | CI Failing |
| NEW + Code-Review +2 (×2) + Workflow +1 | Ready to Merge |
| NEW + Code-Review +2 | Approved (need +2×2) |
| NEW (clean) | Under Review |

## Case ID Format

- Single review: `TRIASSESSMENT-996428`
- Comparison: `TRIASSESSMENT-996428-vs-998960`

## Dashboard Publishing

When using `--update-artifact-dashboard`, artifacts are ingested into the ioshaworkflow dashboard:

```bash
# Title format for single review
"Review 996428: Add RoleName to IdentityAPIAccessControlsTestCase"

# Title format for comparison
"Compare reviews 996428 vs 998960: OSPRH-25872 fix approaches"

# Summary format
"Review assessment of 996428: Adds RoleName validation to identity API access control tests"

# Dashboard URL
http://10.0.151.101:8072/investigations/TRIASSESSMENT-996428?run=run-001
```

## Use Cases

### 1. Evaluate Alternative Implementations

When multiple reviews address the same ticket (e.g., OSPRH-25872), compare them:

```bash
/triassessment 996428 --gerrit --compare 998960 --deep --update-artifact-dashboard
```

**Output:** Side-by-side comparison highlighting:
- File overlap (which files does each modify?)
- Line change magnitude (how big is each approach?)
- Test coverage differences
- Implementation strategy differences
- Recommendation on which to merge or combine

### 2. Assess Review Before Code Review

Before doing a deep `/horizon-code-review`, get a high-level assessment:

```bash
/triassessment 996428 --gerrit --deep
```

**Output:** Review summary with:
- What does this review do? (Technical Context)
- What tickets does it address? (Jira/LP cross-reference)
- What other reviews is it related to? (Related Reviews)
- Is it ready to merge? (Status + Recommendation)

### 3. Track Related Review Network

For a complex feature split across multiple reviews:

```bash
/triassessment 996428 --gerrit --deep
```

**Output:** `related_reviews.md` with:
- Depends-On chain (merge order)
- Same topic reviews (all patches in this feature)
- Alternative implementations (reviews for the same ticket)

### 4. Cross-Reference Jira Ticket Progress

When a Jira ticket references multiple Gerrit reviews, assess each:

```bash
/triassessment OSPRH-25872 --deep
/triassessment 996428 --gerrit --deep
/triassessment 998960 --gerrit --deep
```

Compare ticket-level assessment (Step 1) with review-level assessments (Step 2, 3).

## Knowledge Loading

For Gerrit sources, the skill always loads:
- `../../knowledge/horizon.md` (Horizon architecture, conventions)

Plus conditionally based on commit message/files:
- `../../knowledge/feature-pqc.md` (if PQC/TLS/crypto keywords)
- `../../knowledge/support-investigation.md` (if upgrade/regression keywords)
- `../../knowledge/review-tracking.md` (always for Gerrit)

## Rules

All existing rules apply, plus:

**Rule 9: GERRIT VOTE INTERPRETATION**
- Never report raw vote JSON
- Apply status mapping in order (most specific first)
- Include vote counts: "Code-Review: +2 (×2), +1 (×1)"
- Distinguish CI vs human: "Verified: +1 (Zuul)" vs "Verified: +1 (username)"

**Rule 6: INQUIRY TYPE DETECTION**
- Gerrit reviews DO NOT generate `related_tickets.md` unless Jira tickets are in commit message
- Gerrit comparisons DO NOT generate `related_tickets.md` unless Jira tickets are shared

## Implementation Notes

- Gerrit REST API is publicly accessible (no auth needed)
- All Gerrit JSON responses start with `)]}` XSSI protection - use `tail -n +2`
- Review status is derived from labels, not raw `status` field
- Comparison mode fetches both reviews independently, then computes overlap
- Related review discovery is capped at 20 total fetches
- Jira cross-reference is capped at 5 tickets per review

## Next Steps

After running `/triassessment --gerrit`:

1. **Read the assessment** - Check recommendation and review points
2. **Investigate alternatives** - If "Same Jira Ticket" found, compare approaches
3. **Deep code review** - Use `/horizon-code-review` for detailed analysis
4. **Create verification lab** - Use `/imock` to test the change interactively

## Example Workflow: OSPRH-25872

```bash
# 1. Assess the ticket
/triassessment OSPRH-25872 --deep --update-artifact-dashboard

# 2. Discover related reviews from ticket assessment
# (Step 2.5 Gerrit cross-reference shows 996428 and 998960)

# 3. Compare the two reviews
/triassessment 996428 --gerrit --compare 998960 --deep --update-artifact-dashboard

# 4. Read comparison.md to decide which approach to use

# 5. Deep review of chosen approach
/horizon-code-review 998960

# 6. Create verification lab
/imock assessment=TRIASSESSMENT-OSPRH-25872 review=998960 clone=horizon-osprh-25872 --update-artifact-dashboard
```

**Dashboard outputs:**
- `TRIASSESSMENT-OSPRH-25872/` - Ticket assessment
- `TRIASSESSMENT-996428-vs-998960/` - Review comparison
- `TRIASSESSMENT-OSPRH-25872/` - Verification lab (from /imock)

All accessible at: `http://10.0.151.101:8072/investigations/`
