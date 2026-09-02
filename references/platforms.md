# Platforms and support

## Verified

- Python CLI, catalog validation, transactions, and rollback on Windows, macOS, and Linux CI.
- Node.js strict alias proxy core on Linux CI; it uses platform-neutral Node APIs.
- Windows registry artifact generation is deterministic and performs no import.

## Experimental

- Windows registry import, Claude application discovery, and restart orchestration: environment-specific and intentionally not automated in v0.1.0.
- macOS managed configuration/mobileconfig and LaunchAgent integration: documented direction, not implemented.
- Linux systemd user unit: supplied as a template; paths and environment must be reviewed.

## Unsupported

- Linux Claude Desktop menu modification.
- Full Claude Code/Cowork protocol compatibility, prompt/tool/thinking transformation, or response model-name restoration.
- Automatic mutation of OpenClaw Gateway configuration.

Do not label an environment Verified until its artifact, process lifecycle, proxy directory, and real inference path have been tested there.
