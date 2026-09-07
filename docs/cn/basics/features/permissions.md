# 权限系统

FastBrace 提供了基于**资源 + 操作级别**的细粒度权限系统，支持权限树管理、角色权限配置和前端页面访问控制。



## 核心概念

- **权限资源**：以「模块 + 操作」为维度定义权限，如「用户管理-查看」「用户管理-编辑」
- **权限级别**：三级权限体系 —— 查看（Level 1）、操作（Level 2）、导出（Level 3）
- **权限树**：权限资源以树形结构组织，便于角色创建时勾选权限
- **角色-权限绑定**：每个角色关联一组权限配置，以 JSON 格式存储
- **前端访问控制**：提供细粒度权限接口，返回当前用户有权限的页面和操作，供前端动态渲染



## 文件位置

| 文件 | 说明 |
|------|------|
| `api/permission.py` | 权限管理 API 路由 |
| `api/request_body/permission_request.py` | 权限请求体 |
| `api/response_body/permission_response.py` | 权限响应体 |
| `domain/service/permission_service.py` | 权限领域服务 |
| `domain/entity/permission_resource.py` | 权限资源实体 |
| `domain/repo/permission_resource_repo.py` | 权限资源仓储 |
| `infrastructure/models/permission_resources.py` | 权限资源数据库模型 |
| `infrastructure/core/permissions_limit.py` | 权限校验装饰器 |
| `db/create_permission_resources_table.sql` | 权限资源表建表 SQL |



## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/permissions/tree` | 获取权限树 |
| GET | `/permissions/role/{role_id}` | 获取指定角色的权限树 |
| POST | `/permissions/role/save` | 保存角色权限配置 |
| GET | `/permissions/role/{role_id}/detailed` | 获取角色细粒度权限 |
| GET | `/permissions/user/detailed` | 获取当前用户细粒度权限 |
| POST | `/permissions/validate` | 验证用户是否有指定权限 |
| GET | `/permissions/system/info` | 获取权限系统信息 |



## 使用方式

### 接口权限控制

在 API 路由中使用 `require_admin()` 或 `require_permission()` 装饰器：

```python
from infrastructure.core.permissions_limit import require_admin

@user_router.post("", dependencies=[Depends(require_admin())])
async def add_user(...):
    ...
```



### 初始化权限资源

使用脚本初始化权限资源数据：

```bash
python scripts/permission_init.py
```

> 详细的权限系统使用指南请参阅 [进阶 - 权限系统](/advanced/permission)。
