"""Horizon login helper for Playwright."""


async def login(page, horizon_url, username="admin", password="secret"):
    """Log in to Horizon dashboard."""
    login_url = f"{horizon_url}/auth/login/"
    await page.goto(login_url, wait_until="networkidle", timeout=30000)

    await page.fill('input[name="username"], #id_username', username)
    await page.fill('input[name="password"], #id_password', password)
    await page.click('input[type="submit"], button[type="submit"]')

    await page.wait_for_url("**/project/**", timeout=15000)
