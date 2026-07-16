# Manual Testing Guide — Images Panel: Server-Side Filter Action

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986478](https://review.opendev.org/c/openstack/horizon/+/986478)
**Subject:** Update filtering in the Images table
**Recipe:** images-filter
**Generated:** 2026-07-15 20:20 UTC

> This guide walks through every automated test as a manual, click-by-click
> procedure. Follow each section in order, checking off items as you go.
> Use this while waiting for Zuul CI results on your Gerrit reviews.

---

## Prerequisites

Choose one of the two environment options below. **Option A is recommended** —
it runs Horizon locally on your laptop using `tox -e runserver`, which is faster
to iterate on and only requires SSH into the DevStack VM for creating test data.

---

### Option A — Local Development Server (Recommended)

You need three terminal sessions and a browser.

**Step 1 — Port-forward Keystone from the ITUp VM (Terminal 1):**

This gives your local Horizon access to Keystone for authentication and the
OpenStack APIs. Keep this terminal open for the entire session.

```bash
oc login --token=sha256~<YOUR_TOKEN> --server=https://api.prod-stable-spoke1-dc-rdu3.itup.redhat.com:6443
virtctl port-forward vm/omcgonag-horizon-devstack 5080:80 -n rhos-dfg-ui--runtime-int
```

**Step 2 — iptables redirect (Terminal 2, one-time):**

Route local port 80 to the forwarded port so Horizon can reach Keystone at
`http://127.0.0.1/identity/v3`:

```bash
sudo iptables -t nat -A OUTPUT -o lo -p tcp --dport 80 -j REDIRECT --to-port 5080
curl -s http://127.0.0.1/identity/v3 | python3 -m json.tool | head -5
```

You should see a JSON response with Keystone version info. If not, check your
port-forward in Terminal 1.

**Step 3 — Create test data on the VM (Terminal 2, one-time):**

This is the only step that requires SSH into the DevStack VM. We need multiple
images with different attributes to exercise the filter functionality.

```bash
virtctl ssh ubuntu@vm/omcgonag-horizon-devstack -n rhos-dfg-ui--runtime-int --identity-file ~/.ssh/id_ed25519

# On the VM:
source ~/devstack/openrc admin demo

# Create temp files for upload
dd if=/dev/zero of=/tmp/tiny.img bs=1 count=1
qemu-img create -f qcow2 /tmp/tiny.qcow2 1M

# Clean up any existing test images
for img in verify-seed-image verify-filter-qcow2 verify-filter-raw2; do
  openstack image set --unprotect "$img" 2>/dev/null
  openstack image set --activate "$img" 2>/dev/null
  openstack image delete "$img" 2>/dev/null
done

# Create 3 images with different formats
openstack image create --disk-format raw --container-format bare --file /tmp/tiny.img verify-seed-image
openstack image create --disk-format qcow2 --container-format bare --file /tmp/tiny.qcow2 verify-filter-qcow2
openstack image create --disk-format raw --container-format bare --file /tmp/tiny.img verify-filter-raw2

# Deactivate one for status filter testing
openstack image set --deactivate verify-filter-raw2

# Verify
openstack image list --long -c Name -c Status -c "Disk Format" | grep verify
# Expected:
# | verify-seed-image    | active      | raw   |
# | verify-filter-qcow2  | active      | qcow2 |
# | verify-filter-raw2   | deactivated | raw   |

rm -f /tmp/tiny.img /tmp/tiny.qcow2
exit
```

**Step 4 — Clone and patch Horizon locally (Terminal 2):**

```bash
git clone https://opendev.org/openstack/horizon.git horizon-review-986478
cd horizon-review-986478
git fetch https://review.opendev.org/openstack/horizon refs/changes/78/986478/latest
git checkout FETCH_HEAD
```

> Replace `refs/changes/78/986478/latest` with the actual patchset
> ref from Gerrit (visible in the Download dropdown on the review page).

**Step 5 — Create local_settings.py (Terminal 2):**

Create the file `openstack_dashboard/local/local_settings.py` with the
following content:

```python
import os
from openstack_dashboard.defaults import *

DEBUG = True
ALLOWED_HOSTS = ['*']

OPENSTACK_HOST = '127.0.0.1'
OPENSTACK_KEYSTONE_URL = 'http://127.0.0.1/identity/v3'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

ANGULAR_FEATURES = {
    'images_panel': False,
}
```

> Setting `images_panel` to `False` ensures the Python/Django backend is used
> (not AngularJS). This is the panel version under test.

**Step 6 — Start Horizon (Terminal 2):**

```bash
tox -e runserver -- 0.0.0.0:9000
```

Wait for the Django development server to start. You should see:

```
Starting development server at http://0.0.0.0:9000/
```

**Step 7 — Open the browser:**

1. Open `http://localhost:9000`
2. Login: `admin` / `secret`
3. Navigate to **Project > Compute > Images**

> **Your Horizon URL for all tests below:** `http://localhost:9000`

---

### Option B — DevStack VM (Alternative)

Use this approach if you prefer to test against the Apache-served Horizon
running directly on the DevStack VM. All testing happens on the VM — no local
Horizon checkout is needed.

You need two terminal sessions and a browser.

**Terminal 1 — Port forwarding from ITUp VM:**

```bash
oc login --token=sha256~<YOUR_TOKEN> --server=https://api.prod-stable-spoke1-dc-rdu3.itup.redhat.com:6443
virtctl port-forward vm/omcgonag-horizon-devstack 5080:80 -n rhos-dfg-ui--runtime-int
```

**Terminal 2 — iptables redirect:**

```bash
sudo iptables -t nat -A OUTPUT -o lo -p tcp --dport 80 -j REDIRECT --to-port 5080
curl -s http://127.0.0.1/identity/v3 | python3 -m json.tool | head -5
```

**Apply the patch on the DevStack VM:**

```bash
virtctl ssh ubuntu@vm/omcgonag-horizon-devstack -n rhos-dfg-ui--runtime-int --identity-file ~/.ssh/id_ed25519

# On the VM:
cd /opt/stack/horizon
git fetch https://review.opendev.org/openstack/horizon refs/changes/78/986478/latest
git checkout FETCH_HEAD
sudo systemctl restart apache2
```

**Configure the panel on the VM:**

Edit `openstack_dashboard/local/local_settings.d/_9999_custom.py`:

| Setting | AngularJS (Before) | Python (After) |
|---------|-------------------|----------------|
| `ANGULAR_FEATURES['images_panel']` | `True` | `False` |

After changing, restart Apache: `sudo systemctl restart apache2`.

**Create test data on the VM:**

Follow Step 3 from Option A above (the same seed image commands).

**Browser:**

1. Open `http://127.0.0.1/dashboard/`
2. Login: `admin` / `secret`
3. Navigate to **Project > Compute > Images**

> **Your Horizon URL for all tests below:** `http://127.0.0.1/dashboard/`

---

## Running the Tests

> **URL reminder:**
> - Option A (local): `http://localhost:9000`
> - Option B (DevStack): `http://127.0.0.1/dashboard/`
>
> The GUI steps below say "Navigate to **Project > Compute > Images**" — use
> whichever URL matches your chosen option.
>
> **CLI commands** (e.g., `openstack image list`) require SSH into the DevStack
> VM regardless of which option you chose.

---

## Group A: Panel Loading

### Test 1: Page Loads Correctly

**Group:** A — Panel Loading
**Automated by:** `recipes/images-filter/panel_loading.py` > `test_page_loads`
**Screenshot:** `after_001_panel_loaded.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images** (left sidebar)
2. Wait for the page to fully load (spinner disappears)
3. Observe that the page title reads **"Images"**

#### CLI Equivalent

```bash
openstack image list
```

> Glance API call Horizon makes to populate the table. Issues `GET /v2/images`.

#### Expected Result

- [ ] Page loads without errors (no 500, no blank page)
- [ ] Title bar shows "Images"
- [ ] A table is visible showing available images
- [ ] No JavaScript console errors (open DevTools > Console)

### Test 2: Breadcrumb Visible

**Group:** A — Panel Loading
**Automated by:** `recipes/images-filter/panel_loading.py` > `test_breadcrumb_visible`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Look at the breadcrumb trail near the top of the content area
3. Verify it reads: **Project > Compute > Images**

#### Expected Result

- [ ] Breadcrumb is visible below the top navbar
- [ ] Path shows: `Project > Compute > Images`
- [ ] Each breadcrumb segment is a clickable link (except "Images")

### Test 3: Table Visible

**Group:** A — Panel Loading
**Automated by:** `recipes/images-filter/panel_loading.py` > `test_table_visible`
**Screenshot:** `after_002_table_visible.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Confirm that a data table is visible with at least one row

#### Expected Result

- [ ] Table element is present on the page
- [ ] At least the `verify-seed-image` row is visible
- [ ] Table has standard formatting (striped rows, header row)

### Test 4: Panel Type Detection (Python vs Angular)

**Group:** A — Panel Loading
**Automated by:** `recipes/images-filter/panel_loading.py` > `test_angular_or_python_detected`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Open browser DevTools (F12) > Elements tab
3. Search for `hz-resource-table` — if present, panel is **AngularJS**
4. Search for `table.datatable` or `table.table` — if present, panel is **Python/Django**

#### Expected Result

- [ ] Panel is using **Python/Django** table (no `hz-resource-table` element)
- [ ] Standard Django `<table>` element is rendered

---

## Group B: Table Features

### Test 5: Search/Filter

**Group:** B — Table Features
**Automated by:** `recipes/images-filter/table_features.py` > `test_search_filter`
**Screenshot:** `after_003_search_filter.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Locate the filter area above the table — you should see:
   - A **dropdown** for selecting the filter field (Image Name, Status, Disk Format)
   - A **text input** for entering the filter value
   - A **"Filter"** button
3. Select **"Image Name ="** from the dropdown
4. Type `verify-seed` in the text input
5. Click **Filter** (or press Enter)

#### Expected Result

- [ ] Filter area is present with dropdown + text input + button
- [ ] Table filters to show only images matching "verify-seed"
- [ ] The old tab-based filter (Project / Public) is NOT visible

### Test 6: Column Headers

**Group:** B — Table Features
**Automated by:** `recipes/images-filter/table_features.py` > `test_column_headers`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Examine the table header row

#### Expected Result

- [ ] "Name" column header is present
- [ ] "Status" column header is present
- [ ] Other expected columns visible (Type, Owner, Visibility, Protected, Disk Format, Size)

### Test 7: Row Actions Menu

**Group:** B — Table Features
**Automated by:** `recipes/images-filter/table_features.py` > `test_row_actions_menu`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Find a row with an image you own (e.g., `verify-seed-image`)
3. Look at the actions column on the right side of the row
4. Click the dropdown arrow to see all available actions

#### Expected Result

- [ ] Actions column is present for each row
- [ ] Dropdown reveals actions including: Launch, Create Volume, Edit Image, Update Metadata, Delete Image
- [ ] Actions are contextual (different images may show different actions)

### Test 8: Batch Actions (Select-All)

**Group:** B — Table Features
**Automated by:** `recipes/images-filter/table_features.py` > `test_batch_actions`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Look for a checkbox in the table header row
3. Click it to select all rows

#### Expected Result

- [ ] Select-all checkbox is present in the header
- [ ] Clicking it selects all visible rows
- [ ] Batch action button(s) become active when rows are selected

---

## Group C: Filter Action

> These tests verify the core new functionality added by review 986478.
> They test the `ImageFilterAction` class which replaces the old tab-based
> `OwnerFilter` with a server-side search dropdown supporting name, status,
> and disk_format filters.
>
> **Test data required:** Three images with different attributes (see Prerequisites).

### Test 9: Filter Dropdown Visible

**Group:** C — Filter Action
**Automated by:** `recipes/images-filter/filter_actions.py` > `test_filter_dropdown_visible`
**Screenshot:** `after_004_filter_dropdown_visible.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Look above the table for the filter area
3. Verify three UI elements are present:
   - A **dropdown** with options: "Image Name =", "Status =", "Disk Format ="
   - A **text input** field
   - A **"Filter"** submit button

#### Expected Result

- [ ] Filter dropdown (themable-select) is visible
- [ ] Text input field is visible
- [ ] "Filter" button is visible
- [ ] Dropdown contains the three expected filter choices

### Test 10: OwnerFilter Tabs Gone

**Group:** C — Filter Action
**Automated by:** `recipes/images-filter/filter_actions.py` > `test_owner_filter_tabs_gone`
**Screenshot:** `after_005_owner_filter_tabs_gone.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Look for the old tab-based filter buttons that said **"Project"**, **"Public"**, **"Shared with Me"**
3. Confirm they are **NOT** present

#### Expected Result

- [ ] No "Project" / "Public" / "Shared with Me" filter tabs/buttons
- [ ] No `div.table_filter.btn-group` element in the page
- [ ] The new dropdown filter (Test 9) has replaced the tabs entirely

### Test 11: Filter by Name

**Group:** C — Filter Action
**Automated by:** `recipes/images-filter/filter_actions.py` > `test_filter_by_name`
**Screenshot:** `after_006_filter_by_name.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Select **"Image Name ="** from the filter dropdown
3. Type `verify-seed-image` in the text input
4. Click **Filter**
5. Observe the table results

#### CLI Equivalent

```bash
openstack image list --name verify-seed-image
```

> The filter sends `?name=verify-seed-image` to the Glance API via
> `get_filters()` in `views.py`.

#### Expected Result

- [ ] Table shows only `verify-seed-image` (the name-matched image)
- [ ] `verify-filter-qcow2` and `verify-filter-raw2` are NOT visible
- [ ] The filter is server-side (not just client-side text hiding)

### Test 12: Filter by Status

**Group:** C — Filter Action
**Automated by:** `recipes/images-filter/filter_actions.py` > `test_filter_by_status`
**Screenshot:** `after_007_filter_by_status.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images** (clear any previous filter first)
2. Select **"Status ="** from the filter dropdown
3. Type `active` in the text input
4. Click **Filter**
5. Observe the table results

#### CLI Equivalent

```bash
openstack image list --status active
```

#### Expected Result

- [ ] Table shows only active images (`verify-seed-image`, `verify-filter-qcow2`)
- [ ] `verify-filter-raw2` (deactivated) is NOT visible
- [ ] Filter correctly applies server-side status filtering

### Test 13: Filter by Disk Format

**Group:** C — Filter Action
**Automated by:** `recipes/images-filter/filter_actions.py` > `test_filter_by_disk_format`
**Screenshot:** `after_008_filter_by_disk_format.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images** (clear any previous filter first)
2. Select **"Disk Format ="** from the filter dropdown
3. Type `raw` in the text input
4. Click **Filter**
5. Observe the table results

#### CLI Equivalent

```bash
openstack image list --property disk_format=raw
```

#### Expected Result

- [ ] Table shows only raw-format images (`verify-seed-image`, `verify-filter-raw2`)
- [ ] `verify-filter-qcow2` (qcow2 format) is NOT visible
- [ ] Filter correctly passes `disk_format=raw` to the Glance API

### Test 14: Clear Filter Restores All Images

**Group:** C — Filter Action
**Automated by:** `recipes/images-filter/filter_actions.py` > `test_clear_filter_restores_all`
**Screenshot:** `after_009_clear_filter_restores_all.png`

#### GUI Steps

1. Apply any filter (e.g., filter by name = `verify-seed-image`)
2. Verify the table is filtered (fewer rows)
3. Clear the text input field (delete all text)
4. Click **Filter** (or press Enter)
5. Observe the table results

#### Expected Result

- [ ] Table restores to showing all images (same as before filtering)
- [ ] All three test images are visible again
- [ ] No residual filter state

---

## Cleanup

After all tests are complete, clean up test data. SSH into the DevStack VM
(if not already connected):

```bash
virtctl ssh ubuntu@vm/omcgonag-horizon-devstack -n rhos-dfg-ui--runtime-int --identity-file ~/.ssh/id_ed25519

source ~/devstack/openrc admin demo
openstack image set --unprotect verify-seed-image 2>/dev/null || true
openstack image set --activate verify-seed-image 2>/dev/null || true
openstack image delete verify-seed-image 2>/dev/null || true
openstack image delete verify-filter-qcow2 2>/dev/null || true
openstack image set --activate verify-filter-raw2 2>/dev/null || true
openstack image delete verify-filter-raw2 2>/dev/null || true
exit
```

If using Option A, also stop your local Horizon server (`Ctrl+C` in Terminal 2)
and optionally remove the checkout:

```bash
rm -rf horizon-review-986478
```

---

## Summary Checklist

| # | Test | Group | Status |
|---|------|-------|--------|
| 1 | Page loads correctly | A | [ ] |
| 2 | Breadcrumb visible | A | [ ] |
| 3 | Table visible | A | [ ] |
| 4 | Panel type detection | A | [ ] |
| 5 | Search/filter | B | [ ] |
| 6 | Column headers | B | [ ] |
| 7 | Row actions menu | B | [ ] |
| 8 | Batch actions | B | [ ] |
| 9 | Filter dropdown visible | C | [ ] |
| 10 | OwnerFilter tabs gone | C | [ ] |
| 11 | Filter by name | C | [ ] |
| 12 | Filter by status | C | [ ] |
| 13 | Filter by disk format | C | [ ] |
| 14 | Clear filter restores all | C | [ ] |
