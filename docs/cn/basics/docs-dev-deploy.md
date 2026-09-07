# 文档站开发与部署

FastBrace 文档站基于 [VitePress](https://vitepress.dev/) 构建，支持中英双语。本页介绍如何在本地启动文档开发服务器，以及如何将文档部署到生产环境。

## 本地开发

### 环境要求

| 组件    | 版本要求     | 说明                    |
| ------- | ------------ | ----------------------- |
| Node.js | 18+          | 推荐 22 LTS             |
| npm     | 随 Node 安装 | 用于安装 VitePress 依赖 |

### 安装依赖

进入 `docs/` 目录并安装依赖：

```bash
cd docs
npm install
```

### 启动开发服务器

```bash
在docs目录下执行： npm run docs:dev

或者在根目录执行：  make docs-dev
```

启动后访问 `http://localhost:5173` 即可预览文档站，支持热更新——修改 Markdown 文件后页面会自动刷新。



### 构建与本地预览

在发布前，建议先在本地验证构建产物：

```bash
# 构建静态站点
npm run docs:build

# 预览构建产物（默认端口 4173）
npm run docs:preview
```

构建产物位于 `docs/.vitepress/dist/`，可直接部署到任意静态托管服务。



## 生产部署



### 前提

1. 准备一台服务器 （如果手动部署）
2. 安装配置好nginx
3. 创建文档目录



### Nginx 配置

以下是一份参考配置，将域名指向 VitePress 构建产物目录：

```nginx
server {
    listen 80;
    server_name 【你的域名】;

  root {文档目录}/dist;
    index index.html;

    # 开启 gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;

    # 静态资源长缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # SPA 回退 & cleanUrls 支持
    location / {
        try_files $uri $uri.html $uri/ =404;
    }

    # 自定义 404 页面
    error_page 404 /404.html;
}
```

### 手动部署

1. 在本地或 CI 环境中构建文档：

```bash
make docs-build
```



2. 将构建产物上传到服务器，即将构建好的docs/.vitepress/下的dist目录上传到服务器文档目录



3. 重新加载 Nginx：

```bash
sudo nginx -s reload
```



## GitHub Actions 自动化部署

项目已配置 `.github/workflows/deploy-docs.yaml`，当 `docs/` 目录下的文件发生变更并推送到 `main` 分支时，自动完成构建与部署。



### 配置 GitHub Secrets

在仓库的 **Settings → Secrets and variables → Actions** 中添加以下 Secret：

| Secret 名称        | 说明                     | 示例                                |
| ------------------ | ------------------------ | ----------------------------------- |
| `DOCS_DEPLOY_HOST` | 服务器 IP 或域名         | `123.45.67.89`                      |
| `DOCS_DEPLOY_PORT` | SSH 端口（默认 22）      | `22`                                |
| `DOCS_DEPLOY_USER` | SSH 登录用户名           | `deploy`                            |
| `DOCS_DEPLOY_KEY`  | SSH 私钥（用于免密登录） | `-----BEGIN OPENSSH PRIVATE KEY...` |
| `DOCS_DEPLOY_PATH` | 服务器上的部署目录       | `{文档目录}/dist`                   |

### SSH 免密配置

在服务器本地生成部署专用密钥对（如已有可跳过）：

```bash
ssh-keygen -t ed25519 -C "FastBrace-docs-deploy" -f ~/.ssh/docs_deploy_key
```

将公钥添加到服务器的 `~/.ssh/authorized_keys`：

```bash
ssh-copy-id -i ~/.ssh/docs_deploy_key.pub deploy@your-server
```

然后将私钥内容（`~/.ssh/docs_deploy_key`）填入 GitHub Secret `DOCS_DEPLOY_KEY`。





## Cloudflare Pages 部署（推荐🌟）

除了自建服务器 + Nginx 的部署方式，还可以使用 [Cloudflare Pages](https://developers.cloudflare.com/pages/)（基于 [VitePress 官方指南](https://developers.cloudflare.com/pages/framework-guides/deploy-a-vitepress-site/)）。

Cloudflare Pages 是 Cloudflare 提供的静态站点托管与持续部署服务，支持从 Git 仓库自动构建与发布，免费额度即可满足文档站需求。域名默认是 `*.pages.dev`，也可以绑定自己的自定义域名。

### 方式一：本地构建，然后上传cloudflare部署

这是目前最推荐的零配置方式，无需在本地安装任何 Cloudflare 相关 CLI 工具。

1. 本地执行make docs-build， 产出的静态资源在docs/.vitepress/dist下
2. 进入cloudflare主页，找到左侧侧边栏 Build，然后选择Build下 Compute --->  Workers &Pages
   1. ![截屏2026-09-07 20.29.52](https://picgocloud.com/m/5272cd20-0dcf-473d-8c5c-de51c04a5fec.png)
3. 点击右上角 Create application，选择Upload your static files
   1. ![截屏2026-09-07 20.31.52](https://picgocloud.com/m/73ce3a72-c71b-47fe-bf56-db4398f9f972.png)
4. 最后选择部署，等待部署结果



### 绑定自定义域名 （可选）

如果部署完文档站以后，想要绑定自己的自定义域名可以采用以下步骤

1. 去云厂商诸如阿里云、腾讯云或者cloudflare中购买域名
2. 在cloudflare侧边栏，找到Domains下Overview，然后点击Add domain新增域名， 按照要求一步步配置
3. 最后获取Cloudflare 分配 NS的两个信息，到云厂商的dns修改中进行修改
4. 

### 配置静态资源缓存（可选）

Cloudflare 默认开启 CDN，可额外通过创建 `docs/.vitepress/dist/_headers` 或在 Cloudflare 控制台配置缓存规则，为静态资源设置长缓存以提升加载速度。



