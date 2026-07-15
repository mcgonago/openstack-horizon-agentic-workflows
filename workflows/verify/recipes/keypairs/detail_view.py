"""Group F: Detail View tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))
from horizon_auth import login
from horizon_nav import navigate_to_keypairs
from evidence import screenshot, reset_counter

KEYPAIR_LINK_SEL = (
    'td a[href*="key_pairs/"], '
    'td a[href*="ngdetails/"], '
    'td.anchor a, '
    'hz-cell a, '
    'tr[data-display] td a, '
    'tr[data-object-id] td a'
)


async def _ensure_keypair_exists(page, horizon_url):
    """Create a keypair via the UI if none exist."""
    await page.click(
        '#keypairs__action_create, '
        'a:has-text("Create Key Pair"), '
        '.btn:has-text("Create Key Pair"), '
        'button:has-text("Create Key Pair")',
        timeout=10000,
    )
    await page.wait_for_selector(
        '#id_name, input[name="name"]', state="visible", timeout=10000,
    )
    await page.fill('#id_name, input[name="name"]', "verify-detail-seed")

    submit_sel = (
        '.modal-footer .btn-primary, '
        '.modal-footer input[type="submit"], '
        '.modal-footer button[type="submit"]'
    )
    try:
        async with page.expect_download(timeout=10000) as dl:
            await page.click(submit_sel, timeout=10000)
        await dl.value
    except Exception:
        await page.wait_for_timeout(3000)

    await navigate_to_keypairs(page, horizon_url)
    await page.wait_for_timeout(2000)


async def run_tests(page, horizon_url, admin_user, admin_password,
                    artifacts_dir, phase):
    """Run Group F: Detail View tests."""
    reset_counter()
    results = []

    await login(page, horizon_url, admin_user, admin_password)
    await navigate_to_keypairs(page, horizon_url)

    # F1: Click a keypair name to open detail
    detail_loaded = False
    try:
        keypair_link = await page.query_selector(KEYPAIR_LINK_SEL)

        if not keypair_link:
            await _ensure_keypair_exists(page, horizon_url)
            keypair_link = await page.query_selector(KEYPAIR_LINK_SEL)

        if keypair_link:
            keypair_name = await keypair_link.inner_text()
            await keypair_link.click(force=True)
            await page.wait_for_timeout(3000)
            await screenshot(page, artifacts_dir, "detail_view", phase)
            detail_loaded = True
            results.append({"name": "F1_detail_page_loads", "status": "pass",
                            "keypair": keypair_name.strip()})
        else:
            results.append({"name": "F1_detail_page_loads", "status": "fail",
                            "error": "No keypair link found"})
    except Exception as e:
        results.append({"name": "F1_detail_page_loads", "status": "fail", "error": str(e)})

    # F2: Fingerprint shown on detail page
    try:
        page_text = await page.inner_text('body')
        has_fingerprint = any(
            marker in page_text.lower()
            for marker in ["fingerprint", "finger print"]
        )
        results.append({
            "name": "F2_detail_shows_fingerprint",
            "status": "pass" if has_fingerprint else "fail",
        })
    except Exception as e:
        results.append({"name": "F2_detail_shows_fingerprint", "status": "fail",
                        "error": str(e)})

    # F3: Public key shown on detail page
    try:
        page_text = await page.inner_text('body')
        has_pubkey = any(
            marker in page_text
            for marker in ["ssh-rsa", "Public Key", "public_key", "BEGIN"]
        )
        await screenshot(page, artifacts_dir, "detail_pubkey", phase)
        results.append({
            "name": "F3_detail_shows_public_key",
            "status": "pass" if has_pubkey else "fail",
        })
    except Exception as e:
        results.append({"name": "F3_detail_shows_public_key", "status": "fail",
                        "error": str(e)})

    # F4: Back navigation to key pairs list
    try:
        if detail_loaded:
            await page.goto(
                f"{horizon_url}/project/key_pairs/",
                wait_until="networkidle", timeout=15000,
            )
        else:
            await navigate_to_keypairs(page, horizon_url)

        table = await page.query_selector('table, hz-resource-table')
        await screenshot(page, artifacts_dir, "back_to_list", phase)
        results.append({
            "name": "F4_back_navigation",
            "status": "pass" if table else "fail",
        })
    except Exception as e:
        results.append({"name": "F4_back_navigation", "status": "fail", "error": str(e)})

    return results
