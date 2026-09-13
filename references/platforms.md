# Platforms and support

## Verified

- Python CLI, catalog validation, transactions, and rollback on Windows, macOS, and Linux CI.
- Node.js strict alias proxy core with zero-downtime mtime hot reloading.
- Windows registry artifact generation (`adapters/windows-registry.ps1`).
- Windows Store MSIX container registry piercing via `Invoke-CommandInDesktopPackage` (`-PiercingMSIX`).

## Experimental

- macOS managed configuration/mobileconfig and LaunchAgent integration: documented direction, not implemented.
- Linux systemd user unit: supplied as a template; paths and environment must be reviewed.

## Unsupported

- Linux Claude Desktop menu modification.
- Full Claude Code/Cowork protocol compatibility, prompt/tool/thinking transformation, or response model-name restoration.
- Automatic mutation of OpenClaw Gateway configuration.

Do not label an environment Verified until its artifact, process lifecycle, proxy directory, and real inference path have been tested there.