# AGENTS.md — unifi-mcp

Modular UniFi MCP server using FastMCP with streamable HTTP transport.

## 🚨 Critical Implementation Details

### 1. Controller Type Detection
The `UNIFI_IS_UDM_PRO=true` flag significantly changes API interaction:
*   **API Base Path**: `/proxy/network/api` (UDM Pro) vs `/api` (Legacy)
*   **Login Endpoint**: `/api/auth/login` (UDM Pro) vs `/api/login` (Legacy)
*   **Cookie Name**: `TOKEN` (UDM Pro) vs `unifises` (Legacy)

### 2. Authentication & API Flow
*   **Mandatory Check**: Always call `await ensure_authenticated()` before any API operation.
*   **MAC Normalization**: MAC addresses must be normalized as: `mac.lower().replace("-", ":").replace(".", ":")`.
*   **Site Parameters**: 
    *   Use `site_name=""` ONLY for the `/self/sites` endpoint.
    *   Use `site_name="default"` for all other site-specific operations.

### 3. MCP-Specific Patterns
*   **Tool Design**: Expose a single unified `unifi` tool with an `action` parameter and a separate `unifi_help` tool. Do not create dozens of top-level tools.
*   **Resources**: Use `@mcp.resource("unifi://path")` and return data objects, never raw JSON strings.
*   **Data Formatting**: All bandwidth/storage values must be passed through `format_data_values()` for human-readability (KB, MB, GB), while preserving raw values in `*_raw` fields.
*   **Error Handling**: Return error objects `{"error": "message"}` instead of raising exceptions.

## Development & Operations

### Essential Commands
| Command | Purpose |
|---|---|
| `uv sync` | Install dependencies |
| `./run.sh` | Start server in background + stream logs |
| `./run.sh logs` | Stream logs from existing process |
| `uv run pytest` | Run test suite |
| `uv run ruff check .` | Lint code |
| `uv run mypy .` | Type check |
| `kill $(cat logs/unifi-mcp.pid)` | Stop the server |

### Versioning Policy
**Every feature branch push MUST bump the version in ALL version-bearing files simultaneously.**
*   **Major**: `feat!:` or `BREAKING CHANGE`
*   **Minor**: `feat` or `feat(...)`
*   **Patch**: `fix`, `chore`, `refactor`, `test`, `docs`
*   **Files to Update**: `pyproject.toml`, `.claude-plugin/plugin.json`, `uv.lock` (via `uv lock`), and `CHANGELOG.md`.

## Configuration
Required environment variables:
*   `UNIFI_URL`: Full URL with port (e.g., `https://192.168.1.x:443`).
*   `UNIFI_USERNAME` / `UNIFI_PASSWORD`: Local admin credentials.
*   `UNIFI_MCP_TOKEN`: Bearer token for HTTP auth (unless `UNIFI_MCP_NO_AUTH=true`).
