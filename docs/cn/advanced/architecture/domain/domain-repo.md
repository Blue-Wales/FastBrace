# 领域仓储设计指南

本文档说明 `domain/repo/` 的职责边界、目录结构与编写约定。

## 职责边界

仓储**只做数据库操作**：CRUD、批量写入。该领域不写业务规则、不做权限判断、不跨领域组合数据。

- 业务规则在实体与领域服务中；
- 仓储的核心就是操作数据库"。



## 目录结构

```text
domain/repo/
├── base.py                      # 抽象基类：实体/ORM 互转与通用能力
├── interfaces/                  # 仓储接口（进行抽象）
│   ├── base.py                  # IBaseRepository：通用批量抽象
│   ├── user.py                  # IUserRepository：用户持久化抽象
│   ├── role.py                  # IRoleRepository：角色与闭包表抽象
│   ├── file.py                  # IFileRepository：文件存储抽象
│   └── permission_resource.py   # IPermissionResourceRepository：权限资源抽象
├── user_repo.py                 # UserRepository：SQLAlchemy 实现
├── role_repo.py                 # RoleRepository：闭包表实现
├── file_repo.py                 # FileRepository：附件读写实现
└── permission_resource_repo.py  # PermissionResourceRepository：权限资源实现
```

## 抽象基类（base.py）

`BaseRepository` 提供所有仓储共享的通用能力：

- `_to_entity(orm_obj, entity)`：查询结果 → 领域实体（`model_validate`）；
- `_to_model(model, entity)`：实体 → ORM 模型（按表字段裁剪）；
- `batch_upsert(model, data_list, on_duplicate_key_list)`：MySQL `ON DUPLICATE KEY` 批量写入。

实现类继承它，只补充本模块的专属查询方法即可。



## 接口与实现分离（interfaces/）

`interfaces/` 定义领域层依赖的**持久化契约**（`Protocol`），是稳定边界：

- 接口只描述领域需要的读写能力，不暴露 SQL、表结构、Session 等实现细节；
- 调用方（应用服务、领域服务）依赖接口类型，工厂返回实现类；
- 新增查询方法时，接口与实现必须同步更新，并保持签名一致。



## 编写约定

- 每个实现类用 `@repository_factory.autowire("{module}_repo", scope=BeanScope.PROTOTYPE.value)` 注册；
- 查询方法返回领域实体或值对象，不直接返回 ORM 对象；
- 只做数据库操作，禁止在仓储内写业务判断。



## 新增仓储的流程

1. `domain/repo/interfaces/{module}.py` 定义契约（方法签名 + 文档）；

1. `domain/repo/{module}_repo.py` 继承 `BaseRepository` 实现；

1. 用 `autowire` 注册，并加入 `infrastructure/core/app.py` 的 `auto_load_modules` 预加载列表（若需启动时注册）；

   
