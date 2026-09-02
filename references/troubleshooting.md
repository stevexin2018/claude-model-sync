# Troubleshooting

- **YAML cannot load:** install `claude-model-sync[yaml]` or use JSON.
- **Apply is rejected:** run `plan`, review it, then add `--yes`.
- **Old aliases remain:** this is the safe default; repeat plan/apply with explicit `--prune` only after confirmation.
- **Verify reports unexpected entries:** the manifest contains retained aliases; either include them in desired config or explicitly prune.
- **`/readyz` is 503:** set `UPSTREAM_BASE_URL` and ensure the manifest is readable.
- **`/v1/models` is 401:** send the exact local bearer token configured in `LOCAL_CLIENT_TOKEN`.
- **Unknown model alias:** compare the requested alias with the manifest and hidden/visible status.
- **Port already in use:** choose another `PORT`; do not terminate an unknown process without identifying it.
- **Rollback fails:** confirm the transaction file and its adjacent backup still exist.
