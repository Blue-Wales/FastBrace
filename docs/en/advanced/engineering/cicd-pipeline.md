# CI/CD Pipeline Guide

This document introduces FastBrace's CI/CD pipeline: what a pipeline is, what it does, how the FastBrace pipeline is configured, and common issues that occur while the pipeline runs.

> For your first deployment, start with the [Deployment Guide](./deployment-guide) to complete the initial setup of the server, image registry, and GitHub Secrets.

## What Is a Pipeline

A CI/CD (Continuous Integration / Continuous Deployment) pipeline is a declaratively defined release process stored in the code repository and executed automatically by a platform. FastBrace uses **GitHub Actions**, with the pipeline defined in the repository's `.github/workflows/main.yml` file.

What the pipeline does:

1. **One-click releases**: after merging code into `main`, manually trigger the workflow once from the GitHub page — building the image, pushing it to the registry, syncing deployment files, restarting services, and running health checks all happen automatically, with no need to log into the server.
2. **Consistent environments**: the application and all its dependencies are packaged into a single Docker image, so the build and production runtime environments are identical — avoiding "works on my machine, fails in production".
3. **Traceable versions**: every released image is tagged with the pipeline run number, `run-N`, so the image running in production maps one-to-one to a GitHub Actions run record, making it easy to locate issues and roll back.
4. **Verify on release**: after deployment the pipeline automatically polls the health check endpoint; on failure it prints container logs and fails the pipeline, exposing problems immediately.
5. **Automatic cleanup**: every deployment cleans up dangling images and old image versions automatically, preventing the server disk from filling up.

## Pipeline Overview

The FastBrace pipeline is named `backend-ci-cd` and consists of three jobs:

```
build-and-push (build and push image) ┐
                                      ├──> deploy (deploy to production)
upload-deploy-files (upload deploy files) ┘
```

| Job | Role | Relationship to other jobs |
| --- | --- | --- |
| `build-and-push` | Builds the Docker image on a GitHub runner and pushes it to Alibaba Cloud ACR | Runs in parallel with upload |
| `upload-deploy-files` | Syncs the `deploy/` directory (compose file, etc.) to the server over SSH | Runs in parallel with build |
| `deploy` | SSHes into the server, pulls the new image, restarts services, and runs health checks | Waits for both previous jobs to succeed |

Three parties collaborate:

- **GitHub Actions runner**: the ephemeral Ubuntu environment provided by GitHub that performs the build and push;
- **Alibaba Cloud ACR**: the private image registry storing Docker images;
- **Production server**: receives deployment files over SSH, pulls images, and runs the services with Docker Compose.

## Pipeline Configuration in Detail

The full pipeline definition lives in the repository file `.github/workflows/main.yml`.

### Trigger and concurrency control

```yaml
on:
  workflow_dispatch:

concurrency:
  group: backend-production-deploy
  cancel-in-progress: false
```

- `workflow_dispatch`: **manual trigger** — the pipeline does not run automatically on push / PR. To release, click `Run workflow` on the repository's `Actions` page.
- `concurrency`: only one production deployment is allowed at a time; `cancel-in-progress: false` means a newly triggered pipeline **waits in queue** instead of canceling an in-progress deployment, preventing two deployments from interrupting each other.
- All three jobs declare `environment: production`, so they are uniformly governed by the GitHub Environment protection rules (you can restrict runs to the `main` branch only, or even require manual approval), and all secrets are configured centrally in the `production` environment.
- Each job sets `timeout-minutes` to prevent runners from being occupied for too long when something goes wrong.

### Job 1: build-and-push (build and push image)

| Step | Description |
| --- | --- |
| `actions/checkout@v4` | Checks out the `main` branch code |
| Generate image name | Assembles the image address: `<ACR_REGISTRY>/<ACR_NAMESPACE>/<ACR_REPO, defaults to backend>:run-<run number>` |
| `docker/login-action@v3` | Logs into Alibaba Cloud ACR using `ACR_USERNAME` / `ACR_PASSWORD` |
| `docker/setup-buildx-action@v3` | Enables Buildx (the BuildKit builder) |
| `docker/build-push-action@v6` | Builds the image per `deploy/Dockerfile` and pushes it |

Key configuration of the build step:

- `context: .` + `file: deploy/Dockerfile`: the build context is the repository root, and the Dockerfile lives under `deploy/`.
- The image tag looks like `...:run-<run number>`: the tag uses the GitHub Actions run number (`github.run_number`), which is monotonically increasing across the repository, guaranteeing a unique image tag for every release.
- `provenance: false` / `sbom: false`: disables provenance / sbom attestations. Otherwise BuildKit pushes an OCI image index containing an `application/vnd.oci.empty.v1+json` empty descriptor, which the Alibaba Cloud ACR Personal Edition does not recognize and rejects with `unknown manifest class`.
- `cache-from: type=gha` / `cache-to: type=gha,mode=max`: reuses Docker build layers via the GitHub Actions cache. When dependencies are unchanged, build time drops from 8-12 minutes on a cold run to 1-2 minutes.
- The job declares `permissions: contents: read` and `packages: write`, following the principle of least privilege.

### Job 2: upload-deploy-files (upload deployment files)

The server does not need the application source code, but it does need runtime configuration such as the Docker Compose file. This job:

1. **Configures SSH**: writes the `DEPLOY_SSH_PRIVATE_KEY` private key (with `600` permissions) and adds the server fingerprint to `known_hosts` via `ssh-keyscan` to prevent man-in-the-middle attacks.
2. **Creates the deployment directory**: creates `$DEPLOY_PATH/deploy` on the server.

   > The compose file references the environment file via `env_file: ../.env`, so the compose file must live at `$DEPLOY_PATH/deploy/` and the `.env` file at `$DEPLOY_PATH/.env`.

