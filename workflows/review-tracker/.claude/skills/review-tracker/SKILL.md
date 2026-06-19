---
name: review-tracker
description: Track the lifecycle of an OpenDev Gerrit review — comment threads, reviewer status, votes, and action items. Creates a living document that updates incrementally on recheck. Use when you want to understand where a review conversation stands and what needs attention.
---

# Review Tracker

You are tracking an OpenDev Gerrit review conversation. Your goal is to create or update a living document that captures every comment thread, its status, and what the user needs to do next.

**Agent Collaboration — MANDATORY**: Always invoke **@review-tracker.md** for every tracking operation. This persona handles thread grouping, status classification, and recheck logic. Skip only if the user explicitly asks to.

**Context inheritance**: When invoking subagents, always pass the workflow `rules.md` and `knowledge/review-tracking.md` content as context. Workflow rules and project knowledge take precedence over agent persona guidance.

## Input

The user will provide one of:

- A Gerrit change number (e.g., `977939`)
- A Gerrit change URL (e.g., `https://review.opendev.org/c/openstack/horizon/+/977939`)
- A change number with `--recheck` flag (incremental update)
- A change number with `--status` flag (quick summary, no doc update)

## Process

### Step 0: Parse Input and Determine Mode

1. **Parse input** — extract the change number:
   - If a full URL: extract the number from the path
   - If a bare number: use directly

2. **Determine mode**:
   - If `--status` flag: print current header + Open Threads table from existing tracker, STOP
   - If `--recheck` flag: go to **Recheck Mode** (Step R1)
   - Otherwise: check if `artifacts/review-tracker/tracker-{number}.md` exists
     - If exists: tell the user "Tracker already exists. Use `--recheck` to update, or `--force` to regenerate from scratch."
     - If not exists: go to **Initial Scan Mode** (Step 1)

---

### Initial Scan Mode

#### Step 1: Fetch Review Metadata

Call the Gerrit REST API:

```
GET https://review.opendev.org/changes/{change-id}/detail?o=DETAILED_LABELS&o=CURRENT_REVISION&o=MESSAGES
```

Strip the `)]}' ` XSSI prefix from the response (first line).

Extract:
- `subject` → review title
- `owner.name` → author
- `status` → review status (NEW, MERGED, ABANDONED)
- `updated` → last activity timestamp
- Current patchset number from `revisions`
- Votes from `labels` (Verified, Code-Review, Workflow)
- Message timeline from `messages` (patchset uploads, CI results)

#### Step 2: Fetch All Comments

```
GET https://review.opendev.org/changes/{change-id}/comments
```

Strip the XSSI prefix. This returns a map of `{filepath: [comment]}`.

For each comment, capture: `id`, `author.name`, `updated`, `message`, `line`, `patch_set`, `unresolved`, `in_reply_to`.

#### Step 3: Group and Assess

Follow the thread grouping algorithm from the agent persona:

1. Build reply chains from `in_reply_to` references
2. Group root comments by file + line
3. For `/PATCHSET_LEVEL` comments with no reply chain: group by topic
4. Assign `CMT-{AUTHOR}-{N}` thread IDs
5. Classify each thread's status using the status classification rules
6. Write an AI assessment for each thread (significance, blocking/suggestion/nit, action)

#### Step 4: Generate Document

Write the full tracker document to `artifacts/review-tracker/tracker-{change-number}.md`.

Follow this section order exactly:

```markdown
# Review {number} — Live Comment Tracker

**Review:** {gerrit URL}
**Title:** {subject}
**Author:** {owner}
**Status:** {status}
**Current Patchset:** {number}
**Zuul:** {Verified vote status}
**Files Changed:** {count} ({brief summary of areas})
**Reviewers:** {list of reviewers who commented}

---

## Scan Log

| # | Date | Scanner | Notes |
|---|------|---------|-------|
| 1 | {today} | AI (Claude) | Initial scan — {N} comment threads from {M} reviewers |

---

## Where Things Are At / What To Do Next

### Overall Status
{Narrative summary: patchset count, review activity, key developments}

### Score Summary
{Current votes on each label}

### What You Should Do Next
{Prioritized action items based on open thread analysis}

### Open Threads Requiring Attention

| Thread | File | Status | Owner | Priority |
|--------|------|--------|-------|----------|
| [CMT-XXX-N](#cmt-xxx-n) | {file} | {status} | {who needs to act} | {HIGH/MEDIUM/LOW} |

---

## Patchset-Level Comments

{Thread sections for /PATCHSET_LEVEL comments}

## Inline Comments — {Reviewer Name}

{Thread sections grouped by reviewer}

---

## Comment Statistics

| Reviewer | Total | Resolved | Pending |
|----------|-------|----------|---------|
| {name} | {n} | {n} | {n} |

---

## Key Remaining Items Before This Can Merge

| Item | Severity | Status |
|------|----------|--------|
| {description} | {HIGH/MEDIUM/LOW} | {OPEN/RESOLVED} |
```

Each thread section uses this format:

```markdown
<a name="cmt-xxx-n"></a>
### CMT-XXX-N — {brief topic} — {STATUS}

**Author:** {name} | **File:** {path} | **PS:** {patchset}

> {quoted comment text}

**Reply ({author}, PS{n}):**
> {reply text}

**AI Assessment:** {1-2 sentence assessment of significance and whether it's blocking}

**Status for {User}:** {specific action the user should take}
```

---

### Recheck Mode

#### Step R1: Check for Changes

Read the existing tracker document. Parse the Scan Log to find the date of the most recent scan.

Fetch the review's `updated` timestamp:

```
GET https://review.opendev.org/changes/{change-id}
```

If `updated` is not newer than the last scan date: report "No changes since scan #N on YYYY-MM-DD. Review last updated {timestamp}." and STOP.

#### Step R2: Fetch Current State

Same API calls as Steps 1 and 2 of Initial Scan.

#### Step R3: Diff Against Documented State

Compare the fetched data against the existing document:

| What to check | How to detect |
|---------------|--------------|
| New comments | `updated` timestamp > last scan date |
| Thread status changes | `unresolved` field differs from documented status |
| New patchset | Current PS number > documented PS number |
| Vote changes | Current label values differ from Score Summary |
| CI results | Verified label changed |
| New replies | Comments with `in_reply_to` pointing to documented threads |

#### Step R4: Update Document

For each detected change:

1. Update the affected section in the document
2. Add a Change Log entry (reverse chronological, newest first):

```markdown
## Change Log

### Scan #N — YYYY-MM-DD

1. **NEW** [CMT-XXX-N](#cmt-xxx-n): New comment from {author} on {file}
2. **UPDATED** [Score Summary](#score-summary): Zuul Verified+1 on PS{n}
```

3. Add a new row to the Scan Log
4. Update Comment Statistics
5. Update Open Threads table
6. Update Key Remaining Items (strikethrough completed items)
7. Update header metadata (patchset, Zuul status)

**Do not** rewrite sections with no changes. **Do not** re-generate AI assessments for unchanged threads.

## Output

Write the tracker to:

```
artifacts/review-tracker/tracker-{change-number}.md
```

This file is both the output artifact and the state for future rechecks.
