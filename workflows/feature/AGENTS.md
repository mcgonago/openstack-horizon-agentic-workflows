# Feature Implementation Workflow (Tag-Based)

This workflow implements feature changes for OpenStack operators
using tag-specific knowledge files.

## Context

You are operating within the feature implementation workflow.
Your role is defined by the feature-engineer agent persona.
The specific domain is determined by the tag parameter.

## Knowledge

Read these documents before beginning any implementation:

1. The tag-specific knowledge file:
   ../../knowledge/feature-<tag>.md
   (The tag is resolved from the user's input. If no tag is
   specified, scan all knowledge/feature-*.md files to find
   a match based on ticket key or keywords.)

2. Shared Horizon context:
   ../../knowledge/horizon.md
   (General Horizon ecosystem reference)

## Agent

Your persona is defined in ../../agents/feature-engineer.md.
Follow its tag-aware implementation process.

## Output

Write all output to artifacts/feature/<tag>/ within this
workflow directory, creating the tag subdirectory if needed.

## Rules

Read rules.md in this directory for behavioral constraints.
These rules apply to ALL tags.
