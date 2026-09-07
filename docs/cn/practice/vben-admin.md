# 对接 vben-vue-admin

FastBrace 的定位是**可对接任意前端**的后台服务框架，本文以开源前端方案 [vben-vue-admin](https://github.com/vbenjs/vue-vben-admin)（Vue 3 + Ant Design Vue + Vite）为例，介绍完整的前后端联调方案：登录认证、RSA 密码加密、权限对接与部署。

## 整体架构

```text
浏览器
  └── vben-vue-admin（前端，Vite DevServer / Nginx）
        └── HTTP API（REST + JSON，Bearer Token）
              └── FastBrace（后端，Uvicorn）
                    ├── MySQL（业务数据）
                    └── Redis（缓存 / 登录态）
```

前后端完全解耦：开发期通过 Vite 代理转发接口，生产环境由 Nginx 统一反代，避免跨域问题。

## 准备工作

| 依赖     | 版本                     | 说明                          |
| -------- | ------------------------ | ----------------------------- |
| Node.js  | 18+（建议 20+）          | 前端构建环境                  |
| pnpm     | 8+                       | vben 推荐的包管理器           |
| 后端环境 | 见[快速开始](/intro/getting-started) | MySQL / Redis / uv |

## 第 1 步：启动 FastBrace

```bash
# 1. 初始化数据库（执行 db/ 目录下的建表 SQL）
# 2. 启动后端服务
python main.py server api
```

启动后访问 `http://127.0.0.1:8000/docs` 确认 Swagger 文档可用。

> 后端 CORS 中间件默认 `allow_origins=["*"]`，本地联调不会被跨域拦截；生产环境建议按域名收紧，或直接走 Nginx 同域反代（见下文部署）。

## 第 2 步：配置前端接口地址

克隆并启动 vben-vue-admin：

```bash
git clone https://github.com/vbenjs/vue-vben-admin.git
cd vue-vben-admin
pnpm install
pnpm serve
```

修改 `.env.development`，将接口地址指向 FastBrace（以 vben 2.x 目录结构为例）：

```ini
# .env.development
VITE_GLOB_API_URL=/api
```

并在 `vite.config.ts`（或 `build/vite/proxy.ts`）中配置代理，把 `/api` 转发到后端并去掉前缀：

```ts
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
    ws: false,
  },
},
```

> vben 不同版本的配置文件位置略有差异（2.x 在 `build/vite/proxy.ts`，5.x 为 monorepo 结构），以官方文档为准；核心都是「前端请求 `/api/**` → 代理转发到 FastBrace 根路径」。

## 第 3 步：对接登录认证

FastBrace 使用**标准 OAuth2 密码模式**签发 JWT：

```text
POST /login        Content-Type: multipart/form-data
  username=xxx
  password=xxx     # 可选：RSA 加密后的密文
  role_id=1        # 可选：多角色用户选择登录角色

响应：
{
  "access_token": "...",
  "refresh_token": "...",
  "code": 200
}
```

前端适配要点：

1. **登录请求**：vben 的登录 API 默认是 JSON 请求体，需要在 `src/api/sys/user.ts` 中改为 `form-data` 提交，或直接使用 axios 的 `URLSearchParams`；
2. **令牌携带**：后续请求在请求头加 `Authorization: Bearer <access_token>`（vben 默认即为 Bearer 方案）；
3. **令牌刷新**：`access_token` 过期后，调用 `POST /refresh-token`（`form-data` 传入 `refresh_token`）获取新令牌并更新本地存储；
4. **多角色切换**：FastBrace 提供 `/switch-role` 接口，可在 vben 首页挂一个「切换角色」入口，实现一套账号多角色切换。

登录成功后，前端调用 `GET /users/me` 获取当前用户资料与角色信息，填充 vben 的用户状态；退出登录时调用 `POST /logout` 撤销令牌。

### 可选：开启 RSA 密码加密

如果后端配置了 RSA（见 [加密通信](/advanced/encryption)），登录流程为：

```text
1. GET /security/public-key   →  获取 public_key 与 fingerprint
2. 前端用 jsencrypt 以公钥加密密码（RSA-OAEP-SHA256）
3. POST /login 提交密文
```

FastBrace 提供了开箱即用的前端加密集成方案（详见 [加密通信](/advanced/encryption)#第三步-前端集成)），可直接在 vben 的登录模块中使用 jsencrypt 加密密码，在加密开关关闭时自动回退为明文提交。

## 第 4 步：对接权限与菜单

vben 支持两种菜单模式，可按团队习惯选择：

| 模式         | 菜单来源                       | 适合场景                       |
| ------------ | ------------------------------ | ------------------------------ |
| 前端模式     | vben 本地路由表                | 快速起步，菜单固定             |
| 后端模式     | 登录后从接口拉取菜单树         | 菜单随角色动态变化（推荐）     |

采用后端模式时，将 FastBrace 的权限接口映射为 vben 约定的菜单接口即可：

- FastBrace：`GET /permissions/tree`（权限树）、`GET /permissions/role/{role_id}`（角色权限树）、`GET /permissions/user/detailed`（当前用户细粒度权限）；
- 在后端返回与 vben `getMenuList` 结构兼容的菜单 JSON（`meta.title`、`path`、`icon` 等字段），或在 vben 侧做一次字段转换。

接口级权限的控制方式见[权限系统](/advanced/permission)——后端通过权限装饰器校验，前端用 vben 的 `RoleEnum` / 按钮权限指令控制按钮显隐，两端使用同一套权限编码。

## 第 5 步：业务模块联调

登录打通后，业务模块按「一后端模块 + 一前端页面」的方式推进：

1. 后端：按 [架构指南](/advanced/architecture/api-layer) 或 [Skill](/advanced/engineering/skill) 生成模块接口；
2. 前端：在 vben `src/api/` 下按模块封装请求，页面复用其表格、表单组件；
3. 联调：打开 Swagger（`/docs`）与前端页面并行验证，或让 AI 通过 MCP 自动验证（见 [MCP](/advanced/engineering/mcp)）。

文件上传、Excel 导入导出等通用能力，后端已内置对应接口，前端按普通表单流对接即可。

## 第 6 步：部署上线

生产环境推荐 Nginx 同域反代，规避跨域与 Cookie 问题：

```nginx
server {
    listen 80;
    server_name admin.example.com;

    # 前端静态资源（vben 构建产物）
    location / {
        root /var/www/vben-dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反代
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

后端容器化部署见[部署指南](/advanced/engineering/deployment-guide)，自动化发布流程见 [CI/CD 流水线说明](/advanced/engineering/cicd-pipeline)。

## 常见问题

### 1. 登录返回 422

FastBrace 登录接口使用 `form-data`（OAuth2 规范），前端若以 JSON 提交会触发参数校验失败。确认请求头为 `multipart/form-data`。

### 2. 接口返回 401

检查请求头是否携带 `Authorization: Bearer <access_token>`；令牌过期需先刷新；开发期也常因 Vite 代理未生效导致请求打到前端自身端口。

### 3. RSA 解密失败

后端报「RSA解密失败」说明提交的不是有效密文：确认先调用了 `/security/public-key`，且使用的是**当前后端实例**的公钥（重启后端并更换密钥对后，旧公钥缓存会失效）。

### 4. 权限按钮不显示

后端权限树中的权限编码需要与前端 vben 配置的角色/按钮编码完全一致，注意大小写与下划线。

## 下一步

- 后端权限模型详解：[权限系统](/advanced/permission)
- 用 AI 加速前后端联调：[Skill](/advanced/engineering/skill)、[MCP](/advanced/engineering/mcp)
