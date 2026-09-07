# Log Monitoring

This document describes how to **quickly view** logs from every service in production. FastBrace currently uses **Dozzle** as its production log viewing tool.

## **Dozzle** Advantages

- **Zero-config**: auto-discovers all Docker container logs, no collection rules to write
- **Lightweight**: a single container, ~10MB RAM, no impact on business workloads
- **Instant**: open the browser to search, filter, and tail logs from every service
- **Code-free**: logs go to container stdout/stderr; Dozzle reads the Docker log driver directly

## Prerequisites

FastBrace logs are written to both **local files** and **container stderr** in every environment, including production (see `infrastructure/core/log.py`). The stderr stream is collected by the Docker log driver, and Dozzle reads it via `/var/run/docker.sock`.

## 1. Deploy Dozzle

`deploy/docker-compose.yml` already includes the `dozzle` service. Start it alongside the business services:

```yaml
  dozzle:
    image: amir20/dozzle:latest
    restart: unless-stopped
    ports:
      - "${DOZZLE_PORT:-8890}:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

Once deployed, open `http://<server-ip>:8890` in your browser to view all container logs directly — no login required.

> No authentication by default. Restrict port `8890` to internal networks or trusted IPs via firewall rules. To enable username/password authentication, see "Configuring Access Authentication" below.

### Configuring Access Authentication (optional)

Dozzle v10 no longer supports setting credentials via environment variables; you must mount a `users.yaml` file.

1. Create `deploy/dozzle-users.yaml`:

```yaml
users:
  - name: admin
    password: <bcrypt-hashed password>
```

2. Generate a bcrypt password (run on the server):

```bash
docker run --rm amir20/dozzle:latest generate password "your-password"
```

3. Update `deploy/docker-compose.yml` to mount the file:

```yaml
  dozzle:
    image: amir20/dozzle:latest
    restart: unless-stopped
    ports:
      - "${DOZZLE_PORT:-8890}:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./dozzle-users.yaml:/data/users.yaml:ro
```

## 2. View Logs with Dozzle

After login, the left sidebar lists all containers (api, event-bus, cron_jobs, dozzle, etc.). Click any container to view:

- **Live tail**: new logs stream in automatically
- **Keyword search**: type in the search box; regex supported
- **Level filter**: filter by `INFO`, `WARNING`, `ERROR`, etc.
- **Time jump**: jump to logs at a specific timestamp
- **Multi-container merge**: select multiple containers to view a merged stream

## 3. Command Line (No Web UI)

To view logs from the terminal, use `docker compose logs` directly:

```bash
# Tail all services
docker compose -f deploy/docker-compose.yml logs -f

# Last 200 lines of the api service only
docker compose -f deploy/docker-compose.yml logs -f --tail=200 api

# api and event-bus together
docker compose -f deploy/docker-compose.yml logs -f api event-bus

# Errors only (grep)
docker compose -f deploy/docker-compose.yml logs api | grep -E "ERROR|CRITICAL"
```

## 4. Dozzle Operations Commands

All commands below are run from the project root, assuming the compose file is `deploy/docker-compose.yml`.

### Start / Stop / Restart

```bash
# Start dozzle
docker compose -f deploy/docker-compose.yml up -d dozzle

# Stop dozzle
docker compose -f deploy/docker-compose.yml stop dozzle

# Restart dozzle (after config changes)
docker compose -f deploy/docker-compose.yml restart dozzle

# Recreate the dozzle container (after editing compose; equivalent to stop + rm + up)
docker compose -f deploy/docker-compose.yml up -d --force-recreate dozzle
```

### Status and Logs

```bash
# Check dozzle running status
docker compose -f deploy/docker-compose.yml ps dozzle

# View dozzle's own logs (diagnose startup failures)
docker compose -f deploy/docker-compose.yml logs dozzle --tail=50

# Tail dozzle logs in real time
docker compose -f deploy/docker-compose.yml logs -f dozzle
```

### Port and Connectivity Checks

```bash
# Confirm port 8890 is listening
ss -tlnp | grep 8890

# Direct local test (bypasses nginx — tells you whether the issue is dozzle or the reverse proxy)
curl -sI http://localhost:8890 | head -5

# Check whether the page returns 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:8890
```

## 5. Structured Logs

FastBrace file logs use Loguru's `serialize=True` (see `infrastructure/core/log.py`), so each entry is a single JSON line — convenient for field-based parsing if you later adopt a heavier log platform (such as ELK) as the business grows. Container stdout output is plain text for direct readability.

Key fields:

| Field | Description |
|-------|-------------|
| `record.level.name` | Log level |
| `record.name` | Source module (logger name) |
| `record.time.repr` | Log timestamp |
| `record.extra.request_id` | Request ID |
| `text` | Human-readable formatted message |

## Key Practices and Caveats

- **Redaction**: never log passwords, tokens, access keys, phone numbers, or ID numbers
- **Retention**: the Docker json-file driver has no size limit by default; configure `max-size` and `max-file` in `daemon.json` to avoid filling the disk
- **Port security**: Dozzle reads docker.sock directly (high privilege) — restrict access via firewall; if exposing to the public internet, configure "Access Authentication"
- **Timezone**: logs use local time (`Asia/Shanghai`); Dozzle displays in the container's timezone
- **Log volume control**: keep production at `INFO`; avoid DEBUG to prevent slow writes and excess storage

## Additional Notes

> [!TIP]
>
> If the business later grows to a certain scale, it is best to use an official managed log platform such as Alibaba Cloud SLS to avoid maintenance overhead.
