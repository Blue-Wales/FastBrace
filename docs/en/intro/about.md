# About FastBrace

FastBrace is a **lightweight, high-performance scaffold built on FastAPI**, aiming to provide an out-of-the-box solution for enterprise-grade admin projects. The scaffold ships with core features such as user authentication, role-based permissions, and file upload. It adopts the latest tech stack with a clean architectural separation and can be paired with any frontend project. The project comes with clear, complete documentation, and can also be used to learn **backend development** and **AI application development**. FastBrace will keep tracking the latest technologies and applying them in the project. Valuable suggestions and discussions are welcome 👏.




## Core Features

- **Clean architecture**: designed with DDD (Domain-Driven Design), with clear boundaries

- **Lightweight and high-performance**: built on native FastAPI, fully asynchronous for high performance

- **Out-of-the-box admin capabilities**: users, roles, permissions, file upload, login authentication and other basics are built in; pair with any frontend framework to quickly build enterprise-grade projects

- **AI coding**: ships with framework Skills — just describe your business scenario and send it to AI tools such as Codex, Claude Code, or DeepSeek, and you will get business code that is **consistent, easy to maintain, and high-performance**

- **One-click scripts**: common commands are managed through a Makefile — run them with a single `make`, and say goodbye to typing terminal commands manually

- **Unified uv management**: one uv replaces traditional toolchains such as `pip`, `poetry`, `pyenv`, and `virtualenv`; dependency installation and environment management in one step

- **Reliable engineering quality**: pytest + pytest-asyncio async testing for efficient API testing, with integrated Ruff, lint, and layered style checks to keep the team's code consistent

- **Built-in CI/CD pipeline**: complete pipeline configuration files — you only need to configure the relevant environment variables on GitHub for quick release and deployment



## Documentation Navigation

| Module | Description |
| --- | --- |
| [Getting Started](/en/intro/getting-started) | Environment setup, dependency installation and running the service |
| [Why FastBrace](/en/intro/why-FastBrace) | Comparison with mainstream FastAPI templates |
| [Basics](/en/basics/tech-stack) | Tech stack, project structure and feature overview (login, users, roles, permissions, files, events, cron jobs) |
| [Architecture Guide](/en/advanced/architecture/domain-layer) | Design and coding conventions of the four-layer DDD architecture |
| [Advanced Features](/en/advanced/permission) | Permission system, event system, cron jobs, logging, encrypted communication, template engine and more |
| [Engineering](/en/advanced/engineering/lint-and-style) | Code standards, deployment and CI/CD |
| [Skill & MCP](/en/advanced/engineering/skill) | AI coding conventions (Skill) and tool integration (MCP) |
| [Practice](/en/practice/vben-admin) | vben-vue-admin integration |
| [Changelog](/en/changelog/) | Release history |



## Next Steps

- Run the project locally: [Quick Start](./getting-started)
- Need help: [Technical Support](/en/community/support)
- Support the project: [Sponsor](/en/community/sponsor)
