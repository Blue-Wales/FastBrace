---
layout: home

hero:
  name: FastBrace
  text: 基于FastAPI的中后台高性能框架
  tagline: 采用 DDD 领域驱动架构设计、提供开箱即用的后台能力
  image:
    src: /FastBrace-hero-logo.png
    alt: FastBrace 3D Logo
  actions:
    - theme: brand
      text: 快速开始
      link: /intro/getting-started
    - theme: alt
      text: 架构指南
      link: /advanced/architecture/domain-layer
    - theme: alt
      text: GitHub
      link: https://github.com/Blue-Wales/FastBrace

features:
  - icon: 🏗️
    title: 架构清晰
    details: 采用 DDD 领域驱动架构设计 边界清晰，内置层间依赖规范检查。
  - icon: 📦
    title: 开箱即用的后台能力
    details: 内置用户、角色、权限、文件上传、登录认证等基础功能，可对接任意前端框架，快速生成企业级项目。
  - icon: 🤖
    title: ai编程
    details: 内置 Skill 编码指南，描述业务场景交给 AI 工具，即可生成规范统一、易于维护的业务代码。
  - icon: ⚡
    title: 一键脚本
    details: 常用命令由 Makefile 统一管理，make 一键执行，告别手动拼写终端指令。
  - icon: 🧰
    title: uv 统一管理
    details: 一个 uv 替代 pip / poetry / pyenv / virtualenv 传统工具链，依赖安装与环境管理一步到位。
  - icon: ✅
    title: 工程质量可靠
    details: pytest + pytest-asyncio 异步测试，集成 Ruff lint 与分层风格检查，保证团队代码规范质量。
  - icon: 🚀
    title: 集成 CI/CD 流水线
    details: 完整的流水线配置文件，只需在 GitHub 配置环境变量，即可快速发布部署。
---
