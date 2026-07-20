# Triage Assessment Workflow

This workflow performs quick triage and assessment of Jira tickets
and Launchpad bugs.

## Context

You are operating within the triassessment workflow.
Your role is to provide rapid, structured assessments of tickets
for stakeholder communication.

## Supported Sources

- **Jira** (OSPRH-XXXXX, RHOSSTRAT-XXX) -- fetched via Jira MCP tool
- **Launchpad** (LP#NNNNNNN, numeric ID, or bugs.launchpad.net URL) --
  fetched via public REST API (curl, no auth needed)

Source is auto-detected from input format. See SKILL.md Step 0.

## Knowledge

Read these documents based on ticket context:

1. ../../knowledge/feature-pqc.md -- PQC compliance context
   (when ticket relates to quantum, TLS, cryptography)
2. ../../knowledge/horizon.md -- Horizon project reference
   (when ticket relates to Horizon dashboard)
3. ../../knowledge/support-investigation.md -- Support patterns
   (when ticket relates to support cases, upgrades)
4. ../../knowledge/launchpad-openstack.md -- Launchpad bug lifecycle
   (when source is Launchpad, or ticket references upstream bugs)

## Launchpad Source

When the ticket source is Launchpad (detected by LP# prefix, numeric ID,
or bugs.launchpad.net URL), fetch data from the Launchpad REST API:

- Base URL: https://api.launchpad.net/devel/bugs/{id}
- No authentication needed for public bugs
- Bug tasks (per-project status): /bug_tasks endpoint
- Messages (comments): /messages endpoint
- Activity log: /activity endpoint

Key difference from Jira: Launchpad bugs can affect multiple projects,
each with independent status. Surface this in the Affected Projects table.

Parse comments for review.opendev.org URLs to build Gerrit cross-reference.

## Output

Write all output to artifacts/triassessment/ within this workflow directory.

## Rules

Read rules.md in this directory for behavioral constraints.
