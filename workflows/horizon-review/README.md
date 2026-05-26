# Horizon Review Workflow

Reviews OpenStack Horizon Gerrit patches against project conventions, plugin-API stability, testing requirements, and coding standards.

## Prerequisites

- Access to https://review.opendev.org (Gerrit for OpenStack Horizon)
- Optional: Gerrit MCP server configured (see root README for setup) — enables prior review history and programmatic review posting; workflow falls back to manual artifact generation without it
- Optional: Local Horizon clone for reading source context (useful for large reviews)

## Available Skills

| Skill | Cursor Name | What It Does |
|---|---|---|
| `/horizon-code-review` | `horizon-code-review` | Review a Horizon Gerrit patch for intent, plugin-API stability, test coverage, and conventions |

## Usage

### Cursor

Open the repository root in Cursor. Type `/` in the agent chat:

```
/horizon-code-review https://review.opendev.org/c/openstack/horizon/+/NNNNNN
```

You can also provide:
- A change number: `/horizon-code-review 123456`
- A Gerrit topic: `/horizon-code-review topic:bp/my-feature`
- A git diff pasted directly into the chat

### Claude Code

```bash
cd workflows/horizon-review
claude
# Then:
/horizon-code-review https://review.opendev.org/c/openstack/horizon/+/NNNNNN
```

### Ambient Code Platform (ACP)

Load via Custom Workflow (URL: this repo, Path: `workflows/horizon-review`), then use the skill name directly.

## What the Review Covers

1. **Intent verification** — does the change do what the commit message says?
2. **Plugin-API stability** — do changes to `horizon/` break downstream plugin projects?
3. **OpenStack API client conventions** — correct client usage, pagination, error handling
4. **Testing adequacy** — regression test for bug fixes, coverage of new code, JS tests if needed
5. **Blueprint/bug reference** — is there a linked Launchpad bug or blueprint?
6. **Release notes** — is a `reno` note needed?
7. **Template/URL consistency** — are context variable renames reflected in templates?

## What the Review Does NOT Cover

- Python style, import ordering (enforced by `tox -e pep8`)
- JS lint errors (enforced by `npm run lint`)
- Unit test pass/fail (enforced by `tox -e py3` and `npm run test`)

## Output

Reviews are saved to `artifacts/horizon-review/code-{change-number}.md` with:
- **Verdict**: APPROVE / REQUEST_CHANGES / COMMENT
- **Blockers**: must-fix issues (plugin breakage, missing regression test)
- **Suggestions**: non-blocking improvements
- **Nits**: minor preferences
- **Positive feedback**: what the change does well

## MCP Fallback Behavior

| Capability | With Gerrit MCP | Without Gerrit MCP |
|---|---|---|
| Fetch change metadata | Via MCP | Via Gerrit REST API (anonymous) |
| Prior review history | Available | Skipped (noted in output) |
| Topic change listing | Available | Not available |
| Post review to Gerrit | Via MCP (future skill) | Manual copy-paste from artifact |
