# 部署指南

本文介绍如何把 FastBrace 脚手架部署到服务器

> 部署完成后，日常发布由流水线自动完成，工作原理见 [CI/CD 流水线说明](./cicd-pipeline)。

## 部署架构

FastBrace 采用「镜像仓库 + Docker Compose」的部署方式：

1. GitHub Actions 把应用构建成 Docker 镜像，推送到阿里云 ACR；
2. 部署文件（`docker-compose.yml` 等）通过 SSH 同步到服务器；
3. 服务器拉取镜像，由 Docker Compose 编排运行。

> [!TIP]
>
> **镜像仓库选用阿里云 ACR 的原因：** 服务器在国内，从 `ghcr.io` 拉取镜像会因网络问题超时取消；ACR 国内节点拉取速度快，通常在 **30 秒内**完成，整体部署控制在 **5-8 分钟**。

服务器上运行的容器（定义在 `deploy/docker-compose.yml`）：

| 容器 | 作用 | 端口 |
| --- | --- | --- |
| `api` | FastAPI HTTP 服务 | 宿主机 `${CONFIG_PORT}` → 容器 `8889` |
| `event-bus` | 事件总线消费进程 | 不暴露端口 |
| `cron_jobs` | 定时任务进程 | 不暴露端口 |
| `dozzle` | 轻量日志查看器，浏览器打开即可搜索 / 过滤 / 实时查看容器日志 | 宿主机 `${DOZZLE_PORT:-8890}` → 容器 `8080` |

三个业务容器使用**同一个镜像**（由 `HOUSE_IMAGE` 变量注入），仅启动命令不同；日志分别写入独立的 Docker Volume（`app_log` / `event_log` / `cron_log`，挂载到容器内 `/log/FastBrace/...`）。

服务器目录布局（`DEPLOY_PATH` 例如 `/srv/backend`）：

```
/srv/backend/
├── .env                       # 环境变量文件（流水线从 APP_ENV_VARS 自动写入）
└── deploy/
    └── docker-compose.yml     # Compose 编排文件（流水线自动同步）
```

## 初次配置

### 1. 开通阿里云容器镜像服务（ACR）

