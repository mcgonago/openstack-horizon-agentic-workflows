# Manual Testing Guide — Key Pairs Panel Deangularization

**Review:** https://review.opendev.org/c/openstack/horizon/+/992714
**Subject:** Switch default Key Pairs panel from AngularJS to Python
**Recipe:** keypairs
**Generated:** 2026-06-24 15:04 UTC

> This guide walks through every automated test as a manual, click-by-click
> procedure. Follow each section in order, checking off items as you go.
> Use this while waiting for Zuul CI results on your Gerrit reviews.

---

## Prerequisites

### Environment Setup

You need two terminal sessions and a browser.

**Terminal 1 — Port forwarding from ITUp VM:**

```bash
oc login --token=sha256~<YOUR_TOKEN> --server=https://api.<cluster>:6443
virtctl port-forward vm/horizon-devstack 5080:80 -n rhos-dfg-ui--runtime-int
```

**Terminal 2 — Horizon dev server:**

```bash
sudo iptables -t nat -A OUTPUT -o lo -p tcp --dport 80 -j REDIRECT --to-port 5080
curl -s http://127.0.0.1/identity/v3 | python3 -m json.tool | head -5
cd <horizon-checkout>
tox -e runserver -- 0.0.0.0:9000
```

**Browser:**

1. Open `http://localhost:9000`
2. Login: `admin` / `secret`
3. Navigate to **Project → Compute → Key Pairs**

### Panel Configuration

Edit `openstack_dashboard/local/local_settings.d/_9999_custom.py`:

| Setting | AngularJS (Before) | Python (After) |
|---------|-------------------|----------------|
| `ANGULAR_FEATURES['key_pairs_panel']` | `True` | `False` |

After changing, restart Horizon: `Ctrl+C` then re-run `tox -e runserver -- 0.0.0.0:9000`.

### Test Data Setup

```bash
source ~/devstack/openrc admin admin
openstack keypair create verify-seed-key > /dev/null 2>&1 || true
openstack keypair create verify-seed-key-2 > /dev/null 2>&1 || true
openstack keypair list
```


---

## Group A: Panel Loading


### Test 1: Page Loads Correctly

**Group:** A — Panel Loading
**Automated by:** `recipes/keypairs/panel_loading.py` → `test_page_loads`
**Screenshot:** `after_001_page_loads.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs** (left sidebar)
2. Wait for the page to fully load (spinner disappears)
3. Observe that the page title reads **"Key Pairs"**

#### CLI Equivalent

```bash
openstack keypair list
```

> Nova API call Horizon makes to populate the table. Issues `GET /compute/v2.1/os-keypairs`.

#### Expected Result

- [ ] Page loads without errors (no 500, no blank page)
- [ ] Title bar shows "Key Pairs"
- [ ] A table is visible (even if empty)
- [ ] No JavaScript console errors (open DevTools → Console)

#### Automation Notes

> Playwright navigates to `/project/key_pairs/`, waits for `table` selector, asserts page title contains 'Key Pairs'. Timeout: 30s.

### Test 2: Breadcrumb Visible

**Group:** A — Panel Loading
**Automated by:** `recipes/keypairs/panel_loading.py` → `test_breadcrumb_visible`
**Screenshot:** `after_002_breadcrumb_visible.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Look at the breadcrumb trail near the top of the content area
3. Verify it reads: **Project > Compute > Key Pairs**

#### CLI Equivalent


> No CLI equivalent — breadcrumbs are a pure UI navigation element.

#### Expected Result

- [ ] Breadcrumb is visible below the top navbar
- [ ] Path shows: `Project > Compute > Key Pairs`
- [ ] Each breadcrumb segment is a clickable link (except "Key Pairs")

#### Automation Notes

> Playwright locates `.breadcrumb` or `nav[aria-label="breadcrumb"]`, asserts text content includes 'Key Pairs'.

### Test 3: Table Visible with Headers

