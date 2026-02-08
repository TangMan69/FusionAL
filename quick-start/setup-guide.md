# ⚡ FusionAL Quick Start - 5 Minutes

Get your first MCP server running in under 5 minutes!

## 📋 Prerequisites (30 seconds)

- ✅ **Docker Desktop** installed and running
- ✅ **Claude Desktop** installed
- ✅ **Git** and **Python 3.11+** installed
- ✅ Terminal open

## Step 1: Setup FusionAL (1 minute)

```bash
# Clone repository
git clone https://github.com/TangMan69/FusionAL.git
cd FusionAL

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  (Windows)

# Install FusionAL
pip install -r core/requirements.txt
```

## Step 2: Start the Server (1 minute)

```bash
cd core
python -m uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Step 3: Build Example Server (1 minute)

In a **new terminal**:

```bash
cd FusionAL/examples/dice-roller
docker build -t dice-mcp-server .
```

## Step 4: Configure Claude Desktop (1 minute)

Edit your Claude config file:

**macOS/Linux:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
# or
nano ~/.config/Claude/claude_desktop_config.json
```

**Windows (PowerShell):**
```powershell
notepad "$env:APPDATA\Claude\claude_desktop_config.json"
```

Add this JSON (replace `YOUR_USERNAME`):

```json
{
  "mcpServers": {
    "mcp-toolkit-gateway": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", "/Users/YOUR_USERNAME/.docker/mcp:/mcp",
        "docker/mcp-gateway",
        "--catalog=/mcp/catalogs/docker-mcp.yaml",
        "--catalog=/mcp/catalogs/custom.yaml",
        "--config=/mcp/config.yaml",
        "--registry=/mcp/registry.yaml",
        "--transport=stdio"
      ]
    }
  }
}
```

**For Windows**, use double backslashes:
```json
"-v", "C:\\Users\\YOUR_USERNAME\\.docker\\mcp:/mcp",
```

## Step 5: Test! (30 seconds)

1. **Quit Claude Desktop** completely
2. **Reopen Claude Desktop**
3. **Open a new chat**
4. **Try this:** _"Roll 2d6+5 for damage"_

You should see dice rolling results!

---

## 🎉 Success!

You now have a working MCP server platform with:
- ✅ FastAPI execution engine
- ✅ Python code sandbox (Docker)
- ✅ Dice roller example server
- ✅ MCP gateway integration

---

## 🚀 What's Next?

### Generate Your Own Server

```bash
cd FusionAL/core

python -c "
from ai_agent import generate_mcp_project

# Generate a complete server from description
result = generate_mcp_project(
    prompt='Build a weather server that gets current conditions and forecast',
    provider='claude',
    out_dir='../my-weather-server',
    build=True
)

print('Generated:', result['files'])
print('Built image:', result['build_result']['image_tag'])
"
```

### Register New Server

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "dice-roller",
    "description": "D&D Dice Rolling",
    "url": "stdio",
    "metadata": {"tools": ["roll_dice", "roll_stats"]}
  }'
```

### Test Code Execution

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello from FusionAL!\")\nprint(2 + 2)",
    "use_docker": true
  }'
```

---

## 🔧 Troubleshooting

### "Docker daemon not running"
- Launch Docker Desktop
- Check: `docker ps`

### "Tools not appearing in Claude"
- Verify Docker image built: `docker images | grep dice`
- Check Claude logs: Help → Show Logs
- Restart Claude Desktop completely

### "Connection refused"
- Verify FusionAL server running: `curl http://localhost:8000/health`
- Check port 8000 isn't in use

### "Permission error"
- **macOS/Linux**: May need `sudo`
- **Windows**: Ensure Docker Desktop has file access

---

## 📚 Learn More

- [Full Documentation](../README.md)
- [Building Custom Servers](../docs/custom-servers.md)
- [Docker Gateway Details](../docs/docker-gateway.md)
- [API Reference](../docs/)

---

🎯 **Next**: Build your first custom MCP server! Read [Building Custom Servers](../docs/custom-servers.md)
