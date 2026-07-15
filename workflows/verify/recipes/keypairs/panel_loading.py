"""Group A: Panel Loading tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))
from horizon_auth import login
from horizon_nav import navigate_to_keypairs
from evidence import screenshot, reset_counter


async def run_tests(page, horizon_url, admin_user, admin_password,
                    artifacts_dir, phase):
    """Run Group A: Panel Loading tests."""
    reset_counter()
    results = []

    await login(page, horizon_url, admin_user, admin_password)

    # A1: Page loads
    try:
        await navigate_to_keypairs(page, horizon_url)
        await screenshot(page, artifacts_dir, "panel_loaded", phase)
        results.append({"name": "A1_page_loads", "status": "pass"})
    except Exception as e:
        results.append({"name": "A1_page_loads", "status": "fail", "error": str(e)})

    # A2: Breadcrumb visible
    try:
        breadcrumb = await page.query_selector(
            '.breadcrumb, nav[aria-label="breadcrumb"], ol.breadcrumb'
        )
        status = "pass" if breadcrumb else "fail"
        results.append({"name": "A2_breadcrumb_visible", "status": status})
    except Exception as e:
        results.append({"name": "A2_breadcrumb_visible", "status": "fail", "error": str(e)})

    # A3: Table visible
    try:
        table = await page.query_selector(
            'table, hz-resource-table, .table_wrapper'
        )
        await screenshot(page, artifacts_dir, "table_visible", phase)
        status = "pass" if table else "fail"
        results.append({"name": "A3_table_visible", "status": status})
    except Exception as e:
        results.append({"name": "A3_table_visible", "status": "fail", "error": str(e)})

    # A4: Detect Angular vs Python panel
    try:
        angular = await page.query_selector('hz-resource-table')
        python_table = await page.query_selector('table.datatable, table.table')
        if angular:
            panel_type = "angular"
        elif python_table:
            panel_type = "python"
        else:
            panel_type = "unknown"
        results.append({
            "name": "A4_panel_type_detected",
            "status": "pass",
            "panel_type": panel_type,
        })
    except Exception as e:
        results.append({"name": "A4_panel_type_detected", "status": "fail", "error": str(e)})

    return results
