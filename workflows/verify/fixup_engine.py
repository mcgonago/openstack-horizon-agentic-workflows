"""Branch-specific fixups for Horizon deployment."""

from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


class FixupEngine:
    """Apply branch-specific workarounds before tox run."""

    def __init__(self, fixups_dir):
        self.fixups_dir = Path(fixups_dir)

    def match(self, branch):
        """Return fixups matching the given branch."""
        if not self.fixups_dir.exists() or not yaml:
            return []

        matched = []
        for fixup_file in sorted(self.fixups_dir.glob("*.yaml")):
            with open(fixup_file) as f:
                fixup = yaml.safe_load(f)
            if not fixup:
                continue

            branches = fixup.get("branches", ["*"])
            if "*" in branches or branch in branches:
                fixup["_file"] = str(fixup_file)
                matched.append(fixup)

        return matched

    def apply(self, conn, deploy_dir, branch):
        """Apply all matching fixups via SSH connection."""
        fixups = self.match(branch)
        applied = []

        for fixup in fixups:
            name = fixup.get("name", fixup.get("_file", "unknown"))

            for cmd in fixup.get("pre_tox", []):
                print(f"    fixup [{name}]: {cmd}")
                conn.run(f"cd {deploy_dir} && {cmd}", check=False)

            applied.append(name)

        return applied
