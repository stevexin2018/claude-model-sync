from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .config import desired_models
from .core import ConfigError, models_from_manifest, read_json_if_exists
from .state import apply_plan, make_plan, rollback


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="claude-model-sync")
    root.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("inspect", "plan", "apply", "verify"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--config", type=Path, required=True)
        if name in ("plan", "apply"):
            cmd.add_argument("--prune", action="store_true", help="explicitly remove aliases absent from source")
        if name == "apply":
            cmd.add_argument("--yes", action="store_true", help="confirm writing the planned manifest")
    undo = commands.add_parser("rollback")
    undo.add_argument("--transaction", type=Path, required=True)
    return root


def emit(data: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, sort_keys=True))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if args.command == "rollback":
        return 0, rollback(args.transaction)
    desired, metadata = desired_models(args.config)
    output: Path = metadata["output"]
    if args.command == "inspect":
        current = models_from_manifest(read_json_if_exists(output))
        return 0, {"sourceType": metadata["sourceType"], "output": str(output), "desired": [m.as_dict() for m in desired], "current": [m.as_dict() for m in current]}
    plan = make_plan(output, desired, prune=getattr(args, "prune", False))
    if args.command == "plan":
        return 0, plan
    if args.command == "apply":
        if not args.yes:
            raise ConfigError("apply requires --yes; run plan first")
        return 0, apply_plan(output, plan, source=metadata["sourceType"])
    current = models_from_manifest(read_json_if_exists(output))
    expected = {(m.alias, m.target, m.visible) for m in desired}
    actual = {(m.alias, m.target, m.visible) for m in current}
    ok = expected == actual
    return (0 if ok else 2), {"ok": ok, "output": str(output), "missing": sorted(expected - actual), "unexpected": sorted(actual - expected)}


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        code, data = run(args)
        emit(data, args.json)
        return code
    except (ConfigError, OSError, ValueError, json.JSONDecodeError) as exc:
        emit({"error": str(exc), "type": type(exc).__name__}, args.json)
        return 1
