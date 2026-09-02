from __future__ import annotations

import json
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .core import Model, manifest, models_from_manifest, plan_changes, read_json_if_exists


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def make_plan(output: Path, desired: list[Model], prune: bool) -> dict[str, Any]:
    current_doc = read_json_if_exists(output)
    return plan_changes(models_from_manifest(current_doc), desired, prune=prune)


def apply_plan(output: Path, plan: dict[str, Any], source: str) -> dict[str, Any]:
    if not plan["changed"]:
        return {"changed": False, "output": str(output), "transaction": None}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tx_id = f"{stamp}-{uuid.uuid4().hex[:8]}"
    tx_dir = output.parent / "transactions" / tx_id
    tx_dir.mkdir(parents=True, exist_ok=False)
    backup = None
    if output.exists():
        backup = tx_dir / "before.json"
        shutil.copy2(output, backup)
    rows = [Model(alias=m["alias"], target=m["target"], visible=bool(m["visible"])) for m in plan["models"]]
    document = manifest(rows, source=source)
    atomic_write_json(output, document)
    record = {
        "schemaVersion": 1,
        "createdAt": stamp,
        "output": str(output),
        "backup": str(backup) if backup else None,
        "beforeExisted": backup is not None,
        "afterSha256": document["catalogSha256"],
        "plan": {key: plan[key] for key in ("added", "updated", "removed", "prune")},
    }
    atomic_write_json(tx_dir / "transaction.json", record)
    return {"changed": True, "output": str(output), "transaction": str(tx_dir / "transaction.json")}


def rollback(transaction_path: Path) -> dict[str, Any]:
    record = json.loads(transaction_path.read_text(encoding="utf-8"))
    output = Path(record["output"])
    backup = record.get("backup")
    if backup:
        shutil.copy2(Path(backup), output)
    elif record.get("beforeExisted") is False:
        output.unlink(missing_ok=True)
    else:
        raise ValueError("transaction has no restorable state")
    return {"rolledBack": True, "output": str(output), "transaction": str(transaction_path)}
