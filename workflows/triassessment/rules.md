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