**Group:** A — Panel Loading
**Automated by:** `recipes/keypairs/panel_loading.py` → `test_table_visible`
**Screenshot:** `after_003_table_visible.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Observe the main content area — a table should be present
3. Check the column headers in the table

#### CLI Equivalent

```bash
openstack keypair list -c Name -c Fingerprint -c Type
```

> The table headers correspond to the fields returned by the Nova keypair API.

#### Expected Result

- [ ] Table is present in the content area
- [ ] Column headers include: **Name**, **Fingerprint**, **Type** (at minimum)
- [ ] If keypairs exist, rows are populated with data
- [ ] If no keypairs exist, a "No items to display" message appears

#### Automation Notes

> Playwright asserts `table thead th` elements contain expected header text. Checks for at least 3 column headers.

### Test 4: Panel Implementation Detection

**Group:** A — Panel Loading
**Automated by:** `recipes/keypairs/panel_loading.py` → `test_angular_or_python_detected`
**Screenshot:** `after_004_angular_or_python_detected.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Open browser DevTools (F12) → Elements tab
3. **AngularJS panel:** Look for `<hz-resource-table>` or `ng-` attributes in the DOM
4. **Python panel:** Look for standard Django `<table class="table">` markup without Angular directives

#### CLI Equivalent


> No CLI equivalent — this is a frontend implementation check.

#### Expected Result

- [ ] No `ng-` attributes in the Key Pairs table DOM (Python panel)
- [ ] No `<hz-resource-table>` element
- [ ] Standard HTML `<table>` with Django template rendering
- [ ] The page source (View Source) shows server-rendered HTML rows

#### Automation Notes

> Playwright checks for presence/absence of Angular-specific selectors. Uses `page.query_selector('hz-resource-table')` — null means Python panel.

---

## Group B: Table Features


### Test 5: Search / Filter

**Group:** B — Table Features
**Automated by:** `recipes/keypairs/table_features.py` → `test_search_filter`
**Screenshot:** `after_005_search_filter.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Locate the **search/filter input** above the table
3. Type the name of an existing keypair (e.g., `verify-seed-key`)
4. Observe the table rows filter to show only matching keypairs
5. Clear the search box
6. Verify all keypairs reappear

#### CLI Equivalent

```bash
openstack keypair list | grep verify-seed-key
```

> No server-side filter for keypairs in Nova — the GUI filters client-side.

#### Expected Result

- [ ] Search input is present above the table
- [ ] Typing a name filters table rows in real-time (or on Enter)
- [ ] Only matching rows remain visible
- [ ] Clearing search restores all rows
- [ ] Non-matching search shows "No items to display" or empty table

#### Automation Notes

> Playwright fills the search input, waits for row count to decrease, asserts remaining row text matches the search term.

### Test 6: Column Headers Present

**Group:** B — Table Features
**Automated by:** `recipes/keypairs/table_features.py` → `test_column_headers`
**Screenshot:** `after_006_column_headers.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Examine the table header row
3. Verify all expected columns are present

#### CLI Equivalent

```bash
openstack keypair list
```

> Default columns: Name, Fingerprint, Type.

#### Expected Result

- [ ] **Name** column header present
- [ ] **Fingerprint** column header present
- [ ] **Type** column header present (ssh or x509)
- [ ] Optional: checkbox column for batch selection
- [ ] Optional: Actions column

#### Automation Notes

> Playwright collects `th` text content, asserts set includes {Name, Fingerprint, Type}.

### Test 7: Row Actions Menu

**Group:** B — Table Features
**Automated by:** `recipes/keypairs/table_features.py` → `test_row_actions_menu`
**Screenshot:** `after_007_row_actions_menu.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs** (ensure at least 1 keypair exists)
2. In any keypair row, find the **Actions** dropdown button (right side of row)
3. Click the dropdown
4. Observe the available actions

#### CLI Equivalent


> No CLI equivalent — this tests the UI action menu rendering.

#### Expected Result

- [ ] Each row has an Actions dropdown (or inline action button)
- [ ] Dropdown contains at least: **Delete Key Pair**
- [ ] Actions are clickable (don't click Delete yet — that's Group E)

#### Automation Notes

> Playwright clicks the dropdown trigger, waits for menu to appear, asserts 'Delete' action is present in the menu items.

### Test 8: Batch Actions (Multi-Select)

**Group:** B — Table Features
**Automated by:** `recipes/keypairs/table_features.py` → `test_batch_actions`
**Screenshot:** `after_008_batch_actions.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs** (ensure at least 2 keypairs exist)
2. Click the checkbox on **row 1**
3. Click the checkbox on **row 2**
4. Observe the batch action bar that appears above the table
5. Verify a **"Delete Key Pairs"** button appears

#### CLI Equivalent

```bash
openstack keypair delete test-keypair-1 test-keypair-2
```

> Batch delete via CLI.

#### Expected Result

