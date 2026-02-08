# Building Custom MCP Servers

Learn how to create your own MCP servers using FusionAL's AI-powered builder or manually.

## Option 1: AI-Powered Generation (Recommended)

### Generate with Claude

```python
from core.ai_agent import generate_mcp_project

result = generate_mcp_project(
    prompt="""
    Build an MCP server that integrates with OpenWeather API.
    Features:
    - Get current weather for any city
    - Get 5-day forecast
    - Convert between Celsius and Fahrenheit
    """,
    provider="claude",
    out_dir="./weather-mcp",
    build=True,
    image_tag="weather-mcp:1.0"
)

print(f"Generated files: {result['files']}")
print(f"Output directory: {result['out_dir']}")
```

The AI will generate:
- `Dockerfile` - Container configuration
- `requirements.txt` - Dependencies
- `weather_server.py` - Complete MCP server
- `README.md` - Documentation

### Deploy Generated Server

```bash
cd weather-mcp
docker build -t weather-mcp .

# Register with FusionAL
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weather",
    "description": "Weather MCP Service",
    "metadata": {"image": "weather-mcp"}
  }'
```

---

## Option 2: Manual Server Creation

### 1. Project Structure

```
my-tool-server/
├── Dockerfile
├── requirements.txt
├── my_tool_server.py
├── .env
└── README.md
```

### 2. Write Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY my_tool_server.py .

# Create non-root user
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Run server
CMD ["python", "my_tool_server.py"]
```

### 3. Write requirements.txt

```
mcp[cli]>=1.2.0
# Add your dependencies
requests>=2.31.0
python-dotenv>=1.2.0
```

### 4. Write MCP Server

Key requirements:
- ✅ Use `@mcp.tool()` decorator
- ✅ **Single-line docstrings only** (multi-line breaks gateway)
- ✅ Return strings from all tools
- ✅ Use `async def`
- ✅ Log to `sys.stderr`
- ✅ Default parameters to empty strings `""`

```python
#!/usr/bin/env python3
"""
Weather Tool MCP Server - Example
"""

import os
import sys
import logging
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# Logging to stderr (required for MCP)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("weather-server")

# Initialize MCP server
mcp = FastMCP("weather")

# Configuration
API_KEY = os.getenv("OPENWEATHER_API_KEY", "")


@mcp.tool()
async def get_current_weather(city: str = "", units: str = "metric") -> str:
    """Get current weather for a city (metric or imperial units)."""
    logger.info(f"Fetching weather for {city}")
    
    if not city.strip():
        return "❌ Error: City name required"
    
    if not API_KEY:
        return "❌ Error: OpenWeather API key not configured"
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": API_KEY,
            "units": units
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        weather = data["weather"][0]["main"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        
        unit_symbol = "°C" if units == "metric" else "°F"
        
        return f"""🌤️ **{city.title()}** Weather:
- Conditions: {weather}
- Temperature: {temp}{unit_symbol} (feels like {feels_like}{unit_symbol})
- Humidity: {humidity}%
- Wind Speed: {wind_speed} m/s"""
    
    except requests.exceptions.Timeout:
        return "⏱️ Error: API request timed out"
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return f"❌ Error: City '{city}' not found"
        return f"❌ Weather API Error: {e}"
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def forecast(city: str = "", days: str = "5") -> str:
    """Get weather forecast for specified days (max 5)."""
    logger.info(f"Fetching {days} day forecast for {city}")
    
    if not city.strip():
        return "❌ Error: City name required"
    
    if not API_KEY:
        return "❌ Error: OpenWeather API key not configured"
    
    try:
        num_days = int(days) if days.strip() else 5
        if num_days < 1 or num_days > 5:
            return "❌ Error: Forecast limited to 1-5 days"
        
        # Use 5-day forecast API
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",
            "cnt": num_days * 8  # 8 forecasts per day (3-hour intervals)
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        forecasts = data["list"]
        result = f"📅 **{num_days}-Day Forecast for {city}:**\n"
        
        current_day = None
        for forecast in forecasts:
            timestamp = forecast["dt_txt"]
            date = timestamp.split()[0]
            
            if date != current_day:
                current_day = date
                result += f"\n**{date}:**"
            
            time = timestamp.split()[1][:5]
            temp = forecast["main"]["temp"]
            desc = forecast["weather"][0]["main"]
            result += f"\n  {time}: {temp}°C - {desc}"
        
        return result
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


# Server startup
if __name__ == "__main__":
    logger.info("Starting Weather MCP server...")
    
    if not API_KEY:
        logger.warning("OPENWEATHER_API_KEY not set - server will reject requests")
    
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
```

### 5. Create .env

```env
OPENWEATHER_API_KEY=your_api_key_here
```

### 6. Build & Test

```bash
# Build Docker image
docker build -t weather-mcp .

# Test locally
docker run -it \
  -e OPENWEATHER_API_KEY=your_key \
  weather-mcp

# Register
curl -X POST http://localhost:8000/register \
  -d '{"name": "weather", "description": "Weather Tool"}'
```

---

## Best Practices

### ✅ DO

- Use single-line docstrings only
- Return formatted strings with emojis
- Log to stderr
- Handle errors gracefully
- Use empty string defaults
- Validate user input

### ❌ DON'T

- Use `@mcp.prompt()` decorators
- Use multi-line docstrings
- Return exceptions
- Use `None` as default
- Make network calls without error handling
- Hardcode secrets

---

## Testing Your Server

### Command Line

```bash
# Test directly
export OPENWEATHER_API_KEY=your_key
python weather_server.py

# Send test request
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python weather_server.py
```

### In Claude

1. Register server: `curl -X POST http://localhost:8000/register ...`
2. Restart Claude Desktop
3. Try: _"Get weather for London"_

---

## Common Patterns

### API Integration

```python
async def call_api(endpoint: str = "", method: str = "GET") -> str:
    """Call external API with error handling."""
    try:
        if not endpoint.strip():
            return "❌ Error: Endpoint required"
        
        url = f"https://api.example.com{endpoint}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return f"✅ Result: {response.json()}"
    
    except requests.Timeout:
        return "⏱️ Error: Request timed out"
    except requests.HTTPError as e:
        return f"❌ API Error: {e.response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

### File Operations

```python
async def read_file(path: str = "") -> str:
    """Read and return file contents."""
    try:
        if not path.strip():
            return "❌ Error: File path required"
        
        with open(path, 'r') as f:
            content = f.read()
        
        return f"📄 Content from {path}:\n{content}"
    
    except FileNotFoundError:
        return f"❌ Error: File not found: {path}"
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

### System Commands

```python
async def run_command(cmd: str = "") -> str:
    """Execute shell command safely."""
    try:
        if not cmd.strip():
            return "❌ Error: Command required"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return f"✅ Output:\n{result.stdout}"
    
    except subprocess.TimeoutExpired:
        return "⏱️ Error: Command timed out"
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

---

## Deployment to Production

### Docker Compose

```yaml
version: '3.8'

services:
  weather-mcp:
    build: .
    environment:
      OPENWEATHER_API_KEY: ${OPENWEATHER_API_KEY}
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Run: `docker-compose up -d`

---

Got questions? See [Troubleshooting](./troubleshooting.md)
