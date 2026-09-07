# Deployment Guide

This guide covers deploying the FastBrace backend to a server: the deployment architecture, initial setup (image registry / server / GitHub repository), parameter references, and post-deployment operations and common issues.

> Once deployment is set up, routine releases are handled automatically by the pipeline — see [CI/CD Pipeline Guide](./cicd-pipeline) for how it works.

## Deployment Architecture

FastBrace uses an "image registry + Docker Compose" deployment model:

1. GitHub Actions builds the application into a Docker image and pushes it to Alibaba Cloud ACR;
2. Deployment files (`docker-compose.yml`, etc.) are synced to the server over SSH;
3. The server pulls the image and runs the services via Docker Compose.

> [!TIP]
>
> **Why use Alibaba Cloud ACR for the image registry:** the server is located in China, and pulling images from `ghcr.io` times out and gets canceled due to network issues. ACR's domestic nodes pull fast — usually within **30 seconds** — keeping the whole deployment within **5-8 minutes**.

Containers running on the server (defined in `deploy/docker-compose.yml`):

| Container | Role | Port |
| --- | --- | --- |
| `api` | FastAPI HTTP service | host `${CONFIG_PORT}` → container `8889` |
| `event-bus` | Event bus consumer process | no exposed port |
| `cron_jobs` | Scheduled task process | no exposed port |
| `dozzle` | Lightweight log viewer — open in a browser to search/filter/tail container logs | host `${DOZZLE_PORT:-8890}` → container `8080` |

The three business containers use the **same image** (injected via the `HOUSE_IMAGE` variable) and differ only in their startup commands; logs are written to separate Docker volumes (`app_log` / `event_log` / `cron_log`, mounted at `/log/FastBrace/...` inside the containers).

Server directory layout (`DEPLOY_PATH`, e.g. `/srv/backend`):

```
/srv/backend/
├── .env                       # Environment variables (written automatically by the pipeline from APP_ENV_VARS)
└── deploy/
    └── docker-compose.yml     # Compose file (synced automatically by the pipeline)
```

## Initial Setup

### 1. Enable Alibaba Cloud Container Registry (ACR)

