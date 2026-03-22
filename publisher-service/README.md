# Publisher Service

Thin HTTP wrapper over auto-publisher adapters.
Reads platform_post by ID from DB, publishes via adapter, returns result.

## Endpoints

| Method | Path | Description | DB changes? |
|--------|------|-------------|-------------|
| POST | /publish | Publish by platform_post_id | Yes (sending→sent/failed) |
| POST | /verify | Verify post exists on platform | No |
| POST | /test-publish | **DISABLED** (HTTP 403) | — |
| GET | /health | Health check | No |

## Guards

- **Anti-duplicate:** atomic `sending` lock before publish
- **Allowlist:** `PUBLISH_ALLOWLIST` env var (secondary to SQL upstream in n8n)
- **Feature flags:** `THREADS_REPLY_ENABLED` (default false)

## Deployment

Docker on Contabo, part of n8n docker-compose network.
Port: 8085 internal, 8086 external.

```bash
# Build + deploy (from /opt/n8n/)
docker compose build publisher-service
docker compose up -d publisher-service
```

## Env vars

From `/opt/zinin-corp/.env`:
- Platform tokens (TELEGRAM_CEO_BOT_TOKEN, THREADS_ACCESS_TOKEN, etc.)
- PUBLER_API_KEY, PUBLER_WORKSPACE_ID, PUBLER_*_ACCOUNT_ID
- PUBLISH_ALLOWLIST (comma-separated platform names)
- THREADS_REPLY_ENABLED (true/false)

From docker-compose:
- PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD

## Source of truth

This directory (`content-pipeline/publisher-service/`) is the canonical source.
Deploy: copy main.py + Dockerfile to Contabo `/opt/publisher-service/`.
