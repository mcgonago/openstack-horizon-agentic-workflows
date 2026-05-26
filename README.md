# OpenStack Horizon Agentic Workflows

AI-assisted workflows for OpenStack Horizon development. Currently includes a code review workflow that analyses Horizon Gerrit patches for intent correctness, plugin-API stability, test coverage, and Horizon coding conventions.

Supports **Cursor**, **Claude Code**, and the **Ambient Code Platform (ACP)**.

---

## Available Workflows

| Workflow | Skill command | What it does |
|---|---|---|
| `horizon-review` | `/horizon-code-review` | Reviews a Horizon Gerrit patch |

---

## Quickstart — Cursor

### Step 1 — Clone this repository

```bash
git clone https://github.com/HanzJas/openstack-horizon-agentic-workflows.git
cd openstack-horizon-agentic-workflows
```

### Step 2 — Open the repository in Cursor

1. Open the Cursor app
2. Select **File → Open Folder** and choose the `openstack-horizon-agentic-workflows` folder you cloned

The skills and rules are auto-discovered by Cursor from `.agents/skills/` and `.cursor/rules/` — no additional configuration needed.

### Step 3 — Run a review

1. Press **Ctrl+L** (Windows/Linux) or **Cmd+L** (Mac) to open the agent chat
2. Make sure the mode selector says **Agent** — if it shows *Ask* or *Edit*, click it and switch to **Agent**
3. Type the review command, replacing `NNNNNN` with the Gerrit change number:

```
/horizon-code-review NNNNNN
```

You can also pass a full URL:

```
/horizon-code-review https://review.opendev.org/c/openstack/horizon/+/NNNNNN
```

The agent fetches the patch from Gerrit, analyses it, and writes the result to `artifacts/horizon-review/code-NNNNNN.md`.

---

## Quickstart — Claude Code

### Step 1 — Clone this repository

```bash
git clone https://github.com/HanzJas/openstack-horizon-agentic-workflows.git
```

### Step 2 — Start Claude Code inside the workflow directory

```bash
cd openstack-horizon-agentic-workflows/workflows/horizon-review
claude
```

### Step 3 — Run a review

Inside the Claude Code session, type:

```
/horizon-code-review https://review.opendev.org/c/openstack/horizon/+/NNNNNN
```

---

## Quickstart — Ambient Code Platform (ACP)

In the ACP Custom Workflow dialog, enter:

- **URL**: `https://github.com/HanzJas/openstack-horizon-agentic-workflows.git`
- **Branch**: `main`
- **Path**: `workflows/horizon-review`

Then use `/horizon-code-review` in the workflow chat.

---

## Optional Enhancements

The workflow works out of the box with no extra setup. Two optional enhancements are available if you want deeper reviews:

