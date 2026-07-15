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
- A change number with `--deep-dive` flag (bridge to code analysis for reviewer questions)
- A change number with `--create-patch` flag (check out review, apply fixes from tracker)
- A change number with `--verify-patch` flag (run tox tests against patched checkout)
- A change number with `--final-report` flag (post-merge assessment with metrics)
- A change number with `--update-artifact-dashboard` flag (publish to ioshaworkflow dashboard)
- A change number with `--clone-at PATH` flag (specify where to clone the review code)

Flags are composable:

```
/review-tracker 977939 --create-patch
/review-tracker 977939 --create-patch --verify-patch
/review-tracker 977939 --create-patch --verify-patch --update-artifact-dashboard
/review-tracker 977939 --recheck --create-patch
/review-tracker 977939 --verify-patch
/review-tracker 977939 --final-report
/review-tracker 977939 --final-report --update-artifact-dashboard
/review-tracker 986458 --clone-at /tmp/my-review
/review-tracker 986458 --clone-at /tmp/my-review --create-patch --verify-patch
```

## Process

### Step 0: Parse Input and Determine Mode

1. **Parse input** — extract the change number:
   - If a full URL: extract the number from the path
   - If a bare number: use directly

2. **Detect modifier flags**:
   - `--deep-dive`: set `deep_dive = true`
   - `--update-artifact-dashboard`: set `publish_after = true`
   - `--create-patch`: set `create_patch = true`
   - `--verify-patch`: set `verify_patch = true`
   - `--final-report`: set `final_report = true`
   - `--horizon-url URL`: set `horizon_url = URL` (enables Playwright browser testing)
   - If `horizon_url` not set by flag, check `HORIZON_URL` env var. If not set, Playwright step is skipped.
   - `--clone-at PATH`: set `clone_at = PATH`
   - If `clone_at` not set by flag, check `REVIEW_CLONE_ROOT` env var.
   - If neither set, use default: `IPROJECT_ROOT/projects/review_{number}/reviews/`
     where `IPROJECT_ROOT = /home/omcgonag/Work/mymcp/workspace/iproject`

3. **Determine primary mode**:
   - If `--status` flag: print current header + Open Threads table from existing tracker, STOP
     (all other flags are ignored with `--status`)
   - If `--final-report` flag: go to **Final Report Mode** (Step F1)
     - Requires review status = MERGED. If not MERGED, report error and STOP.
     - Requires existing tracker artifact. If missing, report error and STOP.
   - If `--recheck` flag: go to **Recheck Mode** (Step R1)
   - Otherwise: check if `artifacts/review-tracker/tracker-{number}.md` exists
     - If exists AND no action flags: tell the user "Tracker already exists. Use `--recheck` to update, or `--force` to regenerate from scratch."
     - If exists: proceed to post-primary actions
     - If not exists: go to **Bootstrap and Initial Scan Mode**:
       1. Run **Step 0.5: Bootstrap Review Project** (if using default path)
       2. Run **Step 0.6: Clone Review Code**
       3. Run **Step 0.7: Initial Code Review Bridge**
       4. Then proceed to **Initial Scan Mode** (Step 1)
       5. Set `publish_after = true` (auto-publish on first run)

4. **Post-primary-mode actions** (in order):
   - If `create_patch`: go to **Create Patch Mode** (Step C1)
   - If `verify_patch`: go to **Verify Patch Mode** (Step V1)
   - If `publish_after`: go to **Publish Mode** (Step P1)

---

### Bootstrap and Clone (First Run Only)

These steps run ONLY on first invocation (no existing tracker artifact).

#### Step 0.5: Bootstrap Review Project

**Condition:** Using default clone path (no `--clone-at` flag, no `REVIEW_CLONE_ROOT` env var).

Compute the default project path:

```
IPROJECT_ROOT = /home/omcgonag/Work/mymcp/workspace/iproject
PROJECT_NAME  = review_{number}
PROJECT_DIR   = ${IPROJECT_ROOT}/projects/${PROJECT_NAME}
CLONE_ROOT    = ${PROJECT_DIR}/reviews
```

If `PROJECT_DIR` does not exist, create the iproject project:

```
Call create_project MCP tool:
  project_name = "review_{number}"
  description  = "Review tracking for Gerrit {number}: {subject}"
```

If `create_project` fails (MCP unavailable, permissions, etc.): fall back to
creating the directory manually:

```bash
mkdir -p "${CLONE_ROOT}"
```

**Skip this step if:**
- `--clone-at` was provided (user is managing their own directory)
- `REVIEW_CLONE_ROOT` env var is set
- Project directory already exists

#### Step 0.6: Clone Review Code

Resolve the clone root path:

```
if clone_at is set:
    CLONE_ROOT = clone_at
elif REVIEW_CLONE_ROOT env var is set:
    CLONE_ROOT = REVIEW_CLONE_ROOT
else:
    CLONE_ROOT = ${IPROJECT_ROOT}/projects/review_{number}/reviews
```

Compute clone paths:

```
CLONE_DIR   = ${CLONE_ROOT}/horizon-review-${number}
LAST2       = number % 100, zero-padded to 2 digits
PROJECT     = Gerrit project path (e.g., openstack/horizon)
PATCHSET    = current patchset number from Gerrit API
```

