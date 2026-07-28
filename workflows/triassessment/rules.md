# Triassessment Rules

## 0. Clickable Navigation Links at Top of Every Artifact (Non-negotiable)

Every artifact this workflow produces MUST begin with clickable markdown links
to the key external resources a reader needs to continue their analysis. These
links appear in the artifact header -- the first few lines after the title.

**Hard rule:** Any URL that appears in the header section of an artifact MUST be
a clickable markdown link (`[text](url)`), NEVER a bare URL. This includes:

- Gerrit review URLs
- Jira ticket URLs
- Launchpad bug/blueprint URLs
- GitHub source file URLs
- Any other external reference a visitor would need

**Why:** Artifacts are published to web dashboards where bare URLs are not
automatically linked. A visitor reading the artifact must be able to click
through to the source review, ticket, or file immediately -- without having
to copy-paste URLs. This is a usability requirement, not a style preference.

**Enforcement:** On every regeneration or recheck, verify the header links
are clickable before writing the artifact. If a bare URL is found in the header,
wrap it as a markdown link before proceeding.

---

## 1. READ-ONLY (Non-negotiable)

The triassessment skill NEVER:
- Modifies code in any repository
- Creates branches, PRs, or patches
- Pushes to any remote
- Runs builds, tests, or deployments

It is purely an information-gathering and assessment tool.
The ONLY files it writes are its own artifacts in
`artifacts/triassessment/`.

## 2. NO TICKET MODIFICATIONS (Non-negotiable)

The skill NEVER:
- Changes ticket status (close, reopen, transition) in Jira or Launchpad
- Adds comments to Jira tickets or Launchpad bugs
- Modifies ticket fields (assignee, priority, labels, importance)
- Creates new Jira tickets or Launchpad bugs

It only READS ticket data via the Jira MCP tool or Launchpad REST API.

## 3. RECOMMENDATION, NOT DECISION

All assessment artifacts must use advisory language:
- "Recommend closing" NOT "Closing"
- "Suggest deferring" NOT "Deferring"
- "Assessment indicates" NOT "The answer is"

The human makes the final decision. The skill provides evidence
and recommendation to support that decision.

## 4. KNOWLEDGE ATTRIBUTION

When the assessment references a knowledge base, cite the source:
- "(per feature-pqc.md, Section 2)"
- "(from knowledge/horizon.md)"

This ensures the recommendation is traceable and auditable.

## 5. CODE BLOCK SOURCE LINKS (Non-negotiable)

Every code block showing actual repository code MUST include a clickable
GitHub/GitLab source link immediately before the code fence.

**Hard rule:** When showing code from a file, PR, or commit, add a **Source:**
line with a clickable markdown link to the exact file/PR/commit before the
code fence. This applies to:

- Makefiles, scripts, config files from repos
- Code snippets from PRs or commits
- YAML/JSON configs from CRDs or samples
- Any code that exists in a git repository

**Format:**
```
**Source:** [repo/path/file.ext](https://github.com/org/repo/blob/commit-or-branch/path/file.ext#L10-L20)
```makefile
PASSWORD ?=
...
```

**Why:** Artifacts are read on dashboards where visitors need to verify the
code, see full context, or check for updates. A bare code block with no source
forces the reader to search the codebase manually. Source links make artifacts
immediately actionable.

**Enforcement:** Before writing any artifact, scan for code blocks and verify
each has a source link. If a code block shows repository code without a source
link, add it before proceeding.

**Exceptions:** Pseudo-code, examples, or illustrative snippets that don't
represent actual repository code don't need source links.

## 6. INQUIRY TYPE DETECTION (Non-negotiable)

The triassessment skill must detect the inquiry type and generate appropriate artifacts.

**Inquiry Types:**

1. **Jira Ticket** - Input starts with `OSPRH-`, `RHOSSTRAT-`, etc.
   - Generate: `triage_assessment.md`, `related_tickets.md`
   - Fetch: Jira ticket hierarchy, blocking chains, cross-team dependencies

2. **Launchpad Bug** - Input starts with `LP#`, `lp:`, or is a launchpad URL
   - Generate: `triage_assessment.md`, `related_tickets.md` (only if related bugs found)
   - Fetch: Bug metadata, bug tasks, messages, linked merge proposals

