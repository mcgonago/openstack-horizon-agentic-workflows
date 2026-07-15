"""Phases 3 and 5: Clone, configure, apply patch, start Horizon.

Supports two deploy modes:
  - "local"  (--virtctl): clone/patch/tox on the laptop, Keystone via port-forward
  - "remote" (--devstack): clone/patch/tox on the DevStack VM via SSH
"""

import os
import signal
import subprocess
import time
import urllib.request
import urllib.error
from pathlib import Path

from environment import DevStackConnection


HORIZON_REPO = "https://opendev.org/openstack/horizon.git"
GERRIT_FETCH = "https://review.opendev.org/openstack/horizon"
REMOTE_DEPLOY_DIR = "/opt/stack/horizon-verify"
LOCAL_PORT = 9000
REMOTE_PORT = 8080


# ---------------------------------------------------------------------------
# Public API -- route to local or remote based on state["deploy_mode"]
# ---------------------------------------------------------------------------

def deploy_before(verify_dir, state, args):
    """Phase 3: Deploy unpatched Horizon (baseline)."""
    if state.get("deploy_mode") == "local":
        return _deploy_before_local(verify_dir, state, args)
    return _deploy_before_remote(verify_dir, state, args)


def deploy_after(verify_dir, state, args):
    """Phase 5: Apply review patch and restart Horizon."""
    if state.get("deploy_mode") == "local":
        return _deploy_after_local(verify_dir, state, args)
    return _deploy_after_remote(verify_dir, state, args)


# ---------------------------------------------------------------------------
# LOCAL mode -- clone/patch/tox on the laptop
# ---------------------------------------------------------------------------

def _deploy_before_local(verify_dir, state, args):
    verify_dir = Path(verify_dir)
    checkout_dir = Path(state["artifacts_dir"]) / "horizon-checkout"

    _kill_local_horizon(state)

    if checkout_dir.exists():
        print("  Using existing local checkout...")
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=checkout_dir, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "checkout", f"origin/{state['branch']}"],
            cwd=checkout_dir, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "reset", "--hard"],
            cwd=checkout_dir, check=True, capture_output=True, text=True,
        )
    else:
        print("  Cloning Horizon to local checkout...")
        subprocess.run(
            ["git", "clone", HORIZON_REPO, str(checkout_dir)],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "checkout", f"origin/{state['branch']}"],
            cwd=checkout_dir, check=True, capture_output=True, text=True,
        )

    commit = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=checkout_dir, capture_output=True, text=True,
    )
    state["before_commit"] = commit.stdout.strip()
    print(f"    Base commit: {state['before_commit']}")

    print("  Configuring local_settings.py (AngularJS baseline)...")
    angular_features = _get_angular_features(verify_dir, state, baseline=True)
    _write_local_settings_file(checkout_dir, angular_features=angular_features)

    _apply_local_fixups(verify_dir, checkout_dir, state)

    print(f"  Starting Horizon locally on port {LOCAL_PORT}...")
    proc = _start_local_horizon(checkout_dir, state, "before")
    state["horizon_pid"] = proc.pid

    _wait_for_server("localhost", LOCAL_PORT)

    state["deploy_before"] = {
        "commit": state["before_commit"],
        "angular_keypairs": True,
        "url": f"http://localhost:{LOCAL_PORT}",
        "ready": True,
        "mode": "local",
        "checkout_dir": str(checkout_dir),
    }
    state["horizon_port"] = LOCAL_PORT

    return state


