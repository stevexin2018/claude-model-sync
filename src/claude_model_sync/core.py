from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Model:
    alias: str
    target: str
    visible: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {"alias": self.alias, "target": self.target, "visible": self.visible}


def generate_alias(model_id: str, custom_rules: list[dict[str, str]] | None = None) -> str:
    """Generate a deterministic Claude-compatible alias with multimodal and rule support."""
    value = model_id.strip().lower()
    if not value:
        raise ConfigError("model id cannot be empty")
    if value.startswith("claude-"):
        return value

    if custom_rules:
        for rule in custom_rules:
            pattern = rule.get("match") or rule.get("pattern")
            replacement = rule.get("replace") or rule.get("replacement") or rule.get("alias")
            if pattern and replacement:
                if re.search(pattern, value):
                    res = re.sub(pattern, replacement, value)
                    return res if res.startswith("claude-") else f"claude-{res}"

    if value == "codex-auto-review":
        return "claude-auto-review"

    match_img = re.match(r"^gpt-image-(\d+(?:\.\d+)?)(.*)$", value)
    if match_img:
        version = match_img.group(1).replace(".", "")
        return f"claude-o-image-{version}{match_img.group(2)}"

    match = re.match(r"^gpt-(\d+(?:\.\d+)?)(.*)$", value)
    if match:
        version = match.group(1).replace(".", "")
        return f"claude-o{version}{match.group(2)}"

    match = re.match(r"^gemini-(\d+(?:\.\d+)?)(.*)$", value)
    if match:
        version = match.group(1).replace(".", "")
        return f"claude-g{version}{match.group(2)}"

    if value.startswith("gemini-"):
        return "claude-g-" + value.removeprefix("gemini-")

    safe = re.sub(r"[^a-z0-9._-]+", "-", value).strip("-")
    return "claude-" + safe


def normalize_models(items: Iterable[Any], visible: bool = True, custom_rules: list[dict[str, str]] | None = None) -> list[Model]:
    result: list[Model] = []
    for item in items:
        if isinstance(item, str):
            target, alias, item_visible = item, generate_alias(item, custom_rules), visible
        elif isinstance(item, dict):
            target = str(item.get("target") or item.get("id") or "").strip()
            if not target:
                raise ConfigError("each model needs target or id")
            alias = str(item.get("alias") or generate_alias(target, custom_rules)).strip()
            item_visible = bool(item.get("visible", visible))
        else:
            raise ConfigError("models must be strings or objects")
        if not alias.startswith("claude-"):
            raise ConfigError(f"alias must start with claude-: {alias}")
        result.append(Model(alias=alias, target=target, visible=item_visible))
    validate_models(result)
    return result


def validate_models(models: Iterable[Model]) -> None:
    aliases: dict[str, str] = {}
    targets: set[tuple[str, bool]] = set()
    for model in models:
        previous = aliases.get(model.alias)
        if previous is not None and previous != model.target:
            raise ConfigError(f"alias conflict: {model.alias} maps to both {previous} and {model.target}")
        aliases[model.alias] = model.target
        key = (model.target, model.visible)
        if key in targets:
            raise ConfigError(f"duplicate target in same visibility group: {model.target}")
        targets.add(key)


def merge_models(primary: Iterable[Model], compatibility: Iterable[Model] = ()) -> list[Model]:
    merged = list(primary) + list(compatibility)
    validate_models(merged)
    return merged


def plan_changes(current: Iterable[Model], desired: Iterable[Model], prune: bool = False) -> dict[str, Any]:
    current_map = {m.alias: m for m in current}
    desired_map = {m.alias: m for m in desired}
    added = [m.as_dict() for key, m in desired_map.items() if key not in current_map]
    updated = [m.as_dict() for key, m in desired_map.items() if key in current_map and m != current_map[key]]
    removed = [m.as_dict() for key, m in current_map.items() if key not in desired_map] if prune else []
    retained = [m for key, m in current_map.items() if key not in desired_map] if not prune else []
    effective = list(desired_map.values()) + retained
    effective.sort(key=lambda m: (not m.visible, m.alias))
    return {
        "added": added,
        "updated": updated,
        "removed": removed,
        "prune": prune,
        "changed": bool(added or updated or removed),
        "models": [m.as_dict() for m in effective],
    }


def manifest(models: Iterable[Model], source: str = "configured") -> dict[str, Any]:
    rows = [m.as_dict() for m in models]
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schemaVersion": 1,
        "source": source,
        "catalogSha256": hashlib.sha256(canonical).hexdigest(),
        "models": rows,
    }


def models_from_manifest(data: dict[str, Any]) -> list[Model]:
    return normalize_models(data.get("models", []))


def read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schemaVersion": 1, "models": []}
    return json.loads(path.read_text(encoding="utf-8"))