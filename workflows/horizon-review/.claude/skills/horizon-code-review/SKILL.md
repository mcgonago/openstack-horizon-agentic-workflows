---
name: horizon-code-review
description: Review Horizon code changes for intent correctness, plugin-API stability, testing adequacy, and Horizon coding conventions. Use when reviewing a Gerrit patch, git diff, or set of modified files in OpenStack Horizon.
---

# Horizon Code Review

You are reviewing an OpenStack Horizon patch. Your goal is to assess whether the change correctly implements its stated intent, is consistent with its surroundings, fits Horizon's architecture, and will not break downstream plugins.

**Do not re-check what CI already enforces.** Python style (PEP8, hacking), import ordering, and JS lint are caught by `tox -e pep8` and `npm run lint`. Focus on things that require human judgement.

**Agent Collaboration — MANDATORY**: Always invoke **@horizon-core.md** for every review. This persona assesses plugin-API stability, correct OpenStack API client usage, Django/Horizon framework patterns, and testing adequacy. Skip only if the user explicitly asks to.

**Context inheritance**: When invoking subagents, always pass the workflow `rules.md` and `knowledge/horizon.md` content as context. Workflow rules and project knowledge take precedence over agent persona guidance.

## Input

The user will provide one of:

- A Gerrit change URL (e.g. `https://review.opendev.org/c/openstack/horizon/+/NNNNNN`)
- A Gerrit change number
- A git diff or patch content
- A file path or set of paths to review
- A Gerrit topic name (e.g. `bp/my-feature`)

### Options

- `--artifacts` — Generate an expanded set of review artifacts (testing
  guide, design analysis, risk assessment, AI transparency, human handoff)
  in addition to the standard review. Output is a directory at
  `artifacts/horizon-review/code-{change-number}/` containing 6 artifacts.
  See `artifact-profiles.md` in this workflow directory for artifact
  contracts and required sections.

## Process

### 0. Handle Gerrit Topic (if provided)

If the user provides a **Gerrit topic** instead of a single change:

- **If Gerrit MCP is available**:
  1. Query all open changes for the topic: `topic:{name} status:open project:openstack/horizon`
  2. Present the list to the user with change number, subject, and status
  3. Ask which change to review in depth
  4. Read sibling changes for context before reviewing the selected one
  5. Proceed to step 1

- **If Gerrit MCP is unavailable**: Ask the user to provide a specific change URL. They can find topic changes at `https://review.opendev.org/q/topic:{name}+project:openstack/horizon`.

### 1. Gather Context (Before Reading Code)

Build context the way an experienced reviewer would:

1. **Read the commit message** — understand the stated intent (bug fix? feature? refactor? cleanup?)
2. **Follow references** — open the linked Launchpad bug or blueprint. Understand the problem being solved. A bug fix without a matching bug report is unusual — note it.
3. **Check prior review history** — if Gerrit MCP is available: fetch the change and review prior patchset comments. Prior reviewer feedback often explains design choices that look odd in isolation. Note any unresolved discussions.
   - If Gerrit MCP is unavailable: skip this step and note it in the output.
4. **Survey the change shape** — which files are modified? Is this touching `horizon/` (plugin API), `openstack_dashboard/api/` (client layer), views, templates, tests, JS, or release notes?
5. **Check for related changes** — if there is a Gerrit topic and siblings exist, read their commit messages to understand the full scope of the series.

### 2. Verify Feature Approval (if applicable)

If the change implements a new feature (not a bug fix or refactor):

1. **Check for blueprint tag** — look for `Implements: blueprint {name}` in the commit message
2. **Look up the blueprint** — verify it exists at `https://blueprints.launchpad.net/horizon/+spec/{name}`
3. **If no blueprint found** — flag this. New features should reference a blueprint. Unlike Nova, Horizon does not require a formal spec doc — a blueprint description is sufficient. This is a suggestion, not a blocker, unless the feature is large.

### 3. Read the Code in Context

