# OpenClaw integration

Use the CLI as the deterministic execution layer and keep the OpenClaw Skill as the orchestration guide.

1. Read the chosen OpenClaw provider model catalog without copying its credential value.
2. Export a neutral catalog containing model IDs and optional explicit aliases.
3. Run `inspect` and `plan`; show the diff before any config or registry write.
4. Use OpenClaw SecretRef or the host protected environment for gateway credentials.
5. Apply the local manifest, then point the strict proxy at the upstream provider.
6. Change OpenClaw Gateway configuration only through its documented configuration interface and after approval.
7. Verify manifest equality, proxy health, `/v1/models`, and one authorized real request.

The public repository intentionally contains no personal OpenClaw paths, provider URLs, model snapshots, or SecretRefs.
