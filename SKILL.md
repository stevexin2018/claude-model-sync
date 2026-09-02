---
name: claude-desktop-models
description: "Inspect, plan, apply, verify, or roll back Claude-compatible model catalogs and aliases for Claude Desktop/Cowork, Claude Code, OpenClaw, or local gateways. Use for model-list synchronization, alias generation, menu export, strict proxy setup, and drift checks."
license: MIT
---

# Claude Desktop Models

Use the bundled `claude-model-sync` CLI for deterministic catalog work. Keep credentials in the host secret store or environment; never write them into config, commands, logs, or repository files.

## Procedure

1. **Discover the deployment.** Identify the operating system, intended client, source type, existing manifest, and whether only planning or an actual change was requested. Read [references/platforms.md](references/platforms.md) before claiming platform support. Complete when the supported adapter and paths are known.
2. **Prepare configuration.** Copy `config.example.yaml` or create JSON. Select an inline/local/OpenAI-compatible source, choose the manifest output, separate visible models from hidden compatibility aliases, and reference credentials only by environment-variable name. Complete when `inspect` loads without an error.
3. **Inspect current and desired state.** Run `claude-model-sync inspect --config <path>`. Resolve invalid aliases, duplicate targets, and one-to-many alias conflicts using [references/alias-rules.md](references/alias-rules.md). Complete when current and desired catalogs are explicit.
4. **Plan safely.** Run `claude-model-sync plan --config <path>`. Add `--prune` only when the user explicitly requested removal. Show additions, updates, removals, output path, and any platform write before applying. Complete when the plan is reviewed and destructive changes are confirmed.
5. **Apply the catalog.** Run `claude-model-sync apply --config <path> --yes`, adding `--prune` only if confirmed. Preserve the emitted transaction path. Complete when the manifest is written or the CLI reports an idempotent no-op.
6. **Integrate the client.** Configure the strict alias proxy from `proxy/server.mjs`, or generate the supported platform artifact. On Windows, run `adapters/windows-registry.ps1` to create a reviewable `.reg` file; do not import it without approval. Follow [references/openclaw.md](references/openclaw.md) for OpenClaw. Complete when the proposed external write is reviewed or the client points to the proxy.
7. **Verify.** Run `claude-model-sync verify --config <path>`, check `/healthz`, `/readyz`, and authenticated `/v1/models`, then use a non-sensitive real inference probe only when authorized. Complete when catalog equality and requested runtime behavior pass.
8. **Roll back failures.** Run `claude-model-sync rollback --transaction <transaction.json>`, restore any separately managed OS configuration backup, and verify again. Complete when the prior manifest and client state are restored.

## Safety Rules

- Never infer that deleting stale models is desired; require `--prune` plus confirmation.
- Never commit endpoints, personal paths, application IDs, UUIDs, tokens, prompts, or request headers.
- Default the proxy to loopback, strict alias replacement, a path allowlist, narrow CORS, request limits, timeouts, and local client authentication.
- Treat compatibility profiles that mutate prompts, tools, thinking, metadata, or streaming as separate experimental features; the bundled proxy does not perform them.
- Back up registry, managed preferences, service definitions, and app configuration before changing them.

## References

- [Alias rules](references/alias-rules.md)
- [Platforms and support matrix](references/platforms.md)
- [OpenClaw integration](references/openclaw.md)
- [Security](references/security.md)
- [Troubleshooting](references/troubleshooting.md)
