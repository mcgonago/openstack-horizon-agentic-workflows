"""JSON state persistence for verify pipeline resumability."""

import json
from pathlib import Path
from datetime import datetime, timezone


def load_state(artifacts_dir: Path) -> dict:
    state_file = artifacts_dir / "verify_state.json"
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return {"created_at": datetime.now(timezone.utc).isoformat()}


def save_state(state: dict, artifacts_dir: Path):
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    state_file = artifacts_dir / "verify_state.json"
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2, default=str)
