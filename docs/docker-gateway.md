# Docker Gateway Notes

FusionAL commonly runs behind Docker MCP Gateway for client integrations.

## Expected local ports

- FusionAL API (direct): `8009`
- FusionAL API (via `compose.yaml` host mapping): `8089`

If you run `core/main.py` directly, use `http://localhost:8009`.
If you run via Docker Compose, use `http://localhost:8089` from the host.

## Quick health checks

```bash
curl http://localhost:8009/health
curl http://localhost:8089/health
```

At least one should return `{"status":"ok", ...}` depending on your launch mode.
