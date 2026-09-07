# Application Service Layer Design Guide

This document describes the responsibility boundaries, file structure, and use case orchestration of the `application/` layer.

## Layer Positioning

`application/` is the application layer of DDD and only does **use case orchestration**: composing domain services and repositories, managing transaction boundaries, and assembling responses. Domain rules live in `domain/`, HTTP parsing in `api/`.

```text
api/        → calls application layer interfaces (depends on abstractions, not implementations)
application → orchestrates domain layer repositories and services, returns assembled responses
```



## Common File Structure

| File          | Responsibility                                                          |
| ------------- | ------------------------------------------------------------------------ |
| `base.py`     | Base classes and common capabilities: `BaseApplicationService`, `IBaseApplicationService` |
| `user_app.py` | User use cases: login / token / user CRUD / password / status / role switching |
| `role_app.py` | Role use cases: role CRUD, role-user relation maintenance                |
| `file_app.py` | File use cases: OSS upload                                               |



## Registration and Retrieval

Application services are registered as IoC Beans via a decorator and preloaded by `auto_load_modules` in `infrastructure/core/app.py`:

```python
# application/role_app.py
@application_factory.autowire("role_app_service", scope=BeanScope.PROTOTYPE.value)
class RoleApplicationService(BaseApplicationService):
    ...
```

```python
# infrastructure/core/app.py: new application services must be added to the preload list
auto_load_modules(base_packages=[
    "application.file_app",
    "application.role_app",
    "application.user_app",
    ...
])
```



## Writing Conventions

- Inherit from `BaseApplicationService` to gain the common capabilities `generate_response` / `generate_page_response` / `generate_list_response` / `transaction`;
- Classes inheriting the base only need a short description; do not repeat the base class documentation (e.g., `UserAppService` only writes "user application service");
- Use case methods return a `dict` (`data.model_dump()`), which the API layer wraps into a unified JSON response;
- Throw domain exceptions (`NotFoundError`, `InvalidInputError`, etc.); the global exception handler converts them uniformly.



## Flow for Adding a New Application Service

1. In `application/{module}_app.py`, inherit from `BaseApplicationService` and implement the use case methods;
1. When a contract boundary is needed, declare an `I{Module}AppService(Protocol)` interface (see `IUserAppService`);
1. Register with `@application_factory.autowire("{module}_app_service", ...)`;
1. Add the module to the `auto_load_modules` preload list in `infrastructure/core/app.py`;
