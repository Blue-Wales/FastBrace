# 角色管理

FastBrace 内置了基于**树形结构**的角色管理，支持角色的层级关系、角色与用户的多对多关联。

## 核心概念

- **角色树**：角色支持父子层级关系
- **角色 CRUD**：创建、编辑、删除角色，获取角色详情
- **角色-用户关联**：支持将用户添加到角色、从角色中移除用户，以及查询角色下的用户列表
- **角色切换**：用户可在登录时选择角色，或登录后动态切换



## 文件位置

| 文件 | 说明 |
|------|------|
| `api/role.py` | 角色管理 API 路由 |
| `api/request_body/role_request.py` | 角色请求体 |
| `api/response_model/role_res_model.py` | 角色响应模型 |
| `application/role_app.py` | 角色应用服务层 |
| `domain/service/role_service.py` | 角色领域服务 |
| `domain/entity/role.py` | 角色实体 |
| `domain/repo/role_repo.py` | 角色仓储实现 |
| `infrastructure/models/role.py` | 角色数据库模型 |
| `db/create_roles_table.sql` | 角色表建表 SQL |
| `db/create_role_closure_table.sql` | 角色闭包表建表 SQL |



## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/role/add` | 添加角色（需管理员权限） |
| GET | `/role/tree` | 获取角色树 |
| POST | `/role/edit` | 编辑角色（需管理员权限） |
| POST | `/role/user_list` | 获取角色关联的用户列表 |
| GET | `/role/info` | 获取角色信息 |
| DELETE | `/role/delete` | 删除角色（需管理员权限） |
| POST | `/role/add_users` | 添加用户到角色（需管理员权限） |
| DELETE | `/role/delete_users` | 从角色中移除用户（需管理员权限） |
