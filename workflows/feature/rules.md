# Feature Implementation Rules (All Tags)

These rules apply to every /feature tag=xxx invocation,
regardless of the specific tag or domain.

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
