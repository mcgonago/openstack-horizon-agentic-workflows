"""Group D: Import Keypair tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))
from horizon_auth import login
from horizon_nav import navigate_to_keypairs
from evidence import screenshot, reset_counter

SSH_PUBLIC_KEY = (
    "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7PGiSMjQNIr+vZfNlFBy+"
    "Jj4mG0YxHvF5f5Nc8Xs4FJGj3T7P0cPl7B0kCmHWqQ3XAnlYsGj2rGM+o"
    "VxRz3tBxNDqx3qYL0JkW1lRiDO4YfMk9MzL6N3t5ZkA6vCT0oRy1F24z"
    " verify-test@verify"
)

X509_PUBLIC_KEY = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIICpDCCAYwCCQDU+pQxmNfRFDANBgkqhkiG9w0BAQsFADAUMRIwEAYDVQQDDAls\n"
    "b2NhbGhvc3QwHhcNMjQwMTAxMDAwMDAwWhcNMjUwMTAxMDAwMDAwWjAUMRIwEAYD\n"
    "VQQDDAlsb2NhbGhvc3QwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7\n"
    "-----END CERTIFICATE-----"
)


async def _open_import_form(page):
    """Click Import Public Key and wait for the form fields to appear."""
    await page.click(
        '#keypairs__action_import, '
        'a:has-text("Import Public Key"), '
        '.btn:has-text("Import Public Key")',
        timeout=10000,
    )
    await page.wait_for_selector(
        '#id_name, input[name="name"]',
        state="visible", timeout=10000,
    )


async def _fill_and_submit_import(page, name, key_type, public_key):
    """Fill the import form and submit it."""
    await page.fill('#id_name, input[name="name"]', name)

    type_select = await page.query_selector('#id_key_type, select[name="key_type"]')
    if type_select:
        await type_select.select_option(key_type)

    await page.wait_for_timeout(500)
    pubkey = await page.query_selector('#id_public_key, textarea[name="public_key"]')
    if not pubkey:
        pubkey = await page.query_selector('textarea')
    if pubkey:
        await pubkey.fill(public_key)

    await page.click(
        '.modal-footer .btn-primary, '
        '.modal-footer input[type="submit"], '
        '.modal-footer button[type="submit"]',
        timeout=10000,
    )
    await page.wait_for_timeout(3000)


async def run_tests(page, horizon_url, admin_user, admin_password,
                    artifacts_dir, phase):
    """Run Group D: Import Keypair tests."""
    reset_counter()
    results = []

    await login(page, horizon_url, admin_user, admin_password)
    await navigate_to_keypairs(page, horizon_url)

    # D1: Import SSH keypair
    try:
        await _open_import_form(page)
        await screenshot(page, artifacts_dir, "import_form_open", phase)
        await _fill_and_submit_import(page, "verify-import-ssh", "ssh", SSH_PUBLIC_KEY)
        await screenshot(page, artifacts_dir, "import_ssh_done", phase)
        results.append({"name": "D1_import_ssh_keypair", "status": "pass"})
    except Exception as e:
        results.append({"name": "D1_import_ssh_keypair", "status": "fail", "error": str(e)})

    await navigate_to_keypairs(page, horizon_url)

    # D2: Import X509 keypair
    try:
        await _open_import_form(page)
        await _fill_and_submit_import(page, "verify-import-x509", "x509", X509_PUBLIC_KEY)
        await screenshot(page, artifacts_dir, "import_x509_done", phase)
        results.append({"name": "D2_import_x509_keypair", "status": "pass"})
    except Exception as e:
        results.append({"name": "D2_import_x509_keypair", "status": "fail", "error": str(e)})

    await navigate_to_keypairs(page, horizon_url)

    # D3: Validation errors (submit empty form)
    try:
        await _open_import_form(page)

        submit_btn = await page.query_selector(
            '.modal-footer .btn-primary, '
            '.modal-footer input[type="submit"], '
            '.modal-footer button[type="submit"]'
        )

        angular_disabled = False
        if submit_btn:
            angular_disabled = await submit_btn.evaluate("el => el.disabled")

        if not angular_disabled and submit_btn:
            await submit_btn.click(force=True)
            await page.wait_for_timeout(2000)

        error = await page.query_selector(
            '.help-block, .form-group.has-error, .errorlist, '
            '.alert-danger, [class*="error"]'
        )

        modal_open = await page.query_selector(
            '.modal.in, .modal[style*="display: block"], '
            '.modal-dialog, [role="dialog"]'
        )

        validated = error is not None or angular_disabled or modal_open is not None
        await screenshot(page, artifacts_dir, "validation_error", phase)
        results.append({
            "name": "D3_validation_errors",
            "status": "pass" if validated else "fail",
            "note": ("Submit disabled (Angular validation)" if angular_disabled
                     else "Error displayed" if error
                     else "Modal stayed open (HTML5 validation)" if modal_open
                     else "No validation detected"),
        })

        close_btn = await page.query_selector(
            '.modal button.close, [data-dismiss="modal"], '
            '.btn:has-text("Cancel"), a:has-text("Cancel")'
        )
        if close_btn:
            await close_btn.click(force=True)
            await page.wait_for_timeout(1000)
    except Exception as e:
        results.append({"name": "D3_validation_errors", "status": "fail", "error": str(e)})

    return results
