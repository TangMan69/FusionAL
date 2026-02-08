# FusionAL MCP Builder Prompt

Reference MCP builder template. Complete prompt templates are in the documentation.

## Key Guidelines for MCP Servers

### ✅ MUST DO

1. **Single-line docstrings only**
   - Multi-line docstrings break the gateway
   - One line: `"""Single line description."""`

2. **All parameters default to empty strings**
   - ❌ WRONG: `param: str = None`
   - ✅ RIGHT: `param: str = ""`

3. **Return only strings**
   - All tools must return formatted text
   - Use emojis for visual clarity

4. **Log to stderr**
   - Gateway needs stdout for protocol
   - Use: `logging.basicConfig(stream=sys.stderr)`

5. **Use async functions**
   - All `@mcp.tool()` functions must be `async def`

### ❌ DON'T

- Use `@mcp.prompt()` decorators
- Use `prompt` parameter in `FastMCP()`
- Complex type hints from `typing` module
- Multi-line docstrings (causes gateway panic)
- Return exceptions
- Hardcode credentials

## Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *_server.py .

RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

CMD ["python", "*_server.py"]
```

## Example Tool Structure

```python
@mcp.tool()
async def my_tool(param: str = "") -> str:
    """One-line description of functionality."""
    try:
        if not param.strip():
            return "❌ Error: Parameter required"
        
        # Implementation here
        result = ...
        return f"✅ Success: {result}"
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"
```

For complete builder prompt with examples, see:
https://github.com/TangMan69/docker-mcp-tutorial/blob/main/mcp-builder-prompt/mcp-builder-prompt.md
