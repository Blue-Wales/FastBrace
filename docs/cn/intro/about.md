# 关于FastBrace

FastBrace是一个基于**Fastapi构建的轻量级高性能脚手架**，目标是为开发企业级后台管理项目提供开箱即用的解决方案。脚手架内置用户认证、角色权限、文件上传等核心功能，同时采用最新技术栈和清晰的架构划分，可以对接任意前端项目，项目提供清晰完整的文档说明，也可以用于学习**后端开发**、**ai应用开发**等内容，该项目目前会持续跟进最新技术，并将其应用在项目中，也欢迎大家提供有价值的建议，参与讨论👏。




## 核心特性

- **架构清晰**：采用DDD 领域驱动架构设计， 边界清晰

- **轻量高性能**： 基于原生Fastapi构建、异步高性能

- **开箱即用的后台能力**：用户、角色、权限、文件上传、登录认证等基础功能内置，可对接各种前端框架，快速生成企业级项目

- **ai编程**：内置框架 Skill，只需描述业务场景并发送给 Codex、Claude Code、DeepSeek 等 AI 工具，即可生成**规范统一、易于维护、性能优异**的业务代码

- **一键脚本**：常用命令通过 Makefile 统一管理，`make` 一键执行，告别手动拼写终端指令

- **uv 统一管理**：一个 uv 替代 `pip`、`poetry`、`pyenv`、`virtualenv` 等传统工具链，依赖安装与环境管理一步到位

- **工程质量可靠**： pytest + pytest-asyncio 异步测试，高效测试接口信息，集成Ruff、lint 与分层风格检查，保证团队代码规范质量

- **集成ci cd流水线**：完整的流水线配置文件，你只需要在github 上配置相关环境变量，可快速发布部署



## 文档导航

| 模块 | 说明 |
| --- | --- |
| [快速开始](/intro/getting-started) | 环境准备、安装依赖与启动服务 |
| [为什么选择 FastBrace](/intro/why-FastBrace) | 与主流 FastAPI 模板的对比分析 |
| [基础](/basics/tech-stack) | 技术栈、目录结构与功能概览（登录、用户、角色、权限、文件、事件、定时任务） |
| [架构指南](/advanced/architecture/domain-layer) | DDD 四层架构的设计与编写约定 |
| [进阶功能](/advanced/permission) | 权限系统、事件系统、定时任务、日志、加密通信、模板引擎等 |
| [工程化](/advanced/engineering/lint-and-style) | 代码规范、部署与 CI/CD |
| [Skill 与 MCP](/advanced/engineering/skill) | AI 编码规范（Skill）与工具集成（MCP） |
| [项目实战](/practice/vben-admin) | 对接 vben-vue-admin |
| [更新日志](/changelog/) | 版本迭代记录 |



## 下一步

- 在本地运行项目：[快速开始](./getting-started)
- 需要帮助：[技术支持](/community/support)
- 支持项目发展：[赞助](/community/sponsor)


