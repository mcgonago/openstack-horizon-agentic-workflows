# Code Review — Review 986478

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
**Title:** Update filtering in the Images table
**Author:** Owen McGonagle
**Topic:** de-angularize
**Patchset:** PS2
**Verdict:** COMMENT

---

## Summary

This patch replaces the tab-based `OwnerFilter` (Project / Public / Other tabs) with a
server-side `ImageFilterAction` search dropdown in the project Images table. Users can now
filter images by name, status, or disk format via the Glance API. The implementation mirrors
the existing admin Images filter pattern and includes tests and a release note.

## Blockers

None.

## Suggestions

### 1. Missing `disk_format` → `container_format` mapping for Docker images

The admin images view at [`openstack_dashboard/dashboards/admin/images/views.py:139-143`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/views.py#L139-L143) includes special handling when `disk_format` filter is set to `docker` — it maps the query to `container_format=docker` instead, since Docker images are stored with `disk_format=raw` and `container_format=docker` in Glance.

The project view's `get_filters()` passes `disk_format` through directly, which means searching for "docker" format images would return no results.

**Recommended:** Either add the same docker format mapping, or remove `disk_format` from the filter choices if the special handling isn't worth adding.

### 2. Defensive `filter_action and` guard is inconsistent with admin pattern

The project view's [`get_filters()`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/views.py#L60-L66) adds a `filter_action and` guard before calling `is_api_filter()`:

```python
if filter_field and filter_string and (
        filter_action and filter_action.is_api_filter(filter_field)):
```

The admin view at [`views.py:121-122`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/views.py#L121-L122) omits this guard:

```python
if filter_field and filter_string and (
        filter_action.is_api_filter(filter_field)):
```

The guard is harmless but creates inconsistency. Either the guard is necessary (and should be added to the admin view too) or it's unnecessary (and should be removed here to match the pattern).

### 3. UX change from tabs to search — intentional?

The `OwnerFilter` provided tab-based category filtering (Project / Public / Other) which was zero-click — users saw categorized tabs immediately. The new `ImageFilterAction` requires typing a search term. This is a different UX paradigm. If both are desired, both could coexist (some tables have both `FixedFilterAction` and `FilterAction`). Worth confirming the intent is to fully replace tabs with search.

## Notes

- **CI status:** Zuul Verified-1 on PS2 — build failed. Must be addressed before the review can proceed.
- **Commit message:** Tatiana requested adding `Partially-Implements: blueprint removing-angularjs` since the topic is `de-angularize`.
- **Tests:** Good coverage — 4 tests verify the filter action presence, type, choices, and OwnerFilter removal.
- **Release note:** Present and well-written.
- **Plugin-API:** No concern — changes are in `openstack_dashboard/`, not `horizon/`.