**If `CLONE_DIR` already exists:**

```bash
cd "${CLONE_DIR}"
# Check for dirty state
if [ -n "$(git status --porcelain)" ]; then
    echo "WARNING: Existing clone has uncommitted changes:"
    git status --short
    echo ""
    echo "Clean up the checkout before proceeding, or use --clone-at to specify a different path."
    STOP
fi
# Reuse clean checkout -- update to current patchset if needed
echo "Reusing existing clone at ${CLONE_DIR}"
git fetch origin "refs/changes/${LAST2}/${number}/${PATCHSET}"
git checkout FETCH_HEAD
```

**If `CLONE_DIR` does not exist:**

```bash
mkdir -p "${CLONE_ROOT}"
git clone "https://review.opendev.org/${PROJECT}" "${CLONE_DIR}"
cd "${CLONE_DIR}"
git fetch origin "refs/changes/${LAST2}/${number}/${PATCHSET}"
git checkout FETCH_HEAD
```

Report:

```
Clone: ${CLONE_DIR}
Commit: $(git log -1 --format="%h %s")
Patchset: PS${PATCHSET}
```

Store `CLONE_DIR` and `CLONE_ROOT` for use by later steps (C3, V1).

#### Step 0.7: Initial Code Review Bridge

**Condition:** Initial Scan Mode (first run, no existing tracker). Skip on
`--recheck`, `--create-patch`-only, `--status`, or `--final-report`.

Invoke `/horizon-code-review` with the Gerrit change number. The skill will:

1. Gather context from Gerrit (commit message, prior review history)
2. Read code files from `CLONE_DIR` (the cloned checkout from Step 0.6)
3. Perform its full review (plugin API check, testing adequacy, etc.)
4. Write output to `artifacts/horizon-review/code-{number}.md`

After the horizon-code-review skill completes:

1. Copy the review artifact to the review-tracker bridge artifacts directory:

```bash
mkdir -p artifacts/review-tracker/bridge-artifacts
cp artifacts/horizon-review/code-${number}.md \
   artifacts/review-tracker/bridge-artifacts/initial-review-${number}.md
```

2. Extract key data from the review artifact for inclusion in the tracker:
   - **Verdict** line (APPROVE / REQUEST_CHANGES / COMMENT)
   - **Summary** section (1-2 sentences)
   - **Blockers** section (list of items)
   - **Suggestions** section (list of items)

3. Store extracted data for Step 4 (tracker document generation).

**If bridge fails** (skill error, timeout, unexpected output):

1. Log warning: "Initial code review bridge failed: {reason}"
2. Continue to Step 1 (tracker still provides value without code review)
3. Note in tracker document: "Initial code review: unavailable (bridge error)"

**The tracker ALWAYS completes. Bridge failure is non-fatal.**

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

#### Step 3.5: Bridge to Code Analysis (if --deep-dive)

**ONLY if user passed `--deep-dive` flag**: Detect code-archaeology questions from
reviewer comments and produce actual bridge analysis artifacts with ready-to-paste
Gerrit responses.

This step runs on BOTH initial scan and `--recheck`. On recheck, focus on NEW or
UNRESOLVED threads that were added since the last run.

##### 3.5.1: Detect Bridge Opportunities

For each UNRESOLVED thread, check if it's a code-archaeology question:

**Heuristic:**
1. Contains question pattern: `when/why/how/is there/under what/what happens/does it`
2. Contains code keyword OR references a specific attribute/method/class/variable
3. Status is NOT RESOLVED
4. NOT an LGTM comment, recheck command, or CI status report

**Example matches:**
- "Is there any case where `self.request` doesn't have the `horizon` attribute?"
- "Why do we need the `hasattr` check here?"
- "Under what circumstances would this fail?"

##### 3.5.2: Execute Code Archaeology

For EACH detected bridge opportunity, perform the following research using
the Horizon checkout from Step 0.6 (`CLONE_DIR`). Execute these steps directly
— do NOT delegate to another skill.

**B1 — Search codebase** for the attribute/method/pattern in question:

```bash
git grep -n "{pattern}" -- '*.py'
git grep -n "hasattr.*{pattern}" -- '*.py'
```

Collect file paths, line numbers, and surrounding context (±5 lines).

**B2 — Read relevant files.** From grep results, identify the top 5-10 most
relevant files. Prioritize:
1. File where the question was asked
2. Middleware files (`horizon/middleware.py`, `horizon/middleware/base.py`)
3. Test helpers (`openstack_dashboard/test/helpers.py`)
4. Base classes and context processors

**B3 — Trace lifecycle.** Build a lifecycle map showing where the
attribute/object is created, used, and tested:

| Event | File | Line | Description |
|-------|------|------|-------------|
| Created | ... | ... | Where it's initialized |
| Used | ... | ... | Where the code under review references it |
| Tested | ... | ... | How tests handle it |

**B4 — Identify edge cases.** Check these scenarios:

| Scenario | Missing? | Why |
|----------|----------|-----|
| Production views | ? | Middleware behavior |
| Unit tests (mocked request) | ? | Mock objects may skip middleware |
| Error handlers (500/404) | ? | Whether middleware already ran |
| Admin vs. project context | ? | Same or different path |

