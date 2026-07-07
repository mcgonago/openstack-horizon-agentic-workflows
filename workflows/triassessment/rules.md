# Triassessment Rules

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
