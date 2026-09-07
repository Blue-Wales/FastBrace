# 目录结构

本页介绍 FastBrace 的整体目录组织方式与各目录职责。项目采用 **DDD（领域驱动设计）+ 分层架构**



## 目录结构

```text
FastBrace/
├── api/                          # API 接口层 (Presentation Layer)
│   ├── dto/                      # 数据传输对象
│   ├── request_body/             # 请求体模型
│   ├── response_body/            # 响应体模型
│   ├── response_model/           # 响应模型（用于 Swagger 文档）
│   ├── third_party_body/         # 第三方接口模型
│   └── *.py                      # 路由模块文件
├── application/                  # 应用服务层 (Application Layer)
│   ├── tasks/                    # Celery 定时任务
│   └── *_app.py                  # 应用服务类
├── domain/                       # 领域层 (Domain Layer)
│   ├── aggregate_root/           # 聚合根
│   ├── entity/                   # 领域实体
│   ├── events/                   # 领域事件
│   ├── repo/                     # 仓储实现
│   │   └── interfaces/           # 仓储接口
│   ├── service/                  # 领域服务实现
│   │   └── interfaces/           # 领域服务接口
│   └── value_object/             # 值对象
├── infrastructure/               # 基础设施层 (Infrastructure Layer)
│   ├── config/                   # 配置文件
│   ├── core/                     # 核心组件
│   │   ├── app.py                # FastAPI 应用创建
│   │   ├── routers.py            # 路由注册
│   │   ├── settings.py           # 配置模型
│   │   ├── factorys.py           # Bean 工厂
│   │   ├── middlewares.py        # 中间件
│   │   ├── error_handler.py      # 异常处理
│   │   ├── permissions_limit.py  # 权限控制
│   │   └── enum_var.py           # 枚举常量
│   ├── cron/                     # 定时任务配置
│   ├── events/                   # 事件总线
│   ├── migrations/               # 数据库迁移
│   ├── models/                   # 数据库模型（SQLAlchemy）
│   └── utils/                    # 工具类
├── db/                           # 建表 SQL 文件
├── event_handlers/               # 事件处理器
├── skill/                        # AI Agent 开发约束（skill 文档）
├── agent-docs/                   # 面向 AI 工具的项目约束文档
├── templates/                    # 代码模板
├── scripts/                      # 工程脚本（lint、初始化等）
├── tests/                        # 测试目录
├── docs/                         # 文档站点（VitePress）
├── deploy/                       # Docker 与部署配置
├── entrance/                     # 程序入口
├── main.py                       # CLI 入口（服务启动命令）
├── pyproject.toml                # 依赖、构建、lint 和测试配置
└── Makefile                      # 工程质量脚本入口
```



## 各层职责速览

| 层级             | 目录              | 职责                                                                 |
| ---------------- | ----------------- | -------------------------------------------------------------------- |
| API 接口层       | `api/`            | 路由定义、参数校验、Swagger 文档、调用应用服务                       |
| 应用服务层       | `application/`    | 用例编排、事务边界、跨领域协作、Celery 任务                          |
| 领域层           | `domain/`         | 实体、值对象、聚合根、领域服务、仓储接口与实现——业务规则的核心       |
| 基础设施层       | `infrastructure/` | 数据库模型、配置、中间件、工具类、事件总线等技术实现                 |

依赖方向自上而下：`api` → `application` → `domain`，`infrastructure` 为各层提供技术支撑。分层的详细设计约定见 [架构指南](/advanced/architecture/domain-layer)。



## 下一步

- 查看技术组件与版本：[技术栈](./tech-stack)
- 深入各层设计约定：[架构指南](/advanced/architecture/domain-layer)
- 用 AI 按规范生成模块代码：[Skill](/advanced/engineering/skill)
