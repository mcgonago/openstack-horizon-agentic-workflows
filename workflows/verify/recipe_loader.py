"""Dynamic recipe loading for /verify skill."""

import importlib.util
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def load_recipe(verify_dir, recipe_name):
    """Load recipe config and modules."""
    verify_dir = Path(verify_dir)
    recipe_dir = verify_dir / "recipes" / recipe_name

    if not recipe_dir.exists():
        raise FileNotFoundError(f"Recipe not found: {recipe_name}")

    recipe_yaml = recipe_dir / "recipe.yaml"
    if not recipe_yaml.exists():
        raise FileNotFoundError(f"No recipe.yaml in {recipe_dir}")

    if not yaml:
        raise RuntimeError("pyyaml not installed")

    with open(recipe_yaml) as f:
        config = yaml.safe_load(f)

    config["_dir"] = str(recipe_dir)
    config["_name"] = recipe_name

    return config


def load_group_module(recipe_dir, group_name, module_name=None):
    """Dynamically import a test group module."""
    recipe_dir = Path(recipe_dir)

    name_map = {
        "A": "panel_loading",
        "B": "table_features",
        "C": "create_form",
        "D": "import_form",
        "E": "delete",
        "F": "detail_view",
        "G": "chevron_rows",
    }

    if not module_name:
        module_name = name_map.get(group_name, group_name.lower())

    module_path = recipe_dir / f"{module_name}.py"
    if not module_path.exists():
        return None

    spec = importlib.util.spec_from_file_location(
        f"recipe_group_{group_name}", module_path
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def list_recipes(verify_dir):
    """List available recipes."""
    verify_dir = Path(verify_dir)
    recipes_dir = verify_dir / "recipes"
    if not recipes_dir.exists():
        return []

    result = []
    for d in sorted(recipes_dir.iterdir()):
        if d.is_dir() and d.name != "helpers" and (d / "recipe.yaml").exists():
            result.append(d.name)
    return result
