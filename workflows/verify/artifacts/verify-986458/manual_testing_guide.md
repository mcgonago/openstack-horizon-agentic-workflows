# Manual Testing Guide — Images Panel: Activate/Deactivate Row Actions

**Review:** [https://review.opendev.org/c/openstack/horizon/+/986458](https://review.opendev.org/c/openstack/horizon/+/986458)
**Subject:** Add activate/deactivate row actions to Images table
**Recipe:** images
**Generated:** 2026-07-15 17:24 UTC

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

This is the only step that requires SSH into the DevStack VM. The test image
must have actual data uploaded (not just metadata) so Glance marks it as
"active" — the activate/deactivate actions only work on active images.

```bash
virtctl ssh ubuntu@vm/omcgonag-horizon-devstack -n rhos-dfg-ui--runtime-int --identity-file ~/.ssh/id_ed25519

# On the VM:
source ~/devstack/openrc admin demo
openstack image show verify-seed-image 2>/dev/null && openstack image delete verify-seed-image 2>/dev/null || true
dd if=/dev/zero of=/tmp/tiny.img bs=1 count=1
openstack image create --disk-format raw --container-format bare --file /tmp/tiny.img verify-seed-image
rm -f /tmp/tiny.img

# Verify it's active
openstack image show verify-seed-image -f value -c status
# Expected: active

openstack image list | grep verify-seed
exit
```

> **Important:** Do NOT use `--file /dev/null` — Glance returns HTTP 415
> (Unsupported Media Type) for empty uploads. The 1-byte file trick creates a
> valid active image.

**Step 4 — Clone and patch Horizon locally (Terminal 2):**

```bash
git clone https://opendev.org/openstack/horizon.git horizon-review-986458
cd horizon-review-986458
git fetch https://review.opendev.org/openstack/horizon refs/changes/58/986458/latest
git checkout FETCH_HEAD
```

> Replace `refs/changes/58/986458/latest` with the actual patchset
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

> **Tip:** When you change code or `local_settings.py`, Django auto-reloads.
> For settings changes that require a full restart, press `Ctrl+C` and re-run
> the `tox` command.

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
git fetch https://review.opendev.org/openstack/horizon refs/changes/58/986458/latest
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

```bash
source ~/devstack/openrc admin demo
openstack image show verify-seed-image 2>/dev/null && openstack image delete verify-seed-image 2>/dev/null || true
dd if=/dev/zero of=/tmp/tiny.img bs=1 count=1
openstack image create --disk-format raw --container-format bare --file /tmp/tiny.img verify-seed-image
rm -f /tmp/tiny.img
openstack image show verify-seed-image -f value -c status
# Expected: active
exit
```

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
> **CLI commands** (e.g., `openstack image set --protected`) require SSH into
> the DevStack VM regardless of which option you chose. For Option A, open an
> SSH session in a spare terminal when needed.

---

## Group A: Panel Loading

### Test 1: Page Loads Correctly

**Group:** A — Panel Loading
**Automated by:** `recipes/images/panel_loading.py` > `test_page_loads`
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
**Automated by:** `recipes/images/panel_loading.py` > `test_breadcrumb_visible`

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
**Automated by:** `recipes/images/panel_loading.py` > `test_table_visible`
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
**Automated by:** `recipes/images/panel_loading.py` > `test_angular_or_python_detected`

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
**Automated by:** `recipes/images/table_features.py` > `test_search_filter`
**Screenshot:** `after_003_search_filter.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Locate the search/filter input field above the table
3. Type `verify-seed` in the search box
4. Wait 1-2 seconds for the table to filter

#### Expected Result

- [ ] Search input is present and functional
- [ ] Table filters to show only images matching "verify-seed"
- [ ] Clearing the search restores the full list

### Test 6: Column Headers

**Group:** B — Table Features
**Automated by:** `recipes/images/table_features.py` > `test_column_headers`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Examine the table header row

#### Expected Result

- [ ] "Name" column header is present
- [ ] "Status" column header is present
- [ ] Other expected columns visible (Type, Owner, Visibility, Protected, Disk Format, Size)

### Test 7: Row Actions Menu

**Group:** B — Table Features
**Automated by:** `recipes/images/table_features.py` > `test_row_actions_menu`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Find a row with an image you own (e.g., `verify-seed-image`)
3. Look at the actions column on the right side of the row
4. Click the dropdown arrow to see all available actions

#### Expected Result

- [ ] Actions column is present for each row
- [ ] Dropdown reveals multiple actions including: Launch, Create Volume, Edit Image, Update Metadata, **Deactivate Image**, Delete Image
- [ ] Actions are contextual (different images may show different actions)

### Test 8: Batch Actions (Select-All)

**Group:** B — Table Features
**Automated by:** `recipes/images/table_features.py` > `test_batch_actions`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Look for a checkbox in the table header row
3. Click it to select all rows

#### Expected Result

- [ ] Select-all checkbox is present in the header
- [ ] Clicking it selects all visible rows
- [ ] Batch action button(s) become active when rows are selected

---

## Group C: Activate / Deactivate Actions

> These tests verify the core new functionality added by review 986458.
> They test the `DeactivateImage` and `ReactivateImage` `BatchAction` subclasses.
>
> **CLI commands below require SSH into the DevStack VM.** If using Option A,
> open a terminal and run:
> ```bash
> virtctl ssh ubuntu@vm/omcgonag-horizon-devstack -n rhos-dfg-ui--runtime-int --identity-file ~/.ssh/id_ed25519
> source ~/devstack/openrc admin demo
> ```

### Test 9: Deactivate Action Visible on Active Owned Image

**Group:** C — Activate / Deactivate Actions
**Automated by:** `recipes/images/activate_deactivate.py` > `test_deactivate_action_visible_on_active_owned`
**Screenshot:** `after_004_deactivate_action_visible.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Find the `verify-seed-image` row (status should be "Active")
3. Click the dropdown arrow in the actions column
4. Look for **"Deactivate Image"** in the dropdown menu

#### CLI Equivalent

```bash
openstack image show verify-seed-image -f value -c status -c owner
```

> The `allowed()` method checks: `image.status == "active"` and `image.owner == request.user.tenant_id` and `not image.protected`.

#### Expected Result

- [ ] "Deactivate Image" action is visible in the row dropdown
- [ ] Image status is "Active"
- [ ] Image is owned by the current project (admin)

### Test 10: Deactivate Action Hidden on Non-Owned Images

**Group:** C — Activate / Deactivate Actions
**Automated by:** `recipes/images/activate_deactivate.py` > `test_deactivate_action_hidden_on_not_owned`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Find any image row NOT owned by your project (e.g., shared community images)
3. Click the dropdown arrow in the actions column
4. Confirm "Deactivate Image" is **NOT** listed

#### CLI Equivalent

```bash
openstack image list --long | grep -v "$(openstack project show admin -f value -c id)"
```

#### Expected Result

- [ ] "Deactivate Image" does NOT appear for images not owned by your project
- [ ] Other standard actions (Launch, Create Volume) may still appear

### Test 11: Execute Deactivate

**Group:** C — Activate / Deactivate Actions
**Automated by:** `recipes/images/activate_deactivate.py` > `test_execute_deactivate`
**Screenshot:** `after_005_after_deactivate.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Find the `verify-seed-image` row (status: "Active")
3. Click the dropdown arrow > **"Deactivate Image"**
4. A confirmation dialog appears — click **OK** to confirm
5. Wait for the page to refresh (3-5 seconds)
6. Observe the image status has changed

#### CLI Equivalent

```bash
openstack image deactivate verify-seed-image
openstack image show verify-seed-image -f value -c status
```

> Expected status: `deactivated`

#### Expected Result

- [ ] Confirmation dialog appears after clicking Deactivate
- [ ] After confirming, a success message appears (green banner)
- [ ] Image status changes from "Active" to **"Deactivated"**
- [ ] Page does not show errors

### Test 12: Reactivate Action Visible on Deactivated Image

**Group:** C — Activate / Deactivate Actions
**Automated by:** `recipes/images/activate_deactivate.py` > `test_reactivate_action_visible_on_deactivated`
**Screenshot:** `after_006_reactivate_action_visible.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Find the `verify-seed-image` row (status should now be "Deactivated" from Test 11)
3. Click the dropdown arrow in the actions column
4. Look for **"Reactivate Image"** in the dropdown menu
5. Confirm **"Deactivate Image"** is NOT in the dropdown (mutual exclusion)

#### CLI Equivalent

```bash
openstack image show verify-seed-image -f value -c status
```

> Expected: `deactivated`. When deactivated, the `allowed()` method on `ReactivateImage` returns `True` (checks `image.status == "deactivated"`), while `DeactivateImage.allowed()` returns `False`.

#### Expected Result

- [ ] "Reactivate Image" action IS visible
- [ ] "Deactivate Image" action is NOT visible (image is already deactivated)
- [ ] Image status shows "Deactivated"

### Test 13: Execute Reactivate

**Group:** C — Activate / Deactivate Actions
**Automated by:** `recipes/images/activate_deactivate.py` > `test_execute_reactivate`
**Screenshot:** `after_007_after_reactivate.png`

#### GUI Steps

1. Navigate to **Project > Compute > Images**
2. Find the `verify-seed-image` row (status: "Deactivated")
3. Click the dropdown arrow > **"Reactivate Image"**
4. A confirmation dialog appears — click **OK** to confirm
5. Wait for the page to refresh (3-5 seconds)
6. Observe the image status has changed back

#### CLI Equivalent

```bash
openstack image reactivate verify-seed-image
openstack image show verify-seed-image -f value -c status
```

> Expected status: `active`

#### Expected Result

- [ ] Confirmation dialog appears after clicking Reactivate
- [ ] After confirming, a success message appears (green banner)
- [ ] Image status changes from "Deactivated" back to **"Active"**
- [ ] Page does not show errors

### Test 14: Protected Image Does Not Show Deactivate

**Group:** C — Activate / Deactivate Actions
**Automated by:** `recipes/images/activate_deactivate.py` > `test_protected_image_no_deactivate`

#### GUI Steps

1. First, protect the image via CLI (SSH into DevStack VM):
   ```bash
   openstack image set --protected verify-seed-image
   ```
2. Navigate to **Project > Compute > Images**
3. Find the `verify-seed-image` row (now protected)
4. Click the dropdown arrow in the actions column
5. Confirm "Deactivate Image" is **NOT** listed

#### CLI Equivalent

```bash
openstack image show verify-seed-image -f value -c protected
```

> Expected: `True`. The `allowed()` method on `DeactivateImage` returns `False` when `image.protected` is `True`.

#### Expected Result

- [ ] "Deactivate Image" does NOT appear for protected images
- [ ] Other actions may still appear (Edit Image, etc.)

#### Cleanup

```bash
openstack image set --unprotect verify-seed-image
```

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
exit
```

If using Option A, also stop your local Horizon server (`Ctrl+C` in Terminal 2)
and optionally remove the checkout:

```bash
rm -rf horizon-review-986458
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
| 9 | Deactivate visible on active owned | C | [ ] |
| 10 | Deactivate hidden on non-owned | C | [ ] |
| 11 | Execute deactivate | C | [ ] |
| 12 | Reactivate visible on deactivated | C | [ ] |
| 13 | Execute reactivate | C | [ ] |
| 14 | Protected image no deactivate | C | [ ] |
