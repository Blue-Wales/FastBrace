# 用户管理

FastBrace 提供了开箱即用的用户管理模块，涵盖用户的增删改查、密码管理、状态控制等完整功能。



## 核心概念

- **用户 CRUD**：支持创建、编辑、删除用户，以及分页查询用户列表
- **密码管理**：支持用户自行修改密码和管理员重置密码，密码使用 bcrypt 哈希存储
- **状态控制**：支持批量启用/禁用用户账号
- **头像管理**：用户可关联头像文件，通过文件模块上传



## 文件位置

| 文件 | 说明 |
|------|------|
| `api/user.py` | 用户管理 API 路由 |
| `api/request_body/user_request.py` | 用户请求体 |
| `api/response_model/user_res_model.py` | 用户响应模型 |
| `application/user_app.py` | 用户应用服务层 |
| `domain/service/user_service.py` | 用户领域服务 |
| `domain/entity/user.py` | 用户实体 |
| `domain/repo/user_repo.py` | 用户仓储实现 |
| `infrastructure/models/user.py` | 用户数据库模型 |



## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/users` | 新增用户（需管理员权限） |
| GET | `/users` | 获取用户列表 |
| GET | `/users/me` | 获取当前登录用户信息 |
| GET | `/users/choices` | 获取用户名称列表（下拉选择用） |
| GET | `/users/{user_id}` | 获取用户详细信息 |
| POST | `/users/{user_id}` | 编辑用户 |
| DELETE | `/users/{user_id}` | 删除用户（需管理员权限） |
| POST | `/users/me/password` | 修改当前用户密码 |
| POST | `/users/{user_id}/password` | 修改指定用户密码 |
| POST | `/users/batch/status` | 批量修改用户状态（需管理员权限） |