- [ ] Checkboxes are present on each row
- [ ] Selecting 2+ rows activates the batch action bar
- [ ] Batch action bar shows **"Delete Key Pairs"** button
- [ ] "Select All" checkbox in header selects all visible rows
- [ ] Deselecting all rows hides the batch action bar

#### Automation Notes

> Playwright checks two row checkboxes, waits for batch action bar visibility, asserts delete button text.

### Test 9: Pagination Controls

**Group:** B — Table Features
**Automated by:** `recipes/keypairs/table_features.py` → `test_pagination_controls`
**Screenshot:** `after_009_pagination_controls.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. If fewer than 20 keypairs exist, create more:
   ```bash
   for i in $(seq 1 25); do openstack keypair create "page-test-$i" > /dev/null; done
   ```
3. Look for **Next** / **Previous** pagination links below the table
4. Click **Next** — verify the table shows the next page of results
5. Click **Previous** — verify you return to page 1

#### CLI Equivalent

```bash
openstack keypair list
```

> Nova keypair list doesn't paginate by default in CLI.

#### Expected Result

- [ ] Pagination controls appear when rows exceed page size (default: 20)
- [ ] **Next** link advances to the next page
- [ ] **Previous** link returns to the prior page
- [ ] Page indicator shows current position (e.g., "Displaying 1-20 of 25")
- [ ] If all keypairs fit on one page, pagination controls may be hidden

#### Automation Notes

> Playwright creates 25 test keypairs, navigates to page, checks for pagination elements. Clicks Next, asserts URL or table content changes.

---

## Group C: Create Keypair


### Test 10: Create SSH Keypair

**Group:** C — Create Keypair
**Automated by:** `recipes/keypairs/create_form.py` → `test_create_ssh_keypair`
**Screenshot:** `after_010_create_ssh_keypair.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Click the **"Create Key Pair"** button (top-right above table)
3. In the dialog/form:
   - **Key Pair Name:** `manual-test-ssh`
   - **Key Type:** Select **SSH Key** (typically the default)
4. Click **"Create Key Pair"** (submit button)
5. Wait for success message

#### CLI Equivalent

```bash
openstack keypair create manual-test-ssh
```

> Horizon sends `POST /compute/v2.1/os-keypairs` with `{"keypair": {"name": "...", "type": "ssh"}}`.

#### Expected Result

- [ ] Create dialog opens with Name and Type fields
- [ ] SSH Key is selectable (or default)
- [ ] After submit, a **success notification** appears (green banner)
- [ ] A **private key download** is triggered (PEM file) — see Test C3
- [ ] The dialog closes and the table refreshes

#### Automation Notes

> Playwright clicks create button, fills form, submits, waits for success toast notification.

### Test 11: Create X.509 Keypair

