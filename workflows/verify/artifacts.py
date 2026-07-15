"""Artifact generator for /verify skill — produces manual_testing_guide.md."""

from pathlib import Path
from datetime import datetime, timezone

from recipe_loader import load_recipe


# ---------------------------------------------------------------------------
# Knowledge base: GUI steps, CLI equivalents, expected results per test
# ---------------------------------------------------------------------------

TEST_KNOWLEDGE = {
    ("A", "page_loads"): {
        "title": "Page Loads Correctly",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs** (left sidebar)",
            "Wait for the page to fully load (spinner disappears)",
            'Observe that the page title reads **"Key Pairs"**',
        ],
        "cli": "openstack keypair list",
        "cli_note": "Nova API call Horizon makes to populate the table. Issues `GET /compute/v2.1/os-keypairs`.",
        "expected": [
            "Page loads without errors (no 500, no blank page)",
            'Title bar shows "Key Pairs"',
            "A table is visible (even if empty)",
            "No JavaScript console errors (open DevTools → Console)",
        ],
        "auto_notes": "Playwright navigates to `/project/key_pairs/`, waits for `table` selector, asserts page title contains 'Key Pairs'. Timeout: 30s.",
    },
    ("A", "breadcrumb_visible"): {
        "title": "Breadcrumb Visible",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            "Look at the breadcrumb trail near the top of the content area",
            "Verify it reads: **Project > Compute > Key Pairs**",
        ],
        "cli": None,
        "cli_note": "No CLI equivalent — breadcrumbs are a pure UI navigation element.",
        "expected": [
            "Breadcrumb is visible below the top navbar",
            "Path shows: `Project > Compute > Key Pairs`",
            'Each breadcrumb segment is a clickable link (except "Key Pairs")',
        ],
        "auto_notes": "Playwright locates `.breadcrumb` or `nav[aria-label=\"breadcrumb\"]`, asserts text content includes 'Key Pairs'.",
    },
    ("A", "table_visible"): {
        "title": "Table Visible with Headers",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            "Observe the main content area — a table should be present",
            "Check the column headers in the table",
        ],
        "cli": "openstack keypair list -c Name -c Fingerprint -c Type",
        "cli_note": "The table headers correspond to the fields returned by the Nova keypair API.",
        "expected": [
            "Table is present in the content area",
            "Column headers include: **Name**, **Fingerprint**, **Type** (at minimum)",
            "If keypairs exist, rows are populated with data",
            'If no keypairs exist, a "No items to display" message appears',
        ],
        "auto_notes": "Playwright asserts `table thead th` elements contain expected header text. Checks for at least 3 column headers.",
    },
    ("A", "angular_or_python_detected"): {
        "title": "Panel Implementation Detection",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            "Open browser DevTools (F12) → Elements tab",
            "**AngularJS panel:** Look for `<hz-resource-table>` or `ng-` attributes in the DOM",
            '**Python panel:** Look for standard Django `<table class="table">` markup without Angular directives',
        ],
        "cli": None,
        "cli_note": "No CLI equivalent — this is a frontend implementation check.",
        "expected": [
            "No `ng-` attributes in the Key Pairs table DOM (Python panel)",
            "No `<hz-resource-table>` element",
            "Standard HTML `<table>` with Django template rendering",
            "The page source (View Source) shows server-rendered HTML rows",
        ],
        "auto_notes": "Playwright checks for presence/absence of Angular-specific selectors. Uses `page.query_selector('hz-resource-table')` — null means Python panel.",
    },
    ("B", "search_filter"): {
        "title": "Search / Filter",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            "Locate the **search/filter input** above the table",
            "Type the name of an existing keypair (e.g., `verify-seed-key`)",
            "Observe the table rows filter to show only matching keypairs",
            "Clear the search box",
            "Verify all keypairs reappear",
        ],
        "cli": "openstack keypair list | grep verify-seed-key",
        "cli_note": "No server-side filter for keypairs in Nova — the GUI filters client-side.",
        "expected": [
            "Search input is present above the table",
            "Typing a name filters table rows in real-time (or on Enter)",
            "Only matching rows remain visible",
            "Clearing search restores all rows",
            'Non-matching search shows "No items to display" or empty table',
        ],
        "auto_notes": "Playwright fills the search input, waits for row count to decrease, asserts remaining row text matches the search term.",
    },
    ("B", "column_headers"): {
        "title": "Column Headers Present",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            "Examine the table header row",
            "Verify all expected columns are present",
        ],
        "cli": "openstack keypair list",
        "cli_note": "Default columns: Name, Fingerprint, Type.",
        "expected": [
            "**Name** column header present",
            "**Fingerprint** column header present",
            "**Type** column header present (ssh or x509)",
            "Optional: checkbox column for batch selection",
            "Optional: Actions column",
        ],
        "auto_notes": "Playwright collects `th` text content, asserts set includes {Name, Fingerprint, Type}.",
    },
    ("B", "row_actions_menu"): {
        "title": "Row Actions Menu",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs** (ensure at least 1 keypair exists)",
            "In any keypair row, find the **Actions** dropdown button (right side of row)",
            "Click the dropdown",
            "Observe the available actions",
        ],
        "cli": None,
        "cli_note": "No CLI equivalent — this tests the UI action menu rendering.",
        "expected": [
            "Each row has an Actions dropdown (or inline action button)",
            "Dropdown contains at least: **Delete Key Pair**",
            "Actions are clickable (don't click Delete yet — that's Group E)",
        ],
        "auto_notes": "Playwright clicks the dropdown trigger, waits for menu to appear, asserts 'Delete' action is present in the menu items.",
    },
    ("B", "batch_actions"): {
        "title": "Batch Actions (Multi-Select)",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs** (ensure at least 2 keypairs exist)",
            "Click the checkbox on **row 1**",
            "Click the checkbox on **row 2**",
            "Observe the batch action bar that appears above the table",
            'Verify a **"Delete Key Pairs"** button appears',
        ],
        "cli": "openstack keypair delete test-keypair-1 test-keypair-2",
        "cli_note": "Batch delete via CLI.",
        "expected": [
            "Checkboxes are present on each row",
            "Selecting 2+ rows activates the batch action bar",
            'Batch action bar shows **"Delete Key Pairs"** button',
            '"Select All" checkbox in header selects all visible rows',
            "Deselecting all rows hides the batch action bar",
        ],
        "auto_notes": "Playwright checks two row checkboxes, waits for batch action bar visibility, asserts delete button text.",
    },
    ("B", "pagination_controls"): {
        "title": "Pagination Controls",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            "If fewer than 20 keypairs exist, create more:\n   ```bash\n   for i in $(seq 1 25); do openstack keypair create \"page-test-$i\" > /dev/null; done\n   ```",
            "Look for **Next** / **Previous** pagination links below the table",
            "Click **Next** — verify the table shows the next page of results",
            "Click **Previous** — verify you return to page 1",
        ],
        "cli": "openstack keypair list",
        "cli_note": "Nova keypair list doesn't paginate by default in CLI.",
        "expected": [
            "Pagination controls appear when rows exceed page size (default: 20)",
            "**Next** link advances to the next page",
            "**Previous** link returns to the prior page",
            'Page indicator shows current position (e.g., "Displaying 1-20 of 25")',
            "If all keypairs fit on one page, pagination controls may be hidden",
        ],
        "auto_notes": "Playwright creates 25 test keypairs, navigates to page, checks for pagination elements. Clicks Next, asserts URL or table content changes.",
    },
    ("C", "create_ssh_keypair"): {
        "title": "Create SSH Keypair",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            'Click the **"Create Key Pair"** button (top-right above table)',
            "In the dialog/form:\n   - **Key Pair Name:** `manual-test-ssh`\n   - **Key Type:** Select **SSH Key** (typically the default)",
            'Click **"Create Key Pair"** (submit button)',
            "Wait for success message",
        ],
        "cli": "openstack keypair create manual-test-ssh",
        "cli_note": "Horizon sends `POST /compute/v2.1/os-keypairs` with `{\"keypair\": {\"name\": \"...\", \"type\": \"ssh\"}}`.",
        "expected": [
            "Create dialog opens with Name and Type fields",
            "SSH Key is selectable (or default)",
            "After submit, a **success notification** appears (green banner)",
            "A **private key download** is triggered (PEM file) — see Test C3",
            "The dialog closes and the table refreshes",
        ],
        "auto_notes": "Playwright clicks create button, fills form, submits, waits for success toast notification.",
    },
    ("C", "create_x509_keypair"): {
        "title": "Create X.509 Keypair",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            'Click **"Create Key Pair"**',
            "In the dialog:\n   - **Key Pair Name:** `manual-test-x509`\n   - **Key Type:** Select **X.509 Certificate**",
            'Click **"Create Key Pair"**',
            "Wait for success",
        ],
        "cli": "openstack keypair create --type x509 manual-test-x509",
        "cli_note": "Creates an X.509 type keypair via Nova API.",
        "expected": [
            "X.509 type is available in the dropdown",
            "Submission succeeds without errors",
            "Success notification appears",
            "Certificate download may be triggered",
            'New keypair appears in table with Type = "x509"',
        ],
        "auto_notes": "Same as C1 but selects X.509 from type dropdown. Asserts the new row shows 'x509' in the Type column.",
    },
    ("C", "download_pem"): {
        "title": "PEM File Download",
        "gui_steps": [
            "Perform Create SSH Keypair (Test C1)",
            "After successful creation, observe the browser behavior:",
            "A **download dialog** may appear with the `.pem` file",
            "OR the private key is displayed in a modal with a **Download** or **Copy** button",
            "If displayed in modal: click **Download** or copy the key content",
            "Verify the downloaded file contains a valid PEM private key",
        ],
        "cli": "openstack keypair create download-test > /tmp/download-test.pem\ncat /tmp/download-test.pem | head -1\n# Should show: -----BEGIN RSA PRIVATE KEY-----",
        "cli_note": "The CLI outputs the private key directly to stdout.",
        "expected": [
            "Private key is offered for download after creation",
            "Downloaded file starts with `-----BEGIN RSA PRIVATE KEY-----`",
            "File is non-empty and contains valid PEM content",
            "User is warned that this is the only time the private key can be downloaded",
        ],
        "auto_notes": "Playwright intercepts the download event, saves to temp dir, asserts file starts with PEM header.",
    },
    ("C", "keypair_appears_in_table"): {
        "title": "Keypair Appears in Table After Create",
        "gui_steps": [
            "Note the current number of rows in the Key Pairs table",
            "Create a new keypair (follow Test C1)",
            "After success, observe the table",
            "Verify the new keypair name appears as a row",
        ],
        "cli": "openstack keypair list | grep manual-test",
        "cli_note": "Confirms the keypair was persisted via the API.",
        "expected": [
            "Table refreshes automatically after creation (no manual reload needed)",
            "New keypair row appears with correct **Name**",
            "**Fingerprint** column shows a valid fingerprint hash",
            '**Type** column shows "ssh" or "x509" as appropriate',
            "Row count increased by 1",
        ],
        "auto_notes": "Playwright counts rows before create, performs create, counts after, asserts delta == 1.",
    },
    ("D", "import_ssh_keypair"): {
        "title": "Import SSH Public Key",
        "gui_steps": [
            "First, generate a test key on your laptop:\n   ```bash\n   ssh-keygen -t rsa -b 2048 -f /tmp/import-test-key -N \"\" -q\n   cat /tmp/import-test-key.pub\n   ```",
            "Navigate to **Project → Compute → Key Pairs**",
            'Click **"Import Public Key"** (or "Import Key Pair")',
            "In the dialog:\n   - **Key Pair Name:** `manual-import-ssh`\n   - **Key Type:** SSH Key\n   - **Public Key:** Paste the contents of `/tmp/import-test-key.pub`",
            'Click **"Import Public Key"** (submit)',
        ],
        "cli": "openstack keypair create --public-key /tmp/import-test-key.pub manual-import-ssh",
        "cli_note": "Horizon sends `POST /compute/v2.1/os-keypairs` with the `public_key` field.",
        "expected": [
            "Import dialog has Name, Type, and Public Key fields",
            "Pasting a valid SSH public key is accepted",
            "Success notification appears after submit",
            "New keypair appears in table",
            "No private key download (because you imported, not generated)",
        ],
        "auto_notes": "Playwright generates a test key pair, reads the public key, pastes into the form, submits, and verifies the new row appears.",
    },
    ("D", "import_x509_keypair"): {
        "title": "Import X.509 Certificate",
        "gui_steps": [
            "Generate a test X.509 certificate:\n   ```bash\n   openssl req -x509 -newkey rsa:2048 -keyout /tmp/x509-test.key \\\n     -out /tmp/x509-test.crt -days 1 -nodes -subj \"/CN=test\"\n   cat /tmp/x509-test.crt\n   ```",
            "Navigate to **Project → Compute → Key Pairs**",
            'Click **"Import Public Key"**',
            "In the dialog:\n   - **Key Pair Name:** `manual-import-x509`\n   - **Key Type:** X.509 Certificate\n   - **Public Key:** Paste the X.509 certificate content",
            'Click **"Import Public Key"**',
        ],
        "cli": "openstack keypair create --type x509 --public-key /tmp/x509-test.crt manual-import-x509",
        "cli_note": "Imports an X.509 certificate as a keypair via Nova API.",
        "expected": [
            "X.509 type is selectable in import dialog",
            "Pasting a valid certificate is accepted",
            "Success notification appears",
            'New keypair in table shows Type = "x509"',
        ],
        "auto_notes": "Playwright generates X.509 cert via openssl, pastes into form, submits.",
    },
    ("D", "validation_errors"): {
        "title": "Validation Errors on Empty Submit",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            'Click **"Import Public Key"**',
            "Leave all fields **empty**",
            'Click **"Import Public Key"** (submit)',
            "Observe error messages",
        ],
        "cli": 'openstack keypair create --public-key /dev/null ""\n# Error: Keypair name is required',
        "cli_note": "CLI also rejects empty name/key.",
        "expected": [
            "Form does NOT submit successfully",
            "Error message appears for missing **Name** field",
            "Error message appears for missing **Public Key** field",
            "No new keypair is created in the table",
            "Dialog remains open so user can correct errors",
        ],
        "auto_notes": "Playwright clicks submit on empty form, waits for error elements, asserts error text mentions required fields.",
    },
    ("E", "delete_single"): {
        "title": "Delete Single Keypair",
        "gui_steps": [
            "Create a disposable keypair first:\n   ```bash\n   openstack keypair create delete-test-single > /dev/null\n   ```",
            "Navigate to **Project → Compute → Key Pairs**",
            "Find the `delete-test-single` row",
            "Click the **Actions** dropdown on that row",
            'Click **"Delete Key Pair"**',
            'A confirmation dialog appears — click **"Delete Key Pair"** to confirm',
            "Observe the table",
        ],
        "cli": "openstack keypair delete delete-test-single",
        "cli_note": "Horizon sends `DELETE /compute/v2.1/os-keypairs/<name>` to Nova.",
        "expected": [
            "Confirmation dialog shows the keypair name",
            "After confirming, the row disappears from the table",
            'Success notification: "Deleted Key Pair: delete-test-single"',
            "Table row count decreased by 1",
        ],
        "auto_notes": "Playwright creates a test keypair via API, navigates to table, clicks row action → Delete, confirms dialog, asserts row is removed.",
    },
    ("E", "delete_batch"): {
        "title": "Batch Delete Multiple Keypairs",
        "gui_steps": [
            "Create 2 disposable keypairs:\n   ```bash\n   openstack keypair create delete-batch-1 > /dev/null\n   openstack keypair create delete-batch-2 > /dev/null\n   ```",
            "Navigate to **Project → Compute → Key Pairs**",
            "Check the checkbox on **delete-batch-1** row",
            "Check the checkbox on **delete-batch-2** row",
            'The batch action bar appears — click **"Delete Key Pairs"**',
            'Confirmation dialog appears listing both — click **"Delete Key Pairs"**',
            "Observe the table",
        ],
        "cli": "openstack keypair delete delete-batch-1 delete-batch-2",
        "cli_note": "Batch delete via CLI.",
        "expected": [
            "Confirmation dialog lists **both** keypair names",
            "After confirming, **both** rows disappear",
            "Success notification mentions both deletions",
            "Table row count decreased by 2",
        ],
        "auto_notes": "Playwright creates 2 test keypairs, selects both checkboxes, clicks batch delete, confirms, asserts both rows removed.",
    },
    ("E", "confirm_dialog"): {
        "title": "Delete Confirmation Dialog Content",
        "gui_steps": [
            "Create a disposable keypair:\n   ```bash\n   openstack keypair create confirm-dialog-test > /dev/null\n   ```",
            "Navigate to **Project → Compute → Key Pairs**",
            "Click the **Actions** dropdown on the `confirm-dialog-test` row",
            'Click **"Delete Key Pair"**',
            "**DO NOT click confirm yet** — examine the dialog",
        ],
        "cli": None,
        "cli_note": "No CLI equivalent — this tests the UI confirmation dialog.",
        "expected": [
            "Modal dialog appears with a warning message",
            'Dialog body includes the keypair name: **"confirm-dialog-test"**',
            'Dialog has two buttons: **"Cancel"** and **"Delete Key Pair"**',
            'Clicking **"Cancel"** closes the dialog without deleting',
            "The keypair still exists in the table after canceling",
        ],
        "auto_notes": "Playwright opens delete dialog, asserts dialog text includes keypair name, clicks Cancel, asserts row still exists.",
    },
    ("F", "detail_page_loads"): {
        "title": "Detail Page Loads",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            "Click on the **name** of any existing keypair (it should be a hyperlink)",
            "Observe the detail page that loads",
        ],
        "cli": "openstack keypair show <keypair-name>",
        "cli_note": "Horizon sends `GET /compute/v2.1/os-keypairs/<name>` to retrieve details.",
        "expected": [
            "Clicking the name navigates to a detail page (URL changes)",
            "Detail page shows the keypair name as a heading",
            "Page renders without errors",
            "Breadcrumb updates to: `Project > Compute > Key Pairs > <name>`",
        ],
        "auto_notes": "Playwright clicks the first keypair name link, waits for navigation, asserts URL contains `/key_pairs/`.",
    },
    ("F", "detail_shows_fingerprint"): {
        "title": "Detail Shows Fingerprint",
        "gui_steps": [
            "Navigate to a keypair detail page (follow Test F1)",
            "Look for the **Fingerprint** field in the detail info",
        ],
        "cli": "openstack keypair show <name> -c fingerprint",
        "cli_note": "Shows the colon-separated hex fingerprint.",
        "expected": [
            "Fingerprint is displayed as a labeled field",
            "Format is colon-separated hex: `XX:XX:XX:XX:...`",
            "Value matches CLI output for the same keypair",
        ],
        "auto_notes": "Playwright asserts detail page contains an element with fingerprint text matching `/([0-9a-f]{2}:){15}[0-9a-f]{2}/`.",
    },
    ("F", "detail_shows_public_key"): {
        "title": "Detail Shows Public Key",
        "gui_steps": [
            "Navigate to a keypair detail page (follow Test F1)",
            "Look for the **Public Key** section",
        ],
        "cli": "openstack keypair show <name> -c public_key",
        "cli_note": "Shows the full public key content.",
        "expected": [
            "Public key is displayed (often in a `<textarea>` or `<pre>` block)",
            "For SSH keys: starts with `ssh-rsa` or `ssh-ed25519`",
            "Content is selectable/copyable",
            "Key content matches CLI output",
        ],
        "auto_notes": "Playwright asserts presence of public key content starting with expected key type prefix.",
    },
    ("F", "back_navigation"): {
        "title": "Back Navigation from Detail",
        "gui_steps": [
            "Navigate to a keypair detail page (follow Test F1)",
            'Click the **"Key Pairs"** breadcrumb link (or browser Back button)',
            "Verify you return to the Key Pairs table",
        ],
        "cli": None,
        "cli_note": "No CLI equivalent — this is UI navigation.",
        "expected": [
            "Clicking breadcrumb returns to the Key Pairs list page",
            "Table is displayed with all keypairs",
            "Browser URL returns to `/project/key_pairs/`",
            "No errors during navigation",
        ],
        "auto_notes": "Playwright clicks breadcrumb link, waits for table selector, asserts URL is the list page.",
    },
    ("G", "chevron_toggle"): {
        "title": "Chevron Toggle (Expand/Collapse)",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            "Look for a **chevron icon** (▶ or ▼) on the left side of each row",
            "Click the chevron on the **first** keypair row",
            "Observe the row expanding to show additional details",
            "Click the chevron again",
            "Observe the row collapsing back to normal",
        ],
        "cli": None,
        "cli_note": "No CLI equivalent — this is a UI toggle for inline detail display.",
        "expected": [
            "Chevron icon is present on each keypair row",
            "Clicking chevron expands the row (reveals a sub-section below the row)",
            "Chevron icon rotates/changes to indicate expanded state (▶ → ▼)",
            "Clicking again collapses the expanded section",
            "Toggle is smooth (no page reload or flicker)",
        ],
        "auto_notes": "Playwright clicks chevron selector, waits for expanded content to appear, then clicks again and waits for collapse.",
    },
    ("G", "expanded_content"): {
        "title": "Expanded Content Shows Details",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs**",
            "Click the chevron on any keypair row to expand it",
            "Examine the expanded content",
        ],
        "cli": "openstack keypair show <name>",
        "cli_note": "The expanded content shows the same info as `keypair show`.",
        "expected": [
            "Expanded section shows **Type** (ssh or x509)",
            "Expanded section shows **Fingerprint**",
            "Expanded section shows **Public Key** (or a truncated version)",
            "Content is formatted readably (labels + values)",
        ],
        "auto_notes": "Playwright expands row, queries expanded section for text content, asserts presence of 'Type', 'Fingerprint', and key content.",
    },
    ("G", "multiple_expand"): {
        "title": "Multiple Rows Expanded Simultaneously",
        "gui_steps": [
            "Navigate to **Project → Compute → Key Pairs** (ensure at least 2 keypairs exist)",
            "Click the chevron on **row 1** — it expands",
            "**Without collapsing row 1**, click the chevron on **row 2**",
            "Observe both rows",
        ],
        "cli": None,
        "cli_note": "No CLI equivalent — tests concurrent UI expansion behavior.",
        "expected": [
            "Both rows are expanded simultaneously",
            "Both show their respective detail content",
            "No interference between expanded rows (row 1 doesn't collapse when row 2 expands)",
            "Both can be independently collapsed",
        ],
        "auto_notes": "Playwright expands row 1, then row 2, asserts both expanded sections are visible. Then collapses row 1, asserts row 2 remains expanded.",
    },
}


