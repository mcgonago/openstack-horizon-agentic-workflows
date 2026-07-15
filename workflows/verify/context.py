"""Phase 1: Fetch review from Gerrit, match recipe."""

import json
import re
import urllib.request
from pathlib import Path


GERRIT_API = "https://review.opendev.org"


def resolve_context(verify_dir, state, args):
    """Fetch review metadata and match recipe."""
    review = state["review_number"]
    verify_dir = Path(verify_dir)

    url = f"{GERRIT_API}/changes/{review}/detail?o=CURRENT_REVISION&o=CURRENT_FILES"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        if raw.startswith(")]}'"):
            raw = raw[4:]
        data = json.loads(raw)

    state["title"] = data.get("subject", "")
    state["branch"] = data.get("branch", "master")
    state["status"] = data.get("status", "UNKNOWN")
    state["topic"] = data.get("topic", "")
    state["owner"] = data.get("owner", {}).get("name", "")
    state["project"] = data.get("project", "")

    current_rev_id = data.get("current_revision", "")
    revisions = data.get("revisions", {})
    if current_rev_id and current_rev_id in revisions:
        rev = revisions[current_rev_id]
        state["patchset"] = rev.get("_number", 1)
        state["ref"] = rev.get("ref", "")
        state["files_changed"] = list(rev.get("files", {}).keys())
    else:
        state["patchset"] = 1
        state["ref"] = f"refs/changes/{str(review)[-2:]}/{review}/1"
        state["files_changed"] = []

    commit_msg = ""
    if current_rev_id and current_rev_id in revisions:
        commit_msg = revisions[current_rev_id].get("commit", {}).get("message", "")
    state["commit_message"] = commit_msg
    state["dependencies"] = _parse_depends_on(commit_msg)

    if state["status"] == "MERGED":
        state["post_merge"] = True

    recipe_override = state.get("recipe_override", "")
    if recipe_override:
        state["recipe"] = recipe_override
    else:
        state["recipe"] = _match_recipe(verify_dir, state["files_changed"])
    state["recipe_groups"] = _get_recipe_groups(verify_dir, state["recipe"])

    print(f"  Review: {review} — {state['title']}")
    print(f"  Status: {state['status']}, Patchset: {state['patchset']}")
    print(f"  Branch: {state['branch']}")
    print(f"  Files changed: {len(state['files_changed'])}")
    for f in state['files_changed'][:10]:
        print(f"    - {f}")
    print(f"  Dependencies: {state['dependencies']}")
    print(f"  Recipe: {state['recipe']}")
    print(f"  Groups: {state['recipe_groups']}")

    return state


def _parse_depends_on(commit_msg):
    """Extract Depends-On review numbers from commit message."""
    depends = []
    for line in commit_msg.splitlines():
        match = re.match(
            r"Depends-On:\s*https?://review\.opendev\.org/c/\S+/\+/(\d+)",
            line,
        )
        if match:
            depends.append(int(match.group(1)))
    return depends


def _match_recipe(verify_dir, files_changed):
    """Match recipe based on files changed."""
    try:
        import yaml
    except ImportError:
        return "generic"

    recipes_dir = verify_dir / "recipes"
    if not recipes_dir.exists():
        return "generic"

    for recipe_dir in sorted(recipes_dir.iterdir()):
        if not recipe_dir.is_dir() or recipe_dir.name == "helpers":
            continue
        recipe_yaml = recipe_dir / "recipe.yaml"
        if not recipe_yaml.exists():
            continue
        with open(recipe_yaml) as f:
            recipe = yaml.safe_load(f)
        match_files = recipe.get("match_files", [])
        for pattern in match_files:
            for changed_file in files_changed:
                if changed_file.startswith(pattern) or pattern in changed_file:
                    return recipe_dir.name
    return "generic"


def _get_recipe_groups(verify_dir, recipe_name):
    """Get list of test groups for a recipe."""
    try:
        import yaml
    except ImportError:
        return []

    recipe_yaml = verify_dir / "recipes" / recipe_name / "recipe.yaml"
    if not recipe_yaml.exists():
        return []
    with open(recipe_yaml) as f:
        recipe = yaml.safe_load(f)
    return [g["name"] for g in recipe.get("groups", [])]
