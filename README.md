# Claude Model Sync

A deterministic, portable Claude-compatible model catalog synchronization CLI and strict alias proxy for Claude Desktop/Cowork, Claude Code, OpenClaw, and local gateways.

## Features

- Dynamic catalog ingest from inline/local JSON/YAML or OpenAI-compatible `/v1/models`.
- Deterministic Claude alias generation with support for multimodal image models, code review agents, and declarative `aliasRules` / `transforms`.
- Clear separation between visible menu models and hidden compatibility aliases.
- Deterministic change planning: `inspect`, `plan`, `apply`, `verify`, `rollback`.
- Safe defaults: no silent model deletion unless `--prune` is explicitly supplied.
- Atomic file writes, manifest backup snapshots, transaction logs, and idempotent rollback.
- Strict loopback alias proxy with zero-downtime hot reloading (`mtime` tracking), authentication, path allowlists, body limits, timeouts, narrow CORS, and structured logging.
- Windows Store MSIX container registry piercing (`adapters/windows-registry.ps1 -PiercingMSIX`) and clean app restart orchestration.
- OpenClaw Agent Skill layout, portable Linux user unit templates, and cross-platform CI.

## Quickstart

```bash
python -m pip install -e .
claude-model-sync inspect --config examples/config.json
claude-model-sync plan --config examples/config.json
claude-model-sync apply --config examples/config.json --yes
claude-model-sync verify --config examples/config.json
```

Automations can consume machine-readable JSON:

```bash
claude-model-sync --json plan --config examples/config.json
```

Model removal requires explicit authorization:

```bash
claude-model-sync plan --config config.json --prune
claude-model-sync apply --config config.json --prune --yes
```

## Windows Integration & MSIX Piercing

```powershell
# Generate reviewable .reg file only
./adapters/windows-registry.ps1 -Manifest ./generated/models.json -Output ./generated/claude-models.reg

# Apply to host registry and pierce Windows Store MSIX container sandbox
./adapters/windows-registry.ps1 -Manifest ./generated/models.json -Apply -PiercingMSIX

# Apply and orchestrate clean Claude Desktop restart
./adapters/windows-registry.ps1 -Manifest ./generated/models.json -Apply -PiercingMSIX -RestartApp
```

## Testing

```bash
python -m unittest discover -s tests -p "test_*.py"
python -m compileall -q src tests
node --check proxy/server.mjs
node tests/test_proxy.mjs
```

License is MIT.