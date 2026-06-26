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
- A change number with `--create-patch` flag (check out review, apply fixes from tracker)
- A change number with `--verify-patch` flag (run tox tests against patched checkout)
- A change number with `--update-artifact-dashboard` flag (publish to ioshaworkflow dashboard)

Flags are composable:

```
/review-tracker 977939 --create-patch
/review-tracker 977939 --create-patch --verify-patch
/review-tracker 977939 --create-patch --verify-patch --update-artifact-dashboard
/review-tracker 977939 --recheck --create-patch
/review-tracker 977939 --verify-patch
```

## Process

### Step 0: Parse Input and Determine Mode

1. **Parse input** — extract the change number:
   - If a full URL: extract the number from the path
   - If a bare number: use directly

2. **Detect modifier flags**:
   - `--update-artifact-dashboard`: set `publish_after = true`
   - `--create-patch`: set `create_patch = true`
   - `--verify-patch`: set `verify_patch = true`
   - `--horizon-url URL`: set `horizon_url = URL` (enables Playwright browser testing)
   - If `horizon_url` not set by flag, check `HORIZON_URL` env var. If not set, Playwright step is skipped.

3. **Determine primary mode**:
   - If `--status` flag: print current header + Open Threads table from existing tracker, STOP
     (all other flags are ignored with `--status`)
   - If `--recheck` flag: go to **Recheck Mode** (Step R1)
   - Otherwise: check if `artifacts/review-tracker/tracker-{number}.md` exists
     - If exists AND no action flags: tell the user "Tracker already exists. Use `--recheck` to update, or `--force` to regenerate from scratch."
     - If exists: proceed to post-primary actions
     - If not exists: go to **Initial Scan Mode** (Step 1)

4. **Post-primary-mode actions** (in order):
   - If `create_patch`: go to **Create Patch Mode** (Step C1)
   - If `verify_patch`: go to **Verify Patch Mode** (Step V1)
   - If `publish_after`: go to **Publish Mode** (Step P1)

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

#### Step C3: Clone the Review

Compute paths:

```
REPO_ROOT = parent directory of the workflow repos
            (walk up from workflow root to find the repo/ directory)
CHECKOUT_DIR = ${REPO_ROOT}/review-{number}-ps{N}
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

Compute paths:

```
REPO_ROOT = same as Create Patch Mode
PATCH_DIR = ${REPO_ROOT}/review-{number}-ps{N}
VERIFY_DIR = ${REPO_ROOT}/review-{number}-ps{N}-verify
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
