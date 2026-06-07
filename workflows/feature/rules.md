# Feature Implementation Rules (All Tags)

These rules apply to every /feature tag=xxx invocation,
regardless of the specific tag or domain.

## Safety

- NEVER push code or create a PR without explicit user approval
- NEVER modify upstream shared libraries (e.g., lib-common) directly
- If a ticket is BLOCKED: explain why and STOP implementation
- If a tag knowledge file is missing: list available tags and STOP
- Before implementing, check for existing PRs and branches for the
  same ticket. If found: report status and STOP. Never create
  duplicate PRs or branches for work that already exists.

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
- Section 4 provides INTENT and CONSTRAINTS, not code to copy --
  derive the implementation by reading the target repository
- Follow Section 5 (Architecture Patterns) for HOW
- Do NOT read Section 8 (Reference Implementation) during Steps 3-4.
  Section 8 is post-hoc validation material, not implementation input.
  Reading it during implementation defeats the purpose of the skill
  independently deriving the correct code.

## Artifacts

- Write artifacts to artifacts/feature/<tag>/ (create dir if needed)
- ALL 6 artifacts are mandatory in every mode:
  assessment.md, design.md, testing.md, pr-description.md,
  next-steps.md, what-ai-did.md
- See Step 6 in SKILL.md for required sections per artifact

## Non-Default Modes (--artifacts-only, --dry-run, --blind)

### Shared rules for all non-default modes

- Step 1.5 reports existing work as context but does NOT block
  (exception: --blind skips Step 1.5 entirely)
- Step 7 (PREPARE DELIVERY) is always skipped
- NEVER push code or create PRs in either mode
- Always include a comparison section in the assessment artifact

### --artifacts-only rules

- NEVER modify source files in the target repository
- NEVER generate git commit, push, or PR commands
- Step 4 (IMPLEMENT) is skipped
- Step 3.5 compares knowledge-derived changes vs actual PR
- Validation (Step 5) runs against the existing code, not new edits

### --dry-run rules

- MAY modify files, but ONLY in a disposable git worktree or
  temporary clone -- NEVER in the user's working directory
- Step 4 (IMPLEMENT) runs in the worktree/clone
- Step 5 (VALIDATION) runs in the worktree/clone
- Step 5.5 compares the implemented worktree changes vs the PR diff
- The worktree/clone MUST be cleaned up after artifacts are generated
- If worktree setup fails: fall back to --artifacts-only behavior
  and note the failure in the assessment

### --blind rules (used with --dry-run)

--blind creates an information barrier: the AI implements from
requirements alone, with no access to prior solutions until after
implementation is complete.

- SKIP Step 1.5 entirely -- do NOT search for existing PRs, branches,
  or prior work before Step 5.5
- Do NOT run gh pr list, gh pr diff, gh pr view, or any GitHub PR
  commands before Step 5.5
- Do NOT read Section 8 (Reference Implementation) of the knowledge
  file before Step 5.5
- Do NOT search the target repo's git log for prior PQC-related
  commits or branches before Step 5.5
- Step 5.5 is the FIRST time existing work is discovered and compared
- The assessment artifact MUST disclose that --blind mode was used
  and confirm no existing PRs were accessed during implementation
- If the AI cannot avoid seeing prior work (e.g., the knowledge file
  mentions PR numbers in Section 2), it MUST note this as a potential
  information leak in the assessment

## Artifact Quality Contracts

### Depth Metrics
- assessment.md: minimum 1,200 words, recommended 1,400+
- design.md: minimum 800 words, recommended 1,000+
- testing.md: minimum 400 words, recommended 500+
- pr-description.md: minimum 200 words
- next-steps.md: minimum 250 words
- what-ai-did.md: minimum 400 words
- Total across 6 artifacts: minimum 3,250 words
- If an artifact falls below its minimum, iterate -- read more
  code, add more detail, fill in templates from knowledge Sections
  9-11. Do not declare done until depth targets are met.

### Line-Level Evidence
- Every code claim in assessment.md and design.md MUST include
  file:line references (e.g., `cmd/main.go:84`)
- Claims without file:line references are unverifiable and will
  be flagged during review
- When file:line IS required: code claims, proposed changes,
  current state descriptions, insertion point references
- When file:line is NOT required: domain knowledge statements
  (e.g., "ML-KEM is FIPS 203"), procedural steps (e.g., "run
  go build"), general architecture descriptions

### Evidence Quality
- When citing code, show BOTH the current state and the proposed
  change with file:line references
- Bad: "MinVersion should be set to TLS 1.3"
- Good: "MinVersion is not set at cmd/main.go:84 (defaults to
  TLS 1.0). Proposed: append closure at line 126 setting
  c.MinVersion = tls.VersionTLS13."

### Required Section Enforcement
- Each artifact has required sections defined in Step 6 of SKILL.md
- Do NOT omit required sections even if you believe they are
  not applicable -- write "N/A" with a brief explanation instead
- Do NOT reorder required sections -- follow the order in Step 6
- Use templates from knowledge file Sections 9-11 where provided

### what-ai-did Integrity
- what-ai-did.md MUST report actual execution, not a template
- Map each step to the corresponding SKILL.md step number
- List the actual knowledge files consumed, not just "knowledge
  files were read"
- List the actual decisions made, not "decisions were made"
- Include actual artifact word counts, not placeholders
- Include known limitations and what could not be verified

### No Placeholder Content
- Every artifact section must contain substantive content
- "TODO", "TBD", "will be added later", or empty sections are
  not acceptable
- If genuine information is unavailable, explain WHY and what
  the user should do to obtain it

### What "Substantive" Means
- Substantive = domain-specific, evidence-backed, audience-aware
- NOT substantive: generic filler, repeated headings, vague claims
- Example of NOT substantive:
  "Code Analysis: Found some issues in the TLS configuration."
- Example of substantive:
  "Code Analysis (cmd/main.go:84-164): The tlsOpts slice is
  declared at line 84 as []func(*tls.Config). Currently,
  MinVersion is not set, defaulting to TLS 1.0. The disableHTTP2
  closure at lines 118-121 is the only existing TLS option.
  Proposed: append a new closure at line 126 setting
  c.MinVersion = tls.VersionTLS13. Both the webhook server
  (line 131) and metrics server (line 164) consume tlsOpts,
  so both are covered by a single append."

## Communication

- Technical details go in the assessment report
- PR description follows the template in Section 7
- Explain the WHY (domain rationale) not just the WHAT
