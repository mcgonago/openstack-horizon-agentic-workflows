# Feature Implementation Rules (All Tags)

These rules apply to every /feature tag=xxx invocation,
regardless of the specific tag or domain.

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

**Why:** Artifacts are published to web dashboards where bare URLs are not
automatically linked. A visitor reading the artifact must be able to click
through to the source review, ticket, or file immediately — without having
to copy-paste URLs. This is a usability requirement, not a style preference.

**Enforcement:** On every regeneration, verify the header links are clickable
before writing the artifact. If a bare URL is found in the header, wrap it as
a markdown link before proceeding.

---

## Safety

- NEVER push code or create a PR without explicit user approval
- NEVER modify upstream shared libraries (e.g., lib-common) directly
- If a ticket is BLOCKED: explain why and STOP implementation
- If a tag knowledge file is missing: list available tags and STOP

## Tier Awareness

- Before implementing ANY change, check Section 2 of the tag
  knowledge file for tier classification
- NEVER implement Tier 1 (central) changes as per-operator PRs
- For Tier 1 changes: output the proposed change content and
  advise the user to coordinate with the responsible team
- Only implement Tier 2 (per-operator) changes directly

## Tag Resolution

- Explicit tag= always takes precedence over inference
- If ambiguous (multiple knowledge files match): ask user
- Never guess a tag -- verify against knowledge/feature-*.md

## Validation

- Run ALL validation commands from Section 6 of the tag knowledge
- Report results for each command individually
- If any command fails: analyze, fix, re-run before proceeding
- Do not skip validation even if confident in the changes

## Code Quality

- Include domain rationale comments on every code change
  (explain WHY in terms of the tag domain, not just WHAT changed)
- Preserve existing code formatting and style
- Do not make changes beyond the tag's scope
- Follow Section 4 (Code Change Catalog) exactly
- Follow Section 5 (Architecture Patterns) for HOW

## Artifacts

- Write artifacts to artifacts/feature/<tag>/ (create dir if needed)
- Assessment report: assessment-<ticket>.md
- PR description: pr-description-<ticket>.md

## Communication

- Technical details go in the assessment report
- PR description follows the template in Section 7
- Explain the WHY (domain rationale) not just the WHAT
