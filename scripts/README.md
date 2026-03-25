Scripts
-------

1) `generate_registry_from_docker.ps1` (PowerShell)

- Generates `core/mcp_registry.json` from running Docker containers.
- Usage examples:

```powershell
# include all running containers
.\scripts\generate_registry_from_docker.ps1

# include only containers with Docker label mcp=true
.\scripts\generate_registry_from_docker.ps1 -Label "mcp=true"

# include only containers whose image matches a regex
.\scripts\generate_registry_from_docker.ps1 -ImageRegex "^my-mcp-.*$"
```

2) `generate_registry_from_docker.sh` (macOS / Linux / WSL)

- Same functionality as the PowerShell script. Example usage:

```bash
# all running containers
./scripts/generate_registry_from_docker.sh

# label-filtered
./scripts/generate_registry_from_docker.sh --label mcp=true

# image regex
./scripts/generate_registry_from_docker.sh --image-regex '^my-mcp-.*$'
```

Notes:
- Both scripts back up the existing `core/mcp_registry.json` to `core/mcp_registry.json.bak`.
- They create registry entries with URLs of the form `docker://<container_name>`.
- You can then edit `core/mcp_registry.json` to add tool metadata or more descriptive text.

3) `smoke-generate-endpoint.ps1` (PowerShell)

- Smoke-tests the FusionAL `POST /generate` endpoint end-to-end.
- Calls `/generate`, extracts the returned port, then verifies the generated server responds on `/health`.
- Uses `-ApiKey` if provided, otherwise falls back to `API_KEY` or `FUSIONAL_API_KEY` env vars.

```powershell
# basic run (requires FusionAL core running locally)
.\scripts\smoke-generate-endpoint.ps1

# custom prompt
.\scripts\smoke-generate-endpoint.ps1 -Prompt "Create an MCP server that converts markdown to HTML"

# custom API endpoint + key
.\scripts\smoke-generate-endpoint.ps1 -BaseUrl "http://localhost:8009" -ApiKey "your-api-key"
```
