# Core Components Design Guide

This document describes the responsibilities of each file in `infrastructure/core/` — the "runtime skeleton" of the infrastructure layer.

## File Responsibilities

| File                   | Responsibility                                                                            |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| `app.py`               | FastAPI application factory: creates the app, preloads modules, assembles middleware and routes |
| `settings.py`          | Configuration models: loads and validates all configuration from YAML with Pydantic Settings |
| `container.py`         | IoC container: Bean registration (singleton/prototype) and `get_bean` retrieval            |
| `routers.py`           | Router registration: mounts `APIRouter` by business domain                                 |
| `error_handler.py`     | Exception system: common exception checks and the global exception handler                 |
| `penum_var.py`         | Core enums: core business-domain enums are defined here for easy import by business domains and globally |
| `log.py`               | Log manager: per-module logging configuration based on Loguru                               |
| `middlewares.py`       | Middleware: request logging, JWT authentication                                             |
| `permissions_limit.py` | Permission dependencies                                                                     |



## Startup Assembly Order (app.py)

`create_app(app_settings)` completes application initialization:

1. Initialize logging (`init_logger`);
1. **Preload modules** (`auto_load_modules`)
1. Initialize the database engine and sessions (`init_database`) and the Redis connection pool (`init_cache`);
1. Assemble exception handlers, middleware, and routes, and install the OpenAPI examples.



## Dependency Injection (container.py)

`Container` supports two scopes:

- `SINGLETON`: one shared instance globally;
- `PROTOTYPE`: a new instance per `get_bean` call (used to inject request-scoped `db` sessions).

Global container instances: `application_factory` / `domain_service_factory` / `repository_factory`, each managing the Beans of its own layer.



## Exception System (error_handler.py)

All business exceptions inherit from `OrangeCraftException`; `global_exception_handler` converts them uniformly into a standard JSON response:

```text
NotFoundError(404) / PermissionDeniedError(403) / InvalidInputError(400)
        │
OrangeCraftException (status_code)
        │
global_exception_handler → {"code": ..., "message": ...}
```

Business code throws domain exceptions; there is no need to catch them again in the API layer.



## Middleware (middlewares.py)

- `RequestLogMiddleWare`: logs requests and responses;
- `JWTAuthMiddleware`: unified JWT authentication (`_should_exclude_path` allows `/docs`, `/login`, `/health`, etc.).