**Group:** C — Create Keypair
**Automated by:** `recipes/keypairs/create_form.py` → `test_create_x509_keypair`
**Screenshot:** `after_011_create_x509_keypair.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Click **"Create Key Pair"**
3. In the dialog:
   - **Key Pair Name:** `manual-test-x509`
   - **Key Type:** Select **X.509 Certificate**
4. Click **"Create Key Pair"**
5. Wait for success

#### CLI Equivalent

```bash
openstack keypair create --type x509 manual-test-x509
```

> Creates an X.509 type keypair via Nova API.

#### Expected Result

- [ ] X.509 type is available in the dropdown
- [ ] Submission succeeds without errors
- [ ] Success notification appears
- [ ] Certificate download may be triggered
- [ ] New keypair appears in table with Type = "x509"

#### Automation Notes

> Same as C1 but selects X.509 from type dropdown. Asserts the new row shows 'x509' in the Type column.

### Test 12: PEM File Download

**Group:** C — Create Keypair
**Automated by:** `recipes/keypairs/create_form.py` → `test_download_pem`
**Screenshot:** `after_012_download_pem.png`

#### GUI Steps

1. Perform Create SSH Keypair (Test C1)
2. After successful creation, observe the browser behavior:
3. A **download dialog** may appear with the `.pem` file
4. OR the private key is displayed in a modal with a **Download** or **Copy** button
5. If displayed in modal: click **Download** or copy the key content
6. Verify the downloaded file contains a valid PEM private key

#### CLI Equivalent

```bash
openstack keypair create download-test > /tmp/download-test.pem
cat /tmp/download-test.pem | head -1
# Should show: -----BEGIN RSA PRIVATE KEY-----
```

> The CLI outputs the private key directly to stdout.

#### Expected Result

- [ ] Private key is offered for download after creation
- [ ] Downloaded file starts with `-----BEGIN RSA PRIVATE KEY-----`
- [ ] File is non-empty and contains valid PEM content
- [ ] User is warned that this is the only time the private key can be downloaded

#### Automation Notes

> Playwright intercepts the download event, saves to temp dir, asserts file starts with PEM header.

### Test 13: Keypair Appears in Table After Create

**Group:** C — Create Keypair
**Automated by:** `recipes/keypairs/create_form.py` → `test_keypair_appears_in_table`
**Screenshot:** `after_013_keypair_appears_in_table.png`

#### GUI Steps

1. Note the current number of rows in the Key Pairs table
2. Create a new keypair (follow Test C1)
3. After success, observe the table
4. Verify the new keypair name appears as a row

#### CLI Equivalent

```bash
openstack keypair list | grep manual-test
```

> Confirms the keypair was persisted via the API.

#### Expected Result

- [ ] Table refreshes automatically after creation (no manual reload needed)
- [ ] New keypair row appears with correct **Name**
- [ ] **Fingerprint** column shows a valid fingerprint hash
- [ ] **Type** column shows "ssh" or "x509" as appropriate
- [ ] Row count increased by 1

#### Automation Notes

> Playwright counts rows before create, performs create, counts after, asserts delta == 1.

---

## Group D: Import Keypair


### Test 14: Import SSH Public Key

**Group:** D — Import Keypair
**Automated by:** `recipes/keypairs/import_form.py` → `test_import_ssh_keypair`
**Screenshot:** `after_014_import_ssh_keypair.png`

#### GUI Steps

1. First, generate a test key on your laptop:
   ```bash
   ssh-keygen -t rsa -b 2048 -f /tmp/import-test-key -N "" -q
   cat /tmp/import-test-key.pub
   ```
2. Navigate to **Project → Compute → Key Pairs**
3. Click **"Import Public Key"** (or "Import Key Pair")
4. In the dialog:
   - **Key Pair Name:** `manual-import-ssh`
   - **Key Type:** SSH Key
   - **Public Key:** Paste the contents of `/tmp/import-test-key.pub`
5. Click **"Import Public Key"** (submit)

#### CLI Equivalent

```bash
openstack keypair create --public-key /tmp/import-test-key.pub manual-import-ssh
```

> Horizon sends `POST /compute/v2.1/os-keypairs` with the `public_key` field.

#### Expected Result

- [ ] Import dialog has Name, Type, and Public Key fields
- [ ] Pasting a valid SSH public key is accepted
- [ ] Success notification appears after submit
- [ ] New keypair appears in table
- [ ] No private key download (because you imported, not generated)

#### Automation Notes

> Playwright generates a test key pair, reads the public key, pastes into the form, submits, and verifies the new row appears.

### Test 15: Import X.509 Certificate

**Group:** D — Import Keypair
**Automated by:** `recipes/keypairs/import_form.py` → `test_import_x509_keypair`
**Screenshot:** `after_015_import_x509_keypair.png`

#### GUI Steps

1. Generate a test X.509 certificate:
   ```bash
   openssl req -x509 -newkey rsa:2048 -keyout /tmp/x509-test.key \
     -out /tmp/x509-test.crt -days 1 -nodes -subj "/CN=test"
   cat /tmp/x509-test.crt
   ```
2. Navigate to **Project → Compute → Key Pairs**
3. Click **"Import Public Key"**
4. In the dialog:
   - **Key Pair Name:** `manual-import-x509`
   - **Key Type:** X.509 Certificate
   - **Public Key:** Paste the X.509 certificate content
5. Click **"Import Public Key"**

#### CLI Equivalent

```bash
openstack keypair create --type x509 --public-key /tmp/x509-test.crt manual-import-x509
```

> Imports an X.509 certificate as a keypair via Nova API.

#### Expected Result

- [ ] X.509 type is selectable in import dialog
- [ ] Pasting a valid certificate is accepted
- [ ] Success notification appears
- [ ] New keypair in table shows Type = "x509"

#### Automation Notes

> Playwright generates X.509 cert via openssl, pastes into form, submits.

### Test 16: Validation Errors on Empty Submit

**Group:** D — Import Keypair
**Automated by:** `recipes/keypairs/import_form.py` → `test_validation_errors`
**Screenshot:** `after_016_validation_errors.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Click **"Import Public Key"**
3. Leave all fields **empty**
4. Click **"Import Public Key"** (submit)
5. Observe error messages

