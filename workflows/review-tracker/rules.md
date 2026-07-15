# Review Tracker Workflow Rules

This document contains rules and guidelines for the Review Tracker workflow agent.

## Clickable Navigation Links at Top of Every Artifact (Non-negotiable)

Every artifact this workflow produces MUST begin with clickable markdown links
to the key external resources a reader needs to continue their analysis. These
links appear in the artifact header — the first few lines after the title.

**Hard rule:** Any URL that appears in the header section of an artifact MUST be
a clickable markdown link (`[text](url)`), NEVER a bare URL. This includes:

- Gerrit review URLs
- Jira ticket URLs
- Launchpad bug/blueprint URLs
- GitHub source file URLs
- Any other external reference a visitor would need

**Format:**
```markdown
**Review:** [https://review.opendev.org/c/openstack/horizon/+/992714](https://review.opendev.org/c/openstack/horizon/+/992714)
```

**NOT:**
```markdown
**Review:** https://review.opendev.org/c/openstack/horizon/+/992714
```

**Why:** Artifacts are published to web dashboards where bare URLs are not
automatically linked. A visitor reading the artifact must be able to click
through to the source review, ticket, or file immediately — without having
to copy-paste URLs. This is a usability requirement, not a style preference.

**Enforcement:** On every `--recheck` or regeneration, verify the header links
are clickable before writing the artifact. If a bare URL is found in the header,
wrap it as a markdown link before proceeding.

---

## Accuracy

### Verify Before Documenting

- Every status assignment must be based on Gerrit data, not inference
- If a thread has no explicit resolution signal, status is POSTED (not assumed RESOLVED)
- If the user self-replied "Done" or "all set", check if the thread is actually marked resolved on Gerrit — self-replies do not auto-resolve threads
- Always verify patchset numbers, vote values, and timestamps against the API response

### Quote Fidelity

- Comment text must be quoted verbatim, not paraphrased
- Long comments may be truncated with [...] but key points must be preserved
- Attribution must match the actual Gerrit author name (not username)
- When quoting across patchsets, include the patchset number for context

## Anchors

### Required Format

Anchors MUST be on their own line with blank lines above and below, so markdown
renderers treat them as an HTML block (invisible) rather than inline text:

```markdown
some previous content

<a name="cmt-xxx-n"></a>

### CMT-XXX-N — Topic — STATUS
```

- Do NOT put the anchor inline inside a heading (`### <a name="..."></a>Text`) — many renderers show the raw HTML as visible text
- Do NOT add anchors to headings that are never linked to — only add them when the document contains a `[link](#anchor-name)` reference
- Do NOT use `<a id="...">` — GitLab strips `id` attributes from rendered markdown
- Do NOT use `{#custom-id}` — GitLab does not support Kramdown extension syntax
- Anchor name must be lowercase, hyphen-separated

### Link Format

Internal links to anchors use standard markdown:

```markdown
[CMT-OWN-3](#cmt-own-3)
```

## Change Log

### Entry Format

Every recheck that detects changes MUST add a Change Log entry:

```markdown
### Scan #N — YYYY-MM-DD

1. **NEW** [Section link](#anchor): One-line description of new content
2. **UPDATED** [Section link](#anchor): What changed and why
```

### Ordering

- Newest entry first (reverse chronological)
- Within an entry, list changes in document order

### Linking

- Every entry MUST link to the affected section using the anchor
- Use the same anchor format as the section's `<a name="...">` tag

### Completion Markers

- Use strikethrough (`~~text~~`) for completed/resolved items
- Do NOT delete completed items — preserve the audit trail
- The Change Log is the primary navigation tool for reviewers finding recent updates

## Recheck Behavior

### Minimal Updates

- Only modify sections with actual changes detected from the API
- Do NOT regenerate the entire document on recheck
- Do NOT rewrite AI assessments for unchanged threads
- Do NOT re-fetch file diffs unless a new patchset added or removed files

### Early Exit

- If Gerrit `updated` timestamp is unchanged since the last scan, STOP immediately
- Report "No changes since scan #N on YYYY-MM-DD" and exit
- Do NOT make additional API calls beyond the timestamp check when no changes are detected

### Scan Log

