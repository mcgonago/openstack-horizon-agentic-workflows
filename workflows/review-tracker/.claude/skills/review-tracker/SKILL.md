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
- A change number with `--repo-path PATH` flag (use existing repo checkout, skip cloning)
- A change number with `--update-feature PATH` flag (apply code changes from external design/implementation docs)

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
/review-tracker 998960 --repo-path /path/to/existing/horizon/checkout --create-patch --verify-patch
/review-tracker 986478 --update-feature /path/to/IOSHAWORKFLOW_REVIEW_986478_ADD_VISIBILITY_OWNER
/review-tracker 986478 --update-feature /path/to/FEATURE_BASE --verify-patch
/review-tracker 986478 --update-feature /path/to/FEATURE_BASE --verify-patch --update-artifact-dashboard
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
   - `--follow-up`: set `follow_up = true`
   - `--produce-jira`: set `produce_jira = true`
   - `--osprh NUMBER`: set `parent_osprh = NUMBER`
   - `--horizon-url URL`: set `horizon_url = URL` (enables Playwright browser testing)
   - If `horizon_url` not set by flag, check `HORIZON_URL` env var. If not set, Playwright step is skipped.
   - `--clone-at PATH`: set `clone_at = PATH`
   - If `clone_at` not set by flag, check `REVIEW_CLONE_ROOT` env var.
   - If neither set, use default: `IPROJECT_ROOT/projects/review_{number}/reviews/`
     where `IPROJECT_ROOT = /home/omcgonag/Work/mymcp/workspace/iproject`
   - `--repo-path PATH`: set `repo_path = PATH`
     Use an existing repository checkout instead of cloning. The repo must be a Horizon checkout.
     When set, skips Step 0.6 (clone) entirely. `--create-patch` and `--verify-patch` will use this path.
     **IMPORTANT**: The existing repo must be clean (no uncommitted changes) and on a branch.
     The skill will `git fetch` the review patchset and checkout FETCH_HEAD.
   - `--update-feature PATH`: set `update_feature = true`, set `feature_path = PATH`
     PATH is the base path without `_DESIGN.md` / `_IMPLEMENTATION.md` suffixes.
     Both `{PATH}_DESIGN.md` and `{PATH}_IMPLEMENTATION.md` must exist.

3. **Determine primary mode**:
   - If `--status` flag: print current header + Open Threads table from existing tracker, STOP
     (all other flags are ignored with `--status`)
   - If `--final-report` flag: go to **Final Report Mode** (Step F1)
     - Requires review status = MERGED. If not MERGED, report error and STOP.
     - Requires existing tracker artifact. If missing, report error and STOP.
   - If `--recheck` flag: go to **Recheck Mode** (Step R1)
   - Otherwise: check if `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/tracker-{number}.md` exists
     - If exists AND no action flags: tell the user "Tracker already exists. Use `--recheck` to update, or `--force` to regenerate from scratch."
     - If exists: proceed to post-primary actions
     - If not exists: go to **Bootstrap and Initial Scan Mode**:
       1. Run **Step 0.5: Bootstrap Review Project** (if using default path)
       2. Run **Step 0.6: Clone Review Code**
       3. Run **Step 0.7: Initial Code Review Bridge**
       4. Then proceed to **Initial Scan Mode** (Step 1)
       5. Set `publish_after = true` (auto-publish on first run)

4. **Post-primary-mode actions** (in order):
   - If `follow_up`: go to **Follow-Up Mode** (Step FU1)
   - If `produce_jira`: go to **Produce Jira Mode** (Step PJ1)
   - If `update_feature`: go to **Update Feature Mode** (Step U1)
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
- `--repo-path` was provided (user providing existing checkout)
- `REVIEW_CLONE_ROOT` env var is set
- Project directory already exists

#### Step 0.6: Clone Review Code

**If `repo_path` is set (--repo-path flag):**

Use the provided repository path directly:

```
CLONE_DIR = repo_path
LAST2 = number % 100, zero-padded to 2 digits
PROJECT = Gerrit project path (e.g., openstack/horizon)
PATCHSET = current patchset number from Gerrit API
```

Validate and fetch the review patchset:

```bash
cd "${CLONE_DIR}"

# Verify it's a git repo
if [ ! -d .git ]; then
    echo "ERROR: ${CLONE_DIR} is not a git repository"
    STOP
fi

# Check for dirty state
if [ -n "$(git status --porcelain)" ]; then
    echo "WARNING: Existing repo has uncommitted changes:"
    git status --short
    echo ""
    echo "Clean up the checkout before proceeding."
    STOP
fi

# Fetch and checkout the review patchset
echo "Using existing repo at ${CLONE_DIR}"
git fetch origin "refs/changes/${LAST2}/${number}/${PATCHSET}"
git checkout FETCH_HEAD
```

