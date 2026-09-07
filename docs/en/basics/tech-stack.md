# Tech Stack

The technology choices in FastBrace revolve around three goals: **high performance**, **solid engineering**, and **AI friendliness**. This page lists the core technical components used by the framework. We recommend studying the following items before using the scaffold — getting familiar with them in advance will make working with the scaffold much smoother.



## Runtime Environment

| Component     | Version requirement  | Description                                                       |
| -------- | --------- | ---------------------------------------------------------- |
| Python   | 3.10+     | Modern type annotations and async features                                 |
| MySQL    | 8.x       | Business data storage, with the `utf8mb4` charset by default                        |
| Redis    | 6+        | Caching, login sessions and the Celery broker                               |
| uv       | Latest stable | Manages the Python version, virtual environments and dependencies in one tool, replacing pip/poetry and similar tools |



## Core Dependencies

| Category         | Component               | Version      | Purpose                                                     |
| ------------ | ------------------ | --------- | -------------------------------------------------------- |
| Web framework     | FastAPI            | 0.109+    | High-performance async API framework with built-in OpenAPI/Swagger docs            |
| ASGI server  | Uvicorn           | 0.27+     | Production-grade ASGI server, started with one command in `main.py`                  |
| ORM          | SQLAlchemy        | 2.0+      | Database model definitions with async/sync data access                         |
| Database driver   | PyMySQL           | 1.1+      | MySQL connection driver                                            |
| Database migration   | Alembic           | 1.13+     | Database schema versioning and migrations                                  |
| Configuration management     | Pydantic Settings | 2.0+      | Type-safe configuration models and environment variable management                          |
| Data validation     | Pydantic          | 2.0+      | Request/response model definition and validation                                   |
| Authentication         | PyJWT / bcrypt    | 2.10+/4.3+ | JWT token issuing/verification and password hashing                                |
| Cache         | Redis (redis-py)  | 5.0+      | Cache connections and login session management                                      |
| Task queue     | Celery            | 5.3+      | Async tasks and event processing                                        |
| Scheduled jobs     | Celery Redbeat    | 2.3+      | Redis-backed periodic task scheduler                                |
| Logging         | Loguru            | 0.7+      | Structured logging, replacing the standard-library logging                            |
| Encryption         | cryptography      | 42.0+     | RSA password encryption (RSA-OAEP-SHA256)                           |
| Object storage     | oss2              | 2.18+     | Alibaba Cloud OSS file upload (optional)                               |
| Templates         | Jinja2            | 3.1+      | Template rendering for emails etc.                                            |

> For the full version constraints, refer to `dependencies` in the `pyproject.toml` at the project root; install dependencies with `uv sync --all-extras`.



## Next Steps

- Responsibilities of each directory: [Directory Structure](./project-structure)
- Layered design and coding conventions: [Architecture Guide](/en/advanced/architecture/domain-layer)
