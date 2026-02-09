# Weather API MCP Server

A Model Context Protocol (MCP) server that provides weather information integration. This example demonstrates how to build MCP servers that integrate with external APIs.

## Features

- **get_weather**: Fetch current weather conditions for a location
- **get_forecast**: Get multi-day weather forecasts (1-16 days)
- **parse_weather**: Parse and format raw weather JSON data

## Building and Running

### Prerequisites
- Docker (recommended) or Python 3.11+
- Internet connection for weather API calls

### Run with Docker

```bash
docker build -t weather-api:latest .
docker run --network host weather-api:latest
```

### Run Locally

```bash
pip install -r requirements.txt
python weather_server.py
```

## Integration with FusionAL

Register this server with FusionAL:

```python
import requests

server_config = {
    "name": "weather-api",
    "description": "Weather information and forecast service",
    "url": "http://localhost:9001",  # Adjust port as needed
    "metadata": {
        "tools": ["get_weather", "get_forecast", "parse_weather"],
        "category": "Utilities"
    }
}

requests.post(
    "http://localhost:8080/register",
    json=server_config
)
```

## Tool Examples

### Get Current Weather
```
Input: location="London"
Output: ✅ Weather in London:
- Temperature: 12°C
- Wind Speed: 15 km/h
```

### Get 5-Day Forecast
```
Input: location="Tokyo", days="5"
Output: ✅ 5-day Forecast for Tokyo:
- 2026-02-08: 5°C - 15°C
- 2026-02-09: 6°C - 16°C
...
```

### Parse Weather Data
```
Input: {"temperature": 20, "condition": "Sunny", "humidity": 65}
Output: ✅ Weather Summary:
- Condition: Sunny
- Temperature: 20°C
- Humidity: 65%
```

## Implementation Notes

- Uses the free Open-Meteo API (no API key required)
- Demonstrates error handling patterns
- Shows how to integrate external REST APIs
- Single-line docstrings (required for MCP gateway compatibility)
- Logging to stderr for diagnostics
- All tool functions are async

## Extending

To add more weather features:
1. Add new async functions with `@mcp.tool()` decorator
2. Use single-line docstrings
3. Return formatted strings (not exceptions)
4. Log errors to stderr

Example:
```python
@mcp.tool()
async def get_alerts(location: str = "New York") -> str:
    """Get weather alerts for a location."""
    # Implementation here
    return formatted_alerts
```
