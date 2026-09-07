# 权限系统

FastBrace 权限系统基于 **「模块 + 操作级别」** 模型设计，通过数据库持久化权限资源、装饰器实现接口级鉴权、初始化脚本一键部署，提供从开发到生产的完整权限管理方案。

## 设计思想

### 权限模型

权限系统采用**两级结构**：

```
模块（Module）          操作（Action）
├── Dashboard           └── 查看
├── UserManage
│   ├── Account         ├── 查看 / 操作 / 导出
│   ├── Role            ├── 查看 / 操作 / 导出
│   └── Department      ├── 查看 / 操作 / 导出
```

- **模块层**：对应业务领域（如用户管理、角色管理），由 `Permissions` 枚举定义
- **操作层**：每个模块下的操作类型，由 `PermissionLevel` 枚举定义三级权限
- **权限存储**：角色的权限以 JSON 格式存储在 `roles.permissions` 字段中，键为模块编码，值为级别数组

### 权限校验流程

```
请求 → OAuth2 Token 解析 → 获取用户权限 → require_permission() 装饰器校验 → 通过/拒绝
```



框架提供四种权限校验方式，适用于不同场景：

| 装饰器 | 用途 | 适用场景 |
|--------|------|----------|
| `require_permission()` | 功能权限校验 | 常规接口（查看/操作/导出） |
| `require_role()` | 角色校验 | 限定特定角色可访问 |
| `require_admin()` | 管理员校验 | 系统管理类操作 |
| `require_permission_expression()` | 表达式权限校验 | 复杂权限组合判断 |



## 核心代码位置

| 文件 | 职责 |
|------|------|
| `infrastructure/core/enum_var.py` | 权限模块枚举 `Permissions` + 权限级别枚举 `PermissionLevel` |
| `infrastructure/core/permissions_limit.py` | 权限校验装饰器（`require_permission`、`require_admin` 等） |
| `infrastructure/models/permission_resources.py` | 权限资源 ORM 模型 |
| `domain/service/permission_service.py` | 权限领域服务（权限树构建、校验逻辑） |
| `api/permission.py` | 权限管理 API 接口 |
| `scripts/permission_init.py` | **权限资源初始化脚本** |
| `db/create_permission_resources_table.sql` | 权限资源表 DDL |



## 配置与初始化

### 第一步：定义权限模块

在 `infrastructure/core/enum_var.py` 中声明权限模块：

```python
class Permissions(Enum):
    DASHBOARD = "Dashboard"
    USER_MANAGE = "UserManage"
    ACCOUNT = "UserManage.Account"
    ROLE = "UserManage.Role"
    DEPARTMENT = "UserManage.Department"

class PermissionLevel(BaseCodeLabelEnum):
    VIEW = (1, "查看")
    EDIT = (2, "操作")
    EXPORT = (3, "导出")
```



### 第二步：运行初始化脚本

框架提供了 `scripts/permission_init.py` 脚本，自动根据权限常量配置生成资源树并写入数据库：

```bash
# 首次初始化（已有数据时跳过）
python scripts/permission_init.py

# 强制清空并重建
python scripts/permission_init.py --force-recreate
```

脚本执行流程：
1. 连接数据库，检查权限资源表是否已有数据
2. 根据 `PERMISSION_MAPPING` 常量递归生成模块 → 操作 → 子模块的权限资源树
3. 批量插入 `permission_resources` 表
4. 为超级管理员角色自动补齐全部权限



### 第三步：在接口上使用权限校验

```python
from fastapi import APIRouter, Depends
from infrastructure.core.enum_var import Permissions, PermissionLevel
from infrastructure.core.permissions_limit import require_permission, require_admin

user_router = APIRouter()

# 需要「用户管理-查看」权限
@user_router.get(
    "",
    dependencies=[Depends(require_permission(
        permission_module=Permissions.ACCOUNT,
        required_permissions=[PermissionLevel.VIEW],
    ))],
)
async def get_users():
    ...

# 需要管理员权限
@user_router.post(
    "",
    dependencies=[Depends(require_admin())],
)
async def create_user():
    ...
```

### 第四步：验证权限配置

通过 API 接口验证权限是否配置正确：

```bash
# 获取权限树
curl -X GET "http://localhost:8000/permissions/tree" \
  -H "Authorization: Bearer <token>"

# 验证指定模块权限
curl -X POST "http://localhost:8000/permissions/validate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_permissions": {...}, "module_code": "UserManage.Account", "required_level": 1}'
```



## 权限数据存储格式

角色权限以 JSON 存储在 `roles.permissions` 字段：

```json
{
    "Dashboard": [1],
    "UserManage.Account": [1, 2, 3],
    "UserManage.Role": [1, 2]
}
```

数字含义：`1` = 查看，`2` = 操作，`3` = 导出。



## 添加新权限模块

1. 在 `infrastructure/core/enum_var.py` 的 `Permissions` 枚举中添加新模块
2. 在权限常量配置中添加对应的 `PERMISSION_MAPPING` 条目
3. 运行 `python scripts/permission_init.py --force-recreate` 重建权限资源
4. 在目标接口上添加 `@require_permission()` 装饰器