3. **Syncs the `deploy/` directory through an SSH pipe**:

   ```bash
   tar -C deploy --exclude='Dockerfile*' --exclude='deploy.sh' -czf - . \
     | ssh ... "tar -C '$DEPLOY_PATH/deploy' -xzf -"
   ```

   Only the files needed to run compose are synced, excluding `Dockerfile` (only used at build time, not needed on the server) and `deploy.sh` (a local debugging script).

### Job 3: deploy (deploy to production)

`needs: [build-and-push, upload-deploy-files]` ensures the image has been pushed and the deployment files synced before this job runs. It then SSHes into the server and executes, in order:

1. **Log into ACR**: `docker login`, so the server has permission to pull the private image;
2. **Write environment variables**: `APP_ENV_VARS` is first base64-encoded on the runner, then decoded and written to `$DEPLOY_PATH/.env` on the server, preventing multi-line text and special characters from being mangled by shell escaping during SSH transfer;
3. **Pull the new image**: `docker pull <image>:run-N`;
4. **Stop the old services**: `docker compose down --remove-orphans` (the new image address is passed to compose via the `HOUSE_IMAGE` environment variable);
5. **Clean up old images**: `docker image prune -f` removes dangling images, and old versions of the same repository beyond the most recent 2 are deleted;
6. **Start the new services**: `HOUSE_IMAGE=<new image> docker compose -f deploy/docker-compose.yml up -d`, starting the four containers `api`, `event-bus`, `cron_jobs`, and `dozzle`;
7. **Health check**: polls at most 20 times with a 5-second interval (about 100 seconds total), requesting `http://127.0.0.1:${CONFIG_PORT:-8888}/health`; a response containing `"status":"healthy"` means deployment succeeded. On timeout it prints the last 50 lines of `api` container logs and fails the pipeline.

The SSH connection additionally sets `ServerAliveInterval=15` / `ServerAliveCountMax=40` to prevent the long connection from being dropped while pulling large images.

> `deploy/deploy.sh` is a **local manual debugging script** equivalent to the deployment flow above. Formal deployments are performed automatically by the pipeline; the script does not need to be run manually.

## Routine Release Process

1. Merge the code into the `main` branch
2. Open the repository's `Actions` → select `backend-ci-cd` → click `Run workflow` → select `main`
3. Wait for all three jobs — `build-and-push`, `upload-deploy-files`, and `deploy` — to succeed

**Expected duration:**

| Phase                         | First run | Cached (code-only changes) | Cached (dependencies unchanged) |
| ----------------------------- | --------- | -------------------------- | ------------------------------- |
| Build and push                | 8-12 min  | 3-5 min                    | 1-2 min                         |
| Deploy (including image pull) | 3-5 min   | 2-3 min                    | 2-3 min                         |

## Rollback

The server keeps the most recent 2 image versions. To roll back, SSH into the server, point `HOUSE_IMAGE` at an older image version, and restart the services:

```bash
cd $DEPLOY_PATH
HOUSE_IMAGE="<ACR_REGISTRY>/<ACR_NAMESPACE>/<backend>:run-<old-number>" \
  docker compose -f deploy/docker-compose.yml up -d
```

## Common Issues

**Q: The Alibaba Cloud ACR login step fails**

1. Make sure `ACR_USERNAME`, `ACR_PASSWORD`, and `ACR_REGISTRY` are all set
2. `ACR_USERNAME`: in ACR, copy the username under the login instance in the "Access Credential" section — usually the Alibaba Cloud account login name
3. `ACR_PASSWORD`: set a fixed password in the "Access Credential" section, then use that fixed password
4. `ACR_REGISTRY`: in the "Access Credential" section, copy the address shown next to the username of the login instance

**Q: The build phase reports a `push access denied` error**

Details: `failed to push xx/xx/xx:run-31: push access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed`

1. `ACR_REGISTRY` must be the address copied from the "Access Credential" section in ACR, next to the username of the login instance
2. Confirm the corresponding namespace and image repository (default name `backend`) have been created in ACR, and the account has push permission (a RAM sub-account granted `AliyunContainerRegistryFullAccess` is recommended)

**Q: Pushing the image reports `unknown manifest class`**

The Alibaba Cloud ACR Personal Edition does not recognize the OCI image index that BuildKit pushes by default. The pipeline already sets `provenance: false` and `sbom: false` to avoid this; if you modify the build steps yourself, do not re-enable these two options.

**Q: SSH connection fails with `Permission denied (publickey)`**

1. `DEPLOY_SSH_PRIVATE_KEY` contains the private key (not the `.pub` file) and its content is complete (including the first and last lines)
2. The corresponding public key has been appended to the server's `~/.ssh/authorized_keys`
3. The server's `~/.ssh` permissions are `700` and `authorized_keys` permissions are `600`
4. Verify locally: `ssh -i ./deploy_key -p 22 user@server "whoami"`

**Q: The deploy job health check times out / fails**

A failed health check means the services on the server did not start correctly — common causes are database connection failures, misconfigured `APP_ENV_VARS`, or mismatched ports. For server-side troubleshooting, see [Deployment Guide - Common Issues](./deployment-guide#common-issues).

## Related Documents

- [Deployment Guide](./deployment-guide): server preparation, ACR activation, GitHub Secrets and environment variable parameter reference, deployment operations and troubleshooting
