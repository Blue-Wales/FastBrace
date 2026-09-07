# CI/CD 流水线说明

本文介绍 FastBrace 的 CI/CD 流水线：什么是流水线、它有什么作用、FastBrace 的流水线是如何配置的，以及流水线运行过程中的常见问题。

> 第一次部署请先阅读[部署指南](./deployment-guide)，完成服务器、镜像仓库与 GitHub Secrets 的初始配置。

## 什么是流水线

CI/CD（持续集成 / 持续部署）流水线是一段在代码仓库中声明式定义、由平台自动执行的发布流程。FastBrace 使用 **GitHub Actions**，流水线定义在仓库的 `.github/workflows/main.yml` 文件中。

流水线的作用：

1. **一键发布**：代码合并到 `main` 后，在 GitHub 页面手动触发一次 workflow，构建镜像、推送仓库、同步部署文件、重启服务、健康检查全部自动完成，无需登录服务器手工操作。
2. **环境一致**：应用及其全部依赖打包进同一个 Docker 镜像，构建与生产运行的环境完全一致，避免「本地能跑、线上不行」。
3. **版本可追溯**：每次发布的镜像以流水线运行序号 `run-N` 打标签，线上运行的镜像与 GitHub Actions 运行记录一一对应，出问题可快速定位、回滚。
4. **发布即验证**：部署后自动轮询健康检查接口，失败会打印容器日志并让流水线失败，第一时间暴露问题。
5. **自动清理**：每次部署自动清理悬空镜像与旧版本镜像，避免服务器磁盘被占满。

## 流水线概览

FastBrace 的流水线名为 `backend-ci-cd`，包含三个 job：

```
build-and-push（构建并推送镜像） ┐
                                ├──> deploy（部署生产环境）
upload-deploy-files（上传部署文件）┘
```

| Job | 作用 | 与其他 job 的关系 |
| --- | --- | --- |
| `build-and-push` | 在 GitHub runner 上构建 Docker 镜像并推送到阿里云 ACR | 与 upload 并行执行 |
| `upload-deploy-files` | 通过 SSH 把 `deploy/` 目录（compose 文件等）同步到服务器 | 与 build 并行执行 |
| `deploy` | SSH 登录服务器，拉取新镜像、重启服务、执行健康检查 | 必须等前两个 job 都成功 |

涉及三方协作：

- **GitHub Actions runner**：执行构建与推送（GitHub 提供的临时 Ubuntu 环境）；
- **阿里云 ACR**：存放 Docker 镜像的私有镜像仓库；
- **生产服务器**：通过 SSH 接收部署文件、拉取镜像，并用 Docker Compose 运行服务。

## 流水线配置详解

流水线完整定义见仓库文件 `.github/workflows/main.yml`。

### 触发方式与并发控制

```yaml
on:
  workflow_dispatch:

concurrency:
  group: backend-production-deploy
  cancel-in-progress: false
```

- `workflow_dispatch`：**手动触发**，不随 push / PR 自动执行。发布时在仓库 `Actions` 页面点击 `Run workflow`。
- `concurrency`：同一时间只允许一个生产部署；`cancel-in-progress: false` 表示新触发的流水线会**排队等待**，而不是取消正在进行的部署，避免两次部署互相打断。
- 三个 job 都声明了 `environment: production`，统一受 GitHub Environment 保护规则约束（可限制只有 `main` 分支、甚至需要人工审批才能运行），所有密钥也集中配置在 `production` 环境中。
- 每个 job 都设置了 `timeout-minutes`，防止异常时长时间占用 runner。

### Job 1：build-and-push（构建并推送镜像）

| 步骤 | 说明 |
| --- | --- |
| `actions/checkout@v4` | 拉取 `main` 分支代码 |
| 生成镜像名 | 拼接镜像地址：`<ACR_REGISTRY>/<ACR_NAMESPACE>/<ACR_REPO，默认 backend>:run-<运行序号>` |
| `docker/login-action@v3` | 使用 `ACR_USERNAME` / `ACR_PASSWORD` 登录阿里云 ACR |
| `docker/setup-buildx-action@v3` | 启用 Buildx（BuildKit 构建器） |
| `docker/build-push-action@v6` | 按 `deploy/Dockerfile` 构建镜像并推送 |

构建步骤的关键配置：

- `context: .` + `file: deploy/Dockerfile`：构建上下文为仓库根目录，Dockerfile 位于 `deploy/` 下。
- 镜像标签形如 `...:run-<运行序号>`：标签使用 GitHub Actions 运行序号（`github.run_number`），全局单调递增，保证每次发布的镜像标签唯一。
- `provenance: false` / `sbom: false`：关闭 provenance / sbom 证明附件。否则 BuildKit 会推送 OCI 索引清单，其中包含 `application/vnd.oci.empty.v1+json` 空描述符，阿里云 ACR 个人版不识别，会报 `unknown manifest class`。
- `cache-from: type=gha` / `cache-to: type=gha,mode=max`：利用 GitHub Actions 缓存复用 Docker 构建层。依赖未变更时，构建可从首次的 8-12 分钟缩短到 1-2 分钟。
- job 声明 `permissions: contents: read`、`packages: write`，遵循最小权限原则。

### Job 2：upload-deploy-files（上传部署文件）

服务器上不需要应用源码，但需要 Docker Compose 文件等运行时配置。该 job 执行：

1. **配置 SSH**：写入 `DEPLOY_SSH_PRIVATE_KEY` 私钥（权限 `600`），通过 `ssh-keyscan` 把服务器指纹写入 `known_hosts`，防止中间人攻击。
2. **创建部署目录**：在服务器上创建 `$DEPLOY_PATH/deploy`。

   > compose 文件中通过 `env_file: ../.env` 引用环境变量文件，因此 compose 文件必须位于 `$DEPLOY_PATH/deploy/` 下，`.env` 位于 `$DEPLOY_PATH/.env`。

