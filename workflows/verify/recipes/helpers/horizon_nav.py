"""Horizon navigation helpers for Playwright."""


async def navigate_to_keypairs(page, horizon_url):
    """Navigate to Project > Compute > Key Pairs."""
    url = f"{horizon_url}/project/key_pairs/"
    await page.goto(url, wait_until="networkidle", timeout=30000)
    await page.wait_for_selector(
        'table, hz-resource-table, .table_wrapper',
        timeout=15000,
    )
