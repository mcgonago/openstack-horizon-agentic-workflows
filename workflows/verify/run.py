#!/usr/bin/env python3
"""
/verify skill entry point.
Orchestrates the 7-phase verification pipeline for Horizon Gerrit reviews.
"""

import argparse
import os
import signal
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# Add this directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from state import load_state, save_state


def parse_args():
    parser = argparse.ArgumentParser(
        description="Verify a Horizon Gerrit review end-to-end"
    )
    parser.add_argument("review_number", type=int,
                        help="Gerrit review number (e.g., 992714)")
    parser.add_argument("--execute", action="store_true",
                        help="Auto-execute without pausing")
    parser.add_argument("--phase", type=int, default=1,
                        help="Resume from phase N (1-7)")
    parser.add_argument("--groups", type=str, default="",
                        help="Comma-separated test groups (A,B,C,...)")
    parser.add_argument("--no-before", action="store_true",
                        help="Skip baseline testing")
    parser.add_argument("--post-merge", action="store_true",
                        help="Review already merged; revert for baseline")
    parser.add_argument("--cleanup", action="store_true",
                        help="Delete test resources and exit")
    parser.add_argument("--status", action="store_true",
                        help="Print state and exit")
    parser.add_argument("--artifacts-only", action="store_true",
                        dest="artifacts_only",
                        help="Generate artifacts (manual testing guide) without running tests")
    parser.add_argument("--recipe", type=str, default="",
                        help="Force recipe name (e.g., keypairs) instead of auto-match")
    parser.add_argument("--devstack", type=str, default="",
                        help="Override DevStack host (plain SSH mode)")

    virtctl_group = parser.add_argument_group("virtctl", "ITUp / OpenShift Virtualization options")
    virtctl_group.add_argument("--virtctl", action="store_true",
                               help="Use virtctl ssh instead of plain SSH")
    virtctl_group.add_argument("--vm", type=str, default="",
                               help="VM name (default: horizon-devstack)")
    virtctl_group.add_argument("--namespace", "-n", type=str, default="",
                               help="Namespace (default: rhos-dfg-ui--runtime-int)")
    virtctl_group.add_argument("--identity-file", type=str, default="",
                               dest="identity_file",
                               help="SSH key path (default: ~/.ssh/id_ed25519)")
    virtctl_group.add_argument("--ssh-user", type=str, default="",
                               dest="ssh_user",
                               help="SSH user (default: ubuntu)")
    return parser.parse_args()


def _get_phases():
    """Build phases list with lazy imports."""
    from context import resolve_context
    from environment import setup_environment, cleanup_resources
    from deploy import deploy_before, deploy_after
    from test_runner import run_tests_before, run_tests_after
    from report import generate_report

    return [
        (1, "Context",        resolve_context),
        (2, "Environment",    setup_environment),
        (3, "Deploy Before",  deploy_before),
        (4, "Test Before",    run_tests_before),
        (5, "Deploy After",   deploy_after),
        (6, "Test After",     run_tests_after),
        (7, "Report",         generate_report),
    ]


PHASE_NAMES = [
    "", "Context", "Environment", "Deploy Before",
    "Test Before", "Deploy After", "Test After", "Report"
]


def main():
    args = parse_args()
    verify_dir = Path(__file__).parent
    artifacts_dir = verify_dir / "artifacts" / f"verify-{args.review_number}"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    state = load_state(artifacts_dir)
    state["review_number"] = args.review_number
    state["artifacts_dir"] = str(artifacts_dir)
    state["verify_dir"] = str(verify_dir)

    if args.status:
        _print_status(state)
        return 0

    if args.cleanup:
        from environment import cleanup_resources
        cleanup_resources(state, args)
        return 0

    if args.groups:
        state["selected_groups"] = [g.strip().upper() for g in args.groups.split(",")]
    else:
        state["selected_groups"] = None

    state["no_before"] = args.no_before
    state["post_merge"] = args.post_merge
    state["recipe_override"] = args.recipe
    state["devstack_override"] = args.devstack
    state["started_at"] = datetime.now(timezone.utc).isoformat()

    if args.artifacts_only:
        return _run_artifacts_only(verify_dir, artifacts_dir, state, args)

    phases = _get_phases()
    start_phase = args.phase
    start_time = time.time()
    rc = 0

    try:
        for phase_num, phase_name, phase_fn in phases:
            if phase_num < start_phase:
                print(f"  [SKIP] Phase {phase_num}: {phase_name} (resuming from --phase {start_phase})")
                continue

            if args.no_before and phase_num in (3, 4):
                print(f"  [SKIP] Phase {phase_num}: {phase_name} (--no-before)")
                state[f"phase_{phase_num}_status"] = "skipped"
                save_state(state, artifacts_dir)
                continue

            print(f"\n{'='*60}")
            print(f"  Phase {phase_num}: {phase_name}")
            print(f"{'='*60}")

            try:
                state = phase_fn(verify_dir, state, args)
                state[f"phase_{phase_num}_status"] = "completed"
                save_state(state, artifacts_dir)
                print(f"  [DONE] Phase {phase_num}: {phase_name}")
            except Exception as e:
                state[f"phase_{phase_num}_status"] = "failed"
                state[f"phase_{phase_num}_error"] = str(e)
                save_state(state, artifacts_dir)
                print(f"  [FAIL] Phase {phase_num}: {phase_name}: {e}")
                import traceback
                traceback.print_exc()
                rc = 1
                break

        elapsed = time.time() - start_time
        state["total_duration_s"] = elapsed
        state["completed_at"] = datetime.now(timezone.utc).isoformat()
        save_state(state, artifacts_dir)

        if rc == 0:
            _register_workflow_yaml(state, verify_dir)

        print(f"\n{'='*60}")
        print(f"  Verification {'complete' if rc == 0 else 'failed'} in {elapsed:.0f}s")
        print(f"  Verdict: {state.get('verdict', 'INCOMPLETE')}")
        print(f"  Report: {artifacts_dir / 'verify_report.md'}")
        print(f"{'='*60}")

    finally:
        _cleanup_horizon(state)

    return rc


