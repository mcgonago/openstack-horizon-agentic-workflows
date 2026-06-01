# Support Case Investigation Rules

## Evidence Requirements

- Every claim must reference a specific file, function, or log entry
- Include upstream commit SHAs when identifying code changes between versions
- Quote relevant code snippets -- do not paraphrase
- When comparing versions, show the BEFORE and AFTER side by side

## Scope

- Investigate ONLY the reported symptom -- do not expand scope
- If you discover related issues, note them in a "Related Findings"
  section but do not investigate them
- Focus on Horizon and its immediate API dependencies

## Communication

- Technical details go in investigation_report.md
- Customer-facing language goes in customer_response.md
- Never include internal tooling references in customer-facing output
- Use respectful, empathetic language in customer responses

## Safety

- Do not suggest destructive workarounds (dropping databases, deleting configs)
- Always recommend testing any fix in a non-production environment first
- Flag any security implications (credential exposure, policy bypasses)