def _deploy_after_local(verify_dir, state, args):
    verify_dir = Path(verify_dir)

    if state.get("deploy_before"):
        checkout_dir = Path(state["deploy_before"]["checkout_dir"])
    else:
        checkout_dir = Path(state["artifacts_dir"]) / "horizon-checkout"

    print("  Stopping local Horizon...")
    _kill_local_horizon(state)

    if not checkout_dir.exists():
        print("  Cloning Horizon to local checkout (--no-before mode)...")
        subprocess.run(
            ["git", "clone", HORIZON_REPO, str(checkout_dir)],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "checkout", f"origin/{state['branch']}"],
            cwd=checkout_dir, check=True, capture_output=True, text=True,
        )

    if state.get("post_merge"):
        print("  Post-merge mode: review already in master, using HEAD")
        subprocess.run(
            ["git", "checkout", f"origin/{state['branch']}"],
            cwd=checkout_dir, check=True, capture_output=True, text=True,
        )
    else:
        all_reviews = state.get("dependencies", []) + [state["review_number"]]
        for rev in all_reviews:
            print(f"  Cherry-picking review {rev}...")
            patchset = state.get("patchset", 1) if rev == state["review_number"] else 1
            ref = f"refs/changes/{str(rev)[-2:]}/{rev}/{patchset}"
            subprocess.run(
                ["git", "fetch", GERRIT_FETCH, ref],
                cwd=checkout_dir, check=True, capture_output=True, text=True,
            )
            result = subprocess.run(
                ["git", "cherry-pick", "FETCH_HEAD"],
                cwd=checkout_dir, capture_output=True, text=True,
            )
            if result.returncode != 0:
                print(f"    Cherry-pick conflict for {rev}, trying merge...")
                subprocess.run(
                    ["git", "cherry-pick", "--abort"],
                    cwd=checkout_dir, capture_output=True, text=True,
                )
                subprocess.run(
                    ["git", "merge", "FETCH_HEAD", "--no-edit"],
                    cwd=checkout_dir, capture_output=True, text=True,
                )

    commit = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=checkout_dir, capture_output=True, text=True,
    )
    state["after_commit"] = commit.stdout.strip()
    print(f"    Patched commit: {state['after_commit']}")

    print("  Configuring local_settings.py (Python panel)...")
    angular_features = _get_angular_features(verify_dir, state, baseline=False)
    _write_local_settings_file(checkout_dir, angular_features=angular_features)

    print(f"  Starting Horizon locally on port {LOCAL_PORT}...")
    proc = _start_local_horizon(checkout_dir, state, "after")
    state["horizon_pid"] = proc.pid

    _wait_for_server("localhost", LOCAL_PORT)

    state["deploy_after"] = {
        "commit": state["after_commit"],
        "angular_keypairs": False,
        "url": f"http://localhost:{LOCAL_PORT}",
        "ready": True,
        "mode": "local",
    }

    return state


# ---------------------------------------------------------------------------
# Local helpers
# ---------------------------------------------------------------------------

def _start_local_horizon(checkout_dir, state, phase_label):
    """Start tox -e runserver locally, return the Popen object."""
    log_path = Path(state["artifacts_dir"]) / f"horizon-{phase_label}.log"
    log_file = open(log_path, "w")
    proc = subprocess.Popen(
        ["tox", "-e", "runserver", "--", f"0.0.0.0:{LOCAL_PORT}"],
        cwd=checkout_dir,
        stdout=log_file, stderr=subprocess.STDOUT,
    )
    state["horizon_log"] = str(log_path)
    return proc


def _kill_local_horizon(state):
    """Stop a locally-running Horizon process."""
    pid = state.get("horizon_pid")
    if not pid:
        return
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    except ProcessLookupError:
        pass
    state.pop("horizon_pid", None)


def _get_angular_features(verify_dir, state, baseline=False):
    """Read angular_features from the recipe, return as dict.

    If baseline=True, all features are set to True (AngularJS mode).
    If baseline=False, features use the recipe's desired values.
    Falls back to {'key_pairs_panel': ...} for backward compatibility.
    """
    try:
        import yaml
        recipe_yaml = Path(verify_dir) / "recipes" / state.get("recipe", "") / "recipe.yaml"
        if recipe_yaml.exists():
            with open(recipe_yaml) as f:
                recipe = yaml.safe_load(f)
            af = recipe.get("angular_features", {})
            if af:
                if baseline:
                    return {k: True for k in af}
                return af
    except Exception:
        pass
    return {"key_pairs_panel": baseline}


