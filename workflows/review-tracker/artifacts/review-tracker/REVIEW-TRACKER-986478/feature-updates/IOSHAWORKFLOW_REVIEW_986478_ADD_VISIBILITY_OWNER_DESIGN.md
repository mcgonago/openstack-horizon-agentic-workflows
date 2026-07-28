# Review 986478 — Add Visibility and Owner Filter Choices — Design Specification

**Date:** 2026-07-16
**Status:** DRAFT
**Review:** [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
**Companion:** [Implementation Specification](IOSHAWORKFLOW_REVIEW_986478_ADD_VISIBILITY_OWNER_IMPLEMENTATION.md)
**Bridge Analysis:** [CMT-RAD-2 Deep Dive](../../openstack-horizon-agentic-workflows-review-tracker/workflows/review-tracker/artifacts/review-tracker/bridge-artifacts/986478-cmt-rad-2-analysis.md)
**Tracker:** [tracker-986478.md](../../openstack-horizon-agentic-workflows-review-tracker/workflows/review-tracker/artifacts/review-tracker/tracker-986478.md)
**Thread:** CMT-RAD-2

---

## 1. Problem Statement

Radomir Dopieralski reviewed PS5 of review 986478 and gave Code-Review -1 with an inline comment on [`tables.py:210`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L210):

> could we also have visibility and owner as the possible filters?

The current `ImageFilterAction.filter_choices` has only three filter options: `name`, `status`, and `disk_format`. This is an actionable request from a core reviewer that blocks merge.

---

## 2. Context and Motivation

Review 986478 replaces the tab-based `OwnerFilter` (a client-side `FixedFilterAction` with tabs: Project, Public, Shared, etc.) with `ImageFilterAction` (a server-side `FilterAction` with a search dropdown). This is part of the broader de-angularize initiative tracked by `blueprint removing-angularjs`.

The old `OwnerFilter` provided implicit filtering by ownership and visibility through its tab categories. Users could click "Public" to see only public images, or "Project" to see only their own. The new `ImageFilterAction` currently only filters by name, status, and disk_format — losing the visibility/ownership filtering capability entirely.

Adding `visibility` as a server-side filter restores this lost capability in the new paradigm. Instead of fixed tab buttons, users can select "Visibility =" from the dropdown and type `public`, `private`, `shared`, or `community`.

---

## 3. Glance v2 API Analysis

Both `visibility` and `owner` are valid Glance v2 API filter parameters, already supported by Horizon's `glance.py`:

**visibility:**
- Listed in `KNOWN_PROPERTIES` at [`glance.py:135`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/glance.py#L135)
- Has normalization via `_normalize_is_public_filter()` at [`glance.py:147-158`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/glance.py#L147-L158)
- Valid values: `public`, `private`, `shared`, `community`
- Translates the legacy `is_public` filter to the v2 `visibility` parameter

**owner:**
- Listed in `KNOWN_PROPERTIES` at [`glance.py:142`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/glance.py#L142)
- Has normalization via `_normalize_owner_id_filter()` at [`glance.py:160-168`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/glance.py#L160-L168)
- Expects a project UUID string (e.g., `a1b2c3d4-e5f6-7890-...`)
- Translates `project_id` to `owner` for Glance v2 compatibility

Both parameters are passed through to the Glance API via `image_list_detailed()` without any additional transformation needed by the `ImageFilterAction` — the existing `get_filters()` in `views.py` already handles this.

---

## 4. How Visibility Restores Lost Capability

The old `OwnerFilter.get_fixed_buttons()` created tab buttons:
- **Project** — images owned by `request.user.tenant_id`
- **Public** — images with `visibility=public`
- **Shared with Me** / **Non-Public from Other Projects** — filtered by owner != self

The old `OwnerFilter.categorize()` performed **client-side** sorting of images into these categories using `get_image_categories()`. This client-side approach broke with server-side pagination — the whole point of the migration to `ImageFilterAction`.

Adding `visibility` as a server-side filter lets users query Glance directly:
- `visibility=public` — replaces the "Public" tab
- `visibility=private` — shows only private images
- `visibility=shared` — replaces "Shared with Me" tab
- `visibility=community` — community images

This is a **semantic match, not a 1:1 functional match**. The old tabs were pre-configured buttons; the new approach requires the user to know the value to type. However, it achieves the same filtering power through the Glance API rather than client-side categorization, which is the correct approach for server-side pagination.

---

## 5. The Owner Filter Trade-off

The `owner` filter requires the user to type a project UUID (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`). This is notably less user-friendly than the old `OwnerFilter` tabs, which automatically filtered by `request.user.tenant_id` behind the scenes.

With a server-side filter, there is no such abstraction — the user must know and type the full UUID. There is no project name-to-ID resolution in the filter widget.

However:
- Radomir **explicitly asked** for both `visibility` and `owner`
- The `owner` filter is technically valid and may be useful for admin-like users who know their project IDs
- The label `Owner (Project ID) =` makes clear that a UUID is expected
- Users who don't know the UUID can use `visibility` instead for most use cases

A follow-up review could add a more user-friendly owner filter (e.g., a project selector dropdown), but that's a significantly larger change involving JavaScript and API lookups.

---

## 6. Comparison with Admin Panel

The admin `AdminImageFilterAction` at [`admin/images/tables.py:78-84`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L78-L84) has five filter choices: `name`, `status`, `disk_format`, `size_min`, `size_max`. It does **not** include `visibility` or `owner`.

The project panel is not required to match the admin panel exactly — the two panels serve different audiences. The admin panel has a separate `Tenant` column that shows the project owner, and admins see all images regardless of ownership.

Adding `visibility`/`owner` to the admin panel is a valid follow-up but is out of scope for this review.

---

## 7. Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Add `visibility`? | **Yes** | Restores lost filtering capability, valid Glance v2 param, straightforward 1-line addition |
| Add `owner`? | **Yes** | Radomir explicitly requested it, valid Glance v2 param, label clarifies UUID expected |
| Label for visibility | `'Visibility ='` | Consistent with existing `=` label pattern across all Horizon filter choices |
| Label for owner | `'Owner (Project ID) ='` | Clarifies that a UUID is expected, not a project name |
| Update admin panel too? | **No** (out of scope) | Separate review if desired; admin has different filtering needs |
| Test changes needed? | **Yes** | Existing `test_filter_choices_include_name_status_format` asserts exactly 3 filter choices; must add assertions for `visibility` and `owner` |
