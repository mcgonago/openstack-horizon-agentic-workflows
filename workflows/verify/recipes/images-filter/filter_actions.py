"""Group C: Filter Action tests for Images panel.

Tests the ImageFilterAction that replaces the old tab-based OwnerFilter
with a server-side search dropdown (name, status, disk_format).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))
from horizon_auth import login
from horizon_nav import navigate_to_images
from evidence import screenshot, reset_counter


async def _get_table_row_count(page):
    """Count visible data rows in the images table."""
    rows = await page.query_selector_all(
        'table.datatable tbody tr, table.table tbody tr'
    )
    count = 0
    for row in rows:
        text = (await row.inner_text()).strip()
        if text and "no items" not in text.lower():
            count += 1
    return count


async def _get_table_image_names(page):
    """Extract image names from the visible table rows.

    Horizon renders each data row with a data-display attribute containing
    the resource name: <tr data-display="verify-seed-image" ...>
    """
    names = []
    rows = await page.query_selector_all(
        'table.datatable tbody tr[data-display], '
        'table.table tbody tr[data-display]'
    )
    for row in rows:
        display = await row.get_attribute('data-display')
        if display and display.strip():
            names.append(display.strip())
    return names


async def _select_filter_field(page, value):
    """Select a filter field from the themable-select dropdown.

    Horizon renders FilterAction with filter_type="server" as a Bootstrap
    themable-select dropdown (not a native <select>). The visible UI is a
    button.dropdown-toggle that reveals <li><a data-select-value="..."> items.
    A hidden <select name="images__filter__q_field"> is updated by JS.
    """
    toggle = await page.query_selector(
        'div.table_search .themable-select button.dropdown-toggle, '
        'div.table_search .themable-select .dropdown-toggle'
    )
    if toggle:
        await toggle.click()
        await page.wait_for_timeout(500)
        option = await page.query_selector(
            f'div.table_search .themable-select a[data-select-value="{value}"], '
            f'div.table_search .themable-select li[data-select-value="{value}"] a'
        )
        if option:
            await option.click()
            await page.wait_for_timeout(300)
            return True

    # Fallback: set the hidden select directly
    hidden_select = await page.query_selector(
        'select[name="images__filter__q_field"]'
    )
    if hidden_select:
        await page.select_option(
            'select[name="images__filter__q_field"]', value
        )
        return True

    return False


async def _apply_filter(page, field, value):
    """Select a filter field, type a value, and submit the filter form."""
    selected = await _select_filter_field(page, field)
    if not selected:
        return False

    filter_input = await page.query_selector(
        'input[name="images__filter__q"]'
    )
    if not filter_input:
        return False

    await filter_input.fill(value)
    await page.wait_for_timeout(300)

    submit_btn = await page.query_selector(
        'div.table_search button[type="submit"], '
        'div.table_search button:has-text("Filter")'
    )
    if submit_btn:
        await submit_btn.click()
    else:
        await filter_input.press("Enter")

    await page.wait_for_timeout(2000)
    return True


async def _clear_filter(page):
    """Clear the filter input and submit to restore full listing."""
    filter_input = await page.query_selector(
        'input[name="images__filter__q"]'
    )
    if filter_input:
        await filter_input.fill("")
        await page.wait_for_timeout(300)

        submit_btn = await page.query_selector(
            'div.table_search button[type="submit"], '
            'div.table_search button:has-text("Filter")'
        )
        if submit_btn:
            await submit_btn.click()
        else:
            await filter_input.press("Enter")

        await page.wait_for_timeout(2000)


async def run_tests(page, horizon_url, admin_user, admin_password,
                    artifacts_dir, phase):
    """Run Group C: Filter Action tests."""
    reset_counter()
    results = []

    await login(page, horizon_url, admin_user, admin_password)
    await navigate_to_images(page, horizon_url)

    # C1: Filter dropdown is visible (ImageFilterAction rendered)
    try:
        filter_dropdown = await page.query_selector(
            'div.table_search .themable-select, '
            'select[name="images__filter__q_field"]'
        )
        filter_input = await page.query_selector(
            'input[name="images__filter__q"]'
        )
        filter_button = await page.query_selector(
            'div.table_search button[type="submit"], '
            'div.table_search button:has-text("Filter")'
        )

        all_present = bool(filter_dropdown and filter_input and filter_button)
        await screenshot(page, artifacts_dir, "filter_dropdown_visible", phase)

        details = {
            "dropdown": bool(filter_dropdown),
            "input": bool(filter_input),
            "button": bool(filter_button),
        }
        results.append({
            "name": "C1_filter_dropdown_visible",
            "status": "pass" if all_present else "fail",
            "details": details,
        })
    except Exception as e:
        results.append({
            "name": "C1_filter_dropdown_visible",
            "status": "fail", "error": str(e),
        })

    # C2: OwnerFilter tabs are gone (no FixedFilterAction buttons)
    try:
        # The old OwnerFilter rendered as buttons inside div.table_filter.btn-group
        fixed_filter_group = await page.query_selector(
            'div.table_filter.btn-group'
        )
        project_tab = await page.query_selector(
            'button[name="images__filter__q"][value="project"]'
        )
        public_tab = await page.query_selector(
            'button[name="images__filter__q"][value="public"]'
        )

        tabs_gone = not fixed_filter_group and not project_tab and not public_tab
        await screenshot(page, artifacts_dir, "owner_filter_tabs_gone", phase)

        results.append({
            "name": "C2_owner_filter_tabs_gone",
            "status": "pass" if tabs_gone else "fail",
            "note": "OwnerFilter tabs correctly removed" if tabs_gone
                    else "OwnerFilter tabs still present",
            "details": {
                "fixed_filter_group": bool(fixed_filter_group),
                "project_tab": bool(project_tab),
                "public_tab": bool(public_tab),
            },
        })
    except Exception as e:
        results.append({
            "name": "C2_owner_filter_tabs_gone",
            "status": "fail", "error": str(e),
        })

    # C3: Filter by name
    try:
        initial_count = await _get_table_row_count(page)

        applied = await _apply_filter(page, "name", "verify-seed-image")
        await screenshot(page, artifacts_dir, "filter_by_name", phase)

        if applied:
            filtered_names = await _get_table_image_names(page)
            filtered_count = len(filtered_names)

            name_match = all(
                "verify-seed-image" in n.lower() for n in filtered_names
            ) if filtered_names else False

            results.append({
                "name": "C3_filter_by_name",
                "status": "pass" if name_match and filtered_count > 0 else "fail",
                "initial_count": initial_count,
                "filtered_count": filtered_count,
                "filtered_names": filtered_names[:5],
            })
        else:
            results.append({
                "name": "C3_filter_by_name",
                "status": "fail",
                "error": "could not apply name filter",
            })

        await _clear_filter(page)
        await navigate_to_images(page, horizon_url)
    except Exception as e:
        results.append({
            "name": "C3_filter_by_name",
            "status": "fail", "error": str(e),
        })
        await navigate_to_images(page, horizon_url)

    # C4: Filter by status
    try:
        applied = await _apply_filter(page, "status", "active")
        await screenshot(page, artifacts_dir, "filter_by_status", phase)

        if applied:
            filtered_names = await _get_table_image_names(page)
            # verify-filter-raw2 is deactivated — it should NOT appear
            has_deactivated = any(
                "verify-filter-raw2" in n for n in filtered_names
            )

            results.append({
                "name": "C4_filter_by_status",
                "status": "pass" if not has_deactivated and len(filtered_names) > 0 else "fail",
                "filtered_names": filtered_names[:10],
                "note": "deactivated image correctly excluded" if not has_deactivated
                        else "deactivated image still visible",
            })
        else:
            results.append({
                "name": "C4_filter_by_status",
                "status": "fail",
                "error": "could not apply status filter",
            })

        await _clear_filter(page)
        await navigate_to_images(page, horizon_url)
    except Exception as e:
        results.append({
            "name": "C4_filter_by_status",
            "status": "fail", "error": str(e),
        })
        await navigate_to_images(page, horizon_url)

    # C5: Filter by disk_format
    try:
        applied = await _apply_filter(page, "disk_format", "raw")
        await screenshot(page, artifacts_dir, "filter_by_disk_format", phase)

        if applied:
            filtered_names = await _get_table_image_names(page)
            # Only raw-format images should appear (verify-seed-image, verify-filter-raw2)
            # verify-filter-qcow2 should NOT appear
            has_qcow2 = any(
                "verify-filter-qcow2" in n for n in filtered_names
            )

            results.append({
                "name": "C5_filter_by_disk_format",
                "status": "pass" if not has_qcow2 and len(filtered_names) > 0 else "fail",
                "filtered_names": filtered_names[:10],
                "note": "qcow2 image correctly excluded" if not has_qcow2
                        else "qcow2 image still visible",
            })
        else:
            results.append({
                "name": "C5_filter_by_disk_format",
                "status": "fail",
                "error": "could not apply disk_format filter",
            })

        await _clear_filter(page)
        await navigate_to_images(page, horizon_url)
    except Exception as e:
        results.append({
            "name": "C5_filter_by_disk_format",
            "status": "fail", "error": str(e),
        })
        await navigate_to_images(page, horizon_url)

    # C6: Clear filter restores all images
    try:
        # Apply a filter first to narrow results
        await _apply_filter(page, "name", "verify-seed-image")
        filtered_count = await _get_table_row_count(page)

        # Now clear it
        await _clear_filter(page)
        await page.wait_for_timeout(1000)
        await screenshot(page, artifacts_dir, "clear_filter_restores_all", phase)

        restored_count = await _get_table_row_count(page)
        restored_names = await _get_table_image_names(page)

        results.append({
            "name": "C6_clear_filter_restores_all",
            "status": "pass" if restored_count >= filtered_count else "fail",
            "filtered_count": filtered_count,
            "restored_count": restored_count,
            "restored_names": restored_names[:10],
        })
    except Exception as e:
        results.append({
            "name": "C6_clear_filter_restores_all",
            "status": "fail", "error": str(e),
        })

    return results