- Every recheck adds a row to the Scan Log table, even if no changes were found
- The Notes column summarizes what was found (e.g., "2 new comments on CMT-JAN-1" or "No new activity")

## Document Structure

### Required Sections (in order)

1. Header (review URL, title, author, status, patchset, Zuul, files, reviewers)
2. Scan Log (table)
3. Change Log (reverse chronological — omitted on initial scan)
4. Where Things Are At / What To Do Next
5. Thread sections grouped by type (Patchset-Level, Inline by reviewer)
6. Comment Statistics (table)
7. Key Remaining Items Before This Can Merge (table)

### Clickable URLs

All URLs and file references in tracker documents MUST be rendered as clickable markdown links:

**Header section:**
- `**Review:** [https://review.opendev.org/...](https://review.opendev.org/...)` — NOT bare URL
- `**Files Changed:** 1 ([path/to/file.py:123](https://github.com/openstack/horizon/blob/master/path/to/file.py#L123))` — link to GitHub source with line anchor

**File references anywhere:**
- Format: `[path/to/file.py:line](https://github.com/openstack/horizon/blob/master/path/to/file.py#Lline)`
- If no line number: `[path/to/file.py](https://github.com/openstack/horizon/blob/master/path/to/file.py)`
- Use GitHub line anchors: `#L123` (single line) or `#L123-L456` (range)

