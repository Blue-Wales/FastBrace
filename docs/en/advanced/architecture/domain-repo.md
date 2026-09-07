# Domain Repository Design Guide

This document describes the responsibility boundaries, directory structure, and writing conventions of `domain/repo/`.

## Responsibility Boundaries

Repositories **only do database operations**: CRUD and batch writes. They contain no business rules, no permission checks, and no cross-domain data composition.

- Business rules live in entities and domain services;
- The repository's core job is database operations.



## Directory Structure

```text
domain/repo/
├── base.py                      # Abstract base class: entity/ORM conversion and common capabilities
├── interfaces/                  # Repository interfaces (abstractions)
│   ├── base.py                  # IBaseRepository: common batch abstraction
│   ├── user.py                  # IUserRepository: user persistence abstraction
│   ├── role.py                  # IRoleRepository: role and closure table abstraction
│   ├── file.py                  # IFileRepository: file storage abstraction
│   └── permission_resource.py   # IPermissionResourceRepository: permission resource abstraction
├── user_repo.py                 # UserRepository: SQLAlchemy implementation
├── role_repo.py                 # RoleRepository: closure table implementation
├── file_repo.py                 # FileRepository: attachment read/write implementation
└── permission_resource_repo.py  # PermissionResourceRepository: permission resource implementation
```

## Abstract Base Class (base.py)

`BaseRepository` provides the capabilities shared by all repositories:

- `_to_entity(orm_obj, entity)`: query result → domain entity (`model_validate`);
- `_to_model(model, entity)`: entity → ORM model (trimmed to table columns);
- `batch_upsert(model, data_list, on_duplicate_key_list)`: batch writes via MySQL `ON DUPLICATE KEY`.

Implementation classes inherit from it and only add the query methods specific to their own module.



## Interface/Implementation Separation (interfaces/)

`interfaces/` defines the **persistence contracts** (`Protocol`) that the domain layer depends on — a stable boundary:

- Interfaces only describe the read/write capabilities the domain needs; they never expose implementation details such as SQL, table schemas, or Session;
- Callers (application services, domain services) depend on interface types; factories return implementation classes;
- When adding a query method, update the interface and implementation together and keep the signatures consistent.



## Writing Conventions

- Register each implementation class with `@repository_factory.autowire("{module}_repo", scope=BeanScope.PROTOTYPE.value)`;
- Query methods return domain entities or value objects, never ORM objects directly;
- Do database operations only; business checks inside repositories are forbidden.



## Flow for Adding a New Repository

1. Define the contract in `domain/repo/interfaces/{module}.py` (method signatures + docs);

1. Implement it in `domain/repo/{module}_repo.py` by inheriting `BaseRepository`;

1. Register with `autowire` and add it to the `auto_load_modules` preload list in `infrastructure/core/app.py` (if it must be registered at startup);
