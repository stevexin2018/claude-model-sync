# Claude Model Sync

[![Test](https://github.com/stevexin2018/claude-model-sync/actions/workflows/test.yml/badge.svg)](https://github.com/stevexin2018/claude-model-sync/actions/workflows/test.yml)
[![Secret scan](https://github.com/stevexin2018/claude-model-sync/actions/workflows/secret-scan.yml/badge.svg)](https://github.com/stevexin2018/claude-model-sync/actions/workflows/secret-scan.yml)

Portable model catalog synchronization and strict Claude-compatible aliasing for Claude Desktop/Cowork, Claude Code, OpenClaw, and local gateways.

This initial release extracts the deterministic, reusable core from a proven Windows workflow without publishing machine-specific configuration or credentials. It does **not** claim full Claude protocol emulation.

中文说明：[README.zh-CN.md](README.zh-CN.md)

## Features

- Dynamic catalogs from inline/local JSON or YAML and OpenAI-compatible `/v1/models` endpoints.
- Deterministic `claude-*` aliases with conflict and duplicate validation.
- Separate visible menu models and hidden compatibility aliases.
- `inspect`, `plan`, `apply`, `verify`, and `rollback` commands.
- Safe default: stale aliases are retained unless `--prune` is explicitly supplied.
- Atomic manifest writes, backups, transaction records, idempotent apply, and rollback.
- Strict Node.js alias proxy: loopback binding, optional local client token, endpoint allowlist, body/timeout limits, narrow CORS, cancellation, health endpoints, and structured logs.
- Reviewable Windows `.reg` generation, experimental Linux user-service template, and platform guidance.
- OpenClaw Agent Skill, tests on Windows/macOS/Linux, and Gitleaks CI.

## Support matrix

| Capability | Windows | macOS | Linux |
|---|---|---|---|
| CLI and manifest | Verified in CI | Verified in CI | Verified in CI |
| Strict alias proxy | CI-tested core | CI-tested core | CI-tested core |
| Claude menu artifact | `.reg` generator | Planned/experimental | Unsupported |
| Service integration | Manual | Planned/experimental | systemd user template |

See [references/platforms.md](references/platforms.md) for the exact boundary.

## Quick start

```bash
python -m pip install -e .
claude-model-sync inspect --config examples/config.json
claude-model-sync plan --config examples/config.json
claude-model-sync apply --config examples/config.json --yes
claude-model-sync verify --config examples/config.json
```

JSON output is stable for automation:

```bash
claude-model-sync --json plan --config examples/config.json
```

Removal is never implicit:

```bash
claude-model-sync plan --config config.json --prune
claude-model-sync apply --config config.json --prune --yes
```

## Configuration

JSON works with the Python standard library. YAML requires `PyYAML`:

```bash
python -m pip install -e ".[yaml]"
```

Source examples:

```json
{"source":{"type":"local","path":"catalog.json"}}
```

```yaml
source:
  type: openai
  baseUrl: https://gateway.example.invalid
  tokenEnv: MODEL_GATEWAY_TOKEN
```

The credential value is read at runtime from the named environment variable. Do not put it in the file.

## Strict alias proxy

The proxy only maps `body.model`, lists visible aliases, and forwards `/v1/messages`. It does not rewrite prompts, tools, thinking, metadata, or responses.

Required environment:

- `CLAUDE_MODEL_SYNC_MANIFEST`
- `UPSTREAM_BASE_URL`

Recommended:

- `LOCAL_CLIENT_TOKEN`
- `UPSTREAM_API_KEY` supplied through a protected service environment
- `ALLOWED_ORIGIN` only when browser access is required

```bash
node proxy/server.mjs
```

Health endpoints are `/healthz` and `/readyz`. Unknown paths are rejected.

## Windows menu export

Generate a reviewable registry file; the script does not import it:

```powershell
./adapters/windows-registry.ps1 -Manifest ./generated/models.json -Output ./generated/claude-models.reg
```

Back up `HKCU\Software\Policies\Claude` before importing any registry change.

## Development

```bash
python -m unittest discover -s tests -p "test_*.py"
python -m compileall -q src tests
node --check proxy/server.mjs
node tests/test_proxy.mjs
```

## Security

Read [SECURITY.md](SECURITY.md) and [references/security.md](references/security.md). CI scans repository history with Gitleaks. Never use a personal production gateway in tests.

## License

MIT