**B5 — Pattern analysis.** Count occurrences of similar defensive checks:

```bash
git grep -c "{defensive_pattern}" -- '*.py'
```

Determine if this is a common pattern (>20 occurrences) or rare.

**B6 — Formulate verdict.** Based on lifecycle + edge cases + pattern frequency:
- **NECESSARY** — the check prevents real failures
- **UNNECESSARY** — the check is redundant given framework guarantees
- **CONDITIONAL** — depends on the execution context

**B7 — Draft suggested response.** Write a ready-to-paste Gerrit reply that:
- Directly answers the reviewer's question
- Cites specific file:line evidence
- Is concise (3-5 sentences max in the quote block)
- Sounds like Owen (professional, knowledgeable, respectful)

##### 3.5.3: Write Bridge Artifacts

For each completed analysis, write the artifact to:

```
artifacts/review-tracker/bridge-artifacts/{thread-id-lower}-analysis.md
```

Use this format (matching the `templates/code-archaeology-analysis.md.template`):

```markdown
# Bridge Analysis: {THREAD-ID}

**Question:** {question text from reviewer}

**Reviewer:** {reviewer name}
**Review:** {review number}
**File:** `{file}:{line}`

---

## Investigation

### 1. Where is `{attribute}` set?

**Source:** `{source_file}:{source_line}`
```python
{code snippet showing initialization}
```

**Lifecycle:** {description of when/how it's created}

### 2. Edge cases where it might be missing

| Scenario | Missing? | Why |
|----------|----------|-----|
| Production views | {Yes/No} | {reason} |
| Unit tests (mocked request) | {Yes/No} | {reason} |
| Error handlers (500/404) | {Yes/No} | {reason} |

### 3. Is the defensive check necessary?

**Verdict:** {NECESSARY / UNNECESSARY / CONDITIONAL}

**Evidence:** {specific counts, file references, pattern analysis}

---

## Suggested Response

> {ready-to-paste Gerrit reply}

---

## References

{list of file:line references used in the analysis}
```

Create the bridge-artifacts directory if it doesn't exist:

```bash
mkdir -p artifacts/review-tracker/bridge-artifacts
```

##### 3.5.4: Incorporate Bridge Results into Tracker

For each successful bridge analysis, update the thread's section in the
tracker document with:

```markdown
**Deep Dive:** [Code Analysis](bridge-artifacts/{thread-id-lower}-analysis.md)

**Answer Summary:**
- {key finding 1}
- {key finding 2}
- {key finding 3}

**Suggested Response:**
> {the ready-to-paste response from the analysis}

**Status for Owen:** Copy the suggested response to Gerrit.
```

Place these AFTER the existing **AI Assessment** line. Preserve the original
assessment — the deep dive adds to it, not replaces it.

##### 3.5.5: Handle Failures

If any individual bridge analysis fails (can't find the attribute, grep
returns nothing, question is too vague to research):

1. Log the failure reason
2. Fall back to the structured research guidance note:

```markdown
**Deep Dive:** ⚠️ Automated analysis could not resolve this question.

**Research guidance:**
- Search for `{pattern}` in middleware and base classes
- Check test helpers for mocking patterns
- Review git blame for historical context
```

3. Continue to next thread — **never** fail the entire tracker run.

**The tracker ALWAYS completes. Bridge failure is non-fatal.**

#### Step 4: Generate Document

Write the full tracker document to `artifacts/review-tracker/tracker-{change-number}.md`.

Follow this section order exactly:

```markdown
# Review {number} — Live Comment Tracker

**Review:** [{gerrit URL}]({gerrit URL})
**Title:** {subject}
**Author:** {owner}
**Status:** {status}
**Current Patchset:** {number}
**Zuul:** {Verified vote status}
**Files Changed:** {count} ([`file1.py:line`](https://github.com/openstack/horizon/blob/master/file1.py#Lline), [`file2.py`](https://github.com/openstack/horizon/blob/master/file2.py))
**Reviewers:** {list of reviewers who commented}

---

## Initial Code Review

{If bridge ran successfully in Step 0.7:}

**Performed by:** `/horizon-code-review` (automated bridge)
**Verdict:** {verdict from bridge: APPROVE / REQUEST_CHANGES / COMMENT}
**Full Analysis:** [Code Review](bridge-artifacts/initial-review-{number}.md)

### Summary
{summary extracted from bridge output}

### Blockers
{blockers list from bridge, or "None"}

### Suggestions
{suggestions list from bridge, or "None"}

{If bridge failed:}

**Status:** Unavailable -- bridge to `/horizon-code-review` failed.
Run `/horizon-code-review {number}` manually for code analysis.

{If not first run (recheck): omit this section entirely.}

---

## Scan Log

| # | Date | Scanner | Notes |
|---|------|---------|-------|
| 1 | {today} | AI (Claude) | Initial scan — {N} comment threads from {M} reviewers |

---

## What Needs to Change

This section gives concrete, code-level guidance for every open blocking comment.
Each entry is tied to a scan — new entries accumulate on recheck, resolved ones
get strikethrough.

### Scan #1 — {date}

**{CMT-XXX-N}: {one-line problem statement}**

- **File:** `{path}:{line}`
- **What the code does now:** {describe current behavior with a code snippet}
- **What the reviewer wants:** {describe the requested change precisely}
- **Suggested fix:**
  ```python
  # before
  {current code}

  # after
  {proposed fix}
  ```
- **Why:** {1-2 sentences on the reviewer's reasoning}

{Repeat for each open blocking comment}

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

8. Update "What Needs to Change":
   - Add a new `### Scan #N` sub-section for any new blocking comments
   - Strikethrough entries whose threads are now RESOLVED
   - If a reviewer replied to clarify or change their request, add an updated entry under the new scan

