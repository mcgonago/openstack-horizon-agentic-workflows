"""Phase 2: SSH to DevStack, preflight checks, resource setup."""

import os
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


class DevStackConnection:
    """SSH connection to DevStack instance (plain SSH or virtctl)."""

    def __init__(self, host="", user="stack", key_path=None,
                 mode="ssh", vm="", namespace="", identity_file=""):
        self.host = host
        self.user = user
        self.key_path = key_path
        self.mode = mode

        if mode == "virtctl":
            self._ssh_base = [
                "virtctl", "ssh",
                f"{user}@vm/{vm}",
                "-n", namespace,
                "--identity-file", identity_file,
                "-c",
            ]
        else:
            self._ssh_base = [
                "ssh", "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=10",
            ]
            if key_path:
                self._ssh_base.extend(["-i", key_path])
            self._ssh_base.append(f"{user}@{host}")

    @classmethod
    def from_state(cls, state):
        """Build a connection from saved state config."""
        cfg = state.get("devstack_connection", {})
        if cfg.get("mode") == "virtctl":
            return cls(
                mode="virtctl",
                user=cfg.get("user", "ubuntu"),
                vm=cfg.get("vm", ""),
                namespace=cfg.get("namespace", ""),
                identity_file=cfg.get("identity_file", ""),
            )
        return cls(host=cfg.get("host", state.get("devstack_host", "")),
                   user=cfg.get("user", "stack"))

    def run(self, cmd, timeout=120, check=True):
        """Execute command on DevStack via SSH."""
        full_cmd = self._ssh_base + [cmd]
        result = subprocess.run(
            full_cmd, capture_output=True, text=True, timeout=timeout
        )
        if check and result.returncode != 0:
            raise RuntimeError(
                f"SSH command failed (rc={result.returncode}): {cmd}\n"
                f"stderr: {result.stderr[:500]}"
            )
        return result

    def test_connection(self):
        """Verify SSH connectivity."""
        try:
            result = self.run("echo ok", timeout=15, check=False)
            return result.stdout.strip() == "ok"
        except (subprocess.TimeoutExpired, Exception):
            return False


