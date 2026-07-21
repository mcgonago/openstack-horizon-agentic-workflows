# Review 986478 — Add Visibility and Owner Filter Choices — Implementation Specification

**Date:** 2026-07-16
**Status:** DRAFT
**Review:** [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
**Design Doc:** [IOSHAWORKFLOW_REVIEW_986478_ADD_VISIBILITY_OWNER_DESIGN.md](./IOSHAWORKFLOW_REVIEW_986478_ADD_VISIBILITY_OWNER_DESIGN.md)
**Thread:** CMT-RAD-2

---

## 1. File Inventory

| # | File | Action | Purpose |
|---|------|--------|---------|
| 1 | `openstack_dashboard/dashboards/project/images/images/tables.py` | MODIFY | Add visibility and owner to filter_choices |
| 2 | `openstack_dashboard/dashboards/project/images/images/tests.py` | MODIFY | Update test to verify 5 filter choices |

---

## 2. Code Changes

### Change 1: Add visibility and owner to ImageFilterAction.filter_choices

- **File:** `openstack_dashboard/dashboards/project/images/images/tables.py:206-210`
- **Thread:** CMT-RAD-2
- **What the code does now:** ImageFilterAction has 3 filter_choices: name, status, disk_format
- **What needs to change:** Add visibility and owner as additional filter_choices
- **Code change:**
  ```python
  # before
  filter_choices = (
      ('name', _("Image Name ="), True),
      ('status', _('Status ='), True),
      ('disk_format', _('Format ='), True),
  )

  # after
  filter_choices = (
      ('name', _("Image Name ="), True),
      ('status', _('Status ='), True),
      ('disk_format', _('Format ='), True),
      ('visibility', _('Visibility ='), True),
      ('owner', _('Owner (Project ID) ='), True),
  )
  ```
- **Why:** Reviewer Radomir requested both. Both are valid Glance v2 API filter parameters. Adding visibility restores the filtering capability lost when OwnerFilter tabs were removed. Adding owner provides project-ID-based filtering for users who know their project UUID.

### Change 2: Update filter_choices test to expect 5 choices

- **File:** `openstack_dashboard/dashboards/project/images/images/tests.py:363-368`
- **Thread:** CMT-RAD-2 (test verification)
- **What the code does now:** Test asserts filter_choices contain name, status, disk_format (3 items)
- **What needs to change:** Add assertions for visibility and owner
- **Code change:**
  ```python
  # before
  def test_filter_choices_include_name_status_format(self):
      action = tables.ImageFilterAction()
      choice_fields = [c[0] for c in action.filter_choices]
      self.assertIn('name', choice_fields)
      self.assertIn('status', choice_fields)
      self.assertIn('disk_format', choice_fields)

  # after
  def test_filter_choices_include_name_status_format(self):
      action = tables.ImageFilterAction()
      choice_fields = [c[0] for c in action.filter_choices]
      self.assertIn('name', choice_fields)
      self.assertIn('status', choice_fields)
      self.assertIn('disk_format', choice_fields)
      self.assertIn('visibility', choice_fields)
      self.assertIn('owner', choice_fields)
  ```
- **Why:** Test must match the updated filter_choices to prevent regression. Existing assertions for name, status, and disk_format remain; two new assertions verify the additions.

---

## 3. Verification Steps

1. **Lint check:** `tox -e pep8` (same as CI gate `openstack-tox-pep8`)
2. **Unit tests:** `tox -e py311 -- openstack_dashboard/dashboards/project/images/images/tests.py`
3. **Full images test suite:** `tox -e py311 -- openstack_dashboard/dashboards/project/images/tests.py`
4. **Manual verification:** Start Horizon with `tox -e runserver -- 0.0.0.0:9000`, navigate to Project > Compute > Images, verify the filter dropdown shows 5 options: Image Name, Status, Format, Visibility, Owner (Project ID)
5. **Composable with `--verify-patch`:** `/review-tracker 986478 --update-feature PATH --verify-patch`

---

## 4. Rollback

Reverting is trivial — remove the two added lines:

**tables.py:** Delete the `('visibility', ...)` and `('owner', ...)` lines from `filter_choices`.

**tests.py:** Delete the `self.assertIn('visibility', ...)` and `self.assertIn('owner', ...)` lines.

No database migration, no API contract change, no configuration change. The rollback is a 4-line deletion across 2 files.
