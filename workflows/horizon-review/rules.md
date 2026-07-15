# Horizon Review Workflow Rules

This document contains rules and guidelines for the Horizon Review workflow agent.

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

**Enforcement:** On every regeneration or recheck, verify the header links
are clickable before writing the artifact. If a bare URL is found in the header,
wrap it as a markdown link before proceeding.

---

## MCP Server Integration

### Gerrit MCP Availability

The Horizon Review workflow supports both **Gerrit MCP** and **REST API fallback** modes:

- **With Gerrit MCP**: Full integration — fetch change history, metadata, prior review comments, post reviews programmatically
- **Without Gerrit MCP**: REST API fallback — post reviews using HTTP basic authentication; review history check is skipped

At workflow startup, MCP availability is automatically detected. The agent will report the status and adapt accordingly.

### When Gerrit MCP is Unavailable

If Gerrit MCP is not available or connection fails:

1. **Review Posting** (`/horizon-gerrit-comment` skill, future):
   - Falls back to Gerrit REST API
   - Prompts user for HTTP credentials (username and password from https://review.opendev.org/settings/#HTTPCredentials)
   - Posts review using `POST /changes/{id}/revisions/current/review`
   - Credentials are never stored — prompted each time, cleared after use
   - Maximum 3 authentication attempts, then falls back to manual artifact generation

2. **Review History** (`/horizon-code-review` skill):
   - Gerrit review history check is skipped
   - Note in review output that prior reviewer comments were not examined
   - Suggest manual inspection at `https://review.opendev.org/c/openstack/horizon/+/{change}`

3. **Manual Artifact Fallback**:
   - If REST API posting fails or user cancels, generate a Markdown artifact
   - Artifact contains formatted review comments ready for manual copy-paste to Gerrit UI
   - Saved to `artifacts/horizon-review/gerrit-comment-{change}.md`

### Error Handling

Distinguish clearly between:
- "Gerrit MCP unavailable" → use REST API fallback
- "REST API authentication failed" → invalid credentials
- "Network error" → cannot reach review.opendev.org
- "Change not found" → wrong change number or URL

Every error message must include specific remediation steps.

### Security

- Credentials prompted only when needed, never stored in files or artifacts
- Transmitted over HTTPS only
- Cleared from memory immediately after use

## Review Principles

### Do Not Re-Check What CI Already Enforces

Before flagging an issue, verify that it is NOT already caught by:
- `tox -e pep8` — Python style, import ordering, hacking checks
- `tox -e py3` — Python unit test failures
- `npm run lint` — JavaScript linting
- `npm run test` — JavaScript unit tests

Focus on things that require human judgement: plugin-API stability, architectural fit, correct OpenStack API client usage, test quality, UX consistency.

### Verify Plugin-API Impact Before Flagging

Before flagging a change to `horizon/` as plugin-breaking:
1. Confirm the modified class/method is actually part of the public plugin API (i.e., something a downstream plugin would import or subclass)
2. Check if there is a compatibility shim or if the change is additive (new optional argument)
3. If truly breaking, flag as a blocker with a concrete example of how a plugin would break

### Verify Test Coverage Before Flagging

Before flagging a missing test:
1. Check if existing tests cover the changed code path
2. For bug fixes: confirm the fix is tested by a regression test that would fail without the fix
3. For refactors: if behavior is unchanged and existing tests still pass, a new test may not be required

### Verify Reachability Before Flagging Runtime Bugs

Before reporting a potential runtime failure (e.g., `None` passed where not expected, missing attribute, type mismatch):
1. Trace the activation path — find where the function is called and what values are actually passed
2. Check whether the same pattern exists in the code before the patch (baseline comparison)
3. If the bug exists in the baseline too, note it as a pre-existing issue, not a regression introduced by this patch

## Writing Style

### Be Specific
- Cite file paths and line numbers for every finding
- Reference exact Horizon conventions or documentation sections
- Provide concrete examples of both the problem and the fix

### Distinguish Severity
- **Blockers**: Plugin-API breakage, missing regression test for bug fix, direct raw client use outside `api/`, missing blueprint for a feature
- **Suggestions**: Test coverage gaps, UX patterns diverging from Horizon conventions, missing release note
- **Nits**: Minor naming preferences, comment clarity — always prefixed with "Nit:"

### Be Constructive
- Suggest fixes, not just problems
- Explain **why** something is an issue
- Assume good intent — the author is trying to improve Horizon

### Keep Summaries Scannable
- Top-level summary must be 1-2 sentences
- Busy reviewers should understand the verdict in seconds
- Details belong in separate sections, not the summary

### Reference In-Tree Documentation
- Link to `doc/source/contributor/` for Horizon-specific conventions
- Reference Horizon's own contributor docs rather than duplicating rules here
