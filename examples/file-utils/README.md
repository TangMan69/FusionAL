# File Utilities MCP Server

A Model Context Protocol (MCP) server that provides file system utilities. This example demonstrates how to build MCP servers that safely and securely interact with the filesystem.

## Features

- **count_lines**: Count total lines in a file
- **get_file_info**: Get file metadata (size, modification time, permissions)
- **search_text**: Search for text patterns within files
- **list_files**: List and filter files in a directory

## Building and Running

### Prerequisites
- Docker (recommended) or Python 3.11+
- Read/write access to filesystem paths

### Run with Docker

```bash
docker build -t file-utils:latest .
docker run -v /path/to/data:/data file-utils:latest
```

### Run Locally

```bash
pip install -r requirements.txt
python file_utils_server.py
```

## Integration with FusionAL

Register this server with FusionAL:

```python
import requests

server_config = {
    "name": "file-utils",
    "description": "File system utilities and analysis tools",
    "url": "http://localhost:9002",  # Adjust port as needed
    "metadata": {
        "tools": ["count_lines", "get_file_info", "search_text", "list_files"],
        "category": "Utilities"
    }
}

requests.post(
    "http://localhost:8080/register",
    json=server_config
)
```

## Tool Examples

### Count Lines
```
Input: filepath="README.md"
Output: ✅ File: README.md
- Total lines: 156
```

### Get File Info
```
Input: filepath="data.json"
Output: ✅ File Info: data.json
- Size: 45.32 KB
- Modified: 2026-02-08 15:30:45
- Type: File
- Readable: True
- Writable: True
```

### Search Text
```
Input: filepath="config.py", pattern="SECRET"
Output: ✅ Found 3 match(es) for 'SECRET':
- Line 15: SECRET_KEY = os.getenv("SECRET_KEY")
- Line 42: # TODO: Update SECRET configuration
- Line 89: encrypted_secret = cipher.decrypt(data)
```

### List Files
```
Input: directory="/home/user/projects", extension=".py"
Output: ✅ Files in /home/user/projects:
- main.py (2.14 KB)
- config.py (1.05 KB)
- utils.py (3.21 KB)
```

## Implementation Notes

- Demonstrates proper error handling (file not found, permissions, encoding)
- Shows pagination for large result sets
- Uses Path objects for cross-platform compatibility
- Single-line docstrings (required for MCP gateway compatibility)
- Logging to stderr for diagnostics
- All tool functions are async
- Safe file operations with encoding detection

## Security Considerations

- File paths are validated before access
- Permission checks performed before operations
- Network isolation via Docker provides additional security
- Non-root user execution recommended
- Read-only operations preferred; write operations require explicit permission

## Extending

To add more file utilities:
1. Add new async functions with `@mcp.tool()` decorator
2. Use single-line docstrings
3. Return formatted strings (not exceptions)
4. Include proper error handling
5. Log errors to stderr

Example:
```python
@mcp.tool()
async def file_hash(filepath: str = "file.txt") -> str:
    """Calculate SHA256 hash of a file."""
    # Implementation here
    return hash_result
```
