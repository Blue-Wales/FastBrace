# Directory Structure

This page describes the overall directory organization of FastBrace and the responsibilities of each directory. The project follows **DDD (Domain-Driven Design) + layered architecture**



## Directory Layout

```text
FastBrace/
├── api/                          # API layer (Presentation Layer)
│   ├── dto/                      # Data transfer objects
│   ├── request_body/             # Request body models
│   ├── response_body/            # Response body models
│   ├── response_model/           # Response models (for Swagger docs)
│   ├── third_party_body/         # Third-party API models
│   └── *.py                      # Route module files
├── application/                  # Application service layer (Application Layer)
│   ├── tasks/                    # Celery scheduled tasks
│   └── *_app.py                  # Application service classes
├── domain/                       # Domain layer (Domain Layer)
│   ├── aggregate_root/           # Aggregate roots
│   ├── entity/                   # Domain entities
│   ├── events/                   # Domain events
│   ├── repo/                     # Repository implementations
│   │   └── interfaces/           # Repository interfaces
│   ├── service/                  # Domain service implementations
│   │   └── interfaces/           # Domain service interfaces
│   └── value_object/             # Value objects
├── infrastructure/               # Infrastructure layer (Infrastructure Layer)
│   ├── config/                   # Configuration files
│   ├── core/                     # Core components
│   │   ├── app.py                # FastAPI application creation
│   │   ├── routers.py            # Route registration
│   │   ├── settings.py           # Configuration models
│   │   ├── factorys.py           # Bean factory
│   │   ├── middlewares.py        # Middlewares
│   │   ├── error_handler.py      # Exception handling
│   │   ├── permissions_limit.py  # Permission control
│   │   └── enum_var.py           # Enum constants
│   ├── cron/                     # Scheduled task configuration
│   ├── events/                   # Event bus
│   ├── migrations/               # Database migrations
│   ├── models/                   # Database models (SQLAlchemy)
│   └── utils/                    # Utility classes
├── db/                           # Table creation SQL files
├── event_handlers/               # Event handlers
├── skill/                        # AI Agent development constraints (Skill docs)
├── agent-docs/                   # Project constraint docs for AI tools
├── templates/                    # Code templates
├── scripts/                      # Engineering scripts (lint, initialization, etc.)
├── tests/                        # Test directory
├── docs/                         # Documentation site (VitePress)
├── deploy/                       # Docker and deployment configuration
├── entrance/                     # Program entry points
├── main.py                       # CLI entry (service start commands)
├── pyproject.toml                # Dependency, build, lint and test configuration
└── Makefile                      # Entry point for engineering quality scripts
```



## Layer Responsibilities at a Glance

| Layer             | Directory              | Responsibilities                                                                 |
| ---------------- | ----------------- | -------------------------------------------------------------------- |
| API layer       | `api/`            | Route definitions, parameter validation, Swagger docs, calling application services                       |
| Application service layer       | `application/`    | Use case orchestration, transaction boundaries, cross-domain collaboration, Celery tasks                          |
| Domain layer           | `domain/`         | Entities, value objects, aggregate roots, domain services, repository interfaces and implementations — the heart of business rules       |
| Infrastructure layer       | `infrastructure/` | Database models, configuration, middlewares, utility classes, event bus and other technical implementations                 |

Dependencies flow top-down: `api` → `application` → `domain`, with `infrastructure` providing technical support to all layers. For detailed layered design conventions, see the [Architecture Guide](/en/advanced/architecture/domain-layer).



## Next Steps

- Technical components and versions: [Tech Stack](./tech-stack)
- Dive into the design conventions of each layer: [Architecture Guide](/en/advanced/architecture/domain-layer)
- Generate module code with AI following the conventions: [Skill](/en/advanced/engineering/skill)