#### CLI Equivalent

```bash
openstack keypair create --public-key /dev/null ""
# Error: Keypair name is required
```

> CLI also rejects empty name/key.

#### Expected Result

- [ ] Form does NOT submit successfully
- [ ] Error message appears for missing **Name** field
- [ ] Error message appears for missing **Public Key** field
- [ ] No new keypair is created in the table
- [ ] Dialog remains open so user can correct errors

#### Automation Notes

> Playwright clicks submit on empty form, waits for error elements, asserts error text mentions required fields.

---

## Group E: Delete Keypair


### Test 17: Delete Single Keypair

**Group:** E — Delete Keypair
**Automated by:** `recipes/keypairs/delete.py` → `test_delete_single`
**Screenshot:** `after_017_delete_single.png`

#### GUI Steps

1. Create a disposable keypair first:
   ```bash
   openstack keypair create delete-test-single > /dev/null
   ```
2. Navigate to **Project → Compute → Key Pairs**
3. Find the `delete-test-single` row
4. Click the **Actions** dropdown on that row
5. Click **"Delete Key Pair"**
6. A confirmation dialog appears — click **"Delete Key Pair"** to confirm
7. Observe the table

#### CLI Equivalent

```bash
openstack keypair delete delete-test-single
```

> Horizon sends `DELETE /compute/v2.1/os-keypairs/<name>` to Nova.

#### Expected Result

- [ ] Confirmation dialog shows the keypair name
- [ ] After confirming, the row disappears from the table
- [ ] Success notification: "Deleted Key Pair: delete-test-single"
- [ ] Table row count decreased by 1

#### Automation Notes

> Playwright creates a test keypair via API, navigates to table, clicks row action → Delete, confirms dialog, asserts row is removed.

### Test 18: Batch Delete Multiple Keypairs

**Group:** E — Delete Keypair
**Automated by:** `recipes/keypairs/delete.py` → `test_delete_batch`
**Screenshot:** `after_018_delete_batch.png`

#### GUI Steps

1. Create 2 disposable keypairs:
   ```bash
   openstack keypair create delete-batch-1 > /dev/null
   openstack keypair create delete-batch-2 > /dev/null
   ```
2. Navigate to **Project → Compute → Key Pairs**
3. Check the checkbox on **delete-batch-1** row
4. Check the checkbox on **delete-batch-2** row
5. The batch action bar appears — click **"Delete Key Pairs"**
6. Confirmation dialog appears listing both — click **"Delete Key Pairs"**
7. Observe the table

#### CLI Equivalent

```bash
openstack keypair delete delete-batch-1 delete-batch-2
```

> Batch delete via CLI.

#### Expected Result

- [ ] Confirmation dialog lists **both** keypair names
- [ ] After confirming, **both** rows disappear
- [ ] Success notification mentions both deletions
- [ ] Table row count decreased by 2

#### Automation Notes

> Playwright creates 2 test keypairs, selects both checkboxes, clicks batch delete, confirms, asserts both rows removed.

### Test 19: Delete Confirmation Dialog Content

**Group:** E — Delete Keypair
**Automated by:** `recipes/keypairs/delete.py` → `test_confirm_dialog`
**Screenshot:** `after_019_confirm_dialog.png`

#### GUI Steps

1. Create a disposable keypair:
   ```bash
   openstack keypair create confirm-dialog-test > /dev/null
   ```
2. Navigate to **Project → Compute → Key Pairs**
3. Click the **Actions** dropdown on the `confirm-dialog-test` row
4. Click **"Delete Key Pair"**
5. **DO NOT click confirm yet** — examine the dialog

#### CLI Equivalent


> No CLI equivalent — this tests the UI confirmation dialog.

#### Expected Result

- [ ] Modal dialog appears with a warning message
- [ ] Dialog body includes the keypair name: **"confirm-dialog-test"**
- [ ] Dialog has two buttons: **"Cancel"** and **"Delete Key Pair"**
- [ ] Clicking **"Cancel"** closes the dialog without deleting
- [ ] The keypair still exists in the table after canceling

#### Automation Notes

> Playwright opens delete dialog, asserts dialog text includes keypair name, clicks Cancel, asserts row still exists.