def _write_local_settings_file(checkout_dir, angular_features=None):
    """Write local_settings.py directly to the local checkout."""
    af_block = ""
    if angular_features:
        entries = []
        for key, val in angular_features.items():
            py_val = "True" if val else "False"
            entries.append(f"    '{key}': {py_val},")
        af_block = "ANGULAR_FEATURES = {\n" + "\n".join(entries) + "\n}\n"

    settings_path = (
        Path(checkout_dir)
        / "openstack_dashboard" / "local" / "local_settings.py"
    )
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        "import os\n"
        "from openstack_dashboard.defaults import *\n"
        "\n"
        "DEBUG = True\n"
        "ALLOWED_HOSTS = ['*']\n"
        "\n"
        "OPENSTACK_HOST = '127.0.0.1'\n"
        "OPENSTACK_KEYSTONE_URL = 'http://127.0.0.1/identity/v3'\n"
        "\n"
        "CACHES = {\n"
        "    'default': {\n"
        "        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',\n"
        "    }\n"
        "}\n"
        "\n"
        "SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'\n"
        "\n"
        f"{af_block}"
    )


def _apply_local_fixups(verify_dir, checkout_dir, state):
    """Apply branch-specific fixups to local checkout."""
    try:
        from fixup_engine import FixupEngine
        engine = FixupEngine(verify_dir / "fixups")
        fixups = engine.match(state.get("branch", "master"))
        for fixup in fixups:
            print(f"    Applying fixup: {fixup['name']}")
            for cmd in fixup.get("pre_tox", []):
                subprocess.run(cmd, shell=True, cwd=checkout_dir, check=False)
    except Exception as e:
        print(f"    [WARN] Fixup engine: {e}")


# ---------------------------------------------------------------------------
# REMOTE mode -- original SSH-based deploy (preserved for --devstack)
# ---------------------------------------------------------------------------

def _deploy_before_remote(verify_dir, state, args):
    verify_dir = Path(verify_dir)
    conn = DevStackConnection.from_state(state)

    print("  Stopping any existing Horizon instance...")
    conn.run("pkill -f 'tox.*runserver.*horizon-verify' || true", check=False)
    time.sleep(2)

    print("  Cloning Horizon master...")
    conn.run(f"rm -rf {REMOTE_DEPLOY_DIR}", check=False)
    conn.run(f"git clone {HORIZON_REPO} {REMOTE_DEPLOY_DIR}")
    conn.run(f"cd {REMOTE_DEPLOY_DIR} && git checkout origin/{state['branch']}")

    commit = conn.run(f"cd {REMOTE_DEPLOY_DIR} && git log --oneline -1")
    state["before_commit"] = commit.stdout.strip()
    print(f"    Base commit: {state['before_commit']}")

    print("  Configuring local_settings.py (AngularJS baseline)...")
    _write_remote_settings(conn, angular_keypairs=True)

    _apply_remote_fixups(verify_dir, conn, state)

    print("  Starting Horizon (baseline)...")
    conn.run(
        f"cd {REMOTE_DEPLOY_DIR} && nohup tox -e runserver -- 0.0.0.0:{REMOTE_PORT} "
        f"> /tmp/horizon-verify-before.log 2>&1 &",
        check=False,
    )

    _wait_for_server(state["devstack_host"], REMOTE_PORT)

    state["deploy_before"] = {
        "commit": state["before_commit"],
        "angular_keypairs": True,
        "url": f"http://{state['devstack_host']}:{REMOTE_PORT}",
        "ready": True,
        "mode": "remote",
    }
    state["horizon_port"] = REMOTE_PORT

    return state


