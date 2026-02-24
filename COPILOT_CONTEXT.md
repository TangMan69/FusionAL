# FusionAL + MCP Consulting Kit — Copilot Context File
> This file is the single source of truth for GitHub Copilot to understand the architecture,
> what was changed, why, and what to do next. Keep this updated as the project evolves.

---

## ARCHITECTURE OVERVIEW

### What This Is
FusionAL is a unified MCP gateway stack that:
- Runs a Docker-based `docker/mcp-gateway` container as the stdio transport layer for Claude Desktop
- Dynamically loads 12+ MCP server containers on demand (arxiv, context7, desktop-commander, duckduckgo, fetch, git, memory, node-code-sandbox, playwright, sequentialthinking, time, wikipedia)
- Exposes 4 custom HTTP MCP servers via `mcp-consulting-kit` (ports 8089, 8101, 8102, 8103)
- Uses a registry + catalog YAML system to control which servers load at startup

### Repo Locations
- `C:\Users\puddi\projects\FusionAL\` — gateway config, registry, catalogs, launch scripts
- `C:\Users\puddi\Projects\mcp-consulting-kit\` — 4 custom MCP servers

### Port Map
| Server | Port | Description |
|---|---|---|
| fusional (main gateway) | 8089 | Core FusionAL HTTP MCP server |
| business-intelligence-mcp | 8101 | BI tools |
| api-integration-hub | 8102 | API integration tools |
| content-automation-mcp | 8103 | Content automation tools |

---

## KEY FILES AND THEIR PURPOSE

### Claude Desktop Config
`C:\Users\puddi\AppData\Roaming\Claude\claude_desktop_config.json`
- Defines `fusional-gateway` as an mcpServer entry
- Uses full docker.exe path: `C:\Program Files\Docker\Docker\resources\bin\docker.exe`
- Mounts Windows named pipe: `//./pipe/docker_engine://./pipe/docker_engine`
- Mounts mcp config dir: `C:/Users/puddi/.docker/mcp:/mcp`
- Image: `docker/mcp-gateway`

### Gateway Registry
`C:\Users\puddi\.docker\mcp\registry.yaml`
- Controls which servers load at gateway startup
- Each entry is `servername: ref: ""`  for Docker catalog servers
- Custom HTTP servers use `ref: "http://localhost:PORT"`
- **puppeteer was removed** — it blocks startup by downloading Chrome (~2min) every run

### Gateway Catalogs
- `C:\Users\puddi\.docker\mcp\catalogs\docker-mcp.yaml` — official Docker MCP catalog (DO NOT EDIT, 15k lines)
- `C:\Users\puddi\.docker\mcp\catalogs\custom.yaml` — our custom server definitions

### Gateway Config
`C:\Users\puddi\.docker\mcp\config.yaml`
- Per-server config (paths, storage locations)
- arxiv storage: `/mcp/arxiv-papers`
- desktop-commander paths: `[]`

---

## CHANGES THAT WERE MADE TO GET THE 4 CUSTOM SERVERS RUNNING

### Problem 1: Wrong Docker Socket Mount
**Before:** `-v /var/run/docker.sock:/var/run/docker.sock` (Linux WSL2 socket — fails on Windows native Docker)
**After:** `-v //./pipe/docker_engine://./pipe/docker_engine` (Windows named pipe — correct for Docker Desktop on Windows)

### Problem 2: %USERPROFILE% Not Expanding
**Before:** `-v "%USERPROFILE%\\.docker\\mcp:/mcp"` (env var not expanded by Claude Desktop launcher)
**After:** `-v "C:/Users/puddi/.docker/mcp:/mcp"` (hardcoded absolute path)

### Problem 3: Wrong Image Name
**Before:** `fusional` (custom image that didn't exist locally)
**After:** `docker/mcp-gateway` (official Docker MCP gateway image)

### Problem 4: Malformed config.yaml
**Before:** config.yaml had `log_level: info` and `transport: stdio` as top-level keys (wrong schema)
**After:** config.yaml only contains server-specific config blocks (desktop-commander paths, arxiv storage_path)

### Problem 5: Puppeteer Blocking Init
**Problem:** puppeteer downloads Chrome (~150MB) on every cold start, exceeding Claude Desktop's 60s MCP init timeout
**Fix:** Removed `puppeteer` entry from `registry.yaml` entirely
**To re-add later:** Use a persistent Docker volume to cache Chrome: `docker volume create puppeteer-chrome-cache` and mount it

### Problem 6: docker.exe Not in PATH
**Before:** `"command": "docker"` — Claude Desktop launches with restricted PATH
**After:** `"command": "C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe"` — full absolute path

---

## CUSTOM SERVER SETUP (mcp-consulting-kit)

### Launch Script
`C:\Users\puddi\Projects\mcp-consulting-kit\launch-servers.ps1`
- Starts all 4 custom HTTP servers
- They must be running BEFORE Claude Desktop launches for the registry refs to resolve

### To Start All 4 Servers
```powershell
cd C:\Users\puddi\Projects\mcp-consulting-kit
.\launch-servers.ps1
```

### To Verify They're Running
```powershell
netstat -an | findstr "8089 8101 8102 8103"
```

---

## STARTUP SEQUENCE (REQUIRED ORDER)

1. Ensure Docker Desktop is running (check taskbar)
2. Start custom servers: `.\launch-servers.ps1`
3. Start Claude Desktop: `Start-Process "C:\Users\puddi\AppData\Local\AnthropicClaude\claude.exe"`
4. Wait ~60-90 seconds for gateway to initialize all images
5. Verify in Claude Desktop hammer icon — should show 150+ tools

---

## KNOWN ISSUES / FUTURE WORK

- [ ] Puppeteer: re-add with persistent Chrome volume cache
- [ ] Custom servers need process management (PM2 or Windows Service) so they auto-start
- [ ] arxiv-mcp-server: storage_path `/mcp/arxiv-papers` needs the directory pre-created in the bind mount
- [ ] Add health checks to launch-servers.ps1
- [ ] Consider Cloudflare Tunnel or ngrok to expose custom servers remotely for multi-user access

---

## DEVELOPMENT NOTES FOR COPILOT

- All gateway config is YAML — be careful with indentation (2 spaces, no tabs)
- The `docker-mcp.yaml` catalog is read-only reference — never edit it
- `custom.yaml` follows the same schema as `docker-mcp.yaml` for adding new servers
- Registry entries for HTTP servers: `servername: ref: "http://localhost:PORT"`
- Registry entries for Docker catalog servers: `servername: ref: ""`
- The gateway reads config on every startup — no restart needed for registry/catalog changes, only for claude_desktop_config.json changes