---

## Group F: Detail View


### Test 20: Detail Page Loads

**Group:** F — Detail View
**Automated by:** `recipes/keypairs/detail_view.py` → `test_detail_page_loads`
**Screenshot:** `after_020_detail_page_loads.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Click on the **name** of any existing keypair (it should be a hyperlink)
3. Observe the detail page that loads

#### CLI Equivalent

```bash
openstack keypair show <keypair-name>
```

> Horizon sends `GET /compute/v2.1/os-keypairs/<name>` to retrieve details.

#### Expected Result

- [ ] Clicking the name navigates to a detail page (URL changes)
- [ ] Detail page shows the keypair name as a heading
- [ ] Page renders without errors
- [ ] Breadcrumb updates to: `Project > Compute > Key Pairs > <name>`

#### Automation Notes

> Playwright clicks the first keypair name link, waits for navigation, asserts URL contains `/key_pairs/`.

### Test 21: Detail Shows Fingerprint

**Group:** F — Detail View
**Automated by:** `recipes/keypairs/detail_view.py` → `test_detail_shows_fingerprint`
**Screenshot:** `after_021_detail_shows_fingerprint.png`

#### GUI Steps

1. Navigate to a keypair detail page (follow Test F1)
2. Look for the **Fingerprint** field in the detail info

#### CLI Equivalent

```bash
openstack keypair show <name> -c fingerprint
```

> Shows the colon-separated hex fingerprint.

#### Expected Result

- [ ] Fingerprint is displayed as a labeled field
- [ ] Format is colon-separated hex: `XX:XX:XX:XX:...`
- [ ] Value matches CLI output for the same keypair

#### Automation Notes

> Playwright asserts detail page contains an element with fingerprint text matching `/([0-9a-f]{2}:){15}[0-9a-f]{2}/`.

### Test 22: Detail Shows Public Key

**Group:** F — Detail View
**Automated by:** `recipes/keypairs/detail_view.py` → `test_detail_shows_public_key`
**Screenshot:** `after_022_detail_shows_public_key.png`

#### GUI Steps

1. Navigate to a keypair detail page (follow Test F1)
2. Look for the **Public Key** section

#### CLI Equivalent

```bash
openstack keypair show <name> -c public_key
```

> Shows the full public key content.

#### Expected Result

- [ ] Public key is displayed (often in a `<textarea>` or `<pre>` block)
- [ ] For SSH keys: starts with `ssh-rsa` or `ssh-ed25519`
- [ ] Content is selectable/copyable
- [ ] Key content matches CLI output

#### Automation Notes

> Playwright asserts presence of public key content starting with expected key type prefix.

### Test 23: Back Navigation from Detail

**Group:** F — Detail View
**Automated by:** `recipes/keypairs/detail_view.py` → `test_back_navigation`
**Screenshot:** `after_023_back_navigation.png`

#### GUI Steps

1. Navigate to a keypair detail page (follow Test F1)
2. Click the **"Key Pairs"** breadcrumb link (or browser Back button)
3. Verify you return to the Key Pairs table

#### CLI Equivalent


> No CLI equivalent — this is UI navigation.

#### Expected Result

- [ ] Clicking breadcrumb returns to the Key Pairs list page
- [ ] Table is displayed with all keypairs
- [ ] Browser URL returns to `/project/key_pairs/`
- [ ] No errors during navigation

#### Automation Notes

> Playwright clicks breadcrumb link, waits for table selector, asserts URL is the list page.

---

## Group G: Inline Expansion


### Test 24: Chevron Toggle (Expand/Collapse)

**Group:** G — Inline Expansion
**Automated by:** `recipes/keypairs/chevron_rows.py` → `test_chevron_toggle`
**Screenshot:** `after_024_chevron_toggle.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Look for a **chevron icon** (▶ or ▼) on the left side of each row
3. Click the chevron on the **first** keypair row
4. Observe the row expanding to show additional details
5. Click the chevron again
6. Observe the row collapsing back to normal

#### CLI Equivalent


> No CLI equivalent — this is a UI toggle for inline detail display.

#### Expected Result

- [ ] Chevron icon is present on each keypair row
- [ ] Clicking chevron expands the row (reveals a sub-section below the row)
- [ ] Chevron icon rotates/changes to indicate expanded state (▶ → ▼)
- [ ] Clicking again collapses the expanded section
- [ ] Toggle is smooth (no page reload or flicker)