---

### Create Patch Mode

Reads the "What Needs to Change" section from the existing tracker, checks out
the Gerrit review, and applies the suggested fixes. The developer reviews the diff
and pushes manually.

**CRITICAL:** This mode NEVER executes `git review`, `git push`, or any command
that publishes changes to a remote. See rules.md NEVER-PUSH rule.

#### Step C1: Validate Prerequisites

1. Verify tracker artifact exists: `artifacts/review-tracker/tracker-{number}.md`
   - If missing: report "Run `/review-tracker {number}` first to create the tracker." and STOP
2. Parse the tracker to extract:
   - Current patchset number from the `**Current Patchset:**` line
   - Gerrit project path from the `**Review:**` URL (e.g., `openstack/horizon`)
   - All entries under `## What Needs to Change`
3. Filter to only non-strikethrough entries (entries wrapped in `~~...~~` are resolved)
   - If no open entries: report "All 'What Needs to Change' entries are resolved. Nothing to patch." and STOP

#### Step C2: Parse Fix Entries

For each open entry in "What Needs to Change":

1. Extract `file_path` from the `**File:**` line (format: `` `path:line` ``)
2. Extract the `# before` and `# after` code blocks from the `**Suggested fix:**` section
3. Record the thread ID (e.g., `CMT-JAN-1`) from the entry heading
4. If no before/after blocks found: mark as "manual intervention required" (skip this entry)

#### Step C3: Locate or Clone the Review

Compute paths using the same clone root as Step 0.6:

```
if clone_at is set:
    CLONE_ROOT = clone_at
elif REVIEW_CLONE_ROOT env var is set:
    CLONE_ROOT = REVIEW_CLONE_ROOT
else:
    CLONE_ROOT = IPROJECT_ROOT/projects/review_{number}/reviews
```

```
CHECKOUT_DIR = ${CLONE_ROOT}/horizon-review-${number}
LAST2 = number % 100, zero-padded to 2 digits
```

Check for existing checkout:

- If `CHECKOUT_DIR` exists:
  - Run `git status --porcelain` inside it
  - If output is non-empty (dirty): report the dirty state, show `git status --short`, and STOP (No Clobber Rule)
  - If clean: report "Reusing existing clean checkout" and skip to Step C4

Clone and checkout the patchset:

```bash
git clone "https://review.opendev.org/${PROJECT}" "${CHECKOUT_DIR}"
cd "${CHECKOUT_DIR}"
git fetch origin "refs/changes/${LAST2}/${number}/${N}"
git checkout FETCH_HEAD
```

#### Step C4: Apply Fixes

For each parsed fix entry from Step C2, working in `${CHECKOUT_DIR}`:

1. Read the target file at `fix.file_path`
2. Search for the `before` code block (fuzzy whitespace matching — strip leading whitespace for comparison, preserve original indentation)
3. If found: replace with `after` code block, preserving surrounding indentation. Set status = `APPLIED`
4. If not found, check if `after` code already exists in the file:
   - If yes: set status = `ALREADY_APPLIED` (skip)
   - If no: set status = `NOT_FOUND` (warning — file may have changed since tracker scan)

Use the Edit tool to make the replacements — same as normal file editing.

#### Step C5: Stage and Amend

Only if at least one fix was applied (status = `APPLIED`):

```bash
cd "${CHECKOUT_DIR}"
git add -A
git commit --amend --no-edit
```

If no fixes were applied (all skipped or not found): report the situation and STOP without amending.

**Do NOT run `git review` or `git push`. EVER.**

#### Step C6: Generate Patch Manifest

Write `${CHECKOUT_DIR}/PATCH_MANIFEST.md`:

```markdown
# Patch Manifest — Review {number} PS{N}

**Generated:** {YYYY-MM-DD HH:MM UTC}
**Tracker:** tracker-{number}.md (Scan #{last_scan_number})
**Base Patchset:** PS{N}
**Commit:** {short SHA after amend}

## Applied Fixes

| # | Thread | File | Line | Status |
|---|--------|------|------|--------|
| 1 | {thread_id} | `{file}` | {line} | {APPLIED/ALREADY_APPLIED/NOT_FOUND} |

## Skipped (Manual Intervention Required)

{Table of entries with status NOT_FOUND or no before/after blocks, or "None"}

## How to Review

    cd {checkout_path}
    git diff HEAD~1
    git log -1

## How to Push (YOUR DECISION)

    cd {checkout_path}
    git review

> **WARNING:** Only push after you have reviewed the diff and confirmed the changes.
> This automation does NOT push for you. That decision is yours.
```

#### Step C7: Report

Print a summary to the developer:

```
--create-patch complete for review {number}:

  Checkout:  {checkout_path}
  Applied:   {N} fixes ({thread_ids})
  Skipped:   {N} ({reasons if any})

  Review:    cd {checkout_path} && git diff HEAD~1
  Push:      cd {checkout_path} && git review  (YOUR DECISION)

  Manifest:  {checkout_path}/PATCH_MANIFEST.md
```

---

### Verify Patch Mode

Runs tox-based linting and unit tests against the patched checkout to verify
the fixes don't break anything before the developer pushes.

#### Step V1: Locate or Create Checkout

Compute paths using the same clone root:

```
CLONE_ROOT = same as Step 0.6 / Step C3
PATCH_DIR = ${CLONE_ROOT}/horizon-review-${number}
VERIFY_DIR = ${CLONE_ROOT}/horizon-review-${number}-verify
```

Three scenarios:

1. **`--create-patch` ran first in this invocation:** `PATCH_DIR` exists and is fresh.
   Copy it:
   ```bash
   mkdir -p "${VERIFY_DIR}"
   cp -r "${PATCH_DIR}" "${VERIFY_DIR}/horizon-checkout"
   ```

2. **`--verify-patch` alone, `PATCH_DIR` exists from prior run:** Same copy.

3. **`--verify-patch` alone, no patch checkout:** Clone fresh from Gerrit and apply
   fixes from the tracker (same steps as C3 + C4):
   ```bash
   mkdir -p "${VERIFY_DIR}"
   git clone "https://review.opendev.org/${PROJECT}" "${VERIFY_DIR}/horizon-checkout"
   cd "${VERIFY_DIR}/horizon-checkout"
   git fetch origin "refs/changes/${LAST2}/${number}/${N}"
   git checkout FETCH_HEAD
   # Apply fixes from tracker "What Needs to Change" (same as C4)
   ```

If `VERIFY_DIR` already exists with prior reports: report "Prior verify run found.
Re-running will overwrite reports." and proceed (verify is safe to re-run).

Create reports directory:
```bash
mkdir -p "${VERIFY_DIR}/reports"
```

#### Step V2: Identify Test Suites

Parse the review's changed files (from the tracker header or Gerrit API) and map
to test suites:

| File pattern | Suite | Command |
|---|---|---|
| Any `.py` file | PEP8 | `tox -e pep8` |
| `openstack_dashboard/test/` | Unit tests | `tox -e py311` |
| `openstack_dashboard/dashboards/{panel}/` | Panel tests | `tox -e py311 -- openstack_dashboard/dashboards/{panel}/tests.py` |
| `openstack_dashboard/api/` | API tests | `tox -e py311 -- openstack_dashboard/test/api_tests/` |
| `horizon/` | Framework tests | `tox -e py311 -- horizon/test/` |

Always include `tox -e pep8` (mandatory lint gate).

#### Step V3: Run Tests

Run each suite sequentially, capturing output:

```bash
cd "${VERIFY_DIR}/horizon-checkout"

tox -e pep8 2>&1 | tee "${VERIFY_DIR}/reports/tox-pep8.log"
# Record exit code

tox -e py311 2>&1 | tee "${VERIFY_DIR}/reports/tox-py311.log"
# Record exit code
```

Report progress as each suite completes:
```
  [1/2] tox -e pep8 ... PASS (42s)
  [2/2] tox -e py311 ... PASS (3m 8s)
```

Timeout: if any command runs longer than 30 minutes, kill it and record verdict = TIMEOUT.

#### Step V4: Extract Failure Details

For any suite with non-zero exit code:

1. Read the last 80 lines of the log file
2. Extract error summary lines (PEP8 violations, FAILED markers, tracebacks)
3. Limit to 20 lines max for the report

#### Step V4a-V4e: Playwright Verify (Optional)

This step deploys the review code to the DevStack VM, starts a dev server with the
correct feature flags, generates a targeted Playwright browser test, and runs it.
It is OPTIONAL — if no DevStack VM is available, skip with a note and proceed to V5.

This follows the same deploy-to-VM pattern as the `/verify` skill: SSH into the VM,
clone the review, configure `ANGULAR_FEATURES`, run `tox -e runserver`, and port-forward
the dev server port. The dev server serves at `/` root (no `/dashboard/` prefix).

**V4a: Check VM Availability and Deploy Review Code**

Check for a DevStack VM:
1. `--horizon-url` flag value → if provided, skip VM deployment and use directly
2. `HORIZON_URL` environment variable → same
3. If neither: attempt VM deployment using the DevStack VM (see below)
4. If VM deployment not possible: report "Playwright verify skipped — no Horizon URL
   and no DevStack VM. Pass --horizon-url or set HORIZON_URL to enable browser testing."
   and skip to V5.

**VM Deployment (matching /verify skill pattern):**

