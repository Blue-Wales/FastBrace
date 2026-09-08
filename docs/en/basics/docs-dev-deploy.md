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

### Option 1: Build Locally, Then Upload to Cloudflare

This is currently the most recommended zero-configuration approach — no Cloudflare CLI tools need to be installed locally.

1. Run `make docs-build` locally; the static assets are generated under `docs/.vitepress/dist`
2. Go to the Cloudflare dashboard, find **Build** in the left sidebar, then select **Compute → Workers & Pages**
   1. ![Screenshot](https://picgocloud.com/m/5272cd20-0dcf-473d-8c5c-de51c04a5fec.png)
3. Click **Create application** in the upper right corner, then select **Upload your static files**
   1. ![Screenshot](https://picgocloud.com/m/73ce3a72-c71b-47fe-bf56-db4398f9f972.png)
4. Finally, choose your deployment and wait for the result



### Bind a Custom Domain (Optional)

If you want to bind your own custom domain after deploying the docs site, follow these steps:

1. Purchase a domain from a cloud provider such as Alibaba Cloud, Tencent Cloud, or Cloudflare
2. In the Cloudflare sidebar, go to **Domains → Overview**, then click **Add domain** and follow the setup wizard
3. Finally, obtain the two NS records assigned by Cloudflare and update them in your domain provider's DNS settings

### Configuring Static Asset Caching (Optional)

Cloudflare enables its CDN by default. You can additionally create a `docs/.vitepress/dist/_headers` file or configure cache rules in the Cloudflare dashboard to set long-lived caching for static assets and improve load times.