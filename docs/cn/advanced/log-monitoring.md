# 日志监控

本文介绍如何在生产环境**快速查看**各个服务的日志，目前FastBrace采用**Dozzle** 作为线上日志查看工具。



##  **Dozzle** 优势

- **零配置**：自动发现 Docker 容器日志，无需写采集规则
- **轻量**：单个容器、约 10MB 内存，不占用业务资源
- **即用**：浏览器打开即可搜索、过滤、实时滚动查看所有服务日志
- **无需改代码**：日志直接输出到容器 stdout/stderr，Dozzle 读取 Docker 日志驱动即可
- 

## 前置条件

FastBrace 的日志在所有环境（含生产）均同时输出到**本地文件**和**容器 stderr**（见 `infrastructure/core/log.py`）。容器 stderr 的日志由 Docker 日志驱动收集，Dozzle 通过 `/var/run/docker.sock` 读取。

## 1. Dozzle 部署

`deploy/docker-compose.yml` 已内置 `dozzle` 服务，与业务服务一起启动即可：

```yaml
  dozzle:
    image: amir20/dozzle:latest
    restart: unless-stopped
    ports:
      - "${DOZZLE_PORT:-8890}:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```



部署好后，打开浏览器访问 `http://<服务器IP>:8890` 即可直接查看所有容器日志，无需登录。

> 默认无认证。请通过防火墙限制 `8890` 端口仅对内网或可信 IP 开放。如需账号密码认证，参见下文「配置访问认证」。



### 配置访问认证（可选）

Dozzle v10 不再支持通过环境变量配置账号密码，需挂载 `users.yaml` 文件。

1. 在 `deploy/` 目录下创建 `dozzle-users.yaml`：

```yaml
users:
  - name: admin
    password: <bcrypt 加密后的密码>
```

2. 生成 bcrypt 密码（服务器上执行）：

```bash
docker run --rm amir20/dozzle:latest generate password "你的密码"
```

3. 修改 `deploy/docker-compose.yml`，挂载该文件：

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



## 2. 使用 Dozzle 查看日志

登录后左侧会列出所有容器（api、event-bus、cron_jobs、dozzle 等），点击任意容器即可查看：

- **实时滚动**：新日志自动追加到页面底部
- **关键字搜索**：顶部搜索框输入关键字，支持正则
- **级别过滤**：按 `INFO` / `WARNING` / `ERROR` 等过滤
- **时间跳转**：跳到指定时间点的日志
- **多容器合并**：可同时选中多个容器，合并查看日志流



## 3. 命令行方式（无需 Web）

如果只想用命令行看日志，直接用 `docker compose logs`：

```bash
# 实时查看所有服务
docker compose -f deploy/docker-compose.yml logs -f

# 只看 api 服务最近 200 行
docker compose -f deploy/docker-compose.yml logs -f --tail=200 api

# 同时看 api 和 event-bus
docker compose -f deploy/docker-compose.yml logs -f api event-bus

# 只看错误级别（grep 过滤）
docker compose -f deploy/docker-compose.yml logs api | grep -E "ERROR|CRITICAL"
```



## 4. Dozzle 运维命令

以下命令均在项目根目录下执行，假设 compose 文件为 `deploy/docker-compose.yml`。

### 启停与重启

```bash
# 启动 dozzle
docker compose -f deploy/docker-compose.yml up -d dozzle

# 停止 dozzle
docker compose -f deploy/docker-compose.yml stop dozzle

# 重启 dozzle（配置变更后执行）
docker compose -f deploy/docker-compose.yml restart dozzle

# 重新创建 dozzle 容器（修改 compose 后执行，等价于 stop + rm + up）
docker compose -f deploy/docker-compose.yml up -d --force-recreate dozzle
```

### 状态与日志

```bash
# 查看 dozzle 运行状态
docker compose -f deploy/docker-compose.yml ps dozzle

# 查看 dozzle 自身日志（排查启动失败）
docker compose -f deploy/docker-compose.yml logs dozzle --tail=50

# 实时跟踪 dozzle 日志
docker compose -f deploy/docker-compose.yml logs -f dozzle
```

### 端口与连通性检查

```bash
# 确认 8890 端口已监听
ss -tlnp | grep 8890

# 本机直连测试（绕过 nginx，判断是 dozzle 问题还是反代问题）
curl -sI http://localhost:8890 | head -5

# 测试页面是否返回 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:8890
```



## 5. 结构化日志说明

FastBrace 文件日志启用了 Loguru 的 `serialize=True`（见 `infrastructure/core/log.py`），每条日志为单行 JSON，便于后续业务扩展后接入更重的日志平台（如 ELK）时按字段解析。容器 stdout 输出为纯文本格式，方便直接阅读。

主要字段：

| 字段 | 说明 |
|------|------|
| `record.level.name` | 日志级别 |
| `record.name` | 日志来源模块 |
| `record.time.repr` | 日志时间 |
| `record.extra.request_id` | 请求 ID |
| `text` | 人类可读的格式化消息 |



## 关键实践与注意事项

- **脱敏**：密码、Token、AccessKey、手机号、身份证等敏感信息严禁写入日志
- **保留策略**：Docker json-file 日志驱动默认不限制大小，建议在 `daemon.json` 中配置 `max-size` 和 `max-file`，避免磁盘占满
- **端口安全**：Dozzle 直接读取 docker.sock，权限较高，务必通过防火墙限制访问来源；如需公网访问，请配置「访问认证」
- **时区**：日志使用本地时区（`Asia/Shanghai`），Dozzle 默认按容器时区展示
- **日志量控制**：生产环境保持 `INFO` 级别，避免 DEBUG 拖慢写入并放大存储成本



## 扩展说明

> [!TIP]
>
> 如果后续业务体量存在一定规模，最好采用阿里云 SLS等官方日志维护平台，免运维操作

