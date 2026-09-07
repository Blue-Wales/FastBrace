# 核心组件设计指南

本文档说明 `infrastructure/core/` 各文件的职责，这是基础设施层的"运行时骨架"。

## 文件职责

| 文件                   | 职责                                                      |
| ---------------------- | --------------------------------------------------------- |
| `app.py`               | FastAPI 应用工厂：创建应用、预加载模块、装配中间件与路由  |
| `settings.py`          | 配置模型：用 Pydantic Settings 从 YAML 加载并校验全部配置 |
| `container.py`         | IoC 容器：Bean 注册（单例/多例）与 `get_bean` 获取        |
| `routers.py`           | 路由注册：按业务域挂载 `APIRouter                         |
| `error_handler.py`     | 异常体系：包含常见的 异常校验和全局异常处理器             |
| `penum_var.py`         | 核心枚举：核心的业务域枚举在此定义，便于业务域和全局引入  |
| `log.py`               | 日志管理器：基于 Loguru 的分模块日志配置                  |
| `middlewares.py`       | 中间件：请求日志、JWT 认证                                |
| `permissions_limit.py` | 权限依赖                                                  |



## 启动装配顺序（app.py）

`create_app(app_settings)` 完成应用初始化：

1. 初始化日志（`init_logger`）；
1. **预加载模块**（`auto_load_modules`）
1. 初始化数据库引擎与会话（`init_database`）、Redis 连接池（`init_cache`）；
1. 装配异常处理器、中间件、路由，并安装 OpenAPI 示例。



## 依赖注入（container.py）

`Container` 支持两种作用域：

- `SINGLETON`：全局共享一个实例；
- `PROTOTYPE`：每次 `get_bean` 创建新实例（用于注入请求级 `db` 会话）。

全局容器实例：`application_factory` / `domain_service_factory` / `repository_factory`，分别管理各层 Bean。



## 异常体系（error_handler.py）

所有业务异常继承 `OrangeCraftException`，`global_exception_handler` 统一转换为标准 JSON 响应：

```text
NotFoundError(404) / PermissionDeniedError(403) / InvalidInputError(400)
        │
OrangeCraftException（status_code）
        │
global_exception_handler → {"code": ..., "message": ...}
```

业务代码抛出领域异常，不必在 API 层重复捕获。



## 中间件（middlewares.py）

- `RequestLogMiddleWare`：记录请求与响应日志；
- `JWTAuthMiddleware`：统一 JWT 认证（`_should_exclude_path` 放行 `/docs`、`/login`、`/health` 等）。