3. **Gerrit Review** - Input is a Gerrit URL or numeric review with `--gerrit` flag
   - Generate: `triage_assessment.md`, `related_reviews.md`
   - Fetch: Review metadata, commit message, changed files, related reviews
   - **DO NOT** generate `related_tickets.md` unless Jira tickets are explicitly referenced in commit message

4. **Gerrit Comparison** - Input has `--compare` flag with two review IDs
   - Generate: `triage_assessment_primary.md`, `triage_assessment_compare.md`, `comparison.md`, `related_reviews.md`
   - Fetch: Both reviews, all related reviews for both, cross-reference
   - **DO NOT** generate `related_tickets.md` unless Jira tickets are shared between reviews

5. **GitHub PR** - Input is a GitHub PR URL or PR number with repo context
   - Generate: `triage_assessment.md`, `related_artifacts.md`, `github_pr_analysis.md`
   - Fetch: PR details, related PRs, commits, dependency chains
   - **DO NOT** generate `related_tickets.md` unless Jira tickets are explicitly linked in PR description

6. **Free-form Inquiry** - Natural language description or link to external resources
   - Generate: `triage_assessment.md`, context-appropriate analysis artifacts
   - Parse: Extract all referenced tickets, PRs, commits
   - Generate: `related_tickets.md` only if Jira tickets found, `related_artifacts.md` only if PRs/commits found

**Hard rule:** Never mix artifact types. If the inquiry is about Gerrit reviews with no Jira tickets mentioned in commit messages, do NOT generate `related_tickets.md`. If the inquiry is about a Jira ticket with no Gerrit reviews mentioned, do NOT generate `related_reviews.md`.

**Why:** Mixing artifact types creates confusion. Readers expect content relevant to the source type. Gerrit reviews should focus on code review aspects, not unrelated ticket hierarchies.

**Enforcement:** At Step 0 (Parse Input), detect inquiry type and set artifact flags. Before Step 6 (Write Artifacts), verify artifact content matches inquiry type.

## 7. NO EMOJI CODES IN ARTIFACTS (Non-negotiable)

Emoji codes like `:thinking_face:`, `:smile:`, `:+1:`, etc. MUST be stripped from all generated artifacts before publishing.

**Why:** Emoji codes are markdown shortcuts that render as literal text in many markdown viewers, including the ioshaworkflow dashboard. They make artifacts look unprofessional and are unacceptable for stakeholder-facing reports.

**Enforcement:**
1. **Extraction Phase:** When extracting content from inquiry sources (Slack, GitHub comments, email), strip all emoji codes matching pattern `:[a-z_]+:`
2. **Generation Phase:** Never generate emoji codes in assessment text
3. **Post-processing:** Before writing artifacts, run regex replacement to remove any remaining emoji codes

**Example Cleanup:**
```
Before: "Hmmmm and there was also merged PR #1158 :thinking_face::smile:."
After: "Hmmmm and there was also merged PR #1158."
```

## 8. DESCRIPTIVE LINKS FOR LONG URLS (Non-negotiable)

Long, cryptic URLs MUST be converted to descriptive clickable links.

**Threshold:** URLs longer than 80 characters should be converted to `[descriptive text](url)` format.

**Why:** Long URLs (especially Zuul logs, CI artifacts, GitHub file permalinks) are visually cluttered and hard to scan. Descriptive link text improves readability and makes artifacts shareable with stakeholders.

**Enforcement:**
1. **URL Detection:** Identify bare URLs > 80 chars in artifact content
2. **Context Extraction:** Determine what the link points to (Zuul log, GitHub file, CI artifact, etc.)
3. **Descriptive Text:** Generate concise descriptive text that identifies:
   - **What:** Type of resource (test log, PR file, commit diff, etc.)
   - **Where:** Repository or system (Zuul, GitHub, etc.)
   - **Context:** Relevant identifier (test name, file name, etc.)

**Examples:**