| Enhancement | What you gain | How to enable |
|---|---|---|
| **Gerrit MCP Server** | Agent can read prior reviewer comments and list all changes in a topic | [Setup instructions below](#optional--gerrit-mcp-server) |
| **Local Horizon clone** | Agent can read surrounding source code for context on large or complex patches | [Setup instructions below](#optional--local-horizon-clone) |

Without either, the agent fetches patch content via the public Gerrit REST API and reviews from the diff alone — which is sufficient for the vast majority of patches.

---

## What the Review Covers

The agent does **not** re-check what CI already enforces (PEP8, import order, JS lint). It focuses on things that require human judgement:

1. **Intent** — does the change actually do what the commit message says?
2. **Plugin-API stability** — do changes to `horizon/` break downstream plugin projects (Octavia UI, Designate UI, Magnum UI, etc.)?
3. **OpenStack API client conventions** — correct client instantiation, pagination, error handling
4. **Testing adequacy** — regression test present for bug fixes, new code covered, JS tests where needed
5. **Bug/blueprint reference** — is there a linked Launchpad bug or blueprint?
6. **Release notes** — is a `reno` note needed?
7. **Template/URL consistency** — are context variable renames reflected in templates?

## What the Review Output Looks Like

```
artifacts/horizon-review/code-NNNNNN.md
```

```
# Code Review: <title>

Verdict: APPROVE / REQUEST_CHANGES / COMMENT

## Summary
...

## Blockers        ← must-fix: plugin breakage, missing regression test
## Suggestions     ← non-blocking improvements
## Nits            ← minor preferences, always prefixed with "Nit:"
## Positive Feedback
## Files Reviewed
```

---

## Optional — Gerrit MCP Server

**What you gain:** the agent can read prior reviewer comments (useful when a patch is on patchset 2+) and list all sibling changes in a Gerrit topic.

**Without it:** the agent skips review history and notes it in the output. Everything else works normally.

**To enable**, set up the MCP server:

### 1. Install

```bash
git clone https://gerrit.googlesource.com/gerrit-mcp-server /opt/gerrit-mcp-server
cd /opt/gerrit-mcp-server
./build-gerrit.sh
```

### 2. Configure

```bash
cp gerrit_mcp_server/gerrit_config.sample.json gerrit_mcp_server/gerrit_config.json
```

Edit `gerrit_config.json` with your OpenDev credentials (get your HTTP password at https://review.opendev.org/settings/#HTTPCredentials):

```json
{
  "default_gerrit_base_url": "https://review.opendev.org/",
  "gerrit_hosts": [
    {
      "name": "OpenDev",
      "external_url": "https://review.opendev.org/",
      "authentication": {
        "type": "http_basic",
        "username": "YOUR_GERRIT_USERNAME",
        "auth_token": "YOUR_HTTP_PASSWORD"
      }
    }
  ]
}
```

> Authentication is optional for read-only access — OpenDev allows anonymous Gerrit reads.

### 3. Register with Cursor or Claude Code

**Cursor** — add to `.cursor/mcp.json` in this repo (project-scoped) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "gerrit": {
      "command": "/opt/gerrit-mcp-server/.venv/bin/python",
      "args": ["/opt/gerrit-mcp-server/gerrit_mcp_server/main.py", "stdio"],
      "env": {
        "PYTHONPATH": "/opt/gerrit-mcp-server/"
      }
    }
  }
}
```

**Claude Code** — same JSON, add to `~/.claude.json` or `.claude/settings.json`.

---

## Optional — Local Horizon Clone

**What you gain:** on large or complex patches the agent can read the surrounding source code — not just the changed lines — to better judge architectural fit and local consistency.

**Without it:** the agent reviews from the diff alone, which is sufficient for most patches.

**To enable**, clone the Horizon repository alongside this one:

```bash
git clone https://opendev.org/openstack/horizon.git
```

The skill looks for it at `/workspace/repos/horizon/` in ACP sessions, or at any path you point it to.

---

## Acknowledgements

This repository is based on the architecture and design patterns from [sbauza/openstack-agentic-workflows](https://github.com/sbauza/openstack-agentic-workflows) by Sylvain Bauza. The multi-tool discovery layout (`AGENTS.md` / `CLAUDE.md` / `.agents/skills/` symlinks / `.ambient/ambient.json`), the design principles (no duplicate CI checks, human decides / agent assists), and the overall workflow structure were all taken from that project. The Horizon-specific content — skill logic, review rules, knowledge base, and agent persona — was built on top of that foundation.

---

## Repository Structure

```
.agents/skills/
└── horizon-code-review/           → symlink for Cursor skill discovery
.cursor/
├── agents/horizon-core.md         → symlink for Cursor persona discovery
└── rules/horizon-rules.mdc        → always-applied behavioral rules
agents/
└── horizon-core.md                Horizon core reviewer persona
knowledge/
└── horizon.md                     Horizon project reference (architecture, conventions)
workflows/
└── horizon-review/
    ├── .ambient/ambient.json      ACP workflow config
    ├── .claude/skills/
    │   └── horizon-code-review/
    │       └── SKILL.md           Canonical skill definition (all tools read from here)
    ├── AGENTS.md                  Model-agnostic project reference
    ├── CLAUDE.md                  Claude Code pointer
    ├── rules.md                   Behavioral rules for the review agent
    └── README.md                  Workflow-level documentation
artifacts/                         Generated review outputs (git-ignored)
```