**Comment text:**
- When a comment contains a URL, preserve it as-is (the commenter's formatting)
- When referencing external resources in AI Assessment, use markdown links

**General rule:**
- Any URL or file path the tracker generates must be a clickable markdown link
- URLs from quoted Gerrit comments are preserved verbatim

### Thread Section Format

Each thread section must include:
- Thread ID heading with anchor
- Author and status badge
- Quoted comment text and all replies
- AI assessment (significance, blocking/suggestion/nit, action needed)
- "Status for {User}" line with specific action

## Patch and Verify Safety

### NEVER-PUSH Rule

The skill NEVER executes any command that publishes changes to a remote repository.
The following commands are FORBIDDEN in all modes:

- `git review`
- `git push` (any variant: `--force`, `-u`, bare)
- `ssh review.opendev.org gerrit review`
- Any HTTP POST/PUT to Gerrit's review API
- Any command that submits, approves, or merges a change

The developer MUST review and push manually. The only exception is if the developer
explicitly writes "push it", "run git review", or equivalent in the conversation.

### No Clobber Rule

If a checkout directory exists and has uncommitted changes:

1. Report the dirty state with `git status --short`
2. STOP and ask the developer what to do
3. Do NOT delete, reset, or overwrite the directory

Clean directories at the same patchset may be reused without asking.

### Playwright Safety

- Playwright tests are READ-ONLY against the Horizon UI — they never modify data that
  cannot be cleaned up (they create and delete a test keypair named `verify-pw-test`)
- Credentials are read from environment variables, never hardcoded in committed artifacts
- Generated scripts are saved to artifacts for reproducibility and audit
- Playwright failure does NOT fail the overall verify — tox results are authoritative

### Tracker Dependency

`--create-patch` REQUIRES an existing tracker artifact with a "What Needs to Change"
section containing at least one non-strikethrough entry. If the tracker is missing or
has no actionable entries, STOP with an informative message. Do NOT independently analyze
Gerrit comments.

## Dashboard Publishing

### Explicit Publish Only

- NEVER auto-publish to the dashboard after a scan or recheck
- Only publish when the user explicitly passes `--update-artifact-dashboard`
- The `--status` flag ignores `--update-artifact-dashboard` (status is read-only, no artifact update)

### Nothing-New Detection

- Always check for changes before creating a new run
- Use `check_for_new_artifacts()` with the appropriate rename_map
- If the tracker hasn't changed since the last publish, report "Nothing new to publish" and STOP
- Do NOT create empty or duplicate runs

### Case ID Convention

- Review tracker cases use `REVIEW-TRACKER-{number}` as the case_id
- This differs from `REVIEW-{number}` used by horizon-code-review to avoid collision
- Example: `REVIEW-TRACKER-977939` for tracker, `REVIEW-977939` for code review

### Clickable References

- The "What AI Did" artifact must link knowledge files and agent persona to their source on GitHub
- Skill profiles provide `repo_url` for constructing these links
- The `what_ai_did_generator.py` renders `[path](repo_url/path)` when `repo_url` is present
- All skill profiles in the project must include `repo_url` so references are never bare code spans

### Rename on Publish

- The source artifact `tracker-{number}.md` is published as `tracker.md` in the run directory
- This enables the skill profile to use a fixed filename for the artifact key
- The rename is handled by the `--rename` flag on `ingest_artifacts.py`
- When `rename_map` is provided, only files in the map keys are copied (filters out unrelated trackers)

### Source of Truth Links

**CRITICAL:** All artifacts MUST be committed to git and rendered pages MUST link to the git source.

- Every artifact rendering route must include a `[src]` link pointing to the GitHub source file
- NEVER point to dashboard `/raw` endpoints as source — those serve copied data, not the authoritative git source
- Construct GitHub URLs using the skill profile's `repo_url` field:
  ```
  {repo_url}/workflows/{source_workflow}/artifacts/{source_skill_type}/{filename}
  ```
- For bridge artifacts:
  ```
  {repo_url}/workflows/{source_workflow}/artifacts/{source_skill_type}/bridge-artifacts/{filename}
  ```

This ensures every rendered page has a direct link to the source of truth .md file in git, making it easy to:
1. Verify the dashboard content matches what's committed
2. Edit the source file directly from the dashboard view
3. Track changes via git history
4. Share authoritative links (not copies)

---

## Final Report

### Generation Rules

- ONLY generate when the review status is MERGED on Gerrit
- ALWAYS verify status via API before generating (never trust cached state)
- ALWAYS use Gerrit API data for quantitative metrics (not tracker artifact)
- Use tracker artifact ONLY for qualitative data (thread assessments, scan history)
- NEVER generate a final report without an existing tracker artifact

### Accuracy Rules

- Response times must be computed from actual Gerrit timestamps, not estimated
- Patchset reasoning must be derived from the `kind` field and message timeline
- CI pass rate must count all Verified messages, including rechecks
- Reviewer engagement dates must match the first comment/vote from each reviewer
- "Idle time" is the longest gap between any two consecutive events (not patchsets)

### Honesty Rules

- The Lessons Learned section MUST contain at least one "What Could Improve" entry
- Do NOT attribute CI failures to "flaky tests" without evidence from the logs
- Do NOT minimize long response gaps — measure and report them factually
- If a patchset was unnecessary (e.g., could have been squashed), note it
- Present facts neutrally — the report describes what happened, not what should have happened

### Dashboard Integration

- Case ID: same as tracker (`REVIEW-TRACKER-{number}`)
- Artifact filename: `final-report-{number}.md` → renamed to `final-report.md` on publish
- Published in the same run as the tracker update (when both change in the same invocation)
- Or as a new run if published independently

---

## Bridge Execution Rules

### Bridge Opportunity Detection

- ONLY detect bridges when user passes `--deep-dive` flag
- Use conservative heuristics (false negative OK, false positive BAD)
- Question must contain: pattern (when/why/how) + code keyword + NOT resolved
- Never bridge LGTM comments, recheck commands, or resolved threads

### Bridge Context Generation

- Every bridge context MUST include: question, file, line, code_snippet
- Objective MUST be specific (not generic "analyze this")
- Search patterns MUST be relevant to the question
- Focus files MUST include: question file, middleware, test helpers

### Bridge Invocation

- Timeout MUST be 300 seconds (5 minutes max)
- Subprocess MUST capture stdout + stderr
- NEVER fail tracker run if bridge fails
- Log ALL bridge executions to bridge-log.jsonl (success + failure)

### Bridge Incorporation

- Link format: `[Code Analysis](bridge-artifacts/{thread-id}-analysis.md)`
- Extract Answer Summary (first 3-5 bullets only)
- Extract Suggested Response (full quote block)
- Preserve original AI Assessment (don't replace)

### Graceful Degradation

- If bridge timeout: log, mark "analysis unavailable", continue
- If bridge crash: capture stderr, log, mark "analysis failed", continue
- If output file missing: log error, mark "no output", continue
- Tracker ALWAYS completes, bridge failures are non-fatal