```bash
# 1. SSH into the DevStack VM
ssh stack@${VM_IP}

# 2. Clone the review code
cd /opt/stack
git clone https://review.opendev.org/${PROJECT} horizon-review-${number}
cd horizon-review-${number}
LAST2=$(printf "%02d" $((${number} % 100)))
git fetch origin refs/changes/${LAST2}/${number}/${PATCHSET}
git checkout FETCH_HEAD

# 3. Configure feature flags for the review
# Determine which ANGULAR_FEATURES flags need toggling based on the review's purpose.
# For de-angularization reviews (like 992714), disable the Angular panel:
cat > openstack_dashboard/local/local_settings.d/_9999_custom.py << 'SETTINGS'
ANGULAR_FEATURES = {
    'key_pairs_panel': False,  # Use Django panel from this review
}
SETTINGS

# 4. Start the dev server (serves at / root, NOT /dashboard/)
tox -e runserver -- 0.0.0.0:9000 &
# Wait for startup
sleep 10

# 5. Set up iptables redirect so Keystone works on the dev server
# (Keystone is behind Apache on port 80; dev server needs to reach it)
sudo iptables -t nat -A OUTPUT -p tcp -d 127.0.0.1 --dport 80 -j REDIRECT --to-port 5080
```

From the laptop, port-forward the dev server:
```bash
virtctl port-forward vm/${VM} 9000:9000 -n ${NAMESPACE}
```

Set `HORIZON_URL=http://localhost:9000`.

Verify the URL is reachable:
```bash
curl -s -o /dev/null -w "%{http_code}" "${HORIZON_URL}/auth/login/" 2>/dev/null
```
If not reachable: report and skip to V5.

**V4b: Generate Playwright Test Script**

Based on the tracker's "What Needs to Change" entries, generate a standalone Python script
at `{checkout_dir}/playwright_verify.py`. The script must:

1. Be self-contained (only imports: `playwright.async_api`, `asyncio`, `json`, `sys`, `os`, `pathlib`)
2. Accept `--url` argument for the Horizon URL (default: `http://localhost:9000`)
3. Read credentials from `HORIZON_USER`/`HORIZON_PASSWORD` env vars (default: admin/secret)
4. Login → navigate to the affected panel → exercise the flows affected by the fix
5. Capture screenshots at each assertion point to `playwright_results/screenshots/`
6. Write structured results to `playwright_results/results.json`
7. Exit 0 if all tests pass, 1 if any fail

**IMPORTANT:** The dev server serves at `/` root. All paths use `/auth/login/`,
`/project/key_pairs/`, etc. — NOT `/dashboard/auth/login/`. The `/dashboard/` prefix
is only used by Apache's WSGI configuration.

**Panel identification from file paths:**
- `key_pairs/` or `test_keypairs` → Key Pairs panel at `/project/key_pairs/`
- `instances/` → Instances at `/project/instances/`
- `networks/` → Networks at `/project/networks/`
- `volumes/` → Volumes at `/project/volumes/`
- `images/` → Images at `/project/images/`

**Fix-to-test mapping:**
- Create assertion fix → generate create flow + toast message verification
- Delete assertion fix → generate delete flow + toast message verification
- Table/column fix → generate panel load + column verification
- Form field fix → generate form open + field verification

Use multiple CSS selector alternatives for Angular/Python panel variations, following
the patterns from the `/verify` skill recipes.

**V4c: Install Playwright (if needed)**

```bash
python3 -c "import playwright" 2>/dev/null || pip install playwright --quiet
python3 -m playwright install chromium --with-deps 2>/dev/null || \
    python3 -m playwright install chromium 2>/dev/null
```
If installation fails: report and skip to V5.

**V4d: Run Test Script**

```bash
cd {checkout_dir}
python3 playwright_verify.py --url "${HORIZON_URL}" 2>&1
```
Record exit code and parse `playwright_results/results.json`.

**V4e: Collect Results and Clean Up**

Read results.json and incorporate into the verify report. Copy the generated script
to artifacts:
```bash
cp {checkout_dir}/playwright_verify.py \
   artifacts/review-tracker/playwright-verify-{number}.py
```

Clean up the VM dev server (if deployed in V4a):
```bash
# On the VM: stop the dev server and remove iptables redirect
ssh stack@${VM_IP} "pkill -f 'runserver.*9000'; \
    sudo iptables -t nat -D OUTPUT -p tcp -d 127.0.0.1 --dport 80 -j REDIRECT --to-port 5080 2>/dev/null"
```

---

#### Step V5: Generate Verify Report

Write `${VERIFY_DIR}/reports/verify-report.md`:

```markdown
# Verify Report — Review {number} PS{N}

**Generated:** {YYYY-MM-DD HH:MM UTC}
**Checkout:** {verify_dir}/horizon-checkout/
**Patches Applied:** {count} from tracker-{number}.md
**Overall Verdict:** {PASS / FAIL / PARTIAL}

---

## Test Results

| # | Suite | Command | Exit Code | Duration | Verdict |
|---|-------|---------|-----------|----------|---------|
| 1 | PEP8 | `tox -e pep8` | {code} | {duration} | {PASS/FAIL} |
| 2 | Unit Tests | `tox -e py311` | {code} | {duration} | {PASS/FAIL} |

---

## Failure Details

{For each failed suite: heading, exit code, log path, error summary}

---

## Patches Applied

| # | Thread | File | Change |
|---|--------|------|--------|
| 1 | {thread_id} | `{file}:{line}` | {brief description} |

---

## Next Steps

{If PASS: "All tests passed. Review the diff and push when ready:
    cd {patch_dir} && git review  (YOUR DECISION)"}
{If FAIL: "Fix the failing tests before pushing. See details above."}

---

## Playwright Verify

{If Playwright ran:}

**Horizon URL:** {url}
**Script:** `playwright_verify.py`
**Tests:** {pass_count} passed, {fail_count} failed

| # | Test | Result | Details |
|---|------|--------|---------|
{table of Playwright test results}

### Screenshots

| Step | Screenshot |
|------|-----------|
{table of screenshot paths}

{If Playwright skipped:}

**Status:** SKIPPED — No Horizon URL provided.
Set `HORIZON_URL` or pass `--horizon-url` to enable browser testing.

---

## Raw Logs

- PEP8: `{verify_dir}/reports/tox-pep8.log`
- Unit Tests: `{verify_dir}/reports/tox-py311.log`
- Playwright: `{checkout_dir}/playwright_results/results.json` (if run)
```