def setup_environment(verify_dir, state, args):
    """Connect to DevStack, run preflight, create resources."""
    verify_dir = Path(verify_dir)

    if not yaml:
        raise RuntimeError("pyyaml not installed: pip install pyyaml")

    recipe_yaml = verify_dir / "recipes" / state["recipe"] / "recipe.yaml"
    with open(recipe_yaml) as f:
        recipe = yaml.safe_load(f)

    env_config = recipe.get("environment", {})
    virtctl_config = env_config.get("virtctl", {})

    use_virtctl = getattr(args, "virtctl", False) or virtctl_config.get("enabled", False)

    if use_virtctl:
        vm = getattr(args, "vm", "") or virtctl_config.get("vm", "horizon-devstack")
        namespace = getattr(args, "namespace", "") or virtctl_config.get("namespace", "rhos-dfg-ui--runtime-int")
        identity_file = getattr(args, "identity_file", "") or virtctl_config.get("identity_file", "~/.ssh/id_ed25519")
        ssh_user = getattr(args, "ssh_user", "") or virtctl_config.get("ssh_user", "ubuntu")
        identity_file = os.path.expanduser(identity_file)
        host = "localhost"

        conn = DevStackConnection(
            mode="virtctl", user=ssh_user, vm=vm,
            namespace=namespace, identity_file=identity_file,
        )
    else:
        host = args.devstack or env_config.get("devstack_host", "")

        if host.startswith("${"):
            env_var = host[2:-1]
            host = os.environ.get(env_var, "")
        if not host:
            raise ValueError(
                "No DevStack host configured.\n"
                "Use: --devstack <HOST>  (plain SSH)\n"
                "Or:  --virtctl          (virtctl SSH to ITUp VM)\n"
                "Or set DEVSTACK_HOST environment variable\n"
                "Or configure devstack_host in recipe.yaml"
            )

        conn = DevStackConnection(host)

    password = env_config.get("admin_password", "")
    if password.startswith("${"):
        env_var = password[2:-1]
        password = os.environ.get(env_var, "secret")

    if use_virtctl:
        print("  Checking Keystone port-forward (localhost:80)...")
        try:
            req = urllib.request.Request("http://localhost:80/identity/v3/")
            urllib.request.urlopen(req, timeout=5)
            print("    Keystone port-forward OK")
        except (urllib.error.URLError, OSError):
            raise RuntimeError(
                "Keystone not reachable at localhost:80.\n"
                "Required:\n"
                "  virtctl port-forward vm/horizon-devstack 5080:80 "
                "-n rhos-dfg-ui--runtime-int\n"
                "  sudo iptables -t nat -A OUTPUT -o lo -p tcp --dport 80 "
                "-j REDIRECT --to-port 5080"
            )

    print("  Checking SSH connectivity...")
    if not conn.test_connection():
        label = f"virtctl vm/{vm} -n {namespace}" if use_virtctl else host
        raise RuntimeError(f"Cannot SSH to {label}")
    print("    SSH OK")

    if not use_virtctl:
        print("  Checking disk space...")
        disk = conn.run("df -h /opt/stack 2>/dev/null | tail -1 | awk '{print $4}'", check=False)
        avail = disk.stdout.strip() if disk.returncode == 0 else "unknown"
        print(f"    Available: {avail}")

    print("  Checking OpenStack CLI...")
    os_ver = conn.run("openstack --version 2>&1 || true", check=False)
    ver_text = os_ver.stdout.strip() or os_ver.stderr.strip()
    print(f"    {ver_text[:80]}")

    print("  Checking Keystone...")
    token = conn.run(
        "openstack token issue -f value -c id 2>/dev/null | head -c 20",
        check=False,
    )
    if token.returncode != 0:
        print("    [WARN] Keystone check failed — may need to source openrc")
    else:
        print("    Keystone OK")

    print("  Creating test resources...")
    setup_cmds = recipe.get("setup", [])
    created_resources = []
    for cmd in setup_cmds:
        print(f"    $ {cmd}")
        result = conn.run(cmd, check=False)
        if result.returncode == 0:
            created_resources.append(cmd)
            print("      OK")
        else:
            err = result.stderr.strip()[:100]
            print(f"      WARN: {err}")

    state["devstack_host"] = host
    state["admin_user"] = env_config.get("admin_user", "admin")
    state["admin_password"] = password

    if use_virtctl:
        state["deploy_mode"] = "local"
        state["horizon_port"] = 9000
        state["horizon_url"] = "http://localhost:9000"
        state["devstack_connection"] = {
            "mode": "virtctl",
            "user": ssh_user,
            "vm": vm,
            "namespace": namespace,
            "identity_file": identity_file,
        }
    else:
        state["deploy_mode"] = "remote"
        state["horizon_port"] = int(env_config.get("horizon_port", 8080))
        state["horizon_url"] = f"http://{host}:{state['horizon_port']}"
        state["devstack_connection"] = {"mode": "ssh", "host": host, "user": "stack"}
    state["test_resources"] = created_resources

    count_result = conn.run(
        "openstack keypair list -f json 2>/dev/null | python3 -c "
        "'import sys,json; print(len(json.load(sys.stdin)))'",
        check=False,
    )
    if count_result.returncode == 0:
        state["initial_keypair_count"] = int(count_result.stdout.strip())
    else:
        state["initial_keypair_count"] = 0

    print(f"  Environment ready: {host}")
    return state


def cleanup_resources(state, args):
    """Delete test resources from DevStack."""
    if not state.get("devstack_connection"):
        print("No DevStack connection in state; nothing to clean up.")
        return

    conn = DevStackConnection.from_state(state)

    if yaml:
        verify_dir = Path(state.get("verify_dir", ""))
        recipe_name = state.get("recipe", "")
        recipe_yaml = verify_dir / "recipes" / recipe_name / "recipe.yaml"
        if recipe_yaml.exists():
            with open(recipe_yaml) as f:
                recipe = yaml.safe_load(f)
            for cmd in recipe.get("cleanup", []):
                print(f"  $ {cmd}")
                conn.run(cmd, check=False)

    for name in ["verify-create-ssh", "verify-create-x509",
                 "verify-import-ssh", "verify-import-x509"]:
        conn.run(f"openstack keypair delete {name} 2>/dev/null || true", check=False)

    print("  Cleanup complete.")
