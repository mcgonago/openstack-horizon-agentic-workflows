# Bridge Analysis: CMT-RAD-2

**Reviewer:** Radomir Dopieralski
**Review:** [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
**File:** [`openstack_dashboard/dashboards/project/images/images/tables.py:210`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L210)

---

## Comment Evolution

### Original Comment (PS5, 10:13 UTC)

> could we also have visibility and owner as the possible filters?

**Reviewer's ask:** Add `visibility` and `owner` to the `filter_choices` tuple so users can filter images by visibility (public/private/shared/community) and owner (project ID).

---

## Investigation

*Answers: "could we also have visibility and owner as the possible filters?"*

### 1. Current filter_choices

The patch adds three filter choices that mirror the admin panel:

**Source:** [`openstack_dashboard/dashboards/project/images/images/tables.py:204-210`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L204-L210)
```python
class ImageFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = (
        ('name', _("Image Name ="), True),
        ('status', _('Status ='), True),
        ('disk_format', _('Format ='), True),
    )
```

### 2. Does the Glance API support visibility and owner filters?

**Yes.** The Glance v2 API supports both `visibility` and `owner` as query parameters. Horizon's `glance.py` already normalizes these:

**Source:** [`openstack_dashboard/api/glance.py:135-142`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/glance.py#L135-L142)
```python
# Glance v2 image attributes used for filtering
'visibility', 'protected', 'disk_format',
...
'status', 'size', 'owner', 'id', 'updated_at',
```

And the normalization functions explicitly handle both:

**Source:** [`openstack_dashboard/api/glance.py:147-168`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/glance.py#L147-L168)
```python
def _normalize_is_public_filter(filters):
    # Glance v2 uses filter 'visibility' ('public', 'private', ...).
    ...

def _normalize_owner_id_filter(filters):
    # Glance v2 uses filter 'owner' (Project ID).
    ...
```

### 3. Does the admin panel have these filters?

**No.** The admin `AdminImageFilterAction` does not include `visibility` or `owner` either:

**Source:** [`openstack_dashboard/dashboards/admin/images/tables.py:78-84`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L78-L84)
```python
class AdminImageFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = (('name', _("Image Name ="), True),
                      ('status', _('Status ='), True),
                      ('disk_format', _('Format ='), True),
                      ('size_min', _('Min. Size (MB) ='), True),
                      ('size_max', _('Max. Size (MB) ='), True))
```

However, the admin panel has a separate `tenant` column that shows the project owner, and images are shown unfiltered (admin sees all images regardless of ownership).

### 4. What the old OwnerFilter provided

The patch removes `OwnerFilter` (a `FixedFilterAction` that did **client-side** tab-based filtering). The old `OwnerFilter` categorized images into tabs: "Project", "Public", "Non-Public from Other Projects", etc. This was a different UX — fixed tab buttons vs. a dropdown search field.

**Source:** [`openstack_dashboard/dashboards/project/images/images/tables.py:221-260`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L221-L260)
```python
class OwnerFilter(tables.FixedFilterAction):
    def get_fixed_buttons(self):
        buttons = [make_dict(_('Project'), 'project', 'fa-home')]
        ...
        buttons.append(make_dict(_('Public'), 'public', 'fa-group'))
        return buttons

    def categorize(self, table, images):
        # Client-side categorization by owner/visibility
```

Adding `visibility` as a server-side filter would partially restore this filtering capability in the new search-based UI.

### 5. Is this feasible?

**Yes, straightforward.** Adding visibility and owner is a 2-line change:

```python
class ImageFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = (
        ('name', _("Image Name ="), True),
        ('status', _('Status ='), True),
        ('disk_format', _('Format ='), True),
        ('visibility', _('Visibility ='), True),
        ('owner', _('Owner (Project ID) ='), True),
    )
```

Both are valid Glance v2 API filter parameters. The values would be:
- `visibility`: `public`, `private`, `shared`, `community`
- `owner`: a project UUID

### 6. Consideration

The `owner` filter requires users to type a project UUID, which is not user-friendly. The old `OwnerFilter` tabs were more intuitive ("Project", "Public", "Shared"). Adding `visibility` is clearly useful; `owner` is valid but less practical without project name → ID resolution.

### 7. Verdict

**REASONABLE REQUEST.** Adding `visibility` is straightforward and restores filtering capability lost when removing `OwnerFilter`. Adding `owner` is technically valid but less user-friendly (requires UUID). Recommend adding at least `visibility`.

---

## Suggested Response

> Good idea. I can add visibility -- that's a straightforward Glance v2 filter and would restore the ability to filter by public/private/shared/community that the old OwnerFilter tabs provided. For owner, the Glance API expects a project UUID which isn't very user-friendly (the old tabs abstracted this away). I'll add visibility in the next patchset. Want me to add owner as well, or is visibility sufficient?

---

## References

- [`openstack_dashboard/dashboards/project/images/images/tables.py:204-210`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L204-L210) — ImageFilterAction definition
- [`openstack_dashboard/dashboards/project/images/images/tables.py:221-260`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L221-L260) — Old OwnerFilter being replaced
- [`openstack_dashboard/api/glance.py:135-142`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/glance.py#L135-L142) — Glance v2 supported filter attributes
- [`openstack_dashboard/api/glance.py:147-168`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/glance.py#L147-L168) — Visibility and owner filter normalization
- [`openstack_dashboard/dashboards/admin/images/tables.py:78-84`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L78-L84) — Admin filter (no visibility/owner either)
