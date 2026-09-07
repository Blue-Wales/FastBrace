# 应用服务层设计指南

本文档说明 `application/` 层的职责边界、文件结构与用例编排信息。

## 分层定位

`application/` 是 DDD 的应用层，只做**用例编排**：组合领域服务与仓储、管理事务边界、组装响应。领域规则在 `domain/`，HTTP 解析在 `api/`

```text
api/        → 调用 application 层接口（依赖抽象，不依赖实现）
application → 编排 domain 层仓储与服务，返回组装后的响应
```



## 通用文件结构

| 文件          | 职责                                                                |
| ------------- | ------------------------------------------------------------------- |
| `base.py`     | 基类与通用能力：`BaseApplicationService`、`IBaseApplicationService` |
| `user_app.py` | 用户用例：登录 / token / 用户 CRUD / 密码 / 状态 / 角色切换         |
| `role_app.py` | 角色用例：角色 CRUD、角色-用户关系维护                              |
| `file_app.py` | 文件用例：OSS 上传                                                  |



## 注册与获取

应用服务通过装饰器注册为 IoC Bean，由 `infrastructure/core/app.py` 的 `auto_load_modules` 预加载注册：

```python
# application/role_app.py
@application_factory.autowire("role_app_service", scope=BeanScope.PROTOTYPE.value)
class RoleApplicationService(BaseApplicationService):
    ...
```

```python
# infrastructure/core/app.py：新增应用服务需要加入预加载列表
auto_load_modules(base_packages=[
    "application.file_app",
    "application.role_app",
    "application.user_app",
    ...
])
```



## 编写约定

- 继承 `BaseApplicationService`，获得 `generate_response` / `generate_page_response` / `generate_list_response` / `transaction` 通用能力；
- 继承基类的类只需简短描述，不重复基类文档（例如 `UserAppService` 仅写「用户应用服务」）；
- 用例方法返回 `dict`（`data.model_dump()`），由 API 层包装为统一 JSON 响应；
- 异常抛出领域异常（`NotFoundError`、`InvalidInputError` 等），由全局异常处理器统一转换。



## 新增应用服务流程

1. `application/{module}_app.py` 继承 `BaseApplicationService` 实现用例方法；
1. 需要契约边界时声明 `I{Module}AppService(Protocol)` 接口（参照 `IUserAppService`）；
1. 用 `@application_factory.autowire("{module}_app_service", ...)` 注册；
1. 将模块加入 `infrastructure/core/app.py` 的 `auto_load_modules` 预加载列表；
