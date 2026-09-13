from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any

from .core import ConfigError, Model, merge_models, normalize_models


def load_document(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise ConfigError("YAML config requires PyYAML; use JSON or install claude-model-sync[yaml]") from exc
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ConfigError("configuration root must be an object")
    return data


def fetch_openai_models(base_url: str, token_env: str | None, timeout: float = 20) -> list[str]:
    url = base_url.rstrip("/") + "/v1/models"
    headers = {"Accept": "application/json"}
    if token_env:
        token = os.environ.get(token_env)
        if not token:
            raise ConfigError(f"required credential environment variable is not set: {token_env}")
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    return [str(row["id"]) for row in payload.get("data", []) if isinstance(row, dict) and row.get("id")]


def desired_models(config_path: Path) -> tuple[list[Model], dict[str, Any]]:
    cfg = load_document(config_path)
    source = cfg.get("source", {"type": "inline"})
    source_type = source.get("type", "inline") if isinstance(source, dict) else "inline"
    custom_rules = cfg.get("aliasRules", cfg.get("transforms"))

    if source_type == "inline":
        source_items = cfg.get("models", [])
    elif source_type == "local":
        catalog_path = Path(str(source.get("path", ""))).expanduser()
        if not catalog_path.is_absolute():
            catalog_path = config_path.parent / catalog_path
        catalog = load_document(catalog_path)
        source_items = catalog.get("models", catalog.get("data", []))
    elif source_type == "openai":
        ids = fetch_openai_models(str(source.get("baseUrl", "")), source.get("tokenEnv"))
        source_items = ids
    else:
        raise ConfigError(f"unsupported source type: {source_type}")

    visible = normalize_models(source_items, visible=True, custom_rules=custom_rules)
    compatibility = normalize_models(cfg.get("compatibilityAliases", []), visible=False, custom_rules=custom_rules)
    output_value = str(cfg.get("output", {}).get("manifest", "~/.config/claude-model-sync/models.json"))
    output = Path(output_value).expanduser()
    if not output.is_absolute():
        output = config_path.parent / output
    metadata = {"sourceType": source_type, "output": output, "config": cfg}
    return merge_models(visible, compatibility), metadata