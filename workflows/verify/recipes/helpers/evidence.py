"""Screenshot evidence capture for Playwright tests."""

import os
from pathlib import Path

_counter = 0


async def screenshot(page, artifacts_dir, name, phase=""):
    """Take an auto-numbered screenshot."""
    global _counter
    _counter += 1

    artifacts_dir = Path(artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    prefix = f"{phase}_" if phase else ""
    filename = f"{prefix}{_counter:03d}_{name}.png"
    path = artifacts_dir / filename

    await page.screenshot(path=str(path), full_page=True)
    return str(path)


def reset_counter():
    """Reset screenshot counter (call at start of each phase)."""
    global _counter
    _counter = 0
