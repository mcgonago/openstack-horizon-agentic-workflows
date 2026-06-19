# Review Tracker Workflow

Track the lifecycle of OpenDev Gerrit reviews — comment threads, reviewer status, votes, and action items. Creates a living document that updates incrementally on recheck.

Unlike `/horizon-code-review` (a one-shot code quality assessment), `/review-tracker` produces a **living document** that evolves as the review progresses.

---

## Available Skills

| Skill command | What it does |
|---|---|
| `/review-tracker` | Track a Gerrit review's comment lifecycle |

---

## Quickstart — Cursor

1. Open the `openstack-horizon-agentic-workflows` folder in Cursor
2. Press **Ctrl+L** / **Cmd+L** to open the agent chat
3. Make sure the mode selector says **Agent**
4. Type:

```
/review-tracker 977939
```

Or with a full URL:

```
/review-tracker https://review.opendev.org/c/openstack/horizon/+/977939
```

To update an existing tracker:

```
/review-tracker 977939 --recheck
```

---

## Quickstart — Claude Code

```bash
cd openstack-horizon-agentic-workflows/workflows/review-tracker
claude
```

Then type:

```
/review-tracker 977939
```

---

## Quickstart — Ambient Code Platform (ACP)

In the ACP Custom Workflow dialog, enter:

- **URL**: `https://github.com/HanzJas/openstack-horizon-agentic-workflows.git`
- **Branch**: `main`
- **Path**: `workflows/review-tracker`

Then use `/review-tracker` in the workflow chat.

---

## Output

```
artifacts/review-tracker/tracker-{change-number}.md
```

The tracker document contains:
- Header with review metadata (title, author, status, patchset, votes)
- Scan Log tracking all scans
- Change Log for navigating updates (added on recheck)
- Thread-by-thread analysis with status classification and AI assessments
- Comment statistics per reviewer
- Prioritized action items

---

## Related Skills

| Skill | Relationship |
|---|---|
| `/horizon-code-review` | One-shot code quality assessment — complementary to the living tracker |