**Otherwise (no --repo-path flag):**

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
mkdir -p workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/bridge-artifacts
cp artifacts/horizon-review/code-${number}.md \
   workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/bridge-artifacts/initial-review-${number}.md
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

This step runs on BOTH initial scan and `--recheck`. On recheck, run deep-dive for:

1. **NEW threads** — threads that did not exist in the previous scan
2. **UPDATED threads** — existing UNRESOLVED threads that received new replies since
   the last scan. A reviewer self-correcting or clarifying their own comment
   (reply in same thread, same author) changes the effective question and requires
   re-analysis. When an existing bridge artifact exists for an updated thread,
   **regenerate it** — the new reply may change the verdict and suggested response.
   Update the tracker's AI Assessment, Answer Summary, and Suggested Response
   sections for the thread accordingly.

Skip deep-dive for threads that are RESOLVED or have no new replies since the
last scan and already have a current bridge artifact.

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
workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/bridge-artifacts/{thread-id-lower}-analysis.md
```

Use this format (matching the `templates/code-archaeology-analysis.md.template`):

```markdown
# Bridge Analysis: {THREAD-ID}

**Reviewer:** {reviewer name}
**Review:** [{gerrit URL}]({gerrit URL})
**File:** [`{file}:{line}`](https://github.com/openstack/horizon/blob/master/{file}#L{line})

---

## Comment Evolution

{If the thread has a single comment (no self-correction):}

### Original Comment (PS{N}, {HH:MM} UTC)

> {full quoted comment text}

**Reviewer's ask:** {one-line summary of what they want}

{If the thread has a self-correction (reviewer replied to their own comment):}

### Original Comment (PS{N}, {HH:MM} UTC)

> {full quoted original comment text}

**Reviewer's ask:** {one-line summary of original ask}

### Self-Correction (PS{N}, {HH:MM} UTC)

> {full quoted self-correction text}

**Updated ask:** {one-line summary of what the reviewer is ACTUALLY asking now}

### What Changed

{Explain how the self-correction changes the question. State explicitly which
ask (original or updated) the analysis below addresses.}

{If this thread inherits a self-correction from another thread (e.g., "Same here"):}

### Original Comment (PS{N}, {HH:MM} UTC)

> {full quoted comment text}

**Reviewer's ask:** {one-line summary}

### Inherited Self-Correction

{Explain how a self-correction from another thread applies here, with a link
to the source thread's analysis.}

---

## Investigation

{Each analysis section begins with an italic line anchoring it to a specific
comment from the Comment Evolution section, e.g.:}

*Answers the updated question: "{quoted ask}"*

### 1. Where is `{attribute}` set?

**Source:** [`{source_file}:{source_line}`](https://github.com/openstack/horizon/blob/master/{source_file}#L{source_line})
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

> {ready-to-paste Gerrit reply — file refs stay plain text here, Gerrit doesn't render markdown}

---

## References

{list of clickable file:line references — every entry MUST use
[`path:line`](https://github.com/openstack/horizon/blob/master/path#Lline) format}
```

**IMPORTANT:** All file references in bridge artifacts MUST be clickable markdown
links per the Clickable URLs rule in rules.md. The ONLY exceptions are:
1. File references inside code blocks (``` ``` ```)
2. File references inside `> quoted` suggested responses (meant for Gerrit copy-paste)

**IMPORTANT — Source links on code blocks:** Every fenced code block that shows
code from a specific file MUST have a `**Source:**` line immediately before it
with a clickable GitHub link. A comment inside the code block (e.g.,
`# Volume panel pattern (volumes/tables.py)`) is NOT a substitute — comments
inside code blocks are not clickable. Format:

```markdown
**Source:** [`path/to/file.py:L1-L2`](https://github.com/openstack/horizon/blob/master/path/to/file.py#L1-L2)
```python
code here
```
```

This does NOT apply to generic illustrative snippets with no specific file
attribution, or code inside `> quoted` suggested responses.

Create the bridge-artifacts directory if it doesn't exist:

```bash
mkdir -p workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/bridge-artifacts
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

Write the full tracker document to `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{change-number}/tracker-{change-number}.md`.

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

| # | Timestamp | Scanner | Notes |
|---|-----------|---------|-------|
| 1 | {ISO 8601 UTC, e.g. 2026-07-15T16:30:00Z} | AI (Claude) | Initial scan — {N} comment threads from {M} reviewers |

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

Read the existing tracker document. Parse the Scan Log to find the timestamp of the most recent scan.

The Scan Log stores full ISO 8601 timestamps (e.g., `2026-07-15T15:40:00Z`). If parsing
an older tracker with day-only dates (e.g., `2026-07-15`), treat the date as `YYYY-MM-DDT00:00:00Z`
and always proceed to Step R2 (day-level comparison is too coarse for same-day rechecks).

Fetch the review's `updated` timestamp:

```
GET https://review.opendev.org/changes/{change-id}
```

If `updated` is not newer than the last scan timestamp: report "No changes since scan #N on {timestamp}. Review last updated {timestamp}." and STOP.

#### Step R2: Fetch Current State

Same API calls as Steps 1 and 2 of Initial Scan.

#### Step R3: Diff Against Documented State

Compare the fetched data against the existing document:

| What to check | How to detect |
|---------------|--------------|
| New comments | `updated` timestamp > last scan timestamp |
| Thread status changes | `unresolved` field differs from documented status |
| New patchset | Current PS number > documented PS number |
| Vote changes | Current label values differ from Score Summary |
| CI results | Verified label changed |
| New replies | Comments with `in_reply_to` pointing to documented threads |
| Updated threads | Existing thread received a new reply (same or different author) since last scan — the reply may change the question context, especially reviewer self-corrections |

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

**Exception — updated threads:** When an existing thread receives a new reply that changes
the effective question (e.g., a reviewer self-corrects or clarifies their original comment),
re-generate the AI assessment, update the Deep Dive section (if `--deep-dive`), and revise
the Suggested Response. A reviewer reply in the same thread by the same author is a strong
signal that the question context has shifted — always re-analyze these.

8. Update "What Needs to Change":
   - Add a new `### Scan #N` sub-section for any new blocking comments
   - Strikethrough entries whose threads are now RESOLVED
   - If a reviewer replied to clarify or change their request, add an updated entry under the new scan

#### Step R5: Deep-Dive Marker Protocol

After updating the tracker document on recheck, if any new OPEN threads
were detected that have:
- Status: POSTED — WAITING FOR RESPONSE or NEEDS YOUR RESPONSE
- Severity: HIGH (blocking comment with Code-Review -1)
- A code-archaeology or documentation question

Inform the user:

> {CMT-XXX-N} is a new blocking comment that may benefit from investigation.
> Say "investigate {CMT-XXX-N}" to start a deep-dive capture, or continue
> with other tasks.

When the user triggers an investigation (says "investigate", "deep dive",
"figure out", or similar):

1. Emit a `DEEP-DIVE-START` HTML comment marker with fields:
   `review`, `thread`, `topic`, `timestamp` (required); `run`, `file`,
   `reviewer` (optional).

2. Proceed with the investigation naturally — fetch diffs, search code,
   read docs, formulate responses.

3. When the investigation concludes (fix applied, response drafted, or user
   says "done"), emit a `DEEP-DIVE-END` HTML comment marker with fields:
   `review`, `thread`, `outcome`, `summary`, `timestamp`.

4. Inform the user that the deep dive is captured and can be extracted:

```
python3 ioshaworkflow/scripts/extract-deep-dive.py \
  --mirror-log ~/.claude/mirror-logs/claude-mirror-{today}.md \
  --review {number}
```

**IMPORTANT:** Do NOT emit markers during routine `--recheck` operations.
Markers are ONLY emitted when the user explicitly requests investigation.
See `rules.md` Deep-Dive Capture Protocol for the full marker format.

---

### Create Patch Mode

Reads the "What Needs to Change" section from the existing tracker, checks out
the Gerrit review, and applies the suggested fixes. The developer reviews the diff
and pushes manually.

**CRITICAL:** This mode NEVER executes `git review`, `git push`, or any command
that publishes changes to a remote. See rules.md NEVER-PUSH rule.

#### Step C1: Validate Prerequisites

1. Verify tracker artifact exists: `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/tracker-{number}.md`
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

**If `repo_path` is set (--repo-path flag):**

Use the provided repository directly (already checked out in Step 0.6):

```
CHECKOUT_DIR = repo_path
```

Skip to Step C4 (the repo is already on the correct patchset from Step 0.6).

**Otherwise:**

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

### Update Feature Mode

Reads an external design/implementation document pair, parses the code change
blocks from the implementation doc, and applies them to the Horizon checkout.
This mode is the doc-driven counterpart to `--create-patch` (which reads from
the tracker's "What Needs to Change" section).

**CRITICAL:** This mode NEVER executes `git review`, `git push`, or any command
that publishes changes to a remote. See rules.md NEVER-PUSH rule.

#### Step U1: Validate Prerequisites

1. Verify tracker artifact exists: `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/tracker-{number}.md`
   - If missing: report "Run `/review-tracker {number}` first to create the tracker." and STOP
2. Verify both feature documents exist:
   - `{feature_path}_DESIGN.md`
   - `{feature_path}_IMPLEMENTATION.md`
   - If either is missing: report "Missing document: {path}. Both _DESIGN.md and _IMPLEMENTATION.md are required." and STOP
3. Read the design document — extract:
   - Title from the `# ` heading
   - Thread reference (e.g., CMT-RAD-2) from the `**Thread:**` line or body
   - Summary of the change for the tracker update
4. Read the implementation document — this is the primary input for code changes

#### Step U2: Parse Code Changes

Parse the implementation document's `## 2. Code Changes` section.
For each `### Change N` subsection:

1. Extract `file_path` from the `**File:**` line (format: `` `path:line` `` or `` `path:line-line` ``)
2. Extract the `# before` and `# after` code blocks from the `**Code change:**` section
   (same parsing logic as create-patch's Step C2, but reading from `**Code change:**`
   instead of `**Suggested fix:**`)
3. Extract the `thread_id` from the `**Thread:**` line (if present)
4. Extract a brief description from the `**What needs to change:**` line
5. If no before/after blocks found: mark as "manual intervention required" (skip this entry)

Store as a list of change objects:

```
changes = [
    {
        "change_number": 1,
        "thread_id": "CMT-RAD-2",
        "file": "openstack_dashboard/dashboards/project/images/images/tables.py",
        "line": "206-210",
        "description": "Add visibility and owner to filter_choices",
        "before": "<the before code block>",
        "after": "<the after code block>",
        "status": "pending"
    },
    ...
]
```

#### Step U3: Locate or Clone the Review

Same path resolution as Step C3 (Create Patch Mode):

**If `repo_path` is set (--repo-path flag):**

```
CHECKOUT_DIR = repo_path
```

Skip to Step U4 (the repo is already on the correct patchset from Step 0.6).

**Otherwise:**

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
  - If clean: report "Reusing existing clean checkout" and skip to Step U4

Clone and checkout the patchset:

```bash
git clone "https://review.opendev.org/${PROJECT}" "${CHECKOUT_DIR}"
cd "${CHECKOUT_DIR}"
git fetch origin "refs/changes/${LAST2}/${number}/${N}"
git checkout FETCH_HEAD
```

#### Step U4: Apply Changes

For each parsed change from Step U2, working in `${CHECKOUT_DIR}`:

1. Read the target file at `change.file`
2. Search for the `before` code block (fuzzy whitespace matching — strip leading
   whitespace for comparison, preserve original indentation)
3. If found: replace with `after` code block, preserving surrounding indentation.
   Set status = `APPLIED`
4. If not found, check if `after` code already exists in the file:
   - If yes: set status = `ALREADY_APPLIED` (skip)
   - If no: set status = `NOT_FOUND` (warning — file may have changed since
     the implementation doc was written)

Use the Edit tool to make the replacements — same as Step C4.

#### Step U5: Stage and Amend

Only if at least one change was applied (status = `APPLIED`):

```bash
cd "${CHECKOUT_DIR}"
git add -A
git commit --amend --no-edit
```

If no changes were applied (all skipped or not found): report the situation
and STOP without amending.

**Do NOT run `git review` or `git push`. EVER.**

#### Step U6: Update Tracker Artifact

Read the existing tracker artifact and add a new section documenting what
was applied. Insert a `## Feature Updates` section before
`## Where Things Are At / What To Do Next` (or append to it if it already
exists from a prior `--update-feature` run):

```markdown
## Feature Updates

### {design_title} — {date}

**Source:** [{implementation_doc_basename}]({relative_path_to_implementation_doc})
**Design:** [{design_doc_basename}]({relative_path_to_design_doc})
**Threads Addressed:** {comma-separated thread IDs}

| # | File | Change | Status |
|---|------|--------|--------|
| 1 | `{file}:{line}` | {description} | {APPLIED/ALREADY_APPLIED/NOT_FOUND} |

**Checkout:** `{checkout_dir}`
**Commit:** `{short SHA after amend}`
```

Also update the tracker's "What Needs to Change" section:
- For each thread ID addressed by the feature update, if there is a matching
  open entry in "What Needs to Change", apply strikethrough to mark it resolved
- Add a note: "Resolved via `--update-feature` on {date}"

#### Step U7: Generate Feature Manifest

Write `${CHECKOUT_DIR}/FEATURE_MANIFEST.md`:

```markdown
# Feature Manifest — Review {number} PS{N}

**Generated:** {YYYY-MM-DD HH:MM UTC}
**Design:** {design_doc_path}
**Implementation:** {implementation_doc_path}
**Tracker:** tracker-{number}.md
**Base Patchset:** PS{N}
**Commit:** {short SHA after amend}

## Applied Changes

| # | Thread | File | Line | Description | Status |
|---|--------|------|------|-------------|--------|
| 1 | {thread_id} | `{file}` | {line} | {description} | {APPLIED/ALREADY_APPLIED/NOT_FOUND} |

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

#### Step U8: Report

Print a summary to the developer:

```
--update-feature complete for review {number}:

  Design:    {design_doc_path}
  Impl:      {implementation_doc_path}
  Checkout:  {checkout_path}
  Applied:   {N} changes ({descriptions})
  Skipped:   {N} ({reasons if any})

  Review:    cd {checkout_path} && git diff HEAD~1
  Push:      cd {checkout_path} && git review  (YOUR DECISION)

  Manifest:  {checkout_path}/FEATURE_MANIFEST.md
  Tracker:   Updated with Feature Updates section
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
   workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/playwright-verify-{number}.py
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
- Tracker artifact must exist at `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/tracker-{number}.md`

#### Step F1: Validate Prerequisites

1. Fetch review status from Gerrit:
   ```
   GET https://review.opendev.org/changes/{change-id}
   ```
   If `status` != `MERGED`: report "Review {number} is not yet merged
   (status: {status}). Final reports are generated after merge." and STOP.

2. Check tracker artifact exists:
   `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/tracker-{number}.md`
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

Write the complete report to `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/final-report-{number}.md`
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

  Artifact:  workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/final-report-{number}.md
  Duration:  {days} days ({first_push} to {merge_date})
  Patchsets: {N} ({rework} reworks, {rebase} rebases)
  Threads:   {N} ({blocking} blocking)
  Reviewers: {N}
```

If `publish_after` is set, proceed to Publish Mode (Step P1).

---

### Follow-Up Mode

Analyzes comment threads for deferred follow-up work and generates a structured artifact documenting items to be addressed in future changes.

#### Step FU1: Validate Prerequisites

1. **Check --osprh flag**: If `parent_osprh` not set, report:
   ```
   ERROR: --osprh flag required for follow-up mode.
   
   Usage: /review-tracker {number} --osprh {parent-ticket-number} --follow-up
   
   Example: /review-tracker 986458 --osprh 16426 --follow-up
   ```
   STOP.

2. **Validate parent ticket**: Call `mcp__user-jiraMcp__jira_get_issue` with key `OSPRH-{parent_osprh}`:
   - If found: extract `summary` for later use
   - If not found: report "Parent ticket OSPRH-{parent_osprh} not found. Verify ticket number." and STOP

3. **Verify tracker exists**: Check `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/tracker-{number}.md`
   - If missing: report "Run `/review-tracker {number}` first to create the tracker." and STOP

4. **Check for existing follow-up artifact**: Check `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/follow-up-{number}.md`
   - If exists: report artifact path and STOP with message "Follow-up artifact already exists. Delete it to regenerate."

5. **Read tracker**: Parse comment threads, statuses, and thread metadata

#### Step FU2: Analyze Comments for Deferred Work

For each comment thread in the tracker document:

1. **Check for deferral signals**:
   - Keywords: "follow-up", "followup", "explore this later", "in a future patch", "in a separate change", "TODO", "FIXME", "let's do that later", "sounds good for follow-up"
   - Thread status: RESOLVED with acceptance language

2. **Extract follow-up data if signals found**:
   - **Who suggested it**: Reviewer name from thread
   - **What it is**: Technical description from comment text
   - **Why deferred**: Reason from comment (consistency, scope, API limitation, blocker vs suggestion)
   - **File/line**: From thread metadata
   - **Bridge artifact link**: If available from deep-dive

3. **Classify each item**:
   - **Priority**: HIGH (blocking concern, deferred for scope) / MEDIUM (improvement) / LOW (nice-to-have)
   - **Type**: Technical Debt / Enhancement / Investigation

**Minimum threshold**: If fewer than 1 follow-up item found, report:
```
No follow-up work identified in review {number}.

All comment threads were either:
- Addressed in the review itself
- Not deferring work to future changes
- Informational only

No follow-up artifact created.
```
STOP.

#### Step FU3: Generate Follow-Up Artifact

Write `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/follow-up-{number}.md`:

```markdown
# Follow-Up Work — Review {number}

**Review:** [https://review.opendev.org/c/openstack/horizon/+/{number}](https://review.opendev.org/c/openstack/horizon/+/{number})
**Parent Jira:** [OSPRH-{parent_osprh}](https://redhat.atlassian.net/browse/OSPRH-{parent_osprh})
**Parent Summary:** {parent_summary from jira_get_issue}
**Generated:** {YYYY-MM-DD HH:MM UTC}
**Review Status:** {MERGED / IN REVIEW / ABANDONED}

---

## Summary

Review {number} ({review_subject}) identified {N} follow-up item(s) deferred during review discussions.

---

## Follow-Up Items

### Ticket {N} of {TOTAL}: {Concise Title}

**Suggested by:** {Reviewer Name}
**Thread:** [CMT-XXX-N](tracker-{number}.md#cmt-xxx-n)
**Priority:** {HIGH / MEDIUM / LOW}
**Type:** {Technical Debt / Enhancement / Investigation}

#### Panel 1: Copy/Paste for Jira Web UI (Plain English)

**Project:** OSPRH  
**Issue Type:** Story  
**Parent:** OSPRH-{parent_osprh}  
**Priority:** {High/Medium/Low}  
**Labels:** horizon, de-angularize, {technical-debt|ux-improvement}

**Summary:**
```
{Concise Jira title — under 100 chars}
```

**Description:**
```
{2-3 sentence summary from comment thread}

TECHNICAL DETAILS

Current state: {what the code does now}

Proposed change: {what the follow-up would do}

Files affected: {file paths with line ranges}

WHY DEFERRED

{Explanation from comment thread — e.g., "Deferred to maintain consistency with existing pattern", "Blocked by Glance API limitation", "Out of scope for this review"}

REFERENCES

Original review: https://review.opendev.org/c/openstack/horizon/+/{number}
Comment thread: CMT-XXX-N ({thread topic})
Reviewer acceptance: {quote or citation}
{If applicable: Related pattern/code references}
```

---

#### Panel 2: Copy/Paste for Jira Web UI (Jira Wiki Format)

**Project:** OSPRH  
**Issue Type:** Story  
**Parent:** OSPRH-{parent_osprh}  
**Priority:** {High/Medium/Low}  
**Labels:** horizon, de-angularize, {technical-debt|ux-improvement}

**Summary:**
```
{Concise Jira title — under 100 chars}
```

**Description:** (Copy this into Jira's description field - it will render nicely)
```
{2-3 sentence summary from comment thread}

h3. Technical Details

* Current state: {what the code does now — use |pipes| for inline code}
* Proposed change: {what the follow-up would do}
* Files affected: {file paths with :line notation}

h3. Why Deferred

{Explanation from comment thread}

h3. References

* Original review: https://review.opendev.org/c/openstack/horizon/+/{number}
* Comment thread: CMT-XXX-N ({thread topic})
* Reviewer acceptance: {quote or citation}
{If applicable: Related pattern/code references}
```

---

#### Panel 3: JSON Metadata for Automation

For use with Jira REST API or CLI tools. Requires `JIRA_USER` and `JIRA_TOKEN` environment variables.

**Using jira-cli tool:**
```bash
jira issue create \
  --type Story \
  --parent OSPRH-{parent_osprh} \
  --summary "{Concise Jira title}" \
  --body "$(cat <<'JIRA_BODY'
{FULL PLAIN ENGLISH DESCRIPTION FROM PANEL 1 — COMPLETE, NOT ABBREVIATED}

{Include ALL sections: summary, TECHNICAL DETAILS, WHY DEFERRED, REFERENCES}
{Use the exact same content as Panel 1, just without the markdown code fence}
JIRA_BODY
)" \
  --priority {High/Medium/Low} \
  --label horizon \
  --label de-angularize \
  --label {technical-debt|ux-improvement}
```

**Using curl with REST API:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -u "${JIRA_USER}:${JIRA_TOKEN}" \
  https://redhat.atlassian.net/rest/api/2/issue \
  -d @- <<'EOF'
{
  "fields": {
    "project": {"key": "OSPRH"},
    "issuetype": {"name": "Story"},
    "parent": {"key": "OSPRH-{parent_osprh}"},
    "summary": "{Concise Jira title}",
    "description": "{JIRA WIKI FORMAT FROM PANEL 2 — WITH h3. headers and |pipes| — use \\n for newlines}",
    "priority": {"name": "{High/Medium/Low}"},
    "labels": ["horizon", "de-angularize", "{technical-debt|ux-improvement}"]
  }
}
EOF
```

**Raw JSON metadata:**
```json
{
  "summary": "{Concise Jira title}",
  "description_plain": "{Plain English description from Panel 1}",
  "description_jira_wiki": "{Jira wiki format from Panel 2}",
  "priority": "{High/Medium/Low}",
  "labels": ["horizon", "de-angularize", "{technical-debt|ux-improvement}"],
  "parent_key": "OSPRH-{parent_osprh}",
  "suggested_by": "{Reviewer Name}",
  "tracker_thread": "CMT-XXX-N",
  "gerrit_review": "{number}"
}
```

---

{Repeat for each follow-up item}

---

## Notes

Each follow-up item above provides three formats for Jira ticket creation:

1. **Panel 1:** Plain English - copy/paste into Jira web UI
2. **Panel 2:** Jira Wiki Format - renders with nice formatting in Jira
3. **Panel 3:** CLI/API commands - ready-to-run automation

All three panels contain the same complete information. Use whichever method you prefer.

#### Step FU4: Report

Print summary to user:

```
--follow-up complete for review {number}:

  Parent Jira:   OSPRH-{parent_osprh} ({parent_summary})
  Artifact:      workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/follow-up-{number}.md
  Items found:   {N} follow-up items
  Suggested by:  {comma-separated list of reviewer names}

  Follow-up items:
  1. FU-{number}-1: {title} (Priority: {priority}, suggested by {reviewer})
  {... one line per item ...}

  Next steps:
  - Review the artifact at the path above
  - Run with --produce-jira to create Jira tickets:
    /review-tracker {number} --osprh {parent_osprh} --produce-jira
```

If `publish_after` is set, proceed to Publish Mode (Step P1).

---

### Produce Jira Mode

Creates Jira tickets from the follow-up artifact metadata. Requires credentials in environment variables.

#### Step PJ1: Validate Prerequisites

1. **Check follow-up artifact exists**: Look for `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/follow-up-{number}.md`
   - If missing: report "Run `/review-tracker {number} --osprh {N} --follow-up` first to generate follow-up artifact." and STOP

2. **Read artifact**: Load the markdown file

3. **Parse JSON metadata**: Extract the JSON block at the end (between ` ```json` and ` ``` `)
   - Parse as JSON
   - Extract `parent_jira`, `project_key`, `items[]`

4. **Validate credentials**: Check environment variables:
   - `JIRA_USER`: should be email address (e.g., `omcgonag@redhat.com`)
   - `JIRA_TOKEN`: API token (NOT password)
   - If either missing: report setup instructions and STOP:
     ```
     ERROR: Jira credentials not found.
     
     Set these environment variables:
       export JIRA_USER=your-email@redhat.com
       export JIRA_TOKEN=your-api-token
     
     To create an API token:
       https://id.atlassian.com/manage-profile/security/api-tokens
     ```

#### Step PJ2: Check for Existing Tickets

For each item in `items[]`:

1. **Extract search keywords** from `summary` (first 3-5 meaningful words)

2. **Search Jira** using `mcp__user-jiraMcp__jira_search_issues`:
   ```
   JQL: project = OSPRH AND summary ~ "{keywords}" AND parent = {parent_jira} AND status != Closed
   ```

3. **If found**: Mark item as "already exists" with ticket key, add to skip list

#### Step PJ3: Create Jira Tickets

For each item NOT in skip list:

**Use Jira REST API via curl** (jiraMcp doesn't expose create endpoint):

```bash
JIRA_USER="{from env}"
JIRA_TOKEN="{from env}"

curl -X POST \
  -H "Content-Type: application/json" \
  -u "${JIRA_USER}:${JIRA_TOKEN}" \
  https://redhat.atlassian.net/rest/api/2/issue \
  -d '{
    "fields": {
      "project": {"key": "{project_key}"},
      "summary": "{item.summary}",
      "description": "{item.description}",
      "issuetype": {"name": "{item.issue_type}"},
      "priority": {"name": "{item.priority}"},
      "labels": {item.labels},
      "parent": {"key": "{item.parent_key}"}
    }
  }'
```

**Parse response**:
- Success (HTTP 201): Extract `key` from JSON response (e.g., `OSPRH-12345`)
- Failure (HTTP 400/401/403): Log error, continue with next item
- Auth failure (HTTP 401): Report credential issue and STOP

**Rate limiting**: If response is HTTP 429, sleep 60s and retry once.

#### Step PJ4: Update Follow-Up Artifact

Append a new section to the artifact:

```markdown
---

## Jira Tickets Created

**Created:** {YYYY-MM-DD HH:MM UTC}

| Item | Jira Key | Status | URL |
|------|----------|--------|-----|
| FU-{number}-1 | OSPRH-XXXXX | Created | [OSPRH-XXXXX](https://redhat.atlassian.net/browse/OSPRH-XXXXX) |
| FU-{number}-2 | OSPRH-YYYYY | Already existed | [OSPRH-YYYYY](https://redhat.atlassian.net/browse/OSPRH-YYYYY) |
| FU-{number}-3 | (failed) | Error: {error message} | — |
```

#### Step PJ5: Report

Print summary to user:

```
--produce-jira complete for review {number}:

  Parent Jira:    OSPRH-{parent_osprh}
  Artifact:       follow-up-{number}.md (updated with Jira links)
  
  Results:
  - Created:      {N} new tickets
  - Already exist: {N} tickets
  - Failed:       {N} errors
  
  Tickets created:
  - OSPRH-XXXXX: {title}
  - OSPRH-YYYYY: {title}
  
  View parent and children:
  https://redhat.atlassian.net/issues/?jql=parent%3DOSPRH-{parent_osprh}
```

If `publish_after` is set, proceed to Publish Mode (Step P1).

---

### Publish Mode — Update Artifact Dashboard

This mode publishes the current tracker artifact to the ioshaworkflow dashboard.
It runs after the primary mode completes (or standalone if the tracker already exists).

#### Step P1: Locate Paths

Compute these paths from the workflow root:

- **Source artifact:** `workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/tracker-{number}.md`
- **Ingest script:** Walk up from the workflow root to find the sibling `ioshaworkflow/` repo,
  then use `scripts/ingest_artifacts.py`
- **Dashboard data root:** `{ioshaworkflow_repo}/data/investigations/`

If the source artifact does not exist, report "No tracker artifact found. Run the skill
without `--update-artifact-dashboard` first." and STOP.

#### Step P2: Check for Changes

Build the rename map. Start with the tracker, then add patch/verify artifacts if they exist.

**IMPORTANT:** Bridge artifacts from ALL reviews share one directory. The rename_map
controls which files the ingest script copies. Bridge artifacts MUST be listed explicitly
with a `bridge-artifacts/` prefix — unlisted files are skipped. This prevents artifacts
from other reviews bleeding into this review's dashboard entry.

```python
rename_map = {'tracker-{number}.md': 'tracker.md'}

# Add bridge artifacts for THIS review only.
# Scan bridge-artifacts/ for files that belong to this review:
#   - initial-review-{number}.md  (from Step 0.7 code review bridge)
#   - {thread-id}-analysis.md     (from --deep-dive, referenced in tracker)
# To find deep-dive files: parse the tracker for bridge-artifact links.
bridge_dir = 'workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}/bridge-artifacts'
initial_review = f'initial-review-{number}.md'
if os.path.exists(f'{bridge_dir}/{initial_review}'):
    rename_map[f'bridge-artifacts/{initial_review}'] = initial_review

# Find deep-dive analysis files referenced from the tracker document
for link in re.findall(r'bridge-artifacts/([\w-]+-analysis\.md)', tracker_content):
    if os.path.exists(f'{bridge_dir}/{link}'):
        rename_map[f'bridge-artifacts/{link}'] = link

# If --create-patch produced a manifest, copy it to artifacts and add to rename_map
patch_manifest = '{repo_root}/review-{number}-ps{N}/PATCH_MANIFEST.md'
artifact_dir = 'workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{number}'
if os.path.exists(patch_manifest):
    shutil.copy(patch_manifest, f'{artifact_dir}/patch-manifest-{number}.md')
    rename_map['patch-manifest-{number}.md'] = 'patch-manifest.md'

# If --verify-patch produced a report, copy it to artifacts and add to rename_map
verify_report = '{repo_root}/review-{number}-ps{N}-verify/reports/verify-report.md'
if os.path.exists(verify_report):
    shutil.copy(verify_report, f'{artifact_dir}/verify-report-{number}.md')
    rename_map['verify-report-{number}.md'] = 'verify-report.md'

# If --final-report produced a report, add to rename_map
final_report = f'{artifact_dir}/final-report-{number}.md'
if os.path.exists(final_report):
    rename_map['final-report-{number}.md'] = 'final-report.md'

# If --follow-up produced a follow-up artifact, add to rename_map
follow_up = f'{artifact_dir}/follow-up-{number}.md'
if os.path.exists(follow_up):
    rename_map['follow-up-{number}.md'] = 'follow-up.md'
```

Run the change detection:

```bash
cd {ioshaworkflow_repo} && python3 -c "
import sys; sys.path.insert(0, 'scripts')
from pathlib import Path
from ingest_artifacts import check_for_new_artifacts
workflows_root = Path('../openstack-horizon-agentic-workflows-review-tracker')
result = check_for_new_artifacts(
    'REVIEW-TRACKER-{number}',
    'review-tracker',
    skill_type='review-tracker/REVIEW-TRACKER-{number}',
    workflows_root=workflows_root,
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

Run the ingestion, passing ALL rename_map entries (including bridge artifacts) via `--rename`:

```bash
python3 {ioshaworkflow_repo}/scripts/ingest_artifacts.py \
    REVIEW-TRACKER-{number} \
    review-tracker \
    review-tracker \
    --title "{title}" \
    --summary "{summary}" \
    --skill-type "review-tracker/REVIEW-TRACKER-{number}" \
    --workflows-root ../openstack-horizon-agentic-workflows-review-tracker \
    --rename "tracker-{number}.md:tracker.md,bridge-artifacts/initial-review-{number}.md:initial-review-{number}.md"
```

The `--rename` value is a comma-separated list of `src:dst` pairs built from the
rename_map. Include every `bridge-artifacts/...` entry so the ingest script knows
which bridge artifacts belong to this review. Unlisted bridge artifacts are skipped.

#### Step P4: Report

Report to the user:
- The new run ID (e.g., run-001)
- The dashboard URL: `http://10.0.151.101:8072/investigations/REVIEW-TRACKER-{number}?run={run_id}`
- What changed (from the check result message)

---

## Output

Write the tracker to:

```
workflows/review-tracker/artifacts/review-tracker/REVIEW-TRACKER-{change-number}/tracker-{change-number}.md
```

This file is both the output artifact and the state for future rechecks.
