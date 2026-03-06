# Troubleshooting

## Server not reachable

1. Verify FusionAL is running:
   - `python -m uvicorn main:app --reload --port 8009` (direct)
   - or `docker compose up -d --build` (compose)
2. Check health endpoints:
   - `curl http://localhost:8009/health`
   - `curl http://localhost:8089/health`

## Docker sandbox errors

1. Confirm Docker is running: `docker ps`
2. Confirm your account can access Docker daemon.
3. Re-test `/execute` with `"use_docker": false` to isolate Docker-specific issues.

## MCP tools not visible in client

1. Confirm client config points to the correct endpoint or gateway.
2. Restart the client after config changes.
3. Check FusionAL logs for startup errors and auth failures.