def _run_artifacts_only(verify_dir, artifacts_dir, state, args):
    """Generate artifacts without running the full 7-phase pipeline."""
    from context import resolve_context
    from artifacts import generate_manual_testing_guide

    print(f"\n{'='*60}")
    print(f"  Phase 1: Context (artifacts-only mode)")
    print(f"{'='*60}")

    try:
        state = resolve_context(verify_dir, state, args)
        state["phase_1_status"] = "completed"
    except Exception as e:
        print(f"  [FAIL] Context resolution: {e}")
        state["phase_1_status"] = "failed"
        save_state(state, artifacts_dir)
        return 1

    print(f"\n{'='*60}")
    print(f"  Generating artifacts (--artifacts-only)")
    print(f"{'='*60}")

    state = generate_manual_testing_guide(verify_dir, state, args)
    state["completed_at"] = datetime.now(timezone.utc).isoformat()
    save_state(state, artifacts_dir)
    _register_workflow_yaml(state, verify_dir)

    print(f"\n{'='*60}")
    print(f"  Artifacts generated successfully")
    guide_path = state.get("manual_testing_guide_path", "")
    print(f"  Manual testing guide: {guide_path}")
    print(f"{'='*60}")

    return 0


def _cleanup_horizon(state):
    """Kill any orphaned local Horizon process."""
    pid = state.get("horizon_pid")
    if not pid:
        return
    print(f"\n  Cleaning up local Horizon (pid {pid})...")
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    except ProcessLookupError:
        pass


def _print_status(state):
    """Print current verification state."""
    review = state.get("review_number", "unknown")
    print(f"\n  Review: {review}")
    print(f"  Title: {state.get('title', '(not yet fetched)')}")
    print(f"  Recipe: {state.get('recipe', '(not yet matched)')}")
    print()
    for i in range(1, 8):
        status = state.get(f"phase_{i}_status", "pending")
        error = state.get(f"phase_{i}_error", "")
        icon = {"completed": "+", "failed": "!", "skipped": "-", "pending": " "}.get(status, "?")
        line = f"  [{icon}] Phase {i} ({PHASE_NAMES[i]}): {status}"
        if error:
            line += f" — {error[:60]}"
        print(line)
    print(f"\n  Verdict: {state.get('verdict', 'INCOMPLETE')}")
    if state.get("total_duration_s"):
        print(f"  Duration: {state['total_duration_s']:.0f}s")


def _register_workflow_yaml(state, verify_dir):
    """Write workflow YAML for dashboard discovery."""
    try:
        import yaml
    except ImportError:
        print("  [WARN] pyyaml not installed; skipping workflow YAML generation")
        return

    review = state["review_number"]
    workflow = {
        "schema_version": 2,
        "ticket": {
            "key": f"REVIEW-{review}",
            "summary": state.get("title", ""),
            "source": "gerrit",
            "url": f"https://review.opendev.org/c/openstack/horizon/+/{review}",
        },
        "project": {
            "name": state.get("project", "openstack/horizon"),
            "branch": state.get("branch", "master"),
        },
        "workflow": {
            "skill": "verify",
            "status": "completed" if state.get("verdict") else "incomplete",
            "verdict": state.get("verdict", "INCOMPLETE"),
            "started": state.get("started_at", ""),
            "completed": state.get("completed_at", ""),
        },
        "phases": [
            {"name": PHASE_NAMES[i], "status": state.get(f"phase_{i}_status", "pending")}
            for i in range(1, 8)
        ],
        "artifacts": [
            {"id": "verification_report", "path": f"artifacts/verify-{review}/verify_report.md"},
            {"id": "manual_testing_guide", "path": f"artifacts/verify-{review}/manual_testing_guide.md"},
            {"id": "evidence_before", "path": f"artifacts/verify-{review}/before/"},
            {"id": "evidence_after", "path": f"artifacts/verify-{review}/after/"},
        ],
    }

    # Write to ioshaworkflow data dirs (relative to repo root)
    repo_root = verify_dir.parent.parent
    iosha_root = repo_root.parent / "ioshaworkflow"
    for data_dir in ["data", "data-dev"]:
        out_dir = iosha_root / data_dir / "feature_workflows"
        if out_dir.parent.exists():
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{review}__verify.yaml"
            with open(out_path, "w") as f:
                yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
            print(f"  Workflow YAML: {out_path}")


if __name__ == "__main__":
    sys.exit(main())