# ---------------------------------------------------------------------------
# Rendering functions
# ---------------------------------------------------------------------------

def _render_header(state):
    review = state.get("review_number", "unknown")
    title = state.get("title", "(title not resolved)")
    recipe = state.get("recipe", "keypairs")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""# Manual Testing Guide — Key Pairs Panel Deangularization

**Review:** https://review.opendev.org/c/openstack/horizon/+/{review}
**Subject:** {title}
**Recipe:** {recipe}
**Generated:** {now}

> This guide walks through every automated test as a manual, click-by-click
> procedure. Follow each section in order, checking off items as you go.
> Use this while waiting for Zuul CI results on your Gerrit reviews.
"""


def _render_prerequisites():
    return """---

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
"""


def _render_test_section(group, test_name, global_idx):
    key = (group["name"], test_name)
    knowledge = TEST_KNOWLEDGE.get(key)

    if not knowledge:
        return f"\n### Test {global_idx}: {test_name}\n\n> _No detailed steps available for this test._\n"

    title = knowledge["title"]
    group_label = group["label"]
    module = group.get("module", "unknown")

    lines = []
    lines.append(f"\n### Test {global_idx}: {title}")
    lines.append(f"\n**Group:** {group['name']} — {group_label}")
    lines.append(f"**Automated by:** `recipes/keypairs/{module}.py` → `test_{test_name}`")
    lines.append(f"**Screenshot:** `after_{global_idx:03d}_{test_name}.png`")

    lines.append("\n#### GUI Steps\n")
    for i, step in enumerate(knowledge["gui_steps"], 1):
        lines.append(f"{i}. {step}")

    lines.append("\n#### CLI Equivalent\n")
    if knowledge["cli"]:
        lines.append(f"```bash\n{knowledge['cli']}\n```")
    lines.append(f"\n> {knowledge['cli_note']}")

    lines.append("\n#### Expected Result\n")
    for item in knowledge["expected"]:
        lines.append(f"- [ ] {item}")

    lines.append("\n#### Automation Notes\n")
    lines.append(f"> {knowledge['auto_notes']}")

    return "\n".join(lines)


def _render_summary_checklist(groups):
    lines = ["\n---\n", "## Summary Checklist\n"]

    lines.append("### Before Testing")
    lines.append("- [ ] Environment set up (Terminal 1: port-forward, Terminal 2: Horizon)")
    lines.append("- [ ] Browser open at `http://localhost:9000`, logged in as admin")
    lines.append("- [ ] At least 2 test keypairs exist")
    lines.append("- [ ] Panel configuration set correctly\n")

    global_idx = 0
    for group in groups:
        lines.append(f"### Group {group['name']}: {group['label']}")
        for test_name in group["tests"]:
            global_idx += 1
            key = (group["name"], test_name)
            knowledge = TEST_KNOWLEDGE.get(key, {})
            title = knowledge.get("title", test_name)
            lines.append(f"- [ ] {global_idx}. {title}")
        lines.append("")

    lines.append("### After Testing")
    lines.append("- [ ] Clean up test keypairs:")
    lines.append('  ```bash\n  openstack keypair list -f value -c Name | grep -E "(manual-test|delete-test|page-test|confirm-dialog|import-test)" | xargs -I{} openstack keypair delete "{}"\n  ```')
    lines.append("- [ ] Remove iptables rule:")
    lines.append("  ```bash\n  sudo iptables -t nat -D OUTPUT -o lo -p tcp --dport 80 -j REDIRECT --to-port 5080\n  ```")

    lines.append("\n### Sign-off\n")
    lines.append("| Tester | Date | Panel Config | Result |")
    lines.append("|--------|------|-------------|--------|")
    lines.append("|        |      |             |        |")
    lines.append("\n**Overall Verdict:** [ ] PASS  [ ] FAIL\n")

    return "\n".join(lines)


def _load_recipe(verify_dir, state):
    recipe_name = state.get("recipe", state.get("recipe_override", "keypairs"))
    if not recipe_name:
        recipe_name = "keypairs"
    return load_recipe(verify_dir, recipe_name)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def generate_manual_testing_guide(verify_dir, state, args):
    """Generate manual_testing_guide.md from recipe definition."""
    verify_dir = Path(verify_dir)
    artifacts_dir = Path(state["artifacts_dir"])

    recipe = _load_recipe(verify_dir, state)
    state["recipe"] = recipe.get("_name", "keypairs")

    sections = []
    sections.append(_render_header(state))
    sections.append(_render_prerequisites())

    global_idx = 0
    for group in recipe["groups"]:
        sections.append(f"\n---\n\n## Group {group['name']}: {group['label']}\n")
        for test_name in group["tests"]:
            global_idx += 1
            sections.append(_render_test_section(group, test_name, global_idx))

    sections.append(_render_summary_checklist(recipe["groups"]))

    guide = "\n".join(sections)
    out_path = artifacts_dir / "manual_testing_guide.md"
    out_path.write_text(guide)

    state["manual_testing_guide_path"] = str(out_path)
    state["manual_testing_guide_tests"] = global_idx

    print(f"  Manual testing guide: {out_path}")
    print(f"  Tests documented: {global_idx}")

    return state
