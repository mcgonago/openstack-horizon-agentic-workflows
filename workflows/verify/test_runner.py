"""Phases 4 and 6: Run Playwright tests before/after patch."""

import asyncio
import importlib.util
import sys
from pathlib import Path
from datetime import datetime, timezone


class VerifyTestRunner:
    """Run recipe test groups via Playwright."""

    def __init__(self, verify_dir, state, phase_label):
        self.verify_dir = Path(verify_dir)
        self.state = state
        self.phase_label = phase_label
        self.results = []
        self.horizon_url = f"http://{state['devstack_host']}:{state.get('horizon_port', 8080)}"

    async def run_groups(self, groups):
        """Run selected test groups."""
        recipe_name = self.state.get("recipe", "generic")
        recipe_dir = self.verify_dir / "recipes" / recipe_name

        for group in groups:
            group_file = self._find_group_module(recipe_dir, group)
            if not group_file:
                self.results.append({
                    "group": group["name"],
                    "status": "skipped",
                    "reason": f"No module for group {group['name']}",
                    "tests": [],
                })
                continue

            print(f"    Group {group['name']}: {group.get('label', '')}")
            group_result = await self._run_group(group, group_file, recipe_dir)
            self.results.append(group_result)

        return self.results

    async def _run_group(self, group, group_file, recipe_dir):
        """Run all tests in a group module."""
        spec = importlib.util.spec_from_file_location(
            f"recipe_{group['name']}", group_file
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        tests_fn = getattr(mod, "run_tests", None)
        if not tests_fn:
            return {
                "group": group["name"],
                "status": "error",
                "reason": "No run_tests() function",
                "tests": [],
            }

        artifacts_dir = Path(self.state["artifacts_dir"]) / self.phase_label
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return {
                "group": group["name"],
                "status": "error",
                "reason": "playwright not installed",
                "tests": [],
            }

        test_results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                ignore_https_errors=True,
            )
            page = await context.new_page()

            try:
                test_results = await tests_fn(
                    page=page,
                    horizon_url=self.horizon_url,
                    admin_user=self.state.get("admin_user", "admin"),
                    admin_password=self.state.get("admin_password", "secret"),
                    artifacts_dir=str(artifacts_dir),
                    phase=self.phase_label,
                )
            except Exception as e:
                test_results = [{
                    "name": f"group_{group['name']}_error",
                    "status": "error",
                    "error": str(e),
                }]
            finally:
                await browser.close()

        passed = sum(1 for t in test_results if t.get("status") == "pass")
        failed = sum(1 for t in test_results if t.get("status") == "fail")
        errors = sum(1 for t in test_results if t.get("status") == "error")

        status = "pass" if failed == 0 and errors == 0 else "fail"
        print(f"      {passed} passed, {failed} failed, {errors} errors")

        return {
            "group": group["name"],
            "label": group.get("label", ""),
            "status": status,
            "tests": test_results,
            "counts": {"pass": passed, "fail": failed, "error": errors},
        }

    def _find_group_module(self, recipe_dir, group):
        """Find Python module for a test group."""
        module_name = group.get("module", "")
        if module_name:
            path = recipe_dir / f"{module_name}.py"
            if path.exists():
                return path

        name_map = {
            "A": "panel_loading",
            "B": "table_features",
            "C": "create_form",
            "D": "import_form",
            "E": "delete",
            "F": "detail_view",
            "G": "chevron_rows",
        }
        module = name_map.get(group["name"], group["name"].lower())
        path = recipe_dir / f"{module}.py"
        return path if path.exists() else None


def run_tests_before(verify_dir, state, args):
    """Phase 4: Run tests against unpatched Horizon."""
    return _run_tests(verify_dir, state, args, "before")


def run_tests_after(verify_dir, state, args):
    """Phase 6: Run tests against patched Horizon."""
    return _run_tests(verify_dir, state, args, "after")


def _run_tests(verify_dir, state, args, phase_label):
    """Common test runner for before/after."""
    verify_dir = Path(verify_dir)
    runner = VerifyTestRunner(verify_dir, state, phase_label)

    try:
        import yaml
    except ImportError:
        raise RuntimeError("pyyaml not installed")

    recipe_yaml = verify_dir / "recipes" / state["recipe"] / "recipe.yaml"
    with open(recipe_yaml) as f:
        recipe = yaml.safe_load(f)

    groups = recipe.get("groups", [])
    selected = state.get("selected_groups")
    if selected:
        groups = [g for g in groups if g["name"] in selected]

    print(f"  Running {len(groups)} test groups ({phase_label})...")

    results = asyncio.run(runner.run_groups(groups))

    state[f"test_results_{phase_label}"] = results
    state[f"test_summary_{phase_label}"] = {
        "total_groups": len(results),
        "passed_groups": sum(1 for r in results if r["status"] == "pass"),
        "failed_groups": sum(1 for r in results if r["status"] == "fail"),
        "total_tests": sum(len(r.get("tests", [])) for r in results),
        "passed_tests": sum(r.get("counts", {}).get("pass", 0) for r in results),
        "failed_tests": sum(r.get("counts", {}).get("fail", 0) for r in results),
    }

    summary = state[f"test_summary_{phase_label}"]
    print(f"  Summary ({phase_label}): "
          f"{summary['passed_groups']}/{summary['total_groups']} groups, "
          f"{summary['passed_tests']}/{summary['total_tests']} tests")

    return state
