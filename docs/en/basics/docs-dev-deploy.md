# Documentation Site: Development and Deployment

The FastBrace documentation site is built with [VitePress](https://vitepress.dev/) and supports both Chinese and English. This page explains how to start the docs development server locally and how to deploy the docs to production.

## Local Development

### Requirements

| Component    | Version requirement     | Description                    |
| ------- | ------------ | ----------------------- |
| Node.js | 18+          | 22 LTS recommended             |
| npm     | Installed with Node | Used to install VitePress dependencies |

### Install Dependencies

Go to the `docs/` directory and install dependencies:

```bash
cd docs
npm install
```

### Start the Dev Server

```bash
# From the docs/ directory:
npm run docs:dev

# Or from the project root:
make docs-dev
```

Once started, visit `http://localhost:5173` to preview the docs site. Hot reloading is supported — pages refresh automatically when Markdown files change.

### Build and Preview Locally

Before publishing, it is recommended to verify the build output locally:

```bash
# Build the static site
npm run docs:build

# Preview the build output (default port 4173)
npm run docs:preview
```

The build output lives in `docs/.vitepress/dist/` and can be deployed to any static hosting service.

## Production Deployment

### Prerequisites

1. Prepare a server (if deploying manually)
2. Install and configure Nginx
3. Create the docs directory

### Nginx Configuration

The following is a reference configuration that points your domain to the VitePress build output directory:

```nginx
server {
    listen 80;
    server_name <your-domain>;

    root {docs-directory}/dist;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;

    # Long-lived caching for static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback & cleanUrls support
    location / {
        try_files $uri $uri.html $uri/ =404;
    }

    # Custom 404 page
    error_page 404 /404.html;
}
```

### Manual Deployment

1. Build the docs locally or in a CI environment:

```bash
make docs-build
```

2. Upload the build output to the server, i.e. upload the `dist` directory under `docs/.vitepress/` to the docs directory on the server

3. Reload Nginx:

```bash
sudo nginx -s reload
```

## Automated Deployment with GitHub Actions

The project ships with `.github/workflows/deploy-docs.yaml`. When files under `docs/` change and are pushed to the `main` branch, the build and deployment run automatically.

### Configure GitHub Secrets

Add the following secrets in the repository under **Settings → Secrets and variables → Actions**:

| Secret name        | Description                     | Example                                |
| ------------------ | ------------------------ | ----------------------------------- |
| `DOCS_DEPLOY_HOST` | Server IP or domain         | `123.45.67.89`                      |
| `DOCS_DEPLOY_PORT` | SSH port (default 22)      | `22`                                |
| `DOCS_DEPLOY_USER` | SSH login username           | `deploy`                            |
| `DOCS_DEPLOY_KEY`  | SSH private key (for key-based login) | `-----BEGIN OPENSSH PRIVATE KEY...` |
| `DOCS_DEPLOY_PATH` | Deployment directory on the server       | `{docs-directory}/dist`         |

### SSH Passwordless Setup

Generate a dedicated key pair for deployment locally (skip if you already have one):

```bash
ssh-keygen -t ed25519 -C "FastBrace-docs-deploy" -f ~/.ssh/docs_deploy_key
```

Add the public key to `~/.ssh/authorized_keys` on the server:

```bash
ssh-copy-id -i ~/.ssh/docs_deploy_key.pub deploy@your-server
```

Then paste the private key contents (`~/.ssh/docs_deploy_key`) into the GitHub Secret `DOCS_DEPLOY_KEY`.

## Deploying with Cloudflare Pages (Recommended 🌟)

Besides deploying to your own server with Nginx, you can also use [Cloudflare Pages](https://developers.cloudflare.com/pages/), following the [official VitePress guide](https://developers.cloudflare.com/pages/framework-guides/deploy-a-vitepress-site/).

Cloudflare Pages is a static hosting and continuous deployment service provided by Cloudflare. It builds and publishes your site automatically from a Git repository; the free tier is more than enough for a documentation site. Domains default to `*.pages.dev`, and you can also connect your own custom domain.

### Option 1: Connect a Git Repository via the Cloudflare Dashboard

This is the recommended zero-configuration approach — no Cloudflare CLI tools need to be installed locally.

#### 1. Push code to a remote Git repository

Make sure the project (including the `docs/` directory) is pushed to a supported hosting platform such as GitHub:

```bash
git remote add origin https://github.com/<your-username>/FastBrace.git
git branch -M main
git push -u origin main
```

#### 2. Create a Pages project in Cloudflare

1. Log in to the [Cloudflare Dashboard](https://dash.cloudflare.com/) and go to the **Workers & Pages** page.
2. Click **Create application**.
3. Select the **Pages** tab.
4. Click **Connect to Git**, select the FastBrace repository, then click **Begin setup**.

#### 3. Configure the build settings

Because VitePress lives in the `docs/` subdirectory in this project, fill in the build settings as follows:

| Configuration                       | Value                                   |
| ----------------------------------- | --------------------------------------- |
| Production branch                   | `main`                                  |
| Framework preset                    | `None` (no need to select the VitePress preset) |
| Build command                       | `cd docs && npm install && npm run docs:build` |
| Build output directory              | `docs/.vitepress/dist`                  |
| Deploy command                      | `npx wrangler pages deploy docs/.vitepress/dist --project-name <your-project-name>` |

> **Note**: Cloudflare's built-in VitePress framework preset (build command `npx vitepress build`, build output directory `.vitepress/dist`) assumes VitePress is at the repository root. This project keeps VitePress in the `docs/` subdirectory, so you must set the build command and output directory manually and select the framework preset `None`.

> **Important**: The deploy command defaults to `npx wrangler deploy` (which deploys a Workers script) and fails for a static site with `Could not detect a directory containing static files`. Change it to `npx wrangler pages deploy docs/.vitepress/dist --project-name <your-project-name>`, replacing `<your-project-name>` with the project name you entered when creating the Pages application in Cloudflare (the part before `.pages.dev`). Without `--project-name`, it fails with `Missing Pages project name`.

#### 4. Start the first deployment

Click **Save and Deploy**. Cloudflare will automatically install dependencies, build the site, and publish it. When finished, you will get an access URL like `https://<project-name>.pages.dev`. Every time you commit and push to the `main` branch, it will rebuild and redeploy automatically.

> **Tip**: Pull Requests also generate **preview deployments**, so you can see how changes look before going live.

### Configuring Static Asset Caching (Optional)

Cloudflare enables its CDN by default. You can additionally create a `docs/.vitepress/dist/_headers` file or configure cache rules in the Cloudflare dashboard to set long-lived caching for static assets and improve load times.