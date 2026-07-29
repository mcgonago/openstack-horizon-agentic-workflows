# Follow-Up Work — Review 986458

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986458](https://review.opendev.org/c/openstack/horizon/+/986458)
**Parent Jira:** [OSPRH-16426](https://redhat.atlassian.net/browse/OSPRH-16426)
**Parent Summary:** Add activate/deactivate actions to the Images view
**Generated:** 2026-07-29 18:45 UTC
**Review Status:** MERGED

---

## Summary

Review 986458 (Add activate/deactivate row actions to Images table) identified 1 follow-up item deferred during review discussions.

---

## Follow-Up Items

### FU-986458-1: Adopt PolicyTargetMixin for Image Row Actions

**Suggested by:** Radomir Dopieralski
**Thread:** [CMT-RAD-1](tracker-986458.md#cmt-rad-1), [CMT-RAD-3](tracker-986458.md#cmt-rad-3)
**Priority:** MEDIUM
**Type:** Technical Debt

#### Description

Replace hardcoded `image.owner == request.user.tenant_id` checks in image row actions with the `PolicyTargetMixin` pattern (currently used by Volume actions). This would pass resource ownership (`project_id`) to the RBAC policy framework, allowing operators who modify Glance policy to allow cross-project operations to see the correct button visibility without hardcoding ownership logic in `allowed()`.

#### Technical Details

- **Current state:** `DeactivateImage`, `ReactivateImage`, `DeleteImage`, and `EditImage` in `openstack_dashboard/dashboards/project/images/images/tables.py` all have hardcoded `image.owner == request.user.tenant_id` checks in their `allowed()` methods. The admin panel overrides these entirely (returns `True` without owner checks).

- **Proposed change:** Adopt the `PolicyTargetMixin` pattern used by Volume actions:
  - Create an `ImagePolicyTargetMixin` class that passes `project_id` from the image to the RBAC check
  - Apply to all project-panel image row actions (`DeactivateImage`, `ReactivateImage`, `DeleteImage`, `EditImage`, `UpdateMetadata`)
  - Admin panel actions remain unchanged (they already skip owner checks)

- **Files affected:**
  - [`openstack_dashboard/dashboards/project/images/images/tables.py:135-300`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L135-L300) (image row actions)
  - Reference pattern: [`openstack_dashboard/dashboards/project/volumes/tables.py:47`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47) (VolumePolicyTargetMixin)

#### Why Deferred

Deferred to maintain consistency with the existing pattern across 58+ image actions. Changing only `DeactivateImage` and `ReactivateImage` would have been inconsistent with `DeleteImage`, `EditImage`, and `UpdateMetadata`, which all use the same hardcoded owner check pattern. Radomir accepted keeping the current approach for consistency and suggested exploring `PolicyTargetMixin` as a follow-up that addresses all image actions together.

#### Acceptance Criteria

- [ ] Create `ImagePolicyTargetMixin` class following the Volume panel pattern
- [ ] Apply mixin to all project-panel image row actions: `DeactivateImage`, `Reactivate Image`, `DeleteImage`, `EditImage`, `UpdateMetadata`
- [ ] Verify admin panel actions (AdminDeleteImage, AdminEditImage) remain unchanged
- [ ] Tests added covering custom Glance policies that allow cross-project operations
- [ ] Documentation updated if needed (settings.rst or operator docs)

#### References

- Original review: [https://review.opendev.org/c/openstack/horizon/+/986458](https://review.opendev.org/c/openstack/horizon/+/986458)
- Thread: [CMT-RAD-1](tracker-986458.md#cmt-rad-1)
- Radomir's acceptance: [CMT-RAD-3](tracker-986458.md#cmt-rad-3)
- Code analysis: [bridge-artifacts/cmt-rad-1-analysis.md](bridge-artifacts/cmt-rad-1-analysis.md)
- Volume panel reference pattern: [`openstack_dashboard/dashboards/project/volumes/tables.py:47`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47)

---

## How to Create Jira Tickets

### Panel 1: Copy/Paste for Jira Web UI (Plain English)

**Project:** OSPRH  
**Issue Type:** Story  
**Parent:** OSPRH-16426  
**Priority:** Medium  
**Labels:** horizon, de-angularize, technical-debt

**Summary:**
```
Adopt PolicyTargetMixin for Image Row Actions
```

**Description:**
```
Replace hardcoded image.owner checks in image row actions with PolicyTargetMixin pattern to respect custom Glance RBAC policies.

TECHNICAL DETAILS

Current state: DeactivateImage, ReactivateImage, DeleteImage, EditImage all have hardcoded "image.owner == request.user.tenant_id" checks in their allowed() methods.

Proposed change: Create ImagePolicyTargetMixin following the Volume panel pattern (openstack_dashboard/dashboards/project/volumes/tables.py line 47).

Files affected: openstack_dashboard/dashboards/project/images/images/tables.py lines 135-300

WHY DEFERRED

Deferred to maintain consistency with existing pattern across 58+ image actions. Changing only DeactivateImage/ReactivateImage would be inconsistent with DeleteImage, EditImage, UpdateMetadata. Radomir Dopieralski accepted current approach for consistency and suggested PolicyTargetMixin as follow-up addressing all image actions together.

REFERENCES

Original review: https://review.opendev.org/c/openstack/horizon/+/986458
Comment thread: CMT-RAD-1 (owner check discussion)
Reviewer acceptance: CMT-RAD-3 ("Let's explore this in followup patches")
Volume panel pattern: https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47
```

---

### Panel 2: Copy/Paste for Jira Web UI (Jira Wiki Format)

**Project:** OSPRH  
**Issue Type:** Story  
**Parent:** OSPRH-16426  
**Priority:** Medium  
**Labels:** horizon, de-angularize, technical-debt

**Summary:**
```
Adopt PolicyTargetMixin for Image Row Actions
```

**Description:** (Copy this into Jira's description field - it will render nicely)
```
Replace hardcoded image.owner checks in image row actions with PolicyTargetMixin pattern to respect custom Glance RBAC policies.

h3. Technical Details

* Current state: DeactivateImage, ReactivateImage, DeleteImage, EditImage all have hardcoded |image.owner == request.user.tenant_id| checks
* Proposed change: Create ImagePolicyTargetMixin following Volume panel pattern (openstack_dashboard/dashboards/project/volumes/tables.py:47)
* Files affected: openstack_dashboard/dashboards/project/images/images/tables.py:135-300

h3. Why Deferred

Deferred to maintain consistency with existing pattern across 58+ image actions. Changing only DeactivateImage/ReactivateImage would be inconsistent with DeleteImage, EditImage, UpdateMetadata. Radomir Dopieralski accepted current approach for consistency and suggested PolicyTargetMixin as follow-up addressing all image actions together.

h3. References

* Original review: https://review.opendev.org/c/openstack/horizon/+/986458
* Comment thread: CMT-RAD-1 (owner check discussion)
* Reviewer acceptance: CMT-RAD-3 ("Let's explore this in followup patches")
* Volume panel pattern: https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47
```

---

### Panel 3: JSON Metadata for Automation

For use with Jira REST API or CLI tools. Requires `JIRA_USER` and `JIRA_TOKEN` environment variables.

**Using jira-cli tool:**
```bash
jira issue create \
  --type Story \
  --parent OSPRH-16426 \
  --summary "Adopt PolicyTargetMixin for Image Row Actions" \
  --body "$(cat <<'JIRA_BODY'
Replace hardcoded image.owner checks in image row actions with PolicyTargetMixin pattern to respect custom Glance RBAC policies.

TECHNICAL DETAILS

Current state: DeactivateImage, ReactivateImage, DeleteImage, EditImage all have hardcoded "image.owner == request.user.tenant_id" checks in their allowed() methods.

Proposed change: Create ImagePolicyTargetMixin following the Volume panel pattern (openstack_dashboard/dashboards/project/volumes/tables.py line 47).

Files affected: openstack_dashboard/dashboards/project/images/images/tables.py lines 135-300

WHY DEFERRED

Deferred to maintain consistency with existing pattern across 58+ image actions. Changing only DeactivateImage/ReactivateImage would be inconsistent with DeleteImage, EditImage, UpdateMetadata. Radomir Dopieralski accepted current approach for consistency and suggested PolicyTargetMixin as follow-up addressing all image actions together.

REFERENCES

Original review: https://review.opendev.org/c/openstack/horizon/+/986458
Comment thread: CMT-RAD-1 (owner check discussion)
Reviewer acceptance: CMT-RAD-3 ("Let's explore this in followup patches")
Volume panel pattern: https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47
JIRA_BODY
)" \
  --priority Medium \
  --label horizon \
  --label de-angularize \
  --label technical-debt
```

**Using curl with REST API:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -u "${JIRA_USER}:${JIRA_TOKEN}" \
  https://redhat.atlassian.net/rest/api/2/issue \
  -d @- <<'EOF'
{
  "fields": {
    "project": {"key": "OSPRH"},
    "issuetype": {"name": "Story"},
    "parent": {"key": "OSPRH-16426"},
    "summary": "Adopt PolicyTargetMixin for Image Row Actions",
    "description": "Replace hardcoded image.owner checks in image row actions with PolicyTargetMixin pattern to respect custom Glance RBAC policies.\n\nh3. Technical Details\n\n* Current state: DeactivateImage, ReactivateImage, DeleteImage, EditImage all have hardcoded |image.owner == request.user.tenant_id| checks\n* Proposed change: Create ImagePolicyTargetMixin following Volume panel pattern (openstack_dashboard/dashboards/project/volumes/tables.py:47)\n* Files affected: openstack_dashboard/dashboards/project/images/images/tables.py:135-300\n\nh3. Why Deferred\n\nDeferred to maintain consistency with existing pattern across 58+ image actions. Changing only DeactivateImage/ReactivateImage would be inconsistent with DeleteImage, EditImage, UpdateMetadata. Radomir Dopieralski accepted current approach for consistency and suggested PolicyTargetMixin as follow-up addressing all image actions together.\n\nh3. References\n\n* Original review: https://review.opendev.org/c/openstack/horizon/+/986458\n* Comment thread: CMT-RAD-1 (owner check discussion)\n* Reviewer acceptance: CMT-RAD-3 (\"Let's explore this in followup patches\")\n* Volume panel pattern: https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47",
    "priority": {"name": "Medium"},
    "labels": ["horizon", "de-angularize", "technical-debt"]
  }
}
EOF

REFERENCES
https://review.opendev.org/c/openstack/horizon/+/986458
EOF
)" \
  --priority Medium \
  --label horizon \
  --label de-angularize \
  --label technical-debt
```

**Using curl with REST API:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -u "${JIRA_USER}:${JIRA_TOKEN}" \
  https://redhat.atlassian.net/rest/api/2/issue \
  -d @- <<'EOF'
{
  "fields": {
    "project": {"key": "OSPRH"},
    "summary": "Adopt PolicyTargetMixin for Image Row Actions",
    "description": "Replace hardcoded image.owner checks in image row actions with PolicyTargetMixin pattern to respect custom Glance RBAC policies.\n\nh3. Technical Details\n\n* Current state: DeactivateImage, ReactivateImage, DeleteImage, EditImage all have hardcoded |image.owner == request.user.tenant_id| checks\n* Proposed change: Create ImagePolicyTargetMixin following Volume panel pattern (openstack_dashboard/dashboards/project/volumes/tables.py:47)\n* Files affected: openstack_dashboard/dashboards/project/images/images/tables.py:135-300\n\nh3. Why Deferred\n\nDeferred to maintain consistency with existing pattern across 58+ image actions. Changing only DeactivateImage/ReactivateImage would be inconsistent with DeleteImage, EditImage, UpdateMetadata. Radomir Dopieralski accepted current approach for consistency and suggested PolicyTargetMixin as follow-up addressing all image actions together.\n\nh3. References\n\n* Original review: https://review.opendev.org/c/openstack/horizon/+/986458\n* Comment thread: CMT-RAD-1 (owner check discussion)\n* Reviewer acceptance: CMT-RAD-3 (\"Let's explore this in followup patches\")\n* Volume panel pattern: https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47",
    "issuetype": {"name": "Story"},
    "priority": {"name": "Medium"},
    "labels": ["horizon", "de-angularize", "technical-debt"],
    "parent": {"key": "OSPRH-16426"}
  }
}
EOF
```

**Raw JSON metadata:**
```json
{
  "parent_jira": "OSPRH-16426",
  "parent_summary": "Add activate/deactivate actions to the Images view",
  "project_key": "OSPRH",
  "issue_type": "Story",
  "items": [
    {
      "summary": "Adopt PolicyTargetMixin for Image Row Actions",
      "description": "Replace hardcoded image.owner checks in image row actions with PolicyTargetMixin pattern to respect custom Glance RBAC policies.\\n\\nh3. Technical Details\\n\\n* Current state: DeactivateImage, ReactivateImage, DeleteImage, EditImage all have hardcoded |image.owner == request.user.tenant_id| checks\\n* Proposed change: Create ImagePolicyTargetMixin following Volume panel pattern (openstack_dashboard/dashboards/project/volumes/tables.py:47)\\n* Files affected: openstack_dashboard/dashboards/project/images/images/tables.py:135-300\\n\\nh3. Why Deferred\\n\\nDeferred to maintain consistency with existing pattern across 58+ image actions. Changing only DeactivateImage/ReactivateImage would be inconsistent with DeleteImage, EditImage, UpdateMetadata. Radomir Dopieralski accepted current approach for consistency and suggested PolicyTargetMixin as follow-up addressing all image actions together.\\n\\nh3. References\\n\\n* Original review: https://review.opendev.org/c/openstack/horizon/+/986458\\n* Comment thread: CMT-RAD-1 (owner check discussion)\\n* Reviewer acceptance: CMT-RAD-3 (\\\"Let's explore this in followup patches\\\")\\n* Volume panel pattern: https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/volumes/tables.py#L47",
      "priority": "Medium",
      "labels": ["horizon", "de-angularize", "technical-debt"],
      "parent_key": "OSPRH-16426"
    }
  ]
}
```

---

## Jira Ticket Creation Attempt

**Attempted:** 2026-07-29 19:00 UTC
**Status:** FAILED - Permission Denied

| Item | Jira Key | Status | Error |
|------|----------|--------|-------|
| FU-986458-1 | — | Failed | You do not have permission to create issues in the OSPRH project |

**Next steps:**
1. Request "Create Issues" permission in OSPRH project from project administrators
2. Or create ticket manually via Jira web UI using the content above
3. Or ask someone with permission (manager, team lead) to create the ticket

**Manual creation template:**
- Project: OSPRH
- Issue Type: Story
- Summary: Adopt PolicyTargetMixin for Image Row Actions
- Parent: OSPRH-16426
- Priority: Medium
- Labels: horizon, de-angularize, technical-debt
- Description: (see "Metadata for Jira Creation" section above)
