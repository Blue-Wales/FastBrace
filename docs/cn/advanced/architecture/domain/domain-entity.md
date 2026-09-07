# 领域实体设计指南

本文档说明 `domain/entity/` 的实体定义、基类能力与编写约定。



## 实体概述

实体是有**身份标识**（ID）、且**可变**的领域对象。判断标准：

- 对象有独立 ID，且 ID 在生命周期内不变 → 实体；
- 对象无 ID，值相同即相等，不可变 → 值对象（见[值对象文档](domain-value-object)）。

实体承载**自身状态与行为**：例如 `UserEntity.add_attachments()` 绑定附件。行为与数据放在一起，避免贫血模型。



## 实体基类

`domain/entity/base.py` 的 `Entity` 是所有实体的基类：

```python
class Entity(BaseModel):
    """可变的实体基类"""

    entity_id: int = Field(default_factory=SnowflakeIDGenerator())
```

- `entity_id`：雪花算法自动生成；
- `validate_assignment = True`：属性赋值时校验类型；
- 附件能力：`add_attachments` / `get_file_vo_list` / `get_file_vo_empty_list`，统一处理头像、照片等文件字段，与 `FileType` 枚举对应。



## 现有实体

| 文件                            | 实体                                            | 说明                                            |
| ------------------------------- | ----------------------------------------------- | ----------------------------------------------- |
| `entity/user.py`                | `UserEntity`                                    | 用户属性、角色/附件装配、管理员保护             |
| `entity/role.py`                | `RoleEntity`                                    | 角色属性、闭包树、删除前置校验（管理员/子角色） |
| `entity/permission_resource.py` | `PermissionTreeNode` / `DetailedPermissionNode` | 权限树节点，供权限服务组装粗/细粒度权限         |



## 编写约定

- 继承 `Entity`，字段使用 `Field(title="中文名")` 声明，可空字段给出 `default`/`default_factory`；
- 类文档字符串使用简短一句描述（如「角色领域实体」）；



## 新增实体的流程

1. `domain/entity/{module}.py` 继承 `Entity` 定义字段与行为；
1. 若实体有文件类字段，按 `FileType` 枚举命名并在 `infrastructure/models/` 建立对应表；
1. 同步在 `domain/repo/interfaces/` 与 `domain/repo/` 补充仓储契约与实现。