Do not review the diff in isolation:

- Read surrounding code to assess whether the change is **locally consistent** with its neighbors
- Consider whether the change is **globally sound** — does it fit Horizon's architecture?
- If reviewing a bug fix, understand the code path that leads to the bug — does the fix address the root cause or a symptom?
- Flag unrelated modifications — they should be in separate patches
- **Compare with baseline**: before flagging a potential runtime failure, check whether the same pattern exists in the pre-patch baseline. Only flag it if the change makes things worse than the baseline.

### 4. Plugin API Stability Check (Blockers)

This is the most Horizon-specific and highest-priority check.

**Changes to `horizon/` are potentially plugin-breaking.** Check:

- **Class renames or removals**: any class in `horizon/` that plugins subclass (DataTable, Action, LinkAction, BatchAction, SelfHandlingForm, Workflow, Step, TabGroup, Tab, GenericView, ModalFormView, MultiTableView, etc.)
- **Method signature changes**: adding required arguments, removing arguments, or changing return types on public methods that plugins override
- **Module path changes**: renaming or moving modules under `horizon/` that plugins import
- **URL name changes**: renaming URL `name=` arguments in `horizon/` URL patterns that plugins may `reverse()`
- **Template tag changes**: changes to `horizon/templatetags/` that plugin templates use

**How to assess impact**:
1. Check if the modified class/method is something a downstream plugin would import or subclass
2. Check if the change is additive (new optional argument with a default value — generally safe) vs. breaking (required new argument, removed argument, renamed method)
3. If breaking: flag as a **Blocker** with a concrete description of how a plugin would break
4. If additive: note it as safe but worth documenting

### 5. OpenStack API Client Layer Check

For changes in `openstack_dashboard/api/`:

- Functions must accept `request` as first argument
- Client objects must be instantiated via the appropriate helper (`novaclient(request)`, `neutronclient(request)`, etc.) — never instantiated directly
- List operations on large collections must use paginated APIs, not unlimited `.list()` calls
- Exceptions from client calls must be caught and handled with `horizon.exceptions.handle(request, ...)` or equivalent for user-facing errors
- Do not return raw SDK/client objects to views — wrap in domain objects or dicts as appropriate

### 6. Testing Adequacy Check

Go beyond checking for test existence:

- **Bug fix regression test**: every bug fix must have a test that would fail without the fix. If missing, this is a **Blocker**.
- **New code coverage**: new views, forms, tables, and API wrappers must have unit tests. Assess coverage of important branches and error paths.
- **JavaScript tests**: if `.js` files are added or significantly modified, a corresponding `.spec.js` Jasmine test is expected. Flag as a **Suggestion** if missing.
- **Test quality**:
  - Are mocks applied at the right boundary? Mock `openstack_dashboard.api.{service}.{function}`, not deeper
  - Are `assertNoFormErrors()`, `assertMessageCount()` used appropriately after form POSTs?
  - Are fixtures from `test_data/` reused rather than inventing new, potentially inconsistent test objects?
- **Integration tests**: not required but appreciated for complex UI changes; note if the change would benefit from a Selenium test.

### 7. Release Notes Check

Changes that need a `reno` release note:
- New features or removed features
- Deprecations (Python API or config options)
- Security fixes
- Upgrade-impacting changes
- User-visible behavior changes

Changes that do NOT need a release note:
- Pure bug fixes with no user-visible behavior change
- Internal refactors
- Test-only changes

If a release note is needed and missing, flag as a **Suggestion** (unless it is a security fix — then it is a **Blocker**).

### 8. Additional Checks

- **Templates**: if context variable names were renamed in the view, verify the template was updated too — this is a silent failure that CI does not catch
- **URL names**: if URL `name=` arguments changed, check all `{% url %}` tags and `reverse()` calls referencing them
- **Django compatibility**: if the change uses a Django API, check if it is compatible with all supported Django versions (see `.zuul.yaml` for the version matrix)
- **Config options**: new options should have proper help text, types, and defaults; add them to `openstack_dashboard/defaults.py` if applicable