#### Step V6: Report

Print a summary:

```
--verify-patch complete for review {number} (PS{N} + tracker fixes):

  Workspace:  {verify_dir}/
  PEP8:       {PASS/FAIL} ({duration})
  Unit Tests: {PASS/FAIL} ({duration})
  Verdict:    {PASS/FAIL}

  Full report: {verify_dir}/reports/verify-report.md
  Push when ready: cd {patch_dir} && git review  (YOUR DECISION)
```

---

### Final Report Mode

Generates a comprehensive post-merge assessment document with quantitative metrics,
timeline analysis, reviewer engagement profiles, and honest self-assessment. This mode
produces a standalone document suitable for sharing with management and colleagues.

**Prerequisites:**
- Review status must be MERGED
- Tracker artifact must exist at `artifacts/review-tracker/tracker-{number}.md`

#### Step F1: Validate Prerequisites

1. Fetch review status from Gerrit:
   ```
   GET https://review.opendev.org/changes/{change-id}
   ```
   If `status` != `MERGED`: report "Review {number} is not yet merged
   (status: {status}). Final reports are generated after merge." and STOP.

2. Check tracker artifact exists:
   `artifacts/review-tracker/tracker-{number}.md`
   If missing: report "Run `/review-tracker {number}` first to create
   the tracker." and STOP.

3. Read the existing tracker artifact for thread data and scan history.

#### Step F2: Fetch Complete Gerrit Data

Make two API calls:

```
GET /changes/{change-id}/detail?o=DETAILED_LABELS&o=ALL_REVISIONS&o=MESSAGES
GET /changes/{change-id}/comments
```

From the detail response, extract:
- All patchsets with `_number`, `created`, `kind`, `description`, `uploader`
- All messages with `date`, `author`, `tag`, `message`
- All label votes with `date`, `value`, `name`
- `created`, `updated`, `submitted` timestamps

From the comments response, extract:
- All comments with `author`, `updated`, `message`, `unresolved`, `in_reply_to`
- Group into threads using the same algorithm as initial scan

#### Step F3: Compute Metrics

Calculate these metrics from the raw data:

**Timeline Metrics:**
| Metric | Computation |
|--------|-------------|
| Total duration | `submitted` - `created` (in days) |
| Development phase | First push to first CI pass |
| Idle time | Longest gap between consecutive patchsets |
| Review wait time | Marked ready for review to first reviewer comment |
| Post-feedback time | First reviewer comment to merge |

**Patchset Metrics:**
| Metric | Computation |
|--------|-------------|
| Total patchsets | Count of all revisions |
| REWORK count | Count where `kind` = "REWORK" |
| TRIVIAL_REBASE count | Count where `kind` contains "REBASE" |
| NO_CODE_CHANGE count | Count where `kind` = "NO_CODE_CHANGE" |

**Comment Metrics:**
| Metric | Computation |
|--------|-------------|
| Total comments | Count of all non-CI comments |
| Unique reviewers | Count of distinct comment authors (excluding owner) |
| Blocking comments | Count of threads with severity HIGH |
| Response time per thread | First reply timestamp - root comment timestamp |
| Median response time | Median of all response times |

**CI Metrics:**
| Metric | Computation |
|--------|-------------|
| Total CI runs | Count of Zuul Verified messages |
| Pass rate | Pass count / Total CI runs |
| Recheck count | Count of "recheck" patchset-level comments |

#### Step F4: Determine Patchset Reasoning

For each patchset, determine the reason:

1. If `kind` = "REWORK" and it's PS1: "Initial implementation"
2. If `kind` = "REWORK" and prior PS had Verified-1: "Fix CI failures"
3. If `kind` = "REWORK" and prior PS had Code-Review with comments: "Address reviewer feedback"
4. If `kind` = "TRIVIAL_REBASE": "Rebase on latest master"
5. If `kind` = "NO_CODE_CHANGE": "Commit message update"
6. If `kind` = "TRIVIAL_REBASE_WITH_MESSAGE_UPDATE": "Rebase + commit message update"

Group patchsets into phases:
- **Development phase:** PS1 through first Verified+1
- **Stabilization phase:** Rebases and commit message updates before first review
- **Review response phase:** Patchsets addressing reviewer feedback
- **Final phase:** Last patchset(s) leading to merge

#### Step F5: Generate Lessons Learned

Analyze the data for honest self-assessment:

