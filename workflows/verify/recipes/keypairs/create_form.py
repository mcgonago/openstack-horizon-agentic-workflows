"""Group C: Create Keypair tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))
from horizon_auth import login
from horizon_nav import navigate_to_keypairs
from evidence import screenshot, reset_counter


async def _open_create_form(page):
    """Click Create Key Pair and wait for the form fields to appear."""
    await page.click(
        '#keypairs__action_create, '
        'a:has-text("Create Key Pair"), '
        '.btn:has-text("Create Key Pair")',
        timeout=10000,
    )
    await page.wait_for_selector(
        '#id_name, input[name="name"]',
        state="visible", timeout=10000,
    )


async def run_tests(page, horizon_url, admin_user, admin_password,
                    artifacts_dir, phase):
    """Run Group C: Create Keypair tests."""
    reset_counter()
    results = []

    await login(page, horizon_url, admin_user, admin_password)
    await navigate_to_keypairs(page, horizon_url)

    # C1: Create SSH keypair
    try:
        await _open_create_form(page)
        await screenshot(page, artifacts_dir, "create_form_open", phase)

        await page.fill('#id_name, input[name="name"]', "verify-create-ssh")

        type_select = await page.query_selector('#id_key_type, select[name="key_type"]')
        if type_select:
            await type_select.select_option("ssh")

        submit_sel = (
            '.modal-footer .btn-primary, '
            '.modal-footer input[type="submit"], '
            '.modal-footer button[type="submit"]'
        )
        download = None
        try:
            async with page.expect_download(timeout=10000) as dl:
                await page.click(submit_sel, timeout=10000)
            download = await dl.value
        except Exception:
            await page.wait_for_timeout(3000)

        await screenshot(page, artifacts_dir, "create_ssh_done", phase)
        results.append({"name": "C1_create_ssh_keypair", "status": "pass",
                        "downloaded": download is not None})
    except Exception as e:
        results.append({"name": "C1_create_ssh_keypair", "status": "fail", "error": str(e)})

    await navigate_to_keypairs(page, horizon_url)

    # C2: Create X509 keypair
    try:
        await _open_create_form(page)

        await page.fill('#id_name, input[name="name"]', "verify-create-x509")

        type_select = await page.query_selector('#id_key_type, select[name="key_type"]')
        if type_select:
            await type_select.select_option("x509")

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

        await screenshot(page, artifacts_dir, "create_x509_done", phase)
        results.append({"name": "C2_create_x509_keypair", "status": "pass"})
    except Exception as e:
        results.append({"name": "C2_create_x509_keypair", "status": "fail", "error": str(e)})

    await navigate_to_keypairs(page, horizon_url)

    # C3: Verify created keypairs appear in table
    try:
        await page.wait_for_timeout(2000)
        page_text = await page.inner_text('body')
        ssh_visible = "verify-create-ssh" in page_text
        x509_visible = "verify-create-x509" in page_text
        await screenshot(page, artifacts_dir, "created_keypairs_table", phase)
        status = "pass" if ssh_visible and x509_visible else "fail"
        results.append({
            "name": "C3_keypairs_appear_in_table",
            "status": status,
            "ssh_visible": ssh_visible,
            "x509_visible": x509_visible,
        })
    except Exception as e:
        results.append({"name": "C3_keypairs_appear_in_table", "status": "fail",
                        "error": str(e)})

    return results