Visit [Alibaba Cloud Container Registry](https://cr.console.aliyun.com) and choose the **Personal Edition** (free):

1. After enabling the service, go to `Instance list → Personal instance`
2. Note the registry address, in the format `registry.cn-<region>.aliyuncs.com` (e.g., `registry.cn-hangzhou.aliyuncs.com`)
3. Go to `Namespaces` and create a namespace (e.g., `your-namespace`)
4. Go to `Repositories`, create a repository with the name `backend`, and select the **Private** type
5. Note or set the login password (`Access Credential → Fixed Password`)

> We recommend using a RAM sub-account granted only the `AliyunContainerRegistryFullAccess` permission instead of the primary account.

### 2. Server Preparation

> [!TIP]
>
> Prepare a server, install the Docker environment on it, and create a deployment directory.

```bash
# Install Docker (including the compose plugin)
curl -fsSL https://get.docker.com | sh
# Add the deployment user to the docker group (takes effect after re-login)
sudo usermod -aG docker $USER

# Create the project and deployment directories (the server does not need the app source code)
sudo mkdir -p  【deployment-dir】(such as: /srv/backend/deploy)
sudo chown $USER:$USER /srv/backend

# Upload the Compose file to the server
Upload the docker-compose file to the server deployment directory
```

> There is no need to log in to ACR manually on the server; the workflow logs in automatically on every deployment. On the first pipeline deployment, the `upload-deploy-files` job also creates the directory and syncs the compose file automatically.

### 3. GitHub Repository Configuration

**Create an Environment:**

`Repository Settings → Environments → New environment`, named `production`.

It is recommended to choose `Selected branches` under `Deployment branches and tags` so that only the `main` branch can trigger deployments.

**Add the following Secrets to the `production` Environment:**

> ⚠️ All Secrets must be placed in the `production` Environment secrets; every pipeline job declares `environment: production`, so all of them can read these secrets.

| Secret                   | Required | Description                                      |
| ------------------------ | -------- | ------------------------------------------------ |
| `DEPLOY_HOST`            | ✅       | Server IP or domain                              |
| `DEPLOY_PORT`            | Optional | SSH port; defaults to 22 if empty                |
| `DEPLOY_USER`            | ✅       | SSH login username                               |
| `DEPLOY_PATH`            | ✅       | Server project directory, e.g. `/srv/backend`    |
| `DEPLOY_SSH_PRIVATE_KEY` | ✅       | Full SSH private key content (including first and last lines) |
| `ACR_REGISTRY`           | ✅       | ACR address, e.g. `registry.cn-hangzhou.aliyuncs.com` |
| `ACR_NAMESPACE`          | ✅       | ACR namespace, e.g. `your-namespace`             |
| `ACR_REPO`               | Optional | ACR repository name; defaults to `backend` if empty |
| `ACR_USERNAME`           | ✅       | Primary account login name, or RAM sub-account format `user@<primary-account-id>` |
| `ACR_PASSWORD`           | ✅       | Alibaba Cloud login password or fixed password   |
| `APP_ENV_VARS`           | ✅       | All production environment variables for the app (multi-line text, see below) |

**Generate the deployment SSH key:**

```bash
ssh-keygen -t ed25519 -C "github-actions" -f ./deploy_key -N ""
cat ./deploy_key        # private key → paste into DEPLOY_SSH_PRIVATE_KEY
cat ./deploy_key.pub    # public key → append to the server's ~/.ssh/authorized_keys
```

## Parameter Reference

### `APP_ENV_VARS` environment variables

All production environment variables are written in **one** secret (multi-line text); the pipeline writes them to `$DEPLOY_PATH/.env` on the server during deployment:

```
ENV=prod
HOUSE_IMAGE=
CONFIG_PORT=8888
JWT__SECRET_KEY=
DB__HOST=
DB__USERNAME=
DB__PASSWORD=
DB__DATABASE=
REDIS_DB__HOST=
REDIS_DB__PASSWORD=
OBJECT_STORAGE__ACCESS_KEY=your_oss_key
OBJECT_STORAGE__SECRET_KEY=your_oss_secret
```

Variable descriptions:

| Variable | Description |
| --- | --- |
| `ENV` | Runtime environment; must be `prod` in production (affects log output paths and other behavior) |
| `HOUSE_IMAGE` | Leave empty; the business image address is injected by the pipeline via an environment variable during deployment |
| `CONFIG_PORT` | Host port mapped to the `api` service; the pipeline health check accesses `8888` by default, so keeping `8888` is recommended, and it must match your reverse proxy / firewall rules |
| `JWT__SECRET_KEY` | JWT signing key |
| `DB__HOST` / `DB__USERNAME` / `DB__PASSWORD` / `DB__DATABASE` | Database connection settings |
| `REDIS_DB__HOST` / `REDIS_DB__PASSWORD` | Redis connection settings |
| `OBJECT_STORAGE__ACCESS_KEY` / `OBJECT_STORAGE__SECRET_KEY` | Object storage (OSS) credentials |

Whenever an iteration requires changing environment variables, just update that secret and re-trigger the workflow.

### Compose variables

`deploy/docker-compose.yml` also references the following variables:

| Variable | Description |
| --- | --- |
| `HOUSE_IMAGE` | Image address shared by the three business containers (`api` / `event-bus` / `cron_jobs`); injected by the pipeline when running `docker compose up` |
| `CONFIG_PORT` | Host port for the `api` service; the container listens on `8889` internally |
| `DOZZLE_PORT` | Host port for the `dozzle` log viewer; defaults to `8890`, open `http://<server-ip>:8890` in a browser |

## Image Mirror Acceleration for Log Viewer (China)

The log viewer `dozzle` hosts its image `amir20/dozzle` on `docker.io`, and direct pulls from servers in China may time out. Following the [DaoCloud public-image-mirror](https://github.com/DaoCloud/public-image-mirror) project, replacing the image address prefix with `docker.m.daocloud.io/xxx` routes pulls through domestic nodes, with image hashes identical to the source registry.

**Image mapping (`docker.io` → `docker.m.daocloud.io`):**

| Original image in compose | Accelerated address                          |
| ------------------------- | -------------------------------------------- |
| `amir20/dozzle:latest`    | `docker.m.daocloud.io/amir20/dozzle:latest`  |

### Option 1: Configure a Docker registry mirror (recommended, no compose change)

Edit `/etc/docker/daemon.json` on the server (create the file if it does not exist):

```json
{
  "registry-mirrors": ["https://docker.m.daocloud.io"]
}
```

Restart Docker for the change to take effect:

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

> All `docker.io` images (including `amir20/dozzle`) are then pulled through domestic nodes automatically; `deploy/docker-compose.yml` needs no changes. Note that `registry-mirrors` only applies to `docker.io`; business images via ACR are unaffected.

### Option 2: Pull manually and retag

If you prefer not to change the server's Docker configuration, pull via the accelerated address and retag so compose uses the local image directly:

```bash
docker pull docker.m.daocloud.io/amir20/dozzle:latest
docker tag docker.m.daocloud.io/amir20/dozzle:latest amir20/dozzle:latest
```

### Option 3: Modify the compose image address directly

Replace the `dozzle` image field in `deploy/docker-compose.yml` with the accelerated address, and sync the compose file under the server's `DEPLOY_PATH/deploy` directory:

```yaml
  dozzle:
    image: docker.m.daocloud.io/amir20/dozzle:latest
```

### Notes

1. The mirror is a public cache service with [whitelisting and rate limits](https://github.com/DaoCloud/public-image-mirror/issues/2328); schedule bulk pulls during off-peak hours (01:00-07:00 Beijing time)
2. Mirror service status: [DaoCloud status page](https://status.daocloud.io/status/docker); a `toomanyrequests` error means rate limiting, just retry later

## Post-deployment Verification and Troubleshooting Commands

```bash
# Check service status
docker compose -f /srv/backend/deploy/docker-compose.yml ps

# View logs
docker compose -f /srv/backend/deploy/docker-compose.yml logs --tail=100 api
docker compose -f /srv/backend/deploy/docker-compose.yml logs --tail=100 event-bus cron_jobs

# Health check
curl -i http://127.0.0.1:8888/health

# Manually prune old images
docker image prune -af
```

## Disk Space Management

Runs automatically on every deployment:

1. `docker image prune -f`: cleans up dangling images
2. Keeps the latest 2 versions and deletes older ones

When disk space runs low, run manually:

```bash
docker image prune -af
```

## Common Issues

**Q: The deploy phase reports `no configuration file provided: not found`**

There is no `docker-compose.yml` file under the configured `DEPLOY_PATH` directory. Normally the pipeline's `upload-deploy-files` job syncs it automatically; if deploying manually, place the file in the server's `DEPLOY_PATH/deploy/` directory.

**Q: `docker pull` times out and is canceled during the deploy phase**

The workflow now uses Alibaba Cloud ACR, and pull speed in China is normal. If it still times out, check that the ACR region matches the server's region (e.g., if the server is in Hangzhou, choose `cn-hangzhou` for ACR).

**Q: `docker pull` reports `unauthorized`**

Check that `ACR_USERNAME` / `ACR_PASSWORD` are correct, or that the ACR repository is private and the account has access.

**Q: The log viewer container (dozzle) fails to start, reporting image pull timeouts**

The `amir20/dozzle` image comes from `docker.io`, which may time out when pulled directly from China. See the "Image Mirror Acceleration for Log Viewer (China)" section above: configure a Docker registry mirror (Option 1), or pull via `docker.m.daocloud.io` and retag (Option 2).

**Q: SSH connection fails with `Permission denied (publickey)`**

1. `DEPLOY_SSH_PRIVATE_KEY` contains the private key (not the `.pub` file) and its content is complete
2. The corresponding public key has been appended to the server's `~/.ssh/authorized_keys`
3. The server's `~/.ssh` permissions are `700` and `authorized_keys` permissions are `600`
4. Verify locally: `ssh -i ./deploy_key -p 22 user@server "whoami"`

**Q: Health check times out**

Check the api container's startup logs:

```bash
docker compose -f /srv/backend/deploy/docker-compose.yml logs --tail=100 api
```

Common causes: database connection failure, or a misconfiguration in `APP_ENV_VARS`. Also make sure `CONFIG_PORT` in `APP_ENV_VARS` matches the port the service actually listens on and the port the pipeline health check accesses.
