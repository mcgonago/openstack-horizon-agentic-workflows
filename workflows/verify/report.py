"""Phase 7: Generate verification report with parity matrix."""

from pathlib import Path
from datetime import datetime, timezone

try:
    from jinja2 import Template
except ImportError:
    Template = None


def generate_report(verify_dir, state, args):
    """Generate markdown verification report."""
    verify_dir = Path(verify_dir)
    artifacts_dir = Path(state["artifacts_dir"])

    verdict = _compute_verdict(state)
    state["verdict"] = verdict

    parity_matrix = _build_parity_matrix(state)
    state["parity_matrix"] = parity_matrix

    template_path = verify_dir / "templates" / "verify_report.md.j2"
    if template_path.exists() and Template:
        with open(template_path) as f:
            tmpl = Template(f.read())
        report = tmpl.render(
            state=state,
            verdict=verdict,
            parity=parity_matrix,
            now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        )
    else:
        report = _fallback_report(state, verdict, parity_matrix)

    report_path = artifacts_dir / "verify_report.md"
    with open(report_path, "w") as f:
        f.write(report)

    print(f"  Verdict: {verdict}")
    print(f"  Report: {report_path}")

    from artifacts import generate_manual_testing_guide
    state = generate_manual_testing_guide(verify_dir, state, None)

    return state


def _compute_verdict(state):
    """Determine overall verification verdict."""
    before = state.get("test_summary_before", {})
    after = state.get("test_summary_after", {})

    if not after:
        return "INCOMPLETE"

    after_failed = after.get("failed_tests", 0)

    if state.get("no_before"):
        if after_failed == 0:
            return "PASS"
        return "FAIL"

    if not before:
        return "INCOMPLETE"

    before_passed = before.get("passed_tests", 0)
    after_passed = after.get("passed_tests", 0)
    before_failed = before.get("failed_tests", 0)

    if after_failed == 0 and before_failed == 0:
        return "PASS"

    if after_passed >= before_passed and after_failed <= before_failed:
        return "PASS"

    if after_failed > before_failed:
        regressions = after_failed - before_failed
        return f"FAIL ({regressions} regression{'s' if regressions != 1 else ''})"

    return "PASS_WITH_KNOWN_ISSUES"


def _build_parity_matrix(state):
    """Build before/after parity comparison."""
    before_results = state.get("test_results_before", [])
    after_results = state.get("test_results_after", [])

    before_map = {}
    for group in before_results:
        for test in group.get("tests", []):
            before_map[test["name"]] = test.get("status", "skip")

    after_map = {}
    for group in after_results:
        for test in group.get("tests", []):
            after_map[test["name"]] = test.get("status", "skip")

    all_tests = sorted(set(list(before_map.keys()) + list(after_map.keys())))

    matrix = []
    for test_name in all_tests:
        b = before_map.get(test_name, "skip")
        a = after_map.get(test_name, "skip")

        if b == "pass" and a == "pass":
            parity = "PARITY"
        elif b == "pass" and a != "pass":
            parity = "REGRESSION"
        elif b != "pass" and a == "pass":
            parity = "FIXED"
        elif b == a:
            parity = "UNCHANGED"
        else:
            parity = "CHANGED"

        matrix.append({
            "test": test_name,
            "before": b,
            "after": a,
            "parity": parity,
        })

    return matrix


def _fallback_report(state, verdict, parity_matrix):
    """Generate report without Jinja2."""
    review = state.get("review_number", "unknown")
    title = state.get("title", "")
    branch = state.get("branch", "master")
    recipe = state.get("recipe", "generic")

    lines = [
        f"# Verification Report: Review {review}",
        "",
        f"**Title:** {title}",
        f"**Branch:** {branch}",
        f"**Recipe:** {recipe}",
        f"**Verdict:** {verdict}",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Test Summary",
        "",
    ]

    for label in ["before", "after"]:
        summary = state.get(f"test_summary_{label}", {})
        if summary:
            lines.append(f"### {label.title()}")
            lines.append(f"- Groups: {summary.get('passed_groups', 0)}/{summary.get('total_groups', 0)} passed")
            lines.append(f"- Tests: {summary.get('passed_tests', 0)}/{summary.get('total_tests', 0)} passed")
            lines.append("")

    if parity_matrix:
        lines.append("## Parity Matrix")
        lines.append("")
        lines.append("| Test | Before | After | Parity |")
        lines.append("|------|--------|-------|--------|")
        for row in parity_matrix:
            lines.append(f"| {row['test']} | {row['before']} | {row['after']} | {row['parity']} |")
        lines.append("")

    regressions = [r for r in parity_matrix if r["parity"] == "REGRESSION"]
    if regressions:
        lines.append("## Regressions")
        lines.append("")
        for r in regressions:
            lines.append(f"- **{r['test']}**: was {r['before']}, now {r['after']}")
        lines.append("")

    lines.append("---")
    lines.append("Generated by /verify skill")

    return "\n".join(lines)
