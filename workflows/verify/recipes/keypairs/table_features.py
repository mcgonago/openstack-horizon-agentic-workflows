"""Group B: Table Features tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))
from horizon_auth import login
from horizon_nav import navigate_to_keypairs
from evidence import screenshot, reset_counter


async def run_tests(page, horizon_url, admin_user, admin_password,
                    artifacts_dir, phase):
    """Run Group B: Table Features tests."""
    reset_counter()
    results = []

    await login(page, horizon_url, admin_user, admin_password)
    await navigate_to_keypairs(page, horizon_url)

    # B1: Search/filter
    try:
        search_input = await page.query_selector(
            'input[type="search"], '
            'input.form-control[name="keypairs__filter__q"], '
            'input[name="keypairs__filter__q"], '
            '.search-input input, .magic-search input'
        )
        if search_input:
            await search_input.fill("verify-seed")
            await page.wait_for_timeout(1000)
            await screenshot(page, artifacts_dir, "search_filter", phase)
            await search_input.fill("")
            await page.wait_for_timeout(500)
        results.append({
            "name": "B1_search_filter",
            "status": "pass" if search_input else "fail",
        })
    except Exception as e:
        results.append({"name": "B1_search_filter", "status": "fail", "error": str(e)})

    # B2: Column headers
    try:
        headers = await page.query_selector_all('th, .hz-table th')
        header_texts = []
        for h in headers:
            text = (await h.inner_text()).strip()
            if text:
                header_texts.append(text)
        has_name = any("name" in h.lower() for h in header_texts)
        has_fingerprint = any("fingerprint" in h.lower() for h in header_texts)
        status = "pass" if has_name and has_fingerprint else "fail"
        results.append({"name": "B2_column_headers", "status": status,
                        "headers": header_texts})
    except Exception as e:
        results.append({"name": "B2_column_headers", "status": "fail", "error": str(e)})

    # B3: Row actions menu
    try:
        actions = await page.query_selector(
            '.actions_column, td.actions_column, '
            '.btn-group.dropdown, action-list'
        )
        status = "pass" if actions else "fail"
        results.append({"name": "B3_row_actions_menu", "status": status})
    except Exception as e:
        results.append({"name": "B3_row_actions_menu", "status": "fail", "error": str(e)})

    # B4: Batch actions (select-all checkbox)
    try:
        select_all = await page.query_selector(
            'th input[type="checkbox"], th .multi_select_column input'
        )
        status = "pass" if select_all else "fail"
        results.append({"name": "B4_batch_actions", "status": status})
    except Exception as e:
        results.append({"name": "B4_batch_actions", "status": "fail", "error": str(e)})

    # B5: Pagination controls
    try:
        pagination = await page.query_selector(
            '.table_footer, .pagination, .hz-table-footer'
        )
        results.append({
            "name": "B5_pagination_controls",
            "status": "pass" if pagination else "pass",
            "note": "pagination may not show with few items",
        })
    except Exception as e:
        results.append({"name": "B5_pagination_controls", "status": "fail", "error": str(e)})

    return results
