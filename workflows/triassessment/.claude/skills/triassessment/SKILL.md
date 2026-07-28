---
name: triassessment
description: Quick triage and assessment of Jira tickets, Launchpad bugs, and Gerrit reviews with dependency mapping, comparison, and recommendation
---

# Triage Assessment

Perform a quick triage and assessment of a ticket, bug, or code review,
producing a structured recommendation for stakeholder communication.

Supports three sources:
- **Jira** (OSPRH, RHOSSTRAT, etc.) -- via Jira MCP tool
- **Launchpad** (LP#NNNNNNN) -- via public REST API
- **Gerrit** (review.opendev.org) -- via Gerrit REST API

## Usage

/triassessment <TICKET-ID|REVIEW-ID> [--gerrit] [--compare REVIEW-ID] [--update-artifact-dashboard] [--deep] [--generate-fix]

## Examples

```
# Jira tickets (existing)
/triassessment OSPRH-27628
/triassessment OSPRH-27628 --update-artifact-dashboard
/triassessment OSPRH-27628 --deep --update-artifact-dashboard

# Launchpad bugs (new)
/triassessment LP#2161292
/triassessment lp:2161292
/triassessment 2161292
/triassessment https://bugs.launchpad.net/oslo.policy/+bug/2161292
/triassessment LP#2161292 --deep --update-artifact-dashboard

# With code fix proposals (requires --deep)
/triassessment OSPRH-33457 --deep --generate-fix --update-artifact-dashboard

# Gerrit reviews (new)
/triassessment 996428 --gerrit
/triassessment 996428 --gerrit --deep --update-artifact-dashboard
/triassessment https://review.opendev.org/c/openstack/horizon/+/996428
/triassessment 996428 --gerrit --deep --generate-fix --update-artifact-dashboard

# Gerrit review comparison (new)
/triassessment 996428 --gerrit --compare 998960 --deep --update-artifact-dashboard
```

## Process

### Step 0: Parse Input

Extract the ticket ID from the arguments. Detect flags:
- `--update-artifact-dashboard` -> set PUBLISH=true
- `--deep` -> set DEEP=true
- `--generate-fix` -> set GENERATE_FIX=true (requires DEEP=true)
- `--gerrit` -> set IS_GERRIT=true
- `--compare <REVIEW-ID>` -> set COMPARE_MODE=true, COMPARE_REVIEW=<REVIEW-ID>

**Source detection** -- determine where to fetch the ticket from:

1. If input contains `review.opendev.org/c/`:
   - SOURCE=gerrit
   - Extract review number from URL (last numeric segment after `/+/`)
2. If input is numeric AND `--gerrit` flag is present:
   - SOURCE=gerrit
   - REVIEW_NUMBER = input as-is
3. If `--compare` flag is present:
   - SOURCE=gerrit_compare
   - PRIMARY_REVIEW = main input (must be numeric or gerrit URL)
   - COMPARE_REVIEW = value of --compare flag
4. If input contains `bugs.launchpad.net`:
   - SOURCE=launchpad
   - Extract bug ID from URL path (last numeric segment after `+bug/`)
5. If input starts with `LP#` or `lp:` (case-insensitive):
   - SOURCE=launchpad
   - TICKET_ID = numeric part after prefix
6. If input matches `[A-Z]+-[0-9]+` (e.g., OSPRH-27628):
   - SOURCE=jira
   - TICKET_ID = full match (existing behavior)
7. If input is pure numeric (6-8 digits) and no `--gerrit` flag:
   - SOURCE=launchpad
   - TICKET_ID = input as-is
8. Otherwise: error -- unrecognized format

Set CASE_ID based on source:
- jira: `TRIASSESSMENT-{TICKET_ID}` (e.g., TRIASSESSMENT-OSPRH-27628)
- launchpad: `TRIASSESSMENT-LP-{TICKET_ID}` (e.g., TRIASSESSMENT-LP-2161292)
- gerrit: `TRIASSESSMENT-{REVIEW_NUMBER}` (e.g., TRIASSESSMENT-996428)
- gerrit_compare: `TRIASSESSMENT-{PRIMARY_REVIEW}-vs-{COMPARE_REVIEW}` (e.g., TRIASSESSMENT-996428-vs-998960)

If SOURCE=jira, continue to Step 1. If SOURCE=launchpad, skip to Step 1-LP. If SOURCE=gerrit or gerrit_compare, skip to Step 1-G.

### Step 1: Fetch Ticket Details (Jira)

Use the Jira MCP tool to fetch the ticket:
- Tool: `mcp__user-jiraMcp__jira_get_issue` with `issue_key = <TICKET-ID>`

Extract: summary, description, status, type, priority, labels, components,
fix versions, reporter, assignee, parent epic, linked tickets.

**Epic auto-detection:** If the ticket type is "Epic", set EPIC=true.
Epic mode changes Steps 2, 5, and 6 to produce an epic-level rollup
with a comprehensive children status table and Gerrit cross-reference.

After Step 1, continue to Step 2.

### Step 1-LP: Fetch Launchpad Bug Details (when SOURCE=launchpad)

Fetch the bug metadata, tasks, and messages using curl against the
Launchpad REST API. No authentication is required for public bugs.

**1-LP.a: Bug metadata**

```bash
curl -s "https://api.launchpad.net/devel/bugs/{TICKET_ID}" \
  -H "Accept: application/json"
```

Extract:
- title, description, date_created, date_last_updated
- owner_link (parse username from URL: last path segment after `~`)
- tags (array), security_related (boolean)
- heat, message_count
- duplicate_of_link (if not null, note the duplicate)

**1-LP.b: Bug tasks (per-project status)**

```bash
curl -s "https://api.launchpad.net/devel/bugs/{TICKET_ID}/bug_tasks" \
  -H "Accept: application/json"
```

For each entry in the `entries` array, extract:
- bug_target_name (project name, e.g., "horizon", "oslo.policy")
- status (New, Confirmed, In Progress, Fix Committed, Fix Released, etc.)
- importance (Undecided, Wishlist, Low, Medium, High, Critical)
- assignee_link (parse username, or "Unassigned" if null)
- milestone_link (parse milestone name, or "--" if null)
- date_created, date_fix_committed, date_fix_released

Build the **Affected Projects** table from this data. This is a key
difference from Jira: Launchpad bugs can affect multiple projects, each
with independent status and importance.

**1-LP.c: Messages (comments)**

```bash
curl -s "https://api.launchpad.net/devel/bugs/{TICKET_ID}/messages" \
  -H "Accept: application/json"
```

For each entry in `entries`:
- owner_link (parse username after `~`)
- date_created
- subject
- content (full message body)

Build the **Comment Timeline** table. Also scan each message body for:
- `review.opendev.org` URLs -> extract review numbers for Gerrit cross-ref
- `git.openstack.org` or `opendev.org/` URLs -> note linked repos
- Commit SHAs (40-char hex strings) -> note for reference

**1-LP.d: Gerrit cross-reference (from parsed URLs)**

For each `review.opendev.org` URL found in comments:

```bash
curl -s "https://review.opendev.org/changes/{review_number}?o=CURRENT_REVISION&o=DETAILED_LABELS" \
  | tail -n +2 | python3 -m json.tool
```

Extract: status, subject, owner.name, current patchset,
Code-Review/Verified labels. Map to human-readable review status using
the same mapping table from Step 2.5.

After Step 1-LP, continue to Step 2-LP.

### Step 1-G: Fetch Gerrit Review Details (when SOURCE=gerrit or gerrit_compare)

Fetch the review metadata, commit message, changed files, and comments using
curl against the Gerrit REST API. All OpenDev Gerrit data is publicly accessible.

**1-G.a: Review metadata**

```bash
curl -s "https://review.opendev.org/changes/{REVIEW_NUMBER}?o=CURRENT_REVISION&o=DETAILED_LABELS&o=ALL_COMMITS&o=ALL_FILES&o=MESSAGES&o=DETAILED_ACCOUNTS" \
  | tail -n +2 | python3 -m json.tool
```

The `tail -n +2` removes Gerrit's XSSI protection prefix `)]}` from the response.

Extract:
- **Review metadata:** `_number`, `subject`, `project`, `branch`, `status`, `topic`, `created`, `updated`
- **Owner:** `owner.name`, `owner.email`, `owner.username`
- **Change-Id:** `change_id`
- **Current revision:** `current_revision` (SHA), `revisions.{sha}._number` (patchset number)
- **Commit message:** `revisions.{current_revision}.commit.message` (full message including footers)
- **Changed files:** `revisions.{current_revision}.files` (dict with filenames as keys, insertions/deletions as values)
- **Labels:** `labels.Code-Review.all[]`, `labels.Verified.all[]`, `labels.Workflow.all[]`
- **Messages:** `messages[]` (comment thread with author, timestamp, message text)
- **Related changes:** `revisions.{current_revision}.commit.parents[]` (parent commits)

**1-G.b: Parse commit message**

Extract from the commit message footer:
- **Jira references:** Any `OSPRH-XXXXX`, `RHOSSTRAT-XXX` pattern
- **Launchpad bugs:** `Closes-Bug: #NNNNN`, `Partial-Bug: #NNNNN`, `Related-Bug: #NNNNN`
- **Depends-On:** Gerrit review dependencies (Change-Id references)
- **Change-Id:** Unique change identifier

**1-G.c: Build changed files table**

For each file in `revisions.{current_revision}.files`:
- Filename
- Status: `ADDED`, `MODIFIED`, `DELETED`, `RENAMED`
- Lines added: `lines_inserted`
- Lines deleted: `lines_deleted`
- File size delta: `size_delta`

Calculate totals:
- Total files changed
- Total lines added (sum of `lines_inserted`)
- Total lines deleted (sum of `lines_deleted`)

**1-G.d: Map review status to human-readable**

Use the same mapping table from Step 2.5:

| Gerrit State | Display |
|---|---|
| MERGED | **Merged** |
| ABANDONED | Abandoned |
| NEW + `work_in_progress=true` | WIP |
| NEW + Code-Review -1 or -2 | Needs Revision |
| NEW + Verified -1 | CI Failing |
| NEW + Code-Review +2 (x2) + Workflow +1 | Ready to Merge |
| NEW + Code-Review +2 | Approved (need +2x2) |
| NEW (no negative votes, no +2) | Under Review |

**1-G.e: If COMPARE_MODE=true, fetch COMPARE_REVIEW**

Repeat steps 1-G.a through 1-G.d for COMPARE_REVIEW. Store both review
datasets separately for side-by-side comparison in Step 5-G-compare.

After Step 1-G, continue to Step 2-G.

### Step 2: Fetch Related Tickets

#### Non-Epic Mode (default)

For the parent epic and all linked tickets mentioned in the description,
fetch their details too using the same Jira MCP tool.

Build:
- Ticket hierarchy (epic -> stories)
- Blocking chain (what blocks what)
- Cross-team dependencies

Cap at 10 related ticket fetches. Note truncation if more exist.

#### Epic Mode (EPIC=true)

Use JQL to fetch ALL children of the epic:
- Tool: `mcp__user-jiraMcp__jira_search_issues` with:
  - `jql = "parent = {TICKET-ID} OR 'Epic Link' = {TICKET-ID} ORDER BY created ASC"`
  - `max_results = 50`
- No cap -- fetch all children for a complete rollup
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

### Step 2-LP: Fetch Related Bugs (when SOURCE=launchpad)

**Duplicates:**

```bash
curl -s "https://api.launchpad.net/devel/bugs/{TICKET_ID}/duplicates" \
  -H "Accept: application/json"
```

If entries exist, note each duplicate bug ID and title.

**Linked merge proposals:**

```bash
curl -s "https://api.launchpad.net/devel/bugs/{TICKET_ID}/linked_merge_proposals" \
  -H "Accept: application/json"
```

If entries exist, note each MP URL and status.

**Cross-project awareness:**

The bug_tasks from Step 1-LP.b already contain per-project status.
Use this to build the Dependencies section -- each affected project
is treated as a "related entity" with independent status tracking.

Cap at 10 related bug fetches. Note truncation if more exist.

After Step 2-LP, continue to Step 3 (knowledge cross-reference works
for both sources).

### Step 2-G: Fetch Related Reviews and Jira Cross-Reference (when SOURCE=gerrit or gerrit_compare)

**2-G.a: Jira cross-reference**

For each Jira ticket key extracted from the commit message in Step 1-G.b,
fetch the ticket details using the Jira MCP tool:
- Tool: `mcp__user-jiraMcp__jira_get_issue` with `issue_key = <TICKET-ID>`

Extract: summary, description, status, type, priority, assignee.

Build the **Jira Cross-Reference** table. This answers "what ticket(s)
does this review address?"

Cap at 5 Jira ticket fetches per review. Note truncation if more exist.

**2-G.b: Launchpad cross-reference**

For each Launchpad bug ID extracted from the commit message in Step 1-G.b,
fetch the bug details using the Launchpad REST API (same as Step 1-LP.a):

```bash
curl -s "https://api.launchpad.net/devel/bugs/{BUG_ID}" \
  -H "Accept: application/json"
```

Extract: title, status (from bug_tasks for the relevant project).

Build the **Launchpad Cross-Reference** table if any bugs are referenced.

**2-G.c: Related reviews (Depends-On chain)**

For each Depends-On Change-Id found in the commit message, search Gerrit
for the dependent review:

```bash
curl -s "https://review.opendev.org/changes/?q=change:{CHANGE_ID}&o=CURRENT_REVISION&o=DETAILED_LABELS" \
  | tail -n +2 | python3 -m json.tool
```

Extract: review number, subject, status, owner.

Build the **Depends-On Chain** table.

**2-G.d: Related reviews (same topic)**

If the review has a topic set, search for other reviews with the same topic:

```bash
curl -s "https://review.opendev.org/changes/?q=topic:{TOPIC}+project:{PROJECT}+status:open&o=CURRENT_REVISION&o=DETAILED_LABELS" \
  | tail -n +2 | python3 -m json.tool
```

Filter out the current review from results. Extract for each:
- Review number, subject, status, owner

Build the **Same Topic** table (if more than 1 result).

**2-G.e: Related reviews (same Jira ticket)**

For each Jira ticket found in Step 2-G.a, search Gerrit for other reviews
that reference the same ticket:

```bash
curl -s "https://review.opendev.org/changes/?q=message:{TICKET-KEY}+project:{PROJECT}&o=CURRENT_REVISION&o=DETAILED_LABELS" \
  | tail -n +2 | python3 -m json.tool
```

Filter out the current review(s). This discovers alternative implementations
or related patches for the same issue.

Build the **Same Jira Ticket** table (if more than 1 result).

Cap total related review fetches at 20. Note truncation if more exist.

After Step 2-G, continue to Step 3 (knowledge cross-reference works
for all sources).

### Step 2.5: Gerrit Cross-Reference (Epic Mode Only)

For each child ticket found in Step 2, search OpenDev Gerrit for associated
reviews. This step runs automatically in epic mode -- no `--deep` flag required.

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
| NEW + Code-Review +2 (x2) + Workflow +1 | Ready to Merge |
| NEW + Code-Review +2 | Approved (need +2x2) |
| NEW (no negative votes, no +2) | Under Review |
| No review found for ticket | -- |

Apply the first matching row (most specific first). Evaluate in the order
shown -- e.g., "Needs Revision" takes priority over "Under Review" if both
a -1 and no +2 are present.

**Topic-based cross-reference (optional):**

If the epic description or labels mention a Gerrit topic (e.g., `de-angularize`),
also search for topic-based reviews:

```bash
curl -s "https://review.opendev.org/changes/?q=topic:{topic}+project:openstack/horizon+status:open&o=CURRENT_REVISION&o=DETAILED_LABELS" | tail -n +2 | python3 -m json.tool
```

Cross-reference these with per-ticket results. If a topic-based review was NOT
found by the per-ticket message search, note it as an "unlinked review" in the
output -- it may be missing a Jira key in its commit message.

If a child ticket has multiple Gerrit reviews, track all of them.

### Step 3: Cross-Reference Knowledge Bases

Scan the ticket description for keywords and load matching knowledge:

| Match | Knowledge Base |
|-------|---------------|
| PQC, quantum, TLS, kRSA, ML-KEM, post-quantum, cipher | `../../knowledge/feature-pqc.md` |
| Horizon, dashboard, panel, Angular, Django | `../../knowledge/horizon.md` |
| support, upgrade, regression, must-gather | `../../knowledge/support-investigation.md` |
| review, gerrit, comment, tracker, patch | `../../knowledge/review-tracking.md` |
| launchpad, oslo, scope, policy, upstream bug | `../../knowledge/launchpad-openstack.md` |

**For Gerrit sources:** Always load `../../knowledge/horizon.md` (since the workflow
is Horizon-focused). Also scan the commit message and changed files for keyword matches.

Read matching knowledge files before generating the assessment.

### Step 4: Deep Analysis (if --deep)

If DEEP=true, additionally:
- Search for related PRs on GitHub/OpenDev
- Identify code paths affected
- Map cross-team dependencies with contact info
- Check if existing PRs address this ticket

### Step 4.5: Generate Fix Proposals (if --generate-fix)

If GENERATE_FIX=true (requires DEEP=true), analyze the ticket and generate
concrete code change proposals.

**Prerequisites check:**
- If GENERATE_FIX=true but DEEP=false, error and suggest: `--generate-fix requires --deep`
- Extract affected code paths from ticket description or Deep Analysis (Step 4)

**For each affected file path mentioned in the ticket:**

1. **Locate the repository:**
   - Check if file path is in openstack-k8s-operators repos (horizon-operator, nova-operator, etc.)
   - Check if file path is in openstack repos (horizon, nova, etc.)
   - If repo is not locally available, note "Repository checkout needed" in proposal

2. **Read the affected file(s):**
   - Use grep/find to locate the file
   - Read the relevant sections (use line numbers if provided in ticket)
   - Read surrounding context (±20 lines) to understand structure

3. **Generate fix proposal:**
   - **Current Code** block: Show the problematic code
   - **Proposed Change** block: Show the fixed code with inline comments explaining changes
   - **Rationale**: Explain why this change fixes the issue
   - **Testing Strategy**: Suggest how to verify the fix works
   - **Migration Notes**: If the change breaks compatibility, note upgrade path

4. **Write `artifacts/triassessment/{CASE_ID}/proposed_fixes.md`** with structure:

```markdown
# Proposed Fixes: <TICKET-ID>

**Ticket:** [<TICKET-ID>](ticket-url)
**Generated:** <timestamp>
**Confidence:** <LOW|MEDIUM|HIGH> based on available context

## Summary

<One-paragraph summary of the fix approach>

## Affected Files

<Table of files to be changed, with change type (modify/add/delete)>

| File | Change Type | Lines | Complexity |
|------|-------------|-------|------------|
| path/to/file.py | Modify | ~15 | Medium |

---

## Fix 1: <Short description>

**File:** `path/to/file.py`
**Lines:** 123-145
**Complexity:** Medium
**Risk:** Low (no API changes)

### Current Code

```python
# Current implementation (problematic)
def problematic_function():
    # ... code ...
```

### Proposed Change

```python
# Fixed implementation
def problematic_function():
    # FIX: Set AllowPrivilegeEscalation to false per OSPRH-33457
    security_context = {
        "allowPrivilegeEscalation": False,  # Changed from True
        "runAsUser": 48,
        "capabilities": {
            "drop": ["ALL"]  # Changed from ["MKNOD"]
        }
    }
```

### Rationale

<Explain why this change fixes the issue, reference ticket details>

### Testing Strategy

<Suggest unit tests, integration tests, manual verification steps>

### Migration Notes

<If breaking change: upgrade path, deprecation warnings, etc.>

---

## Fix 2: <Next fix>

...

---

## Implementation Checklist

- [ ] Review fix proposals with team
- [ ] Create feature branch
- [ ] Implement Fix 1: <description>
- [ ] Implement Fix 2: <description>
- [ ] Run test suite
- [ ] Manual verification
- [ ] Submit Gerrit review
- [ ] Link review to <TICKET-ID>

---

**Disclaimer:** These proposals are AI-generated based on ticket description
and available code context. Review carefully before implementation.

Generated: <timestamp> | Skill: /triassessment --generate-fix | Model: <model-id>
```

**Confidence levels:**
- **HIGH**: All affected files located, full context available, fix is straightforward
- **MEDIUM**: Most files located, some assumptions made, fix requires judgment
- **LOW**: Missing code context, fix is speculative, requires investigation

**If code files cannot be located:**
- Note which files are missing
- Provide fix proposals based on ticket description alone
- Set confidence to LOW
- Suggest: "Clone <repo-url> to enable concrete fix proposals"

### Step 5: Generate Triage Assessment

Write `artifacts/triassessment/{CASE_ID}/triage_assessment.md` with sections:

1. **Ticket Summary** -- Key/value table of ticket fields
2. **Affected Projects** -- (Launchpad only) Per-project status table
3. **Comment Timeline** -- (Launchpad only) Summarized comment thread
4. **Linked Reviews** -- (Launchpad only) Gerrit reviews parsed from comments
5. **Technical Context** -- Plain language explanation of the ask
6. **Dependencies & Blockers** -- Table of related tickets and their status
7. **Impact Analysis** -- What happens if we proceed vs close
8. **Recommendation** -- Verdict (CLOSE/IMPLEMENT/DEFER/ESCALATE/MONITOR), confidence, rationale
9. **Talking Points** -- Bullet points for stakeholder response
10. **Deep Analysis** -- (only if --deep) Extended code/PR references

**Launchpad Ticket Summary format:**

```markdown
## Ticket Summary

| Field | Value |
|-------|-------|
| Key | [LP#NNNNNNN](https://bugs.launchpad.net/bugs/NNNNNNN) |
| Title | Bug title |
| Source | Launchpad |
| Filed | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Reporter | Display Name (username) |
| Heat | N |
| Tags | tag1, tag2 or (none) |
| Security Related | Yes/No |
```

**Affected Projects table (Launchpad only):**

```markdown
## Affected Projects

| Project | Status | Importance | Assignee | Milestone |
|---------|--------|------------|----------|-----------|
| project-a | Fix Released | High | Name | milestone |
| project-b | New | Undecided | Unassigned | -- |
```

**Comment Timeline (Launchpad only):**

```markdown
## Comment Timeline

| # | Author | Date | Summary |
|---|--------|------|---------|
| 0 | username | YYYY-MM-DD HH:MM | One-line summary of comment |
```

**Linked Reviews (Launchpad only, from comment parsing):**

```markdown
## Linked Reviews

| Review | Subject | Status | Project | Files | Lines |
|--------|---------|--------|---------|-------|-------|
| [NNNNNN](gerrit-url) | Subject | Merged | project | N | +A/-D |
```

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

**Epic Children Status** -- the primary at-a-glance table:

```markdown
## Epic Children Status

| Key | Summary | Type | Status | Assignee | Created | Updated | Review | Review Status |
|-----|---------|------|--------|----------|---------|---------|--------|---------------|
| [OSPRH-XXXXX](jira-url) | Short title (~60 chars) | Story | In Progress | Name | 2026-01-15 | 2026-07-10 | [986458](gerrit-url) | Under Review |
| [OSPRH-YYYYY](jira-url) | Short title | Story | Done | Name | 2026-02-01 | 2026-06-20 | [985123](gerrit-url) | **Merged** |
| [OSPRH-ZZZZZ](jira-url) | Short title | Task | To Do | Unassigned | 2026-03-10 | 2026-03-10 | -- | -- |
```

Column rules:
- **Key:** clickable Jira link -- `[OSPRH-XXXXX](https://redhat.atlassian.net/browse/OSPRH-XXXXX)`
- **Summary:** first ~60 characters of the ticket summary
- **Type:** Story, Task, Sub-task, Bug, etc.
- **Status:** Jira status verbatim
- **Assignee:** Jira assignee display name, or "Unassigned" if empty
- **Created:** YYYY-MM-DD format
- **Updated:** YYYY-MM-DD format
- **Review:** clickable Gerrit link `[{number}](review-url)`, or "--" if none found
- **Review Status:** human-readable status from Step 2.5, or "--" if no review

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
- `(per feature-pqc.md, Section 2)` -- auto-links to GitHub knowledge file
- `(from horizon.md)` -- auto-links without section
- Jira tickets (`OSPRH-12345`, `RHOSSTRAT-123`) -- auto-link
- Patterns: `(per|from|see|via) <filename>.md[, Section N]`

#### Gerrit Review Assessment (when SOURCE=gerrit)

When the source is a Gerrit review, Step 5 produces a different structure
optimized for code review assessment rather than ticket triage.

Write `artifacts/triassessment/{CASE_ID}/triage_assessment.md` with sections:

1. **Review Summary** -- Key/value table of review fields
2. **Commit Message** -- Full commit message with footer references
3. **Jira Cross-Reference** -- Linked Jira tickets (if any)
4. **Launchpad Cross-Reference** -- Linked LP bugs (if any)
5. **Changed Files** -- Table of modified files with line counts
6. **Related Reviews** -- Depends-On chain, same topic, same Jira ticket
7. **Technical Context** -- Plain language: what does this review do?
8. **Impact Analysis** -- What happens if merged vs abandoned
9. **Recommendation** -- Verdict (MERGE/NEEDS_REVISION/ABANDON/DEFER/INVESTIGATE), confidence, rationale
10. **Review Points** -- Checklist-style bullet points for code review
11. **Deep Analysis** -- (only if --deep) Extended code/test analysis

**Review Summary format:**

```markdown
# Triage Assessment: Review {REVIEW_NUMBER}

**Review:** [{REVIEW_NUMBER}](https://review.opendev.org/c/{PROJECT}/+/{REVIEW_NUMBER})  
**Generated:** {timestamp}  
**Source:** OpenDev Gerrit  
**Skill:** /triassessment --gerrit

---

## Review Summary

| Field | Value |
|-------|-------|
| Review | [{REVIEW_NUMBER}](https://review.opendev.org/c/{PROJECT}/+/{REVIEW_NUMBER}) |
| Subject | {commit subject line} |
| Project | {project} |
| Branch | {branch} |
| Status | {status display from Step 1-G.d} |
| Topic | {topic or (none)} |
| Owner | {name} ({username}) |
| Created | YYYY-MM-DD HH:MM |
| Updated | YYYY-MM-DD HH:MM |
| Patchset | #{patchset_number} |
| Files Changed | {N} files (+{additions}/-{deletions} lines) |
| Code-Review | {vote summary: +2 (×N), +1 (×N), -1 (×N)} |
| Verified | {vote summary: +1 (Zuul)} or {-1 (Zuul)} |
| Workflow | {+1 or --} |
```

**Commit Message section:**

```markdown
## Commit Message

\`\`\`
{full commit message including all footers}

Change-Id: I{change_id}
Closes-Bug: #{bug_id}
Related: OSPRH-XXXXX
\`\`\`
```

**Jira Cross-Reference section (if Jira tickets found):**

```markdown
## Jira Cross-Reference

| Ticket | Summary | Status | Type | Assignee |
|--------|---------|--------|------|----------|
| [OSPRH-XXXXX](jira-url) | {summary} | {status} | {type} | {assignee or Unassigned} |
```

**Launchpad Cross-Reference section (if LP bugs found):**

```markdown
## Launchpad Cross-Reference

| Bug | Title | Status (horizon) | Importance |
|-----|-------|------------------|------------|
| [LP#{bug_id}](lp-url) | {title} | {status} | {importance} |
```

**Changed Files section:**

```markdown
## Changed Files

| File | Status | Lines | Complexity |
|------|--------|-------|------------|
| {filepath} | Modified | +{ins}/-{del} | {LOW/MEDIUM/HIGH based on line count} |
```

Complexity heuristic:
- LOW: < 50 lines changed
- MEDIUM: 50-150 lines changed
- HIGH: > 150 lines changed

**Related Reviews section (if any found in Step 2-G):**

```markdown
## Related Reviews

### Depends-On Chain

| Review | Subject | Status | Owner |
|--------|---------|--------|-------|
| [{number}](gerrit-url) | {subject} | {status} | {owner.name} |

### Same Topic: {topic}

| Review | Subject | Status | Owner |
|--------|---------|--------|-------|
| [{number}](gerrit-url) | {subject} | {status} | {owner.name} |

### Same Jira Ticket: OSPRH-XXXXX

| Review | Subject | Status | Owner |
|--------|---------|--------|-------|
| [{number}](gerrit-url) | {subject} | {status} | {owner.name} |
```

Only include subsections where results were found.

**Technical Context, Impact Analysis, Recommendation, Review Points:**

Use the same format as Jira/Launchpad assessments, but adapt the content
to focus on code review questions:
- Does this implementation match the ticket requirements?
- Are there test coverage gaps?
- Does this introduce breaking changes?
- Are there alternative approaches in related reviews?

Include a footer: `Generated: <timestamp> | Skill: /triassessment --gerrit | Model: <model-id>`

#### Gerrit Comparison Assessment (when SOURCE=gerrit_compare)

When running in comparison mode (`--compare`), Step 5 produces both
individual assessments (one per review) AND a comparison artifact.

Write three files:
1. `artifacts/triassessment/{CASE_ID}/triage_assessment_primary.md` -- Assessment of PRIMARY_REVIEW
2. `artifacts/triassessment/{CASE_ID}/triage_assessment_compare.md` -- Assessment of COMPARE_REVIEW
3. `artifacts/triassessment/{CASE_ID}/comparison.md` -- Side-by-side comparison

**comparison.md structure:**

```markdown
# Review Comparison: {PRIMARY_REVIEW} vs {COMPARE_REVIEW}

**Primary Review:** [{PRIMARY_REVIEW}](gerrit-url)  
**Comparison Review:** [{COMPARE_REVIEW}](gerrit-url)  
**Both address:** {common Jira tickets or "No explicit linkage"}  
**Generated:** {timestamp}

---

## Side-by-Side Summary

| Aspect | Review {PRIMARY_REVIEW} | Review {COMPARE_REVIEW} |
|--------|-------------------------|-------------------------|
| Subject | {subject} | {subject} |
| Status | {status} | {status} |
| Owner | {owner.name} | {owner.name} |
| Files Changed | {N} files | {M} files |
| Lines Changed | +{ins}/-{del} | +{ins}/-{del} |
| Patchset | #{ps} | #{ps} |
| Code-Review | {vote summary} | {vote summary} |
| Verified | {vote summary} | {vote summary} |
| Created | YYYY-MM-DD | YYYY-MM-DD |
| Updated | YYYY-MM-DD | YYYY-MM-DD |
| Topic | {topic or (none)} | {topic or (none)} |
| Test Coverage | {Yes/No/Partial from file analysis} | {Yes/No/Partial} |

## Overlap Analysis

**Common Files Modified:**

| File | {PRIMARY_REVIEW} Lines | {COMPARE_REVIEW} Lines |
|------|------------------------|------------------------|
| {filepath} | +{ins}/-{del} | +{ins}/-{del} |

**Unique to Review {PRIMARY_REVIEW}:**
- {filepath} (+{ins}/-{del})
- {filepath} (+{ins}/-{del})

**Unique to Review {COMPARE_REVIEW}:**
- {filepath} (+{ins}/-{del})
- {filepath} (+{ins}/-{del})

## Approach Comparison

### Review {PRIMARY_REVIEW} Approach

{Plain language explanation: What does this review do? How does it solve
the problem? What are the key implementation choices?}

### Review {COMPARE_REVIEW} Approach

{Plain language explanation: What does this review do? How does it solve
the problem? What are the key implementation choices?}

## Key Differences

1. **Implementation Strategy:** {difference 1}
2. **File Scope:** {difference 2}
3. **Test Coverage:** {difference 3}
4. **Breaking Changes:** {difference 4}

## Recommendation

**Preferred:** {PRIMARY_REVIEW} / {COMPARE_REVIEW} / MERGE_BOTH / NEITHER / INVESTIGATE_FURTHER

**Confidence:** HIGH / MEDIUM / LOW

**Rationale:**

{Why this verdict? What are the key differentiators? Which approach is
more maintainable, complete, or aligned with project conventions?}

**Path Forward:**

- {Action item 1}
- {Action item 2}
- {Action item 3}

---

Generated: {timestamp} | Skill: /triassessment --gerrit --compare | Model: {model-id}
```

**Comparison heuristics:**

- **File overlap percentage:** `(common_files / total_unique_files) * 100`
- **Approach similarity:** LOW (< 30% overlap), MEDIUM (30-70%), HIGH (> 70%)
- **Test coverage comparison:** Count test files in changed files for each review
- **Complexity comparison:** Sum complexity scores from Changed Files tables

### Step 6: Generate Related Artifacts Summary

**For Jira/Launchpad sources:**

Write `artifacts/triassessment/{CASE_ID}/related_tickets.md` with sections:

1. **Ticket Hierarchy** -- Table: Level, Ticket, Title, Status, Assignee, Created, Updated
2. **Blocking Chain** -- Visual representation of blocking relationships
3. **Cross-Team Dependencies** -- Table: Dependency, Team, Status, Notes
4. **Resolution Paths** -- For blocked tickets, list possible paths forward

**For Gerrit sources:**

Write `artifacts/triassessment/{CASE_ID}/related_reviews.md` with sections:

1. **Review Network** -- Visual representation of review relationships (Depends-On, same topic, same ticket)
2. **Jira Ticket Context** -- (if linked) Ticket hierarchy from Step 2-G.a
3. **Alternative Implementations** -- (from Step 2-G.e) Other reviews addressing the same ticket
4. **Merge Dependencies** -- (from Step 2-G.c) Depends-On chain with merge status
5. **Path Forward** -- Recommended sequence for merging related reviews

**For Gerrit comparison mode:**

Write `artifacts/triassessment/{CASE_ID}/related_reviews.md` covering BOTH reviews.

Skip this step if there are no related reviews/tickets to document.

### Step 7: Publish to Dashboard (if --update-artifact-dashboard)

If PUBLISH=true, auto-ingest artifacts into the dashboard:

Run the ingestion script:
```bash
cd /home/omcgonag/Work/mymcp/workspace/iproject/projects/ioshaworkflow/repo/ioshaworkflow
python scripts/ingest_artifacts.py \
  <CASE_ID> \
  triassessment \
  triassessment \
  --skill-type triassessment/<CASE_ID> \
  --title "<ticket-summary-truncated-to-80-chars>" \
  --summary "Triage assessment of <TICKET-ID>: <brief-context>"
```

**Note:** The `--skill-type triassessment/<CASE_ID>` points to the per-ticket subdirectory created in Step 5/6.

**Case ID conventions:**
- Jira: `TRIASSESSMENT-OSPRH-27628`
- Launchpad: `TRIASSESSMENT-LP-2161292`
- Gerrit: `TRIASSESSMENT-996428`
- Gerrit comparison: `TRIASSESSMENT-996428-vs-998960`

**Title Formatting:**
- Keep under 80 characters
- For Jira/LP: "RCA of <component> <issue-type> (<severity>)" for security bugs
- For Jira/LP: "<Action> <component> <brief-description>" for features/stories
- For Gerrit: "Review <number>: <abbreviated-subject>" (subject truncated to fit 80 chars)
- For Gerrit comparison: "Compare reviews <A> vs <B>: <common-topic>"
- Examples:
  - "RCA of Horizon operator security vulnerability (CVSS 7.3)"
  - "Review 996428: Add RoleName to IdentityAPIAccessControlsTestCase"
  - "Compare reviews 996428 vs 998960: OSPRH-25872 fix approaches"

**Summary Formatting:**
- For Jira/LP: "Triage assessment of <TICKET-ID>: <brief-context>"
- For Gerrit single: "Review assessment of <REVIEW-NUMBER>: <what-it-does>"
- For Gerrit comparison: "Comparison of reviews <A> vs <B> for <ticket>: <difference-summary>"
- Keep total under 200 characters
- Examples:
  - "Triage assessment of OSPRH-33457: Root cause analysis for horizon-operator privilege escalation path"
  - "Review assessment of 996428: Adds RoleName validation to identity API access control tests"
  - "Comparison of reviews 996428 vs 998960 for OSPRH-25872: Scope coverage differences in test implementation"

**After ingestion succeeds:**
Report the dashboard URL to the user:
```
✅ Artifacts published to dashboard
View at: http://10.0.151.101:8072/investigations/<CASE_ID>?run=run-001
```

**If ingestion fails:**
Inform the user with the error message and provide manual instructions:
```
❌ Auto-ingestion failed: <error-message>

Manual ingestion:
cd /home/omcgonag/Work/mymcp/workspace/iproject/projects/ioshaworkflow/repo/ioshaworkflow
python scripts/ingest_artifacts.py \
  <CASE_ID> \
  triassessment \
  triassessment \
  --skill-type triassessment/<CASE_ID> \
  --title "<ticket-summary>" \
  --summary "Triage assessment of <TICKET-ID>"
```

## Output

Files written to artifacts/triassessment/{CASE_ID}/:

**For Jira/Launchpad sources:**
- triage_assessment.md -- Structured assessment with recommendation
- related_tickets.md -- Related ticket hierarchy and dependencies
- proposed_fixes.md -- (only if --generate-fix) Concrete code change proposals with diffs

**For Gerrit single review:**
- triage_assessment.md -- Review assessment with recommendation
- related_reviews.md -- Related review network (Depends-On, same topic, same ticket)
- proposed_fixes.md -- (only if --generate-fix) Code improvement proposals

**For Gerrit comparison:**
- triage_assessment_primary.md -- Assessment of primary review
- triage_assessment_compare.md -- Assessment of comparison review
- comparison.md -- Side-by-side comparison with recommendation
- related_reviews.md -- Combined review network for both reviews

**Directory structure:**
```
artifacts/triassessment/
├── TRIASSESSMENT-OSPRH-33457/
│   ├── triage_assessment.md
│   ├── related_tickets.md
│   └── proposed_fixes.md
├── TRIASSESSMENT-LP-2161292/
│   ├── triage_assessment.md
│   └── related_tickets.md
├── TRIASSESSMENT-996428/
│   ├── triage_assessment.md
│   └── related_reviews.md
└── TRIASSESSMENT-996428-vs-998960/
    ├── triage_assessment_primary.md
    ├── triage_assessment_compare.md
    ├── comparison.md
    └── related_reviews.md
```

This per-case directory structure ensures:
- No overwrites across different assessments
- Clean git history (each assessment is a separate directory)
- Easy archival/deployment (copy entire subdirectories)

## Knowledge Sources

Loaded conditionally based on ticket content:
- knowledge/feature-pqc.md -- PQC compliance context
- knowledge/horizon.md -- Horizon project reference
- knowledge/support-investigation.md -- Support investigation patterns
- knowledge/launchpad-openstack.md -- Launchpad bug lifecycle and OpenStack patterns

## Rules

Follow the behavioral rules in rules.md within this workflow directory.