def _deploy_after_remote(verify_dir, state, args):
    verify_dir = Path(verify_dir)
    conn = DevStackConnection.from_state(state)

    print("  Stopping Horizon...")
    conn.run("pkill -f 'tox.*runserver.*horizon-verify' || true", check=False)
    time.sleep(2)

    if state.get("post_merge"):
        print("  Post-merge mode: review already in master, using HEAD")
        conn.run(f"cd {REMOTE_DEPLOY_DIR} && git checkout origin/{state['branch']}")
    else:
        all_reviews = state.get("dependencies", []) + [state["review_number"]]
        for rev in all_reviews:
            print(f"  Applying review {rev}...")
            patchset = state.get("patchset", 1) if rev == state["review_number"] else 1
            ref = f"refs/changes/{str(rev)[-2:]}/{rev}/{patchset}"
            conn.run(f"cd {REMOTE_DEPLOY_DIR} && git fetch {GERRIT_FETCH} {ref}")
            result = conn.run(
                f"cd {REMOTE_DEPLOY_DIR} && git cherry-pick FETCH_HEAD",
                check=False,
            )
            if result.returncode != 0:
                print(f"    Cherry-pick conflict for {rev}, trying merge...")
                conn.run(f"cd {REMOTE_DEPLOY_DIR} && git cherry-pick --abort", check=False)
                conn.run(f"cd {REMOTE_DEPLOY_DIR} && git merge FETCH_HEAD --no-edit",
                         check=False)

    commit = conn.run(f"cd {REMOTE_DEPLOY_DIR} && git log --oneline -1")
    state["after_commit"] = commit.stdout.strip()
    print(f"    Patched commit: {state['after_commit']}")

    print("  Configuring local_settings.py (Python panel)...")
    _write_remote_settings(conn, angular_keypairs=False)

    print("  Starting Horizon (patched)...")
    conn.run(
        f"cd {REMOTE_DEPLOY_DIR} && nohup tox -e runserver -- 0.0.0.0:{REMOTE_PORT} "
        f"> /tmp/horizon-verify-after.log 2>&1 &",
        check=False,
    )

    _wait_for_server(state["devstack_host"], REMOTE_PORT)

    state["deploy_after"] = {
        "commit": state["after_commit"],
        "angular_keypairs": False,
        "url": f"http://{state['devstack_host']}:{REMOTE_PORT}",
        "ready": True,
        "mode": "remote",
    }

    return state


def _write_remote_settings(conn, angular_keypairs=False):
    """Write local_settings.py on DevStack via SSH."""
    angular_val = "True" if angular_keypairs else "False"
    settings = (
        "import os\n"
        "from openstack_dashboard.defaults import *\n"
        "\n"
        "DEBUG = True\n"
        "ALLOWED_HOSTS = ['*']\n"
        "\n"
        "OPENSTACK_HOST = '127.0.0.1'\n"
        "OPENSTACK_KEYSTONE_URL = 'http://127.0.0.1/identity/v3'\n"
        "\n"
        "CACHES = {\n"
        "    'default': {\n"
        "        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',\n"
        "    }\n"
        "}\n"
        "\n"
        "SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'\n"
        "\n"
        f"ANGULAR_FEATURES = {{\n"
        f"    'key_pairs_panel': {angular_val},\n"
        f"}}\n"
    )

    conn.run(
        f"cat > {REMOTE_DEPLOY_DIR}/openstack_dashboard/local/local_settings.py "
        f"<< 'SETTINGS_EOF'\n{settings}SETTINGS_EOF"
    )


def _apply_remote_fixups(verify_dir, conn, state):
    """Apply branch-specific fixups via SSH."""
    try:
        from fixup_engine import FixupEngine
        engine = FixupEngine(verify_dir / "fixups")
        fixups = engine.match(state.get("branch", "master"))
        for fixup in fixups:
            print(f"    Applying fixup: {fixup['name']}")
            for cmd in fixup.get("pre_tox", []):
                conn.run(f"cd {REMOTE_DEPLOY_DIR} && {cmd}", check=False)
    except Exception as e:
        print(f"    [WARN] Fixup engine: {e}")


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------

def _wait_for_server(host, port, timeout=300):
    """Poll until Horizon responds (any HTTP response = server is up)."""
    paths = ["/auth/login/", "/dashboard/auth/login/"]
    deadline = time.time() + timeout
    print(f"  Waiting for Horizon at {host}:{port}...")
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        for path in paths:
            try:
                url = f"http://{host}:{port}{path}"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    print(f"    Horizon ready at {url} after {attempt} attempts.")
                    return
            except urllib.error.HTTPError as e:
                if e.code in (301, 302, 403):
                    print(f"    Horizon ready at {url} (HTTP {e.code}) after {attempt} attempts.")
                    return
            except (urllib.error.URLError, OSError, TimeoutError):
                pass
        if attempt % 10 == 0:
            print(f"    Still waiting... (attempt {attempt})")
        time.sleep(3)
    raise RuntimeError(f"Horizon did not start within {timeout}s at {host}:{port}")
