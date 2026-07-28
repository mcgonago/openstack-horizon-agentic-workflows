# Triassessment Workflow

Quick triage and assessment of Jira tickets, Launchpad bugs, and Gerrit reviews.

## Usage

```bash
# Jira tickets
/triassessment <TICKET-ID> [--update-artifact-dashboard] [--deep] [--generate-fix]

# Launchpad bugs
/triassessment LP#<BUG-ID> [--update-artifact-dashboard] [--deep]

# Gerrit reviews
/triassessment <REVIEW-ID> --gerrit [--update-artifact-dashboard] [--deep] [--generate-fix]

# Gerrit review comparison (NEW!)
/triassessment <REVIEW-ID> --gerrit --compare <OTHER-REVIEW-ID> [--deep] [--update-artifact-dashboard]
```

**Flags:**
- `--gerrit` - Analyze a Gerrit review instead of a ticket
- `--compare <REVIEW-ID>` - Compare two Gerrit reviews side-by-side
- `--update-artifact-dashboard` - Publish artifacts to ioshaworkflow dashboard
- `--deep` - Perform deeper analysis with additional context
- `--generate-fix` - Generate concrete code fix proposals (requires `--deep`)

## What It Does

### Jira/Launchpad Mode

1. Fetches ticket/bug details and related tickets
2. Cross-references relevant knowledge bases
3. Generates a structured triage assessment with recommendation
4. Optionally publishes to the ioshaworkflow dashboard

### Gerrit Single Review Mode

1. Fetches review metadata, commit message, changed files, votes
2. Extracts and fetches Jira/Launchpad references from commit message
3. Discovers related reviews (Depends-On, same topic, same ticket)
4. Generates review assessment with recommendation
5. Optionally publishes to the ioshaworkflow dashboard

### Gerrit Comparison Mode (NEW!)

1. Fetches both reviews independently
2. Computes file overlap and line change differences
3. Analyzes approach differences
4. Generates side-by-side comparison with recommendation
5. Identifies which review (or both, or neither) should be merged

## Artifacts

### Jira/Launchpad Sources

| Artifact | Description |
|----------|-------------|
| `triage_assessment.md` | Context, dependencies, impact analysis, recommendation, talking points |
| `related_tickets.md` | Ticket hierarchy, blocking chains, cross-team dependencies |
| `proposed_fixes.md` | (with `--generate-fix`) Concrete code change proposals with diffs |

### Gerrit Single Review

| Artifact | Description |
|----------|-------------|
| `triage_assessment.md` | Review summary, Jira/LP cross-ref, changed files, recommendation |
| `related_reviews.md` | Related review network (Depends-On, same topic, same ticket) |
| `proposed_fixes.md` | (with `--generate-fix`) Code improvement proposals |

### Gerrit Comparison

| Artifact | Description |
|----------|-------------|
| `triage_assessment_primary.md` | Assessment of primary review |
| `triage_assessment_compare.md` | Assessment of comparison review |
| `comparison.md` | Side-by-side comparison with recommendation |
| `related_reviews.md` | Combined review network for both reviews |

## Dashboard

When published, artifacts appear at:

- Jira/LP: `http://10.0.151.101:8072/investigations/TRIASSESSMENT-<TICKET-ID>`
- Gerrit single: `http://10.0.151.101:8072/investigations/TRIASSESSMENT-<REVIEW-ID>`
- Gerrit comparison: `http://10.0.151.101:8072/investigations/TRIASSESSMENT-<REVIEW-A>-vs-<REVIEW-B>`

## Examples

```bash
# Assess a Jira ticket with deep analysis
/triassessment OSPRH-25872 --deep --update-artifact-dashboard

# Assess a Launchpad bug
/triassessment LP#2161292 --deep --update-artifact-dashboard

# Assess a Gerrit review
/triassessment 996428 --gerrit --deep --update-artifact-dashboard

# Compare two Gerrit reviews addressing the same issue
/triassessment 996428 --gerrit --compare 998960 --deep --update-artifact-dashboard

# Generate fix proposals for a ticket
/triassessment OSPRH-33457 --deep --generate-fix --update-artifact-dashboard
```

## Use Cases

### 1. Evaluate Alternative Implementations

When multiple reviews address the same ticket:

```bash
/triassessment 996428 --gerrit --compare 998960 --deep --update-artifact-dashboard
```

Output: Side-by-side comparison showing file overlap, line change magnitude, test coverage differences, and recommendation.

### 2. Quick Review Assessment

Before doing a deep `/horizon-code-review`:

```bash
/triassessment 996428 --gerrit --deep
```

Output: High-level summary of what the review does, what tickets it addresses, and related reviews.

### 3. Track Multi-Review Feature

For complex features split across multiple reviews:

```bash
/triassessment 996428 --gerrit --deep
```

Output: `related_reviews.md` shows Depends-On chain (merge order) and same-topic reviews (all patches).

## New in v2.0: Gerrit Support

See [GERRIT_FEATURE_SUMMARY.md](GERRIT_FEATURE_SUMMARY.md) for detailed documentation of Gerrit features, including:

- Review metadata extraction
- Jira/Launchpad cross-reference from commit messages
- Related review discovery
- Vote interpretation and status mapping
- Comparison mode with overlap analysis