访问 [阿里云容器镜像服务](https://cr.console.aliyun.com)，选择**个人版**（免费）：

1. 开通服务后，进入 `实例列表 → 个人实例`
2. 记录镜像仓库地址，格式为 `registry.cn-<地区>.aliyuncs.com`（如 `registry.cn-hangzhou.aliyuncs.com`）
3. 进入 `命名空间`，创建一个命名空间（如 `your-namespace`）
4. 进入 `镜像仓库`，创建仓库，名称填 `backend`（或其他），类型选**私有**
5. 记录或设置登录密码（`访问凭证 → 固定密码`）

> 推荐使用 RAM 子账号并只授予 `AliyunContainerRegistryFullAccess` 权限，避免使用主账号。

### 2. 服务器准备

> [!TIP]
>
> 准备一台服务器，并在服务器上安装好 Docker 环境，以及创建部署目录。

```bash
# 安装 Docker（含 compose 插件）
curl -fsSL https://get.docker.com | sh
# 将部署用户加入 docker 组（重新登录后生效）
sudo usermod -aG docker $USER

# 创建项目和部署目录（服务器不需要应用源码）
sudo mkdir -p  【部署目录】（诸如：/srv/backend/deploy）
sudo chown $USER:$USER /srv/backend

# 将 Compose 文件上传到服务器
将 docker-compose 文件上传到服务器部署目录
```

> 无需在服务器手动登录 ACR，流水线每次部署时会自动登录。首次使用流水线部署时，`上传部署文件` job 也会自动创建目录并同步 compose 文件。

### 3. GitHub 仓库配置

**创建 Environment：**

`仓库 Settings → Environments → New environment`，名称填 `production`。

建议在 `Deployment branches and tags` 中选择 `Selected branches`，只允许 `main` 分支触发部署。

**在 `production` Environment 中添加以下 Secrets：**

> ⚠️ 所有 Secret 必须放在 `production` Environment secrets 中，流水线的 job 均声明了 `environment: production`，都能读取到。

| Secret                   | 必填 | 说明                                             |
| ------------------------ | ---- | ------------------------------------------------ |
| `DEPLOY_HOST`            | ✅   | 服务器 IP 或域名                                 |
| `DEPLOY_PORT`            | 可选 | SSH 端口，不填默认 22                            |
| `DEPLOY_USER`            | ✅   | SSH 登录用户名                                   |
| `DEPLOY_PATH`            | ✅   | 服务器项目目录，如 `/srv/backend`                |
| `DEPLOY_SSH_PRIVATE_KEY` | ✅   | SSH 私钥完整内容（含首尾行）                     |
| `ACR_REGISTRY`           | ✅   | ACR 地址，如 `registry.cn-hangzhou.aliyuncs.com` |
| `ACR_NAMESPACE`          | ✅   | ACR 命名空间，如 `your-namespace`                |
| `ACR_REPO`               | 可选 | ACR 仓库名，不填默认 `backend`                   |
| `ACR_USERNAME`           | ✅   | 主账号登录名，或 RAM 子账号格式 `user@主账号ID`  |
| `ACR_PASSWORD`           | ✅   | 阿里云登录密码或固定密码                         |
| `APP_ENV_VARS`           | ✅   | 应用所有生产环境变量（多行文本，见下方说明）     |

**生成部署 SSH key：**

```bash
ssh-keygen -t ed25519 -C "github-actions" -f ./deploy_key -N ""
cat ./deploy_key        # 私钥 → 填入 DEPLOY_SSH_PRIVATE_KEY
cat ./deploy_key.pub    # 公钥 → 追加到服务器 ~/.ssh/authorized_keys
```

## 参数说明

### `APP_ENV_VARS` 环境变量

应用所有生产环境变量写在**一个** secret 里（多行文本），流水线部署时会将其写入服务器的 `$DEPLOY_PATH/.env`：

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

各变量说明：

| 变量 | 说明 |
| --- | --- |
| `ENV` | 运行环境，生产必须设为 `prod`（影响日志写入路径等行为） |
| `HOUSE_IMAGE` | 随机标识（必填） |
| `CONFIG_PORT` | `api` 服务映射到宿主机的端口；流水线健康检查默认访问 `8888`，建议保持 `8888`，并与反向代理 / 防火墙规则一致 |
| `JWT__SECRET_KEY` | JWT 签名密钥 |
| `DB__HOST` / `DB__USERNAME` / `DB__PASSWORD` / `DB__DATABASE` | 数据库连接信息 |
| `REDIS_DB__HOST` / `REDIS_DB__PASSWORD` | Redis 连接信息 |
| `OBJECT_STORAGE__ACCESS_KEY` / `OBJECT_STORAGE__SECRET_KEY` | 对象存储（OSS）密钥 （如不需要配置数据，为空即可） |

每次迭代如需修改环境变量，只需更新该 secret，重新触发 workflow 即可。

### Compose 变量

`deploy/docker-compose.yml` 中还引用了以下变量：

| 变量 | 说明 |
| --- | --- |
| `HOUSE_IMAGE` | 三个业务容器（`api` / `event-bus` / `cron_jobs`）共用的镜像地址，由流水线在 `docker compose up` 时注入 |
| `CONFIG_PORT` | `api` 服务宿主机端口，容器内固定监听 `8889` |
| `DOZZLE_PORT` | `dozzle` 日志查看器宿主机端口，默认 `8890`，浏览器访问 `http://服务器IP:8890` |



## 日志查看镜像加速（国内）

参考开源项目： https://github.com/DaoCloud/public-image-mirror



日志查看工具 `dozzle` 的镜像 `amir20/dozzle` 托管在 `docker.io`，国内服务器直连拉取可能超时。参考 [DaoCloud public-image-mirror](https://github.com/DaoCloud/public-image-mirror) 项目，将镜像地址替换前缀为 `docker.m.daocloud.io/xxx`，即可经国内节点加速拉取，镜像 hash 与源站完全一致。

**镜像对应关系（`docker.io` → `docker.m.daocloud.io`）：**

| compose 中的原始镜像        | 国内加速地址                                     |
| --------------------------- | ------------------------------------------------ |
| `amir20/dozzle:latest`      | `docker.m.daocloud.io/amir20/dozzle:latest`      |

### 方式一：配置 Docker 镜像加速器（推荐，无需改 compose）

在服务器上编辑 `/etc/docker/daemon.json`（文件不存在则新建）：

```json
{
  "registry-mirrors": ["https://docker.m.daocloud.io"]
}
```

重启 Docker 生效：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

> 配置后 `docker.io` 的镜像（含 `amir20/dozzle`）自动经国内节点加速，`deploy/docker-compose.yml` 无需修改。注意 `registry-mirrors` 只对 `docker.io` 生效，业务镜像走 ACR 不受影响。

### 方式二：手动拉取并重打标签

不改动服务器 Docker 配置时，可经加速地址拉取后改回原标签，compose 会直接使用本地镜像：

```bash
docker pull docker.m.daocloud.io/amir20/dozzle:latest
docker tag docker.m.daocloud.io/amir20/dozzle:latest amir20/dozzle:latest
```

### 方式三：直接修改 compose 镜像地址

将 `deploy/docker-compose.yml` 中 `dozzle` 的镜像字段替换为加速地址，并同步更新服务器 `DEPLOY_PATH/deploy` 目录下的 compose 文件：

```yaml
  dozzle:
    image: docker.m.daocloud.io/amir20/dozzle:latest
```

### 使用注意

1. 加速服务状态可查看 [DaoCloud 服务状态页](https://status.daocloud.io/status/docker)；拉取报 `toomanyrequests` 说明触发限流，稍后重试即可



## 部署后验证与排查命令

```bash
# 查看服务状态
docker compose -f /srv/backend/deploy/docker-compose.yml ps

# 查看日志
docker compose -f /srv/backend/deploy/docker-compose.yml logs --tail=100 api
docker compose -f /srv/backend/deploy/docker-compose.yml logs --tail=100 event-bus cron_jobs

# 健康检查
curl -i http://127.0.0.1:8888/health

# 手动清理旧镜像
docker image prune -af
```



## 磁盘空间管理

每次部署自动执行：

1. `docker image prune -f`：清理悬空镜像
2. 保留最近 2 个版本，删除更旧的

磁盘告急时手动执行：

```bash
docker image prune -af
```



## 常见问题

**Q: 部署阶段出现 `no configuration file provided: not found`**

配置的 `DEPLOY_PATH` 目录下没有 `docker-compose.yml` 文件。正常情况下流水线的 `上传部署文件` job 会自动同步；若手动部署，需要将该文件放置到服务器 `DEPLOY_PATH/deploy/` 目录下。

**Q: 部署阶段 `docker pull` 超时取消**

已改用阿里云 ACR，国内拉取速度正常。如仍超时，检查 ACR 地域是否与服务器同区（如服务器在杭州，ACR 选 `cn-hangzhou`）。

**Q: `docker pull` 报 `unauthorized`**

检查 `ACR_USERNAME` / `ACR_PASSWORD` 是否正确，或 ACR 仓库是否为私有且账号有权限。

**Q: 日志查看容器（dozzle）启动失败，提示拉取镜像超时**

`amir20/dozzle` 镜像来自 `docker.io`，国内直连拉取容易超时。参见上文「日志查看镜像加速（国内）」章节：配置 Docker 镜像加速器（方式一），或经 `docker.m.daocloud.io` 手动拉取后重打标签（方式二）。

**Q: SSH 连接失败 `Permission denied (publickey)`**

1. `DEPLOY_SSH_PRIVATE_KEY` 填的是私钥（不是 `.pub` 文件）且内容完整
2. 对应公钥已追加到服务器 `~/.ssh/authorized_keys`
3. 服务器 `~/.ssh` 权限为 `700`，`authorized_keys` 权限为 `600`
4. 本机验证：`ssh -i ./deploy_key -p 22 user@server "whoami"`

**Q: 健康检查超时**

查看 api 容器启动日志：

```bash
docker compose -f /srv/backend/deploy/docker-compose.yml logs --tail=100 api
```

常见原因：数据库连接失败、`APP_ENV_VARS` 中配置有误。此外注意 `APP_ENV_VARS` 中 `CONFIG_PORT` 需与服务实际监听端口、流水线健康检查访问的端口保持一致。
