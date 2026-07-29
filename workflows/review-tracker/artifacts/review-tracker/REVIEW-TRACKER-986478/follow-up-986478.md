# Follow-Up Work — Review 986478

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
**Parent Jira:** [OSPRH-16422](https://redhat.atlassian.net/browse/OSPRH-16422)
**Parent Summary:** Update filtering in the Images table
**Generated:** 2026-07-29 18:50 UTC
**Review Status:** NEW

---

## Summary

Review 986478 (Update filtering in the Images table) identified 2 follow-up items deferred during review discussions with Radomir Dopieralski.

---

## Follow-Up Items

### FU-986478-1: Substring Matching for Image Name Filter

**Suggested by:** Radomir Dopieralski
**Thread:** [CMT-RAD-1](tracker.md#cmt-rad-1)
**Priority:** MEDIUM
**Type:** Enhancement

#### Description

Replace the exact-match `name` filter with substring search in `ImageFilterAction`, allowing users to filter images by partial name match (e.g., typing "ubuntu" shows "ubuntu-22.04", "ubuntu-24.04", etc.) instead of requiring the full exact name.

#### Technical Details

- **Current state:** `ImageFilterAction.filter_choices` includes `('name', _('Image Name ='), True)` which performs exact matching via the Glance v2 API `name` parameter. The admin panel (`AdminImageFilterAction`) uses the same exact-match pattern.

- **Proposed change:** Implement substring matching for image names. This would require one of:
  - **Option A (client-side filtering):** Fetch all images without name filter, filter results in Python by substring, but this breaks server-side pagination for large image lists (> 1000 images)
  - **Option B (hybrid approach):** Use a custom filter that fetches paginated results and filters by substring, similar to how Horizon handles some dynamic dropdowns, but this pattern is not used anywhere else in Horizon for table filters
  - **Option C (API enhancement):** Propose Glance API enhancement to support substring matching on `name` parameter (would require cross-project coordination with Glance team)

- **Files affected:**
  - [`openstack_dashboard/dashboards/project/images/images/tables.py:206-210`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L206-L210) (ImageFilterAction)
  - [`openstack_dashboard/dashboards/admin/images/tables.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py) (AdminImageFilterAction for consistency)

#### Why Deferred

Deferred due to Glance v2 API limitation — the `name` filter performs exact matching only. Changing to substring would require either client-side filtering (breaking server-side pagination for large deployments) or a custom hybrid approach not used anywhere else in Horizon. Radomir marked the comment as resolved (`unresolved: false`), indicating it was a suggestion rather than a blocker. The exact-match behavior is consistent with the admin Images panel and all other server-side filters in Horizon (all use `=` labels).

#### Acceptance Criteria

- [ ] Choose implementation strategy (client-side, hybrid, or Glance API enhancement)
- [ ] Implement substring matching for `name` filter in both project and admin Images tables
- [ ] Preserve pagination for large image lists (if using hybrid approach)
- [ ] Update filter label from "Image Name =" to "Image Name contains" (or similar)
- [ ] Tests added covering substring match behavior
- [ ] Release note added documenting new filter capability

#### References

- Original review: [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
- Thread: [CMT-RAD-1](tracker.md#cmt-rad-1)
- Radomir's comment: "I noticed that the image name must match exactly to be shown by the filter, wouldn't it make more sense to make the filter show all images that contain the string?"
- Deep-dive analysis: [bridge-artifacts/986478-cmt-rad-1-analysis.md](bridge-artifacts/986478-cmt-rad-1-analysis.md)
- Admin panel reference: [`openstack_dashboard/dashboards/admin/images/tables.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py)

---

### FU-986478-2: Owner Filter Choice

**Suggested by:** Radomir Dopieralski
**Thread:** [CMT-RAD-2](tracker.md#cmt-rad-2)
**Priority:** LOW
**Type:** Enhancement

#### Description

Add `('owner', _('Owner ='), True)` to `ImageFilterAction.filter_choices`, allowing users to filter images by owner project UUID. This complements the `visibility` filter that was already added in the original review.

#### Technical Details

- **Current state:** `ImageFilterAction.filter_choices` includes `name`, `status`, `disk_format`, and `visibility` (added during review). The `owner` filter was discussed but not added.

- **Proposed change:** Add `('owner', _('Owner ='), True)` to the filter_choices tuple. The Glance v2 API supports the `owner` filter parameter and `openstack_dashboard/api/glance.py` already passes it through correctly. Users would need to enter a project UUID (e.g., `d3f4f5g6h7i8j9k0l1m2n3o4p5q6r7s8`), which is less user-friendly than the old tab-based `OwnerFilter` that abstracted this away (tabs: "Project", "Public", "Shared").

- **Files affected:**
  - [`openstack_dashboard/dashboards/project/images/images/tables.py:206-210`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L206-L210)
  - [`openstack_dashboard/dashboards/project/images/images/tests.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tests.py) (add test coverage)

#### Why Deferred

Deferred pending confirmation from Radomir whether the `owner` filter is actually needed alongside `visibility`. The `owner` filter requires users to know and type a project UUID, which is not very user-friendly — the old tab-based `OwnerFilter` provided "Project", "Public", "Shared" tabs that abstracted away the UUID requirement. The `visibility` filter (already added) restores most of the old filtering capability (public/private/shared/community). The `owner` filter would be useful for operators who know project UUIDs, but may not be needed for typical end users. Radomir's original comment asked "could we also have visibility and owner" — visibility was added, but owner was left as a follow-up pending clarification.

#### Acceptance Criteria

- [ ] Confirm with Radomir (or project team) that `owner` filter is wanted
- [ ] Add `('owner', _('Owner ='), True)` to `ImageFilterAction.filter_choices`
- [ ] Add test coverage in `images/tests.py` verifying the filter is present
- [ ] Update release note (if applicable) mentioning `owner` filter addition
- [ ] Consider UX improvement: help text or placeholder showing example UUID format

#### References

- Original review: [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
- Thread: [CMT-RAD-2](tracker.md#cmt-rad-2)
- Radomir's comment: "could we also have visibility and owner as the possible filters?"
- Deep-dive analysis: [bridge-artifacts/986478-cmt-rad-2-analysis.md](bridge-artifacts/986478-cmt-rad-2-analysis.md)
- Visibility filter was added via `--update-feature` on 2026-07-16

---


## How to Create Jira Tickets

### Ticket 1 of 2: Substring Matching for Image Name Filter

#### Panel 1: Copy/Paste for Jira Web UI (Plain English)

**Project:** OSPRH  
**Issue Type:** Story  
**Parent:** OSPRH-16422  
**Priority:** Medium  
**Labels:** horizon, de-angularize, ux-improvement

**Summary:**
```
Substring Matching for Image Name Filter
```

**Description:**
```
Replace exact-match image name filter with substring search in both project and admin Images tables.

TECHNICAL DETAILS

Current state: ImageFilterAction uses name param with exact match (Glance v2 API limitation)

Proposed change: Implement substring matching via client-side filtering, hybrid approach, or Glance API enhancement

Files affected: 
- openstack_dashboard/dashboards/project/images/images/tables.py lines 206-210
- openstack_dashboard/dashboards/admin/images/tables.py

WHY DEFERRED

Deferred due to Glance v2 API limitation -- the name filter performs exact matching only. Changing to substring would require client-side filtering (breaks pagination) or custom hybrid approach not used elsewhere. Radomir Dopieralski marked comment resolved (suggestion, not blocker). Exact-match behavior is consistent with admin Images panel and all other server-side filters in Horizon.

IMPLEMENTATION OPTIONS

Option A: Client-side filtering (breaks pagination for large deployments)
Option B: Hybrid approach (not used elsewhere in Horizon)
Option C: Glance API enhancement (requires cross-project coordination)

REFERENCES

Original review: https://review.opendev.org/c/openstack/horizon/+/986478
Thread: CMT-RAD-1 (substring matching suggestion)
Reviewer: Radomir Dopieralski
```

---

### Ticket 2 of 2: Add Owner Filter to Images Table

#### Panel 1: Copy/Paste for Jira Web UI (Plain English)

**Project:** OSPRH  
**Issue Type:** Story  
**Parent:** OSPRH-16422  
**Priority:** Low  
**Labels:** horizon, de-angularize, ux-improvement

**Summary:**
```
Add Owner Filter to Images Table
```

**Description:**
```
Add owner filter choice to ImageFilterAction, allowing users to filter images by project UUID.

TECHNICAL DETAILS

Current state: ImageFilterAction has name, status, disk_format, visibility filters

Proposed change: Add ('owner', _('Owner ='), True) to filter_choices

API support: Glance v2 supports owner param, openstack_dashboard/api/glance.py passes it through

Files affected: openstack_dashboard/dashboards/project/images/images/tables.py lines 206-210

WHY DEFERRED

Deferred pending confirmation from Radomir Dopieralski whether owner filter is needed alongside visibility. Owner filter requires users to know/type project UUID (not user-friendly) -- old tab-based OwnerFilter provided Project/Public/Shared tabs that abstracted away UUIDs. Visibility filter (already added) restores most old filtering capability. Owner would be useful for operators who know project UUIDs, but may not be needed for typical end users.

UX CONSIDERATION

Owner filter requires UUID input (e.g., d3f4f5g6h7i8j9k0l1m2n3o4p5q6r7s8). Consider adding help text or placeholder showing example format.

REFERENCES

Original review: https://review.opendev.org/c/openstack/horizon/+/986478
Thread: CMT-RAD-2 (visibility and owner request)
Reviewer: Radomir Dopieralski
Visibility filter was added via --update-feature on 2026-07-16
```

---

### Ticket 1 of 2: Substring Matching for Image Name Filter

#### Panel 2: Copy/Paste for Jira Web UI (Jira Wiki Format)

**Project:** OSPRH  
**Issue Type:** Story  
**Parent:** OSPRH-16422  
**Priority:** Medium  
**Labels:** horizon, de-angularize, ux-improvement

**Summary:**
```
Substring Matching for Image Name Filter
```

**Description:** (Copy this into Jira's description field - it will render nicely)
```
Replace exact-match image name filter with substring search in both project and admin Images tables.

h3. Technical Details

* Current state: ImageFilterAction uses |name| param with exact match (Glance v2 API limitation)
* Proposed change: Implement substring matching via client-side filtering, hybrid approach, or Glance API enhancement
* Files affected: openstack_dashboard/dashboards/project/images/images/tables.py:206-210, openstack_dashboard/dashboards/admin/images/tables.py

h3. Why Deferred

Deferred due to Glance v2 API limitation -- the name filter performs exact matching only. Changing to substring would require client-side filtering (breaks pagination) or custom hybrid approach not used elsewhere. Radomir Dopieralski marked comment resolved (suggestion, not blocker). Exact-match behavior is consistent with admin Images panel and all other server-side filters in Horizon.

h3. Implementation Options

* Option A: Client-side filtering (breaks pagination for large deployments)
* Option B: Hybrid approach (not used elsewhere in Horizon)
* Option C: Glance API enhancement (requires cross-project coordination)

h3. References

* Original review: https://review.opendev.org/c/openstack/horizon/+/986478
* Thread: CMT-RAD-1 (substring matching suggestion)
* Reviewer: Radomir Dopieralski
```

#### Panel 3: JSON Metadata for Automation

**Using jira-cli tool:**
```bash
jira issue create \
  --type Story \
  --parent OSPRH-16422 \
  --summary "Substring Matching for Image Name Filter" \
  --body "$(cat <<'EOF'
Replace exact-match image name filter with substring search.

TECHNICAL DETAILS
* Current: exact match via Glance API
* Proposed: substring via client-side/hybrid/API enhancement
* Files: openstack_dashboard/dashboards/project/images/images/tables.py:206-210

WHY DEFERRED
Glance API limitation - requires architectural decision on filtering approach.

REFERENCES
https://review.opendev.org/c/openstack/horizon/+/986478
EOF
)" \
  --priority Medium \
  --label horizon \
  --label de-angularize \
  --label ux-improvement
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
    "summary": "Substring Matching for Image Name Filter",
    "description": "Replace exact-match image name filter with substring search in both project and admin Images tables.\n\nh3. Technical Details\n\n* Current state: ImageFilterAction uses |name| param with exact match (Glance v2 API limitation)\n* Proposed change: Implement substring matching via client-side filtering, hybrid approach, or Glance API enhancement\n* Files affected: openstack_dashboard/dashboards/project/images/images/tables.py:206-210, openstack_dashboard/dashboards/admin/images/tables.py\n\nh3. Why Deferred\n\nDeferred due to Glance v2 API limitation -- the name filter performs exact matching only. Changing to substring would require client-side filtering (breaks pagination) or custom hybrid approach not used elsewhere. Radomir Dopieralski marked comment resolved (suggestion, not blocker). Exact-match behavior is consistent with admin Images panel and all other server-side filters in Horizon.\n\nh3. Implementation Options\n\n* Option A: Client-side filtering (breaks pagination for large deployments)\n* Option B: Hybrid approach (not used elsewhere in Horizon)\n* Option C: Glance API enhancement (requires cross-project coordination)\n\nh3. References\n\n* Original review: https://review.opendev.org/c/openstack/horizon/+/986478\n* Thread: CMT-RAD-1 (substring matching suggestion)\n* Reviewer: Radomir Dopieralski",
    "issuetype": {"name": "Story"},
    "priority": {"name": "Medium"},
    "labels": ["horizon", "de-angularize", "ux-improvement"],
    "parent": {"key": "OSPRH-16422"}
  }
}
EOF
```

---

### Ticket 2 of 2: Add Owner Filter to Images Table

#### Panel 2: Copy/Paste for Jira Web UI (Jira Wiki Format)

**Project:** OSPRH  
**Issue Type:** Story  
**Parent:** OSPRH-16422  
**Priority:** Low  
**Labels:** horizon, de-angularize, ux-improvement

**Summary:**
```
Add Owner Filter to Images Table
```

**Description:** (Copy this into Jira's description field - it will render nicely)
```
Add owner filter choice to ImageFilterAction, allowing users to filter images by project UUID.

h3. Technical Details

* Current state: ImageFilterAction has name, status, disk_format, visibility filters
* Proposed change: Add |('owner', _('Owner ='), True)| to filter_choices
* API support: Glance v2 supports owner param, openstack_dashboard/api/glance.py passes it through
* Files affected: openstack_dashboard/dashboards/project/images/images/tables.py:206-210

h3. Why Deferred

Deferred pending confirmation from Radomir Dopieralski whether owner filter is needed alongside visibility. Owner filter requires users to know/type project UUID (not user-friendly) -- old tab-based OwnerFilter provided Project/Public/Shared tabs that abstracted away UUIDs. Visibility filter (already added) restores most old filtering capability. Owner would be useful for operators who know project UUIDs, but may not be needed for typical end users.

h3. UX Consideration

Owner filter requires UUID input (e.g., |d3f4f5g6h7i8j9k0l1m2n3o4p5q6r7s8|). Consider adding help text or placeholder showing example format.

h3. References

* Original review: https://review.opendev.org/c/openstack/horizon/+/986478
* Thread: CMT-RAD-2 (visibility and owner request)
* Reviewer: Radomir Dopieralski
* Visibility filter was added via --update-feature on 2026-07-16
```

#### Panel 3: JSON Metadata for Automation

**Using jira-cli tool:**
```bash
jira issue create \
  --type Story \
  --parent OSPRH-16422 \
  --summary "Add Owner Filter to Images Table" \
  --body "$(cat <<'EOF'
Add owner filter choice to ImageFilterAction, allowing users to filter images by project UUID.

TECHNICAL DETAILS
* Current: name, status, disk_format, visibility filters only
* Proposed: Add owner filter choice
* Files: openstack_dashboard/dashboards/project/images/images/tables.py:206-210

WHY DEFERRED
Pending confirmation if needed - requires UUID input (not user-friendly).

UX CONSIDERATION
Owner filter requires UUID input. Consider help text showing example format.

REFERENCES
https://review.opendev.org/c/openstack/horizon/+/986478
EOF
)" \
  --priority Low \
  --label horizon \
  --label de-angularize \
  --label ux-improvement
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
    "summary": "Add Owner Filter to Images Table",
    "description": "Add owner filter choice to ImageFilterAction, allowing users to filter images by project UUID.\n\nh3. Technical Details\n\n* Current state: ImageFilterAction has name, status, disk_format, visibility filters\n* Proposed change: Add |('owner', _('Owner ='), True)| to filter_choices\n* API support: Glance v2 supports owner param, openstack_dashboard/api/glance.py passes it through\n* Files affected: openstack_dashboard/dashboards/project/images/images/tables.py:206-210\n\nh3. Why Deferred\n\nDeferred pending confirmation from Radomir Dopieralski whether owner filter is needed alongside visibility. Owner filter requires users to know/type project UUID (not user-friendly) -- old tab-based OwnerFilter provided Project/Public/Shared tabs that abstracted away UUIDs. Visibility filter (already added) restores most old filtering capability. Owner would be useful for operators who know project UUIDs, but may not be needed for typical end users.\n\nh3. UX Consideration\n\nOwner filter requires UUID input (e.g., |d3f4f5g6h7i8j9k0l1m2n3o4p5q6r7s8|). Consider adding help text or placeholder showing example format.\n\nh3. References\n\n* Original review: https://review.opendev.org/c/openstack/horizon/+/986478\n* Thread: CMT-RAD-2 (visibility and owner request)\n* Reviewer: Radomir Dopieralski\n* Visibility filter was added via --update-feature on 2026-07-16",
    "issuetype": {"name": "Story"},
    "priority": {"name": "Low"},
    "labels": ["horizon", "de-angularize", "ux-improvement"],
    "parent": {"key": "OSPRH-16422"}
  }
}
EOF
```
