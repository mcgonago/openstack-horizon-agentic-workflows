---
name: triassessment
description: Quick triage and assessment of Jira tickets with dependency mapping and recommendation
---

# Triage Assessment

Perform a quick triage and assessment of a Jira ticket, producing a
structured recommendation for stakeholder communication.

## Usage

/triassessment <TICKET-ID> [--update-artifact-dashboard] [--deep]

## Examples

/triassessment OSPRH-27628
/triassessment OSPRH-27628 --update-artifact-dashboard
/triassessment OSPRH-27628 --deep --update-artifact-dashboard

## Process

### Step 0: Parse Input

Extract the ticket ID from the arguments. Detect flags:
- `--update-artifact-dashboard` → set PUBLISH=true
- `--deep` → set DEEP=true

### Step 1: Fetch Ticket Details

Use the Jira MCP tool to fetch the ticket:
- Tool: `mcp__user-jiraMcp__jira_get_issue` with `issue_key = <TICKET-ID>`

Extract: summary, description, status, type, priority, labels, components,
fix versions, reporter, assignee, parent epic, linked tickets.

**Epic auto-detection:** If the ticket type is "Epic", set EPIC=true.
Epic mode changes Steps 2, 5, and 6 to produce an epic-level rollup
with a comprehensive children status table and Gerrit cross-reference.

### Step 2: Fetch Related Tickets

#### Non-Epic Mode (default)

For the parent epic and all linked tickets mentioned in the description,
fetch their details too using the same Jira MCP tool.

Build:
- Ticket hierarchy (epic → stories)
- Blocking chain (what blocks what)
- Cross-team dependencies

Cap at 10 related ticket fetches. Note truncation if more exist.

#### Epic Mode (EPIC=true)

Use JQL to fetch ALL children of the epic:
- Tool: `mcp__user-jiraMcp__jira_search_issues` with:
  - `jql = "parent = {TICKET-ID} OR 'Epic Link' = {TICKET-ID} ORDER BY created ASC"`
  - `max_results = 50`
- No cap — fetch all children for a complete rollup
- For each child, extract: key, summary, type, status, assignee,
  created date, updated date, description (first sentence only),
  linked tickets
- If any child's data is incomplete from the search result, fetch it
  individually with `mcp__user-jiraMcp__jira_get_issue`
- If the epic has a parent (strategy ticket), fetch that too

Build:
- Complete child ticket list with all metadata
- Blocking chain (what blocks what, including cross-epic dependencies)
- Status counts for the progress summary

### Step 2.5: Gerrit Cross-Reference (Epic Mode Only)

For each child ticket found in Step 2, search OpenDev Gerrit for associated
reviews. This step runs automatically in epic mode — no `--deep` flag required.

**Per-ticket search:**

```bash
curl -s "https://review.opendev.org/changes/?q=message:{CHILD-KEY}+project:openstack/horizon&o=CURRENT_REVISION&o=DETAILED_LABELS" | tail -n +2 | python3 -m json.tool
```

For each review found, extract:
- Review number and URL (`https://review.opendev.org/c/openstack/horizon/+/{number}`)
- Status: `status` field (NEW, MERGED, ABANDONED)
- WIP flag: `work_in_progress` field
- Current patchset: `revisions.{sha}._number`
- Verified vote: `labels.Verified.all[]`
- Code-Review votes: `labels.Code-Review.all[]`
- Topic: `topic` field

**Map to human-readable review status:**

| Gerrit State | Display |
|---|---|
| MERGED | **Merged** |
| ABANDONED | Abandoned |
| NEW + `work_in_progress=true` | WIP |
| NEW + Code-Review -1 or -2 | Needs Revision |
| NEW + Verified -1 | CI Failing |
| NEW + Code-Review +2 (×2) + Workflow +1 | Ready to Merge |
| NEW + Code-Review +2 | Approved (need +2×2) |
| NEW (no negative votes, no +2) | Under Review |
| No review found for ticket | — |

Apply the first matching row (most specific first). Evaluate in the order
shown — e.g., "Needs Revision" takes priority over "Under Review" if both
a -1 and no +2 are present.

**Topic-based cross-reference (optional):**

If the epic description or labels mention a Gerrit topic (e.g., `de-angularize`),
also search for topic-based reviews:

```bash
curl -s "https://review.opendev.org/changes/?q=topic:{topic}+project:openstack/horizon+status:open&o=CURRENT_REVISION&o=DETAILED_LABELS" | tail -n +2 | python3 -m json.tool
```

Cross-reference these with per-ticket results. If a topic-based review was NOT
found by the per-ticket message search, note it as an "unlinked review" in the
output — it may be missing a Jira key in its commit message.

If a child ticket has multiple Gerrit reviews, track all of them.

### Step 3: Cross-Reference Knowledge Bases

Scan the ticket description for keywords and load matching knowledge:

| Match | Knowledge Base |
|-------|---------------|
| PQC, quantum, TLS, kRSA, ML-KEM, post-quantum, cipher | `../../knowledge/feature-pqc.md` |
| Horizon, dashboard, panel, Angular, Django | `../../knowledge/horizon.md` |
| support, upgrade, regression, must-gather | `../../knowledge/support-investigation.md` |
| review, gerrit, comment, tracker | `../../knowledge/review-tracking.md` |

Read matching knowledge files before generating the assessment.

### Step 4: Deep Analysis (if --deep)

If DEEP=true, additionally:
- Search for related PRs on GitHub/OpenDev
- Identify code paths affected
- Map cross-team dependencies with contact info
- Check if existing PRs address this ticket

### Step 5: Generate Triage Assessment

Write `artifacts/triassessment/triage_assessment.md` with sections:

