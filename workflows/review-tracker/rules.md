# Review Tracker Workflow Rules

This document contains rules and guidelines for the Review Tracker workflow agent.

## Accuracy

### Verify Before Documenting

- Every status assignment must be based on Gerrit data, not inference
- If a thread has no explicit resolution signal, status is POSTED (not assumed RESOLVED)
- If the user self-replied "Done" or "all set", check if the thread is actually marked resolved on Gerrit — self-replies do not auto-resolve threads
- Always verify patchset numbers, vote values, and timestamps against the API response

### Quote Fidelity

- Comment text must be quoted verbatim, not paraphrased
- Long comments may be truncated with [...] but key points must be preserved
- Attribution must match the actual Gerrit author name (not username)
- When quoting across patchsets, include the patchset number for context

## Anchors

### Required Format

All internal document anchors MUST use:

```html
<a name="cmt-xxx-n"></a>
```

- Do NOT use `<a id="...">` — GitLab strips `id` attributes from rendered markdown
- Do NOT use `{#custom-id}` — GitLab does not support Kramdown extension syntax
- Anchor name must be lowercase, hyphen-separated
- Anchor must appear on the line immediately before its heading

### Link Format

Internal links to anchors use standard markdown:

```markdown
[CMT-OWN-3](#cmt-own-3)
```

## Change Log

### Entry Format

Every recheck that detects changes MUST add a Change Log entry:

```markdown
### Scan #N — YYYY-MM-DD

1. **NEW** [Section link](#anchor): One-line description of new content
2. **UPDATED** [Section link](#anchor): What changed and why
```

### Ordering

- Newest entry first (reverse chronological)
- Within an entry, list changes in document order

### Linking

- Every entry MUST link to the affected section using the anchor
- Use the same anchor format as the section's `<a name="...">` tag

### Completion Markers

- Use strikethrough (`~~text~~`) for completed/resolved items
- Do NOT delete completed items — preserve the audit trail
- The Change Log is the primary navigation tool for reviewers finding recent updates

## Recheck Behavior

### Minimal Updates

- Only modify sections with actual changes detected from the API
- Do NOT regenerate the entire document on recheck
- Do NOT rewrite AI assessments for unchanged threads
- Do NOT re-fetch file diffs unless a new patchset added or removed files

### Early Exit

- If Gerrit `updated` timestamp is unchanged since the last scan, STOP immediately
- Report "No changes since scan #N on YYYY-MM-DD" and exit
- Do NOT make additional API calls beyond the timestamp check when no changes are detected

### Scan Log

- Every recheck adds a row to the Scan Log table, even if no changes were found
- The Notes column summarizes what was found (e.g., "2 new comments on CMT-JAN-1" or "No new activity")

## Document Structure

### Required Sections (in order)

1. Header (review URL, title, author, status, patchset, Zuul, files, reviewers)
2. Scan Log (table)
3. Change Log (reverse chronological — omitted on initial scan)
4. Where Things Are At / What To Do Next
5. Thread sections grouped by type (Patchset-Level, Inline by reviewer)
6. Comment Statistics (table)
7. Key Remaining Items Before This Can Merge (table)

### Thread Section Format

Each thread section must include:
- Thread ID heading with anchor
- Author and status badge
- Quoted comment text and all replies
- AI assessment (significance, blocking/suggestion/nit, action needed)
- "Status for {User}" line with specific action
