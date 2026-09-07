# 登录认证

FastBrace 内置了完整的认证登录系统，基于 **OAuth2 + JWT** 实现，支持 RSA 加密密码传输和多角色选择。



## 核心概念

- **OAuth2 密码模式**：使用用户名/密码进行认证，服务端签发 JWT Token
- **RSA 加密**：前端传输密码时使用 RSA 公钥加密，后端私钥解密，保障网络安全
- **多角色切换**：登录时可选择角色，登录后支持动态切换角色并刷新 Token
- **Token 刷新**：通过 refresh_token 无感续签 access_token



## 文件位置

| 文件 | 说明 |
|------|------|
| `api/login.py` | 登录认证 API 路由 |
| `api/request_body/user_request.py` | 登录请求体定义 |
| `infrastructure/utils/oauth2_tools.py` | OAuth2 / JWT 工具 |
| `infrastructure/utils/rsa_utils.py` | RSA 加解密工具 |
| `domain/service/user_service.py` | 用户领域服务 |



## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/login` | 用户名密码登录 |
| POST | `/switch-role` | 切换用户角色 |
| GET | `/users/{username}/roles` | 获取用户角色列表 |
| POST | `/refresh-token` | 刷新 Token |
| POST | `/logout` | 退出登录 |
| GET | `/current-role` | 获取当前角色信息 |