**What Went Well — look for:**
- Fast response to reviewer comments (< 24h)
- Clear commit messages
- Reviewer engagement (multiple reviewers, devstack testing)

**What Could Improve — look for:**
- Multiple CI failures before first pass
- Long gaps between patchsets (> 5 days)
- Slow response to comments (> 3 days)

#### Step F6: Generate Final Report Document

Write the complete report to `artifacts/review-tracker/final-report-{number}.md`
with these sections in order:

1. Header (review URL, author, final status, total patchsets, duration, comment count)
2. Executive Summary (2-3 paragraphs)
3. Review Timeline (chronological table of all events)
4. Patchset History (table + narrative by phase)
5. Reviewer Engagement (per-reviewer analysis)
6. Comment Thread Analysis (all threads with response times)
7. Response Time Metrics (median, mean, fastest, slowest)
8. CI Performance (per-patchset results + summary)
9. Code Evolution Metrics (rework vs rebase vs message-only counts)
10. AI-Assisted Tracking Summary (scan history, capabilities exercised)
11. Key Milestones (first push, first CI pass, first review, merge)
12. Lessons Learned (What Went Well, What Could Improve, Patterns to Repeat)
13. Appendix: Vote History

All URLs must be clickable markdown links (per rules.md).

#### Step F7: Report and Continue

Print summary to the user:
```
--final-report complete for review {number}:

  Artifact:  artifacts/review-tracker/final-report-{number}.md
  Duration:  {days} days ({first_push} to {merge_date})
  Patchsets: {N} ({rework} reworks, {rebase} rebases)
  Threads:   {N} ({blocking} blocking)
  Reviewers: {N}
```

If `publish_after` is set, proceed to Publish Mode (Step P1).

---

### Publish Mode — Update Artifact Dashboard

This mode publishes the current tracker artifact to the ioshaworkflow dashboard.
It runs after the primary mode completes (or standalone if the tracker already exists).

#### Step P1: Locate Paths

Compute these paths from the workflow root:

- **Source artifact:** `artifacts/review-tracker/tracker-{number}.md`
- **Ingest script:** Walk up from the workflow root to find the sibling `ioshaworkflow/` repo,
  then use `scripts/ingest_artifacts.py`
- **Dashboard data root:** `{ioshaworkflow_repo}/data/investigations/`

If the source artifact does not exist, report "No tracker artifact found. Run the skill
without `--update-artifact-dashboard` first." and STOP.

#### Step P2: Check for Changes

Build the rename map. Start with the tracker, then add patch/verify artifacts if they exist:

```python
rename_map = {'tracker-{number}.md': 'tracker.md'}

# If --create-patch produced a manifest, copy it to artifacts and add to rename_map
patch_manifest = '{repo_root}/review-{number}-ps{N}/PATCH_MANIFEST.md'
if os.path.exists(patch_manifest):
    shutil.copy(patch_manifest, 'artifacts/review-tracker/patch-manifest-{number}.md')
    rename_map['patch-manifest-{number}.md'] = 'patch-manifest.md'

# If --verify-patch produced a report, copy it to artifacts and add to rename_map
verify_report = '{repo_root}/review-{number}-ps{N}-verify/reports/verify-report.md'
if os.path.exists(verify_report):
    shutil.copy(verify_report, 'artifacts/review-tracker/verify-report-{number}.md')
    rename_map['verify-report-{number}.md'] = 'verify-report.md'

# If --final-report produced a report, add to rename_map
final_report = 'artifacts/review-tracker/final-report-{number}.md'
if os.path.exists(final_report):
    rename_map['final-report-{number}.md'] = 'final-report.md'
```

Run the change detection:

```bash
cd {ioshaworkflow_repo} && python3 -c "
import sys; sys.path.insert(0, 'scripts')
from ingest_artifacts import check_for_new_artifacts
result = check_for_new_artifacts(
    'REVIEW-TRACKER-{number}',
    'review-tracker',
    skill_type='review-tracker',
    source_project_variant='openstack-horizon-agentic-workflows-review-tracker',
    rename_map={rename_map}
)
print(result)
"
```

If `has_new` is `False`: report the message (e.g., "Nothing new to publish — artifacts
unchanged since run-002") and STOP. Do not create a duplicate run.

#### Step P3: Ingest

Extract metadata from the tracker document header:
- **title**: The `**Title:**` line value
- **summary**: Construct from header: "Gerrit {number}: {title}. {thread_count} threads, PS{ps}, {status}."

Run the ingestion:

```bash
python3 {ioshaworkflow_repo}/scripts/ingest_artifacts.py \
    REVIEW-TRACKER-{number} \
    review-tracker \
    review-tracker \
    --title "{title}" \
    --summary "{summary}" \
    --skill-type review-tracker \
    --source-project-variant openstack-horizon-agentic-workflows-review-tracker \
    --rename "tracker-{number}.md:tracker.md"
```

#### Step P4: Report

Report to the user:
- The new run ID (e.g., run-001)
- The dashboard URL: `http://10.0.151.101:8072/investigations/REVIEW-TRACKER-{number}?run={run_id}`
- What changed (from the check result message)

---

## Output

Write the tracker to:

```
artifacts/review-tracker/tracker-{change-number}.md
```

This file is both the output artifact and the state for future rechecks.
