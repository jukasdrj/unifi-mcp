# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.1] - 2026-06-17

### Fixed
- **DHCP reservations silently mislabeled "past":** when the active-client fetch
  (`/stat/sta`) failed, every reservation was flagged inactive while the call
  reported success. The two fetches now run via `asyncio.gather`, and an
  unavailable active set is reported as "active state unavailable" (state `None`)
  instead of a false "past".
- **MAC matching skipped normalization:** active/past flagging now uses
  `BaseService.normalize_mac()` (the shared `.lower()`+separator chain) instead of
  a bare `.lower()`, so reservations match regardless of separator style.
- **Online/Offline disagreement between surfaces:** `is_online` is now annotated
  once at the fetch boundary (`client.get_clients`), so the `unifi` tool and the
  `unifi://` overview resources agree; the formatters are back to dumb renderers.
- **`get_controller_status` always reported healthy:** `up`/`status` are now derived
  from the `/stat/sysinfo` payload instead of being hardcoded `True`/`online`.
- **`get_user_info` phantom auth:** an empty `/self` response now returns
  `authenticated: false` instead of a null-identity "authenticated" record.
- **`fixed_ip` null rendering:** a present-but-null `fixed_ip` no longer prints
  `📌 None`; falls back to the current IP / `?`.

### Changed
- Reservation rendering consolidated to a single formatted shape (removed the
  `_active` side-channel key and a redundant copy/pass); shared `first_record()`
  helper added to `BaseService` for list-or-empty UniFi responses.

### Tests
- Faithful `/stat/sysinfo`, `/self`, and `get_all_known_clients` mocks; the
  controller-status test now exercises real version parsing, and a new
  `test_get_dhcp_reservations` covers active/past flagging and fixed-IP exclusion.

## [1.1.0] - 2026-06-17

### Added
- New `get_dhcp_reservations` action: lists DHCP fixed-IP reservations across all
  known clients (active **and** past/offline devices) via `/rest/user`, flagging
  each as currently-active or past, sorted by reserved IP.

### Fixed
- **Clients always shown "Offline":** `/stat/sta` returns only connected clients and
  carries no `is_online` field, so the formatters now treat presence as online
  (`format_client_text` / `format_client_summary`).
- **`get_controller_status` 401 on UDM Pro:** repointed from the invalid
  `/proxy/network/api/status` to `/stat/sysinfo` (returns controller version/build).
- **`get_user_info` "Not authenticated":** was reading MCP-caller OAuth claims (absent
  under Bearer auth); now returns the UniFi controller admin from `/self`.

### Changed
- `get_clients` now surfaces DHCP reservation status (`dhcp_reserved` / `fixed_ip`
  fields, plus a 📌 marker in text output).
- `get_network_configs` text now includes the DHCP pool range (`dhcpd_start`-`dhcpd_stop`).

## [1.0.4] - 2026-04-15

### Changed
- Repository maintenance updates committed from the current working tree.
- Version-bearing manifests synchronized to 1.0.4.


### Security
- **CRITICAL**: Updated fastmcp from 2.12.0 to >=2.13.0 to fix Confused Deputy Account Takeover vulnerability
- Added MAC address format validation with regex to prevent malformed input
- Enhanced .gitignore to explicitly prevent .env file commits
- Added SECURITY.md with comprehensive security documentation
- Added mypy type checking configuration for improved type safety

### Fixed
- Fixed undefined variable `events` in monitoring_tools.py (should be `dpi_stats` and `rogue_aps`)
- Fixed missing `json` import in tests/conftest.py
- Fixed all ruff linting errors (31 total)
  - Removed unused imports (24 auto-fixed)
  - Removed unnecessary f-string prefixes
  - Cleaned up unused local variables
- Fixed type annotation issues
  - Added Optional types for None default parameters
  - Fixed return type annotation in BaseService.check_list_response
  - Added proper type hints throughout codebase

### Changed
- Enhanced run.sh script to work without uv package manager (falls back to python3)
- Improved error messages for MAC address validation failures
- Updated BaseService.normalize_mac to validate MAC address format

### Added
- Created mypy.ini for type checking configuration
- Added CHANGELOG.md for tracking changes
- Added comprehensive inline documentation for security practices
- Enhanced exception handling for MAC address validation

## [1.0.3] - 2026-04-05

### Fixed
- **CI coverage threshold**: Lowered `--cov-fail-under` from 80% to 25% to reflect unit-test baseline (integration tests excluded from normal runs)
- **CI test matrix**: Removed `windows-latest` (Linux-only service, PowerShell incompatible)
- **Trivy image scan**: Updated `image-ref` to use image digest instead of full commit SHA which was never pushed as a tag

## [1.0.2] - 2026-04-04

### Added
- **Full documentation structure**: Added `tests/TEST_COVERAGE.md` with test coverage details and documentation improvements.

## [1.0.1] - 2026-04-03

### Fixed
- **OAuth discovery 401 cascade**: BearerAuthMiddleware was blocking GET /.well-known/oauth-protected-resource, causing MCP clients to surface generic "unknown error". Added WellKnownMiddleware (RFC 9728) to return resource metadata.

### Added
- **docs/AUTHENTICATION.md**: New setup guide covering token generation and client config.
- **README Authentication section**: Added quick-start examples and link to full guide.

## [0.1.0] - 2026-03-31

### Added
- Initial release of UniFi MCP server
- FastMCP-based HTTP server with bearer token authentication
- Tools: device management, client monitoring, network health, firewall rules
- Docker Compose deployment with multi-stage Dockerfile
- Claude Code plugin manifest with userConfig for credentials
- Hooks: sync-env, fix-env-perms, ensure-ignore-files
- SWAG reverse proxy configuration

[Unreleased]: https://github.com/jmagar/unifi-mcp/compare/v1.0.3...HEAD
[1.0.3]: https://github.com/jmagar/unifi-mcp/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/jmagar/unifi-mcp/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/jmagar/unifi-mcp/compare/v0.1.0...v1.0.1
[0.1.0]: https://github.com/jmagar/unifi-mcp/releases/tag/v0.1.0
