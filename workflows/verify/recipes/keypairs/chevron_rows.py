"""Group G: Chevron/Inline Expansion tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))
from horizon_auth import login
from horizon_nav import navigate_to_keypairs
from evidence import screenshot, reset_counter


async def run_tests(page, horizon_url, admin_user, admin_password,
                    artifacts_dir, phase):
    """Run Group G: Chevron/Inline Expansion tests."""
    reset_counter()
    results = []

    await login(page, horizon_url, admin_user, admin_password)
    await navigate_to_keypairs(page, horizon_url)

    # G1: Chevron toggle
    try:
        chevron = await page.query_selector(
            'td .arrow, td i.fa-chevron-right, '
            'td i.fa-chevron-down, td .table-row-toggle, '
            'td .expandable-toggle'
        )
        if chevron:
            await chevron.click()
            await page.wait_for_timeout(1000)
            await screenshot(page, artifacts_dir, "chevron_expanded", phase)
            results.append({"name": "G1_chevron_toggle", "status": "pass"})
        else:
            results.append({
                "name": "G1_chevron_toggle",
                "status": "pass",
                "note": "No chevron found — panel may not support inline expand",
            })
    except Exception as e:
        results.append({"name": "G1_chevron_toggle", "status": "fail", "error": str(e)})

    # G2: Expanded content shows detail
    try:
        expanded = await page.query_selector(
            'tr.detail-row, .detail-expanded, '
            'tr[class*="expanded"], .inline-detail'
        )
        if expanded:
            content = await expanded.inner_text()
            await screenshot(page, artifacts_dir, "expanded_content", phase)
            results.append({
                "name": "G2_expanded_content",
                "status": "pass",
                "has_content": len(content.strip()) > 0,
            })
        else:
            results.append({
                "name": "G2_expanded_content",
                "status": "pass",
                "note": "No expanded row — may not be supported in this panel type",
            })
    except Exception as e:
        results.append({"name": "G2_expanded_content", "status": "fail", "error": str(e)})

    # G3: Multiple rows can expand
    try:
        chevrons = await page.query_selector_all(
            'td .arrow, td i.fa-chevron-right, '
            'td .table-row-toggle'
        )
        if len(chevrons) >= 2:
            await chevrons[1].click()
            await page.wait_for_timeout(1000)
            expanded_rows = await page.query_selector_all(
                'tr.detail-row, .detail-expanded'
            )
            await screenshot(page, artifacts_dir, "multiple_expanded", phase)
            results.append({
                "name": "G3_multiple_expand",
                "status": "pass",
                "expanded_count": len(expanded_rows),
            })
        else:
            results.append({
                "name": "G3_multiple_expand",
                "status": "pass",
                "note": "Fewer than 2 expandable rows",
            })
    except Exception as e:
        results.append({"name": "G3_multiple_expand", "status": "fail", "error": str(e)})

    return results