```
Before: https://sf.apps.int.gpc.ocp-hub.prod.psi.redhat.com/logs/ac8/components-integration/ac832f9aca7d40ff8d271d5bcf6c3418/controller/ci-framework-data/tests/test_operator/horizon/ui_integration_test_results.html.gz?sort=result

After: [Zuul CI log (ui_integration_test_results)](https://sf.apps.int.gpc.ocp-hub.prod.psi.redhat.com/logs/ac8/components-integration/ac832f9aca7d40ff8d271d5bcf6c3418/controller/ci-framework-data/tests/test_operator/horizon/ui_integration_test_results.html.gz?sort=result)
```

```
Before: https://github.com/openstack-k8s-operators/horizon-operator/commit/427781ab94fc381b57ad4689e48ed6a171e528e0

After: [this change](https://github.com/openstack-k8s-operators/horizon-operator/commit/427781ab94fc381b57ad4689e48ed6a171e528e0)
OR
[horizon-operator commit 427781ab](https://github.com/openstack-k8s-operators/horizon-operator/commit/427781ab94fc381b57ad4689e48ed6a171e528e0)
```

**Exceptions:**
- Short URLs (< 80 chars) can remain bare if context is clear
- Table cells where column header identifies resource type
- Reference sections where URL structure itself provides value

## 9. GERRIT VOTE INTERPRETATION (Non-negotiable for Gerrit sources)

When processing Gerrit review votes (Code-Review, Verified, Workflow), use
the human-readable status mapping from Step 2.5 in SKILL.md.

**Hard rules:**
1. **Never report raw vote JSON** - readers need status, not API responses
2. **Apply rules in order** - most specific first (MERGED beats everything, WIP beats needs-revision, etc.)
3. **Include vote counts** - "Code-Review: +2 (×2), +1 (×1)" not just "+2"
4. **Distinguish CI vs human votes** - "Verified: +1 (Zuul)" vs "Verified: +1 (username)"

**Vote summary format:**
```
Code-Review: +2 (×2), +1 (×1), -1 (×1)
Verified: +1 (Zuul)
Workflow: +1
```

**Status display priorities (from SKILL.md Step 2.5):**
1. MERGED → **Merged** (bold, this is done)
2. ABANDONED → Abandoned
3. NEW + work_in_progress → WIP
4. NEW + Code-Review -1/-2 → Needs Revision
5. NEW + Verified -1 → CI Failing
6. NEW + Code-Review +2 (×2) + Workflow +1 → Ready to Merge
7. NEW + Code-Review +2 → Approved (need +2×2)
8. NEW (clean) → Under Review

**Why:** Gerrit's label structure is complex. Stakeholders need "is this ready
to merge?" not "labels.Code-Review.all[0].value == 2". The status mapping
provides that translation.

**Enforcement:** Before writing review summary tables, apply the status mapping.
Never show raw Gerrit status fields like "NEW" without context.

## 10. ASCII-ONLY BOX DIAGRAMS (Non-negotiable)

**All box diagrams MUST use pure ASCII characters. NO UNICODE.**

**Forbidden characters:**
- Box drawing: ┌ ┐ └ ┘ ├ ┤ ─ │ ┬ ┴ ┼
- Symbols: ✅ ✓ ✗ → ← ↑ ↓ • ◦ ★
- Em-dashes: — (use `--`)
- Any character outside the ASCII range (0x00-0x7F)

**Required ASCII alternatives:**
- Box corners: `+`
- Horizontal lines: `-`
- Vertical lines: `|`
- Checkmarks: `[OK]` or `[X]`
- Arrows: `->`, `<-`, `v`, `^`
- Bullets: `*` or `-`

**Enforcement:**
1. **Before writing artifacts:** Use only ASCII characters in diagrams
2. **After writing artifacts:** Run `check_box_alignment.py --fix` on ALL .md files
3. **Never skip this step** - it must be run before declaring work done

**Script location:**
```bash
python3 /home/omcgonag/Work/mymcp/workspace/iproject/projects/ioshaworkflow/repo/ioshaworkflow/scripts/check_box_alignment.py --fix <file.md>
```

**Why:** Unicode box-drawing characters render inconsistently across browsers, terminals, and markdown viewers. ASCII is universal and works everywhere. This is a hard rule that applies to ALL artifacts in ALL workflows.

**Example:**

WRONG (unicode):
```
┌─────────────┐
│ Hello World │
└─────────────┘
```

CORRECT (ASCII):
```
+-------------+
| Hello World |
+-------------+
```