#### Automation Notes

> Playwright clicks chevron selector, waits for expanded content to appear, then clicks again and waits for collapse.

### Test 25: Expanded Content Shows Details

**Group:** G — Inline Expansion
**Automated by:** `recipes/keypairs/chevron_rows.py` → `test_expanded_content`
**Screenshot:** `after_025_expanded_content.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs**
2. Click the chevron on any keypair row to expand it
3. Examine the expanded content

#### CLI Equivalent

```bash
openstack keypair show <name>
```

> The expanded content shows the same info as `keypair show`.

#### Expected Result

- [ ] Expanded section shows **Type** (ssh or x509)
- [ ] Expanded section shows **Fingerprint**
- [ ] Expanded section shows **Public Key** (or a truncated version)
- [ ] Content is formatted readably (labels + values)

#### Automation Notes

> Playwright expands row, queries expanded section for text content, asserts presence of 'Type', 'Fingerprint', and key content.

### Test 26: Multiple Rows Expanded Simultaneously

**Group:** G — Inline Expansion
**Automated by:** `recipes/keypairs/chevron_rows.py` → `test_multiple_expand`
**Screenshot:** `after_026_multiple_expand.png`

#### GUI Steps

1. Navigate to **Project → Compute → Key Pairs** (ensure at least 2 keypairs exist)
2. Click the chevron on **row 1** — it expands
3. **Without collapsing row 1**, click the chevron on **row 2**
4. Observe both rows

#### CLI Equivalent


> No CLI equivalent — tests concurrent UI expansion behavior.

#### Expected Result

- [ ] Both rows are expanded simultaneously
- [ ] Both show their respective detail content
- [ ] No interference between expanded rows (row 1 doesn't collapse when row 2 expands)
- [ ] Both can be independently collapsed

#### Automation Notes

> Playwright expands row 1, then row 2, asserts both expanded sections are visible. Then collapses row 1, asserts row 2 remains expanded.

---

## Summary Checklist

### Before Testing
- [ ] Environment set up (Terminal 1: port-forward, Terminal 2: Horizon)
- [ ] Browser open at `http://localhost:9000`, logged in as admin
- [ ] At least 2 test keypairs exist
- [ ] Panel configuration set correctly

### Group A: Panel Loading
- [ ] 1. Page Loads Correctly
- [ ] 2. Breadcrumb Visible
- [ ] 3. Table Visible with Headers
- [ ] 4. Panel Implementation Detection

### Group B: Table Features
- [ ] 5. Search / Filter
- [ ] 6. Column Headers Present
- [ ] 7. Row Actions Menu
- [ ] 8. Batch Actions (Multi-Select)
- [ ] 9. Pagination Controls

### Group C: Create Keypair
- [ ] 10. Create SSH Keypair
- [ ] 11. Create X.509 Keypair
- [ ] 12. PEM File Download
- [ ] 13. Keypair Appears in Table After Create

### Group D: Import Keypair
- [ ] 14. Import SSH Public Key
- [ ] 15. Import X.509 Certificate
- [ ] 16. Validation Errors on Empty Submit

### Group E: Delete Keypair
- [ ] 17. Delete Single Keypair
- [ ] 18. Batch Delete Multiple Keypairs
- [ ] 19. Delete Confirmation Dialog Content

### Group F: Detail View
- [ ] 20. Detail Page Loads
- [ ] 21. Detail Shows Fingerprint
- [ ] 22. Detail Shows Public Key
- [ ] 23. Back Navigation from Detail

### Group G: Inline Expansion
- [ ] 24. Chevron Toggle (Expand/Collapse)
- [ ] 25. Expanded Content Shows Details
- [ ] 26. Multiple Rows Expanded Simultaneously

### After Testing
- [ ] Clean up test keypairs:
  ```bash
  openstack keypair list -f value -c Name | grep -E "(manual-test|delete-test|page-test|confirm-dialog|import-test)" | xargs -I{} openstack keypair delete "{}"
  ```
- [ ] Remove iptables rule:
  ```bash
  sudo iptables -t nat -D OUTPUT -o lo -p tcp --dport 80 -j REDIRECT --to-port 5080
  ```

### Sign-off

| Tester | Date | Panel Config | Result |
|--------|------|-------------|--------|
|        |      |             |        |

**Overall Verdict:** [ ] PASS  [ ] FAIL