### 9. Generate Expanded Artifacts (if --artifacts)

If the user provided `--artifacts`:

1. Read `artifact-profiles.md` in this workflow directory for the full
   artifact contracts and required sections
2. Create the output directory: `artifacts/horizon-review/code-{change-number}/`
3. Write `review.md` — same content as the standard single-artifact output
4. Write `design-analysis.md` — use the findings from Steps 3-4 and
   @horizon-core's assessment. Include before/after code walkthrough,
   edge case enumeration (minimum 3), and plugin ecosystem impact
5. Write `testing-guide.md` — generate manual test cases based on:
   - The specific code changes identified in Step 3
   - `knowledge/horizon.md` settings checklist (for auth/settings changes)
   - The testing adequacy assessment from Step 6
   - Depth rules from `artifact-profiles.md` (full vs minimal)
6. Write `risk-assessment.md` — formalize the risk findings from Steps 4-8
   into a structured table. Consult `knowledge/horizon.md` for security
   settings, performance settings, and plugin stability vectors
7. Write `what-ai-did.md` — enumerate checks performed, knowledge sources
   consulted, Gerrit context used, and honest limitations
8. Write `what-you-do-next.md` — human handoff with concrete next steps
   based on the verdict

All artifacts use the same context gathered in Steps 0-8. Do NOT re-read
the code, re-query Gerrit, or re-invoke @horizon-core. Each artifact is
a different view of the same deep analysis.

## Output

### Default (no --artifacts)

Write the review to `artifacts/horizon-review/code-{change-number}.md` with this structure:

```markdown
# Code Review: {brief description}

**Change**: {Gerrit URL}
**Files**: {count and brief summary of affected areas}
**Date**: {date}
**Verdict**: {APPROVE / REQUEST_CHANGES / COMMENT}

## Summary
{1-2 sentence summary of what the change does and whether it achieves its stated intent}

## Review History
{If Gerrit MCP was available: note whether prior feedback was addressed.}
{If Gerrit MCP was unavailable: note that prior reviewer comments were not examined — link for manual inspection}

## Blockers
{Issues that must be fixed before merge. If none, write "None."}

### Plugin API Impact
{Any changes to horizon/ public classes, method signatures, or module paths}

### Missing Regression Test
{Bug fixes without a test that would fail without the fix}

### Intent or Architecture Issues
{Does the change actually solve the problem? Does it fit Horizon's architecture?}

## Suggestions
{Non-blocking improvements — test coverage gaps, UX divergence, missing release note, missing blueprint reference}

## Nits
{Minor preferences, always prefixed with "Nit:"}

## Positive Feedback
{What the change does well — acknowledge good patterns and craftsmanship}

## Files Reviewed
| File | Type | Notes |
|---|---|---|
| path/to/file.py | Modified | ... |
```

### Expanded (--artifacts)

Write the standard review to `artifacts/horizon-review/code-{change-number}.md`
(backward compatibility — always generated).

Additionally, create a directory at `artifacts/horizon-review/code-{change-number}/`
and write the 6 artifacts defined in `artifact-profiles.md`:

1. `review.md` — Core review (same content as `code-{change-number}.md`)
2. `design-analysis.md` — Architecture + edge cases
3. `testing-guide.md` — Manual test procedures
4. `risk-assessment.md` — Formal risk table
5. `what-ai-did.md` — AI transparency
6. `what-you-do-next.md` — Human handoff

Report to the user which artifacts were generated and their file paths.

### Writing Style

Follow the rules in `rules.md`. In particular:

- Write every finding as if speaking to the patch author directly — be a helpful colleague
- Explain **why** something is a problem, not just **what** the rule says
- Each blocker or suggestion should be self-contained — readable without jumping to other sections
- The Summary must be 1-2 sentences that a busy reviewer can scan in seconds
- Nits must always be prefixed with "Nit:" so the author knows they are low-priority
