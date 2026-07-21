# Bridge Analysis: CMT-RAD-1

**Reviewer:** Radomir Dopieralski
**Review:** [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
**File:** `/PATCHSET_LEVEL`

---

## Comment Evolution

### Original Comment (PS5, 10:13 UTC)

> This looks great, thanks.
>
> I noticed that the image name must match exactly to be shown by the filter, wouldn't it make more sense to make the filter show all images that contain the string?

**Reviewer's ask:** Change the image name filter from exact match to substring/contains match.

---

## Investigation

*Answers: "wouldn't it make more sense to make the filter show all images that contain the string?"*

### 1. How the filter currently works

The `ImageFilterAction` defines `filter_type = "server"` with `filter_choices` that include `('name', _("Image Name ="), True)`. The `True` flag marks it as an API filter.

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

The `get_filters()` method in the view passes the filter field and string directly to the Glance API:

**Source:** [`openstack_dashboard/dashboards/project/images/views.py:60-66`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/views.py#L60-L66)
```python
def get_filters(self):
    filters = {}
    filter_field = self.table.get_filter_field()
    filter_string = self.table.get_filter_string()
    filter_action = self.table._meta._filter_action
    if filter_field and filter_string and (
            filter_action and filter_action.is_api_filter(filter_field)):
        filters[filter_field] = filter_string
    return filters
```

This passes `{'name': 'exact-string'}` to `api.glance.image_list_detailed()`, which forwards it to the Glance v2 API. The Glance v2 API `name` filter performs **exact matching** by default.

### 2. Is this a Horizon limitation or a Glance API limitation?

**This is a Glance API behavior.** The Glance v2 `name` filter does exact match. There is no built-in `name__contains` or substring parameter in the Glance v2 images API.

However, this is the same exact behavior that the **admin panel** has:

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

The admin panel uses the same `"Image Name ="` label and exact-match behavior. This review mirrors the admin filter pattern, which is the intended behavior.

### 3. Convention across the codebase

Every server-type filter in the codebase uses exact-match labels (`=`). No panel uses `~` (contains) labels:

| Panel | Filter | Label |
|-------|--------|-------|
| Admin Images | name | `"Image Name ="` |
| Admin Instances | name | `"Instance Name ="` |
| Admin Volumes | name | `"Volume Name ="` |
| Identity Projects | name | `"Project Name ="` |
| Identity Users | name | `"User Name ="` |
| **Project Images (this patch)** | name | **`"Image Name ="`** |

All use exact match because they rely on server-side API filtering, and most OpenStack APIs filter by exact match on name.

### 4. Could we add substring matching?

To support substring filtering, the approach would be either:

1. **Client-side filtering** — Change `filter_type` from `"server"` to `"query"`, which performs JavaScript-based client-side filtering on already-loaded data. This supports substring matching but breaks server-side pagination (loads ALL images, then filters in browser). Not suitable for large deployments.

2. **Hybrid approach** — Keep the API filter for pagination but add a secondary client-side pass. This would require custom `FilterAction` subclass code that no other panel uses.

3. **Glance API extension** — Glance doesn't natively support substring name filtering in v2 API.

### 5. Verdict

**The exact-match behavior is CONSISTENT with all other panels and is a Glance API limitation, not a code choice.** The `"Image Name ="` label correctly signals exact match to the user. Changing to substring would either require client-side filtering (breaking pagination) or a custom hybrid that no other Horizon panel implements.

Radomir's comment is marked `unresolved: false`, suggesting this is a suggestion rather than a blocker. The right response is to acknowledge the limitation and explain that it matches the existing admin panel behavior.

---

## Suggested Response

> Thanks! The exact-match behavior is inherited from the Glance v2 API -- the name filter doesn't support substring matching. This matches how the admin Images filter works too (same filter_choices with "Image Name ="). Changing to substring would require either client-side filtering (which breaks pagination for large image lists) or a hybrid approach that no other panel uses. I kept it consistent with the admin pattern, but happy to explore a follow-up if there's demand for substring search.

---

## References

- [`openstack_dashboard/dashboards/project/images/images/tables.py:204-210`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py#L204-L210) — ImageFilterAction definition
- [`openstack_dashboard/dashboards/project/images/views.py:60-66`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/views.py#L60-L66) — get_filters() passing name to Glance API
- [`openstack_dashboard/dashboards/admin/images/tables.py:78-84`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/admin/images/tables.py#L78-L84) — AdminImageFilterAction with same exact-match behavior
- [`openstack_dashboard/api/glance.py:259`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/glance.py#L259) — filters passed directly to Glance client
