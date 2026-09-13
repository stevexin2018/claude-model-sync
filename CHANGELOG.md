# Changelog

All notable changes to this project are documented here.

## [0.2.0] - 2026-09-14

### Added

- **Windows MSIX Container Registry Piercing**: Added `-Apply` and `-PiercingMSIX` switches to `adapters/windows-registry.ps1`, enabling automatic discovery and injection into Windows Store MSIX containerized virtual registries (`User.dat`) via `Invoke-CommandInDesktopPackage`.
- **Client Restart Automation**: Added `-RestartApp` helper in `adapters/windows-registry.ps1` to cleanly terminate tray background processes and relaunch Claude Desktop via `shell:AppsFolder`.
- **Zero-Downtime Proxy Hot Reloading**: Enhanced `proxy/server.mjs` with file modification time (`mtime`) tracking to automatically reload updated catalogs without restarting Node.js proxy processes.
- **Multimodal & Special Model Alias Derivation**: Enhanced `core.py` to deterministically derive clean aliases for OpenAI multimodal image models (`gpt-image-2.5` -> `claude-o-image-25`, `gpt-image-2.5-flare` -> `claude-o-image-25-flare`), auxiliary review models (`codex-auto-review` -> `claude-auto-review`), and Google agents (`gemini-pro-agent` -> `claude-g-pro-agent`).
- **Declarative Custom Alias Transforms**: Added support for `aliasRules` / `transforms` in configuration files for custom regex pattern replacements.

### Changed

- Bumped package version to 0.2.0 across pyproject.toml, package metadata, and skill manifests.

## [0.1.0] - 2026-09-03

### Added

- Portable Agent Skill and bilingual documentation.
- Dynamic inline, local, and OpenAI-compatible model sources.
- Alias generation, conflict checks, visible/hidden aliases, explicit pruning, JSON output, atomic apply, transactions, verification, and rollback.
- Strict local alias proxy with authentication option, allowlisted routes, limits, health checks, cancellation, and structured logs.
- Windows registry artifact generator and Linux user-service template.
- Cross-platform tests and Gitleaks workflow.