1. **Ticket Summary** — Key/value table of ticket fields
2. **Technical Context** — Plain language explanation of the ask
3. **Dependencies & Blockers** — Table of related tickets and their status
4. **Impact Analysis** — What happens if we proceed vs close
5. **Recommendation** — Verdict (CLOSE/IMPLEMENT/DEFER/ESCALATE), confidence, rationale
6. **Talking Points** — Bullet points for stakeholder response
7. **Deep Analysis** — (only if --deep) Extended code/PR references

#### Epic Rollup Sections (when EPIC=true)

When the ticket is an Epic, the triage_assessment.md ADDITIONALLY includes
the following sections (inserted after "Ticket Summary" and before
"Technical Context"):

**Epic Progress Summary:**

```markdown
## Epic Progress Summary

| Metric | Value |
|--------|-------|
| Total Children | {N} |
| Closed / Done | {N} ({percentage}%) |
| In Progress | {N} |
| Open / To Do | {N} |
| Blocked | {N} |
| With Active Gerrit Reviews | {N} |
| Gerrit Reviews Merged | {N} |
```

**Epic Children Status** — the primary at-a-glance table:

```markdown
## Epic Children Status

| Key | Summary | Type | Status | Assignee | Created | Updated | Review | Review Status |
|-----|---------|------|--------|----------|---------|---------|--------|---------------|
| [OSPRH-XXXXX](jira-url) | Short title (~60 chars) | Story | In Progress | Name | 2026-01-15 | 2026-07-10 | [986458](gerrit-url) | Under Review |
| [OSPRH-YYYYY](jira-url) | Short title | Story | Done | Name | 2026-02-01 | 2026-06-20 | [985123](gerrit-url) | **Merged** |
| [OSPRH-ZZZZZ](jira-url) | Short title | Task | To Do | Unassigned | 2026-03-10 | 2026-03-10 | — | — |
```

Column rules:
- **Key:** clickable Jira link — `[OSPRH-XXXXX](https://redhat.atlassian.net/browse/OSPRH-XXXXX)`
- **Summary:** first ~60 characters of the ticket summary
- **Type:** Story, Task, Sub-task, Bug, etc.
- **Status:** Jira status verbatim
- **Assignee:** Jira assignee display name, or "Unassigned" if empty
- **Created:** YYYY-MM-DD format
- **Updated:** YYYY-MM-DD format
- **Review:** clickable Gerrit link `[{number}](review-url)`, or "—" if none found
- **Review Status:** human-readable status from Step 2.5, or "—" if no review

If a child ticket has multiple Gerrit reviews, list each on a separate row
with the same ticket info repeated, or use comma-separated links if both
fit on one line.

**Blocked Items** (only if any children are blocked):

```markdown
## Blocked Items

| Ticket | Blocked By | Blocker Status | Path Forward |
|--------|-----------|----------------|--------------|
| [OSPRH-XXXXX](url) | [OSPRH-YYYYY](url) | In Progress | Wait for YYYYY to merge |
```

**Unlinked Reviews** (only if topic-based search found reviews not tied
to any child ticket):

```markdown
## Unlinked Reviews (topic: {topic})

These Gerrit reviews match the epic's topic but do not reference any child
ticket key in their commit message:

| Review | Subject | Status | Author |
|--------|---------|--------|--------|
| [{number}](gerrit-url) | Commit subject line | Under Review | Author Name |
```

Include a footer: `Generated: <timestamp> | Skill: /triassessment | Model: <model-id>`

**Auto-linkable references:** When citing knowledge files, use the format:
- `(per feature-pqc.md, Section 2)` — auto-links to GitHub knowledge file
- `(from horizon.md)` — auto-links without section
- Jira tickets (`OSPRH-12345`, `RHOSSTRAT-123`) — auto-link
- Patterns: `(per|from|see|via) <filename>.md[, Section N]`

### Step 6: Generate Related Tickets Summary

Write `artifacts/triassessment/related_tickets.md` with sections:

1. **Ticket Hierarchy** — Table: Level, Ticket, Title, Status, Assignee, Created, Updated
2. **Blocking Chain** — Visual representation of blocking relationships
3. **Cross-Team Dependencies** — Table: Dependency, Team, Status, Notes
4. **Resolution Paths** — For blocked tickets, list possible paths forward

### Step 7: Publish to Dashboard (if --update-artifact-dashboard)

If PUBLISH=true, inform the user to ingest artifacts:

```
Artifacts written to: artifacts/triassessment/
Case ID: TRIASSESSMENT-<TICKET-ID>

To ingest into dashboard:
cd /home/omcgonag/Work/mymcp/workspace/iproject/projects/ioshaworkflow/repo/ioshaworkflow
python scripts/ingest_artifacts.py \
  --case-id TRIASSESSMENT-<TICKET-ID> \
  --skill triassessment \
  --title "<ticket-summary>" \
  --summary "Triage assessment of <TICKET-ID>" \
  --source-dir ../openstack-horizon-agentic-workflows/workflows/triassessment/artifacts/triassessment/
```

Or use the dashboard "Ingest Artifacts" button at:
http://10.0.151.101:8072/investigations/TRIASSESSMENT-<TICKET-ID>

## Output

Files written to artifacts/triassessment/:

- triage_assessment.md — Structured assessment with recommendation
- related_tickets.md — Related ticket hierarchy and dependencies

## Knowledge Sources

Loaded conditionally based on ticket content:
- knowledge/feature-pqc.md — PQC compliance context
- knowledge/horizon.md — Horizon project reference
- knowledge/support-investigation.md — Support investigation patterns

## Rules

Follow the behavioral rules in rules.md within this workflow directory.
