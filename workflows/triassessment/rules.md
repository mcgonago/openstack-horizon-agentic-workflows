# Triassessment Rules

## 0. Clickable Navigation Links at Top of Every Artifact (Non-negotiable)

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

**Why:** Artifacts are published to web dashboards where bare URLs are not
automatically linked. A visitor reading the artifact must be able to click
through to the source review, ticket, or file immediately — without having
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

## 2. NO JIRA MODIFICATIONS (Non-negotiable)

The skill NEVER:
- Changes ticket status (close, reopen, transition)
- Adds comments to Jira tickets
- Modifies ticket fields (assignee, priority, labels)
- Creates new Jira tickets

It only READS ticket data via the Jira MCP tool.

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