3. **通过 SSH 管道同步 `deploy/` 目录**：

   ```bash
   tar -C deploy --exclude='Dockerfile*' --exclude='deploy.sh' -czf - . \
     | ssh ... "tar -C '$DEPLOY_PATH/deploy' -xzf -"
   ```

   只同步 compose 运行所需文件，排除 `Dockerfile`（仅构建时使用，服务器不需要）和 `deploy.sh`（本地调试脚本）。

### Job 3：deploy（部署生产环境）

通过 `needs: [build-and-push, upload-deploy-files]` 确保镜像已推送、部署文件已同步后才执行。随后 SSH 登录服务器依次执行：

1. **登录 ACR**：`docker login`，使服务器有权限拉取私有镜像；
2. **写入环境变量**：`APP_ENV_VARS` 先在 runner 上 base64 编码，传到服务器后再解码写入 `$DEPLOY_PATH/.env`，避免多行文本与特殊字符在 SSH 传输中被转义破坏；
3. **拉取新镜像**：`docker pull <镜像>:run-N`；
4. **停止旧服务**：`docker compose down --remove-orphans`（通过 `HOUSE_IMAGE` 环境变量把新镜像地址传给 compose）；
5. **清理旧镜像**：`docker image prune -f` 清理悬空镜像，并删除同一仓库下除最近 2 个版本外的旧镜像；
6. **启动新服务**：`HOUSE_IMAGE=<新镜像> docker compose -f deploy/docker-compose.yml up -d`，启动 `api`、`event-bus`、`cron_jobs`、`dozzle` 四个容器；
7. **健康检查**：轮询最多 20 次、每次间隔 5 秒（共约 100 秒），请求 `http://127.0.0.1:${CONFIG_PORT:-8888}/health`，响应中包含 `"status":"healthy"` 即视为部署成功；超时则打印 `api` 容器最近 50 行日志并让流水线失败。

SSH 连接额外设置了 `ServerAliveInterval=15` / `ServerAliveCountMax=40`，防止拉取大镜像时长连接被断开。

> `deploy/deploy.sh` 是与上述部署流程等价的**本地手动调试脚本**，正式部署由流水线自动完成，无需手动执行。



## 日常发布流程

1. 将代码合并到 `main` 分支
2. 打开仓库 `Actions` → 选择 `backend-ci-cd` → 点击 `Run workflow` → 选择 `main`
3. 等待 `构建并推送镜像`、`上传部署文件` 和 `部署生产环境` 三个 job 全部成功

**预期耗时：**

| 阶段               | 首次     | 有缓存（仅代码变更） | 有缓存（依赖未变更） |
| ------------------ | -------- | -------------------- | -------------------- |
| 构建并推送         | 8-12 min | 3-5 min              | 1-2 min              |
| 部署（含拉取镜像） | 3-5 min  | 2-3 min              | 2-3 min              |



## 回滚

服务器上保留最近 2 个版本的镜像。如需回滚，SSH 登录服务器，将 `HOUSE_IMAGE` 指定为旧版本镜像后重启服务即可：

```bash
cd $DEPLOY_PATH
HOUSE_IMAGE="<ACR_REGISTRY>/<ACR_NAMESPACE>/<backend>:run-<旧序号>" \
  docker compose -f deploy/docker-compose.yml up -d
```



## 常见问题

**Q: 登录阿里云 ACR 步骤失败**

1. 确保 `ACR_USERNAME`、`ACR_PASSWORD`、`ACR_REGISTRY` 均有填写
2. `ACR_USERNAME`：进入 ACR，在「访问凭证」模块复制登录实例下的用户名，一般为阿里云账号登录名
3. `ACR_PASSWORD`：在「访问凭证」模块设置固定密码，然后填写该固定密码
4. `ACR_REGISTRY`：在「访问凭证」模块复制登录实例下用户名后面的地址信息

**Q: 构建阶段出现 `push access denied` 错误**

问题详情：`failed to push xx/xx/xx:run-31: push access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed`

1. `ACR_REGISTRY` 需进入 ACR，在「访问凭证」模块复制登录实例下用户名后面的地址信息
2. 确认 ACR 中已创建对应的命名空间与镜像仓库（默认名 `backend`），且账号有推送权限（推荐使用 RAM 子账号并授予 `AliyunContainerRegistryFullAccess`）

**Q: 推送镜像时报 `unknown manifest class`**

阿里云 ACR 个人版不识别 BuildKit 默认推送的 OCI 索引清单。流水线已设置 `provenance: false`、`sbom: false` 规避；若自行修改构建步骤，请勿重新开启这两个选项。

**Q: SSH 连接失败 `Permission denied (publickey)`**

1. `DEPLOY_SSH_PRIVATE_KEY` 填的是私钥（不是 `.pub` 文件）且内容完整（含首尾行）
2. 对应公钥已追加到服务器 `~/.ssh/authorized_keys`
3. 服务器 `~/.ssh` 权限为 `700`，`authorized_keys` 权限为 `600`
4. 本机验证：`ssh -i ./deploy_key -p 22 user@server "whoami"`

**Q: 部署 job 健康检查超时 / 失败**

健康检查失败说明服务器上的服务未正常启动，常见原因是数据库连接失败、`APP_ENV_VARS` 配置有误、端口不一致等。服务端排查方法见[部署指南 - 常见问题](./deployment-guide#常见问题)。

## 相关文档

- [部署指南](./deployment-guide)：服务器准备、ACR 开通、GitHub Secrets 与环境变量参数说明、部署运维与排查
